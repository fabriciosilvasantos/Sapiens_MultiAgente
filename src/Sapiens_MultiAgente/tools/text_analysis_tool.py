"""
Ferramenta de análise textual para documentos acadêmicos.

Realiza extração de palavras-chave, análise de frequência, identificação
de entidades (instituições, pessoas, datas) e resumo temático de textos.
"""

import re
import string
from collections import Counter
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


# Stopwords do português (conjunto básico)
STOPWORDS_PT = frozenset({
    "a", "o", "e", "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas",
    "um", "uma", "uns", "umas", "para", "por", "com", "que", "se", "é", "ao", "à",
    "os", "as", "ser", "ter", "foi", "são", "mais", "mas", "ou", "já", "não", "este",
    "esta", "esse", "essa", "isso", "aquele", "aquela", "como", "também", "seu", "sua",
    "seus", "suas", "ele", "ela", "eles", "elas", "eu", "nos", "nós", "sobre", "entre",
    "até", "após", "desde", "durante", "pela", "pelo", "pelos", "pelas", "num", "numa",
    "quando", "onde", "quem", "qual", "quais", "cada", "todo", "toda", "todos", "todas",
    "assim", "então", "porque", "quando", "muito", "pouco", "bem", "ainda", "apenas",
    "mesmo", "tanto", "quanto", "além", "através", "entre", "contra", "dentro", "fora",
    "antes", "depois", "sendo", "tendo", "sendo", "fazer", "feito", "entre", "pode",
    "podem", "deve", "devem", "há", "houve", "havia", "será", "foram", "eram",
})

# Padrões para identificação de entidades
PADROES_ENTIDADES = {
    "instituicoes": re.compile(
        r"\b(UENF|UFRJ|USP|UNICAMP|UFMG|UFF|UERJ|IFF|CEFET|IFES|INEP|CAPES|MEC|CNPq|FAPESP|"
        r"universidade|faculdade|instituto|centro|escola|campus)\b",
        re.IGNORECASE,
    ),
    "anos": re.compile(r"\b(19|20)\d{2}\b"),
    "semestres": re.compile(r"\b\d{4}/[12]\b"),
    "percentuais": re.compile(r"\b\d+(?:[.,]\d+)?\s*%"),
    "cursos": re.compile(
        r"\b(graduação|pós-graduação|mestrado|doutorado|especialização|licenciatura|"
        r"bacharelado|tecnólogo|stricto sensu|lato sensu)\b",
        re.IGNORECASE,
    ),
    "indicadores_academicos": re.compile(
        r"\b(evasão|retenção|reprovação|aprovação|matrícula|ingresso|egresso|concluinte|"
        r"desempenho|nota|média|coeficiente|ira|cr|enade|ideb)\b",
        re.IGNORECASE,
    ),
}


class TextAnalysisToolInput(BaseModel):
    """Input schema para TextAnalysisTool."""

    texto: str = Field(
        ...,
        description="Texto a ser analisado (conteúdo de documento acadêmico, relatório ou narrativa).",
    )
    tipo_analise: str = Field(
        default="completa",
        description=(
            "Tipo de análise: "
            "'palavras_chave' — top palavras mais frequentes; "
            "'entidades' — extrai instituições, datas, indicadores; "
            "'temas' — identifica temas acadêmicos principais; "
            "'completa' — todas as análises combinadas."
        ),
    )
    top_n: int = Field(
        default=15,
        description="Número de palavras-chave ou entidades a retornar (padrão: 15).",
    )


class TextAnalysisTool(BaseTool):
    name: str = "TextAnalysisTool"
    description: str = (
        "Analisa o conteúdo textual de documentos acadêmicos. Extrai palavras-chave, "
        "identifica entidades (instituições, datas, indicadores acadêmicos), detecta "
        "temas principais e resume o conteúdo qualitativo de relatórios, atas, "
        "avaliações e textos narrativos."
    )
    args_schema: Type[BaseModel] = TextAnalysisToolInput

    def _run(self, texto: str, tipo_analise: str = "completa", top_n: int = 15) -> str:
        try:
            if not texto or len(texto.strip()) < 50:
                return "❌ ERRO: Texto muito curto para análise (mínimo 50 caracteres)."

            if tipo_analise == "palavras_chave":
                return self._analisar_palavras_chave(texto, top_n)
            elif tipo_analise == "entidades":
                return self._extrair_entidades(texto)
            elif tipo_analise == "temas":
                return self._identificar_temas(texto)
            else:
                return self._analise_completa(texto, top_n)

        except Exception as e:
            return f"❌ ERRO na análise textual: {str(e)}"

    # ------------------------------------------------------------------
    # Análises
    # ------------------------------------------------------------------

    def _analisar_palavras_chave(self, texto: str, top_n: int) -> str:
        tokens = self._tokenizar(texto)
        tokens_filtrados = [t for t in tokens if t not in STOPWORDS_PT and len(t) > 3]
        frequencias = Counter(tokens_filtrados)
        top = frequencias.most_common(top_n)

        if not top:
            return "Nenhuma palavra-chave significativa encontrada no texto."

        total = sum(frequencias.values())
        linhas = [
            f"## Palavras-Chave — Top {top_n}\n",
            "| # | Palavra | Frequência | % do texto |",
            "|---|---------|-----------|------------|",
        ]
        for i, (palavra, freq) in enumerate(top, 1):
            pct = round(freq / total * 100, 1)
            linhas.append(f"| {i} | **{palavra}** | {freq} | {pct}% |")

        linhas.append(f"\n_Total de tokens analisados: {total}_")
        return "\n".join(linhas)

    def _extrair_entidades(self, texto: str) -> str:
        linhas = ["## Entidades Identificadas no Texto\n"]

        for categoria, padrao in PADROES_ENTIDADES.items():
            matches = padrao.findall(texto)
            if matches:
                contagem = Counter(m if isinstance(m, str) else m[0] for m in matches)
                label = categoria.replace("_", " ").capitalize()
                linhas.append(f"### {label}")
                for entidade, freq in contagem.most_common(10):
                    linhas.append(f"- **{entidade}** ({freq}x)")
                linhas.append("")

        if len(linhas) == 1:
            linhas.append("_Nenhuma entidade acadêmica identificada no texto._")

        return "\n".join(linhas)

    def _identificar_temas(self, texto: str) -> str:
        texto_lower = texto.lower()

        temas_academicos = {
            "Evasão e Retenção": ["evasão", "evasao", "retenção", "retencao", "abandono", "desistência"],
            "Desempenho Acadêmico": ["nota", "média", "desempenho", "reprovação", "aprovação", "rendimento"],
            "Gestão Institucional": ["gestão", "planejamento", "orçamento", "administração", "pró-reitoria"],
            "Pós-Graduação": ["mestrado", "doutorado", "pós-graduação", "stricto", "dissertação", "tese"],
            "Pesquisa Científica": ["pesquisa", "publicação", "artigo", "produção", "cnpq", "capes"],
            "Extensão Universitária": ["extensão", "comunidade", "projeto", "programa"],
            "Infraestrutura": ["laboratório", "biblioteca", "infraestrutura", "instalações"],
            "Corpo Docente": ["docente", "professor", "qualificação", "doutorado", "dedicação"],
            "Inclusão e Diversidade": ["inclusão", "diversidade", "cotas", "bolsa", "auxílio"],
            "Internacionalização": ["internacional", "mobilidade", "intercâmbio", "estrangeiro"],
        }

        temas_encontrados = {}
        for tema, palavras in temas_academicos.items():
            ocorrencias = sum(texto_lower.count(p) for p in palavras)
            if ocorrencias > 0:
                temas_encontrados[tema] = ocorrencias

        if not temas_encontrados:
            return "## Temas\n_Nenhum tema acadêmico predominante identificado no texto._"

        temas_ordenados = sorted(temas_encontrados.items(), key=lambda x: x[1], reverse=True)

        linhas = [
            "## Temas Acadêmicos Identificados\n",
            "| Tema | Relevância | Indicador |",
            "|------|-----------|-----------|",
        ]
        max_ocorr = temas_ordenados[0][1] if temas_ordenados else 1
        for tema, ocorr in temas_ordenados:
            barra = "█" * min(int(ocorr / max_ocorr * 10), 10)
            linhas.append(f"| {tema} | {barra} | {ocorr} ocorrências |")

        linhas.append(
            f"\n**Tema principal:** {temas_ordenados[0][0]}\n"
            f"**Foco secundário:** {temas_ordenados[1][0] if len(temas_ordenados) > 1 else 'N/A'}"
        )
        return "\n".join(linhas)

    def _analise_completa(self, texto: str, top_n: int) -> str:
        stats = self._estatisticas_basicas(texto)
        palavras = self._analisar_palavras_chave(texto, top_n)
        entidades = self._extrair_entidades(texto)
        temas = self._identificar_temas(texto)

        return (
            f"## Análise Textual Completa\n\n"
            f"{stats}\n\n---\n\n"
            f"{palavras}\n\n---\n\n"
            f"{entidades}\n\n---\n\n"
            f"{temas}"
        )

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------

    def _tokenizar(self, texto: str) -> list:
        texto_limpo = texto.lower()
        texto_limpo = re.sub(r"https?://\S+", " ", texto_limpo)
        texto_limpo = texto_limpo.translate(str.maketrans("", "", string.punctuation + "«»""''"))
        return texto_limpo.split()

    def _estatisticas_basicas(self, texto: str) -> str:
        palavras = texto.split()
        frases = re.split(r"[.!?]+", texto)
        paragrafos = [p for p in texto.split("\n\n") if p.strip()]
        chars = len(texto)

        return (
            f"### Estatísticas do Texto\n"
            f"| Métrica | Valor |\n"
            f"|---------|-------|\n"
            f"| Palavras | {len(palavras)} |\n"
            f"| Frases | {len([f for f in frases if f.strip()])} |\n"
            f"| Parágrafos | {len(paragrafos)} |\n"
            f"| Caracteres | {chars} |\n"
            f"| Média palavras/frase | "
            f"{round(len(palavras) / max(len([f for f in frases if f.strip()]), 1), 1)} |"
        )
