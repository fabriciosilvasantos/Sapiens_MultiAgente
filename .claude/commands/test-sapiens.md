Execute a suíte completa de testes do SAPIENS com relatório de cobertura.

Rode o seguinte comando e mostre o resultado completo:

```bash
source .venv/bin/activate && pytest tests/ -v --tb=short --cov=src/Sapiens_MultiAgente --cov-report=term-missing
```
