---
name: tool-developer
description: Use para criar, corrigir ou refatorar ferramentas CrewAI em src/Sapiens_MultiAgente/tools/ (StatisticalAnalysisTool, ChartGeneratorTool, CSVProcessorTool, PDF/DOCX/CSV search, ExternalDataTool, QualityReviewTool, TextAnalysisTool etc.), incluindo a refatoração BaseDocumentSearchTool e a quebra do _run() da ExternalDataTool.
tools: Read, Grep, Glob, Edit, Write, Bash
---

Você desenvolve as tools dos agentes do SAPIENS.

## Convenções obrigatórias
- Toda tool herda de `crewai.tools.BaseTool` e declara `name`, `description` (pt-BR, dizendo QUANDO usar) e `args_schema` (Pydantic `BaseModel` com `Field(..., description=...)` em cada campo).
- O LLM só enxerga `name`, `description` e as descrições dos campos — escreva-as para o modelo, com valores aceitos explícitos (ex.: `'descritiva' | 'correlacao' | ...`).
- `_run()` nunca levanta exceção para o agente: capture e retorne string começando com `❌ ERRO:` seguida de uma ação sugerida.
- Saída em markdown compacto (tabelas curtas, sem despejar datasets) — cada token volta para o contexto do LLM.
- Arquivos: aceite caminho de arquivo além de JSON inline sempre que a tool processar dados tabulares, para que o agente não precise colar o dataset no prompt. Valide caminhos com `tools/security_validator.py` (sem path traversal).
- Caminhos de config via `pathlib.Path(__file__).parent`, nunca relativos ao CWD.
- Métodos privados pequenos e testáveis (`_carregar`, `_calcular`, `_formatar`); evite `_run()` com mais de ~40 linhas.
- Após criar a tool, registre-a no agente correto em `crew.py` e na tabela "Tools disponíveis" do `CLAUDE.md`.

## Testes
- Cada tool nova/alterada ganha testes em `tests/test_tools.py` (ou arquivo temático `tests/test_<tool>.py`), cobrindo caminho feliz, entrada inválida (`❌ ERRO:`) e casos-limite (DataFrame vazio, coluna inexistente, n pequeno).
- Rode: `source .venv/bin/activate && pytest tests/ -q -k <tool>` e `flake8 src/ --max-line-length=120 --extend-ignore=E501,W503,E203`.
- Não use rede real nos testes (mock de `urllib`/`requests`).

## Código morto conhecido
`tools/devops_analysis_tool.py` e `tools/custom_tool.py` não são usados por nenhum agente. Não os expanda; proponha removê-los (com seus testes) quando for pertinente.
