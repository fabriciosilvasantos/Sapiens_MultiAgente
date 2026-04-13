# SAPIENS — Analise de Viabilidade MCP (Model Context Protocol)

Data: 2026-04-13

---

## O que e MCP

Protocolo padronizado que permite LLMs acessarem ferramentas externas via
servidores dedicados. Em vez de tools como classes Python acopladas ao agente,
as ferramentas rodam como servicos independentes que qualquer cliente MCP
pode consumir.

## Arquitetura atual vs. com MCP

```
ATUAL (CrewAI Tools acopladas)
CrewAI Agent
  -> LLM (OpenRouter/Groq)
       -> Tool._run()  <-- classe Python local
            -> pandas/scipy/matplotlib/pypdf (in-process)

COM MCP (Tools como servidores)
CrewAI Agent
  -> LLM (OpenRouter/Groq)
       -> MCP Client -> HTTP/stdio -> MCP Server
            -> Tool isolada (processo separado)
                 -> pandas/scipy/matplotlib/pypdf
```

---

## Candidatas a MCP

| Tool atual                  | Candidata? | Justificativa                                                        |
|-----------------------------|:----------:|----------------------------------------------------------------------|
| `StatisticalAnalysisTool`   | Sim        | Pesada (scipy/sklearn), servidor dedicado com mais RAM/CPU           |
| `ChartGeneratorTool`        | Sim        | Matplotlib consome memoria; servidor separado evita memory leaks     |
| `ExternalDataTool`          | Sim        | HTTP ao IBGE; MCP server com cache proprio, reutilizavel             |
| `PDFSearchTool`             | Talvez     | I/O-bound; MCP adicionaria latencia sem ganho claro                  |
| `DOCXSearchTool`            | Talvez     | Mesmo caso do PDF                                                    |
| `CSVProcessorTool`          | Talvez     | Pesado em datasets grandes, mas precisa acesso local ao filesystem   |
| `CSVSearchTool`             | Nao        | Leve, depende de DataFrame em memoria                                |
| `DataValidationTool`        | Nao        | Simples, acesso local ao filesystem                                  |
| `QualityReviewTool`         | Nao        | Logica pura (regex + scoring), sem I/O externo                       |
| `TextAnalysisTool`          | Nao        | NLP leve (tokenizacao, regex), sem dependencias pesadas              |
| `SecurityValidator`         | Nao        | Precisa acesso local ao arquivo para validar MIME/hash               |
| `AcademicLogger`            | Nao        | Logging local, nao e tool dos agentes                                |

---

## PROS

### 1. Isolamento de processos
Matplotlib, scipy e sklearn rodam em processo separado. Se crash ou memory
leak acontecer, nao derruba o Flask nem o CrewAI. Hoje chart_generator_tool.py
usa matplotlib.use('Agg') dentro do mesmo processo Flask.

### 2. Reutilizacao entre projetos
Um MCP server de "Analise Estatistica" ou "Dados INEP/IBGE" poderia ser usado
por outros projetos academicos. O ExternalDataTool com benchmarks nacionais
hardcoded (INEP 2023, IBGE PNAD, CAPES) e bom candidato a servico compartilhado.

### 3. Escalabilidade independente
Se a analise estatistica for o gargalo, escala so o MCP server de estatistica
sem escalar o Flask inteiro.

### 4. Versionamento independente
Atualizar scipy ou matplotlib nao exige redeploy do SAPIENS inteiro — so do
MCP server correspondente.

### 5. Testabilidade
MCP servers podem ser testados isoladamente com qualquer cliente MCP, sem
precisar instanciar o CrewAI.

---

## CONTRAS

### 1. Complexidade operacional significativa
Hoje: pip install e pronto. Com MCP: N processos/servicos para gerenciar,
monitorar e lidar com falhas de comunicacao. Para ~5.400 linhas com 1-3
usuarios simultaneos, e overengineering.

### 2. Latencia adicional
Cada chamada de tool passa por serializacao JSON -> transporte -> deserializacao.
Estimativa: ~5-20ms por chamada MCP vs. ~0.1ms Python direto. Em 50+ invocacoes
por analise, adiciona 0.5-1s.

### 3. Transferencia de dados
- CSVProcessorTool retorna DataFrames de ate 100K linhas. Serializar via JSON/MCP
  e muito mais lento que acesso em memoria.
- ChartGeneratorTool retorna imagens base64 (~200KB+). Overhead desnecessario local.
- PDFSearchTool/DOCXSearchTool precisam acesso ao filesystem dos uploads.

### 4. CrewAI nao suporta MCP nativamente
Seria necessario criar wrapper BaseTool -> MCP Client para cada tool.
Camada de indirecao sem ganho funcional.

### 5. Debugging mais dificil
Erro no servidor MCP -> serializado -> retornado ao cliente -> re-raised.
Perda de contexto no stack trace.

### 6. Deploy mais complexo
SAPIENS tem Dockerfile e Vercel deploy (api/index.py). MCP servers requerem
orquestracao (docker-compose). Na Vercel (serverless), MCP nao faz sentido.

---

## Analise custo-beneficio por cenario

| Cenario                                          | MCP vale? | Motivo                                                       |
|--------------------------------------------------|:---------:|--------------------------------------------------------------|
| SAPIENS como esta (1-3 usuarios, deploy local)   | Nao       | Complexidade nao justifica. Tools locais funcionam bem.      |
| SAPIENS multi-tenant (10+ usuarios simultaneos)  | Talvez    | Isolar StatisticalAnalysis e ChartGenerator em workers ajuda |
| SAPIENS como plataforma (tools reutilizaveis)    | Sim       | ExternalDataTool e StatisticalAnalysis como MCP servers      |
| Migracao para outro framework (nao CrewAI)       | Sim       | MCP servers sao framework-agnostic                           |

---

## Recomendacao

**Nao adotar MCP agora.** O SAPIENS e compacto (~5.400 linhas) com tools leves
que rodam bem in-process. Overhead de complexidade operacional, latencia e
wrapper CrewAI->MCP nao compensa para o uso atual.

### Alternativas sem MCP (mesmo beneficio)
1. Isolar matplotlib em subprocess para evitar memory leaks
2. Adicionar cache no ExternalDataTool para chamadas IBGE
3. Mover para Process.hierarchical no CrewAI para paralelizar os 6 agentes

### Quando reconsiderar MCP
- SAPIENS virar plataforma multi-tenant
- Outras aplicacoes precisarem das mesmas tools (INEP/IBGE, estatistica)
- Migracao para framework com suporte MCP nativo

---

## Pontos de atencao identificados durante a analise

### Gargalos atuais (independente de MCP)
1. **Execucao sequencial**: Process.sequential no crew.py apesar de async_execution=True
2. **Polling SSE**: time.sleep(1) no event_generator — nao e event-driven
3. **SQLite sync**: cada update de status faz INSERT/UPDATE em disco
4. **Sem recuperacao parcial**: 1 agente falhando marca toda analise como erro
5. **Sem cache de analises**: mesmo topico + mesmos dados = LLM calls duplicadas
6. **Sem tracking de tokens**: impossivel medir custo por analise

### Vulnerabilidades
1. File path injection: caminhos de upload passados direto para tools sem sanitizacao
2. Matplotlib memory leaks em servidor de longa duracao
3. IBGE API sincrona com timeout de 5s bloqueando agent thread
