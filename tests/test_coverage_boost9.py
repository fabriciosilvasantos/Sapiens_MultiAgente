"""
Boost de cobertura — Rodada 9.
Alvos em web/app.py (97% → ~99%):

- Linha 233-234 : except Exception no filtro fmt_dt (string inválida)
- Linha 383-384 : except Exception no health check quando DB falha
- Linha 409     : render_template('status.html') quando Accept: text/html
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def app_client(tmp_path):
    db_path = str(tmp_path / "test.db")
    with patch('Sapiens_MultiAgente.web.app.DB_PATH', db_path), \
         patch('Sapiens_MultiAgente.web.auth.DB_PATH', db_path):
        from Sapiens_MultiAgente.web.app import SapiensWebInterface
        interface = SapiensWebInterface()
        flask_app = interface.create_app()
        flask_app.config['TESTING'] = True
        flask_app.config['WTF_CSRF_ENABLED'] = False
        client = flask_app.test_client()
        client.post('/login', data={'username': 'admin', 'senha': 'sapiens@2025'})
        yield flask_app, client


# ---------------------------------------------------------------------------
# Linha 233-234: except Exception no filtro fmt_dt
# ---------------------------------------------------------------------------

class TestFmtDtFiltro:
    def test_fmt_dt_com_string_invalida_retorna_string_original(self, app_client):
        """Quando fmt_dt recebe algo que não pode ser parseado, retorna o valor truncado."""
        flask_app, _ = app_client
        with flask_app.app_context():
            fmt_dt = flask_app.jinja_env.filters['fmt_dt']
            # String que falha no strptime (não é data) — slice [:19] = 'nao-e-uma-data-vali'
            resultado = fmt_dt('nao-e-uma-data-valida-xxxx')
            assert resultado == 'nao-e-uma-data-vali'

    def test_fmt_dt_com_none_retorna_vazio(self, app_client):
        flask_app, _ = app_client
        with flask_app.app_context():
            fmt_dt = flask_app.jinja_env.filters['fmt_dt']
            assert fmt_dt(None) == ''
            assert fmt_dt('') == ''

    def test_fmt_dt_com_formato_invalido_sem_separador(self, app_client):
        """String que passa o slice mas falha o strptime — exercita o except."""
        flask_app, _ = app_client
        with flask_app.app_context():
            fmt_dt = flask_app.jinja_env.filters['fmt_dt']
            # 19 chars mas não é data válida
            resultado = fmt_dt('XXXXXXXXXXXXXXXXXXX')
            assert resultado == 'XXXXXXXXXXXXXXXXXXX'


# ---------------------------------------------------------------------------
# Linha 383-384: except Exception no health check quando DB falha
# ---------------------------------------------------------------------------

class TestHealthCheckDbFalha:
    def test_health_check_com_db_falhando(self, app_client):
        """Quando o DB_PATH aponta para diretório inexistente, health check retorna banco_dados='error'."""
        flask_app, client = app_client
        # Aponta DB_PATH para um caminho inválido (diretório que não existe)
        with patch('Sapiens_MultiAgente.web.app.DB_PATH', '/caminho/inexistente/sapiens.db'):
            resp = client.get('/api/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'healthy'
        assert data['banco_dados'] == 'erro'


# ---------------------------------------------------------------------------
# Linha 409: render_template('status.html') quando Accept: text/html
# ---------------------------------------------------------------------------

class TestStatusHtmlBranch:
    def test_status_com_accept_html_renderiza_template(self, app_client):
        """Quando cliente envia Accept: text/html, /status retorna HTML em vez de JSON."""
        _, client = app_client
        resp = client.get('/status', headers={'Accept': 'text/html'})
        assert resp.status_code == 200
        assert b'SAPIENS' in resp.data or b'status' in resp.data.lower()
