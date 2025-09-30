#!/bin/bash

# =============================================================================
# SCRIPT DE INSTALAÇÃO - SAPIENS PLATAFORMA ACADÊMICA
# =============================================================================

set -e  # Parar em caso de erro

echo "🚀 SAPIENS - Instalação Automática"
echo "================================="

# Detectar comando Python
detect_python() {
    if command -v python3 &> /dev/null; then
        echo "python3"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
        if (( $(echo "$PYTHON_VERSION >= 3.10" | bc -l) )); then
            echo "python"
        else
            echo "python3"
        fi
    else
        echo "Erro: Nenhum comando Python encontrado!" >&2
        exit 1
    fi
}

PYTHON_CMD=$(detect_python)
echo "✅ Comando Python detectado: $PYTHON_CMD"

# Verificar versão do Python
echo "🔍 Verificando versão do Python..."
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "📦 Versão atual: $PYTHON_VERSION"

# Extrair major e minor version
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MAJOR" -eq 3 -a "$PYTHON_MINOR" -lt 10 ]; then
    echo "❌ Python 3.10+ é obrigatório! Versão atual: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Versão do Python compatível: $PYTHON_VERSION"

# Instalar dependências do sistema (se necessário)
echo "📦 Instalando dependências do sistema..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-venv python3-dev
elif command -v yum &> /dev/null; then
    sudo yum install -y python3-pip python3-devel
elif command -v brew &> /dev/null; then
    brew install python@3.10
fi

# Instalar/Atualizar pip
echo "📦 Atualizando pip..."
$PYTHON_CMD -m pip install --upgrade pip

# Instalar UV (se disponível)
if command -v curl &> /dev/null; then
    echo "🚀 Tentando instalar UV para instalação mais rápida..."
    curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null || echo "⚠️ UV não pôde ser instalado, continuando com pip..."
fi

# Instalar dependências do projeto
echo "📦 Instalando dependências do SAPIENS..."
if command -v uv &> /dev/null; then
    echo "🚀 Usando UV para instalação rápida..."
    uv pip install -e .
else
    echo "📦 Usando pip tradicional..."
    $PYTHON_CMD -m pip install -e .
fi

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo "⚙️ Criando arquivo .env..."
    cp .env.example .env
    echo "✅ Arquivo .env criado! Configure suas credenciais."
    echo "🔧 Edite o arquivo .env e adicione sua OPENAI_API_KEY"
else
    echo "✅ Arquivo .env já existe"
fi

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p logs
mkdir -p uploads
mkdir -p temp

# Verificar instalação
echo "🔍 Verificando instalação..."
if $PYTHON_CMD -c "import crewai, flask, pandas, numpy; print('✅ Todas as dependências instaladas com sucesso!')" 2>/dev/null; then
    echo "🎉 Instalação concluída com sucesso!"
else
    echo "⚠️ Algumas dependências podem não estar instaladas corretamente"
fi

# Instruções finais
echo ""
echo "🎯 Como usar o SAPIENS:"
echo ""
echo "1️⃣ Configure o arquivo .env:"
echo "   - Edite .env e adicione sua OPENAI_API_KEY"
echo ""
echo "2️⃣ Inicie a interface web:"
echo "   $PYTHON_CMD start_sapiens.py --web"
echo "   # ou"
echo "   $PYTHON_CMD start_sapiens.py"
echo ""
echo "3️⃣ Acesse no navegador:"
echo "   http://127.0.0.1:5000"
echo ""
echo "📚 Para mais informações, consulte o README.md"
echo ""
echo "✨ Instalação concluída! Bom trabalho com o SAPIENS!"