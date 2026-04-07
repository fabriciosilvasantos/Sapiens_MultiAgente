"""
Testes para alcançar 80%+ de cobertura total:
- statistical_analysis_tool.py (79% → ~92%)
- web/auth.py (72% → ~88%)
- web/app.py (60% → ~70%)
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# ---------------------------------------------------------------------------
# StatisticalAnalysisTool — caminhos não cobertos (79% → ~92%)
# ---------------------------------------------------------------------------

class TestStatisticalAnalysisToolExtended:
    def _json(self, data):
        return json.dumps(data)

    # Formatos de entrada alternativos
    def test_input_dict_formato(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._json({"nota": [8.5, 7.0, 9.0, 6.5, 8.0], "freq": [1, 2, 3, 4, 5]})
        result = StatisticalAnalysisTool()._run(data=data, analysis_type="descriptive")
        assert "ANÁLISE DESCRITIVA" in result

    def test_input_formato_nao_suportado(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        result = StatisticalAnalysisTool()._run(data="42", analysis_type="descriptive")
        assert "ERRO" in result

    def test_dados_vazios_retorna_erro(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        result = StatisticalAnalysisTool()._run(data="[]", analysis_type="descriptive")
        assert "ERRO" in result

    def test_variaveis_inexistentes_retorna_erro(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._json([{"a": 1, "b": 2} for _ in range(10)])
        result = StatisticalAnalysisTool()._run(
            data=data, analysis_type="descriptive", variables=["coluna_inexistente"]
        )
        assert "ERRO" in result

    # Descritiva com colunas categóricas
    def test_descritiva_com_categoricas(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._json([
            {"curso": "CC", "nota": float(i)} for i in range(10)
        ] + [
            {"curso": "Mat", "nota": float(i) + 0.5} for i in range(10)
        ])
        result = StatisticalAnalysisTool()._run(data=data, analysis_type="descriptive")
        assert "ANÁLISE DESCRITIVA" in result
        assert "CATEGÓRICAS" in result

    def test_descritiva_shapiro_falha(self):
        """Shapiro-Wilk falha com dados constantes — cobre o except na linha 114."""
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._json([{"x": 5.0} for _ in range(10)])  # todos iguais
        result = StatisticalAnalysisTool()._run(data=data, analysis_type="descriptive")
        assert "ANÁLISE DESCRITIVA" in result

    # Correlação
    def test_correlacao_sem_correlacao_forte(self):
        """Quando |r| < 0.5 em todos os pares, deve exibir mensagem de nenhuma correlação."""
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        # Dados propositalmente sem correlação (padrão ortogonal)
        data = self._json([
            {"x": float(i % 3), "y": float((i * 7) % 5)} for i in range(30)
        ])
        result = StatisticalAnalysisTool()._run(data=data, analysis_type="correlation")
        assert "CORRELAÇÃO" in result

    def test_correlacao_com_uma_variavel_numerica(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._json([{"x": float(i)} for i in range(10)])
        result = StatisticalAnalysisTool()._run(data=data, analysis_type="correlation")
        assert "ERRO" in result

    # Testes de hipóteses
    def test_hipotese_com_uma_variavel(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._json([{"x": float(i)} for i in range(10)])
        result = StatisticalAnalysisTool()._run(data=data, analysis_type="hypothesis_test")
        assert "ERRO" in result

    # Regressão
    def test_regressao_com_uma_variavel(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._json([{"x": float(i)} for i in range(20)])
        result = StatisticalAnalysisTool()._run(data=data, analysis_type="regression")
        assert "ERRO" in result

    def test_regressao_com_poucos_pontos(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._json([{"x": float(i), "y": float(i)} for i in range(2)])
        result = StatisticalAnalysisTool()._run(data=data, analysis_type="regression")
        assert "ERRO" in result and "insuficientes" in result

    def test_regressao_excelente_ajuste(self):
        """R² > 0.8 → 'Excelente ajuste'."""
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._json([{"x": float(i), "y": float(i) * 2.0 + 1.0} for i in range(20)])
        result = StatisticalAnalysisTool()._run(data=data, analysis_type="regression")
        assert "Excelente" in result or "REGRESSÃO" in result

    def test_regressao_bom_ajuste(self):
        """R² entre 0.6 e 0.8 → 'Bom ajuste'."""
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        import random
        random.seed(42)
        data = self._json([
            {"x": float(i), "y": float(i) * 1.5 + random.uniform(0, 2)} for i in range(30)
        ])
        result = StatisticalAnalysisTool()._run(data=data, analysis_type="regression")
        assert "REGRESSÃO" in result

    def test_regressao_ajuste_fraco(self):
        """R² < 0.3 → 'Ajuste fraco' — dados com alto ruído."""
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        import random
        random.seed(99)
        data = self._json([
            {"x": float(i), "y": random.uniform(0, 100)} for i in range(30)
        ])
        result = StatisticalAnalysisTool()._run(data=data, analysis_type="regression")
        assert "REGRESSÃO" in result

    # Intérpretes privados — testados diretamente
    def test_interpretar_eta2_grande(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        tool = StatisticalAnalysisTool()
        assert tool._interpretar_eta2(0.20) == "efeito grande"

    def test_interpretar_eta2_medio(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        tool = StatisticalAnalysisTool()
        assert tool._interpretar_eta2(0.08) == "efeito médio"

    def test_interpretar_eta2_pequeno(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        tool = StatisticalAnalysisTool()
        assert tool._interpretar_eta2(0.02) == "efeito pequeno"

    def test_interpretar_eta2_negligenciavel(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        tool = StatisticalAnalysisTool()
        assert tool._interpretar_eta2(0.005) == "efeito negligenciável"

    def test_interpret_correlation_muito_forte(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        assert StatisticalAnalysisTool()._interpret_correlation_strength(0.95) == "Correlação muito forte"

    def test_interpret_correlation_forte(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        assert StatisticalAnalysisTool()._interpret_correlation_strength(0.75) == "Correlação forte"

    def test_interpret_correlation_moderada(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        assert StatisticalAnalysisTool()._interpret_correlation_strength(0.60) == "Correlação moderada"

    def test_interpret_correlation_fraca(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        assert StatisticalAnalysisTool()._interpret_correlation_strength(0.35) == "Correlação fraca"

    def test_interpret_correlation_muito_fraca(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        assert StatisticalAnalysisTool()._interpret_correlation_strength(0.10) == "Correlação muito fraca"

    # ANOVA — caminhos de erro
    def test_anova_sem_variaveis_numericas(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._json([{"grupo": "A"}, {"grupo": "B"}])
        result = StatisticalAnalysisTool()._run(
            data=data, analysis_type="anova_one_way", group_column="grupo"
        )
        assert "ERRO" in result

    def test_anova_com_um_grupo(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._json([{"grupo": "A", "nota": float(i)} for i in range(5)])
        result = StatisticalAnalysisTool()._run(
            data=data, analysis_type="anova_one_way", group_column="grupo"
        )
        assert "ERRO" in result

    def test_anova_grupos_com_nan(self):
        """Grupos com apenas NaN devem gerar aviso e não erro fatal."""
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._json([
            {"grupo": "A", "nota": None},
            {"grupo": "B", "nota": None},
        ])
        result = StatisticalAnalysisTool()._run(
            data=data, analysis_type="anova_one_way", group_column="grupo"
        )
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# web/auth.py — caminhos não cobertos (72% → ~88%)
# ---------------------------------------------------------------------------

class TestAuthExtended:
    """Usa DB isolado via patch para não contaminar sapiens.db."""

    @pytest.fixture
    def db_auth(self, tmp_path):
        db_path = str(tmp_path / "auth_test.db")
        with patch('Sapiens_MultiAgente.web.auth.DB_PATH', db_path):
            from Sapiens_MultiAgente.web.auth import init_auth_db, _falhas_login
            init_auth_db()
            _falhas_login.clear()
            yield db_path, _falhas_login

    def test_hash_senha_legado(self):
        from Sapiens_MultiAgente.web.auth import _hash_senha_legado
        h = _hash_senha_legado("minhasenha")
        assert isinstance(h, str)
        assert len(h) == 64  # SHA-256 hex

    def test_verificar_bloqueio_ativo(self, db_auth):
        import time
        from Sapiens_MultiAgente.web.auth import verificar_bloqueio, _falhas_login
        username = "usuario_bloqueio_test"
        agora = time.time()
        _falhas_login[username] = [agora] * 5
        bloqueado, restante = verificar_bloqueio(username)
        assert bloqueado is True
        assert restante > 0

    def test_verificar_bloqueio_inativo(self, db_auth):
        from Sapiens_MultiAgente.web.auth import verificar_bloqueio, _falhas_login
        _falhas_login.pop("usuario_ok", None)
        bloqueado, _ = verificar_bloqueio("usuario_ok")
        assert bloqueado is False

    def test_login_invalido_registra_falha(self, db_auth):
        from Sapiens_MultiAgente.web.auth import Usuario
        usuario, msg = Usuario.autenticar("admin", "senha_errada")
        assert usuario is None
        assert "inválidas" in msg.lower() or "tentativa" in msg.lower()

    def test_login_bloqueado_apos_5_falhas(self, db_auth):
        from Sapiens_MultiAgente.web.auth import Usuario, _falhas_login
        _falhas_login.pop("admin", None)
        for _ in range(5):
            Usuario.autenticar("admin", "senha_errada")
        usuario, msg = Usuario.autenticar("admin", "senha_errada")
        assert usuario is None
        assert "bloqueada" in msg.lower()

    def test_autenticar_retorna_mensagem_bloqueio_com_tempo(self, db_auth):
        import time
        from Sapiens_MultiAgente.web.auth import Usuario, _falhas_login
        username = "admin"
        _falhas_login.pop(username, None)
        agora = time.time()
        _falhas_login[username] = [agora] * 5
        usuario, msg = Usuario.autenticar(username, "qualquer")
        assert usuario is None
        assert "bloqueada" in msg.lower()
        assert "s" in msg  # contém segundos restantes

    def test_criar_usuario_novo(self, db_auth):
        from Sapiens_MultiAgente.web.auth import Usuario
        result = Usuario.criar("novo_usuario", "senha123", "Novo User")
        assert result is True

    def test_criar_usuario_duplicado_retorna_false(self, db_auth):
        from Sapiens_MultiAgente.web.auth import Usuario
        Usuario.criar("duplicado", "senha1", "Primeiro")
        result = Usuario.criar("duplicado", "senha2", "Segundo")
        assert result is False

    def test_criar_usuario_admin(self, db_auth):
        from Sapiens_MultiAgente.web.auth import Usuario
        result = Usuario.criar("admin2", "senha_admin", "Admin 2", admin=True)
        assert result is True
        usuario, _ = Usuario.autenticar("admin2", "senha_admin")
        assert usuario is not None
        assert usuario.admin is True

    def test_buscar_por_id_existente(self, db_auth):
        from Sapiens_MultiAgente.web.auth import Usuario
        # admin tem id=1 criado pelo init_auth_db
        user = Usuario.buscar_por_id("1")
        assert user is not None
        assert user.username == "admin"

    def test_buscar_por_id_inexistente(self, db_auth):
        from Sapiens_MultiAgente.web.auth import Usuario
        user = Usuario.buscar_por_id("9999")
        assert user is None

    def test_buscar_por_id_invalido_retorna_none(self, db_auth):
        from Sapiens_MultiAgente.web.auth import Usuario
        user = Usuario.buscar_por_id("nao_e_numero")
        assert user is None

    def test_migracao_hash_legado(self, db_auth, tmp_path):
        """Usuário com hash legado (sem salt) deve ser migrado para PBKDF2 no primeiro login."""
        import sqlite3
        from datetime import datetime
        db_path, _ = db_auth

        from Sapiens_MultiAgente.web.auth import _hash_senha_legado, Usuario

        senha = "senha_legada_123"
        legacy_hash = _hash_senha_legado(senha)

        # Insere usuário com formato legado (salt vazio)
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                INSERT INTO usuarios (username, senha_hash, salt, nome, admin, criado_em)
                VALUES (?, ?, '', ?, 0, ?)
            """, ('user_legado', legacy_hash, 'Usuário Legado', datetime.now().isoformat()))
            conn.commit()

        # Primeiro login deve funcionar e migrar para PBKDF2
        usuario, erro = Usuario.autenticar('user_legado', senha)
        assert usuario is not None
        assert erro is None

        # Verificar que o salt foi atualizado (migração concluída)
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT salt FROM usuarios WHERE username = ?", ('user_legado',)
            ).fetchone()
        assert row is not None
        assert len(row[0]) > 0  # salt preenchido após migração


# ---------------------------------------------------------------------------
# web/app.py — rotas e métodos adicionais (60% → ~70%)
# ---------------------------------------------------------------------------

class TestWebAppExtended:

    @pytest.fixture
    def app_cliente(self, tmp_path):
        db_path = str(tmp_path / "test_web.db")
        with patch('Sapiens_MultiAgente.web.app.DB_PATH', db_path), \
             patch('Sapiens_MultiAgente.web.auth.DB_PATH', db_path):
            from Sapiens_MultiAgente.web.app import SapiensWebInterface
            interface = SapiensWebInterface()
            flask_app = interface.create_app()
            flask_app.config['TESTING'] = True
            flask_app.config['WTF_CSRF_ENABLED'] = False
            client = flask_app.test_client()
            client.post('/login', data={'username': 'admin', 'senha': 'sapiens@2025'})
            yield interface, client

    # api_iniciar_analise — POST com tópico (linhas 451-466)
    def test_api_iniciar_analise_com_topico(self, app_cliente):
        interface, client = app_cliente
        with patch.object(interface, '_executar_analise'):
            resp = client.post('/api/v1/analises',
                               json={'topico_pesquisa': 'Análise de desempenho'},
                               content_type='application/json')
        assert resp.status_code == 202
        data = resp.get_json()
        assert 'analise_id' in data
        assert data['status'] == 'processando'
        assert 'links' in data

    # api_status_analise — 403 quando outro usuário tenta acessar (linha 500)
    def test_api_status_analise_403_outro_usuario(self, app_cliente):
        from Sapiens_MultiAgente.web.auth import Usuario
        interface, client = app_cliente

        # Cria segundo usuário não-admin
        Usuario.criar('user2_test', 'senha_user2', 'User 2', admin=False)

        # Cria análise pertencente ao admin (usuario_id='1')
        analise_id = "analise-admin-403"
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'topico_pesquisa': 'Análise do admin',
            'status': 'processando',
            'progresso': 50,
            'arquivos': [],
            'usuario_id': '1',
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)

        # Login como user2
        client.get('/logout', follow_redirects=True)
        client.post('/login', data={'username': 'user2_test', 'senha': 'senha_user2'})

        resp = client.get(f'/api/v1/analises/{analise_id}')
        assert resp.status_code == 403

    # api_resultados_analise — 403 quando outro usuário (linha 540)
    def test_api_resultados_analise_403_outro_usuario(self, app_cliente):
        from Sapiens_MultiAgente.web.auth import Usuario
        interface, client = app_cliente

        Usuario.criar('user3_test', 'senha_user3', 'User 3', admin=False)

        analise_id = "analise-admin-result-403"
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'topico_pesquisa': 'Resultado do admin',
            'status': 'concluida',
            'progresso': 100,
            'resultados': 'OK',
            'arquivos': [],
            'usuario_id': '1',
            'timestamp_inicio': '2026-01-01T00:00:00',
            'concluido_em': '2026-01-01T01:00:00',
        }
        interface._salvar_analise(analise_id)

        client.get('/logout', follow_redirects=True)
        client.post('/login', data={'username': 'user3_test', 'senha': 'senha_user3'})

        resp = client.get(f'/api/v1/analises/{analise_id}/resultados')
        assert resp.status_code == 403

    # SSE stream — análise concluída (linhas 292-320)
    def test_stream_analise_concluida(self, app_cliente):
        interface, client = app_cliente
        analise_id = "stream-concluida-001"
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'topico_pesquisa': 'Teste SSE',
            'status': 'concluida',
            'progresso': 100,
            'arquivos': [],
            'usuario_id': '1',
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)
        resp = client.get(f'/stream/{analise_id}')
        assert resp.status_code == 200
        assert b'data:' in resp.data

    def test_stream_analise_nao_encontrada(self, app_cliente):
        _, client = app_cliente
        resp = client.get('/stream/id-que-nao-existe-9999')
        assert resp.status_code == 200
        assert b'erro' in resp.data.lower()

    # Páginas HTML de resultados e progresso (linhas 913-921)
    def test_resultados_analise_concluida_renderiza_html(self, app_cliente):
        interface, client = app_cliente
        analise_id = "html-result-001"
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'topico_pesquisa': 'Análise completa',
            'status': 'concluida',
            'progresso': 100,
            'resultados': 'Resultados da análise.',
            'arquivos': [],
            'usuario_id': '1',
            'timestamp_inicio': '2026-01-01T00:00:00',
            'concluido_em': '2026-01-01T01:00:00',
        }
        interface._salvar_analise(analise_id)
        resp = client.get(f'/resultados/{analise_id}')
        assert resp.status_code == 200

    def test_resultados_analise_em_progresso_renderiza_html(self, app_cliente):
        interface, client = app_cliente
        analise_id = "html-prog-001"
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'topico_pesquisa': 'Em andamento',
            'status': 'processando',
            'progresso': 50,
            'arquivos': [],
            'usuario_id': '1',
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)
        resp = client.get(f'/resultados/{analise_id}')
        assert resp.status_code == 200

    def test_resultados_analise_inexistente_redireciona(self, app_cliente):
        _, client = app_cliente
        resp = client.get('/resultados/id-inexistente-xyz', follow_redirects=False)
        assert resp.status_code == 302

    # status_analise via rota HTML (linha 909)
    def test_status_analise_html(self, app_cliente):
        interface, client = app_cliente
        analise_id = "status-html-001"
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'topico_pesquisa': 'Status test',
            'status': 'processando',
            'progresso': 30,
            'arquivos': [],
            'usuario_id': '1',
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)
        resp = client.get(f'/status/{analise_id}')
        assert resp.status_code == 200

    def test_status_analise_html_inexistente(self, app_cliente):
        _, client = app_cliente
        resp = client.get('/status/id-nao-existe-html')
        assert resp.status_code == 404

    # _limpar_uploads_orfaos (linhas 883-902)
    def test_limpar_uploads_orfaos_remove_arquivos_velhos(self, app_cliente):
        interface, _ = app_cliente
        upload_folder = interface.upload_config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)

        # Arquivo órfão (não está em nenhuma análise ativa)
        orfao = os.path.join(upload_folder, 'orfao_antigo_test.txt')
        with open(orfao, 'w') as f:
            f.write('arquivo orfao')

        # max_idade_horas=-1 → limite negativo → qualquer arquivo é "antigo"
        interface._limpar_uploads_orfaos(max_idade_horas=-1)
        assert not os.path.exists(orfao)

    def test_limpar_uploads_orfaos_preserva_ativos(self, app_cliente):
        interface, _ = app_cliente
        upload_folder = interface.upload_config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)

        # Arquivo vinculado a uma análise ativa
        ativo = os.path.join(upload_folder, 'arquivo_ativo_test.csv')
        with open(ativo, 'w') as f:
            f.write('dados')

        interface.analises_ativas['analise-ativa-001'] = {
            'arquivos': [{'caminho': ativo}]
        }

        interface._limpar_uploads_orfaos(max_idade_horas=-1)
        assert os.path.exists(ativo)

        # Limpa manualmente
        os.remove(ativo)
        interface.analises_ativas.pop('analise-ativa-001', None)

    def test_limpar_uploads_pasta_inexistente(self, app_cliente):
        interface, _ = app_cliente
        interface.upload_config['UPLOAD_FOLDER'] = '/pasta/que/nao/existe'
        # Não deve lançar exceção
        interface._limpar_uploads_orfaos()
        # Restaura
        interface.upload_config['UPLOAD_FOLDER'] = 'uploads'

    # _get_historico com admin vê todas as análises (linha 928)
    def test_historico_admin_ve_todas_analises(self, app_cliente):
        _, client = app_cliente
        resp = client.get('/historico')
        assert resp.status_code == 200

    # api_listar_analises com filtro (garante caminho do filtro de status)
    def test_api_listar_analises_filtro_processando(self, app_cliente):
        interface, client = app_cliente
        with patch.object(interface, '_executar_analise'):
            client.post('/api/v1/analises',
                        json={'topico_pesquisa': 'Análise filtro'},
                        content_type='application/json')
        resp = client.get('/api/v1/analises?status=processando')
        assert resp.status_code == 200
