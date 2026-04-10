"""
Testes para main.py, custom_tool.py e rotas web autenticadas.
Cobre as lacunas de cobertura nesses módulos.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# ---------------------------------------------------------------------------
# CustomTool (0% → 100%)
# ---------------------------------------------------------------------------

class TestCustomTool:
    def test_run_retorna_string(self):
        from Sapiens_MultiAgente.tools.custom_tool import MyCustomTool
        tool = MyCustomTool()
        result = tool._run(argument="qualquer argumento")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_instancia_com_nome_e_descricao(self):
        from Sapiens_MultiAgente.tools.custom_tool import MyCustomTool
        tool = MyCustomTool()
        assert tool.name
        assert tool.description


# ---------------------------------------------------------------------------
# main.py (19% → ~75%)
# ---------------------------------------------------------------------------

class TestMainModule:

    def _mock_crew(self):
        mock_crew = MagicMock()
        mock_instance = MagicMock()
        mock_instance.crew.return_value = mock_crew
        return mock_crew, mock_instance

    def test_run_chama_kickoff(self):
        from Sapiens_MultiAgente import main
        mock_crew, mock_instance = self._mock_crew()
        with patch(
            'Sapiens_MultiAgente.main.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
            return_value=mock_instance,
        ):
            main.run()
        mock_crew.kickoff.assert_called_once()
        call_kwargs = mock_crew.kickoff.call_args[1]
        assert 'topico_pesquisa' in call_kwargs.get('inputs', {})

    def test_train_chama_train(self):
        from Sapiens_MultiAgente import main
        mock_crew, mock_instance = self._mock_crew()
        with patch(
            'Sapiens_MultiAgente.main.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
            return_value=mock_instance,
        ), patch('sys.argv', ['main.py', '3', 'output.pkl']):
            main.train()
        mock_crew.train.assert_called_once_with(
            n_iterations=3, filename='output.pkl', inputs=mock_crew.train.call_args[1]['inputs']
        )

    def test_train_lanca_excecao_formatada(self):
        from Sapiens_MultiAgente import main
        mock_crew, mock_instance = self._mock_crew()
        mock_crew.train.side_effect = RuntimeError("Falha no treinamento")
        with patch(
            'Sapiens_MultiAgente.main.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
            return_value=mock_instance,
        ), patch('sys.argv', ['main.py', '3', 'output.pkl']):
            with pytest.raises(Exception, match="error occurred while training"):
                main.train()

    def test_replay_chama_replay(self):
        from Sapiens_MultiAgente import main
        mock_crew, mock_instance = self._mock_crew()
        with patch(
            'Sapiens_MultiAgente.main.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
            return_value=mock_instance,
        ), patch('sys.argv', ['main.py', 'task-id-xyz']):
            main.replay()
        mock_crew.replay.assert_called_once_with(task_id='task-id-xyz')

    def test_replay_lanca_excecao_formatada(self):
        from Sapiens_MultiAgente import main
        mock_crew, mock_instance = self._mock_crew()
        mock_crew.replay.side_effect = RuntimeError("Falha no replay")
        with patch(
            'Sapiens_MultiAgente.main.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
            return_value=mock_instance,
        ), patch('sys.argv', ['main.py', 'task-id-xyz']):
            with pytest.raises(Exception, match="error occurred while replaying"):
                main.replay()

    def test_test_chama_test(self):
        from Sapiens_MultiAgente import main
        mock_crew, mock_instance = self._mock_crew()
        with patch(
            'Sapiens_MultiAgente.main.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
            return_value=mock_instance,
        ), patch('sys.argv', ['main.py', '2', 'gpt-4']):
            main.test()
        mock_crew.test.assert_called_once_with(
            n_iterations=2, openai_model_name='gpt-4', inputs=mock_crew.test.call_args[1]['inputs']
        )

    def test_test_lanca_excecao_formatada(self):
        from Sapiens_MultiAgente import main
        mock_crew, mock_instance = self._mock_crew()
        mock_crew.test.side_effect = RuntimeError("Falha no teste")
        with patch(
            'Sapiens_MultiAgente.main.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
            return_value=mock_instance,
        ), patch('sys.argv', ['main.py', '2', 'gpt-4']):
            with pytest.raises(Exception, match="error occurred while testing"):
                main.test()


# ---------------------------------------------------------------------------
# Web — rotas autenticadas (web/app.py 40% → ~55%)
# ---------------------------------------------------------------------------

class TestWebRotasAutenticadas:
    """
    Testa rotas que requerem login usando o fluxo real de autenticação.
    O admin padrão (admin / sapiens@2025) é criado por init_auth_db().
    """

    @pytest.fixture
    def app(self, tmp_path):
        db_path = str(tmp_path / "test_sapiens.db")
        with patch('Sapiens_MultiAgente.web.app.DB_PATH', db_path), \
             patch('Sapiens_MultiAgente.web.auth.DB_PATH', db_path):
            from Sapiens_MultiAgente.web.app import SapiensWebInterface
            interface = SapiensWebInterface()
            flask_app = interface.create_app()
            flask_app.config['TESTING'] = True
            flask_app.config['WTF_CSRF_ENABLED'] = False
            yield flask_app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    @pytest.fixture
    def auth_client(self, client):
        """Cliente com sessão autenticada como admin."""
        client.post('/login', data={'username': 'admin', 'senha': 'sapiens@2025'})
        return client

    # Rotas públicas
    def test_sobre_retorna_200(self, client):
        resp = client.get('/sobre')
        assert resp.status_code == 200

    def test_health_check_sem_login_redireciona(self, client):
        resp = client.get('/api/health', follow_redirects=False)
        assert resp.status_code == 302

    def test_health_check_com_login_retorna_json(self, auth_client):
        resp = auth_client.get('/api/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'healthy'
        assert 'versao' in data
        assert 'banco_dados' in data

    def test_status_page_com_login_retorna_200(self, auth_client):
        resp = auth_client.get('/status')
        assert resp.status_code == 200

    def test_login_com_credenciais_corretas(self, client):
        resp = client.post(
            '/login',
            data={'username': 'admin', 'senha': 'sapiens@2025'},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert '/' in resp.headers['Location']

    # Rotas protegidas — redireciona sem login
    def test_index_sem_login_redireciona(self, client):
        resp = client.get('/', follow_redirects=False)
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']

    def test_historico_sem_login_redireciona(self, client):
        resp = client.get('/historico', follow_redirects=False)
        assert resp.status_code == 302

    def test_api_analises_sem_login_redireciona(self, client):
        resp = client.get('/api/v1/analises', follow_redirects=False)
        assert resp.status_code == 302

    # Rotas protegidas — acessíveis com login
    def test_index_com_login_retorna_200(self, auth_client):
        resp = auth_client.get('/')
        assert resp.status_code == 200

    def test_analise_get_com_login_retorna_200(self, auth_client):
        resp = auth_client.get('/analise')
        assert resp.status_code == 200

    def test_historico_com_login_retorna_200(self, auth_client):
        resp = auth_client.get('/historico')
        assert resp.status_code == 200

    def test_api_analises_get_com_login(self, auth_client):
        resp = auth_client.get('/api/v1/analises')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'analises' in data
        assert 'total' in data
        assert isinstance(data['analises'], list)

    def test_api_analises_get_com_filtro_status(self, auth_client):
        resp = auth_client.get('/api/v1/analises?status=concluida&limit=10')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'analises' in data

    def test_api_analise_inexistente_retorna_404(self, auth_client):
        resp = auth_client.get('/api/v1/analises/id-que-nao-existe-999')
        assert resp.status_code == 404
        assert 'error' in resp.get_json()

    def test_api_iniciar_analise_sem_topico_retorna_400(self, auth_client):
        resp = auth_client.post(
            '/api/v1/analises',
            json={},
            content_type='application/json',
        )
        assert resp.status_code == 400
        assert 'error' in resp.get_json()

    def test_api_resultados_analise_inexistente_retorna_404(self, auth_client):
        resp = auth_client.get('/api/v1/analises/inexistente-abc/resultados')
        assert resp.status_code == 404

    def test_logout_redireciona(self, auth_client):
        resp = auth_client.get('/logout', follow_redirects=False)
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']

    def test_upload_sem_arquivo_retorna_400(self, auth_client):
        resp = auth_client.post('/upload', data={})
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'error' in data

    def test_status_analise_inexistente_retorna_404(self, auth_client):
        resp = auth_client.get('/status/analise-inexistente-xyz')
        assert resp.status_code == 404

    def test_resultados_analise_inexistente_retorna_404(self, auth_client):
        resp = auth_client.get('/resultados/analise-inexistente-xyz')
        assert resp.status_code in (302, 404)

    def test_export_analise_inexistente_retorna_404(self, auth_client):
        resp = auth_client.get('/export/analise-inexistente-xyz/pdf')
        assert resp.status_code == 404

    def test_export_formato_invalido_retorna_400(self, auth_client, tmp_path):
        """Cria uma análise falsa no banco e testa formato inválido."""
        import sqlite3, json, uuid
        from unittest.mock import patch
        analise_id = str(uuid.uuid4())
        db_path = str(tmp_path / "test_sapiens.db")
        with patch('Sapiens_MultiAgente.web.app.DB_PATH', db_path), \
             patch('Sapiens_MultiAgente.web.auth.DB_PATH', db_path):
            import sqlite3 as _sq
            with _sq.connect(db_path) as conn:
                conn.execute(
                    "INSERT INTO analises (id, usuario_id, topico, status, progresso, arquivos, criado_em) "
                    "VALUES (?, 'admin', 'Teste', 'concluida', 100, '[]', '2026-01-01T00:00:00')",
                    (analise_id,)
                )
                conn.commit()
        resp = auth_client.get(f'/export/{analise_id}/xml')
        assert resp.status_code == 400

    def test_stream_analise_inexistente_retorna_200_sse(self, auth_client):
        # SSE sempre retorna 200; análise inexistente envia evento de erro no stream
        resp = auth_client.get('/stream/analise-inexistente-xyz')
        assert resp.status_code == 200
        assert 'text/event-stream' in resp.content_type
