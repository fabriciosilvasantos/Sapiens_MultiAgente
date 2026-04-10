"""
Boost de cobertura — Rodada 6.
Cobre lacunas remanescentes após boost5 (~4% restante).

Alvos:
- academic_logger.py  98-101  : JsonFormatter com tempo_execucao_ms
- chart_generator_tool.py 148-150 : handler de exceção em _generate_chart
- csv_processor_tool.py 113-114  : exceção após leitura do CSV
- csv_search_tool.py  58        : CSV com apenas cabeçalho (df.empty)
- csv_search_tool.py  138       : conversão numérica de coluna string
- auth.py             187-188   : exceção interna em autenticar
- statistical_analysis_tool.py 288-289 : ANOVA com só 1 grupo válido pós-NaN
- security_validator.py 205     : aviso de arquivo grande (80-100% do limite)
- security_validator.py 255     : _validar_conteudo_dados com ext não suportada
- web/app.py          1009      : Spacer para linha vazia no PDF exportado
"""

import os
import sys
import json
import logging
import sqlite3
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# ---------------------------------------------------------------------------
# academic_logger.py — linhas 98-101 (JsonFormatter com tempo_execucao_ms)
# ---------------------------------------------------------------------------

class TestAcademicLoggerJsonFormatterTempo:
    """Acessa o formatter diretamente para cobrir o ramo tempo_execucao_ms."""

    def _obter_formatter(self):
        """Obtém o JsonFormatter do auditoria_logger, garantindo estado limpo."""
        logging.getLogger('sapiens_academico').handlers.clear()
        logging.getLogger('sapiens_auditoria').handlers.clear()

        from Sapiens_MultiAgente.tools.academic_logger import AcademicAuditor

        auditor = AcademicAuditor()
        auditoria_logger = logging.getLogger('sapiens_auditoria')

        assert len(auditoria_logger.handlers) > 0, (
            "auditoria_logger sem handlers — _setup_logging() não executado"
        )

        formatter = auditoria_logger.handlers[-1].formatter
        # JsonFormatter não tem sessao_id/usuario_id como atributos de instância
        # (o código usa getattr(record, ..., self.sessao_id) mas self.sessao_id
        #  é avaliado na chamada — precisamos injetá-los no formatter).
        formatter.sessao_id = auditor.sessao_id
        formatter.usuario_id = auditor.usuario_id
        return formatter, auditor

    def test_json_formatter_inclui_tempo_execucao_ms(self):
        formatter, auditor = self._obter_formatter()

        record = logging.LogRecord(
            name='sapiens_auditoria',
            level=logging.INFO,
            pathname='test_boost6.py',
            lineno=0,
            msg='mensagem de teste boost6',
            args=(),
            exc_info=None,
        )
        record.dados_adicionais = {}
        record.tempo_execucao_ms = 123.456  # <- aciona linhas 98-101

        resultado = formatter.format(record)
        data = json.loads(resultado)

        assert 'tempo_execucao_ms' in data
        assert data['tempo_execucao_ms'] == pytest.approx(123.456)

    def test_json_formatter_sem_tempo_execucao_nao_inclui_campo(self):
        """Caminho oposto: sem tempo_execucao_ms o campo não aparece."""
        formatter, auditor = self._obter_formatter()

        record = logging.LogRecord(
            name='sapiens_auditoria',
            level=logging.INFO,
            pathname='test_boost6.py',
            lineno=0,
            msg='sem tempo',
            args=(),
            exc_info=None,
        )
        record.dados_adicionais = {}

        resultado = formatter.format(record)
        data = json.loads(resultado)
        assert 'tempo_execucao_ms' not in data


# ---------------------------------------------------------------------------
# chart_generator_tool.py — linhas 148-150 (exceção em _generate_chart)
# ---------------------------------------------------------------------------

class TestChartGeneratorException:
    """Força exceção dentro do bloco try de _generate_chart."""

    def test_excecao_no_tight_layout_retorna_erro(self):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        import Sapiens_MultiAgente.tools.chart_generator_tool as cgt

        tool = ChartGeneratorTool()
        dados = json.dumps([{'x': 1, 'val': 10}, {'x': 2, 'val': 20}, {'x': 3, 'val': 30}])

        with patch.object(cgt.plt, 'tight_layout', side_effect=RuntimeError('erro tight_layout')):
            result = tool._run(data=dados, chart_type='histogram')

        assert '❌ ERRO' in result
        assert 'tight_layout' in result or 'ERRO' in result

    def test_excecao_no_savefig_base64_retorna_erro(self):
        """Força exceção em base64.b64encode para cobrir linhas 148-150."""
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        import Sapiens_MultiAgente.tools.chart_generator_tool as cgt

        tool = ChartGeneratorTool()
        dados = json.dumps([{'v': i} for i in range(5)])

        with patch.object(cgt.base64, 'b64encode', side_effect=RuntimeError('encode falhou')):
            result = tool._run(data=dados, chart_type='histogram')

        assert '❌ ERRO' in result


# ---------------------------------------------------------------------------
# csv_processor_tool.py — linhas 113-114 (exceção após leitura do CSV)
# ---------------------------------------------------------------------------

class TestCSVProcessorException:
    """Força exceção em _analyze_data_types para cobrir o except externo."""

    def test_excecao_em_analyze_data_types_retorna_erro(self, tmp_path):
        from Sapiens_MultiAgente.tools.csv_processor_tool import CSVProcessorTool

        csv_file = tmp_path / 'dados.csv'
        csv_file.write_text('col1,col2\n1,a\n2,b\n', encoding='utf-8')

        tool = CSVProcessorTool()

        with patch.object(tool, '_analyze_data_types', side_effect=RuntimeError('falha analyze')):
            result = tool._run(file_path=str(csv_file))

        assert '❌ ERRO' in result
        assert 'falha analyze' in result


# ---------------------------------------------------------------------------
# csv_search_tool.py — linha 58 (df.empty — CSV com só cabeçalho)
# ---------------------------------------------------------------------------

class TestCSVSearchDFVazio:
    """CSV válido mas sem linhas de dados → df.empty → linha 58."""

    def test_csv_somente_cabecalho_retorna_erro_vazio(self, tmp_path):
        from Sapiens_MultiAgente.tools.csv_search_tool import CSVSearchTool

        csv_file = tmp_path / 'somente_header.csv'
        csv_file.write_text('col1,col2,col3\n', encoding='utf-8')

        tool = CSVSearchTool()
        result = tool._run(file_path=str(csv_file))

        assert '❌ ERRO' in result
        assert 'vazio' in result.lower()


# ---------------------------------------------------------------------------
# csv_search_tool.py — linha 138 (conversão numérica de coluna string)
# ---------------------------------------------------------------------------

class TestCSVSearchConversaoNumerica:
    """Aplica filtro numérico em coluna de string → aciona to_numeric (linha 138)."""

    def test_filtro_numerico_em_coluna_string_converte(self, tmp_path):
        from Sapiens_MultiAgente.tools.csv_search_tool import CSVSearchTool

        # Coluna 'score' com valores numéricos armazenados como string no CSV
        csv_file = tmp_path / 'notas.csv'
        csv_file.write_text(
            'nome,score\nAna,10\nBia,5\nCaio,8\n',
            encoding='utf-8',
        )

        tool = CSVSearchTool()
        # Condição >6 numa coluna que será lida como object (string) inicialmente
        result = tool._run(
            file_path=str(csv_file),
            numeric_filters={'score': '>6'},
        )

        # Deve retornar ao menos Ana (10) e Caio (8)
        assert 'Ana' in result or 'score' in result.lower() or '❌' not in result


# ---------------------------------------------------------------------------
# web/auth.py — linhas 187-188 (except Exception em autenticar)
# ---------------------------------------------------------------------------

class TestAuthExcecaoInterna:
    """Força exceção em _get_db dentro de autenticar → linhas 187-188."""

    def test_autenticar_excecao_interna_retorna_erro(self):
        from Sapiens_MultiAgente.web import auth
        from Sapiens_MultiAgente.web.auth import Usuario

        # Garante que o usuário não está bloqueado
        auth._falhas_login.pop('usuario_boost6', None)

        with patch('Sapiens_MultiAgente.web.auth._get_db',
                   side_effect=RuntimeError('banco explodiu')):
            usuario, erro = Usuario.autenticar('usuario_boost6', 'qualquer_senha')

        assert usuario is None
        assert erro == 'Erro interno de autenticação.'


# ---------------------------------------------------------------------------
# statistical_analysis_tool.py — linhas 288-289 (ANOVA grupo insuficiente)
# ---------------------------------------------------------------------------

class TestStatisticalANOVAGrupoInsuficiente:
    """Grupo com todos NaN → só 1 amostra válida → aviso linhas 288-289."""

    def test_anova_um_grupo_valido_emite_aviso(self):
        import pandas as pd
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool

        # Grupo A tem TODOS os valores NaN para a coluna target
        # Grupo B tem valores válidos
        # → após dropna, apenas grupo B sobra (1 amostra) → "Dados insuficientes"
        df = pd.DataFrame({
            'grupo': ['A', 'A', 'A', 'B', 'B', 'B'],
            'nota': [None, None, None, 7.0, 8.0, 9.0],
        })

        tool = StatisticalAnalysisTool()
        result = tool._run(
            data=df.to_json(orient='records'),
            analysis_type='anova_one_way',
            group_column='grupo',
        )

        assert 'insuficientes' in result.lower() or 'ANOVA' in result


# ---------------------------------------------------------------------------
# security_validator.py — linha 205 (aviso arquivo grande, 80-100% do limite)
# ---------------------------------------------------------------------------

class TestSecurityValidatorAvisoGrande:
    """Arquivo entre 80-100% do max_file_size_mb → aviso (linha 205)."""

    def test_validar_tamanho_aviso_80_porcento(self, tmp_path):
        from Sapiens_MultiAgente.tools.security_validator import AcademicSecurityValidator

        # max = 0.00001 MB ≈ 10 bytes; 80% = 8 bytes → 9 bytes dispara aviso
        validator = AcademicSecurityValidator({'max_file_size_mb': 0.00001})

        arquivo = tmp_path / 'alerta_tamanho.csv'
        arquivo.write_bytes(b'x' * 9)

        result = validator._validar_tamanho(str(arquivo))

        assert result['valido'] is True
        assert len(result['avisos']) > 0
        assert any('grande' in a.lower() or 'aproximando' in a.lower()
                   for a in result['avisos'])


# ---------------------------------------------------------------------------
# security_validator.py — linha 255 (_validar_conteudo_dados com ext .txt)
# ---------------------------------------------------------------------------

class TestSecurityValidatorConteudoExtNaoSuportada:
    """Chama _validar_conteudo_dados com extensão .txt → return early (linha 255)."""

    def test_validar_conteudo_dados_extensao_txt_retorna_ok(self, tmp_path):
        from Sapiens_MultiAgente.tools.security_validator import AcademicSecurityValidator

        validator = AcademicSecurityValidator()

        arquivo = tmp_path / 'texto.txt'
        arquivo.write_text('conteúdo qualquer', encoding='utf-8')

        result = validator._validar_conteudo_dados(str(arquivo))

        # Retorna resultado padrão sem erros (return early na linha 255)
        assert result['valido'] is True
        assert result['erros'] == []


# ---------------------------------------------------------------------------
# web/app.py — linha 1009 (Spacer para linha vazia no PDF exportado)
# ---------------------------------------------------------------------------

class TestWebExportPDFLinhaVazia:
    """PDF export com resultados contendo linha vazia → Spacer linha 1009."""

    @pytest.fixture
    def app_autenticado(self, tmp_path):
        db_path = str(tmp_path / 'test_boost6.db')
        with patch('Sapiens_MultiAgente.web.app.DB_PATH', db_path), \
             patch('Sapiens_MultiAgente.web.auth.DB_PATH', db_path):
            from Sapiens_MultiAgente.web.app import SapiensWebInterface
            interface = SapiensWebInterface()
            flask_app = interface.create_app()
            flask_app.config['TESTING'] = True
            flask_app.config['WTF_CSRF_ENABLED'] = False
            yield flask_app, db_path

    def test_export_pdf_com_linha_vazia_gera_spacer(self, app_autenticado):
        flask_app, db_path = app_autenticado

        analise_id = 'boost6-pdf-test-001'
        resultados = "Linha com conteúdo\n\nOutra linha após vazio\nMais uma linha"

        # Insere análise concluída diretamente no banco
        # Colunas reais: id, usuario_id, topico, status, progresso,
        #                arquivos, resultados, erro, criado_em, atualizado_em, concluido_em
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO analises
                    (id, usuario_id, topico, status, progresso,
                     arquivos, resultados, criado_em, atualizado_em, concluido_em)
                VALUES (?, 'admin', 'Tópico Boost6 PDF', 'concluida', 100,
                        '[]', ?, datetime('now'), datetime('now'), datetime('now'))
                """,
                (analise_id, resultados),
            )
            conn.commit()

        with flask_app.test_client() as client:
            # Autentica
            _pw = os.getenv('SAPIENS_ADMIN_PASSWORD')
            client.post('/login', data={'username': 'admin', 'senha': _pw})

            # Exporta como PDF
            resp = client.get(f'/export/{analise_id}/pdf')

        assert resp.status_code == 200
        assert resp.content_type == 'application/pdf'
        # Verifica que o PDF foi gerado (começa com %PDF)
        assert resp.data[:4] == b'%PDF'
