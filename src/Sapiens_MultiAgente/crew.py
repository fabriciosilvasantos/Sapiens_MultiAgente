import os

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
    FileReadTool,
    ScrapeWebsiteTool
)

# Import custom tools
from .tools.data_validation_tool import DataValidationTool
from .tools.csv_processor_tool import CSVProcessorTool
from .tools.statistical_analysis_tool import StatisticalAnalysisTool
from .tools.pdf_search_tool import PDFSearchTool
from .tools.docx_search_tool import DOCXSearchTool
from .tools.csv_search_tool import CSVSearchTool




@CrewBase
class SapiensAcademicMultiAgentDataAnalysisPlatformCrew:
    """SapiensAcademicMultiAgentDataAnalysisPlatform crew"""


    @agent
    def agente_gerente_orquestrador(self) -> Agent:
        return Agent(
            config=self.agents_config["agente_gerente_orquestrador"],
            tools=[
                FileReadTool(),
                ScrapeWebsiteTool(),
                DataValidationTool(),
                CSVProcessorTool()
            ]
        )

    @agent
    def especialista_em_analise_descritiva(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_em_analise_descritiva"],
            tools=[
                FileReadTool(),
                StatisticalAnalysisTool()
            ]
        )

    @agent
    def especialista_em_analise_diagnostica(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_em_analise_diagnostica"],
            tools=[
                FileReadTool(),
                StatisticalAnalysisTool(),
                CSVProcessorTool()
            ]
        )

    @agent
    def especialista_em_analise_preditiva(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_em_analise_preditiva"],
            tools=[
                FileReadTool(),
                StatisticalAnalysisTool()
            ]
        )

    @agent
    def especialista_em_analise_prescritiva(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_em_analise_prescritiva"],
            tools=[
                FileReadTool(),
                StatisticalAnalysisTool(),
                CSVProcessorTool()
            ]
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
        )

    @task
    def executar_analise_diagnostica(self) -> Task:
        return Task(
            config=self.tasks_config["executar_analise_diagnostica"],
        )

    @task
    def executar_analise_preditiva(self) -> Task:
        return Task(
            config=self.tasks_config["executar_analise_preditiva"],
        )

    @task
    def executar_analise_prescritiva(self) -> Task:
        return Task(
            config=self.tasks_config["executar_analise_prescritiva"],
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
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
