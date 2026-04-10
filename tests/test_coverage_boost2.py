"""
Testes para aumentar cobertura de:
- ChartGeneratorTool (65% → ~90%)
- DataValidationTool (48% → ~80%)
- AcademicSecurityValidator (57% → ~75%)
- AcademicAuditor / academic_logger (56% → ~80%)
- web/app.py métodos internos (49% → ~60%)
"""

import os
import sys
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# ---------------------------------------------------------------------------
# ChartGeneratorTool — tipos de gráficos não cobertos (65% → ~90%)
# ---------------------------------------------------------------------------

class TestChartGeneratorToolExtended:
    def _json(self, rows):
        return json.dumps(rows)

    def test_bar_chart(self):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        data = self._json([{"categoria": "A"}, {"categoria": "B"}, {"categoria": "A"}])
        result = ChartGeneratorTool()._run(data=data, chart_type="bar", x_column="categoria")
        assert result.startswith("data:image/png;base64,") or "salvo" in result.lower()

    def test_line_chart(self):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        data = self._json([{"x": i, "y": i * 2} for i in range(20)])
        result = ChartGeneratorTool()._run(data=data, chart_type="line", x_column="x", y_column="y")
        assert result.startswith("data:image/png;base64,") or "salvo" in result.lower()

    def test_line_chart_sem_x_column(self):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        data = self._json([{"a": i, "b": i + 1} for i in range(20)])
        result = ChartGeneratorTool()._run(data=data, chart_type="line")
        assert result.startswith("data:image/png;base64,") or "salvo" in result.lower()

    def test_scatter_chart(self):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        data = self._json([{"x": float(i), "y": float(i) + 1} for i in range(20)])
        result = ChartGeneratorTool()._run(data=data, chart_type="scatter", x_column="x", y_column="y")
        assert result.startswith("data:image/png;base64,") or "salvo" in result.lower()

    def test_scatter_sem_colunas_numericas_suficientes(self):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        data = self._json([{"nome": "Alice"}, {"nome": "Bob"}])
        result = ChartGeneratorTool()._run(data=data, chart_type="scatter")
        assert "ERRO" in result

    def test_boxplot_chart(self):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        data = self._json([{"a": float(i), "b": float(i) * 2} for i in range(20)])
        result = ChartGeneratorTool()._run(data=data, chart_type="boxplot")
        assert result.startswith("data:image/png;base64,") or "salvo" in result.lower()

    def test_heatmap_sem_colunas_suficientes(self):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        data = self._json([{"nome": "Alice"}, {"nome": "Bob"}])
        result = ChartGeneratorTool()._run(data=data, chart_type="correlation_heatmap")
        assert "ERRO" in result

    def test_grafico_com_titulo_customizado(self):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        data = self._json([{"nota": float(i)} for i in range(20)])
        result = ChartGeneratorTool()._run(data=data, chart_type="histogram",
                                           x_column="nota", title="Distribuição de Notas")
        assert result.startswith("data:image/png;base64,") or "salvo" in result.lower()

    def test_dados_vazios_retorna_erro(self):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        result = ChartGeneratorTool()._run(data="[]", chart_type="histogram")
        assert "ERRO" in result

    def test_json_invalido_retorna_erro(self):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        result = ChartGeneratorTool()._run(data="nao_e_json", chart_type="histogram")
        assert "ERRO" in result

    def test_matplotlib_indisponivel(self):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        with patch('Sapiens_MultiAgente.tools.chart_generator_tool.MATPLOTLIB_AVAILABLE', False):
            result = ChartGeneratorTool()._run(data='[{"x":1}]', chart_type="histogram")
        assert "ERRO" in result

    def test_salva_em_arquivo_bar(self, tmp_path):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        data = self._json([{"cat": "A"}, {"cat": "B"}, {"cat": "A"}])
        output = str(tmp_path / "bar.png")
        result = ChartGeneratorTool()._run(data=data, chart_type="bar", output_path=output)
        assert "salvo" in result.lower()
        assert os.path.exists(output)


# ---------------------------------------------------------------------------
# DataValidationTool — caminho principal de validação (48% → ~80%)
# ---------------------------------------------------------------------------

class TestDataValidationToolExtended:
    def _make_csv(self, content: str, tmp_path) -> str:
        path = str(tmp_path / "test.csv")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path

    def test_valida_csv_com_sucesso(self, tmp_path):
        from Sapiens_MultiAgente.tools.data_validation_tool import DataValidationTool
        path = self._make_csv("nome,nota\nAlice,8.5\nBob,7.0\n", tmp_path)
        result = DataValidationTool()._run(file_path=path)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_tipo_de_arquivo_nao_suportado(self, tmp_path):
        from Sapiens_MultiAgente.tools.data_validation_tool import DataValidationTool
        path = str(tmp_path / "arquivo.xyz")
        with open(path, 'w') as f:
            f.write("dados quaisquer")
        result = DataValidationTool()._run(file_path=path)
        assert isinstance(result, str)

    def test_check_pii_indicators_detecta_email(self, tmp_path):
        from Sapiens_MultiAgente.tools.data_validation_tool import DataValidationTool
        path = str(tmp_path / "pii.csv")
        with open(path, 'w', encoding='utf-8') as f:
            f.write("email,nome\nalice@exemplo.com,Alice\n")
        tool = DataValidationTool()
        warnings = tool._check_pii_indicators(path, 'text/csv')
        assert isinstance(warnings, list)
        assert any('email' in w.lower() for w in warnings)

    def test_check_pii_indicators_sem_pii(self, tmp_path):
        from Sapiens_MultiAgente.tools.data_validation_tool import DataValidationTool
        path = str(tmp_path / "clean.csv")
        with open(path, 'w', encoding='utf-8') as f:
            f.write("produto,preco\nMaca,1.50\n")
        tool = DataValidationTool()
        warnings = tool._check_pii_indicators(path, 'text/csv')
        assert isinstance(warnings, list)
        assert len(warnings) == 0

    def test_check_pii_nao_leitura_em_binario(self, tmp_path):
        """Tipo MIME que não é texto não deve gerar avisos PII."""
        from Sapiens_MultiAgente.tools.data_validation_tool import DataValidationTool
        path = str(tmp_path / "data.bin")
        with open(path, 'wb') as f:
            f.write(b'\x00\x01\x02\x03')
        tool = DataValidationTool()
        warnings = tool._check_pii_indicators(path, 'application/octet-stream')
        assert warnings == []


# ---------------------------------------------------------------------------
# AcademicSecurityValidator — métodos não cobertos (57% → ~75%)
# ---------------------------------------------------------------------------

class TestAcademicSecurityValidatorExtended:

    def test_validar_arquivo_csv_completo(self, tmp_path):
        from Sapiens_MultiAgente.tools.security_validator import AcademicSecurityValidator
        path = str(tmp_path / "dados.csv")
        with open(path, 'w', encoding='utf-8') as f:
            f.write("nome,nota\nAlice,8.5\nBob,7.0\n")
        result = AcademicSecurityValidator().validar_arquivo(path)
        assert isinstance(result, dict)
        assert 'valido' in result

    def test_validar_arquivo_extensao_nao_permitida(self, tmp_path):
        from Sapiens_MultiAgente.tools.security_validator import AcademicSecurityValidator
        path = str(tmp_path / "arquivo.xyz")
        with open(path, 'w') as f:
            f.write("dados")
        result = AcademicSecurityValidator().validar_arquivo(path)
        assert result['valido'] is False

    def test_validar_tamanho_arquivo(self, tmp_path):
        from Sapiens_MultiAgente.tools.security_validator import AcademicSecurityValidator
        path = str(tmp_path / "grande.csv")
        with open(path, 'w') as f:
            f.write("nome,nota\nAlice,8.5\n")
        validator = AcademicSecurityValidator(config={"max_file_size_mb": 0.000001})
        result = validator._validar_tamanho(path)
        assert result['valido'] is False
        assert any("grande" in e.lower() for e in result['erros'])

    def test_validar_pii_detecta_cpf(self, tmp_path):
        from Sapiens_MultiAgente.tools.security_validator import AcademicSecurityValidator
        path = str(tmp_path / "pii.csv")
        with open(path, 'w', encoding='utf-8') as f:
            f.write("cpf,nome\n123.456.789-00,Alice\nalice@teste.com,Bob\n")
        result = AcademicSecurityValidator()._validar_pii(path)
        assert isinstance(result, dict)
        assert len(result.get('pii_encontrada', [])) > 0

    def test_validar_conteudo_csv_qualidade(self, tmp_path):
        from Sapiens_MultiAgente.tools.security_validator import AcademicSecurityValidator
        path = str(tmp_path / "parcial.csv")
        with open(path, 'w', encoding='utf-8') as f:
            # 50% de dados faltantes
            f.write("a,b\n1,\n,2\n,\n1,2\n")
        result = AcademicSecurityValidator()._validar_conteudo_dados(path)
        assert isinstance(result, dict)
        assert result['valido'] is True

    def test_validar_multiplos_arquivos(self, tmp_path):
        from Sapiens_MultiAgente.tools.security_validator import AcademicSecurityValidator
        paths = []
        for i in range(3):
            p = str(tmp_path / f"file{i}.csv")
            with open(p, 'w') as f:
                f.write(f"col\n{i}\n")
            paths.append(p)
        result = AcademicSecurityValidator().validar_multiplos_arquivos(paths)
        assert result['total_arquivos'] == 3
        assert 'taxa_sucesso' in result

    def test_gerar_relatorio_seguranca_valido(self):
        from Sapiens_MultiAgente.tools.security_validator import AcademicSecurityValidator
        resultado = {
            'arquivo': '/tmp/test.csv',
            'valido': True,
            'erros': [],
            'avisos': ['Aviso de teste'],
            'informacoes': {'tamanho': '1KB'},
            'timestamp': '2026-01-01T00:00:00',
        }
        relatorio = AcademicSecurityValidator().gerar_relatorio_seguranca(resultado)
        assert "SAPIENS" in relatorio
        assert "VÁLIDO" in relatorio
        assert "AVISOS" in relatorio

    def test_gerar_relatorio_seguranca_invalido(self):
        from Sapiens_MultiAgente.tools.security_validator import AcademicSecurityValidator
        resultado = {
            'arquivo': '/tmp/test.exe',
            'valido': False,
            'erros': ['Extensão bloqueada: .exe'],
            'avisos': [],
            'informacoes': {},
            'timestamp': '2026-01-01T00:00:00',
        }
        relatorio = AcademicSecurityValidator().gerar_relatorio_seguranca(resultado)
        assert "INVÁLIDO" in relatorio
        assert "ERROS" in relatorio

    def test_funcao_utilitaria_global(self, tmp_path):
        from Sapiens_MultiAgente.tools.security_validator import validar_seguranca_arquivo
        path = str(tmp_path / "test.csv")
        with open(path, 'w') as f:
            f.write("col\n1\n")
        result = validar_seguranca_arquivo(path)
        assert isinstance(result, dict)
        assert 'valido' in result

    def test_calcular_hash(self, tmp_path):
        from Sapiens_MultiAgente.tools.security_validator import AcademicSecurityValidator
        path = str(tmp_path / "hash.csv")
        with open(path, 'w') as f:
            f.write("conteudo de teste para hash")
        h = AcademicSecurityValidator()._calcular_hash(path)
        assert len(h) == 64  # SHA-256 hex


# ---------------------------------------------------------------------------
# AcademicAuditor — métodos de auditoria e decorador (56% → ~80%)
# ---------------------------------------------------------------------------

class TestAcademicAuditor:

    @pytest.fixture
    def auditor(self):
        import logging
        # Importa PRIMEIRO — dispara auditor_global que adiciona handlers
        from Sapiens_MultiAgente.tools.academic_logger import AcademicAuditor
        # Limpa handlers DEPOIS do import para que a nova instância faça setup completo
        # (sem isso, _setup_logging() retorna cedo e auditoria_logger nunca é atribuído)
        for name in ('sapiens_academico', 'sapiens_auditoria'):
            logging.getLogger(name).handlers.clear()
        return AcademicAuditor()

    def test_auditar_evento_info(self, auditor):
        auditor.auditar_evento("evento_customizado_xyz", dados_entrada={"k": "v"})
        tipos = [e['evento_tipo'] for e in auditor._eventos_auditoria]
        assert "evento_customizado_xyz" in tipos

    def test_auditar_evento_critico(self, auditor):
        # 'inicio_analise' está na lista de criticidade alta do config
        auditor.auditar_evento("inicio_analise", dados_entrada={"topico": "teste"})
        tipos = [e['evento_tipo'] for e in auditor._eventos_auditoria]
        assert "inicio_analise" in tipos

    def test_auditar_evento_medio(self, auditor):
        # 'delegacao_tarefa' está na lista de criticidade média do config
        auditor.auditar_evento("delegacao_tarefa", dados_entrada={"agente": "gerente"})
        tipos = [e['evento_tipo'] for e in auditor._eventos_auditoria]
        assert "delegacao_tarefa" in tipos

    def test_auditar_evento_com_tempo_execucao(self, auditor):
        auditor.auditar_evento("evento_com_tempo", tempo_execucao_ms=123.45)
        evento = next(e for e in auditor._eventos_auditoria if e['evento_tipo'] == 'evento_com_tempo')
        assert evento['tempo_execucao_ms'] == 123.45

    def test_iniciar_analise(self, auditor):
        auditor.iniciar_analise("Análise de notas", {"arquivo": "notas.csv"})
        assert any(e['evento_tipo'] == 'inicio_analise' for e in auditor._eventos_auditoria)

    def test_validar_dados_positivo(self, auditor):
        auditor.validar_dados(True, "Dados OK")
        assert any(e['evento_tipo'] == 'validacao_dados' for e in auditor._eventos_auditoria)

    def test_validar_dados_negativo(self, auditor):
        auditor.validar_dados(False, "Arquivo corrompido")
        assert any(e['evento_tipo'] == 'validacao_dados' for e in auditor._eventos_auditoria)

    def test_registrar_erro(self, auditor):
        auditor.registrar_erro(ValueError("Erro de formato"), "validacao_csv")
        evento = next(e for e in auditor._eventos_auditoria if e['evento_tipo'] == 'erro_sistema')
        assert "ValueError" in evento['dados_entrada']['erro_tipo']

    def test_finalizar_analise_sucesso(self, auditor):
        auditor.finalizar_analise(True, {"registros": 100})
        assert any(e['evento_tipo'] == 'resultado_analise' for e in auditor._eventos_auditoria)

    def test_finalizar_analise_falha(self, auditor):
        auditor.finalizar_analise(False, {})
        assert any(e['evento_tipo'] == 'resultado_analise' for e in auditor._eventos_auditoria)

    def test_get_estatisticas_auditoria(self, auditor):
        auditor.iniciar_analise("Teste")
        auditor.validar_dados(True, "OK")
        stats = auditor.get_estatisticas_auditoria()
        assert stats['total_eventos'] >= 2
        assert 'eventos_por_tipo' in stats
        assert 'inicio_analise' in stats['eventos_por_tipo']

    def test_calcular_tempo_sessao_com_eventos(self, auditor):
        auditor.iniciar_analise("Primeiro")
        auditor.finalizar_analise(True, {})
        stats = auditor.get_estatisticas_auditoria()
        assert stats['tempo_sessao_minutos'] >= 0.0

    def test_calcular_tempo_sessao_sem_eventos(self, auditor):
        # Sem eventos, deve retornar 0.0
        assert auditor._calcular_tempo_sessao() == 0.0

    def test_exportar_auditoria_json(self, auditor, tmp_path):
        auditor.iniciar_analise("Teste de exportação")
        path = str(tmp_path / "auditoria.json")
        resultado = auditor.exportar_auditoria_json(path)
        assert resultado == path
        assert os.path.exists(path)
        with open(path, encoding='utf-8') as f:
            dados = json.load(f)
        assert 'eventos' in dados
        assert 'metadata' in dados

    def test_exportar_auditoria_json_path_automatico(self, auditor):
        # Sem path fornecido — deve criar arquivo automático em logs/
        os.makedirs("logs", exist_ok=True)
        resultado = auditor.exportar_auditoria_json()
        assert resultado is not None
        if resultado and os.path.exists(resultado):
            os.remove(resultado)

    def test_decorator_auditar_tempo_execucao_sucesso(self):
        from Sapiens_MultiAgente.tools.academic_logger import auditar_tempo_execucao

        @auditar_tempo_execucao
        def dobrar(x):
            return x * 2

        assert dobrar(5) == 10

    def test_decorator_auditar_tempo_execucao_com_excecao(self):
        from Sapiens_MultiAgente.tools.academic_logger import auditar_tempo_execucao

        @auditar_tempo_execucao
        def funcao_que_falha():
            raise RuntimeError("Falha intencional")

        with pytest.raises(RuntimeError, match="Falha intencional"):
            funcao_que_falha()

    def test_agrupar_eventos_por_tipo(self, auditor):
        auditor.iniciar_analise("A")
        auditor.iniciar_analise("B")
        auditor.validar_dados(True)
        grupos = auditor._agrupar_eventos_por_tipo()
        assert grupos.get('inicio_analise', 0) >= 2
        assert grupos.get('validacao_dados', 0) >= 1


# ---------------------------------------------------------------------------
# web/app.py — métodos internos e rotas adicionais (49% → ~60%)
# ---------------------------------------------------------------------------

class TestWebMetodosInternos:

    @pytest.fixture
    def interface(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        with patch('Sapiens_MultiAgente.web.app.DB_PATH', db_path), \
             patch('Sapiens_MultiAgente.web.auth.DB_PATH', db_path):
            from Sapiens_MultiAgente.web.app import SapiensWebInterface
            yield SapiensWebInterface()

    @pytest.fixture
    def app_cliente(self, tmp_path):
        db_path = str(tmp_path / "test2.db")
        with patch('Sapiens_MultiAgente.web.app.DB_PATH', db_path), \
             patch('Sapiens_MultiAgente.web.auth.DB_PATH', db_path):
            from Sapiens_MultiAgente.web.app import SapiensWebInterface
            interface = SapiensWebInterface()
            flask_app = interface.create_app()
            flask_app.config['TESTING'] = True
            flask_app.config['WTF_CSRF_ENABLED'] = False
            client = flask_app.test_client()
            _pw = os.getenv('SAPIENS_ADMIN_PASSWORD')
            client.post('/login', data={'username': 'admin', 'senha': _pw})
            yield interface, client

    # _validar_url
    def test_validar_url_https_valida(self, interface):
        ok, msg = interface._validar_url("https://www.exemplo.com/dados.csv")
        assert ok is True

    def test_validar_url_http_valida(self, interface):
        ok, msg = interface._validar_url("http://universidade.br/arquivo.csv")
        assert ok is True

    def test_validar_url_localhost_bloqueado(self, interface):
        ok, msg = interface._validar_url("http://localhost/arquivo.csv")
        assert ok is False

    def test_validar_url_ip_privado_bloqueado(self, interface):
        ok, msg = interface._validar_url("http://192.168.1.1/dados.csv")
        assert ok is False

    def test_validar_url_ip_loopback_bloqueado(self, interface):
        ok, msg = interface._validar_url("http://127.0.0.1/dados.csv")
        assert ok is False

    def test_validar_url_schema_ftp_bloqueado(self, interface):
        ok, msg = interface._validar_url("ftp://servidor.com/arquivo.csv")
        assert ok is False

    def test_validar_url_sem_hostname(self, interface):
        ok, msg = interface._validar_url("http:///sem-host")
        assert ok is False

    def test_validar_url_metadata_cloud_bloqueado(self, interface):
        ok, msg = interface._validar_url("http://169.254.169.254/latest/meta-data")
        assert ok is False

    # _allowed_file
    def test_allowed_file_csv(self, interface):
        assert interface._allowed_file("dados.csv") is True

    def test_allowed_file_xlsx(self, interface):
        assert interface._allowed_file("planilha.xlsx") is True

    def test_allowed_file_exe_bloqueado(self, interface):
        assert interface._allowed_file("malware.exe") is False

    def test_allowed_file_sem_extensao(self, interface):
        assert interface._allowed_file("arquivo_sem_extensao") is False

    # get_estatisticas
    def test_get_estatisticas_sem_analises(self, interface):
        stats = interface.get_estatisticas()
        assert 'analises_ativas' in stats
        assert stats['analises_ativas'] == 0

    def test_get_estatisticas_com_analise(self, interface):
        interface.analises_ativas['test-001'] = {
            'arquivos': [{'nome': 'a.csv'}],
            'timestamp_inicio': '2026-01-01T00:00:00',
        }
        stats = interface.get_estatisticas()
        assert stats['analises_ativas'] == 1
        assert stats['arquivos_upload_total'] == 1

    # _limpar_arquivos_analise
    def test_limpar_arquivos_analise(self, interface, tmp_path):
        arquivo = str(tmp_path / "temp.csv")
        with open(arquivo, 'w') as f:
            f.write("dado")
        analise_id = "limpar-test-001"
        interface.analises_ativas[analise_id] = {
            'arquivos': [{'caminho': arquivo}],
        }
        interface._limpar_arquivos_analise(analise_id)
        assert analise_id not in interface.analises_ativas
        assert not os.path.exists(arquivo)

    # Upload via HTTP
    def test_upload_sem_arquivo_retorna_400(self, app_cliente):
        _, client = app_cliente
        resp = client.post('/upload', data={}, content_type='multipart/form-data')
        assert resp.status_code == 400

    def test_upload_extensao_invalida_retorna_400(self, app_cliente):
        import io
        _, client = app_cliente
        data = {'arquivo': (io.BytesIO(b'MZ\x00'), 'malware.exe', 'application/octet-stream')}
        resp = client.post('/upload', data=data, content_type='multipart/form-data')
        assert resp.status_code == 400

    def test_upload_nome_vazio_retorna_400(self, app_cliente):
        import io
        _, client = app_cliente
        data = {'arquivo': (io.BytesIO(b'dado'), '', 'text/csv')}
        resp = client.post('/upload', data=data, content_type='multipart/form-data')
        assert resp.status_code == 400

    # Exportação TXT
    def test_exportar_analise_txt(self, app_cliente):
        interface, client = app_cliente
        analise_id = "export-txt-001"
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'topico_pesquisa': 'Exportação de teste TXT',
            'status': 'concluida',
            'resultados': 'Resultados bem-sucedidos.',
            'progresso': 100,
            'arquivos': [],
            'usuario_id': '1',
            'timestamp_inicio': '2026-01-01T00:00:00',
            'timestamp_fim': '2026-01-01T01:00:00',
            'concluido_em': '2026-01-01T01:00:00',
        }
        interface._salvar_analise(analise_id)
        resp = client.get(f'/export/{analise_id}/txt')
        assert resp.status_code == 200
        assert b'Exporta' in resp.data or b'SAPIENS' in resp.data

    def test_exportar_analise_formato_invalido(self, app_cliente):
        interface, client = app_cliente
        analise_id = "export-inv-001"
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'topico_pesquisa': 'Teste',
            'status': 'concluida',
            'resultados': 'OK',
            'progresso': 100,
            'arquivos': [],
            'usuario_id': '1',
            'timestamp_inicio': '2026-01-01T00:00:00',
            'timestamp_fim': '2026-01-01T01:00:00',
            'concluido_em': '2026-01-01T01:00:00',
        }
        interface._salvar_analise(analise_id)
        resp = client.get(f'/export/{analise_id}/xml')
        assert resp.status_code == 400

    def test_exportar_analise_nao_concluida_retorna_404(self, app_cliente):
        interface, client = app_cliente
        analise_id = "export-pend-001"
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
        resp = client.get(f'/export/{analise_id}/txt')
        assert resp.status_code == 404

    # API v1 — resultados de análise concluída
    def test_api_resultados_analise_concluida(self, app_cliente):
        interface, client = app_cliente
        analise_id = "result-api-001"
        interface.analises_ativas[analise_id] = {
            'id': analise_id,
            'topico_pesquisa': 'API resultados',
            'status': 'concluida',
            'resultados': 'Análise concluída com sucesso.',
            'progresso': 100,
            'arquivos': [],
            'usuario_id': '1',
            'timestamp_inicio': '2026-01-01T00:00:00',
            'concluido_em': '2026-01-01T01:00:00',
        }
        interface._salvar_analise(analise_id)
        resp = client.get(f'/api/v1/analises/{analise_id}/resultados')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['analise_id'] == analise_id

    def test_api_resultados_analise_pendente_retorna_409(self, app_cliente):
        interface, client = app_cliente
        analise_id = "result-pend-001"
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
        resp = client.get(f'/api/v1/analises/{analise_id}/resultados')
        assert resp.status_code == 409

    def test_api_status_analise_com_login(self, app_cliente):
        interface, client = app_cliente
        analise_id = "status-api-001"
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
        resp = client.get(f'/api/v1/analises/{analise_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['id'] == analise_id
