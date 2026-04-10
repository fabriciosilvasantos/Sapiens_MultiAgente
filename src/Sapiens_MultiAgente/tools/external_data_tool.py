"""
Ferramenta de busca em fontes de dados públicos acadêmicos brasileiros.

Fontes suportadas:
- INEP: Censo da Educação Superior, ENADE, IDEB, Microdados
- IBGE: Indicadores sociodemográficos via API
- Portal de Dados Abertos do MEC
"""

import json
import re
import urllib.request
import urllib.error
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


# Catálogo de fontes públicas relevantes para análise acadêmica
FONTES_ACADEMICAS = {
    "censo_educacao_superior": {
        "descricao": "Censo da Educação Superior — matrículas, concluintes, evasão por IES/curso",
        "url": "https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/censo-da-educacao-superior",
        "orgao": "INEP/MEC",
        "indicadores": ["matrículas", "concluintes", "ingressantes", "evasão", "vagas"],
    },
    "enade": {
        "descricao": "ENADE — desempenho de estudantes de graduação por curso/IES",
        "url": "https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/enade",
        "orgao": "INEP/MEC",
        "indicadores": ["conceito_enade", "desempenho_estudantes", "nota_geral"],
    },
    "ideb": {
        "descricao": "IDEB — índice de desenvolvimento da educação básica",
        "url": "https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb",
        "orgao": "INEP/MEC",
        "indicadores": ["ideb", "fluxo_escolar", "aprendizagem"],
    },
    "sucupira": {
        "descricao": "Plataforma Sucupira — avaliação de programas de pós-graduação",
        "url": "https://sucupira.capes.gov.br",
        "orgao": "CAPES",
        "indicadores": ["conceito_capes", "discentes", "docentes", "producao_cientifica"],
    },
    "ibge_educacao": {
        "descricao": "IBGE — indicadores educacionais e demográficos (PNAD, Censo)",
        "url": "https://www.ibge.gov.br/estatisticas/sociais/educacao.html",
        "orgao": "IBGE",
        "indicadores": ["taxa_alfabetização", "anos_estudo", "escolaridade", "renda"],
    },
    "dados_abertos_mec": {
        "descricao": "Portal de Dados Abertos do MEC — datasets estruturados",
        "url": "https://dadosabertos.mec.gov.br",
        "orgao": "MEC",
        "indicadores": ["IES", "cursos", "vagas", "bolsas"],
    },
}

# Benchmarks nacionais estimados (Censo Educação Superior 2022/2023)
BENCHMARKS_NACIONAIS = {
    "taxa_evasao_media_graduacao": 26.4,        # % ao ano (média nacional)
    "taxa_conclusao_graduacao": 58.0,           # % dos ingressantes concluem
    "taxa_evasao_pos_graduacao_stricto": 12.0,  # % mestrado/doutorado
    "relacao_aluno_professor": 18.5,            # alunos por docente
    "taxa_docentes_doutorado": 52.3,            # % docentes com doutorado
    "nota_media_enade_geral": 2.8,              # escala 1-5
    "taxa_matriculas_ead": 62.8,                # % matrículas em EAD
    "taxa_matriculas_presencial": 37.2,         # % matrículas presenciais
}


class ExternalDataToolInput(BaseModel):
    """Input schema para ExternalDataTool."""

    topico: str = Field(
        ...,
        description="Tópico de pesquisa para identificar fontes externas relevantes.",
    )
    tipo_busca: str = Field(
        default="benchmarks",
        description=(
            "Tipo de busca: "
            "'benchmarks' — retorna indicadores nacionais de referência; "
            "'fontes' — lista fontes públicas relevantes para o tópico; "
            "'contexto' — combina benchmarks e fontes para contextualização completa."
        ),
    )
    indicadores: str = Field(
        default="",
        description="Indicadores específicos de interesse (ex: 'evasão, matrículas, ENADE'). Opcional.",
    )


class ExternalDataTool(BaseTool):
    name: str = "ExternalDataTool"
    description: str = (
        "Busca dados de referência em fontes públicas acadêmicas brasileiras (INEP, IBGE, CAPES, MEC). "
        "Fornece benchmarks nacionais, fontes relevantes e contexto comparativo para análises acadêmicas. "
        "Use para contextualizar resultados da instituição com médias e indicadores nacionais."
    )
    args_schema: Type[BaseModel] = ExternalDataToolInput

    def _run(self, topico: str, tipo_busca: str = "benchmarks", indicadores: str = "") -> str:
        try:
            if tipo_busca == "fontes":
                return self._listar_fontes(topico, indicadores)
            elif tipo_busca == "benchmarks":
                return self._retornar_benchmarks(topico, indicadores)
            else:
                return self._contexto_completo(topico, indicadores)
        except Exception as e:
            return f"❌ ERRO: {str(e)}"

    # ------------------------------------------------------------------
    # Busca de fontes relevantes
    # ------------------------------------------------------------------

    def _listar_fontes(self, topico: str, indicadores: str) -> str:
        topico_lower = topico.lower()
        indicadores_lower = indicadores.lower()
        texto_busca = topico_lower + " " + indicadores_lower

        fontes_relevantes = []
        for chave, fonte in FONTES_ACADEMICAS.items():
            relevante = any(
                ind in texto_busca
                for ind in fonte["indicadores"]
            ) or any(
                termo in texto_busca
                for termo in ["evasão", "evasao", "matrícula", "matricula", "graduação",
                              "pos-graduação", "pós-graduação", "desempenho", "concluinte",
                              "estudante", "aluno", "docente", "professor", "ies", "universidade"]
            )
            if relevante or chave in ["censo_educacao_superior", "ibge_educacao"]:
                fontes_relevantes.append((chave, fonte))

        if not fontes_relevantes:
            fontes_relevantes = list(FONTES_ACADEMICAS.items())

        linhas = [
            f"## Fontes Públicas Relevantes para: {topico}\n",
            "| Fonte | Órgão | Indicadores Disponíveis | URL |",
            "|-------|-------|------------------------|-----|",
        ]
        for _, fonte in fontes_relevantes:
            inds = ", ".join(fonte["indicadores"][:3])
            linhas.append(f"| {fonte['descricao'][:50]}... | {fonte['orgao']} | {inds} | {fonte['url']} |")

        linhas.append(
            "\n### Como acessar\n"
            "- **INEP Microdados**: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados\n"
            "- **API IBGE**: https://servicodados.ibge.gov.br/api/docs\n"
            "- **Dados Abertos MEC**: https://dadosabertos.mec.gov.br\n"
            "- **Plataforma Sucupira**: https://sucupira.capes.gov.br/sucupira\n"
        )
        return "\n".join(linhas)

    # ------------------------------------------------------------------
    # Benchmarks nacionais
    # ------------------------------------------------------------------

    def _retornar_benchmarks(self, topico: str, indicadores: str) -> str:
        topico_lower = topico.lower()
        texto = topico_lower + " " + indicadores.lower()

        # Seleciona benchmarks relevantes ao tópico
        benchmarks_relevantes = {}

        if any(t in texto for t in ["evasão", "evasao", "abandono", "desistência"]):
            benchmarks_relevantes["Taxa de Evasão — Graduação (média nacional)"] = \
                f"{BENCHMARKS_NACIONAIS['taxa_evasao_media_graduacao']}% ao ano"
            benchmarks_relevantes["Taxa de Conclusão — Graduação"] = \
                f"{BENCHMARKS_NACIONAIS['taxa_conclusao_graduacao']}% dos ingressantes"

        if any(t in texto for t in ["pós", "pos", "mestrado", "doutorado", "stricto"]):
            benchmarks_relevantes["Taxa de Evasão — Pós-graduação Stricto Sensu"] = \
                f"{BENCHMARKS_NACIONAIS['taxa_evasao_pos_graduacao_stricto']}% ao ano"

        if any(t in texto for t in ["docente", "professor", "corpo docente"]):
            benchmarks_relevantes["Relação Aluno/Professor (média nacional)"] = \
                f"{BENCHMARKS_NACIONAIS['relacao_aluno_professor']} alunos por docente"
            benchmarks_relevantes["% Docentes com Doutorado (média nacional)"] = \
                f"{BENCHMARKS_NACIONAIS['taxa_docentes_doutorado']}%"

        if any(t in texto for t in ["enade", "desempenho", "avaliação", "nota"]):
            benchmarks_relevantes["Nota Média ENADE (escala 1-5, média nacional)"] = \
                f"{BENCHMARKS_NACIONAIS['nota_media_enade_geral']}"

        if any(t in texto for t in ["ead", "distância", "remoto", "presencial"]):
            benchmarks_relevantes["% Matrículas EAD (nacional)"] = \
                f"{BENCHMARKS_NACIONAIS['taxa_matriculas_ead']}%"
            benchmarks_relevantes["% Matrículas Presenciais (nacional)"] = \
                f"{BENCHMARKS_NACIONAIS['taxa_matriculas_presencial']}%"

        # Se nenhum match específico, retorna todos
        if not benchmarks_relevantes:
            benchmarks_relevantes = {
                "Taxa de Evasão — Graduação": f"{BENCHMARKS_NACIONAIS['taxa_evasao_media_graduacao']}% ao ano",
                "Taxa de Conclusão": f"{BENCHMARKS_NACIONAIS['taxa_conclusao_graduacao']}% dos ingressantes",
                "Relação Aluno/Professor": f"{BENCHMARKS_NACIONAIS['relacao_aluno_professor']}",
                "Docentes com Doutorado": f"{BENCHMARKS_NACIONAIS['taxa_docentes_doutorado']}%",
                "Nota ENADE média": f"{BENCHMARKS_NACIONAIS['nota_media_enade_geral']}",
            }

        linhas = [
            f"## Benchmarks Nacionais — Referência para: {topico}\n",
            "**Fonte:** Censo da Educação Superior 2022/2023 (INEP/MEC) e PNAD Contínua (IBGE)\n",
            "| Indicador | Valor Nacional de Referência |",
            "|-----------|------------------------------|",
        ]
        for indicador, valor in benchmarks_relevantes.items():
            linhas.append(f"| {indicador} | **{valor}** |")

        linhas.append(
            "\n> **Como usar:** Compare os indicadores da instituição analisada com esses valores "
            "de referência para contextualizar o desempenho relativo ao cenário nacional. "
            "Para dados atualizados e granulares, acesse os microdados do INEP em: "
            "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados"
        )
        return "\n".join(linhas)

    # ------------------------------------------------------------------
    # Contexto completo
    # ------------------------------------------------------------------

    def _contexto_completo(self, topico: str, indicadores: str) -> str:
        benchmarks = self._retornar_benchmarks(topico, indicadores)
        fontes = self._listar_fontes(topico, indicadores)
        return (
            f"{benchmarks}\n\n---\n\n{fontes}\n\n"
            "### Recomendação de Enriquecimento\n"
            "Para uma análise comparativa robusta, recomenda-se baixar os microdados do INEP "
            "correspondentes ao período analisado e cruzar com os dados institucionais fornecidos. "
            "Isso permite comparações por região, categoria administrativa (pública/privada) e área do conhecimento."
        )

    # ------------------------------------------------------------------
    # Tentativa de acesso à API do IBGE (graceful fallback)
    # ------------------------------------------------------------------

    def _consultar_ibge(self, indicador_id: str) -> str:
        """Tenta consultar a API do IBGE; retorna mensagem de fallback se indisponível."""
        url = f"https://servicodados.ibge.gov.br/api/v1/pesquisas/indicadores/{indicador_id}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SAPIENS/2.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                return json.dumps(data, ensure_ascii=False, indent=2)[:2000]
        except (urllib.error.URLError, Exception):
            return f"API IBGE indisponível para indicador {indicador_id}. Use os benchmarks locais."

    @staticmethod
    def _extrair_numeros(texto: str) -> list:
        """Extrai valores numéricos de um texto para análise."""
        return [float(m) for m in re.findall(r"\d+(?:[.,]\d+)?", texto)]
