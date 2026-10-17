# SAPIENS — Análise de Agentes e Subagentes

Gerado em: 2026-10-17

Este documento tem duas partes:

1. **Agentes do produto** (CrewAI) — avaliação de quais agentes da crew fazem sentido, problemas encontrados e mudanças recomendadas.
2. **Subagentes de desenvolvimento** (Claude Code, em `.claude/agents/`) — os "mods" criados para acelerar o desenvolvimento do projeto e o porquê de cada um.

---

## Parte 1 — Agentes CrewAI da plataforma

### Fluxo atual

```
validacao_rigorosa_de_dados_e_pergunta      (gerente)
  ↓
processamento_de_dados_reais_validados      (gerente)
  ↓
descritiva │ diagnóstica │ preditiva │ prescritiva │ fontes externas │ textual   (async, todas só com o resumo do processamento)
  ↓
revisar_qualidade_cientifica                (revisor)
  ↓
compilacao_e_apresentacao_do_relatorio_final (gerente)
```

### Veredito por agente

| Agente | Faz sentido? | Observação |
|---|---|---|
| `agente_gerente_orquestrador` | **Sim, mas mal nomeado** | O processo é `Process.sequential`; ele não gerencia nada — executa 3 tasks (validar, processar, compilar). Acumula papel de engenheiro de dados e de redator. |
| `especialista_em_analise_descritiva` | **Sim** | Núcleo da plataforma. Único com `ChartGeneratorTool`. |
| `especialista_em_analise_diagnostica` | **Sim** | Usa modelo de raciocínio (Nemotron 120B) — adequado. |
| `especialista_em_analise_preditiva` | **Sim, com ressalvas** | Não tem ferramenta de séries temporais; só regressão linear. Com séries anuais curtas (ex.: 2020–2025 = 6 pontos) as projeções têm pouca validade — a task deve exigir ressalva explícita. |
| `especialista_em_analise_prescritiva` | **Sim, mas posicionado errado** | Roda em paralelo e recebe apenas o resumo dos dados. Recomendação sem diagnóstico/previsão é opinião. Deve depender de descritiva + diagnóstica + preditiva + benchmarks. |
| `especialista_em_fontes_externas` | **Sim** | Benchmarks vêm de catálogo estático em `ExternalDataTool` (bom para reprodutibilidade); o `ScrapeWebsiteTool` abre superfície de prompt injection/SSRF. |
| `especialista_em_analise_textual` | **Sim, condicional** | Roda sempre, mesmo sem PDF/DOCX — desperdício de tokens e risco de alucinação. Deve virar `ConditionalTask`. |
| `revisor_de_qualidade_cientifica` | **Sim** | Diferencial acadêmico. Hoje só pontua; não há ciclo de correção. |

**Não recomendo adicionar novos agentes de produto agora.** O gargalo não é falta de especialistas, e sim o fluxo de dados entre eles (ver problemas abaixo). Mais agentes = mais chamadas a modelos gratuitos com limite de taxa e mais latência.

Também **não faz sentido** um agente "DevOps": `tools/devops_analysis_tool.py` e `tools/custom_tool.py` não são usados por nenhum agente (código morto mantido só pelos testes).

### Problemas encontrados (por prioridade)

> **Status (2026-10-17):** problemas 1 a 7 corrigidos — `{arquivos_analisados}` interpolado nas tasks, guardrail `validar_dados_disponiveis` (em `crew.py`, sem retentativas) na validação e prescritiva síncrona após as análises paralelas; `StatisticalAnalysisTool` aceita `file_path` (CSV/Excel/JSON); `agents.yaml` só com campos do `crewai.Agent` (`max_iter` no lugar de `max_iterations`); análise textual como `ConditionalTask`, só com PDF/DOCX/TXT; timeout cancela a crew (`cancelar()` + callbacks) e erros em tasks paralelas não travam mais o kickoff (`TaskParalela`).

1. ✅ **Crítico — os agentes não recebem os caminhos dos arquivos.** `web/app.py` envia `inputs={'topico_pesquisa', 'arquivos_analisados'}`, mas nenhum texto de `agents.yaml`/`tasks.yaml` usa `{arquivos_analisados}`. O CrewAI só interpola placeholders presentes no texto, então os agentes nunca sabem quais arquivos analisar. Correção: incluir `Arquivos disponíveis: {arquivos_analisados}` nas descriptions de `validacao_rigorosa_de_dados_e_pergunta` e `processamento_de_dados_reais_validados` (e nas tasks analíticas).
2. ✅ **Alto — `StatisticalAnalysisTool` exige o dataset inteiro como string JSON** (`data: str`). O LLM teria de colar os dados no argumento da tool, o que estoura contexto e convida à fabricação de números. Correção aplicada: parâmetro `file_path` (extensões tabulares, arquivo precisa existir; separador e encoding detectados), com precedência sobre `data`.
3. ✅ **Alto — a validação não interrompe a crew.** A task diz "SE não há dados: PARAR", mas em processo sequencial as demais tasks rodam do mesmo jeito. Correção: `guardrail` na task de validação (falha se a saída começar com `DADOS NECESSÁRIOS`) ou checar arquivos em `app.py` antes do `kickoff`.
4. ✅ **Médio — prescritiva em paralelo** (ver tabela). Correção: torná-la síncrona, após as async, com `context` = descritiva, diagnóstica, preditiva, benchmarks.
5. ✅ **Médio — chaves inválidas em `agents.yaml`.** `max_iterations`, `ferramentas`, `temperatura_modelo`, `timeout_minutos`, `seguranca`, `formato_saida` e os blocos globais `sistema/seguranca/performance` não são campos do `crewai.Agent` e são ignorados. Dão falsa impressão de configuração. Correção: usar `max_iter`, `max_execution_time`, `allow_delegation: false`; remover o resto (temperatura já vem de `llm_config.yaml`, tools de `crew.py`).
6. ✅ **Médio — análise textual incondicional** → `ConditionalTask` que só roda se houver `.pdf/.docx/.txt` em `arquivos_analisados`.
7. ✅ **Alto (era Baixo) — o timeout da crew não cancela a execução.** `future.cancel()` não interrompe uma thread já em execução, e o `with ThreadPoolExecutor` esperava a crew terminar antes de reportar o timeout. Além disso, no CrewAI 0.203 uma exceção numa task async nunca resolve o `Future`, e o `kickoff` travava para sempre (ex.: erro persistente do LLM numa análise paralela). Correção: `crew_instance.cancelar()` faz os callbacks levantarem `AnaliseCancelada` no próximo passo de cada agente; `executor.shutdown(wait=False)`; `TaskParalela` repassa exceções ao `Future`.
8. **Baixo — revisor sem ciclo de correção.** Opção futura: `guardrail` no relatório final exigindo pontuação mínima, ou task de "revisão das ressalvas" antes da compilação.

### Estatísticas pré-calculadas (2026-10-17)

Descritiva, correlação e visão geral do dataset (linhas, colunas, tipos, nulos) são
cálculos determinísticos. Agora são feitos uma vez em Python, num `@before_kickoff`
(`estatisticas_previas.py`), e entregues prontos nas tasks via `{estatisticas_previas}`.
Efeitos: menos chamadas de ferramenta pelos agentes, números de referência que o
revisor usa para detectar valores inventados, e nenhuma dependência do LLM para
decidir *se* calcula a estatística básica. A análise descritiva também passou a omitir
colunas quase únicas (nomes, matrículas) e a listar no máximo 15 categorias por coluna,
para não enviar dados pessoais de alunos ao LLM externo.

### Fluxo recomendado

```
validacao_rigorosa_de_dados_e_pergunta   (gerente, guardrail)
  ↓
processamento_de_dados_reais_validados   (gerente)
  ↓
executar_analise_textual                 (ConditionalTask: só com PDF/DOCX/TXT; não pode ser async)
  ↓
descritiva │ diagnóstica │ preditiva │ fontes externas   ← async
  ↓
executar_analise_prescritiva             (síncrona; context = todas acima)
  ↓
revisar_qualidade_cientifica
  ↓
compilacao_e_apresentacao_do_relatorio_final
```

Opcional (quando o relatório final crescer): separar um agente `redator_executivo` para a compilação, deixando o gerente só com validação/processamento — renomeando-o para `engenheiro_de_dados_academicos`.

---

## Parte 2 — Subagentes de desenvolvimento (Claude Code)

Arquivos em `.claude/agents/`. O Claude Code os aciona automaticamente pela `description`, ou explicitamente ("use o subagente test-engineer para ...").

| Subagente | Escreve código? | Quando usar |
|---|---|---|
| `crewai-architect` | Sim | agents.yaml, tasks.yaml, crew.py, llm_config — os problemas 1, 3–8 acima |
| `tool-developer` | Sim | Tools em `tools/` — problema 2, `BaseDocumentSearchTool`, refatorar `ExternalDataTool` |
| `test-engineer` | Sim | pytest, mocks de LLM, fixtures, consolidar `test_coverage_boost*` |
| `flask-web-developer` | Sim | `web/`, API v1, SSE, SQLite, uploads, templates |
| `security-auditor` | Não (leitura) | Uploads, SSRF, auth, LGPD/PII de alunos enviada ao LLM, segredos |
| `statistical-methods-reviewer` | Não (leitura) | Corretude estatística das tools, prompts analíticos e relatórios gerados |

### Por que estes seis

O código do SAPIENS se divide em quatro áreas com regras próprias (crew, tools, web, testes): um subagente que escreve código para cada uma. Dois revisores só de leitura cobrem riscos que um desenvolvedor tende a não ver no próprio código: segurança/LGPD (a plataforma recebe dados pessoais de alunos e os envia a LLMs externos) e rigor estatístico (proposta central do produto).

### Subagentes avaliados e descartados

- **Um subagente por agente CrewAI** (descritivo, diagnóstico...) — duplicaria a crew; a manutenção dos prompts cabe ao `crewai-architect`.
- **Frontend/UI designer** — são 9 templates Jinja simples; o `flask-web-developer` cobre.
- **DBA/SQLite** — uma tabela de análises e uma de usuários; não justifica um especialista.
- **DevOps/Docker/Vercel** — mudanças raras; CI já existe. Os comandos `/test-sapiens` e `/lint-sapiens` resolvem o dia a dia.
- **Code reviewer genérico** — o Claude Code já tem `/code-review` e `/security-review` nativos.

### Fluxos de uso sugeridos

- **Nova análise estatística**: `statistical-methods-reviewer` (desenho do método) → `tool-developer` (implementa) → `test-engineer` (testa) → `crewai-architect` (liga ao agente).
- **Corrigir o fluxo da crew**: `crewai-architect` → `test-engineer`.
- **Antes de deploy**: `security-auditor` + `/test-sapiens` + `/lint-sapiens`.
