Execute o lint do projeto SAPIENS com flake8 e mostre o resultado.

Rode o seguinte comando:

```bash
source .venv/bin/activate && flake8 src/ --max-line-length=120 --exclude=__pycache__ --extend-ignore=E501,W503,E203
```

Se não houver saída, o código está limpo. Se houver erros, liste-os e corrija automaticamente.
