Verifique se todas as variáveis de ambiente necessárias para o SAPIENS estão configuradas.

Rode o seguinte comando e mostre o resultado:

```bash
source .venv/bin/activate && python3 -c "
import os

required = {
    'OPENAI_API_KEY':   'Chave da API OpenRouter (obrigatória para LLM)',
    'OPENAI_API_BASE':  'Base URL do OpenRouter (ex: https://openrouter.ai/api/v1)',
    'FLASK_SECRET_KEY': 'Chave secreta Flask para sessões',
}
optional = {
    'SAPIENS_ADMIN_PASSWORD': 'Senha do admin (padrão: sapiens@2025)',
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
    val = os.getenv(var, '(usando padrão)')
    print(f'  ℹ️   {var} = {val}')

print()
print('Resultado:', '✅ Ambiente OK' if ok else '❌ Configure as variáveis faltando no arquivo .env')
"
```

Se houver variáveis obrigatórias faltando, explique como configurá-las no arquivo `.env`.
