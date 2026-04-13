# SAPIENS — Documentação de Uso

> Plataforma Acadêmica Multiagente de Análise de Dados  
> Versão 2.1.0 · Atualizado em Abril de 2026

---

## Sumário

1. [O que é o SAPIENS](#1-o-que-é-o-sapiens)
2. [Fluxo Geral de Funcionamento](#2-fluxo-geral-de-funcionamento)
3. [Os 5 Agentes Especializados](#3-os-5-agentes-especializados)
4. [Os 4 Tipos de Análise](#4-os-4-tipos-de-análise)
5. [Como Usar — Interface Web](#5-como-usar--interface-web)
6. [Como Usar — API REST](#6-como-usar--api-rest)
7. [Como Usar — CLI](#7-como-usar--cli)
8. [Tipos de Arquivo Suportados](#8-tipos-de-arquivo-suportados)
9. [Exemplos Práticos Completos](#9-exemplos-práticos-completos)
10. [Interpretando os Resultados](#10-interpretando-os-resultados)
11. [Segurança e Limites](#11-segurança-e-limites)
12. [Referência da API](#12-referência-da-api)
13. [Resolução de Problemas](#13-resolução-de-problemas)

---

## 1. O que é o SAPIENS

O **SAPIENS** é uma plataforma que utiliza uma equipe de agentes de inteligência artificial para conduzir análises de dados acadêmicos de forma automatizada. Em vez de um único modelo de IA respondendo a uma pergunta, o SAPIENS orquestra **5 agentes especializados** que trabalham em paralelo para produzir um relatório completo com quatro dimensões analíticas.

**Quando usar o SAPIENS?**

- Você tem dados de desempenho de alunos e quer entender o que está acontecendo
- Precisa identificar por que as taxas de evasão aumentaram
- Quer projetar tendências para o próximo semestre ou ano
- Precisa de recomendações baseadas em dados para tomar decisões estratégicas

**O que o SAPIENS entrega?**

Um relatório único em Markdown ou PDF contendo:
- Resumo estatístico dos dados (análise descritiva)
- Causas e correlações encontradas (análise diagnóstica)
- Projeções e tendências futuras (análise preditiva)
- Recomendações acionáveis (análise prescritiva)

---

## 2. Fluxo Geral de Funcionamento

```
Usuário
  │
  ├── Fornece: tópico de pesquisa + arquivos de dados (CSV/Excel/PDF/DOCX)
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SAPIENS Web Interface                        │
│  1. Autentica o usuário                                         │
│  2. Valida os arquivos enviados (tipo, tamanho, segurança)      │
│  3. Gera ID único para a análise                                │
│  4. Salva análise no banco SQLite                               │
│  5. Dispara a execução em thread separada (não bloqueia)        │
└─────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│                       CrewAI Engine                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Fase 1 — Gerente Orquestrador                          │   │
│  │  • Valida se existem dados reais                        │   │
│  │  • Extrai e limpa os dados                              │   │
│  │  • Rastreia a origem de cada informação                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│            ┌──────────────┼──────────────┐                     │
│            │              │              │                     │
│            ▼              ▼              ▼                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│  │  Descritiva  │ │ Diagnóstica  │ │  Preditiva   │           │
│  │  (paralelo)  │ │  (paralelo)  │ │  (paralelo)  │           │
│  └──────────────┘ └──────────────┘ └──────────────┘           │
│       + ┌──────────────┐                                        │
│         │ Prescritiva  │  ← todas executam ao mesmo tempo      │
│         │  (paralelo)  │                                        │
│         └──────────────┘                                        │
│                           │                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Fase Final — Gerente Orquestrador                      │   │
│  │  • Consolida todos os resultados                        │   │
│  │  • Gera relatório final estruturado                     │   │
│  │  • Inclui resumo executivo e recomendações              │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
  │
  ▼
Relatório Final disponível para download (PDF ou TXT)
```

### Progressão de Status

Durante a execução, a análise passa pelos seguintes estados:

| Status | Progresso | Descrição |
|--------|-----------|-----------|
| `processando` | 0% | Análise criada, aguardando início |
| `arquivos_validados` | 25% | Arquivos aceitos e prontos |
| `executando_analise` | 25% | Agentes iniciados |
| `processando_dados` | 50% | Dados sendo processados pelos agentes |
| `gerando_relatorio` | 90% | Relatório sendo compilado |
| `concluida` | 100% | Relatório disponível |
| `erro` | — | Falha durante a execução |

---

## 3. Os 5 Agentes Especializados

### Agente 1 — Gerente Orquestrador

**Função**: Ponto de entrada e saída de toda a análise. Valida os dados antes de distribuir o trabalho e consolida os resultados ao final.

**Comportamento crítico**: Se nenhum dado real for fornecido (sem arquivo, sem link), o Gerente **interrompe a análise** e solicita dados específicos. Ele nunca gera dados fictícios ou simulações sem avisar explicitamente.

**Ferramentas que usa**:
- `FileReadTool` — leitura de arquivos CSV, Excel, PDF, DOCX
- `ScrapeWebsiteTool` — acesso a sites e links fornecidos
- `DataValidationTool` — verificação de integridade e tipo dos dados
- `CSVProcessorTool` — extração de estatísticas básicas de CSV

---

### Agente 2 — Especialista em Análise Descritiva

**Função**: Responde "O que aconteceu?". Produz o retrato atual dos dados.

**O que entrega**:
- Médias, medianas, desvios padrão
- Distribuições e frequências
- Tendências ao longo do tempo
- Identificação de outliers
- Tabelas e gráficos descritivos

**Ferramentas que usa**:
- `StatisticalAnalysisTool` — estatísticas descritivas, testes de normalidade (Shapiro-Wilk)
- `ChartGeneratorTool` — histogramas, gráficos de barras, boxplots, mapas de calor
- `FileReadTool` — acesso aos dados originais

---

### Agente 3 — Especialista em Análise Diagnóstica

**Função**: Responde "Por que aconteceu?". Identifica causas e correlações.

**O que entrega**:
- Matrizes de correlação (coeficiente de Pearson)
- Testes de hipóteses (teste T, ANOVA)
- Análise de significância estatística (p-valor ≤ 0,05)
- Identificação de variáveis preditoras
- Comparação entre grupos

**Ferramentas que usa**:
- `StatisticalAnalysisTool` — correlação, regressão, ANOVA, testes T
- `CSVProcessorTool`, `PDFSearchTool`, `DOCXSearchTool` — leitura de dados

---

### Agente 4 — Especialista em Análise Preditiva

**Função**: Responde "O que pode acontecer?". Projeta o futuro com base nos padrões encontrados.

**O que entrega**:
- Modelos de regressão linear e tendências
- Séries temporais e projeções
- Intervalos de confiança
- Estimativas de probabilidade
- Cenários (otimista, realista, pessimista)

**Ferramentas que usa**:
- `StatisticalAnalysisTool` — regressão, séries temporais
- `CSVProcessorTool` — acesso aos dados históricos

---

### Agente 5 — Especialista em Análise Prescritiva

**Função**: Responde "O que devemos fazer?". Traduz os dados em ação.

**O que entrega**:
- Recomendações priorizadas por impacto
- Estratégias de intervenção com passos concretos
- Análise de cenários e riscos
- Critérios de sucesso mensuráveis
- Plano de implementação sugerido

**Ferramentas que usa**:
- `StatisticalAnalysisTool`, `CSVProcessorTool`, `CSVSearchTool`

---

## 4. Os 4 Tipos de Análise

### Análise Descritiva — "O que aconteceu?"

Produz um retrato estatístico dos dados. É sempre o primeiro passo e serve de base para todas as outras análises.

**Exemplo de tópico**: *"Distribuição de notas dos alunos de Engenharia no semestre 2025/1"*

**O que esperar no relatório**:
```
## Análise Descritiva

### Estatísticas Gerais
- Total de alunos: 342
- Média geral: 6,8 (±1,4)
- Mediana: 7,0
- Taxa de reprovação: 18,4%

### Distribuição por Disciplina
| Disciplina     | Média | Desvio Padrão | Reprovação |
|----------------|-------|---------------|------------|
| Cálculo I      | 5,9   | 1,8           | 31%        |
| Programação I  | 7,4   | 1,2           | 12%        |
| Física I       | 6,2   | 1,6           | 24%        |

### Observações
- Outliers detectados: 14 alunos com nota < 2,0
- Distribuição não normal (p=0.003, teste Shapiro-Wilk)
```

---

### Análise Diagnóstica — "Por que aconteceu?"

Explica os padrões encontrados na fase descritiva. Busca relações causais e correlações entre variáveis.

**Exemplo de tópico**: *"Por que a taxa de reprovação em Cálculo I é o dobro da média?"*

**O que esperar no relatório**:
```
## Análise Diagnóstica

### Correlações Identificadas (Pearson)
- Frequência × Nota final: r = 0,78 (forte positiva, p < 0,001)
- Horas de estudo × Nota final: r = 0,61 (moderada positiva, p < 0,001)
- Nota no EM × Nota em Cálculo I: r = 0,54 (moderada, p < 0,001)

### Comparação entre Grupos (ANOVA)
- Alunos com frequência > 75%: média 7,6
- Alunos com frequência < 75%: média 4,2
- Diferença estatisticamente significativa (F=48.3, p < 0,001)

### Fatores de Risco Identificados
1. Frequência abaixo de 75% (risco 3,4x maior de reprovação)
2. Nota < 6,0 na primeira prova (risco 2,8x maior)
3. Sem monitoria: risco 1,9x maior de reprovação
```

---

### Análise Preditiva — "O que pode acontecer?"

Projeta tendências e comportamentos futuros com base nos padrões históricos.

**Exemplo de tópico**: *"Qual será a taxa de evasão no próximo ano letivo?"*

**O que esperar no relatório**:
```
## Análise Preditiva

### Modelo de Regressão (R² = 0,84)
Variáveis preditoras: frequência, nota_p1, nota_historico_ensino_medio

### Projeção — Próximo Semestre
| Cenário     | Taxa de Evasão | Intervalo de Confiança (95%) |
|-------------|----------------|------------------------------|
| Otimista    | 8,2%           | [6,1% — 10,3%]               |
| Realista    | 11,7%          | [9,4% — 14,0%]               |
| Pessimista  | 16,3%          | [13,1% — 19,5%]              |

### Alunos em Risco (próximo semestre)
- 47 alunos com probabilidade > 70% de evasão
- Concentração: 1º e 2º período
- Perfil de risco: frequência < 70% E nota_p1 < 5,0
```

---

### Análise Prescritiva — "O que devemos fazer?"

Transforma os dados em um plano de ação concreto e priorizado.

**Exemplo de tópico**: *"Quais intervenções implementar para reduzir a evasão?"*

**O que esperar no relatório**:
```
## Análise Prescritiva

### Recomendações Priorizadas

**[ALTA PRIORIDADE] Programa de Alerta Precoce**
- Ação: Identificar automaticamente alunos com frequência < 70% após 3ª semana
- Impacto esperado: Redução de 25–35% na evasão (IC 95%)
- Custo de implementação: Baixo (processo automatizável)
- Prazo sugerido: Implementar no início do próximo semestre

**[ALTA PRIORIDADE] Reforço em Cálculo I**
- Ação: Dobrar as sessões de monitoria (de 2x para 4x por semana)
- Impacto esperado: Redução de 15% na reprovação
- Evidência: alunos com monitoria têm nota média 1,8 pontos acima

**[MÉDIA PRIORIDADE] Revisão do Processo Seletivo**
- Ação: Incluir avaliação diagnóstica de Matemática na matrícula
- Impacto esperado: Melhor alinhamento de expectativas
- Prazo sugerido: Próximo processo seletivo

### Métricas de Sucesso Sugeridas
- Taxa de evasão < 10% no próximo semestre
- Taxa de reprovação em Cálculo I < 20%
- NPS dos alunos em risco ≥ 7,0
```

---

## 5. Como Usar — Interface Web

### Acesso e Login

1. Acesse `http://localhost:5000` (ou o endereço do servidor)
2. Entre com suas credenciais:
   - **Usuário padrão**: `admin`
   - **Senha padrão**: `sapiens@2025`
3. Você será redirecionado para a página inicial

---

### Iniciando uma Análise

Clique em **"Iniciar Análise"** na navbar ou na home page. Você verá um formulário com três seções:

**1. Tópico de Pesquisa** (obrigatório)

Descreva em linguagem natural o que você quer analisar. Seja específico — quanto mais contexto, melhor o relatório.

```
Exemplos de bons tópicos:

✓ "Análise do desempenho acadêmico dos alunos de graduação em Medicina 
   da turma 2022, com foco na correlação entre frequência e aprovação 
   nas disciplinas do ciclo básico"

✓ "Identificar os fatores que levaram ao aumento de 30% na taxa de 
   evasão do curso de Direito entre 2023 e 2025, e propor ações 
   de retenção para o próximo semestre"

✓ "Projeção da demanda por vagas nos cursos STEM para os próximos 
   3 anos com base nos dados históricos de inscrições do ENEM"

✗ "Analisar dados" (muito vago)
✗ "Me dê insights sobre desempenho" (sem contexto)
```

**2. Links de Sites** (opcional)

Cole URLs de páginas que contenham dados ou contexto relevante, uma por linha.

```
https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/censo-da-educacao-superior
https://www.ibge.gov.br/estatisticas/sociais/educacao
```

> **Atenção**: Links internos, localhost e endereços de intranet são bloqueados por segurança.

**3. Upload de Arquivos** (opcional)

Arraste e solte ou clique para selecionar seus arquivos. O sistema valida cada arquivo automaticamente.

```
Formatos aceitos: CSV, Excel (.xlsx, .xls), PDF, Word (.docx), TXT
Tamanho máximo: 100 MB por arquivo
```

Clique em **"Iniciar Análise"** para submeter.

---

### Acompanhando o Progresso

Após submeter, você é redirecionado para a página de resultados. O painel lateral exibe as etapas:

```
✓ Processamento Inicial      (validação e preparação)
⟳ Análises Avançadas         (agentes trabalhando em paralelo)  ← em andamento
○ Geração de Relatório       (compilação final)
```

A barra de progresso e o status são atualizados em tempo real via SSE (Server-Sent Events) — não é necessário recarregar a página.

---

### Visualizando os Resultados

Quando concluída, o relatório aparece com quatro abas:

| Aba | Conteúdo |
|-----|----------|
| **Resumo** | Resumo executivo e principais achados |
| **Análise Completa** | Relatório integral dos 5 agentes |
| **Dados** | Estatísticas brutas e tabelas |
| **Recomendações** | Lista priorizada de ações |

Para exportar, use os botões no canto superior direito:
- **Exportar PDF** — relatório formatado para impressão
- **Exportar TXT** — texto puro para copiar/colar

---

### Histórico de Análises

Acesse **"Histórico"** na navbar para ver todas as análises realizadas. Você pode:
- Filtrar por status (em andamento, concluída, com erro)
- Reabrir qualquer análise anterior
- Exportar resultados anteriores

---

## 6. Como Usar — API REST

A API permite integrar o SAPIENS em sistemas externos, scripts e automações.

### Autenticação

Todos os endpoints requerem login. Use a sessão do browser ou cookies de autenticação.

Para automação via script, faça login primeiro:

```python
import requests

session = requests.Session()

# Login
login = session.post('http://localhost:5000/login', data={
    'username': 'admin',
    'senha': 'sapiens@2025'
})
# A sessão mantém o cookie automaticamente
```

---

### Fluxo Completo via API

#### Passo 1 — Iniciar a análise

```bash
curl -X POST http://localhost:5000/api/v1/analises \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"topico_pesquisa": "Análise de evasão no curso de Física 2024"}'
```

```json
{
  "analise_id": "a3f1e2b4-8c29-4d7a-b5f6-1234567890ab",
  "status": "processando",
  "links": {
    "status": "/api/v1/analises/a3f1e2b4-8c29-4d7a-b5f6-1234567890ab",
    "resultados": "/api/v1/analises/a3f1e2b4-8c29-4d7a-b5f6-1234567890ab/resultados",
    "stream": "/stream/a3f1e2b4-8c29-4d7a-b5f6-1234567890ab"
  }
}
```

#### Passo 2 — Fazer upload de arquivo (opcional)

```bash
curl -X POST http://localhost:5000/upload \
  -b cookies.txt \
  -F "arquivo=@/caminho/para/notas_alunos.csv"
```

```json
{
  "success": true,
  "filename": "20260408_093012_notas_alunos.csv",
  "original_name": "notas_alunos.csv",
  "size": 48291,
  "validacao": {"valido": true, "tipo": "text/csv"}
}
```

#### Passo 3 — Monitorar o status

```bash
curl http://localhost:5000/api/v1/analises/a3f1e2b4-8c29-4d7a-b5f6-1234567890ab \
  -b cookies.txt
```

```json
{
  "id": "a3f1e2b4-8c29-4d7a-b5f6-1234567890ab",
  "topico_pesquisa": "Análise de evasão no curso de Física 2024",
  "status": "executando_analise",
  "progresso": 50,
  "criado_em": "2026-04-08T09:30:00"
}
```

#### Passo 4 — Obter os resultados

```bash
curl http://localhost:5000/api/v1/analises/a3f1e2b4-8c29-4d7a-b5f6-1234567890ab/resultados \
  -b cookies.txt
```

```json
{
  "analise_id": "a3f1e2b4-8c29-4d7a-b5f6-1234567890ab",
  "topico_pesquisa": "Análise de evasão no curso de Física 2024",
  "resultados": "# Relatório de Análise...",
  "concluido_em": "2026-04-08T09:58:12"
}
```

> Se a análise ainda não terminou, o retorno será HTTP 409 com `"status": "processando"`.

---

### Script Python Completo

```python
import requests
import time

BASE_URL = "http://localhost:5000"

# Inicia sessão autenticada
session = requests.Session()
session.post(f"{BASE_URL}/login", data={
    'username': 'admin',
    'senha': 'sapiens@2025'
})

# Inicia análise
resp = session.post(f"{BASE_URL}/api/v1/analises", json={
    "topico_pesquisa": "Correlação entre frequência e desempenho no curso de Enfermagem"
})
analise_id = resp.json()["analise_id"]
print(f"Análise iniciada: {analise_id}")

# Aguarda conclusão com polling
while True:
    status = session.get(f"{BASE_URL}/api/v1/analises/{analise_id}").json()
    progresso = status["progresso"]
    estado = status["status"]
    print(f"  [{progresso}%] {estado}")

    if estado == "concluida":
        break
    elif estado == "erro":
        print(f"Erro: {status.get('erro')}")
        exit(1)

    time.sleep(10)  # aguarda 10 segundos antes do próximo check

# Obtém resultados
resultado = session.get(f"{BASE_URL}/api/v1/analises/{analise_id}/resultados").json()
print("\n--- RELATÓRIO ---")
print(resultado["resultados"])

# Salva em arquivo
with open("relatorio.txt", "w", encoding="utf-8") as f:
    f.write(resultado["resultados"])
print("\nRelatório salvo em relatorio.txt")
```

---

### Monitorar via SSE (tempo real)

Para receber atualizações de progresso em tempo real sem polling:

```python
import sseclient
import requests

session = requests.Session()
session.post("http://localhost:5000/login", data={
    'username': 'admin', 'senha': 'sapiens@2025'
})

analise_id = "a3f1e2b4-8c29-4d7a-b5f6-1234567890ab"

response = session.get(
    f"http://localhost:5000/stream/{analise_id}",
    stream=True
)

for event in sseclient.SSEClient(response):
    import json
    data = json.loads(event.data)
    print(f"Progresso: {data['progresso']}% — Status: {data['status']}")
    if data['status'] in ('concluida', 'erro'):
        break
```

---

## 7. Como Usar — CLI

O SAPIENS pode ser executado diretamente pela linha de comando para testes e desenvolvimento.

### Pré-requisitos

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Configurar variáveis de ambiente (necessário)
export OPENAI_API_KEY="sua-chave-openrouter"
export OPENAI_API_BASE="https://openrouter.ai/api/v1"
export FLASK_SECRET_KEY="chave-secreta-segura"
```

### Iniciar o servidor web

```bash
python -c "
from src.Sapiens_MultiAgente.web.app import SapiensWebInterface
SapiensWebInterface(host='127.0.0.1', port=5000, debug=True).create_app().run(
    host='127.0.0.1', port=5000, debug=True
)
"
```

Acesse: `http://localhost:5000`

### Executar análise via CrewAI diretamente

```bash
# Análise padrão de demonstração
python -m Sapiens_MultiAgente run

# Treinar o crew (para otimização de prompts)
python -m Sapiens_MultiAgente train 3 treinamento_output.pkl

# Reproduzir execução de uma tarefa específica
python -m Sapiens_MultiAgente replay <task-id>

# Testar com modelo específico
python -m Sapiens_MultiAgente test 2 openai/gpt-4o
```

---

## 8. Tipos de Arquivo Suportados

### Formatos Aceitos

| Formato | Extensão | Melhor Para |
|---------|----------|-------------|
| CSV | `.csv` | Dados tabulares estruturados (notas, frequência, matrículas) |
| Excel | `.xlsx`, `.xls` | Planilhas com múltiplas abas |
| PDF | `.pdf` | Relatórios, artigos, documentos escaneados com texto |
| Word | `.docx` | Documentos textuais, relatórios institucionais |
| Texto | `.txt` | Dados brutos, logs, exportações simples |

### Limites

| Parâmetro | Valor |
|-----------|-------|
| Tamanho máximo por arquivo | 100 MB |
| Arquivos por análise | Ilimitado (via formulário) |
| Tipos MIME verificados | Sim (segurança) |
| Hash de integridade | SHA-256 |

### Como Estruturar um CSV

Para melhores resultados, o CSV deve ter:

```csv
aluno_id,nome,periodo,disciplina,nota_p1,nota_p2,nota_final,frequencia,situacao
001,Ana Silva,3,Cálculo I,7.5,8.0,7.8,0.92,aprovado
002,Bruno Lima,1,Cálculo I,3.0,4.5,3.8,0.65,reprovado
003,Carla Souza,2,Física I,6.5,7.0,6.8,0.88,aprovado
```

**Boas práticas**:
- Primeira linha com cabeçalho descritivo
- Dados numéricos sem formatação (use `7.5` não `7,5`)
- Datas no formato `YYYY-MM-DD`
- Codificação UTF-8
- Separador vírgula (o sistema também detecta `;`, `\t`, `|`)

---

## 9. Exemplos Práticos Completos

### Exemplo 1 — Análise de Desempenho por Curso

**Cenário**: A reitoria quer entender por que certos cursos têm taxa de reprovação acima de 30%.

**Arquivos necessários**:
```
notas_2024_2.csv (aluno_id, curso, disciplina, nota, frequencia, periodo)
historico_anos_anteriores.csv (mesmo formato, anos 2021–2024)
```

**Tópico a usar**:
```
Análise comparativa da taxa de reprovação dos cursos de graduação da 
instituição no período 2021–2024, identificando disciplinas críticas, 
fatores de risco e tendências, com foco especial nos cursos com taxa 
acima de 30%. Incluir recomendações para redução da reprovação.
```

**O que o relatório vai conter**:
- Taxa de reprovação por curso e disciplina (descritiva)
- Correlação entre frequência, período do curso e reprovação (diagnóstica)
- Projeção para 2025 sem intervenção (preditiva)
- Plano de ação com priorização por impacto (prescritiva)

---

### Exemplo 2 — Análise de Evasão

**Cenário**: O departamento de pós-graduação quer entender e prever evasão de mestrandos.

**Arquivos necessários**:
```
matriculas_mestrado.csv (aluno_id, orientador, area, ano_ingresso, status_atual)
producao_academica.csv (aluno_id, publicacoes, congressos, bolsa)
```

**Tópico a usar**:
```
Análise do fenômeno de evasão no programa de pós-graduação stricto sensu 
(mestrado) nos últimos 5 anos. Identificar o perfil dos alunos que evadem, 
os principais fatores associados (orientador, área temática, financiamento, 
tempo no programa) e propor estratégias de retenção com base em evidências.
```

**O que o relatório vai conter**:
- Distribuição de evasão por ano, área e orientador (descritiva)
- Variáveis com maior correlação com evasão (diagnóstica)
- Perfil de risco dos alunos atuais + probabilidade individual (preditiva)
- Programa de retenção com ações para os próximos 6 meses (prescritiva)

---

### Exemplo 3 — Análise com Link Externo

**Cenário**: Pesquisador quer contextualizar dados locais com benchmarks nacionais.

**Arquivos necessários**:
```
dados_locais.csv (dados da própria instituição)
```

**Links a usar**:
```
https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/sinopses-estatisticas/educacao-superior
```

**Tópico a usar**:
```
Comparar o desempenho dos alunos de Ciências da Computação desta 
instituição com as médias nacionais disponíveis no INEP. Identificar 
em quais métricas a instituição está acima ou abaixo da média e propor 
metas realistas de melhoria para os próximos 2 anos.
```

---

### Exemplo 4 — Análise Rápida via API

**Cenário**: Sistema automatizado que gera relatório mensal de indicadores.

```python
import requests
import time
from datetime import datetime

def gerar_relatorio_mensal(mes_referencia: str, csv_path: str):
    """Gera relatório mensal automaticamente via API."""

    session = requests.Session()
    session.post("http://localhost:5000/login", data={
        'username': 'admin', 'senha': 'sapiens@2025'
    })

    # Upload do arquivo
    with open(csv_path, 'rb') as f:
        upload = session.post("http://localhost:5000/upload",
                              files={"arquivo": f})
    print(f"Upload: {upload.json()['filename']}")

    # Inicia análise
    topico = f"""
    Relatório mensal de indicadores acadêmicos referência {mes_referencia}.
    Analisar desempenho geral, identificar disciplinas críticas, comparar 
    com mês anterior e propor ajustes para o próximo período.
    """

    resp = session.post("http://localhost:5000/api/v1/analises",
                        json={"topico_pesquisa": topico.strip()})
    analise_id = resp.json()["analise_id"]

    # Aguarda (timeout de 2 horas)
    inicio = time.time()
    while time.time() - inicio < 7200:
        status = session.get(
            f"http://localhost:5000/api/v1/analises/{analise_id}"
        ).json()

        if status["status"] == "concluida":
            # Busca e salva resultado
            resultado = session.get(
                f"http://localhost:5000/api/v1/analises/{analise_id}/resultados"
            ).json()

            filename = f"relatorio_{mes_referencia.replace('/', '_')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(resultado["resultados"])

            print(f"Relatório salvo: {filename}")
            return filename

        elif status["status"] == "erro":
            raise RuntimeError(f"Análise falhou: {status.get('erro')}")

        time.sleep(30)

    raise TimeoutError("Análise não concluiu em 2 horas")


# Uso
gerar_relatorio_mensal("Março/2026", "dados_marco_2026.csv")
```

---

## 10. Interpretando os Resultados

### Estrutura do Relatório Final

O relatório é entregue em Markdown e segue esta estrutura:

```
# Relatório de Análise — [Tópico]

## Resumo Executivo
(3-5 pontos principais, escrito para gestores)

## 1. Análise Descritiva
(estatísticas, tabelas, tendências observadas)

## 2. Análise Diagnóstica
(correlações, causas, testes estatísticos)

## 3. Análise Preditiva
(projeções, modelos, intervalos de confiança)

## 4. Análise Prescritiva
(recomendações priorizadas, plano de ação)

## Considerações Metodológicas
(limitações, premissas, qualidade dos dados)
```

### Como Ler os Indicadores Estatísticos

| Indicador | O que significa | Como interpretar |
|-----------|-----------------|------------------|
| **r (correlação)** | Força da relação entre duas variáveis | 0 = nenhuma, 1 = perfeita. \|r\| > 0,5 é relevante |
| **p-valor** | Probabilidade do resultado ser por acaso | p < 0,05 = resultado significativo |
| **R²** | Quanto o modelo explica da variabilidade | 0,7 = modelo explica 70% das variações |
| **IC 95%** | Intervalo de confiança | O valor verdadeiro está neste intervalo 95% das vezes |
| **Desvio padrão (σ)** | Dispersão em torno da média | Pequeno = dados homogêneos, grande = heterogêneos |

### Sinais de um Bom Relatório

- As análises citam os dados reais fornecidos (não dados genéricos)
- Os números são coerentes entre as seções
- As recomendações têm relação direta com os problemas identificados
- Limitações dos dados são mencionadas

### Sinais de Problema

- Relatório muito genérico sem citar os dados enviados → forneça arquivos mais detalhados
- "Não foi possível acessar os dados" → verifique o formato do CSV ou o tamanho do arquivo
- Análise incompleta → o tópico pode estar muito vago; adicione contexto

---

## 11. Segurança e Limites

### O que o Sistema Valida

Antes de processar qualquer arquivo, o SAPIENS verifica:

| Verificação | Detalhe |
|-------------|---------|
| Tipo MIME | O arquivo é realmente o que diz ser (ex.: não é um executável renomeado como .csv) |
| Tamanho | Máximo 100 MB por arquivo |
| Hash SHA-256 | Integridade do arquivo durante a transferência |
| PII (dados pessoais) | Detecta CPF, CNPJ, e-mail, telefone e alerta o usuário |

### Links Bloqueados por Segurança

O sistema bloqueia URLs que apontem para:
- Localhost (`127.0.0.1`, `::1`)
- Redes privadas (`192.168.x.x`, `10.x.x.x`, `172.16-31.x.x`)
- Metadata de cloud AWS, GCP, Azure (`169.254.169.254`)
- Domínios internos (`.local`, `.internal`)

### Limites de Taxa (Rate Limiting)

| Endpoint | Limite |
|----------|--------|
| `POST /upload` | 5 uploads por minuto por IP |
| `GET /status/<id>` | 10 consultas por minuto por IP |
| Todos os outros | 200 por hora / 50 por minuto |

### Dados e Privacidade

- Os arquivos são deletados automaticamente após o processamento da análise
- Os resultados ficam armazenados no banco SQLite local
- Cada usuário só acessa suas próprias análises
- Logs de auditoria registram todas as operações com timestamp

---

## 12. Referência da API

### Endpoints Disponíveis

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `GET` | `/` | Página inicial | ✓ |
| `GET` | `/analise` | Formulário de análise | ✓ |
| `POST` | `/analise` | Submeter análise via form | ✓ |
| `POST` | `/upload` | Upload de arquivo (AJAX) | ✓ |
| `GET` | `/resultados/<id>` | Página de resultados | ✓ |
| `GET` | `/progresso/<id>` | Página de progresso | ✓ |
| `GET` | `/historico` | Histórico de análises | ✓ |
| `GET` | `/stream/<id>` | SSE de progresso em tempo real | ✓ |
| `GET` | `/export/<id>/<fmt>` | Exportar resultado (`pdf` ou `txt`) | ✓ |
| `GET` | `/status/<id>` | Status JSON de uma análise | ✓ |
| `GET` | `/status` | Painel de saúde do sistema | ✓ |
| `GET` | `/api/health` | Health check JSON | ✓ |
| `GET` | `/api/v1/analises` | Listar análises (API REST) | ✓ |
| `POST` | `/api/v1/analises` | Criar análise (API REST) | ✓ |
| `GET` | `/api/v1/analises/<id>` | Detalhes de uma análise | ✓ |
| `GET` | `/api/v1/analises/<id>/resultados` | Resultados completos | ✓ |
| `GET` | `/api/docs` | Documentação Swagger | ✓ |

### Códigos de Retorno

| Código | Significado |
|--------|-------------|
| `200` | Sucesso |
| `202` | Análise iniciada (processamento assíncrono) |
| `302` | Redirecionamento (formulário web) |
| `400` | Dados inválidos na requisição |
| `401` | Não autenticado |
| `403` | Sem permissão para acessar este recurso |
| `404` | Análise não encontrada |
| `409` | Análise ainda não concluída |
| `429` | Limite de taxa excedido |
| `500` | Erro interno do servidor |

---

## 13. Resolução de Problemas

### "A análise ficou com status 'erro'"

**Causa mais comum**: A LLM não conseguiu processar os dados.

**O que fazer**:
1. Verifique os logs em `logs/sapiens_academico.log`
2. Verifique se as variáveis de ambiente estão configuradas:
   ```bash
   echo $OPENAI_API_KEY
   echo $OPENAI_API_BASE
   ```
3. Verifique se o arquivo CSV está bem formatado (sem caracteres especiais no cabeçalho)
4. Tente um tópico mais simples primeiro para testar

---

### "O relatório é muito genérico"

**Causa**: O tópico de pesquisa não tinha contexto suficiente, ou os arquivos não foram carregados corretamente.

**O que fazer**:
1. Adicione mais contexto ao tópico: curso, período, instituição, objetivo específico
2. Confirme que o arquivo foi carregado antes de iniciar (o ícone de validação deve aparecer verde)
3. Verifique se o CSV tem cabeçalho descritivo

---

### "O upload falhou"

**Causa**: Tipo de arquivo não suportado, tamanho acima do limite, ou arquivo corrompido.

**O que fazer**:
1. Confirme que o arquivo tem extensão `.csv`, `.xlsx`, `.xls`, `.pdf`, `.docx` ou `.txt`
2. Verifique se o arquivo tem menos de 100 MB
3. Tente abrir o arquivo localmente para confirmar que não está corrompido
4. Para CSV, salve como UTF-8 e use vírgula como separador

---

### "A análise está demorando muito"

**Comportamento normal**: O SAPIENS usa 5 agentes e cada um faz múltiplas chamadas à LLM. O tempo médio é de 10–40 minutos para análises completas.

**Timeout configurável**:
```bash
# Aumentar timeout para 4 horas (padrão é 2 horas)
export SAPIENS_CREW_TIMEOUT=14400
```

---

### "Erro CSRF token missing"

Ao usar o formulário web, este erro indica que a sessão expirou.

**O que fazer**:
1. Faça logout e login novamente
2. Verifique se a variável `FLASK_SECRET_KEY` está configurada
3. Não use a mesma aba por mais de 8 horas sem interação

---

### Variáveis de Ambiente

| Variável | Obrigatória | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `OPENAI_API_KEY` | Sim | — | Chave da API OpenRouter |
| `OPENAI_API_BASE` | Sim | — | URL base OpenRouter (`https://openrouter.ai/api/v1`) |
| `FLASK_SECRET_KEY` | Sim | — | Chave secreta para sessões Flask |
| `SAPIENS_ADMIN_PASSWORD` | Não | `sapiens@2025` | Senha do usuário admin |
| `SAPIENS_DB_PATH` | Não | `sapiens.db` | Caminho do banco SQLite |
| `SAPIENS_CREW_TIMEOUT` | Não | `7200` (2h) | Timeout da análise em segundos |
| `SAPIENS_ENV` | Não | `desenvolvimento` | Ambiente (`desenvolvimento` ou `producao`) |
| `WEB_HOST` | Não | `127.0.0.1` | Host do servidor Flask |
| `WEB_PORT` | Não | `5000` | Porta do servidor Flask |

---

*Documentação gerada para SAPIENS v2.1.0 · Abril de 2026*
