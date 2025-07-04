FROM python:3.12-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/code/.hf_cache

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY ./apps/ml-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./apps/ml-service/new_onnx_models ./new_onnx_models

COPY ./apps/ml-service/app ./app

RUN python -c "from transformers import CLIPProcessor; CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')"

RUN useradd -m appuser && \
    chown -R appuser:appuser /code
USER appuser

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8001/ || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]