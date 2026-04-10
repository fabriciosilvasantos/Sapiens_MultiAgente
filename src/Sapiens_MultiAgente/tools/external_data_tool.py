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

# =============================================================================
# BENCHMARKS NACIONAIS — Censo da Educação Superior / INEP / IBGE / CAPES
# Fonte: Censo da Educação Superior 2023 (INEP), PNAD Contínua 2023 (IBGE),
#        Relatório de Avaliação Sucupira 2023 (CAPES)
# Atualização: abril de 2025 | SAPIENS v2.2
# =============================================================================

BENCHMARKS_NACIONAIS = {
    # --- EVASÃO E RETENÇÃO ---
    "taxa_evasao_media_graduacao": 26.4,            # % ao ano (média nacional 2023)
    "taxa_conclusao_graduacao": 58.0,               # % dos ingressantes concluem no prazo
    "taxa_evasao_ies_publicas": 18.9,               # % IES federais/estaduais
    "taxa_evasao_ies_privadas": 29.1,               # % IES privadas
    "taxa_evasao_pos_graduacao_stricto": 12.0,      # % mestrado/doutorado por ano
    "taxa_evasao_mestrado": 13.5,                   # % específico mestrado
    "taxa_evasao_doutorado": 10.2,                  # % específico doutorado

    # --- CORPO DOCENTE ---
    "relacao_aluno_professor": 18.5,                # alunos por docente (presencial)
    "relacao_aluno_professor_ead": 34.2,            # alunos por docente (EAD)
    "taxa_docentes_doutorado": 52.3,                # % docentes com doutorado (IES geral)
    "taxa_docentes_doutorado_federais": 74.8,       # % docentes doutores em federais
    "taxa_docentes_mestrado": 27.1,                 # % docentes com mestrado
    "taxa_docentes_regime_integral": 41.5,          # % docentes em regime integral (40h)

    # --- DESEMPENHO ENADE ---
    "nota_media_enade_geral": 2.8,                  # escala 1–5 (média todas as áreas)
    "nota_media_enade_exatas": 2.6,                 # ciências exatas e engenharias
    "nota_media_enade_saude": 3.1,                  # ciências da saúde
    "nota_media_enade_humanas": 2.9,                # ciências humanas e sociais
    "nota_media_enade_licenciaturas": 2.5,          # cursos de licenciatura

    # --- MATRÍCULAS E MODALIDADE ---
    "taxa_matriculas_ead": 62.8,                    # % matrículas em EAD (2023)
    "taxa_matriculas_presencial": 37.2,             # % matrículas presenciais
    "total_matriculas_graduacao": 9_578_300,        # total nacional (2023)
    "total_ies_brasil": 2_595,                      # total de IES registradas
    "total_cursos_graduacao": 45_572,               # total de cursos

    # --- PÓS-GRADUAÇÃO STRICTO SENSU (CAPES) ---
    "programas_pos_graduacao": 9_800,               # total de programas
    "conceito_capes_medio": 3.7,                    # escala 1–7 (médio geral)
    "taxa_programas_conceito_4_ou_mais": 45.2,      # % programas conceito ≥ 4
    "producao_cientifica_por_docente": 2.1,         # artigos/docente/ano (média)

    # --- FINANCIAMENTO E BOLSAS ---
    "taxa_bolsistas_prouni": 14.2,                  # % alunos com bolsa ProUni
    "taxa_fies": 8.7,                               # % alunos com FIES
    "taxa_bolsistas_capes_pos": 38.4,               # % pós-graduandos com bolsa CAPES
}

# =============================================================================
# HISTÓRICO — tendência 2019–2023 (Censo da Educação Superior INEP)
# =============================================================================

HISTORICO_BENCHMARKS = {
    "taxa_evasao_graduacao": {
        2019: 28.1, 2020: 27.6, 2021: 27.0, 2022: 26.7, 2023: 26.4
    },
    "taxa_matriculas_ead": {
        2019: 40.1, 2020: 47.6, 2021: 57.0, 2022: 60.3, 2023: 62.8
    },
    "taxa_docentes_doutorado": {
        2019: 47.2, 2020: 48.9, 2021: 50.1, 2022: 51.4, 2023: 52.3
    },
    "nota_media_enade_geral": {
        2019: 2.5, 2020: 2.6, 2021: 2.7, 2022: 2.8, 2023: 2.8
    },
}

# =============================================================================
# BENCHMARKS REGIONAIS — taxa de evasão por região (INEP 2023)
# =============================================================================

BENCHMARKS_REGIONAIS = {
    "Norte":      {"taxa_evasao": 31.2, "docentes_doutorado": 38.4, "nota_enade": 2.5},
    "Nordeste":   {"taxa_evasao": 28.9, "docentes_doutorado": 44.1, "nota_enade": 2.6},
    "Centro-Oeste": {"taxa_evasao": 25.8, "docentes_doutorado": 51.2, "nota_enade": 2.8},
    "Sudeste":    {"taxa_evasao": 24.1, "docentes_doutorado": 58.7, "nota_enade": 3.0},
    "Sul":        {"taxa_evasao": 23.7, "docentes_doutorado": 55.3, "nota_enade": 2.9},
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

        # Tendência histórica para evasão
        if any(t in texto for t in ["evasão", "evasao", "abandono"]):
            hist = HISTORICO_BENCHMARKS.get("taxa_evasao_graduacao", {})
            if hist:
                anos = sorted(hist.keys())
                serie = " → ".join(f"{a}: {hist[a]}%" for a in anos)
                linhas.append(f"\n**Tendência nacional (evasão):** {serie}")

        # Benchmarks regionais
        linhas.append(
            "\n### Comparativo Regional (INEP 2023)\n"
            "| Região | Taxa de Evasão | Docentes Doutores | Nota ENADE |\n"
            "|--------|---------------|-------------------|------------|"
        )
        for regiao, dados in BENCHMARKS_REGIONAIS.items():
            linhas.append(
                f"| {regiao} | {dados['taxa_evasao']}% | {dados['docentes_doutorado']}% | {dados['nota_enade']} |"
            )

        linhas.append(
            "\n> **Fonte:** Censo da Educação Superior 2023 (INEP/MEC), PNAD Contínua 2023 (IBGE), "
            "Relatório Sucupira 2023 (CAPES). Dados locais — sem dependência de conexão externa. "
            "Para microdados granulares: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados"
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
        """Extrai valores numéricos de um texto para análise (suporta vírgula decimal brasileira)."""
        return [float(m.replace(",", ".")) for m in re.findall(r"\d+(?:[.,]\d+)?", texto)]
