Inicie o servidor Flask do SAPIENS em modo desenvolvimento.

Rode o seguinte comando (em background para não bloquear):

```bash
source .venv/bin/activate && FLASK_SECRET_KEY=dev-key python -c "
from src.Sapiens_MultiAgente.web.app import SapiensWebInterface
app = SapiensWebInterface(host='127.0.0.1', port=5000, debug=True).create_app()
app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
"
```

Informe ao usuário que o servidor estará disponível em http://127.0.0.1:5000
