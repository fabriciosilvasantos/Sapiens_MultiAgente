# SAPIENS — Plataforma de Análise de Dados Acadêmicos

![Versão](https://img.shields.io/badge/SAPIENS-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Testes](https://img.shields.io/badge/testes-423%20passando-brightgreen)
![Licença](https://img.shields.io/badge/licença-MIT-lightgrey)

> Transforme dados acadêmicos em relatórios completos com um clique — sem precisar saber programação.

Desenvolvido na **Universidade Estadual do Norte Fluminense Darcy Ribeiro (UENF)**, o SAPIENS foi criado para que gestores, professores e pesquisadores possam obter análises aprofundadas de dados institucionais de forma simples, rápida e confiável.

---

## O que é o SAPIENS?

O SAPIENS é uma plataforma que usa **inteligência artificial** para analisar dados acadêmicos automaticamente. Você carrega um arquivo com seus dados (planilha, PDF ou documento), faz uma pergunta e o sistema entrega um relatório completo com:

- O que aconteceu nos seus dados
- Por que aconteceu
- O que pode acontecer no futuro
- O que você deve fazer
- Como sua instituição se compara com a média nacional (INEP/MEC)

Tudo isso sem precisar conhecer estatística ou programação.

---

## Para quem é o SAPIENS?

| Perfil | Como o SAPIENS ajuda |
|--------|----------------------|
| **Reitores e diretores** | Relatórios prontos para tomada de decisão estratégica |
| **Coordenadores de curso** | Entender evasão, reprovação e desempenho dos alunos |
| **Professores pesquisadores** | Análises estatísticas com rigor metodológico |
| **Servidores da área acadêmica** | Processar grandes volumes de dados sem esforço manual |
| **Gestores de políticas educacionais** | Comparar indicadores com benchmarks nacionais |

---

## Como funciona?

O SAPIENS funciona como uma equipe de especialistas virtuais trabalhando ao mesmo tempo:

```
Você envia os dados e a pergunta
          ↓
  O sistema valida e processa os dados
          ↓
  ┌─────────────────────────────────────────────┐
  │  Descritiva  │  Diagnóstica  │  Preditiva   │
  │  Prescritiva │  Benchmarks   │  Análise de  │
  │              │  Nacionais    │  Documentos  │
  └─────────────────────────────────────────────┘
      (todos trabalhando ao mesmo tempo)
          ↓
  Revisão de qualidade científica
          ↓
  Relatório final consolidado
```

O sistema conta com **8 especialistas virtuais** — cada um responde uma pergunta diferente:

| Especialista | Pergunta respondida |
|---|---|
| Gerente Orquestrador | Os dados são válidos? O que precisa ser analisado? |
| Análise Descritiva | O que aconteceu nos dados? |
| Análise Diagnóstica | Por que aconteceu? |
| Análise Preditiva | O que pode acontecer? |
| Análise Prescritiva | O que devemos fazer? |
| Benchmarks Nacionais | Como estamos em relação ao Brasil? (INEP/IBGE/MEC) |
| Análise de Documentos | O que dizem os textos e relatórios? |
| Revisor de Qualidade | A análise tem embasamento científico? (nota 0–100) |

---

## Exemplo real — UENF 2020 a 2025

**Dados:** Planilha com registros de 132 alunos, 12 cursos, 5 centros.

**Pergunta feita:** *"Analise a evasão estudantil por curso no período 2020–2025."*

**Resultado obtido em minutos:**

- A evasão caiu **50%** (de 212 para 106 alunos evadidos por semestre)
- A principal causa identificada: expansão das bolsas de assistência estudantil (+45%)
- O CCT concentra **59,6%** de toda a evasão da UENF
- A UENF **superou a média nacional** de evasão: 18,9% vs 26,4% (INEP 2023)
- Projeção para 2026: taxa abaixo de **15%** se a tendência continuar
- Recomendações práticas priorizadas por urgência

---

## Principais funcionalidades

- **Upload simples** — aceita planilhas (.csv, .xlsx), PDFs e documentos Word
- **Relatório em português** — linguagem clara, tabelas e gráficos incluídos
- **Comparação nacional** — benchmarks automáticos do INEP, IBGE, CAPES e MEC
- **Análise de documentos** — extrai informações de relatórios e textos
- **Gráficos automáticos** — visualizações geradas junto com o relatório
- **Revisão metodológica** — o sistema avalia a própria qualidade da análise (nota 0–100)
- **Progresso em tempo real** — acompanhe cada etapa enquanto ela acontece
- **Troca de modelo de IA** — escolha entre diferentes modelos gratuitos via painel
- **Histórico de análises** — todas as análises ficam salvas para consulta posterior

---

## Como usar

### 1. Acesse o sistema
Abra o navegador e acesse o endereço fornecido pelo seu administrador (ex: `http://servidor:4000`).

### 2. Faça login
Entre com as credenciais fornecidas pelo administrador do sistema.

### 3. Inicie uma análise
1. Clique em **"Nova Análise"**
2. Escreva o tópico de pesquisa (ex: *"Evasão estudantil 2020–2024"*)
3. Faça o upload do arquivo de dados
4. Clique em **"Iniciar Análise"**

### 4. Acompanhe o progresso
O painel mostra em tempo real quais especialistas já terminaram o trabalho.

### 5. Baixe o relatório
Quando concluído, o relatório completo fica disponível para download.

---

## Formatos de arquivo aceitos

| Formato | Extensão | Uso |
|---------|----------|-----|
| Planilha Excel | `.xlsx`, `.xls` | Dados tabulares (alunos, notas, matrículas) |
| CSV | `.csv` | Dados exportados de sistemas acadêmicos |
| PDF | `.pdf` | Relatórios, atas, documentos institucionais |
| Word | `.docx` | Relatórios e documentos de texto |

---

## Segurança e privacidade

- Acesso protegido por **login e senha**
- Senhas armazenadas com **criptografia** (não são salvas em texto simples)
- Registro completo de todas as ações em **log de auditoria**
- Proteção contra upload de arquivos maliciosos
- Os dados ficam armazenados **apenas no seu servidor institucional**

---

## Instalação (para o administrador de TI)

### Pré-requisitos
- Python 3.10 ou superior
- Servidor Linux/Windows com acesso à internet
- Chave de API do [OpenRouter](https://openrouter.ai) (gratuita)

### Passos

```bash
# 1. Baixar o projeto
git clone https://github.com/fabriciosilvasantos/Sapiens_MultiAgente.git
cd Sapiens_MultiAgente

# 2. Criar ambiente virtual e instalar dependências
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows
pip install -e .

# 3. Configurar o ambiente
cp .env.example .env
# Editar .env com sua chave de API e senha do administrador

# 4. Iniciar o servidor
python -m Sapiens_MultiAgente.web.app
```

Acesse: `http://127.0.0.1:4000`

### Variáveis de ambiente essenciais (`.env`)

```
OPENAI_API_KEY=sua-chave-openrouter    # Chave da API de IA (gratuita no OpenRouter)
OPENAI_API_BASE=https://openrouter.ai/api/v1
FLASK_SECRET_KEY=uma-senha-segreta-qualquer
SAPIENS_ADMIN_PASSWORD=senha-do-admin
```

---

## Modelos de IA disponíveis

O SAPIENS usa modelos de linguagem do [OpenRouter](https://openrouter.ai). O modelo pode ser trocado pelo administrador sem reiniciar o sistema — cada especialista pode usar um modelo diferente, otimizado para o seu tipo de tarefa:

| Modelo | Custo | Indicado para |
|--------|-------|---------------|
| **DeepSeek R1** | **Gratuito** | Raciocínio científico — diagnóstica, preditiva, revisão |
| **Llama 3.3 70B** | **Gratuito** | Orquestração e relatório final (86% MMLU) |
| **Gemma 4 31B** (Google) | **Gratuito** | Análise textual em português (256K contexto) |
| **Gemma 4 26B MoE** (Google) | **Gratuito** | Padrão — rápido, fontes externas |
| **Mistral Small 3 24B** | **Gratuito** | Alternativa geral (81% MMLU) |
| **Llama 3.3 8B** | **Gratuito** | Opção leve e rápida |
| OpenRouter Auto | Pode ter custo | Melhor modelo disponível automaticamente |

Para trocar o modelo, acesse `POST /api/config/llm` ou edite `config/llm_config.yaml`.

### Disponibilidade garantida

Se o OpenRouter estiver indisponível (sobrecarga, manutenção), o SAPIENS ativa automaticamente o **Groq** como fallback — 10× mais rápido e sem interrupção para o usuário. Configure `GROQ_API_KEY` no `.env` para habilitar.

---

## Monitoramento da plataforma

O painel `/status` exibe em tempo real:
- Uso de CPU e memória do servidor
- Total de análises realizadas / concluídas / com erro
- Taxa de sucesso histórica

---

## Perguntas frequentes

**O SAPIENS precisa de conexão com a internet?**
Sim, para acessar os modelos de IA do OpenRouter. Os seus dados nunca saem do servidor institucional — apenas o texto das perguntas e respostas é enviado à API.

**Qual o tamanho máximo de arquivo?**
100 MB por padrão (configurável pelo administrador).

**Quantas análises posso fazer ao mesmo tempo?**
Até 3 análises simultâneas por padrão (configurável).

**Os relatórios ficam salvos?**
Sim, todas as análises ficam registradas no banco de dados do sistema e podem ser consultadas a qualquer momento pelo usuário que as criou.

**O sistema é gratuito?**
O SAPIENS é open-source (MIT). Os modelos de IA no tier gratuito do OpenRouter também são gratuitos, sem custo por análise.

---

## Suporte

- **Problemas / sugestões:** [github.com/fabriciosilvasantos/Sapiens_MultiAgente/issues](https://github.com/fabriciosilvasantos/Sapiens_MultiAgente/issues)
- **Contato:** fabricio@uenf.br

---

## Licença

MIT License — uso livre para fins acadêmicos, institucionais e comerciais.

---

## Agradecimentos

- **CrewAI** — framework de orquestração de agentes de IA
- **Meta / Google / Mistral** — modelos de linguagem open-source
- **OpenRouter** — infraestrutura de acesso a modelos de IA
- **INEP / IBGE / CAPES / MEC** — dados públicos educacionais brasileiros
- **Comunidade acadêmica da UENF** — inspiração, testes e feedback

---

<div align="center">
  <strong>SAPIENS v1.0.0 — Desenvolvido na UENF</strong><br>
  Transformando dados acadêmicos em conhecimento estratégico
</div>
