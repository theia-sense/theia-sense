import io
import logging
import os
import sys
import traceback
from contextlib import asynccontextmanager
from typing import Any

import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
from transformers import CLIPProcessor

from . import schemas
from .config import settings
from .utils import assign_categories, load_tags_and_categories

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

TAG_LIST, TAG_TO_CATEGORIES = load_tags_and_categories(settings.categories_json_path)

ml_models: dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading ML assets...")

    for path in [settings.text_model_path, settings.vision_model_path, settings.aesthetic_model_path]:
        if not path.exists():
            raise FileNotFoundError(f"ONNX model not found: {path}")

    text_session = ort.InferenceSession(str(settings.text_model_path), providers=settings.providers)
    vision_session = ort.InferenceSession(str(settings.vision_model_path), providers=settings.providers)
    aesthetic_session = ort.InferenceSession(str(settings.aesthetic_model_path), providers=settings.providers)

    processor = CLIPProcessor.from_pretrained(settings.model_id)
    if isinstance(processor, tuple):
        processor = processor[0]

    text_inputs = processor(text=TAG_LIST, return_tensors="np", padding=True)
    onnx_text_inputs = {
        "input_ids": np.array(text_inputs["input_ids"]).astype(np.int64),
        "attention_mask": np.array(text_inputs["attention_mask"]).astype(np.int64),
    }
    text_outputs = text_session.run(None, onnx_text_inputs)
    tag_features = np.asarray(text_outputs[0])
    tag_features /= np.linalg.norm(tag_features, axis=-1, keepdims=True)

    ml_models.update({
        "text_session": text_session,
        "vision_session": vision_session,
        "aesthetic_session": aesthetic_session,
        "processor": processor,
        "tag_features": tag_features,
    })
    logger.info(f"Models loaded. Providers: {settings.providers}")

    yield

    logger.info("Shutting down ML service...")
    ml_models.clear()


app = FastAPI(
    title="Theia ML Service",
    version="0.3.0",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


def _models_ready() -> bool:
    return all(k in ml_models for k in ("vision_session", "processor", "tag_features"))


@app.get("/health")
async def health_check():
    if not _models_ready():
        return JSONResponse(status_code=503, content={"status": "unhealthy", "reason": "Models not loaded"})
    try:
        test_input = np.random.randn(1, 3, 224, 224).astype(np.float32)
        ml_models["vision_session"].run(None, {"pixel_values": test_input})
        return {"status": "healthy", "models_loaded": True}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(status_code=503, content={"status": "unhealthy", "reason": str(e)})


@app.get("/")
async def root():
    if not _models_ready():
        return {"status": "running", "models_loaded": False}
    return {"status": "running", "models_loaded": True}


@app.post("/threshold/", response_model=list[schemas.AnnotationResponse])
async def threshold_filter(data: list[schemas.AnnotationResponse]):
    """Filter images below a dynamic aesthetic score threshold (mean + std/2)."""
    if not data:
        return []
    scores = np.array([r.score for r in data])
    cutoff = float(np.mean(scores) + np.std(scores) / 2)
    return [r for r in data if r.score >= cutoff]


@app.post("/annotate/", response_model=list[schemas.AnnotationResponse])
async def annotate(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No image files uploaded.")
    if not _models_ready():
        raise HTTPException(status_code=503, detail="Models not available.")

    image_data = []
    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            logger.warning(f"Skipping non-image: {file.filename}")
            continue
        try:
            contents = await file.read()
            image_data.append((file.filename, contents))
        except Exception as e:
            logger.error(f"Error reading {file.filename}: {e}")

    all_results = []
    for i in range(0, len(image_data), settings.batch_size):
        batch = image_data[i : i + settings.batch_size]
        all_results.extend(_process_batch(batch))

    if not all_results:
        return []

    diverse = _rank_diverse(all_results, threshold=settings.diversity_threshold)

    return [
        schemas.AnnotationResponse(
            filename=item["filename"],
            tags=assign_categories(item["tags"], TAG_TO_CATEGORIES, 1, settings.top_n_categories),
            score=item["score"],
        )
        for item in diverse
    ]


def _process_batch(img_data: list[tuple[str, bytes]]) -> list[dict]:
    images, filenames = [], []
    for filename, raw_bytes in img_data:
        try:
            img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
            images.append(img)
            filenames.append(filename)
        except (IOError, UnidentifiedImageError) as e:
            logger.warning(f"Could not open {filename}: {e}")

    if not images:
        return []

    processor = ml_models["processor"]
    vision_session = ml_models["vision_session"]
    tag_features = ml_models["tag_features"]

    inputs = processor(images=images, return_tensors="np", padding=True)
    pixel_values = inputs["pixel_values"]

    img_features = vision_session.run(None, {"pixel_values": pixel_values})[0]
    img_features /= np.linalg.norm(img_features, axis=-1, keepdims=True)

    aesthetic_scores = _compute_aesthetic_scores(pixel_values)
    similarity = img_features @ tag_features.T

    results = []
    for i, scores in enumerate(similarity):
        top_idx = np.argsort(scores)[::-1][: settings.top_k_tags]
        tags = [TAG_LIST[idx] for idx in top_idx if scores[idx] > settings.tag_threshold]
        results.append({
            "filename": os.path.basename(filenames[i]),
            "tags": tags,
            "score": float(aesthetic_scores[i]),
            "embedding": img_features[i],
        })
    return results


def _compute_aesthetic_scores(pixel_values: np.ndarray) -> list[float]:
    session = ml_models.get("aesthetic_session")
    if session is None:
        raise RuntimeError("Aesthetic model not loaded.")
    input_name = session.get_inputs()[0].name
    return session.run(None, {input_name: pixel_values})[0].flatten()


def _rank_diverse(
    results: list[dict], threshold: float
) -> list[dict]:
    """Greedy diversity selection: iteratively pick the highest-scoring
    candidate and remove others whose embedding cosine similarity exceeds
    the threshold."""
    if not results:
        return []

    candidates = sorted(results, key=lambda x: x["score"], reverse=True)
    selected: list[dict] = []

    while candidates:
        best = candidates.pop(0)
        selected.append(best)
        if not candidates:
            break
        emb = best["embedding"].reshape(1, -1)
        remaining = np.array([c["embedding"] for c in candidates])
        sims = (emb @ remaining.T).flatten()
        candidates = [c for i, c in enumerate(candidates) if sims[i] < threshold]

    # Strip embeddings — they're only needed for diversity ranking
    for item in selected:
        item.pop("embedding", None)

    return selected
