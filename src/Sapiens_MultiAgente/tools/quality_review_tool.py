"""
Ferramenta de revisão de qualidade científica para análises acadêmicas.

Verifica consistência metodológica, conclusões sem suporte estatístico,
vieses analíticos e boas práticas de rigor científico.
"""

import re
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


# Padrões que indicam possíveis problemas metodológicos
ALERTAS_METODOLOGICOS = [
    (r"\bprova\b|\bcomprova\b|\bconfirma\b",
     "Linguagem determinística: análise estatística não 'prova', indica evidências."),
    (r"\bsempre\b|\bnunca\b|\btodos\b|\bnenhum\b",
     "Generalização absoluta detectada — verifique se os dados suportam essa afirmação."),
    (r"\bcausa\b|\bprovoca\b|\bgera\b",
     "Afirmação causal: correlação ≠ causalidade. Verifique se há delineamento experimental."),
    (r"n\s*=\s*[1-9]\b|amostra.*pequena|poucos dados",
     "Amostra possivelmente pequena — resultados podem ter baixo poder estatístico."),
    (r"p\s*[<>=]\s*0\.\d+",
     "Valor-p detectado — verificar se o contexto menciona tamanho de efeito, não apenas significância."),
    (r"r²?\s*=\s*0\.[0-2]\d",
     "R² baixo (< 0.3) detectado — modelo explica pouca variância; interpretar com cautela."),
    (r"sem dados|dados insuficientes|não foi possível",
     "Limitação de dados identificada — verificar se a análise sinaliza isso ao leitor."),
]

# Checklist de boas práticas por tipo de análise
CHECKLIST_POR_TIPO = {
    "descritiva": [
        "Medidas de tendência central (média/mediana) reportadas",
        "Medidas de dispersão (desvio padrão/IQR) reportadas",
        "Tamanho da amostra (n) explicitado",
        "Outliers identificados ou tratados",
        "Distribuição dos dados caracterizada",
    ],
    "diagnostica": [
        "Teste de normalidade realizado antes de testes paramétricos",
        "Nível de significância (α) definido",
        "Tamanho de efeito reportado (não apenas p-valor)",
        "Hipóteses nula e alternativa formuladas",
        "Pressupostos do teste verificados",
    ],
    "preditiva": [
        "Separação treino/teste ou validação cruzada realizada",
        "Métricas de desempenho do modelo reportadas",
        "Intervalo de confiança das previsões incluído",
        "Limitações do modelo mencionadas",
        "Horizonte de previsão claramente definido",
    ],
    "prescritiva": [
        "Recomendações baseadas em evidências dos dados",
        "Priorização com critérios explícitos",
        "Limitações e riscos mencionados",
        "Métricas de sucesso para as recomendações definidas",
        "Custo/benefício considerado",
    ],
}


class QualityReviewToolInput(BaseModel):
    """Input schema para QualityReviewTool."""

    conteudo_analise: str = Field(
        ...,
        description="Texto completo ou trecho da análise a ser revisada.",
    )
    tipo_analise: str = Field(
        default="geral",
        description=(
            "Tipo da análise sendo revisada: "
            "'descritiva', 'diagnostica', 'preditiva', 'prescritiva' ou 'geral' (revisão completa)."
        ),
    )
    nivel_rigor: str = Field(
        default="academico",
        description=(
            "Nível de rigor esperado: "
            "'academico' — padrão para publicação científica; "
            "'executivo' — relatório para gestores, menos técnico."
        ),
    )


class QualityReviewTool(BaseTool):
    name: str = "QualityReviewTool"
    description: str = (
        "Revisa a qualidade metodológica e científica de análises acadêmicas. "
        "Detecta problemas como generalizações indevidas, afirmações causais sem suporte, "
        "ausência de métricas de qualidade e vieses analíticos. "
        "Gera um relatório de revisão com pontos de atenção e recomendações de melhoria."
    )
    args_schema: Type[BaseModel] = QualityReviewToolInput

    def _run(
        self,
        conteudo_analise: str,
        tipo_analise: str = "geral",
        nivel_rigor: str = "academico",
    ) -> str:
        try:
            alertas = self._verificar_alertas(conteudo_analise)
            checklist = self._verificar_checklist(conteudo_analise, tipo_analise)
            pontuacao = self._calcular_pontuacao(alertas, checklist)
            return self._formatar_relatorio(alertas, checklist, pontuacao, tipo_analise, nivel_rigor)
        except Exception as e:
            return f"❌ ERRO na revisão de qualidade: {str(e)}"

    # ------------------------------------------------------------------
    # Verificações
    # ------------------------------------------------------------------

    def _verificar_alertas(self, texto: str) -> list:
        """Detecta padrões problemáticos no texto."""
        texto_lower = texto.lower()
        encontrados = []
        for padrao, mensagem in ALERTAS_METODOLOGICOS:
            if re.search(padrao, texto_lower):
                encontrados.append(mensagem)
        return encontrados

    def _verificar_checklist(self, texto: str, tipo_analise: str) -> dict:
        """Verifica presença de elementos metodológicos esperados."""
        texto_lower = texto.lower()
        tipos = [tipo_analise] if tipo_analise != "geral" else list(CHECKLIST_POR_TIPO.keys())

        resultados = {}
        for tipo in tipos:
            if tipo not in CHECKLIST_POR_TIPO:
                continue
            itens = {}
            for item in CHECKLIST_POR_TIPO[tipo]:
                # Heurística: verifica palavras-chave do item no texto
                palavras_chave = re.findall(r"\b\w{4,}\b", item.lower())
                presentes = sum(1 for p in palavras_chave if p in texto_lower)
                itens[item] = presentes >= max(1, len(palavras_chave) // 3)
            resultados[tipo] = itens
        return resultados

    def _calcular_pontuacao(self, alertas: list, checklist: dict) -> dict:
        """Calcula pontuação de qualidade (0-100)."""
        # Penalidades por alertas
        penalidade_alertas = min(len(alertas) * 8, 40)

        # Bônus por checklist cumprido
        total_itens = sum(len(v) for v in checklist.values())
        itens_ok = sum(sum(1 for ok in v.values() if ok) for v in checklist.values())
        bonus_checklist = round((itens_ok / max(total_itens, 1)) * 60)

        pontuacao = max(0, bonus_checklist - penalidade_alertas + 40)
        pontuacao = min(100, pontuacao)

        if pontuacao >= 80:
            nivel = "Excelente"
            cor = "verde"
        elif pontuacao >= 60:
            nivel = "Satisfatório"
            cor = "amarelo"
        elif pontuacao >= 40:
            nivel = "Necessita melhorias"
            cor = "laranja"
        else:
            nivel = "Revisão significativa necessária"
            cor = "vermelho"

        return {"pontuacao": pontuacao, "nivel": nivel, "cor": cor}

    # ------------------------------------------------------------------
    # Formatação do relatório
    # ------------------------------------------------------------------

    def _formatar_relatorio(
        self,
        alertas: list,
        checklist: dict,
        pontuacao: dict,
        tipo_analise: str,
        nivel_rigor: str,
    ) -> str:
        pct = pontuacao["pontuacao"]
        nivel = pontuacao["nivel"]

        linhas = [
            "## Revisão de Qualidade Científica\n",
            f"**Pontuação:** {pct}/100 — {nivel}",
            f"**Tipo de análise revisada:** {tipo_analise.capitalize()}",
            f"**Nível de rigor:** {nivel_rigor.capitalize()}\n",
        ]

        # Alertas metodológicos
        if alertas:
            linhas.append("### Pontos de Atenção Metodológica\n")
            for alerta in alertas:
                linhas.append(f"- ⚠️ {alerta}")
            linhas.append("")
        else:
            linhas.append("### Pontos de Atenção\n_Nenhum padrão problemático detectado._\n")

        # Checklist por tipo
        if checklist:
            linhas.append("### Checklist de Boas Práticas\n")
            for tipo, itens in checklist.items():
                linhas.append(f"**{tipo.capitalize()}:**")
                for item, ok in itens.items():
                    marca = "✅" if ok else "❌"
                    linhas.append(f"  {marca} {item}")
                linhas.append("")

        # Recomendações baseadas nos gaps
        recomendacoes = self._gerar_recomendacoes(alertas, checklist, nivel_rigor)
        if recomendacoes:
            linhas.append("### Recomendações de Melhoria\n")
            for rec in recomendacoes:
                linhas.append(f"- {rec}")

        # Parecer final
        linhas.append("\n### Parecer Final\n")
        if pct >= 80:
            linhas.append(
                "A análise apresenta boa qualidade metodológica e pode ser utilizada "
                "com confiança para embasar decisões acadêmicas."
            )
        elif pct >= 60:
            linhas.append(
                "A análise é satisfatória para uso executivo, mas recomenda-se atenção "
                "aos pontos levantados antes de utilização em publicações científicas."
            )
        else:
            linhas.append(
                "A análise requer revisão metodológica antes de ser utilizada como "
                "referência em publicações ou decisões estratégicas de alto impacto."
            )

        return "\n".join(linhas)

    def _gerar_recomendacoes(self, alertas: list, checklist: dict, nivel_rigor: str) -> list:
        recs = []
        itens_faltando = [
            item for itens in checklist.values()
            for item, ok in itens.items() if not ok
        ]
        if itens_faltando and nivel_rigor == "academico":
            recs.append(
                f"Complementar a análise com: {'; '.join(itens_faltando[:3])}."
            )
        if any("causal" in a.lower() for a in alertas):
            recs.append(
                "Substituir linguagem causal por correlacional: "
                "'X está associado a Y' em vez de 'X causa Y'."
            )
        if any("absoluta" in a.lower() for a in alertas):
            recs.append(
                "Qualificar afirmações absolutas com termos como 'na maioria dos casos', "
                "'tende a' ou 'em média'."
            )
        if any("p-valor" in a.lower() or "valor-p" in a.lower() for a in alertas):
            recs.append(
                "Complementar o p-valor com tamanho de efeito (Cohen's d, η², r) "
                "para uma interpretação completa da significância prática."
            )
        return recs
