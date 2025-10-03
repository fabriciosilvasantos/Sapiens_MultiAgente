#!/bin/bash

# Script para publicar SAPIENS no GitHub
echo "🚀 Iniciando publicação do SAPIENS no GitHub..."

# Verificar se o usuário está autenticado
if ! gh auth status >/dev/null 2>&1; then
    echo "🔐 Você precisa se autenticar no GitHub primeiro:"
    echo "gh auth login"
    echo ""
    echo "Após a autenticação, execute este script novamente."
    exit 1
fi

# Solicitar nome de usuário do GitHub
read -p "Digite seu nome de usuário do GitHub: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ Nome de usuário não pode estar vazio!"
    exit 1
fi

# Verificar se o repositório já existe no GitHub
if gh repo view "$GITHUB_USERNAME/Sapiens_MultiAgente" >/dev/null 2>&1; then
    echo "✅ Repositório já existe no GitHub!"
else
    echo "📁 Criando repositório no GitHub..."
    gh repo create "$GITHUB_USERNAME/Sapiens_MultiAgente" --public --source=. --remote=origin --push

    if [ $? -eq 0 ]; then
        echo "✅ Repositório criado e código enviado com sucesso!"
        echo "🌐 URL do repositório: https://github.com/$GITHUB_USERNAME/Sapiens_MultiAgente"
    else
        echo "❌ Erro ao criar repositório. Você pode criá-lo manualmente em:"
        echo "https://github.com/new"
        echo "Nome do repositório: Sapiens_MultiAgente"
        echo ""
        echo "Após criar manualmente, configure o remote e faça push:"
        echo "git remote add origin https://github.com/$GITHUB_USERNAME/Sapiens_MultiAgente.git"
        echo "git push -u origin main"
    fi
fi

echo ""
echo "🎉 Processo de publicação concluído!"
echo "📖 Não se esqueça de atualizar o README.md com a URL correta do repositório."
