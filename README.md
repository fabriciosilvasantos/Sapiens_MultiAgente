# Projeto SAPIENS — Plataforma Acadêmica Multiagente de Análise de Dados

![SAPIENS Logo](https://img.shields.io/badge/SAPIENS-2.0.0-blue)
![Python Version](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

O **SAPIENS** é uma plataforma avançada que utiliza orquestração de agentes de IA para executar análises de dados complexas — descritivas, diagnósticas, preditivas e prescritivas — com foco acadêmico.

---

## Introdução e Visão Geral

O sistema foi concebido como **Software Livre**, operando em um servidor dedicado para garantir segurança, desempenho e autonomia institucional. Sua arquitetura multiagente foi projetada para automatizar e simplificar todo o processo de extração de insights a partir de dados acadêmicos e administrativos.

No centro da aplicação está um **Agente Gerente (Orquestrador)**, que atua como um Analista de Dados Sênior virtual, coordenando agentes especializados responsáveis por etapas como limpeza, transformação, escolha de metodologias, execução de análises e elaboração de relatórios.

O SAPIENS resolve um problema recorrente nas universidades: a dificuldade de realizar análises de dados robustas e profundas, essenciais para decisões administrativas estratégicas e para o avanço da pesquisa científica.

---

## Objetivo do Produto

O objetivo principal é **fortalecer a gestão universitária baseada em evidências** e **acelerar a pesquisa científica**, oferecendo uma ferramenta poderosa, prática e acessível.

A plataforma permitirá que gestores, pesquisadores e alunos obtenham respostas rápidas e confiáveis para suas necessidades analíticas, automatizando processos críticos — como preparação de dados, seleção de técnicas, execução de análises e apresentação dos resultados — sem exigir conhecimento avançado em ciência de dados.



### Potencial de Uso e Impacto

Esta seção detalha o valor estratégico que a plataforma SAPIENS entrega à comunidade acadêmica.

#### Potencial de Uso

O SAPIENS atende aos dois pilares centrais de uma universidade: a gestão e a pesquisa.

●**Na Gestão Acadêmica**: A plataforma se torna uma ferramenta essencial para pró-reitorias e
coordenações, permitindo que gestores tomem decisões estratégicas baseadas em evidências de
forma ágil, respondendo a perguntas complexas sobre evasão, alocação de recursos e planejamento
de matrículas.

●**Na Pesquisa Científica**: Para pesquisadores e alunos de pós-graduação, o SAPIENS acelera
drasticamente o ciclo da pesquisa, permitindo a análise de grandes volumes de dados experimentais, a validação de hipóteses e a análise de dados de teses e dissertações com rigor estatístico, mesmo para
não especialistas.

#### Economia de Tempo

A economia de tempo é um dos benefícios mais diretos da plataforma. O SAPIENS transforma tarefas que
levariam semanas de trabalho manual em processos que podem ser concluídos em horas ou
minutos, ao automatizar as etapas mais demoradas da análise:

1.**Preparação e Limpeza dos Dados**: Automatiza a tarefa que consome até 80% do tempo de um
analista.

2.**Seleção da Metodologia**: Elimina horas de dúvida e pesquisa ao decidir automaticamente o método
de análise mais adequado.

3.**Geração de Relatórios**: Entrega instantaneamente um relatório completo com visualizações e textos
explicativos.

#### Impacto no Fator Humano

O SAPIENS não visa substituir o analista humano, mas sim potencializar sua capacidade intelectual.

1.**Democratização da Análise**: Reduz a necessidade de conhecimento técnico especializado,
permitindo que especialistas de domínio (professores, pesquisadores) realizem análises complexas de
forma autônoma, eliminando gargalos e dependências.

2.**Foco no Estratégico, Não no Operacional**: Ao automatizar as tarefas repetitivas e operacionais, a
plataforma libera o profissional para se concentrar no que realmente importa: interpretar os
resultados, fazer novas perguntas, debater os insights e tomar decisões informadas. O esforço
humano é deslocado da tarefa mecânica para a análise crítica e estratégica, onde a inteligência
humana é insubstituível.


### O Processo de Análise no SAPIENS

Esta seção detalha como a plataforma SAPIENS aborda as etapas fundamentais do processo de análise de
dados.

- **Fazendo a Pergunta**: O usuário insere sua pergunta em linguagem natural.

- **Coleta dos Dados**: O usuário faz o upload de seus arquivos de dados ou conecta-se a bancos de
dados.

- **Exploração, Preparação e Limpeza**: O Agente Gerente automatiza a limpeza e preparação dos dados.

- **Análise dos Dados**: O Agente Gerente interpreta a pergunta e delega a tarefa ao Agente Especialista
apropriado.

- **Apresentando os Resultados**: O Agente Gerente traduz a análise técnica em uma apresentação clara
e acionável.



### Os Agentes Especializados

O sistema é composto por uma equipe de agentes com papéis bem definidos em `src/Sapiens_MultiAgente/config/agents.yaml`:

- **Gerente Orquestrador**: O "guardião" do rigor científico. Sua principal função é validar se os dados fornecidos são reais e impedir alucinações ou simulações não solicitadas.
- **Especialista em Análise Descritiva**: Foca em "O que aconteceu?", gerando estatísticas e tendências.
- **Especialista em Análise Diagnóstica**: Foca em "Por que aconteceu?", buscando correlações e causas (usa o modelo Nemotron).
- **Especialista em Análise Preditiva**: Foca em "O que pode acontecer?", criando modelos de previsão.
- **Especialista em Análise Prescritiva**: Foca em "O que devemos fazer?", gerando recomendações acionáveis.

###  Fluxo de Trabalho

1. **Entrada**: O usuário faz upload de arquivos ou fornece links via interface Web.
2. **Validação**: O sistema valida a segurança dos arquivos e o Gerente Orquestrador verifica se há dados reais suficientes.
3. **Execução**: A análise roda em *background* (thread separada no Flask), onde os agentes processam os dados sequencialmente conforme configurado em `tasks.yaml`.
4. **Auditoria**: Todas as ações são registradas pelo `AcademicLogger` para garantir rastreabilidade.
5. **Resultado**: Um relatório final consolidado é gerado e apresentado ao usuário.



### Características Principais

- **🤖 Agentes Especializados**: 5 agentes especializados em diferentes tipos de análise
- **🔒 Segurança Avançada**: Validação rigorosa de arquivos e auditoria completa
- **🌐 Interface Web**: Interface moderna e responsiva para interação
- **📊 Análise Completa**: Descritiva, diagnóstica, preditiva e prescritiva
- **📋 Auditoria Detalhada**: Sistema completo de logging para rastreabilidade
- **🔧 Configuração Flexível**: Estrutura configurável para diferentes ambientes

### Tipos de Análise

| Tipo | Descrição | Agente Especialista |
|------|-----------|-------------------|
| **Descritiva** | O que aconteceu? | Estatísticas básicas e tendências |
| **Diagnóstica** | Por que aconteceu? | Causas e correlações |
| **Preditiva** | O que pode acontecer? | Previsões futuras |
| **Prescritiva** | O que devemos fazer? | Recomendações acionáveis |


### Arquitetura e Tecnologias

O projeto segue uma arquitetura modular bem definida, separando a lógica de inteligência artificial da interface do usuário.

- **Core (IA & Agentes)**: Utiliza o framework **CrewAI** para orquestrar 5 agentes especializados.
- **Interface Web**: Construída com **Flask**, oferecendo upload de arquivos e visualização de progresso.
- **Modelos de IA**: Configurado para usar modelos abertos de alta performance via API (Llama 3.3 8B e Nemotron Nano 9B).
- **Processamento de Dados**: Pandas, NumPy e ferramentas customizadas para leitura de CSV, Excel, PDF e DOCX.
- **Infraestrutura**: Preparado para deploy serverless no **Vercel** ou execução local.




### 🛠️ Instalação e Configuração

Para instruções detalhadas sobre instalação, configuração e deploy, consulte o arquivo [INSTALL.md](INSTALL.md).

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

## Estrutura do Projeto

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



## 📊 Características Técnicas

### Arquitetura de Agentes

| Agente | Especialidade | Modelo | Ferramentas |
|--------|--------------|--------|-------------|
| **Gerente Orquestrador** | Coordenação geral | Llama 3.3 8B | FileRead, ScrapeWebsite, Validação |
| **Análise Descritiva** | Estatísticas básicas | Llama 3.3 8B | Statistical, CSV Processor |
| **Análise Diagnóstica** | Correlações e causas | Llama 3.3 8B | Statistical, FileRead |
| **Análise Preditiva** | Previsões futuras | Llama 3.3 8B | Statistical, CSV Processor |
| **Análise Prescritiva** | Recomendações | Llama 3.3 8B | Statistical, FileRead |

### Tecnologias Utilizadas

- **Framework Principal**: CrewAI 0.177+
- **Interface Web**: Flask 3.0+
- **Processamento de Dados**: Pandas, NumPy, SciPy
- **Validação de Arquivos**: python-magic
- **Auditoria**: Logging estruturado com rotação
- **Frontend**: Bootstrap 5.3, jQuery



## 🤝 Suporte e Contribuição

### Como Obter Ajuda

- 📖 **Documentação**: [Wiki do Projeto](https://github.com/seu-repo/wiki)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/seu-repo/discussions)
- 🐛 **Reportar Bugs**: [Issues](https://github.com/seu-repo/issues)
- 📧 **Contato Direto**: fabricio.silva.santos@gmail.com

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
