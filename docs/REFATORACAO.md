# SAPIENS — Plano de Refatoracao

Levantamento completo de refatoracoes pendentes, ordenado por prioridade.
Gerado em: 2026-04-10

---

## CONCLUIDO

### [x] web/app.py — Extracao de metodos do create_app()
- **Arquivo**: `src/Sapiens_MultiAgente/web/app.py`
- **Problema**: `create_app()` com ~477 linhas, todas as rotas definidas inline
- **Solucao aplicada**: Extraido em 6 metodos privados (`_setup_template_filters`, `_setup_auth_routes`, `_setup_page_routes`, `_setup_system_routes`, `_setup_config_routes`, `_setup_api_v1_routes`) + `_event_generator` extraido do SSE inline
- **Resultado**: `create_app()` reduzido para ~40 linhas, 513 testes passando

---

## PRIORIDADE ALTA

### [ ] Duplicacao entre pdf_search_tool.py e docx_search_tool.py
- **Arquivos**:
  - `src/Sapiens_MultiAgente/tools/pdf_search_tool.py` (264 linhas)
  - `src/Sapiens_MultiAgente/tools/docx_search_tool.py` (269 linhas)
- **Problema**: ~70% de estrutura identica — schema de input, logica de busca por texto, tratamento de erros, formatacao de saida
- **Solucao proposta**: Criar `BaseDocumentSearchTool` com template method pattern. Cada subclasse implementa apenas `_extract_text()`, `_get_info()` e `_search_content()`. Elimina ~150 linhas duplicadas.
- **Testes afetados**: `tests/test_search_tools.py` (428 linhas)

### [ ] external_data_tool.py — Metodo _run() com ~150 linhas
- **Arquivo**: `src/Sapiens_MultiAgente/tools/external_data_tool.py` (343 linhas)
- **Problema**: `_run()` faz fetch HTTP, parsing de resposta e formatacao tudo em um unico metodo
- **Solucao proposta**: Extrair em `_fetch_data()`, `_parse_response()`, `_format_result()`. Facilita teste unitario de cada etapa.
- **Testes afetados**: `tests/test_coverage_boost4.py`

### [ ] Consolidar arquivos test_coverage_boost
- **Arquivos**:
  - `tests/test_coverage_boost2.py` (631 linhas)
  - `tests/test_coverage_boost3.py` (573 linhas)
  - `tests/test_coverage_boost4.py` (960 linhas)
  - `tests/test_coverage_boost5.py` (708 linhas)
  - `tests/test_coverage_boost6.py` (352 linhas)
  - `tests/test_coverage_boost7.py` (432 linhas)
  - `tests/test_coverage_boost8.py` (149 linhas)
  - `tests/test_coverage_boost9.py` (96 linhas)
  - `tests/test_coverage_boost10.py` (666 linhas)
- **Problema**: 9 arquivos com nomes genericos (~4.567 linhas total). Impossivel saber o que cada um testa sem abrir o arquivo.
- **Solucao proposta**: Renomear/reorganizar por funcionalidade:
  - `test_security_validator.py` — testes de validacao de seguranca
  - `test_statistical_analysis.py` — testes de analise estatistica
  - `test_chart_generator.py` — testes de geracao de graficos
  - `test_academic_logger.py` — testes de auditoria
  - `test_export.py` — testes de exportacao PDF/TXT
  - `test_web_routes.py` — testes de rotas web adicionais
  - `test_llm_config.py` — testes de configuracao LLM
  - `test_monitoring.py` — testes de monitoramento

---

## PRIORIDADE MEDIA

### [ ] Constantes repetidas em multiplos arquivos
- **Arquivos afetados**:
  - `src/Sapiens_MultiAgente/web/app.py` linha 82: `ALLOWED_EXTENSIONS`
  - `api/index.py`: mesma lista de extensoes duplicada
  - `src/Sapiens_MultiAgente/tools/security_validator.py`: `config_padrao` com MIME types e extensoes
- **Problema**: Alterar extensoes permitidas requer mudanca em 3 lugares
- **Solucao proposta**: Criar `src/Sapiens_MultiAgente/config/constants.py` com:
  ```python
  ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'pdf', 'docx', 'txt'}
  MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
  ALLOWED_MIME_TYPES = { ... }
  ```

### [ ] Caminhos de YAML hardcoded
- **Arquivos afetados**:
  - `src/Sapiens_MultiAgente/tools/academic_logger.py`: `"src/Sapiens_MultiAgente/config/logging_config.yaml"`
  - `src/Sapiens_MultiAgente/config/llm_settings.py`: caminho relativo para `llm_config.yaml`
- **Problema**: Quebra quando executado de diretorio diferente da raiz do projeto
- **Solucao proposta**: Usar `pathlib.Path(__file__).parent` para resolver caminhos relativos ao modulo

### [ ] conftest.py minimo
- **Arquivo**: `tests/conftest.py` (14 linhas)
- **Problema**: Fixtures compartilhadas (app Flask de teste, cliente HTTP, usuario autenticado) sao recriadas em cada arquivo de teste
- **Solucao proposta**: Centralizar em `conftest.py`:
  ```python
  @pytest.fixture
  def app():
      interface = SapiensWebInterface()
      return interface.create_app()

  @pytest.fixture
  def client(app):
      return app.test_client()

  @pytest.fixture
  def authenticated_client(client):
      # login e retorna client autenticado
  ```

### [ ] security_validator.py — Classe grande com responsabilidades mistas
- **Arquivo**: `src/Sapiens_MultiAgente/tools/security_validator.py` (354 linhas)
- **Problema**: `AcademicSecurityValidator` faz validacao de arquivo (extensao, MIME, tamanho), deteccao de PII (regex CPF/email/telefone) e hashing — responsabilidades distintas
- **Solucao proposta**: Separar em:
  - `FileValidator` — extensao, MIME type, tamanho
  - `PIIDetector` — regex de dados sensiveis
  - `AcademicSecurityValidator` — orquestra ambos (facade)

### [ ] academic_logger.py — God class
- **Arquivo**: `src/Sapiens_MultiAgente/tools/academic_logger.py` (300 linhas)
- **Problema**: `AcademicAuditor` acumula configuracao de logging, formatacao JSON, eventos de auditoria, exportacao e estatisticas
- **Solucao proposta**: Separar em:
  - `AcademicAuditor` — interface principal (eventos de auditoria)
  - `JsonAuditFormatter` — formatacao de log em JSON
  - `AuditExporter` — exportacao de relatorios de auditoria

---

## PRIORIDADE BAIXA

### [ ] Alertas flake8 (43 ocorrencias)
- **Distribuicao**:
  - 22x `E501` — linhas longas (>120 caracteres)
  - 10x `E302` — espacamento entre funcoes
  - 7x `E402` — imports fora do topo
  - 3x `F401` — imports nao utilizados (`json` importado mas nao usado)
  - 1x `E305` — espacamento apos definicao de classe
- **Solucao**: Correcao mecanica, pode ser feita com autoformatter

### [ ] custom_tool.py — Stub sem uso
- **Arquivo**: `src/Sapiens_MultiAgente/tools/custom_tool.py` (20 linhas)
- **Problema**: Arquivo esqueleto sem funcionalidade real
- **Solucao proposta**: Remover se nao for necessario, ou documentar se for placeholder intencional

### [ ] Type hints incompletos nos metodos _run()
- **Arquivos afetados**: Varios em `tools/`
- **Problema**: Metodos `_run()` retornam `str` mas nem todos tem anotacao de retorno explicita
- **Solucao proposta**: Adicionar `-> str` nos metodos `_run()` de todas as tools

### [ ] DB_PATH duplicado em app.py e auth.py
- **Arquivos**:
  - `src/Sapiens_MultiAgente/web/app.py` linha 36
  - `src/Sapiens_MultiAgente/web/auth.py` linha 16
- **Problema**: Mesma chamada `os.getenv('SAPIENS_DB_PATH', 'sapiens.db')` em dois modulos
- **Solucao proposta**: Definir em um unico local e importar (ex: `config/constants.py`)

### [ ] _get_db() duplicado em app.py e auth.py
- **Arquivos**:
  - `src/Sapiens_MultiAgente/web/app.py` linhas 39-43
  - `src/Sapiens_MultiAgente/web/auth.py` linhas 30-33
- **Problema**: Funcao identica definida duas vezes
- **Solucao proposta**: Mover para modulo compartilhado (`web/db.py` ou `config/database.py`)

---

## FORA DE ESCOPO (nao precisa de refatoracao)

| Componente | Motivo |
|------------|--------|
| `crew.py` (203 linhas) | Bem organizado, YAML-driven |
| `auth.py` (217 linhas) | PBKDF2-SHA256, 100k iteracoes, salt individual, protecao brute-force |
| `config/llm_fallback.py` (165 linhas) | Retry + fallback Groq, limpo |
| `config/llm_settings.py` (98 linhas) | Compacto e funcional |
| `monitoring.py` (153 linhas) | Isolado e independente |
| Arquitetura de agentes | Sem dependencias circulares, separacao clara |
| Tools individuais (exceto as listadas) | Tamanho razoavel, responsabilidade unica |

---

## METRICAS ATUAIS

| Metrica | Valor |
|---------|-------|
| Linhas de codigo (src/) | ~5.400 |
| Linhas de teste | ~6.800 |
| Ratio teste/codigo | 1.25x |
| Testes | 513 passando |
| Dependencias circulares | 0 |
| Alertas flake8 | 43 |
