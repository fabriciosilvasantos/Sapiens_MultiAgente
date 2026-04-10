# SAPIENS — Guia para Claude Code

## Contexto do projeto

Plataforma acadêmica multiagente de análise de dados construída com CrewAI + Flask.

- **Pacote principal**: `src/Sapiens_MultiAgente/`
- **Ambiente virtual**: `.venv/` (ativar com `source .venv/bin/activate`)
- **Banco de dados**: SQLite em `sapiens.db` (criado automaticamente)
- **Testes**: `pytest tests/` — atualmente 57 testes
- **LLM**: OpenRouter via variável `OPENAI_API_KEY` + `OPENAI_API_BASE`

## Skills disponíveis

### /test-sapiens
Executa a suíte completa de testes com relatório de cobertura.

```bash
source .venv/bin/activate && pytest tests/ -v --tb=short --cov=src/Sapiens_MultiAgente --cov-report=term-missing
```

### /lint-sapiens
Verifica qualidade de código com flake8 nas configurações do projeto.

```bash
source .venv/bin/activate && flake8 src/ --max-line-length=120 --exclude=__pycache__ --extend-ignore=E501,W503,E203
```

### /start-dev
Inicia o servidor Flask em modo desenvolvimento na porta 5000.

```bash
source .venv/bin/activate && python -c "
from src.Sapiens_MultiAgente.web.app import SapiensWebInterface
SapiensWebInterface(host='127.0.0.1', port=5000, debug=True).create_app().run(host='127.0.0.1', port=5000, debug=True)
"
```

### /check-env
Verifica se todas as variáveis de ambiente necessárias estão configuradas.

```bash
python -c "
import os
required = {
    'OPENAI_API_KEY':    'Chave da API OpenRouter (obrigatória para LLM)',
    'OPENAI_API_BASE':   'Base URL do OpenRouter (ex: https://openrouter.ai/api/v1)',
    'FLASK_SECRET_KEY':  'Chave secreta Flask para sessões',
}
optional = {
    'SAPIENS_ADMIN_PASSWORD': 'Senha do admin padrão (padrão: sapiens@2025)',
    'SAPIENS_DB_PATH':        'Caminho do banco SQLite (padrão: sapiens.db)',
    'SAPIENS_CREW_TIMEOUT':   'Timeout da crew em segundos (padrão: 7200)',
    'SAPIENS_ENV':            'Ambiente: desenvolvimento | producao',
    'WEB_HOST':               'Host do servidor (padrão: 127.0.0.1)',
    'WEB_PORT':               'Porta do servidor (padrão: 5000)',
}
print('=== Variáveis OBRIGATÓRIAS ===')
ok = True
for var, desc in required.items():
    val = os.getenv(var)
    status = '✅' if val else '❌ FALTANDO'
    print(f'  {status}  {var}: {desc}')
    if not val:
        ok = False
print()
print('=== Variáveis OPCIONAIS ===')
for var, desc in optional.items():
    val = os.getenv(var, '(padrão)')
    print(f'  ℹ️   {var} = {val}')
print()
print('Resultado:', '✅ Ambiente OK' if ok else '❌ Configure as variáveis faltando no arquivo .env')
"
```

## Convenções do projeto

- Usar `uv pip install` para instalar dependências
- Todas as tools herdam de `crewai.tools.BaseTool` com `args_schema` Pydantic
- Mensagens de erro nas tools começam com `❌ ERRO:`
- Análises são persistidas em SQLite + cache em memória (`analises_ativas`)
- Senhas usam PBKDF2-SHA256 com salt aleatório por usuário (ver `web/auth.py`)
- Timeout da crew configurável via `SAPIENS_CREW_TIMEOUT` (padrão 2h)

## Arquitetura dos agentes

```
agente_gerente_orquestrador             → valida dados e orquestra
  ↓
especialista_em_analise_descritiva      ┐
especialista_em_analise_diagnostica     │
especialista_em_analise_preditiva       ├ async_execution=True (paralelas)
especialista_em_analise_prescritiva     │
especialista_em_fontes_externas         │ (INEP/IBGE benchmarks)
especialista_em_analise_textual         ┘ (NLP documentos)
  ↓ (todas concluídas)
revisor_de_qualidade_cientifica         → revisão metodológica (sequencial)
  ↓
compilacao_e_apresentacao_do_relatorio_final
```

## Tools disponíveis

| Tool | Descrição |
|------|-----------|
| `DataValidationTool` | Valida arquivos e dados de entrada |
| `CSVProcessorTool` | Processa e limpa arquivos CSV |
| `StatisticalAnalysisTool` | Análises estatísticas (descritiva, correlação, regressão) |
| `ChartGeneratorTool` | Gera gráficos em base64 |
| `PDFSearchTool` | Lê e pesquisa em PDFs |
| `DOCXSearchTool` | Lê e pesquisa em arquivos DOCX |
| `CSVSearchTool` | Pesquisa em CSVs |
| `ExternalDataTool` | Benchmarks INEP/IBGE/CAPES/MEC |
| `QualityReviewTool` | Revisão metodológica científica |
| `TextAnalysisTool` | Análise textual NLP (palavras-chave, entidades, temas) |
