"""
Testes das estatísticas calculadas antes da crew (estatisticas_previas.py)
e da omissão de identificadores na análise descritiva.
"""

import os
import sys
from unittest.mock import patch

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

DATASET_UENF = os.path.join(os.path.dirname(__file__), '..', 'data', 'uenf_alunos_2020_2025.csv')


class TestCalcularEstatisticasPrevias:

    def test_sem_arquivos(self):
        from Sapiens_MultiAgente.estatisticas_previas import calcular_estatisticas_previas, SEM_DADOS_TABULARES
        assert calcular_estatisticas_previas([]) == SEM_DADOS_TABULARES
        assert calcular_estatisticas_previas(None) == SEM_DADOS_TABULARES

    def test_ignora_documentos(self):
        from Sapiens_MultiAgente.estatisticas_previas import calcular_estatisticas_previas, SEM_DADOS_TABULARES
        assert calcular_estatisticas_previas(['/up/relatorio.pdf', '/up/ata.docx', '/up/notas.txt']) \
            == SEM_DADOS_TABULARES

    def test_dataset_real_uenf(self):
        from Sapiens_MultiAgente.estatisticas_previas import calcular_estatisticas_previas
        texto = calcular_estatisticas_previas([DATASET_UENF])
        assert "### Arquivo: uenf_alunos_2020_2025.csv" in texto
        assert "Linhas: 132 | Colunas: 11" in texto
        assert "Valores ausentes: nenhum" in texto
        assert "ANÁLISE DESCRITIVA" in texto
        assert "evadidos ↔ reprovacoes: r = 0.907" in texto
        assert "❌" not in texto

    def test_aceita_caminho_unico_como_string(self):
        from Sapiens_MultiAgente.estatisticas_previas import calcular_estatisticas_previas
        assert "Linhas: 132" in calcular_estatisticas_previas(DATASET_UENF)

    def test_reporta_valores_ausentes(self, tmp_path):
        from Sapiens_MultiAgente.estatisticas_previas import calcular_estatisticas_previas
        arquivo = tmp_path / "notas.csv"
        arquivo.write_text("nota,frequencia\n7.5,80\n,90\n6.5,\n9.0,95\n", encoding="utf-8")
        texto = calcular_estatisticas_previas([str(arquivo)])
        assert "Valores ausentes: nota=1, frequencia=1" in texto

    def test_varios_arquivos_e_arquivo_inexistente(self, tmp_path):
        from Sapiens_MultiAgente.estatisticas_previas import calcular_estatisticas_previas
        xlsx = tmp_path / "dados.xlsx"
        pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 6, 8]}).to_excel(xlsx, index=False)
        texto = calcular_estatisticas_previas([str(xlsx), "/nao/existe.csv"])
        assert "### Arquivo: dados.xlsx" in texto
        assert "### Arquivo: existe.csv" in texto
        assert "❌ ERRO: Arquivo não encontrado" in texto

    def test_falha_inesperada_nao_derruba(self):
        from Sapiens_MultiAgente import estatisticas_previas
        with patch.object(estatisticas_previas, "_estatisticas_do_arquivo", side_effect=RuntimeError("boom")):
            texto = estatisticas_previas.calcular_estatisticas_previas(["/up/notas.csv"])
        assert "❌ ERRO: não foi possível calcular estatísticas: boom" in texto

    def test_trunca_saida_grande(self, tmp_path, monkeypatch):
        from Sapiens_MultiAgente import estatisticas_previas
        monkeypatch.setattr(estatisticas_previas, "MAX_CARACTERES_POR_ARQUIVO", 300)
        texto = estatisticas_previas.calcular_estatisticas_previas([DATASET_UENF])
        assert "(truncado; use StatisticalAnalysisTool para o restante)" in texto
        assert len(texto) < 500


class TestDescritivaOmiteIdentificadores:
    """Colunas quase únicas (nomes, matrículas) não podem ir listadas ao LLM."""

    @pytest.fixture
    def tool(self):
        from Sapiens_MultiAgente.tools.statistical_analysis_tool import StatisticalAnalysisTool
        return StatisticalAnalysisTool()

    def test_coluna_de_nomes_e_omitida(self, tool, tmp_path):
        arquivo = tmp_path / "alunos.csv"
        linhas = ["nome,nota"] + [f"Aluno Número {i},{5 + i % 5}" for i in range(40)]
        arquivo.write_text("\n".join(linhas), encoding="utf-8")
        resultado = tool._run(file_path=str(arquivo), analysis_type="descritiva")
        assert "nome: 40 valores distintos (provável identificador — valores omitidos)" in resultado
        assert "Aluno Número 7" not in resultado

    def test_categorias_limitadas_as_mais_frequentes(self, tool, tmp_path):
        arquivo = tmp_path / "cursos.csv"
        # 20 cursos, cada um repetido 5 vezes: categórica de verdade, mas acima do limite
        linhas = ["curso,nota"] + [f"Curso {i % 20},{i % 10}" for i in range(100)]
        arquivo.write_text("\n".join(linhas), encoding="utf-8")
        resultado = tool._run(file_path=str(arquivo), analysis_type="descritiva")
        assert "… e mais 5 categorias" in resultado

    def test_categorias_pequenas_listadas_por_inteiro(self, tool):
        resultado = tool._run(file_path=DATASET_UENF, analysis_type="descritiva")
        assert "Pedagogia" in resultado
        assert "2025/1" in resultado
        assert "e mais" not in resultado


class TestIntegracaoComCrew:

    ENV = {'OPENAI_API_KEY': 'test-key', 'OPENAI_API_BASE': 'http://localhost'}

    def test_tasks_numericas_recebem_estatisticas(self):
        from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        config = SapiensAcademicMultiAgentDataAnalysisPlatformCrew().tasks_config
        for nome in [
            'executar_analise_descritiva',
            'executar_analise_diagnostica',
            'executar_analise_preditiva',
            'revisar_qualidade_cientifica',
        ]:
            assert '{estatisticas_previas}' in config[nome]['description'], nome

    def test_before_kickoff_calcula_estatisticas(self):
        from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        with patch.dict(os.environ, self.ENV):
            instancia = SapiensAcademicMultiAgentDataAnalysisPlatformCrew()
        entradas = instancia._preparar_entradas({'topico_pesquisa': 'Evasão', 'arquivos_analisados': [DATASET_UENF]})
        assert "r = 0.907" in entradas['estatisticas_previas']
        assert entradas['topico_pesquisa'] == 'Evasão'

    def test_before_kickoff_respeita_valor_informado(self):
        from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        with patch.dict(os.environ, self.ENV):
            instancia = SapiensAcademicMultiAgentDataAnalysisPlatformCrew()
        entradas = instancia._preparar_entradas({'arquivos_analisados': [DATASET_UENF],
                                                 'estatisticas_previas': 'já calculado'})
        assert entradas['estatisticas_previas'] == 'já calculado'

    def test_kickoff_entrega_numeros_as_tasks(self):
        from crewai import Agent
        from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        descricoes = {}

        def agente_falso(self, task, context=None, tools=None):
            descricoes[task.name] = task.description
            return "ok"

        env = {**self.ENV, 'CREWAI_DISABLE_TELEMETRY': 'true', 'OTEL_SDK_DISABLED': 'true'}
        with patch.dict(os.environ, env), patch.object(Agent, 'execute_task', agente_falso):
            crew = SapiensAcademicMultiAgentDataAnalysisPlatformCrew().crew()
            crew.kickoff(inputs={'topico_pesquisa': 'Evasão', 'arquivos_analisados': [DATASET_UENF]})

        assert "evadidos ↔ reprovacoes: r = 0.907" in descricoes['executar_analise_diagnostica']
        assert "Linhas: 132 | Colunas: 11" in descricoes['revisar_qualidade_cientifica']
        assert "r = 0.907" not in descricoes['buscar_dados_externos_e_benchmarks']
