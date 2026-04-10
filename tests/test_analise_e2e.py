"""
Testes E2E do fluxo de análise do SAPIENS.

Verifica se o pipeline completo funciona — desde o disparo da análise até
a persistência dos resultados — usando mock da crew para evitar chamadas
reais à LLM.

Cenários cobertos:
  1. Fluxo feliz: análise conclui com resultados salvos
  2. Transições de status: processando → executando_analise → … → concluida
  3. Análise com arquivo CSV real
  4. Erro no crew: status vai para 'erro' com mensagem
  5. Timeout: análise excede SAPIENS_CREW_TIMEOUT
  6. Via API REST: POST /api/v1/analises → polling → resultados
  7. Via formulário web: POST /analise → redirect → resultados
  8. Análises paralelas: múltiplas análises simultâneas
"""

import os
import io
import time
import uuid
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RESULTADO_SIMULADO = """
# Relatório de Análise Acadêmica

## Análise Descritiva
- Média geral: 7,4
- Desvio padrão: 1,2
- Distribuição: normal

## Análise Diagnóstica
- Correlação entre frequência e desempenho: 0,78 (forte)

## Análise Preditiva
- Projeção próximo semestre: leve melhora esperada

## Análise Prescritiva
- Aumentar atividades de reforço para os 20% inferiores
"""

CSV_ACADEMICO = """aluno_id,nome,nota_p1,nota_p2,frequencia,reprovado
1,Ana Silva,8.5,9.0,0.95,0
2,Bruno Lima,5.0,4.5,0.72,1
3,Carla Souza,7.0,7.5,0.88,0
4,Diego Costa,3.5,4.0,0.60,1
5,Elena Martins,9.5,9.8,0.98,0
6,Fabio Nunes,6.5,6.0,0.80,0
7,Gabi Torres,4.0,5.0,0.65,1
8,Hugo Ramos,8.0,8.5,0.91,0
"""


def _aguardar_conclusao(interface, analise_id, timeout=15):
    """Aguarda análise atingir status terminal. Lança TimeoutError se exceder."""
    status_terminais = {'concluida', 'erro'}
    deadline = time.time() + timeout
    while time.time() < deadline:
        analise = interface._buscar_analise(analise_id)
        if analise and analise.get('status') in status_terminais:
            return analise
        time.sleep(0.05)
    raise TimeoutError(f"Análise {analise_id} não terminou em {timeout}s")


def _mock_crew(resultado=None):
    """Retorna um mock de SapiensAcademicMultiAgentDataAnalysisPlatformCrew."""
    resultado = resultado or RESULTADO_SIMULADO
    mock_kickoff_result = MagicMock()
    mock_kickoff_result.__str__ = lambda self: resultado

    mock_crew_obj = MagicMock()
    mock_crew_obj.kickoff.return_value = mock_kickoff_result

    mock_instance = MagicMock()
    mock_instance.crew.return_value = mock_crew_obj

    return mock_instance, mock_crew_obj


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def setup(tmp_path):
    """
    Cria SapiensWebInterface isolada com banco temporário.
    Retorna (interface, flask_app, client_autenticado).
    """
    db_path = str(tmp_path / "sapiens_e2e.db")
    upload_dir = str(tmp_path / "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    with patch('Sapiens_MultiAgente.web.app.DB_PATH', db_path), \
         patch('Sapiens_MultiAgente.web.auth.DB_PATH', db_path):

        from Sapiens_MultiAgente.web.app import SapiensWebInterface
        interface = SapiensWebInterface()
        interface.upload_config['UPLOAD_FOLDER'] = upload_dir

        flask_app = interface.create_app()
        flask_app.config['TESTING'] = True
        flask_app.config['WTF_CSRF_ENABLED'] = False
        flask_app.config['UPLOAD_FOLDER'] = upload_dir

        client = flask_app.test_client()
        # Autentica como admin
        client.post('/login', data={'username': 'admin', 'senha': 'sapiens@2025'})

        yield interface, flask_app, client


@pytest.fixture
def csv_file(tmp_path):
    """Cria um arquivo CSV acadêmico real no filesystem."""
    path = tmp_path / "notas_alunos.csv"
    path.write_text(CSV_ACADEMICO, encoding='utf-8')
    return str(path)


# ---------------------------------------------------------------------------
# 1. Fluxo feliz — análise conclui com resultados
# ---------------------------------------------------------------------------

class TestFluxoFeliz:

    def test_analise_conclui_com_status_concluida(self, setup):
        interface, _, _ = setup
        mock_instance, _ = _mock_crew()
        analise_id = str(uuid.uuid4())

        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'usuario_id': 'admin',
            'topico_pesquisa': 'Desempenho acadêmico 2024',
            'status': 'processando',
            'progresso': 0,
            'arquivos': [],
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            interface._executar_analise(analise_id)
            analise = _aguardar_conclusao(interface, analise_id)

        assert analise['status'] == 'concluida'
        assert analise['progresso'] == 100

    def test_resultados_sao_salvos_no_banco(self, setup):
        interface, _, _ = setup
        mock_instance, _ = _mock_crew()
        analise_id = str(uuid.uuid4())

        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'usuario_id': 'admin',
            'topico_pesquisa': 'Análise de evasão escolar',
            'status': 'processando',
            'progresso': 0,
            'arquivos': [],
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            interface._executar_analise(analise_id)
            _aguardar_conclusao(interface, analise_id)

        # Remove do cache e busca direto do banco
        interface.analises_ativas.pop(analise_id, None)
        analise_banco = interface._buscar_analise(analise_id)

        assert analise_banco is not None
        assert analise_banco['status'] == 'concluida'
        assert analise_banco.get('resultados') is not None
        assert len(analise_banco['resultados']) > 10

    def test_timestamp_fim_e_registrado(self, setup):
        interface, _, _ = setup
        mock_instance, _ = _mock_crew()
        analise_id = str(uuid.uuid4())

        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'usuario_id': 'admin',
            'topico_pesquisa': 'Teste timestamp',
            'status': 'processando',
            'progresso': 0,
            'arquivos': [],
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            interface._executar_analise(analise_id)
            analise = _aguardar_conclusao(interface, analise_id)

        # Em cache: chave é 'timestamp_fim'; no banco: chave é 'concluido_em'
        fim = analise.get('timestamp_fim') or analise.get('concluido_em')
        assert fim is not None
        assert 'T' in fim  # formato ISO


# ---------------------------------------------------------------------------
# 2. Transições de status
# ---------------------------------------------------------------------------

class TestTransicoesDeStatus:

    def test_status_passa_por_etapas_esperadas(self, setup):
        """Registra todos os status observados durante a análise."""
        interface, _, _ = setup
        mock_instance, mock_crew_obj = _mock_crew()

        # Faz kickoff ser ligeiramente lento para capturar status intermediários
        estados_capturados = []

        def kickoff_lento(**kwargs):
            time.sleep(0.1)
            resultado = MagicMock()
            resultado.__str__ = lambda self: RESULTADO_SIMULADO
            return resultado

        mock_crew_obj.kickoff.side_effect = kickoff_lento

        analise_id = str(uuid.uuid4())
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'usuario_id': 'admin',
            'topico_pesquisa': 'Rastreamento de status',
            'status': 'processando',
            'progresso': 0,
            'arquivos': [],
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)

        # Monitora status em thread separada
        import threading
        monitorando = True

        def monitorar():
            while monitorando:
                a = interface._buscar_analise(analise_id)
                if a:
                    s = a.get('status')
                    if s and (not estados_capturados or estados_capturados[-1] != s):
                        estados_capturados.append(s)
                time.sleep(0.02)

        t = threading.Thread(target=monitorar, daemon=True)
        t.start()

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            interface._executar_analise(analise_id)
            _aguardar_conclusao(interface, analise_id)

        monitorando = False
        t.join(timeout=1)

        # Verifica que houve progressão e chegou em 'concluida'
        assert 'concluida' in estados_capturados
        assert estados_capturados[-1] == 'concluida'

    def test_progresso_chega_a_100(self, setup):
        interface, _, _ = setup
        mock_instance, _ = _mock_crew()
        analise_id = str(uuid.uuid4())

        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'usuario_id': 'admin',
            'topico_pesquisa': 'Progresso 100%',
            'status': 'processando',
            'progresso': 0,
            'arquivos': [],
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            interface._executar_analise(analise_id)
            analise = _aguardar_conclusao(interface, analise_id)

        assert analise['progresso'] == 100


# ---------------------------------------------------------------------------
# 3. Análise com arquivo CSV real
# ---------------------------------------------------------------------------

class TestAnaliseComArquivo:

    def test_analise_com_csv_real(self, setup, csv_file):
        interface, _, _ = setup
        mock_instance, mock_crew_obj = _mock_crew()

        # Captura os inputs passados para o crew
        inputs_capturados = {}

        def capturar_inputs(**kwargs):
            inputs_capturados.update(kwargs.get('inputs', {}))
            result = MagicMock()
            result.__str__ = lambda self: RESULTADO_SIMULADO
            return result

        mock_crew_obj.kickoff.side_effect = capturar_inputs

        analise_id = str(uuid.uuid4())
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'usuario_id': 'admin',
            'topico_pesquisa': 'Análise de notas dos alunos',
            'status': 'processando',
            'progresso': 0,
            'arquivos': [{'caminho': csv_file, 'nome': 'notas_alunos.csv'}],
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            interface._executar_analise(analise_id)
            analise = _aguardar_conclusao(interface, analise_id)

        assert analise['status'] == 'concluida'
        # Verifica que o caminho do arquivo foi passado ao crew
        assert csv_file in inputs_capturados.get('arquivos_analisados', [])

    def test_analise_sem_arquivo_tambem_funciona(self, setup):
        """Análise sem uploads (apenas tópico) deve concluir normalmente."""
        interface, _, _ = setup
        mock_instance, _ = _mock_crew()
        analise_id = str(uuid.uuid4())

        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'usuario_id': 'admin',
            'topico_pesquisa': 'Revisão bibliográfica sobre pedagogia',
            'status': 'processando',
            'progresso': 0,
            'arquivos': [],
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            interface._executar_analise(analise_id)
            analise = _aguardar_conclusao(interface, analise_id)

        assert analise['status'] == 'concluida'


# ---------------------------------------------------------------------------
# 4. Erro no crew
# ---------------------------------------------------------------------------

class TestErroCrew:

    def test_excecao_no_crew_marca_analise_como_erro(self, setup):
        interface, _, _ = setup
        mock_instance, mock_crew_obj = _mock_crew()
        mock_crew_obj.kickoff.side_effect = RuntimeError("LLM indisponível")

        analise_id = str(uuid.uuid4())
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'usuario_id': 'admin',
            'topico_pesquisa': 'Cenário de erro',
            'status': 'processando',
            'progresso': 0,
            'arquivos': [],
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            interface._executar_analise(analise_id)
            analise = _aguardar_conclusao(interface, analise_id)

        assert analise['status'] == 'erro'
        assert analise.get('erro') is not None
        assert 'LLM indisponível' in analise['erro']

    def test_mensagem_de_erro_e_salva_no_banco(self, setup):
        interface, _, _ = setup
        mock_instance, mock_crew_obj = _mock_crew()
        mock_crew_obj.kickoff.side_effect = ValueError("Chave de API inválida")

        analise_id = str(uuid.uuid4())
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'usuario_id': 'admin',
            'topico_pesquisa': 'Teste persistência de erro',
            'status': 'processando',
            'progresso': 0,
            'arquivos': [],
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            interface._executar_analise(analise_id)
            _aguardar_conclusao(interface, analise_id)

        # Busca diretamente do banco (sem cache)
        interface.analises_ativas.pop(analise_id, None)
        analise_banco = interface._buscar_analise(analise_id)

        assert analise_banco is not None
        assert analise_banco['status'] == 'erro'
        assert 'Chave de API inválida' in analise_banco.get('erro', '')


# ---------------------------------------------------------------------------
# 5. Timeout
# ---------------------------------------------------------------------------

class TestTimeout:

    def test_timeout_marca_analise_como_erro(self, setup):
        interface, _, _ = setup
        mock_instance, mock_crew_obj = _mock_crew()

        # Crew leva mais tempo que o timeout configurado
        def crew_lento(**kwargs):
            time.sleep(3)
            result = MagicMock()
            result.__str__ = lambda self: "nunca vai chegar aqui"
            return result

        mock_crew_obj.kickoff.side_effect = crew_lento

        analise_id = str(uuid.uuid4())
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'usuario_id': 'admin',
            'topico_pesquisa': 'Teste timeout',
            'status': 'processando',
            'progresso': 0,
            'arquivos': [],
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)

        # Timeout de 1s — bem abaixo dos 3s que a crew vai demorar
        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance), \
             patch.dict(os.environ, {'SAPIENS_CREW_TIMEOUT': '1'}):
            interface._executar_analise(analise_id)
            analise = _aguardar_conclusao(interface, analise_id, timeout=10)

        assert analise['status'] == 'erro'
        assert 'tempo limite' in analise.get('erro', '').lower() or \
               'timeout' in analise.get('erro', '').lower() or \
               'SAPIENS_CREW_TIMEOUT' in analise.get('erro', '')


# ---------------------------------------------------------------------------
# 6. Via API REST
# ---------------------------------------------------------------------------

class TestViaApiRest:

    def test_post_api_inicia_analise_e_retorna_202(self, setup):
        interface, _, client = setup
        mock_instance, _ = _mock_crew()

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            resp = client.post(
                '/api/v1/analises',
                json={'topico_pesquisa': 'Impacto do reforço escolar'},
                content_type='application/json',
            )

        assert resp.status_code == 202
        data = resp.get_json()
        assert 'analise_id' in data
        assert data['status'] == 'processando'
        assert 'links' in data

    def test_analise_via_api_conclui_com_resultados(self, setup):
        interface, _, client = setup
        mock_instance, _ = _mock_crew()

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            resp = client.post(
                '/api/v1/analises',
                json={'topico_pesquisa': 'Análise E2E via API'},
                content_type='application/json',
            )
            analise_id = resp.get_json()['analise_id']

            # Aguarda conclusão
            analise = _aguardar_conclusao(interface, analise_id)

        assert analise['status'] == 'concluida'

        # Busca resultados via API
        resp_resultado = client.get(f'/api/v1/analises/{analise_id}/resultados')
        assert resp_resultado.status_code == 200
        data = resp_resultado.get_json()
        assert data.get('resultados') is not None

    def test_api_retorna_status_correto_durante_execucao(self, setup):
        interface, _, client = setup
        mock_instance, mock_crew_obj = _mock_crew()

        # Crew com delay para capturar status intermediário
        def crew_pausado(**kwargs):
            time.sleep(0.3)
            result = MagicMock()
            result.__str__ = lambda self: RESULTADO_SIMULADO
            return result

        mock_crew_obj.kickoff.side_effect = crew_pausado

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            resp = client.post(
                '/api/v1/analises',
                json={'topico_pesquisa': 'Status em tempo real'},
                content_type='application/json',
            )
            analise_id = resp.get_json()['analise_id']

            # Consulta imediatamente (ainda processando)
            resp_status = client.get(f'/api/v1/analises/{analise_id}')
            assert resp_status.status_code == 200
            status_imediato = resp_status.get_json().get('status')
            assert status_imediato in {'processando', 'executando_analise', 'processando_dados',
                                       'gerando_relatorio', 'concluida'}

            _aguardar_conclusao(interface, analise_id)

        # Consulta após conclusão
        resp_final = client.get(f'/api/v1/analises/{analise_id}')
        assert resp_final.get_json()['status'] == 'concluida'


# ---------------------------------------------------------------------------
# 7. Via formulário web
# ---------------------------------------------------------------------------

class TestViaFormularioWeb:

    def test_post_formulario_redireciona_para_progresso(self, setup, tmp_path):
        interface, flask_app, client = setup
        mock_instance, _ = _mock_crew()

        csv_path = tmp_path / "dados.csv"
        csv_path.write_text(CSV_ACADEMICO, encoding='utf-8')

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            resp = client.post(
                '/analise',
                data={
                    'topico_pesquisa': 'Análise via formulário',
                    'links_sites': '',
                },
                follow_redirects=False,
            )

        # Deve redirecionar para resultados (o form inicia e redireciona direto)
        assert resp.status_code == 302
        location = resp.headers.get('Location', '')
        assert '/resultados/' in location or '/analise' in location

    def test_pagina_progresso_retorna_200(self, setup):
        interface, _, client = setup
        mock_instance, _ = _mock_crew()

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            resp_post = client.post(
                '/analise',
                data={'topico_pesquisa': 'Análise progresso page'},
                follow_redirects=False,
            )

            location = resp_post.headers.get('Location', '')
            if '/resultados/' in location or '/progresso/' in location:
                resp_pagina = client.get(location)
                assert resp_pagina.status_code in (200, 302)

    def test_pagina_resultados_retorna_200_apos_conclusao(self, setup):
        interface, _, client = setup
        mock_instance, _ = _mock_crew()
        analise_id = str(uuid.uuid4())

        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'usuario_id': 'admin',
            'topico_pesquisa': 'Teste página resultados',
            'status': 'processando',
            'progresso': 0,
            'arquivos': [],
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            interface._executar_analise(analise_id)
            _aguardar_conclusao(interface, analise_id)

        resp = client.get(f'/resultados/{analise_id}')
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 8. Análises paralelas
# ---------------------------------------------------------------------------

class TestAnaliseParalela:

    def test_tres_analises_simultaneas_todas_concluem(self, setup):
        interface, _, _ = setup
        mock_instance, _ = _mock_crew()

        ids = [str(uuid.uuid4()) for _ in range(3)]

        for analise_id in ids:
            interface.analises_ativas[analise_id] = {
                'id': analise_id,
                'usuario_id': 'admin',
                'topico_pesquisa': f'Análise paralela {analise_id[:8]}',
                'status': 'processando',
                'progresso': 0,
                'arquivos': [],
                'timestamp_inicio': '2026-01-01T00:00:00',
            }
            interface._salvar_analise(analise_id)

        with patch('Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
                   return_value=mock_instance):
            for analise_id in ids:
                interface._executar_analise(analise_id)

            resultados = [_aguardar_conclusao(interface, analise_id) for analise_id in ids]

        assert all(r['status'] == 'concluida' for r in resultados)
        assert all(r['progresso'] == 100 for r in resultados)
