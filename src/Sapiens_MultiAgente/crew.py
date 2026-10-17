import os
import threading
from pathlib import Path
from typing import Any

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, before_kickoff, crew, task
from crewai.tasks.conditional_task import ConditionalTask
from crewai_tools import (
    FileReadTool,
    ScrapeWebsiteTool,
)

from .config.llm_settings import get_model_for_agent
from .config.llm_fallback import build_llm
from .estatisticas_previas import calcular_estatisticas_previas
from .preparacao_dados import resumir_arquivos, validar_arquivos
from .tools.statistical_analysis_tool import StatisticalAnalysisTool
from .tools.pdf_search_tool import PDFSearchTool
from .tools.docx_search_tool import DOCXSearchTool
from .tools.csv_search_tool import CSVSearchTool
from .tools.chart_generator_tool import ChartGeneratorTool
from .tools.external_data_tool import ExternalDataTool
from .tools.quality_review_tool import QualityReviewTool
from .tools.text_analysis_tool import TextAnalysisTool

EXTENSOES_DOCUMENTOS = {".pdf", ".docx", ".txt"}


class TaskParalela(Task):
    """Task async cujo erro chega ao Future.

    No CrewAI 0.203, Task._execute_task_async não trata exceções: se o agente
    falha (erro do LLM, rate limit, cancelamento), o Future nunca é resolvido
    e Crew.kickoff fica bloqueado para sempre esperando por ele.
    """

    def _execute_task_async(self, agent, context, tools, future) -> None:
        try:
            resultado = self._execute_core(agent, context, tools)
        except BaseException as erro:  # noqa: BLE001 - qualquer falha precisa liberar o Future
            future.set_exception(erro)
        else:
            future.set_result(resultado)


class AnaliseCancelada(TimeoutError):
    """Levantada nos callbacks da crew depois de cancelar(); interrompe agentes e tasks.

    Herda de TimeoutError porque o CrewAI repassa esse tipo sem as retentativas
    automáticas do agente (max_retry_limit), encerrando a execução de imediato.
    """


def ha_documentos_textuais(arquivos: Any) -> bool:
    """True se algum dos arquivos enviados for documento textual (PDF, DOCX, TXT)."""
    if isinstance(arquivos, str):
        arquivos = [arquivos]
    return any(Path(str(a)).suffix.lower() in EXTENSOES_DOCUMENTOS for a in arquivos or [])


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

    # Sem kickoff (ex.: replay), executa a análise textual como antes.
    _tem_documentos: bool = True

    def __init__(self):
        self._cancelamento = threading.Event()

    def cancelar(self) -> None:
        """Pede o fim da execução: cada agente para no próximo passo (após a chamada ao LLM em curso).

        Threads Python não podem ser interrompidas de fora; sem isto a crew
        continuaria consumindo tokens depois do timeout da análise.
        """
        self._cancelamento.set()

    def _verificar_cancelamento(self, _saida: Any) -> None:
        if self._cancelamento.is_set():
            raise AnaliseCancelada("Análise cancelada: tempo limite excedido.")

    @before_kickoff
    def _preparar_entradas(self, inputs: dict | None) -> dict | None:
        """Valida e prepara os arquivos em Python, sem chamar o LLM.

        - sem arquivos utilizáveis, levanta DadosNecessarios ("DADOS NECESSÁRIOS: ...")
          antes de qualquer chamada ao modelo;
        - {resumo_dados}: tipo, tamanho e dimensões de cada arquivo;
        - {estatisticas_previas}: descritiva e correlação calculadas em Python;
        - registra se há PDF/DOCX/TXT, para a condição da análise textual.
        """
        self._verificar_cancelamento(None)
        inputs = dict(inputs or {})
        arquivos = validar_arquivos(inputs.get("arquivos_analisados"))
        self._tem_documentos = ha_documentos_textuais(arquivos)
        inputs.setdefault("resumo_dados", resumir_arquivos(arquivos))
        inputs.setdefault("estatisticas_previas", calcular_estatisticas_previas(arquivos))
        return inputs

    @agent
    def agente_gerente_orquestrador(self) -> Agent:
        return Agent(
            config=self.agents_config["agente_gerente_orquestrador"],
            # Só compila o relatório a partir do context: validação e processamento
            # dos arquivos são feitos em Python (preparacao_dados.py) antes do kickoff.
            tools=[],
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
    def executar_analise_descritiva(self) -> Task:
        return TaskParalela(
            config=self.tasks_config["executar_analise_descritiva"],
            async_execution=True,
        )

    @task
    def executar_analise_diagnostica(self) -> Task:
        return TaskParalela(
            config=self.tasks_config["executar_analise_diagnostica"],
            async_execution=True,
        )

    @task
    def executar_analise_preditiva(self) -> Task:
        return TaskParalela(
            config=self.tasks_config["executar_analise_preditiva"],
            async_execution=True,
        )

    @task
    def buscar_dados_externos_e_benchmarks(self) -> Task:
        return TaskParalela(
            config=self.tasks_config["buscar_dados_externos_e_benchmarks"],
            async_execution=True,
        )

    @task
    def executar_analise_textual(self) -> Task:
        # ConditionalTask não pode ser a primeira task nem async; o CrewAI aguarda
        # as tasks paralelas pendentes antes de avaliá-la, por isso fica logo após
        # o bloco paralelo. A condição usa os arquivos enviados, não o texto do LLM.
        return ConditionalTask(
            config=self.tasks_config["executar_analise_textual"],
            condition=lambda _saida_anterior: self._tem_documentos,
        )

    @task
    def executar_analise_prescritiva(self) -> Task:
        return Task(
            config=self.tasks_config["executar_analise_prescritiva"],
            # Síncrona: aguarda as análises paralelas, cujos achados recebe via context.
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
            # Chamados após cada passo de agente e cada task concluída.
            step_callback=self._verificar_cancelamento,
            task_callback=self._verificar_cancelamento,
        )
