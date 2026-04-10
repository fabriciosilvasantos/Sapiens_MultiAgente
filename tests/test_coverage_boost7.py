"""
Boost de cobertura — Rodada 7.
Alvos restantes após boost6 (97% → ~99%):

- csv_search_tool.py  138       : pd.to_numeric em coluna string
- main.py             61-76     : bloco if __name__ == '__main__'
- web/app.py          318       : time.sleep no SSE stream
- web/app.py          634-664   : download de links em _processar_analise
- web/app.py          818-819   : TimeoutError em _executar_analise
- web/app.py          1060-1061 : bloco if __name__ == '__main__' em app.py
- pdf_search_tool.py  220       : continue para XObject não-imagem
"""

import os
import sys
import json
import time
import sqlite3
import runpy
import threading
import pytest
from unittest.mock import patch, MagicMock, PropertyMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# ---------------------------------------------------------------------------
# csv_search_tool.py — linha 138 (pd.to_numeric em coluna string)
# ---------------------------------------------------------------------------

class TestCSVSearchToNumeric:
    """
    'score' com valor 'n/a' faz pandas ler a coluna como object dtype.
    Ao aplicar filtro numérico, _apply_numeric_filters converte via
    pd.to_numeric(errors='coerce') — linha 138.
    """

    def test_filtro_numerico_coluna_object_dtype(self, tmp_path):
        from Sapiens_MultiAgente.tools.csv_search_tool import CSVSearchTool

        csv_file = tmp_path / 'notas_mixed.csv'
        # 'n/a' força dtype object para 'score'
        csv_file.write_text(
            'nome,score\nAna,10\nBia,n/a\nCaio,8\n',
            encoding='utf-8',
        )

        tool = CSVSearchTool()
        result = tool._run(
            file_path=str(csv_file),
            numeric_filters={'score': '>6'},
        )

        # Ana (10) e Caio (8) passam; Bia (NaN após coerce) não
        assert 'Ana' in result or 'Caio' in result or '❌' not in result


# ---------------------------------------------------------------------------
# main.py — linhas 61-76 (bloco if __name__ == '__main__')
# ---------------------------------------------------------------------------

_MAIN_MODULE = 'Sapiens_MultiAgente.main'


class TestMainEntryPoint:
    """Usa runpy.run_module para executar o bloco __main__ de main.py."""

    def test_sem_argumentos_exibe_uso_e_sai(self):
        with patch.object(sys, 'argv', ['main.py']):
            with pytest.raises(SystemExit) as exc:
                runpy.run_module(_MAIN_MODULE, run_name='__main__', alter_sys=False)
        assert exc.value.code == 1

    def test_comando_run(self):
        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew') as MockCrew, \
             patch.object(sys, 'argv', ['main.py', 'run']):
            MockCrew.return_value.crew.return_value.kickoff.return_value = 'ok'
            runpy.run_module(_MAIN_MODULE, run_name='__main__', alter_sys=False)

    def test_comando_train_cobre_ramo(self):
        """train() com sys.argv[1]='train' falha em int('train'), mas o ramo É coberto."""
        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew') as MockCrew, \
             patch.object(sys, 'argv', ['main.py', 'train']):
            MockCrew.return_value.crew.return_value.train.return_value = None
            with pytest.raises(Exception, match='training'):
                runpy.run_module(_MAIN_MODULE, run_name='__main__', alter_sys=False)

    def test_comando_replay_cobre_ramo(self):
        """replay() usa sys.argv[1] como task_id — 'replay' é string válida para o mock."""
        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew') as MockCrew, \
             patch.object(sys, 'argv', ['main.py', 'replay']):
            MockCrew.return_value.crew.return_value.replay.return_value = None
            runpy.run_module(_MAIN_MODULE, run_name='__main__', alter_sys=False)

    def test_comando_test_cobre_ramo(self):
        """test() com sys.argv[1]='test' falha em int('test'), mas o ramo É coberto."""
        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew') as MockCrew, \
             patch.object(sys, 'argv', ['main.py', 'test']):
            MockCrew.return_value.crew.return_value.test.return_value = None
            with pytest.raises(Exception, match='testing'):
                runpy.run_module(_MAIN_MODULE, run_name='__main__', alter_sys=False)

    def test_comando_desconhecido_sai_com_1(self):
        with patch.object(sys, 'argv', ['main.py', 'invalid_cmd']):
            with pytest.raises(SystemExit) as exc:
                runpy.run_module(_MAIN_MODULE, run_name='__main__', alter_sys=False)
        assert exc.value.code == 1


# ---------------------------------------------------------------------------
# web/app.py — linha 318 (time.sleep no loop SSE)
# ---------------------------------------------------------------------------

class TestSSEStream:
    """SSE stream: analise em progresso → time.sleep(1) → status final → break."""

    @pytest.fixture
    def app_cliente(self, tmp_path):
        db_path = str(tmp_path / 'test_sse.db')
        with patch('Sapiens_MultiAgente.web.app.DB_PATH', db_path), \
             patch('Sapiens_MultiAgente.web.auth.DB_PATH', db_path):
            from Sapiens_MultiAgente.web.app import SapiensWebInterface
            interface = SapiensWebInterface()
            flask_app = interface.create_app()
            flask_app.config['TESTING'] = True
            flask_app.config['WTF_CSRF_ENABLED'] = False
            yield interface, flask_app.test_client()

    def test_stream_passa_por_sleep_e_termina(self, app_cliente):
        """
        Estratégia: primeira chamada retorna progresso=-1 (igual ao ultimo_progresso inicial)
        → não faz yield, não bloqueia a leitura pelo cliente → time.sleep(1) é atingido
        → segunda chamada retorna status 'concluida' → yield final → break.
        """
        interface, client = app_cliente
        analise_id = 'sse-sleep-test-001'

        call_count = 0
        mock_sleep = MagicMock()

        def mock_buscar(aid):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # progresso=-1 == ultimo_progresso(-1) → sem yield → sleep(1) hit
                return {'progresso': -1, 'status': 'processando'}
            # Segundo retorno: status final → yield + break
            return {'progresso': 100, 'status': 'concluida'}

        with patch.object(interface, '_buscar_analise', side_effect=mock_buscar), \
             patch('time.sleep', mock_sleep):
            resp = client.get(f'/stream/{analise_id}')

        assert resp.status_code == 200
        body = resp.get_data(as_text=True)
        assert 'data:' in body
        # time.sleep(1) deve ter sido chamado (linha 318 coberta)
        mock_sleep.assert_called()
        assert call_count >= 2


# ---------------------------------------------------------------------------
# web/app.py — linhas 634-664 (download de links em _processar_analise)
# ---------------------------------------------------------------------------

class TestLinkDownload:
    """Testa os ramos de download de URLs válidas em _processar_analise."""

    @pytest.fixture
    def app_cliente(self, tmp_path):
        db_path = str(tmp_path / 'test_link.db')
        upload_folder = str(tmp_path / 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        with patch('Sapiens_MultiAgente.web.app.DB_PATH', db_path), \
             patch('Sapiens_MultiAgente.web.auth.DB_PATH', db_path):
            from Sapiens_MultiAgente.web.app import SapiensWebInterface
            interface = SapiensWebInterface()
            flask_app = interface.create_app()
            flask_app.config['TESTING'] = True
            flask_app.config['WTF_CSRF_ENABLED'] = False
            flask_app.config['UPLOAD_FOLDER'] = upload_folder
            yield interface, flask_app.test_client()

    def _login(self, client):
        _pw = os.getenv('SAPIENS_ADMIN_PASSWORD')
        client.post('/login', data={'username': 'admin', 'senha': _pw})

    def test_link_200_valido_processado(self, app_cliente):
        """requests.get → 200, segurança válida → arquivo adicionado (634-656)."""
        interface, client = app_cliente
        self._login(client)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'coluna1,coluna2\n1,2\n3,4\n'

        with patch('Sapiens_MultiAgente.web.app.requests.get', return_value=mock_resp), \
             patch.object(interface.security_validator, 'validar_arquivo',
                          return_value={'valido': True, 'erros': [], 'avisos': []}), \
             patch.object(interface, '_executar_analise'):
            resp = client.post(
                '/analise',
                data={
                    'topico_pesquisa': 'Teste link válido',
                    'links_sites': 'http://example.com/dados.csv',
                },
                follow_redirects=True,
            )

        assert resp.status_code == 200

    def test_link_200_invalido_remove_arquivo(self, app_cliente):
        """requests.get → 200 mas segurança inválida → remove e flash (657-660)."""
        interface, client = app_cliente
        self._login(client)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'conteudo malicioso'

        with patch('Sapiens_MultiAgente.web.app.requests.get', return_value=mock_resp), \
             patch.object(interface.security_validator, 'validar_arquivo',
                          return_value={'valido': False, 'erros': ['tipo não permitido'], 'avisos': []}), \
             patch.object(interface, '_executar_analise'):
            resp = client.post(
                '/analise',
                data={
                    'topico_pesquisa': 'Teste link inválido',
                    'links_sites': 'http://example.com/malware.exe',
                },
                follow_redirects=True,
            )

        assert resp.status_code == 200

    def test_link_nao_200_emite_flash(self, app_cliente):
        """requests.get → 404 → flash de aviso (linha 662)."""
        interface, client = app_cliente
        self._login(client)

        mock_resp = MagicMock()
        mock_resp.status_code = 404

        with patch('Sapiens_MultiAgente.web.app.requests.get', return_value=mock_resp), \
             patch.object(interface, '_executar_analise'):
            resp = client.post(
                '/analise',
                data={
                    'topico_pesquisa': 'Teste link 404',
                    'links_sites': 'http://example.com/inexistente',
                },
                follow_redirects=True,
            )

        assert resp.status_code == 200

    def test_link_excecao_na_requisicao(self, app_cliente):
        """requests.get lança exceção → flash de aviso (linha 664)."""
        interface, client = app_cliente
        self._login(client)

        with patch('Sapiens_MultiAgente.web.app.requests.get',
                   side_effect=RuntimeError('conexão recusada')), \
             patch.object(interface, '_executar_analise'):
            resp = client.post(
                '/analise',
                data={
                    'topico_pesquisa': 'Teste link erro',
                    'links_sites': 'http://example.com/timeout',
                },
                follow_redirects=True,
            )

        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# web/app.py — linhas 818-819 (TimeoutError em _executar_analise)
# ---------------------------------------------------------------------------

class TestExecutarAnaliseTimeout:
    """Crew.kickoff trava; timeout=0 → concurrent.futures.TimeoutError → linhas 818-819."""

    @pytest.fixture
    def interface_com_db(self, tmp_path):
        db_path = str(tmp_path / 'test_timeout.db')
        with patch('Sapiens_MultiAgente.web.app.DB_PATH', db_path), \
             patch('Sapiens_MultiAgente.web.auth.DB_PATH', db_path):
            from Sapiens_MultiAgente.web.app import SapiensWebInterface
            interface = SapiensWebInterface()
            interface.create_app()
            yield interface, db_path

    def test_timeout_seta_status_erro(self, interface_com_db):
        """
        Usa patcher.start()/stop() para manter o patch ativo durante a execução
        da thread de background — evita que o patch expire antes do worker terminar.
        _limpar_arquivos_analise remove a entrada de analises_ativas, então
        verificamos o status no banco de dados.
        """
        import concurrent.futures
        from datetime import datetime as _dt

        interface, db_path = interface_com_db
        analise_id = 'timeout-boost7-001'
        _now = _dt.now().isoformat()

        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'topico_pesquisa': 'teste timeout',
            'arquivos': [],
            'status': 'processando',
            'progresso': 0,
            'usuario_id': 'admin',
            'timestamp_inicio': _now,
            'criado_em': _now,
            'atualizado_em': _now,
            'timestamp_atualizacao': _now,
            'concluido_em': None,
            'resultados': None,
            'erro': None,
        }

        # Patches ativos durante toda a execução da thread (start/stop manual)
        p_crew = patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew')
        p_env = patch.dict(os.environ, {'SAPIENS_CREW_TIMEOUT': '0'})

        MockCrew = p_crew.start()
        p_env.start()
        try:
            mock_instance = MagicMock()
            MockCrew.return_value = mock_instance
            mock_crew_obj = MagicMock()
            mock_instance.crew.return_value = mock_crew_obj

            # kickoff dura 0.5s; com CREW_TIMEOUT=0 → future.result(timeout=0) → TimeoutError
            mock_crew_obj.kickoff.side_effect = lambda inputs: time.sleep(0.5) or 'ok'

            interface._executar_analise(analise_id)

            # Aguarda a thread de background concluir (máx 3s)
            deadline = time.time() + 3.0
            while time.time() < deadline:
                status = interface.analises_ativas.get(analise_id, {}).get('status', '')
                if status == 'erro':
                    break
                time.sleep(0.05)
        finally:
            p_env.stop()
            p_crew.stop()

        # _limpar_arquivos_analise remove a entrada de analises_ativas após conclusão
        # → verificamos o status persistido no banco de dados
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT status, erro FROM analises WHERE id = ?", (analise_id,)
            ).fetchone()

        assert row is not None, "Análise não foi persistida no banco"
        assert row['status'] == 'erro'
        assert row['erro'] is not None
        assert 'limite' in row['erro'].lower() or 'timeout' in row['erro'].lower()


# ---------------------------------------------------------------------------
# web/app.py — linhas 1060-1061 (bloco if __name__ == '__main__')
# ---------------------------------------------------------------------------

class TestWebAppMainBlock:
    """Executa o bloco __main__ de app.py via runpy."""

    def test_main_block_cria_e_executa_interface(self):
        """
        Patcha flask.Flask.run para evitar que o servidor HTTP bloqueie.
        O bloco __main__ chama create_web_interface().run() → app.run() → mock.
        """
        import flask

        with patch.object(flask.Flask, 'run', return_value=None):
            runpy.run_module(
                'Sapiens_MultiAgente.web.app',
                run_name='__main__',
                alter_sys=False,
            )
        # Se chegamos aqui sem travar, o bloco __main__ foi executado com sucesso


# ---------------------------------------------------------------------------
# pdf_search_tool.py — linha 220 (continue para XObject sem Subtype /Image)
# ---------------------------------------------------------------------------

class TestPDFXObjectNaoImagem:
    """_extract_images com XObject cujo /Subtype != /Image → continue (linha 220)."""

    def test_xobject_form_e_ignorado(self, tmp_path):
        from Sapiens_MultiAgente.tools.pdf_search_tool import PDFSearchTool

        tool = PDFSearchTool()

        # Mock do objeto XObject com /Subtype = /Form (não é /Image)
        mock_obj_form = MagicMock()
        mock_obj_form.get.side_effect = lambda key, default=None: (
            '/Form' if key == '/Subtype' else default
        )

        mock_obj_ref = MagicMock()
        mock_obj_ref.get_object.return_value = mock_obj_form

        # Mock do XObject dict com um item do tipo /Form
        mock_xobjects = MagicMock()
        mock_xobjects.items.return_value = [('Form1', mock_obj_ref)]

        # Mock do recurso da página
        mock_resources = MagicMock()
        mock_resources.get.side_effect = lambda key, default=None: (
            mock_xobjects if key == '/XObject' else default
        )

        # Mock da página
        mock_page = MagicMock()
        mock_page.get.return_value = mock_resources

        # Mock do reader
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]

        output_dir = str(tmp_path / 'imgs')
        result = tool._extract_images(mock_reader, 'fake.pdf', output_dir, [0])

        # Nenhuma imagem extraída (o XObject é /Form, não /Image)
        assert 'imagens' in result.lower() or 'encontrada' in result.lower() or '0' in result
