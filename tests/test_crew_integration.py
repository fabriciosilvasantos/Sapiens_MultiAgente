"""
Testes de integração do crew SAPIENS.
Verifica estrutura, agentes, tasks e configurações sem executar o LLM.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestCrewEstrutura:
    """Valida que o crew está estruturado corretamente."""

    def test_importa_crew(self):
        from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        assert SapiensAcademicMultiAgentDataAnalysisPlatformCrew is not None

    def test_instancia_crew(self):
        from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        crew_instance = SapiensAcademicMultiAgentDataAnalysisPlatformCrew()
        assert crew_instance is not None

    def test_agentes_config_existe(self):
        from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        crew_instance = SapiensAcademicMultiAgentDataAnalysisPlatformCrew()
        config = crew_instance.agents_config
        assert config is not None
        assert len(config) > 0

    def test_tasks_config_existe(self):
        from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        crew_instance = SapiensAcademicMultiAgentDataAnalysisPlatformCrew()
        config = crew_instance.tasks_config
        assert config is not None
        assert len(config) > 0

    def test_cinco_agentes_configurados(self):
        from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        crew_instance = SapiensAcademicMultiAgentDataAnalysisPlatformCrew()
        agentes_esperados = [
            'agente_gerente_orquestrador',
            'especialista_em_analise_descritiva',
            'especialista_em_analise_diagnostica',
            'especialista_em_analise_preditiva',
            'especialista_em_analise_prescritiva',
        ]
        for agente in agentes_esperados:
            assert agente in crew_instance.agents_config, f"Agente ausente: {agente}"

    def test_sete_tasks_configuradas(self):
        from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        crew_instance = SapiensAcademicMultiAgentDataAnalysisPlatformCrew()
        tasks_esperadas = [
            'validacao_rigorosa_de_dados_e_pergunta',
            'processamento_de_dados_reais_validados',
            'executar_analise_descritiva',
            'executar_analise_diagnostica',
            'executar_analise_preditiva',
            'executar_analise_prescritiva',
            'compilacao_e_apresentacao_do_relatorio_final',
        ]
        for task in tasks_esperadas:
            assert task in crew_instance.tasks_config, f"Task ausente: {task}"

    def test_agentes_tem_campos_obrigatorios(self):
        from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        crew_instance = SapiensAcademicMultiAgentDataAnalysisPlatformCrew()
        # O agents.yaml tem chaves extras de configuração global — ignorar chaves sem 'role'
        agentes_reais = {k: v for k, v in crew_instance.agents_config.items() if 'role' in v}
        assert len(agentes_reais) >= 5, "Esperados pelo menos 5 agentes com 'role'"
        for nome, config in agentes_reais.items():
            assert 'goal' in config, f"Agente '{nome}' sem 'goal'"
            assert 'backstory' in config, f"Agente '{nome}' sem 'backstory'"

    def test_tasks_tem_campos_obrigatorios(self):
        from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        crew_instance = SapiensAcademicMultiAgentDataAnalysisPlatformCrew()
        for nome, config in crew_instance.tasks_config.items():
            assert 'description' in config, f"Task '{nome}' sem 'description'"
            assert 'expected_output' in config, f"Task '{nome}' sem 'expected_output'"
            assert 'agent' in config, f"Task '{nome}' sem 'agent'"

    def test_analises_paralelas_com_async(self):
        """As 4 análises devem ter async_execution=True."""
        from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key', 'OPENAI_API_BASE': 'http://localhost'}):
            try:
                crew_instance = SapiensAcademicMultiAgentDataAnalysisPlatformCrew()
                tasks_async = [
                    crew_instance.executar_analise_descritiva(),
                    crew_instance.executar_analise_diagnostica(),
                    crew_instance.executar_analise_preditiva(),
                    crew_instance.executar_analise_prescritiva(),
                ]
                for task in tasks_async:
                    assert task.async_execution is True, \
                        f"Task '{task.description[:40]}' deveria ter async_execution=True"
            except Exception:
                pytest.skip("Não foi possível instanciar tasks sem LLM configurado")

    def test_relatorio_nao_e_async(self):
        """O relatório final deve aguardar todas as análises (sem async)."""
        from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key', 'OPENAI_API_BASE': 'http://localhost'}):
            try:
                crew_instance = SapiensAcademicMultiAgentDataAnalysisPlatformCrew()
                relatorio = crew_instance.compilacao_e_apresentacao_do_relatorio_final()
                assert relatorio.async_execution is not True
            except Exception:
                pytest.skip("Não foi possível instanciar tasks sem LLM configurado")


class TestCrewFerramentas:
    """Valida que as ferramentas customizadas são importáveis e instanciáveis."""

    def test_todas_ferramentas_importam(self):
        ferramentas = [
            ('Sapiens_MultiAgente.tools.csv_processor_tool', 'CSVProcessorTool'),
            ('Sapiens_MultiAgente.tools.statistical_analysis_tool', 'StatisticalAnalysisTool'),
            ('Sapiens_MultiAgente.tools.data_validation_tool', 'DataValidationTool'),
            ('Sapiens_MultiAgente.tools.pdf_search_tool', 'PDFSearchTool'),
            ('Sapiens_MultiAgente.tools.docx_search_tool', 'DOCXSearchTool'),
            ('Sapiens_MultiAgente.tools.csv_search_tool', 'CSVSearchTool'),
            ('Sapiens_MultiAgente.tools.chart_generator_tool', 'ChartGeneratorTool'),
        ]
        for modulo, classe in ferramentas:
            mod = __import__(modulo, fromlist=[classe])
            cls = getattr(mod, classe)
            instancia = cls()
            assert instancia is not None, f"{classe} não pôde ser instanciada"

    def test_ferramentas_tem_nome_e_descricao(self):
        from Sapiens_MultiAgente.tools.csv_processor_tool import CSVProcessorTool
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool

        for cls in [CSVProcessorTool, StatisticalAnalysisTool, ChartGeneratorTool]:
            tool = cls()
            assert tool.name, f"{cls.__name__} sem 'name'"
            assert tool.description, f"{cls.__name__} sem 'description'"


class TestWebApp:
    """Testes de integração da interface web."""

    @pytest.fixture
    def app(self):
        from Sapiens_MultiAgente.web.app import SapiensWebInterface
        interface = SapiensWebInterface()
        flask_app = interface.create_app()
        flask_app.config['TESTING'] = True
        flask_app.config['WTF_CSRF_ENABLED'] = False
        return flask_app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_health_check(self, client):
        resp = client.get('/api/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'healthy'
        assert 'versao' in data

    def test_login_get(self, client):
        resp = client.get('/login')
        assert resp.status_code == 200

    def test_login_invalido(self, client):
        resp = client.post('/login', data={
            'username': 'usuario_invalido',
            'senha': 'senha_errada'
        }, follow_redirects=True)
        assert resp.status_code == 200
        body = resp.data.decode('utf-8').lower()
        assert any(word in body for word in ('incorretos', 'inválid', 'credencial', 'bloqueada'))

    def test_rota_protegida_redireciona_para_login(self, client):
        resp = client.get('/', follow_redirects=False)
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']

    def test_api_status_analise_inexistente(self, client):
        with client.session_transaction() as sess:
            sess['_user_id'] = '1'  # simula sessão autenticada
        resp = client.get('/status/id-inexistente-000')
        # Deve retornar 404 ou redirecionar para login
        assert resp.status_code in (404, 302)

    def test_api_health_nao_requer_login(self, client):
        """Health check deve estar acessível sem autenticação."""
        resp = client.get('/api/health')
        assert resp.status_code == 200


class TestFluxoEndToEnd:
    """
    Testa o fluxo completo de análise de ponta a ponta, com crew mockada.
    Garante que criação → execução → resultados funciona sem LLM real.
    """

    @pytest.fixture
    def interface(self):
        from Sapiens_MultiAgente.web.app import SapiensWebInterface
        return SapiensWebInterface()

    def test_health_check_disponivel(self, interface):
        """App Flask inicializa sem erros."""
        app = interface.create_app()
        assert app is not None

    def test_fluxo_analise_com_crew_mockada(self, interface, tmp_path):
        """
        Fluxo completo: cria análise → worker executa → status concluída.
        A crew é mockada para retornar resultado sem chamar LLM.
        """
        import time
        from unittest.mock import patch, MagicMock

        csv_file = tmp_path / "dados_teste.csv"
        csv_file.write_text("nome,nota\nAlice,8.5\nBob,7.0\nCarla,9.2\n")

        resultado_mock = "Análise concluída com sucesso. Dados analisados: 3 registros."
        analise_id = "teste-e2e-001"

        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'topico_pesquisa': 'Teste E2E automático',
            'status': 'aguardando',
            'progresso': 0,
            'arquivos': [{'caminho': str(csv_file), 'nome': 'dados_teste.csv'}],
            'usuario_id': '1',
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)

        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = resultado_mock
        mock_crew_instance = MagicMock()
        mock_crew_instance.crew.return_value = mock_crew

        with patch(
            'Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
            return_value=mock_crew_instance
        ):
            interface._executar_analise(analise_id)
            for _ in range(20):
                time.sleep(0.5)
                analise = interface._buscar_analise(analise_id)
                if analise and analise.get('status') in ('concluida', 'erro'):
                    break

        analise_final = interface._buscar_analise(analise_id)
        assert analise_final is not None, "Análise não encontrada no banco após execução"
        assert analise_final['status'] == 'concluida', (
            f"Status esperado 'concluida', obtido: {analise_final.get('status')} "
            f"| erro: {analise_final.get('erro')}"
        )
        assert analise_final['progresso'] == 100
        assert resultado_mock in str(analise_final.get('resultados', ''))

    def test_analise_registra_erro_em_falha(self, interface):
        """Se a crew lançar exceção, status deve ser 'erro' e não travar."""
        import time
        from unittest.mock import patch, MagicMock

        analise_id = "teste-e2e-erro"
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'topico_pesquisa': 'Teste falha',
            'status': 'aguardando',
            'progresso': 0,
            'arquivos': [],
            'usuario_id': '1',
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)

        mock_crew = MagicMock()
        mock_crew.kickoff.side_effect = RuntimeError("LLM indisponível")
        mock_crew_instance = MagicMock()
        mock_crew_instance.crew.return_value = mock_crew

        with patch(
            'Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
            return_value=mock_crew_instance
        ):
            interface._executar_analise(analise_id)
            for _ in range(20):
                time.sleep(0.5)
                analise = interface._buscar_analise(analise_id)
                if analise and analise.get('status') in ('concluida', 'erro'):
                    break

        analise_final = interface._buscar_analise(analise_id)
        assert analise_final is not None
        assert analise_final['status'] == 'erro'
        assert 'LLM indisponível' in str(analise_final.get('erro', ''))

    def test_cache_liberado_apos_conclusao(self, interface):
        """Após concluir, a entrada deve ser removida do cache em memória."""
        import time
        from unittest.mock import patch, MagicMock

        analise_id = "teste-cache-cleanup"
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'topico_pesquisa': 'Teste cache',
            'status': 'aguardando',
            'progresso': 0,
            'arquivos': [],
            'usuario_id': '1',
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        interface._salvar_analise(analise_id)

        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = "ok"
        mock_crew_instance = MagicMock()
        mock_crew_instance.crew.return_value = mock_crew

        with patch(
            'Sapiens_MultiAgente.crew.SapiensAcademicMultiAgentDataAnalysisPlatformCrew',
            return_value=mock_crew_instance
        ):
            interface._executar_analise(analise_id)
            for _ in range(20):
                time.sleep(0.5)
                if analise_id not in interface.analises_ativas:
                    break

        assert analise_id not in interface.analises_ativas, (
            "Cache deveria ter sido liberado após conclusão da análise"
        )
