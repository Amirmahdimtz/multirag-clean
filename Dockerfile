FROM python:3.10-slim-bookworm@sha256:2559be987fd64d61badbdafd303ea58a9ccab36d6c3c08bce219e762177d2eca AS builder

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN python -m venv "${VIRTUAL_ENV}"

WORKDIR /build

COPY requirements.txt .

# Install a CPU-only PyTorch wheel. The FastAPI container does not need GPU
# access; GPU execution is isolated in the vLLM service.
RUN pip install --upgrade pip setuptools wheel \
    && pip install --index-url https://download.pytorch.org/whl/cpu torch==2.6.0 \
    && pip install -r requirements.txt


FROM python:3.10-slim-bookworm@sha256:2559be987fd64d61badbdafd303ea58a9ccab36d6c3c08bce219e762177d2eca AS runtime

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HOME=/home/multirag

RUN groupadd --gid 10001 multirag \
    && useradd --uid 10001 --gid multirag --create-home multirag

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

COPY --chown=multirag:multirag . .

RUN mkdir -p /app/storage /models/embedding /models/torch \
    && chown -R multirag:multirag /app/storage /models /home/multirag

USER multirag

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=180s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health/', timeout=3)"

CMD ["python", "main.py"]
