"""
Testes unitários das ferramentas SAPIENS.
"""

import json
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# ---------------------------------------------------------------------------
# CSVProcessorTool
# ---------------------------------------------------------------------------

class TestCSVProcessorTool:
    def _make_csv(self, content: str) -> str:
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        f.write(content)
        f.flush()
        return f.name

    def teardown_method(self):
        # limpa arquivos temporários criados durante os testes
        pass

    def test_processa_csv_simples(self):
        from Sapiens_MultiAgente.tools.csv_processor_tool import CSVProcessorTool
        path = self._make_csv("nome,nota\nAlice,8.5\nBob,7.0\nCarla,9.2\n")
        try:
            tool = CSVProcessorTool()
            result = tool._run(file_path=path)
            assert "3" in result or "linhas" in result.lower()
            assert "PROCESSADO COM SUCESSO" in result
        finally:
            os.unlink(path)

    def test_detecta_separador_ponto_virgula(self):
        from Sapiens_MultiAgente.tools.csv_processor_tool import CSVProcessorTool
        path = self._make_csv("nome;nota\nAlice;8.5\nBob;7.0\n")
        try:
            tool = CSVProcessorTool()
            result = tool._run(file_path=path)
            assert "PROCESSADO COM SUCESSO" in result
        finally:
            os.unlink(path)

    def test_arquivo_inexistente(self):
        from Sapiens_MultiAgente.tools.csv_processor_tool import CSVProcessorTool
        tool = CSVProcessorTool()
        result = tool._run(file_path="/nao/existe.csv")
        assert "ERRO" in result

    def test_arquivo_vazio(self):
        from Sapiens_MultiAgente.tools.csv_processor_tool import CSVProcessorTool
        path = self._make_csv("")
        try:
            tool = CSVProcessorTool()
            result = tool._run(file_path=path)
            assert "ERRO" in result
        finally:
            os.unlink(path)

    def test_sem_limite_de_linhas(self):
        """Garante que arquivos com mais de 1.000 linhas são processados."""
        from Sapiens_MultiAgente.tools.csv_processor_tool import CSVProcessorTool
        linhas = ["valor"] + [str(i) for i in range(1500)]
        path = self._make_csv("\n".join(linhas))
        try:
            tool = CSVProcessorTool()
            result = tool._run(file_path=path)
            assert "1,500" in result or "1500" in result
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# StatisticalAnalysisTool
# ---------------------------------------------------------------------------

class TestStatisticalAnalysisTool:
    def _make_data(self, rows: list[dict]) -> str:
        return json.dumps(rows)

    def test_analise_descritiva(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._make_data([{"nota": i, "frequencia": i * 2} for i in range(1, 21)])
        tool = StatisticalAnalysisTool()
        result = tool._run(data=data, analysis_type="descriptive")
        assert "ANÁLISE DESCRITIVA" in result
        assert "nota" in result

    def test_correlacao(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._make_data([{"x": i, "y": i + 1} for i in range(20)])
        tool = StatisticalAnalysisTool()
        result = tool._run(data=data, analysis_type="correlation")
        assert "CORRELAÇÃO" in result

    def test_hipotese(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._make_data([{"a": i, "b": i * 2} for i in range(20)])
        tool = StatisticalAnalysisTool()
        result = tool._run(data=data, analysis_type="hypothesis_test")
        assert "HIPÓTESES" in result

    def test_regressao(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._make_data([{"x": float(i), "y": float(i) * 2 + 1} for i in range(20)])
        tool = StatisticalAnalysisTool()
        result = tool._run(data=data, analysis_type="regression")
        assert "REGRESSÃO" in result or "R²" in result

    def test_tipo_invalido(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._make_data([{"x": 1}])
        tool = StatisticalAnalysisTool()
        result = tool._run(data=data, analysis_type="invalido")
        assert "ERRO" in result

    def test_json_invalido(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        tool = StatisticalAnalysisTool()
        result = tool._run(data="não é json", analysis_type="descriptive")
        assert "ERRO" in result

    def test_filtra_variaveis(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        data = self._make_data([{"a": i, "b": i * 2, "c": i * 3} for i in range(20)])
        tool = StatisticalAnalysisTool()
        result = tool._run(data=data, analysis_type="descriptive", variables=["a"])
        assert "a" in result
        assert "ANÁLISE DESCRITIVA" in result


# ---------------------------------------------------------------------------
# DataValidationTool
# ---------------------------------------------------------------------------

class TestDataValidationTool:
    def _make_file(self, content: str, suffix: str) -> str:
        f = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8')
        f.write(content)
        f.flush()
        return f.name

    def test_arquivo_inexistente(self):
        from Sapiens_MultiAgente.tools.data_validation_tool import DataValidationTool
        tool = DataValidationTool()
        result = tool._run(file_path="/nao/existe.csv")
        assert "ERRO" in result

    def test_arquivo_muito_grande(self):
        from Sapiens_MultiAgente.tools.data_validation_tool import DataValidationTool
        path = self._make_file("a,b\n1,2\n", '.csv')
        try:
            tool = DataValidationTool()
            result = tool._run(file_path=path, max_size_mb=0)
            assert "ERRO" in result and "grande" in result.lower()
        finally:
            os.unlink(path)

    def test_calcula_hash_sha256(self):
        from Sapiens_MultiAgente.tools.data_validation_tool import DataValidationTool
        tool = DataValidationTool()
        path = self._make_file("conteudo de teste", '.txt')
        try:
            resultado = tool._calculate_sha256(path)
            assert len(resultado) == 64  # SHA-256 hex = 64 chars
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# AcademicSecurityValidator
# ---------------------------------------------------------------------------

class TestAcademicSecurityValidator:
    def test_extensao_bloqueada(self):
        from Sapiens_MultiAgente.tools.security_validator import AcademicSecurityValidator
        validator = AcademicSecurityValidator()
        # Cria arquivo .exe temporário
        f = tempfile.NamedTemporaryFile(suffix='.exe', delete=False)
        f.write(b'MZ')  # magic bytes de PE
        f.flush()
        try:
            result = validator.validar_arquivo(f.name)
            assert result['valido'] is False
        finally:
            f.close()
            os.unlink(f.name)

    def test_arquivo_valido_csv(self):
        from Sapiens_MultiAgente.tools.security_validator import AcademicSecurityValidator
        validator = AcademicSecurityValidator()
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        f.write("nome,nota\nAlice,9.0\n")
        f.flush()
        try:
            result = validator.validar_arquivo(f.name)
            assert result['valido'] is True
        finally:
            f.close()
            os.unlink(f.name)


# ---------------------------------------------------------------------------
# ChartGeneratorTool
# ---------------------------------------------------------------------------

class TestChartGeneratorTool:
    def _make_data(self, rows: list[dict]) -> str:
        return json.dumps(rows)

    def test_histogram(self):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        data = self._make_data([{"nota": i} for i in range(50)])
        tool = ChartGeneratorTool()
        result = tool._run(data=data, chart_type="histogram", x_column="nota")
        assert result.startswith("data:image/png;base64,") or "salvo" in result.lower()

    def test_correlation_heatmap(self):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        data = self._make_data([{"x": i, "y": i * 2} for i in range(20)])
        tool = ChartGeneratorTool()
        result = tool._run(data=data, chart_type="correlation_heatmap")
        assert result.startswith("data:image/png;base64,") or "salvo" in result.lower()

    def test_tipo_invalido(self):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        data = self._make_data([{"x": 1}])
        tool = ChartGeneratorTool()
        result = tool._run(data=data, chart_type="grafico_invalido")
        assert "ERRO" in result

    def test_salva_em_arquivo(self, tmp_path):
        from Sapiens_MultiAgente.tools.chart_generator_tool import ChartGeneratorTool
        data = self._make_data([{"nota": i} for i in range(30)])
        output = str(tmp_path / "grafico.png")
        tool = ChartGeneratorTool()
        result = tool._run(data=data, chart_type="histogram", x_column="nota", output_path=output)
        assert "salvo" in result.lower()
        assert os.path.exists(output)


# ---------------------------------------------------------------------------
# StatisticalAnalysisTool — ANOVA One-Way
# ---------------------------------------------------------------------------

class TestAnovaOneway:
    def _make_data(self, rows: list) -> str:
        return json.dumps(rows)

    def test_anova_basico(self):
        """ANOVA deve detectar diferença entre grupos com médias distintas."""
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        dados = (
            [{"grupo": "A", "nota": 5.0 + i * 0.1} for i in range(10)] +
            [{"grupo": "B", "nota": 8.0 + i * 0.1} for i in range(10)] +
            [{"grupo": "C", "nota": 3.0 + i * 0.1} for i in range(10)]
        )
        tool = StatisticalAnalysisTool()
        result = tool._run(
            data=self._make_data(dados),
            analysis_type="anova_one_way",
            group_column="grupo",
        )
        assert "ANOVA ONE-WAY" in result
        assert "F =" in result
        assert "Eta²" in result

    def test_anova_sem_group_column(self):
        """Sem group_column, deve retornar erro claro."""
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        dados = [{"grupo": "A", "nota": i} for i in range(5)]
        tool = StatisticalAnalysisTool()
        result = tool._run(data=self._make_data(dados), analysis_type="anova_one_way")
        assert "ERRO" in result

    def test_anova_grupo_inexistente(self):
        """Coluna de grupo que não existe no DataFrame deve retornar erro."""
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        dados = [{"nota": i} for i in range(5)]
        tool = StatisticalAnalysisTool()
        result = tool._run(
            data=self._make_data(dados),
            analysis_type="anova_one_way",
            group_column="coluna_inexistente",
        )
        assert "ERRO" in result

    def test_anova_post_hoc_3_grupos(self):
        """Com 3 grupos e ANOVA significativa, deve incluir comparações post-hoc."""
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        dados = (
            [{"g": "X", "val": float(i)} for i in range(5)] +
            [{"g": "Y", "val": float(i) + 20} for i in range(5)] +
            [{"g": "Z", "val": float(i) + 40} for i in range(5)]
        )
        tool = StatisticalAnalysisTool()
        result = tool._run(
            data=self._make_data(dados),
            analysis_type="anova_one_way",
            group_column="g",
        )
        assert "ANOVA ONE-WAY" in result
        # Post-hoc só aparece quando ANOVA é significativa e há 3+ grupos
        if "significativa" in result.lower():
            assert "vs" in result


# ---------------------------------------------------------------------------
# PDFSearchTool — extração de imagens
# ---------------------------------------------------------------------------

class TestPDFImageExtraction:
    def test_pdf_sem_imagens_retorna_mensagem(self, tmp_path):
        """PDF com apenas texto deve informar que não há imagens."""
        from Sapiens_MultiAgente.tools.pdf_search_tool import PDFSearchTool
        try:
            from pypdf import PdfWriter, PdfReader
            from pypdf.generic import NameObject

            # Cria PDF mínimo sem imagens
            writer = PdfWriter()
            writer.add_blank_page(width=200, height=200)
            pdf_path = str(tmp_path / "sem_imagens.pdf")
            with open(pdf_path, "wb") as f:
                writer.write(f)

            tool = PDFSearchTool()
            result = tool._run(file_path=pdf_path, extract_images=True)
            assert "imagem" in result.lower()
        except ImportError:
            pytest.skip("pypdf não disponível")

    def test_pdf_inexistente_com_extract_images(self):
        """Arquivo inexistente deve retornar ERRO mesmo com extract_images=True."""
        from Sapiens_MultiAgente.tools.pdf_search_tool import PDFSearchTool
        tool = PDFSearchTool()
        result = tool._run(file_path="/nao/existe.pdf", extract_images=True)
        assert "ERRO" in result


# ---------------------------------------------------------------------------
# DOCXSearchTool — extração de imagens
# ---------------------------------------------------------------------------

class TestDOCXImageExtraction:
    def test_docx_sem_imagens(self, tmp_path):
        """DOCX sem imagens deve informar que não há imagens."""
        from Sapiens_MultiAgente.tools.docx_search_tool import DOCXSearchTool
        try:
            from docx import Document
            doc = Document()
            doc.add_paragraph("Documento de teste sem imagens.")
            docx_path = str(tmp_path / "sem_imagens.docx")
            doc.save(docx_path)

            tool = DOCXSearchTool()
            result = tool._run(file_path=docx_path, extract_images=True)
            assert "imagem" in result.lower()
        except ImportError:
            pytest.skip("python-docx não disponível")

    def test_docx_inexistente(self):
        """Arquivo inexistente deve retornar ERRO."""
        from Sapiens_MultiAgente.tools.docx_search_tool import DOCXSearchTool
        tool = DOCXSearchTool()
        result = tool._run(file_path="/nao/existe.docx", extract_images=True)
        assert "ERRO" in result
