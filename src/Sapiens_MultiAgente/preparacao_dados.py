"""
Validação e resumo dos arquivos de entrada, em Python, antes da crew.

Substitui as tasks "validacao_rigorosa_de_dados_e_pergunta" e
"processamento_de_dados_reais_validados", que gastavam duas chamadas de LLM
em verificações determinísticas (o arquivo existe? qual a extensão? quantas
linhas e colunas?). Sem dados válidos, a análise é interrompida antes de
qualquer chamada ao modelo.
"""
from pathlib import Path
from typing import Any, Iterable

from .tools.statistical_analysis_tool import StatisticalAnalysisTool

# .txt não entra como tabela: costuma ser documento narrativo (vai para a análise textual).
EXTENSOES_TABULARES = {".csv", ".xlsx", ".xls", ".json"}
# Mesmo conjunto aceito pelo upload (web/app.py) + JSON, aceito pela StatisticalAnalysisTool.
EXTENSOES_ACEITAS = EXTENSOES_TABULARES | {".pdf", ".docx", ".txt"}


class DadosNecessarios(ValueError):
    """Não há dados reais utilizáveis; a mensagem é exibida ao usuário como erro da análise."""


def normalizar_arquivos(arquivos: Any) -> list[str]:
    if not arquivos:
        return []
    if isinstance(arquivos, str):
        return [arquivos]
    if isinstance(arquivos, Iterable):
        return [str(a) for a in arquivos]
    return []


def validar_arquivos(arquivos: Any) -> list[str]:
    """Retorna os caminhos válidos; levanta DadosNecessarios se não houver nenhum utilizável.

    Arquivos inexistentes ou com extensão não aceita interrompem a análise: seguir
    com parte dos dados produziria um relatório incompleto sem que o usuário saiba.
    """
    caminhos = normalizar_arquivos(arquivos)
    if not caminhos:
        raise DadosNecessarios(
            "DADOS NECESSÁRIOS: nenhum arquivo foi enviado. Envie dados reais em CSV, Excel "
            "(.xlsx/.xls), JSON, PDF, DOCX ou TXT. O SAPIENS não gera dados fictícios."
        )
    problemas = []
    for caminho in caminhos:
        extensao = Path(caminho).suffix.lower()
        if extensao not in EXTENSOES_ACEITAS:
            problemas.append(f"{Path(caminho).name}: extensão '{extensao or '(nenhuma)'}' não aceita")
        elif not Path(caminho).is_file():
            problemas.append(f"{Path(caminho).name}: arquivo não encontrado")
    if problemas:
        raise DadosNecessarios(
            "DADOS NECESSÁRIOS: não foi possível usar todos os arquivos enviados — "
            + "; ".join(problemas)
            + ". Envie novamente arquivos CSV, Excel, JSON, PDF, DOCX ou TXT."
        )
    return caminhos


def _tamanho_legivel(caminho: Path) -> str:
    tamanho = caminho.stat().st_size
    if tamanho < 1024:
        return f"{tamanho} B"
    if tamanho < 1024 ** 2:
        return f"{tamanho / 1024:.1f} KB"
    return f"{tamanho / 1024 ** 2:.1f} MB"


def resumir_arquivos(caminhos: list[str]) -> str:
    """Lista cada arquivo com tipo, tamanho e, para tabelas, linhas × colunas."""
    tool = StatisticalAnalysisTool()
    linhas = []
    for caminho in caminhos:
        p = Path(caminho)
        extensao = p.suffix.lower()
        descricao = f"- {p.name} ({extensao.lstrip('.').upper()}, {_tamanho_legivel(p)})"
        if extensao in EXTENSOES_TABULARES:
            try:
                df = tool._carregar_arquivo(caminho)
                if isinstance(df, str):
                    descricao += f" — {df}"
                else:
                    descricao += f" — tabela com {len(df)} linhas e {len(df.columns)} colunas"
            except Exception as erro:  # noqa: BLE001 - o resumo não pode derrubar a análise
                descricao += f" — ❌ ERRO: não foi possível ler a tabela: {erro}"
        else:
            descricao += " — documento textual"
        linhas.append(descricao)
    return "Arquivos validados pelo SAPIENS:\n" + "\n".join(linhas)
