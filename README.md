# SAPIENS — Plataforma Acadêmica Multiagente de Análise de Dados

![Versão](https://img.shields.io/badge/SAPIENS-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Testes](https://img.shields.io/badge/testes-423%20passando-brightgreen)
![Licença](https://img.shields.io/badge/licença-MIT-lightgrey)

O **SAPIENS** é uma plataforma de código aberto que utiliza orquestração de agentes de IA para executar análises acadêmicas completas — descritivas, diagnósticas, preditivas, prescritivas, textuais e comparativas com benchmarks nacionais — com rigor científico e interface web acessível.

Desenvolvido na **Universidade Estadual do Norte Fluminense Darcy Ribeiro (UENF)**, o SAPIENS foi concebido para fortalecer a gestão universitária baseada em evidências e acelerar a pesquisa científica.

---

## Visão Geral

O sistema resolve um problema recorrente em instituições acadêmicas: a dificuldade de realizar análises de dados robustas sem exigir conhecimento avançado em ciência de dados. Um **Agente Gerente Orquestrador** coordena equipes de agentes especializados que trabalham em paralelo, entregando um relatório final consolidado com qualidade metodológica verificada.

---

## Pipeline Multiagente

```
Validação → Processamento →

  [ Descritiva | Diagnóstica | Preditiva | Prescritiva | Fontes Externas | Textual ]
                              (execução paralela)
                                        ↓
                          Revisor de Qualidade Científica
                                        ↓
                              Relatório Final
```

| Etapa | Agente | Pergunta respondida |
|-------|--------|-------------------|
| Validação + Processamento | Gerente Orquestrador | Dados reais disponíveis? |
| Análise Descritiva | Especialista Descritivo | O que aconteceu? |
| Análise Diagnóstica | Especialista Diagnóstico | Por que aconteceu? |
| Análise Preditiva | Especialista Preditivo | O que pode acontecer? |
| Análise Prescritiva | Especialista Prescritivo | O que devemos fazer? |
| Fontes Externas | Especialista em Benchmarks | Como estamos vs o Brasil? |
| Análise Textual | Especialista em NLP | O que dizem os documentos? |
| Revisão de Qualidade | Revisor Científico | A análise tem rigor metodológico? |
| Relatório Final | Gerente Orquestrador | — |

---

## Ferramentas Disponíveis

| Tool | Descrição |
|------|-----------|
| `DataValidationTool` | Valida arquivos e dados de entrada |
| `CSVProcessorTool` | Processa e limpa arquivos CSV/Excel |
| `StatisticalAnalysisTool` | Análises estatísticas (descritiva, correlação, regressão, ANOVA) |
| `ChartGeneratorTool` | Gera gráficos em base64 e PNG |
| `PDFSearchTool` | Lê e pesquisa em PDFs |
| `DOCXSearchTool` | Lê e pesquisa em arquivos DOCX |
| `CSVSearchTool` | Pesquisa em CSVs |
| `ExternalDataTool` | Benchmarks nacionais INEP/IBGE/CAPES/MEC |
| `TextAnalysisTool` | NLP: palavras-chave, entidades, temas |
| `QualityReviewTool` | Revisão metodológica científica (pontuação 0–100) |

---

## Características Principais

- **8 agentes especializados** com papéis distintos e ferramentas dedicadas
- **Execução paralela** dos 6 especialistas, seguida de revisão sequencial
- **Revisão de qualidade científica** integrada — detecta generalizações, causalidade sem suporte, p-valor sem tamanho de efeito
- **Benchmarks nacionais** automáticos via INEP, IBGE, CAPES e MEC
- **Análise textual (NLP)** de PDFs, DOCX e relatórios narrativos
- **Interface web Flask** com SSE para progresso em tempo real
- **Monitor de plataforma** com métricas de CPU, memória e análises via `/api/monitoring`
- **Segurança**: PBKDF2-SHA256, validação MIME, CSRF, rate limiting, auditoria JSONL
- **Suporte PT/EN** nas ferramentas estatísticas
- **423 testes automatizados** passando

---

## Arquitetura e Tecnologias

### Backend
| Tecnologia | Versão | Função |
|---|---|---|
| **Python** | 3.10+ | Linguagem principal |
| **CrewAI** | 0.177+ | Orquestração dos agentes |
| **Flask** | 3.0+ | Interface web |
| **Flask-Login / WTF / Limiter** | — | Autenticação, CSRF, rate limiting |
| **Pandas / NumPy / SciPy** | — | Análises estatísticas |
| **Matplotlib** | — | Geração de gráficos |
| **pypdf / python-docx** | — | Leitura de PDF e DOCX |
| **psutil** | — | Monitoramento de recursos |
| **SQLite** | — | Persistência de análises |
| **OpenRouter** | — | Provedor LLM |
| **Llama 3.3 8B** | — | Modelo de linguagem dos agentes |

### Frontend
| Tecnologia | Função |
|---|---|
| **Bootstrap 5.3** | Layout responsivo |
| **Font Awesome 6.4** | Ícones |
| **Server-Sent Events (SSE)** | Progresso em tempo real |

---

## Instalação

### Pré-requisitos
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (gerenciador de pacotes recomendado)
- Conta no [OpenRouter](https://openrouter.ai) com chave de API

### Passos

```bash
# 1. Clonar o repositório
git clone https://github.com/fabriciosilvasantos/Sapiens_MultiAgente.git
cd Sapiens_MultiAgente

# 2. Criar e ativar ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# 3. Instalar dependências
uv pip install -e .

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas chaves
```

### Variáveis de Ambiente (`.env`)

```env
# Obrigatórias
OPENAI_API_KEY=sua-chave-openrouter
OPENAI_API_BASE=https://openrouter.ai/api/v1
FLASK_SECRET_KEY=sua-chave-secreta-flask

# Opcionais
SAPIENS_ADMIN_PASSWORD=sapiens@2025
SAPIENS_DB_PATH=sapiens.db
SAPIENS_CREW_TIMEOUT=7200
WEB_HOST=127.0.0.1
WEB_PORT=4000
```

---

## Como Usar

### Interface Web (recomendado)

```bash
source .venv/bin/activate
python -m Sapiens_MultiAgente.web.app
```

Acesse: `http://127.0.0.1:4000`

1. Faça login com as credenciais configuradas
2. Faça upload do arquivo de dados (CSV, Excel, PDF, DOCX)
3. Descreva o tópico de pesquisa
4. Acompanhe o progresso em tempo real
5. Baixe o relatório final

### Linha de Comando

```bash
source .venv/bin/activate
python -m Sapiens_MultiAgente.main run
```

---

## Estrutura do Projeto

```
Sapiens_MultiAgente/
├── pyproject.toml
├── CLAUDE.md                          # Guia para Claude Code
├── src/Sapiens_MultiAgente/
│   ├── crew.py                        # Definição de agentes e tarefas
│   ├── main.py                        # CLI
│   ├── config/
│   │   ├── agents.yaml                # Configuração dos 8 agentes
│   │   └── tasks.yaml                 # Definição das 10 tarefas
│   ├── tools/
│   │   ├── data_validation_tool.py
│   │   ├── csv_processor_tool.py
│   │   ├── statistical_analysis_tool.py
│   │   ├── chart_generator_tool.py
│   │   ├── pdf_search_tool.py
│   │   ├── docx_search_tool.py
│   │   ├── csv_search_tool.py
│   │   ├── external_data_tool.py      # Benchmarks INEP/IBGE/CAPES/MEC
│   │   ├── text_analysis_tool.py      # NLP acadêmico
│   │   └── quality_review_tool.py     # Revisão metodológica
│   └── web/
│       ├── app.py                     # Flask + SSE + rotas
│       ├── auth.py                    # Autenticação PBKDF2-SHA256
│       ├── monitoring.py              # SapiensMonitor (CPU/mem/análises)
│       └── templates/                 # Templates HTML
├── tests/                             # 423 testes automatizados
└── data/                              # Datasets e relatórios de exemplo
```

---

## Executar Testes

```bash
source .venv/bin/activate
pytest tests/ -v --tb=short --cov=src/Sapiens_MultiAgente --cov-report=term-missing
```

---

## Monitoramento

A plataforma expõe métricas em tempo real via `/api/monitoring` (requer login):

```json
{
  "cpu_pct": 12.4,
  "mem_pct": 34.2,
  "disk_pct": 58.0,
  "analises_total": 47,
  "analises_ok": 44,
  "taxa_sucesso": 93.6
}
```

Visualização disponível em `/status`.

---

## Exemplo de Análise

**Dataset:** Alunos da UENF 2020–2025 (132 registros, 12 cursos, 5 centros)

**Pergunta:** *"Analise a evasão estudantil por curso no período 2020–2025."*

**Resultado obtido:**
- Evasão caiu **50%** (212 → 106 evadidos/semestre)
- Correlação evasão × reprovações: **r = 0,907**
- CCT concentra **59,6%** de toda a evasão institucional
- UENF superou a média nacional (18,9% vs 26,4% — INEP 2023)
- Projeção 2026: taxa abaixo de **15%** se tendência mantida

---

## Segurança

- Senhas com **PBKDF2-SHA256** + salt único por usuário
- Validação de **tipo MIME** em todos os uploads
- **Rate limiting** nas rotas de análise
- Proteção **CSRF** em formulários
- **Auditoria** completa em `logs/auditoria_academica.jsonl`
- Timeout configurável via `SAPIENS_CREW_TIMEOUT`

---

## Contribuição

1. Faça fork do projeto
2. Crie uma branch: `git checkout -b feature/minha-feature`
3. Commit: `git commit -m 'feat: descrição da feature'`
4. Push: `git push origin feature/minha-feature`
5. Abra um Pull Request

---

## Suporte

- **Bugs / Issues:** [github.com/fabriciosilvasantos/Sapiens_MultiAgente/issues](https://github.com/fabriciosilvasantos/Sapiens_MultiAgente/issues)
- **Contato:** fabricio@uenf.br

---

## Licença

MIT License — veja o arquivo `LICENSE` para detalhes.

---

## Agradecimentos

- **CrewAI Team** — framework de orquestração de agentes
- **Meta** — modelo Llama 3.3
- **OpenRouter** — infraestrutura de acesso a LLMs
- **INEP / IBGE / CAPES / MEC** — dados públicos de referência
- **Comunidade acadêmica da UENF** — inspiração e feedback

---

<div align="center">
  <strong>SAPIENS v1.0.0 — Desenvolvido na UENF</strong><br>
  Transformando dados acadêmicos em conhecimento estratégico
</div>
