# =============================================================================
# SAPIENS — Plataforma Acadêmica Multiagente de Análise de Dados
# Build multi-stage: builder instala deps, runtime é a imagem final mínima.
# =============================================================================

# ── Stage 1: builder ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Dependências do sistema necessárias para compilação e python-magic
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libmagic1 \
        libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala uv para resolução rápida de dependências
RUN pip install --no-cache-dir uv

# Copia apenas os arquivos de dependências primeiro (cache de camadas)
COPY pyproject.toml ./
COPY src/ src/

# Cria venv isolado e instala dependências de produção
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python3 -e . --no-cache

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Dependências de runtime (sem -dev)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copia o venv do builder
COPY --from=builder /opt/venv /opt/venv

# Copia o código da aplicação
COPY src/ src/
COPY pyproject.toml ./

# Cria diretórios necessários em runtime
RUN mkdir -p uploads logs

# Usuário não-root para segurança
RUN useradd -m -u 1001 sapiens && chown -R sapiens:sapiens /app
USER sapiens

# Variáveis de ambiente padrão (sobrescrevem com docker run -e ou .env)
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=src/Sapiens_MultiAgente/web/app.py \
    SAPIENS_ENV=producao \
    WEB_HOST=0.0.0.0 \
    WEB_PORT=5000

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')"

CMD ["python", "-c", \
     "from Sapiens_MultiAgente.web.app import SapiensWebInterface; \
      import os; \
      SapiensWebInterface( \
          host=os.getenv('WEB_HOST','0.0.0.0'), \
          port=int(os.getenv('WEB_PORT',5000)), \
          debug=os.getenv('SAPIENS_DEBUG','false').lower()=='true' \
      ).run()"]
