import asyncio
import logging
import sys
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import schemas
from .config import (
    ML_SERVICE_BASE_URL,
    ML_SERVICE_URL_ANNOTATE,
    ML_SERVICE_URL_THRESHOLD,
    settings,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

api_client: dict[str, httpx.AsyncClient] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting backend service...")

    headers = {"User-Agent": "Theia-Backend/1.0"}
    if settings.hf_token:
        headers["Authorization"] = f"Bearer {settings.hf_token}"
        logger.info("HF token configured for ML service auth")
    else:
        logger.info("No HF token set, using direct ML service connection")

    client = httpx.AsyncClient(
        timeout=settings.ml_service_timeout,
        headers=headers,
        follow_redirects=True,
    )
    api_client["client"] = client

    try:
        logger.info(f"Testing ML service at {ML_SERVICE_BASE_URL}")
        resp = await client.get(f"{ML_SERVICE_BASE_URL}/")
        if resp.status_code == 200:
            logger.info(f"ML service reachable: {resp.json()}")
        else:
            logger.warning(f"ML service returned {resp.status_code}")
    except Exception as e:
        logger.error(f"Cannot reach ML service: {e}")

    yield

    logger.info("Shutting down...")
    await client.aclose()


app = FastAPI(title="Theia API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


def _validate_file(file: UploadFile) -> bool:
    try:
        if hasattr(file, "size") and file.size is not None and file.size > settings.max_file_size:
            logger.warning(f"File too large: {file.filename} ({file.size} bytes)")
            return False
        if file.filename:
            ext = Path(file.filename).suffix.lower()
            if ext not in settings.allowed_extensions:
                logger.warning(f"Invalid extension: {file.filename} ({ext})")
                return False
        if file.content_type and not file.content_type.startswith("image/"):
            logger.warning(f"Invalid MIME type: {file.filename} ({file.content_type})")
            return False
        return True
    except Exception as e:
        logger.error(f"Validation error for {file.filename}: {e}")
        return False


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled {type(exc).__name__}: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "type": type(exc).__name__},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.get("/health")
async def health_check():
    try:
        resp = await api_client["client"].get(f"{ML_SERVICE_BASE_URL}/", timeout=10.0)
        ml_ok = resp.status_code == 200
        ml_body = resp.json() if ml_ok else None
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "ml_service_connected": False, "reason": str(e)},
        )

    return {
        "status": "healthy" if ml_ok else "degraded",
        "ml_service_connected": ml_ok,
        "ml_service_status": ml_body,
        "version": "0.1.0",
    }


@app.get("/")
async def root():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/predict/", response_model=list[schemas.BackendResponse])
async def predict(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    logger.info(f"Processing {len(files)} files")

    image_data = []
    for file in files:
        if not _validate_file(file):
            continue
        try:
            contents = await file.read()
            image_data.append((file.filename, contents, file.content_type))
        except Exception as e:
            logger.error(f"Error reading {file.filename}: {e}")

    if not image_data:
        raise HTTPException(status_code=400, detail="No valid image files found.")

    batches = [image_data[i : i + settings.batch_size] for i in range(0, len(image_data), settings.batch_size)]

    async def _send_batch(batch):
        files_payload = [("files", (name, data, ct)) for name, data, ct in batch]
        try:
            resp = await api_client["client"].post(ML_SERVICE_URL_ANNOTATE, files=files_payload, timeout=300)
            resp.raise_for_status()
            return [
                schemas.BackendResponse(filename=item["filename"], tags=item.get("tags"), score=item.get("score"))
                for item in resp.json()
            ]
        except httpx.HTTPStatusError as e:
            logger.error(f"ML annotate error: {e.response.status_code}")
            raise HTTPException(status_code=e.response.status_code, detail=f"ML service error: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"ML service unreachable: {e}")
            raise HTTPException(status_code=503, detail="ML service unavailable")

    all_results = await asyncio.gather(*[_send_batch(b) for b in batches])
    flat = [r for batch in all_results for r in batch]

    # Apply threshold filtering (best-effort — fall back to unfiltered on failure)
    try:
        payload = [{"filename": r.filename, "tags": r.tags, "score": r.score} for r in flat]
        resp = await api_client["client"].post(
            ML_SERVICE_URL_THRESHOLD, json=payload, timeout=300.0,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        return [
            schemas.BackendResponse(filename=item["filename"], tags=item["tags"], score=item["score"])
            for item in resp.json()
        ]
    except Exception as e:
        logger.warning(f"Threshold filtering failed ({e}), returning unfiltered")
        return flat
