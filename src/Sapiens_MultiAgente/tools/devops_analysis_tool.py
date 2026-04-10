import os
import json
import csv
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class DevOpsAnalysisToolInput(BaseModel):
    """Input schema para DevOpsAnalysisTool."""

    data_source: str = Field(
        ...,
        description=(
            "Caminho para arquivo (CSV, JSON, TXT) com dados de CI/CD/infraestrutura, "
            "ou texto direto com métricas e logs."
        ),
    )
    analysis_type: str = Field(
        default="geral",
        description="Tipo de análise: geral | pipeline | infraestrutura | incidentes",
    )


class DevOpsAnalysisTool(BaseTool):
    name: str = "DevOpsAnalysisTool"
    description: str = (
        "Analisa dados de CI/CD, pipelines de build/deploy, métricas de infraestrutura "
        "e registros de incidentes. Aceita arquivos CSV/JSON/TXT ou texto direto com "
        "logs e métricas operacionais."
    )
    args_schema: Type[BaseModel] = DevOpsAnalysisToolInput

    def _run(self, data_source: str, analysis_type: str = "geral") -> str:
        try:
            content = self._load_content(data_source)
            if content.startswith("❌ ERRO"):
                return content

            if analysis_type == "pipeline":
                return self._analyze_pipeline(content)
            elif analysis_type == "infraestrutura":
                return self._analyze_infrastructure(content)
            elif analysis_type == "incidentes":
                return self._analyze_incidents(content)
            else:
                return self._analyze_general(content)

        except Exception as e:
            return f"❌ ERRO: {str(e)}"

    # ------------------------------------------------------------------
    # Carregamento de dados
    # ------------------------------------------------------------------

    def _load_content(self, data_source: str) -> str:
        """Tenta carregar como arquivo; se não existir, trata como texto direto."""
        if not os.path.exists(data_source):
            return data_source

        ext = os.path.splitext(data_source)[1].lower()

        try:
            if ext == ".json":
                with open(data_source, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return json.dumps(data, ensure_ascii=False, indent=2)

            elif ext == ".csv":
                rows = []
                with open(data_source, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        rows.append(row)
                return json.dumps(rows[:500], ensure_ascii=False, indent=2)

            else:
                with open(data_source, "r", encoding="utf-8", errors="replace") as f:
                    return f.read(50_000)

        except Exception as e:
            return f"❌ ERRO ao ler arquivo '{data_source}': {str(e)}"

    # ------------------------------------------------------------------
    # Análises
    # ------------------------------------------------------------------

    def _analyze_general(self, content: str) -> str:
        lines = content.splitlines()
        total_lines = len(lines)

        keywords_erro = [
            ln for ln in lines
            if any(k in ln.lower() for k in ("error", "erro", "fail", "falha", "exception"))
        ]
        keywords_ok = [
            ln for ln in lines
            if any(k in ln.lower() for k in ("success", "sucesso", "passed", "ok", "deploy"))
        ]

        taxa_erro = round(len(keywords_erro) / max(total_lines, 1) * 100, 1)
        taxa_ok = round(len(keywords_ok) / max(total_lines, 1) * 100, 1)

        return (
            f"## Análise DevOps — Visão Geral\n\n"
            f"**Fonte de dados:** {total_lines} linhas analisadas\n\n"
            f"### Resumo de Eventos\n"
            f"- Registros com indicadores de **erro/falha**: {len(keywords_erro)} ({taxa_erro}%)\n"
            f"- Registros com indicadores de **sucesso**: {len(keywords_ok)} ({taxa_ok}%)\n\n"
            f"### Amostra de Erros Identificados\n"
            + (
                "\n".join(f"- `{ln.strip()}`" for ln in keywords_erro[:5])
                if keywords_erro
                else "_Nenhum erro encontrado nos dados._"
            )
            + "\n\n### Recomendações\n"
            + self._recommendations(taxa_erro)
        )

    def _analyze_pipeline(self, content: str) -> str:
        lines = content.splitlines()

        builds = [ln for ln in lines if "build" in ln.lower()]
        deploys = [ln for ln in lines if "deploy" in ln.lower()]
        falhas = [ln for ln in lines if any(k in ln.lower() for k in ("failed", "error", "falha"))]
        duracoes = self._extract_durations(content)

        avg_dur = round(sum(duracoes) / len(duracoes), 1) if duracoes else None

        relatorio = (
            f"## Análise de Pipeline CI/CD\n\n"
            f"| Métrica | Valor |\n"
            f"|---------|-------|\n"
            f"| Eventos de Build | {len(builds)} |\n"
            f"| Eventos de Deploy | {len(deploys)} |\n"
            f"| Falhas detectadas | {len(falhas)} |\n"
        )
        if avg_dur:
            relatorio += f"| Duração média estimada | {avg_dur}s |\n"

        relatorio += "\n### Falhas Identificadas\n"
        relatorio += (
            "\n".join(f"- `{ln.strip()}`" for ln in falhas[:8])
            if falhas
            else "_Nenhuma falha explícita encontrada._"
        )

        taxa = round(len(falhas) / max(len(builds) + len(deploys), 1) * 100, 1)
        relatorio += f"\n\n**Taxa de falha estimada:** {taxa}%\n\n"
        relatorio += "### Recomendações\n" + self._recommendations(taxa)
        return relatorio

    def _analyze_infrastructure(self, content: str) -> str:
        lines = content.splitlines()

        cpu_lines = [ln for ln in lines if "cpu" in ln.lower()]
        mem_lines = [ln for ln in lines if any(k in ln.lower() for k in ("mem", "memory", "memória"))]
        disk_lines = [ln for ln in lines if any(k in ln.lower() for k in ("disk", "disco", "storage"))]
        alert_lines = [ln for ln in lines if any(k in ln.lower() for k in ("alert", "alerta", "critical", "crítico"))]

        return (
            f"## Análise de Infraestrutura\n\n"
            f"| Componente | Registros |\n"
            f"|------------|----------|\n"
            f"| CPU | {len(cpu_lines)} |\n"
            f"| Memória | {len(mem_lines)} |\n"
            f"| Disco | {len(disk_lines)} |\n"
            f"| Alertas | {len(alert_lines)} |\n\n"
            f"### Alertas Críticos\n"
            + (
                "\n".join(f"- `{ln.strip()}`" for ln in alert_lines[:8])
                if alert_lines
                else "_Nenhum alerta crítico detectado._"
            )
            + "\n\n### Recomendações de Infraestrutura\n"
            "- Monitorar tendências de CPU e memória para identificar vazamentos de recursos.\n"
            "- Configurar alertas proativos com thresholds baseados nos dados históricos.\n"
            "- Revisar estratégia de escalabilidade horizontal se houver picos recorrentes.\n"
        )

    def _analyze_incidents(self, content: str) -> str:
        lines = content.splitlines()

        p1 = [ln for ln in lines if any(k in ln.lower() for k in ("p1", "crítico", "critical", "sev1"))]
        p2 = [ln for ln in lines if any(k in ln.lower() for k in ("p2", "alto", "high", "sev2"))]
        resolved = [ln for ln in lines if any(k in ln.lower() for k in ("resolved", "resolvido", "closed", "fechado"))]

        total = len(p1) + len(p2)
        taxa_resolucao = round(len(resolved) / max(total, 1) * 100, 1)

        return (
            f"## Análise de Incidentes\n\n"
            f"| Severidade | Quantidade |\n"
            f"|------------|------------|\n"
            f"| P1 — Crítico | {len(p1)} |\n"
            f"| P2 — Alto | {len(p2)} |\n"
            f"| Resolvidos | {len(resolved)} |\n\n"
            f"**Taxa de resolução:** {taxa_resolucao}%\n\n"
            f"### Incidentes Críticos (P1)\n"
            + (
                "\n".join(f"- `{ln.strip()}`" for ln in p1[:5])
                if p1
                else "_Nenhum incidente P1 detectado._"
            )
            + "\n\n### Recomendações\n"
            "- Implementar post-mortems para todos os incidentes P1.\n"
            "- Estabelecer runbooks para reduzir MTTR em ocorrências recorrentes.\n"
            "- Revisar monitoramento e alertas para detecção mais precoce.\n"
        )

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------

    def _extract_durations(self, content: str) -> list:
        """Extrai valores numéricos próximos de 's' (segundos) ou 'ms' no texto."""
        import re
        matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:ms|s\b)", content)
        return [float(m) for m in matches[:100]]

    def _recommendations(self, taxa_erro: float) -> str:
        if taxa_erro >= 20:
            return (
                "- **Alta taxa de erros** detectada. Priorizar investigação imediata das causas raiz.\n"
                "- Implementar circuit breakers e fallbacks nos componentes com maior número de falhas.\n"
                "- Revisar pipelines de qualidade (testes automatizados, code review).\n"
            )
        elif taxa_erro >= 5:
            return (
                "- Taxa de erros moderada. Monitorar tendência e implementar alertas proativos.\n"
                "- Adicionar mais cobertura de testes nas áreas com maior incidência de erros.\n"
            )
        else:
            return (
                "- Taxa de erros dentro do esperado. Manter monitoramento contínuo.\n"
                "- Documentar práticas atuais para garantir consistência.\n"
            )
