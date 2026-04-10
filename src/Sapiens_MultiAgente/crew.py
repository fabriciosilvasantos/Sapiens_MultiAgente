import os
from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
    FileReadTool,
    ScrapeWebsiteTool,
)

from .config.llm_settings import get_model_for_agent
from .config.llm_fallback import build_llm
from .tools.data_validation_tool import DataValidationTool
from .tools.csv_processor_tool import CSVProcessorTool
from .tools.statistical_analysis_tool import StatisticalAnalysisTool
from .tools.pdf_search_tool import PDFSearchTool
from .tools.docx_search_tool import DOCXSearchTool
from .tools.csv_search_tool import CSVSearchTool
from .tools.chart_generator_tool import ChartGeneratorTool
from .tools.external_data_tool import ExternalDataTool
from .tools.quality_review_tool import QualityReviewTool
from .tools.text_analysis_tool import TextAnalysisTool


@CrewBase
class SapiensAcademicMultiAgentDataAnalysisPlatformCrew:
    """SapiensAcademicMultiAgentDataAnalysisPlatform crew"""

    def _get_llm(self, agent_name: str = "") -> LLM:
        """Retorna LLM otimizado para o agente, com fallback Groq se GROQ_API_KEY estiver definida."""
        m = get_model_for_agent(agent_name)
        return build_llm(
            model_cfg=m,
            openrouter_api_key=os.environ.get("OPENAI_API_KEY", ""),
            openrouter_base_url=os.environ.get("OPENAI_API_BASE", "https://openrouter.ai/api/v1"),
            groq_api_key=os.environ.get("GROQ_API_KEY") or None,
        )

    @agent
    def agente_gerente_orquestrador(self) -> Agent:
        return Agent(
            config=self.agents_config["agente_gerente_orquestrador"],
            tools=[
                FileReadTool(),
                DataValidationTool(),
                CSVProcessorTool(),
            ],
            llm=self._get_llm("agente_gerente_orquestrador"),
        )

    @agent
    def especialista_em_analise_descritiva(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_em_analise_descritiva"],
            tools=[
                FileReadTool(),
                StatisticalAnalysisTool(),
                ChartGeneratorTool(),  # único agente com geração de gráficos
            ],
            llm=self._get_llm("especialista_em_analise_descritiva"),
        )

    @agent
    def especialista_em_analise_diagnostica(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_em_analise_diagnostica"],
            tools=[
                FileReadTool(),
                StatisticalAnalysisTool(),
            ],
            llm=self._get_llm("especialista_em_analise_diagnostica"),
        )

    @agent
    def especialista_em_analise_preditiva(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_em_analise_preditiva"],
            tools=[
                FileReadTool(),
                StatisticalAnalysisTool(),
            ],
            llm=self._get_llm("especialista_em_analise_preditiva"),
        )

    @agent
    def especialista_em_analise_prescritiva(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_em_analise_prescritiva"],
            tools=[
                FileReadTool(),
                StatisticalAnalysisTool(),
                CSVSearchTool(),
            ],
            llm=self._get_llm("especialista_em_analise_prescritiva"),
        )

    @agent
    def especialista_em_fontes_externas(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_em_fontes_externas"],
            tools=[
                ExternalDataTool(),
                ScrapeWebsiteTool(),
            ],
            llm=self._get_llm("especialista_em_fontes_externas"),
        )

    @agent
    def especialista_em_analise_textual(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_em_analise_textual"],
            tools=[
                TextAnalysisTool(),
                FileReadTool(),
                PDFSearchTool(),
                DOCXSearchTool(),
            ],
            llm=self._get_llm("especialista_em_analise_textual"),
        )

    @agent
    def revisor_de_qualidade_cientifica(self) -> Agent:
        return Agent(
            config=self.agents_config["revisor_de_qualidade_cientifica"],
            tools=[
                QualityReviewTool(),
            ],
            llm=self._get_llm("revisor_de_qualidade_cientifica"),
        )

    @task
    def validacao_rigorosa_de_dados_e_pergunta(self) -> Task:
        return Task(
            config=self.tasks_config["validacao_rigorosa_de_dados_e_pergunta"],
        )

    @task
    def processamento_de_dados_reais_validados(self) -> Task:
        return Task(
            config=self.tasks_config["processamento_de_dados_reais_validados"],
        )

    @task
    def executar_analise_descritiva(self) -> Task:
        return Task(
            config=self.tasks_config["executar_analise_descritiva"],
            async_execution=True,
        )

    @task
    def executar_analise_diagnostica(self) -> Task:
        return Task(
            config=self.tasks_config["executar_analise_diagnostica"],
            async_execution=True,
        )

    @task
    def executar_analise_preditiva(self) -> Task:
        return Task(
            config=self.tasks_config["executar_analise_preditiva"],
            async_execution=True,
        )

    @task
    def executar_analise_prescritiva(self) -> Task:
        return Task(
            config=self.tasks_config["executar_analise_prescritiva"],
            async_execution=True,
        )

    @task
    def buscar_dados_externos_e_benchmarks(self) -> Task:
        return Task(
            config=self.tasks_config["buscar_dados_externos_e_benchmarks"],
            async_execution=True,
        )

    @task
    def executar_analise_textual(self) -> Task:
        return Task(
            config=self.tasks_config["executar_analise_textual"],
            async_execution=True,
        )

    @task
    def revisar_qualidade_cientifica(self) -> Task:
        return Task(
            config=self.tasks_config["revisar_qualidade_cientifica"],
        )

    @task
    def compilacao_e_apresentacao_do_relatorio_final(self) -> Task:
        return Task(
            config=self.tasks_config["compilacao_e_apresentacao_do_relatorio_final"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the SapiensAcademicMultiAgentDataAnalysisPlatform crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
