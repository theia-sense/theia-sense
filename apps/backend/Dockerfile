# --- Build Stage ---
FROM python:3.12-slim AS builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./apps/backend/requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

COPY ./packages/ml-models ./packages/ml-models
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -e ./packages/ml-models

# --- Final Stage ---
FROM python:3.12-slim

WORKDIR /code

COPY --from=builder /usr/src/app/wheels /wheels

RUN pip install --no-cache /wheels/*

COPY ./apps/backend/app /code/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]