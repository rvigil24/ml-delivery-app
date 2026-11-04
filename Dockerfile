# syntax=docker/dockerfile:1
FROM python:3.12.14-slim@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f AS build
COPY --from=ghcr.io/astral-sh/uv:0.12.23@sha256:61d393e44e249f2e4b526b6c7ddcecce245946826e608e11c93ad4f5bba55b21 /uv /usr/local/bin/uv
WORKDIR /build
COPY pyproject.toml uv.lock README.md ./
# Exportar las versiones bloqueadas, excluyendo herramientas offline.
RUN uv export --quiet --frozen --no-dev --no-emit-project \
    --prune torch --prune pyspark --prune dask --prune matplotlib \
    --output-file requirements.txt \
    && uv venv /opt/venv \
    && uv pip install --python /opt/venv/bin/python --require-hashes -r requirements.txt
COPY backend/src backend/src
COPY ml/src ml/src
RUN uv pip install --python /opt/venv/bin/python --no-deps .

FROM python:3.12.14-slim@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f AS runtime
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN useradd --uid 10001 --create-home delivery
WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY infra/docker/init_mongo.py /app/init_mongo.py
USER delivery
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=6 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]
CMD ["uvicorn", "delivery.main:app", "--host", "0.0.0.0", "--port", "8000"]
