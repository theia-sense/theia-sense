FROM python:3.12-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY ./apps/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./apps/backend/app ./app

ARG ML_SERVICE_URL_ARG="http://ml-service:8001/annotate/"
ENV ML_SERVICE_URL=${ML_SERVICE_URL_ARG}

RUN useradd -m appuser && \
    chown -R appuser:appuser /code
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]