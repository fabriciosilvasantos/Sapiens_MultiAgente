"""
Testes da validação e do resumo dos arquivos feitos em Python antes da crew.
"""

import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

DATASET_UENF = os.path.join(os.path.dirname(__file__), '..', 'data', 'uenf_alunos_2020_2025.csv')


class TestValidarArquivos:

    def test_retorna_caminhos_validos(self, tmp_path):
        from Sapiens_MultiAgente.preparacao_dados import validar_arquivos
        pdf = tmp_path / "relatorio.pdf"
        pdf.write_bytes(b"%PDF-1.4")
        assert validar_arquivos([DATASET_UENF, str(pdf)]) == [DATASET_UENF, str(pdf)]

    def test_aceita_string_unica(self):
        from Sapiens_MultiAgente.preparacao_dados import validar_arquivos
        assert validar_arquivos(DATASET_UENF) == [DATASET_UENF]

    @pytest.mark.parametrize("arquivos", [[], None, ""])
    def test_sem_arquivos(self, arquivos):
        from Sapiens_MultiAgente.preparacao_dados import DadosNecessarios, validar_arquivos
        with pytest.raises(DadosNecessarios, match="DADOS NECESSÁRIOS: nenhum arquivo foi enviado"):
            validar_arquivos(arquivos)

    def test_lista_todos_os_problemas(self, tmp_path):
        from Sapiens_MultiAgente.preparacao_dados import DadosNecessarios, validar_arquivos
        sem_extensao = tmp_path / "dados"
        sem_extensao.write_text("a,b\n1,2\n")
        with pytest.raises(DadosNecessarios) as erro:
            validar_arquivos([DATASET_UENF, "/nao/existe.xlsx", str(sem_extensao)])
        mensagem = str(erro.value)
        assert "existe.xlsx: arquivo não encontrado" in mensagem
        assert "dados: extensão '(nenhuma)' não aceita" in mensagem
        assert "uenf_alunos" not in mensagem

    def test_diretorio_nao_e_arquivo(self, tmp_path):
        from Sapiens_MultiAgente.preparacao_dados import DadosNecessarios, validar_arquivos
        pasta = tmp_path / "pasta.csv"
        pasta.mkdir()
        with pytest.raises(DadosNecessarios, match="pasta.csv: arquivo não encontrado"):
            validar_arquivos([str(pasta)])


class TestResumirArquivos:

    def test_tabela_e_documento(self, tmp_path):
        from Sapiens_MultiAgente.preparacao_dados import resumir_arquivos
        docx = tmp_path / "ata.docx"
        docx.write_bytes(b"x" * 2048)
        resumo = resumir_arquivos([DATASET_UENF, str(docx)])
        assert resumo.startswith("Arquivos validados pelo SAPIENS:")
        assert "- uenf_alunos_2020_2025.csv (CSV, 7.9 KB) — tabela com 132 linhas e 11 colunas" in resumo
        assert "- ata.docx (DOCX, 2.0 KB) — documento textual" in resumo

    def test_xlsx_e_tamanho_em_bytes(self, tmp_path):
        from Sapiens_MultiAgente.preparacao_dados import resumir_arquivos
        xlsx = tmp_path / "dados.xlsx"
        pd.DataFrame({"x": [1, 2, 3]}).to_excel(xlsx, index=False)
        txt = tmp_path / "nota.txt"
        txt.write_text("curta")
        resumo = resumir_arquivos([str(xlsx), str(txt)])
        assert "tabela com 3 linhas e 1 colunas" in resumo
        assert "- nota.txt (TXT, 5 B) — documento textual" in resumo

    def test_tabela_ilegivel_nao_derruba(self, tmp_path):
        from Sapiens_MultiAgente.preparacao_dados import resumir_arquivos
        quebrado = tmp_path / "quebrado.xlsx"
        quebrado.write_bytes(b"isto nao e um excel")
        resumo = resumir_arquivos([str(quebrado)])
        assert "quebrado.xlsx" in resumo
        assert "❌ ERRO" in resumo
