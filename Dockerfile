# ---- build stage ----
FROM python:3.11-slim AS builder

WORKDIR /app

COPY app/requirements.txt requirements.txt

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

# ---- runtime stage ----
FROM python:3.11-slim

WORKDIR /app

RUN useradd -m appuser

COPY --from=builder /opt/venv /opt/venv
COPY . .

ENV PATH="/opt/venv/bin:$PATH"

ENV PORT 8000

USER appuser

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
