from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
    FileReadTool,
    ScrapeWebsiteTool,
)

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

    @agent
    def agente_gerente_orquestrador(self) -> Agent:
        return Agent(
            config=self.agents_config["agente_gerente_orquestrador"],
            tools=[
                FileReadTool(),
                DataValidationTool(),
                CSVProcessorTool(),
            ],
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
        )

    @agent
    def especialista_em_analise_diagnostica(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_em_analise_diagnostica"],
            tools=[
                FileReadTool(),
                StatisticalAnalysisTool(),
            ],
        )

    @agent
    def especialista_em_analise_preditiva(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_em_analise_preditiva"],
            tools=[
                FileReadTool(),
                StatisticalAnalysisTool(),
            ],
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
        )

    @agent
    def especialista_em_fontes_externas(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_em_fontes_externas"],
            tools=[
                ExternalDataTool(),
                ScrapeWebsiteTool(),
            ],
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
        )

    @agent
    def revisor_de_qualidade_cientifica(self) -> Agent:
        return Agent(
            config=self.agents_config["revisor_de_qualidade_cientifica"],
            tools=[
                QualityReviewTool(),
            ],
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
