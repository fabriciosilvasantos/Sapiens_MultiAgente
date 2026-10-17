"""
Estatísticas calculadas em Python antes da crew.

Descritiva e correlação são cálculos determinísticos: não precisam de um agente
decidindo quando chamar a StatisticalAnalysisTool. Calculá-las uma vez, antes do
kickoff, e entregar o resultado pronto nas tasks economiza chamadas ao LLM e dá
aos agentes números de referência que eles não precisam (nem podem) inventar.
"""
from pathlib import Path
from typing import Any, Iterable

from .tools.statistical_analysis_tool import StatisticalAnalysisTool

# .txt fica de fora: costuma ser documento narrativo (vai para a análise textual).
EXTENSOES_PRE_CALCULO = {".csv", ".xlsx", ".xls", ".json"}

# Teto por arquivo para não estourar o contexto dos modelos gratuitos.
MAX_CARACTERES_POR_ARQUIVO = 8000

SEM_DADOS_TABULARES = (
    "Nenhum arquivo tabular (CSV, Excel, JSON) foi enviado; não há estatísticas pré-calculadas."
)


def _normalizar(arquivos: Any) -> list[str]:
    if not arquivos:
        return []
    if isinstance(arquivos, str):
        return [arquivos]
    if isinstance(arquivos, Iterable):
        return [str(a) for a in arquivos]
    return []


def _visao_geral(tool: StatisticalAnalysisTool, caminho: str) -> str:
    df = tool._carregar_arquivo(caminho)
    if isinstance(df, str):  # mensagem "❌ ERRO: ..."
        return df
    nulos = df.isna().sum()
    nulos = nulos[nulos > 0]
    linhas = [f"Linhas: {len(df)} | Colunas: {len(df.columns)}"]
    linhas.append("Colunas: " + ", ".join(f"{c} ({df[c].dtype})" for c in df.columns))
    if nulos.empty:
        linhas.append("Valores ausentes: nenhum")
    else:
        linhas.append("Valores ausentes: " + ", ".join(f"{c}={n}" for c, n in nulos.items()))
    return "\n".join(linhas)


def _estatisticas_do_arquivo(tool: StatisticalAnalysisTool, caminho: str) -> str:
    partes = [
        _visao_geral(tool, caminho),
        tool._run(file_path=caminho, analysis_type="descritiva"),
        tool._run(file_path=caminho, analysis_type="correlacao"),
    ]
    texto = "\n\n".join(p.strip() for p in partes if p)
    if len(texto) > MAX_CARACTERES_POR_ARQUIVO:
        texto = texto[:MAX_CARACTERES_POR_ARQUIVO] + "\n… (truncado; use StatisticalAnalysisTool para o restante)"
    return texto


def calcular_estatisticas_previas(arquivos: Any) -> str:
    """Retorna, em texto, visão geral + descritiva + correlação de cada arquivo tabular.

    Nunca levanta exceção: falhas por arquivo viram "❌ ERRO: ..." no próprio texto,
    para que a crew siga e os agentes vejam o problema.
    """
    tabulares = [a for a in _normalizar(arquivos) if Path(a).suffix.lower() in EXTENSOES_PRE_CALCULO]
    if not tabulares:
        return SEM_DADOS_TABULARES

    tool = StatisticalAnalysisTool()
    blocos = []
    for caminho in tabulares:
        try:
            conteudo = _estatisticas_do_arquivo(tool, caminho)
        except Exception as erro:  # noqa: BLE001 - um arquivo ruim não pode derrubar a análise
            conteudo = f"❌ ERRO: não foi possível calcular estatísticas: {erro}"
        blocos.append(f"### Arquivo: {Path(caminho).name}\n{conteudo}")
    return "\n\n".join(blocos)
