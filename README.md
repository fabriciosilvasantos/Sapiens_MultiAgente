# SAPIENS - Plataforma Acadêmica Multiagente de Análise de Dados

![SAPIENS Logo](https://img.shields.io/badge/SAPIENS-2.0.0-blue)
![Python Version](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Plataforma acadêmica avançada para análise de dados usando múltiplos agentes especializados. Desenvolvida com CrewAI e interface web moderna para pesquisadores, gestores universitários e estudantes.

## 🚀 Características Principais

- **🤖 Agentes Especializados**: 5 agentes especializados em diferentes tipos de análise
- **🔒 Segurança Avançada**: Validação rigorosa de arquivos e auditoria completa
- **🌐 Interface Web**: Interface moderna e responsiva para interação
- **📊 Análise Completa**: Descritiva, diagnóstica, preditiva e prescritiva
- **📋 Auditoria Detalhada**: Sistema completo de logging para rastreabilidade
- **🔧 Configuração Flexível**: Estrutura configurável para diferentes ambientes

## 📋 Tipos de Análise

| Tipo | Descrição | Agente Especialista |
|------|-----------|-------------------|
| **Descritiva** | O que aconteceu? | Estatísticas básicas e tendências |
| **Diagnóstica** | Por que aconteceu? | Causas e correlações |
| **Preditiva** | O que pode acontecer? | Previsões futuras |
| **Prescritiva** | O que devemos fazer? | Recomendações acionáveis |

## 🛠️ Instalação

### Pré-requisitos

- Python >= 3.10 e < 3.14
- UV (recomendado) ou pip
- Git

### Dependências Adicionais

Para processamento completo de arquivos, certifique-se de ter as seguintes bibliotecas instaladas:
- `python-docx` - Para processamento de arquivos DOCX
- `pypdf` - Para processamento de arquivos PDF
- Todas as outras dependências serão instaladas automaticamente

### Passo a Passo

1. **Clone o repositório**
```bash
git clone <repository-url>
cd Sapiens_MultiAgente
```

2. **Execute a instalação automática (recomendado)**
```bash
# Instalação automática (Linux/macOS)
./install_sapiens.sh

# Ou instalação manual
chmod +x install_sapiens.sh
./install_sapiens.sh
```

3. **Instalação manual alternativa**
```bash
# Detectar automaticamente python3
python3 start_sapiens.py --status

# Instalar dependências
python3 -m pip install -e .

# Ou usar o launcher
python3 start_sapiens.py
```

4. **Configure o ambiente**
```bash
# Copiar configurações de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
nano .env  # ou use seu editor preferido
```
## 🚀 Como Usar

### Interface Web (Recomendado)

1. **Inicie a interface web**
```bash
# Método 1: Usando o launcher
python3 start_sapiens.py --web

# Método 2: Diretamente
cd src/Sapiens_MultiAgente
python3 -m web.app

# Método 3: Especificar host/porta
python3 start_sapiens.py --web --host 0.0.0.0 --port 8080
```

2. **Acesse no navegador**
```
http://127.0.0.1:5000
```

3. **Faça upload dos seus dados**
   - CSV, Excel, PDF, DOCX
   - Máximo 100MB por arquivo

4. **Descreva sua pesquisa**
   - Seja específico sobre o objetivo
   - Escolha tipos de análise desejados

5. **Acompanhe o progresso**
   - Sistema mostra progresso em tempo real
   - Auditoria completa de todas as ações

### Linha de Comando (Avançado)

```bash
# Método 1: Usando o launcher
python3 start_sapiens.py --cli --topic "Sua pesquisa aqui"

# Método 2: Diretamente
cd src/Sapiens_MultiAgente
python3 main.py run

# Método 3: Verificar status
python3 start_sapiens.py --status
```

### Launcher Interativo

```bash
# Inicia menu interativo
python3 start_sapiens.py

# Opções disponíveis:
# 1) Interface web
# 2) Análise CLI
# 3) Status do sistema
# 4) Sair
```

## 📁 Estrutura do Projeto

```
Sapiens_MultiAgente/
├── 📋 README.md
├── ⚙️ pyproject.toml
├── 🔧 src/Sapiens_MultiAgente/
│   ├── 🤖 crew.py              # Configuração dos agentes
│   ├── 🚀 main.py              # Interface de linha de comando
│   ├── ⚙️ config/
│   │   ├── agents.yaml         # Configuração detalhada dos agentes
│   │   ├── tasks.yaml          # Definição das tarefas
│   │   └── logging_config.yaml # Configurações de auditoria
│   ├── 🛠️ tools/
│   │   ├── academic_tools.py   # Ferramentas especializadas
│   │   ├── academic_logger.py  # Sistema de auditoria
│   │   ├── security_validator.py # Validação de segurança
│   │   └── custom_tool.py      # Template para ferramentas
│   └── 🌐 web/
│       ├── app.py              # Interface web Flask
│       └── templates/          # Templates HTML
├── 📊 knowledge/               # Base de conhecimento
└── 🧪 tests/                   # Testes automatizados
```

## 🔒 Segurança e Auditoria

### Configurações de Segurança

A partir da versão 2.0.0, foram implementadas melhorias significativas de segurança:

- **Secret Key Dinâmica**: A secret key do Flask agora é carregada de variável de ambiente (`FLASK_SECRET_KEY`)
- **Validação de Arquivos**: Verificação rigorosa de tipos MIME e conteúdo malicioso
- **Auditoria Completa**: Sistema de logging estruturado para rastreabilidade
- **Controle de Acesso**: Validações em múltiplas camadas

#### Configurando a Secret Key

```bash
# Edite o arquivo .env
nano .env

# Adicione uma secret key segura:
FLASK_SECRET_KEY=minha-secret-key-muito-segura-aqui
```

**IMPORTANTE**: Nunca use a secret key padrão em produção!

### Características de Segurança

- ✅ **Validação de arquivos**: Verificação de tipo, tamanho e conteúdo
- 🔍 **Detecção de PII**: Identificação automática de dados pessoais
- 📋 **Auditoria completa**: Log de todas as ações realizadas
- 🔐 **Hash de arquivos**: Integridade verificada por SHA-256
- ⏱️ **Controle de tempo**: Timeout configurável por análise

### Sistema de Logging

O sistema registra automaticamente:
- Início e fim de análises
- Validação de arquivos
- Erros e exceções
- Uso de recursos
- Ações dos agentes

Logs disponíveis em: `logs/auditoria_academica.jsonl`

## ⚙️ Configuração Avançada

### Variáveis de Ambiente

```bash
# Configurações básicas
export SAPIENS_ENV=producao
export SAPIENS_LOG_LEVEL=INFO

# Configurações de segurança
export SAPIENS_MAX_FILE_SIZE=100MB
export SAPIENS_ENABLE_PII_DETECTION=true

# Configurações de modelo
export OPENAI_API_KEY=sua-chave-aqui
export SAPIENS_DEFAULT_MODEL=gpt-4
```

### Arquivos de Configuração

- `config/agents.yaml`: Configurações detalhadas dos agentes
- `config/logging_config.yaml`: Configurações de auditoria
- `.env`: Variáveis de ambiente locais

## 📊 Características Técnicas

### Arquitetura de Agentes

| Agente | Especialidade | Modelo | Ferramentas |
|--------|--------------|--------|-------------|
| **Gerente Orquestrador** | Coordenação geral | Llama 3.3 8B | FileRead, ScrapeWebsite, Validação |
| **Análise Descritiva** | Estatísticas básicas | Llama 3.3 8B | Statistical, CSV Processor |
| **Análise Diagnóstica** | Correlações e causas | Nemotron Nano 9B | Statistical, FileRead |
| **Análise Preditiva** | Previsões futuras | Llama 3.3 8B | Statistical, CSV Processor |
| **Análise Prescritiva** | Recomendações | Llama 3.3 8B | Statistical, FileRead |

### Tecnologias Utilizadas

- **Framework Principal**: CrewAI 0.177+
- **Interface Web**: Flask 3.0+
- **Processamento de Dados**: Pandas, NumPy, SciPy
- **Validação de Arquivos**: python-magic
- **Auditoria**: Logging estruturado com rotação
- **Frontend**: Bootstrap 5.3, jQuery

### Requisitos de Sistema

- **Sistema Operacional**: Linux/macOS/Windows
- **Memória RAM**: Mínimo 2GB, recomendado 4GB+
- **Armazenamento**: 1GB disponível
- **Rede**: Conexão para modelos de IA externos

## 🤝 Suporte e Contribuição

### Como Obter Ajuda

- 📖 **Documentação**: [Wiki do Projeto](https://github.com/seu-repo/wiki)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/seu-repo/discussions)
- 🐛 **Reportar Bugs**: [Issues](https://github.com/seu-repo/issues)
- 📧 **Contato Direto**: fabricio.silva.santos@example.com

### Diretrizes para Contribuição

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Tipos de Contribuição Bem-vinda

- 🔧 **Bug fixes**
- ✨ **Novas funcionalidades**
- 📚 **Melhorias na documentação**
- 🧪 **Testes adicionais**
- 🎨 **Melhorias na interface**

## 🔧 Troubleshooting

### Problemas Comuns e Soluções

#### ❌ "python: comando não encontrado"
```bash
# Use python3 explicitamente
python3 start_sapiens.py --web

# Ou instale python3-is-python3
sudo apt-get install python-is-python3  # Ubuntu/Debian
```

#### ❌ "ModuleNotFoundError"
```bash
# Reinstale as dependências
python3 -m pip install -e .

# Ou use o script de instalação
./install_sapiens.sh
```

#### ❌ "Arquivo .env não encontrado"
```bash
# Criar arquivo .env automaticamente
cp .env.example .env

# Configure sua OPENAI_API_KEY no arquivo .env
```

#### ❌ "Porta já em uso"
```bash
# Use uma porta diferente
python3 start_sapiens.py --web --port 8080
```

#### ❌ "Erro de permissão"
```bash
# Corrija permissões dos scripts
chmod +x start_sapiens.py install_sapiens.sh

# Execute com sudo se necessário (não recomendado)
sudo python3 start_sapiens.py --web
```

#### ❌ "OPENAI_API_KEY não configurada"
```bash
# Edite o arquivo .env
nano .env

# Adicione sua chave:
# OPENAI_API_KEY=sua-chave-aqui
```

### Verificar Instalação

```bash
# Verificar status do sistema
python3 start_sapiens.py --status

# Verificar dependências Python
python3 -c "import crewai, flask, pandas; print('✅ OK')"

# Verificar arquivos essenciais
ls -la src/Sapiens_MultiAgente/
```

### Obter Ajuda

```bash
# Ver todas as opções do launcher
python3 start_sapiens.py --help

# Ver logs detalhados
tail -f logs/sapiens_academico.log
## 🚀 Deploy no Vercel (Produção Serverless)

O SAPIENS foi adaptado para funcionar perfeitamente no Vercel como aplicação serverless.

### Pré-requisitos para Vercel

- Conta no [Vercel](https://vercel.com)
- GitHub conectado ao Vercel
- OpenAI API Key configurada

### Configuração das Variáveis de Ambiente

Configure estas variáveis no dashboard do Vercel (Project Settings > Environment Variables):

```bash
# Configurações obrigatórias
OPENAI_API_KEY=sua-chave-openai-aqui
FLASK_SECRET_KEY=sua-chave-secreta-muito-segura-aqui

# Configurações de produção
SAPIENS_ENV=producao
SAPIENS_DEBUG=false
FLASK_ENV=producao
FLASK_DEBUG=false

# Configurações serverless
UPLOAD_FOLDER=/tmp/uploads
LOGS_FOLDER=/tmp/logs
TEMP_FOLDER=/tmp/temp
```

⚠️ **Importante sobre FLASK_SECRET_KEY:**
- Gere uma chave secreta forte e única
- Nunca use a mesma chave em produção e desenvolvimento
- Se não definida, o sistema gerará uma automaticamente (menos seguro)

### Deploy Automático

1. **Conecte o repositório no Vercel**
   ```bash
   # O Vercel detectará automaticamente a configuração
   # baseada no arquivo vercel.json
   ```

2. **Configure as variáveis de ambiente**
   - Acesse o dashboard do Vercel
   - Vá em Project Settings > Environment Variables
   - Adicione todas as variáveis listadas acima

3. **Deploy automático**
   - Faça push das alterações para o GitHub
   - O Vercel fará deploy automaticamente

### Arquivos Importantes para Vercel

- `vercel.json` - Configuração do build e rotas
- `api/index.py` - Ponto de entrada serverless
- `requirements.txt` - Dependências para produção
- `vercel.env.example` - Exemplo de configuração

### Limitações do Ambiente Serverless

⚠️ **Importante**: Algumas funcionalidades foram adaptadas para funcionar em ambiente serverless:

- **Processamento síncrono**: Análises são processadas imediatamente (não em background)
- **Armazenamento temporário**: Arquivos são armazenados em `/tmp` (limpeza automática)
- **Análises simultâneas**: Limitado a 1 análise por vez
- **Timeout**: Máximo de 10 minutos por análise

### URL da Aplicação

Após o deploy, sua aplicação estará disponível em:
```
https://seu-projeto.vercel.app
```

### Monitoramento e Logs

- Use o comando `vercel logs` para ver logs da aplicação
- Configure alertas no dashboard do Vercel
- Monitore uso da API no dashboard do OpenAI

### Solução de Problemas

**Erro comum: Module not found**
```bash
# Certifique-se de que o requirements.txt está correto
# e que todas as dependências estão listadas
```

**Erro de timeout**
- Reduza a complexidade da análise
- Use tópicos de pesquisa mais específicos
- Considere dividir análises grandes em partes menores

**Problemas de memória**
- Otimize o tamanho dos arquivos de entrada
- Use apenas arquivos essenciais para análise

### Suporte

Para problemas específicos do deploy no Vercel:
1. Verifique os logs: `vercel logs --follow`
2. Teste localmente: `python3 api/index.py`
3. Consulte a [documentação do Vercel](https://vercel.com/docs)

---



Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 🙏 Agradecimentos

- **CrewAI Team** pelo framework excepcional
- **OpenAI** pelos modelos de linguagem
- **NVIDIA** pelo modelo Nemotron
- **Meta** pelo modelo Llama
- **Comunidade acadêmica** pela inspiração e feedback

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!**

<div align="center">
  <p><strong>Desenvolvido com ❤️ para a comunidade acadêmica</strong></p>
  <p>SAPIENS - Transformando dados em conhecimento desde 2025</p>
</div>
