from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image, UnidentifiedImageError
import io
import os
import numpy as np
import onnxruntime as ort
from transformers import CLIPProcessor
from typing import Dict, Any, List
from fastapi.middleware.cors import CORSMiddleware
from . import schemas
from contextlib import asynccontextmanager
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TAG_LIST = [
    "building", "architecture", "urban", "car", "automobile", "tree", "park",
    "nature", "landscape", "person", "dog", "family", "selfie", "food",
    "tasty", "happy", "colorful", "moody", "aesthetic"
]
TOP_K_TAGS = 10
BATCH_SIZE = 64
TAG_THRESHOLD = 0.09
DIVERSITY_THRESHOLD = 0.95 

# Model Paths
ONNX_PATH = Path("new_onnx_models")
TEXT_MODEL_PATH = ONNX_PATH / "clip_text.onnx"
VISION_MODEL_PATH = ONNX_PATH / "clip_vision.onnx"
AESTHETIC_MODEL_PATH = ONNX_PATH / "aesthetic.onnx"

# Runtime Configuration
MODEL_ID = "openai/clip-vit-base-patch32"
PROVIDERS = ['CUDAExecutionProvider'] if ort.get_device() == 'GPU' else ['CPUExecutionProvider']

ml_models: Dict[str, Any] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's lifespan. Loads ONNX models and processor on startup.
    """
    # --- Startup ---
    logger.info("Application startup: Loading ML assets...")
    try:
        for path in [TEXT_MODEL_PATH, VISION_MODEL_PATH, AESTHETIC_MODEL_PATH]:
            if not path.exists():
                raise FileNotFoundError(
                    f"ONNX model files not found: {path}"
                )

        text_session = ort.InferenceSession(str(TEXT_MODEL_PATH), providers=PROVIDERS)
        vision_session = ort.InferenceSession(str(VISION_MODEL_PATH), providers=PROVIDERS)
        aesthetic_session = ort.InferenceSession(str(AESTHETIC_MODEL_PATH), providers=PROVIDERS)

        processor = CLIPProcessor.from_pretrained(MODEL_ID)
        if isinstance(processor, tuple):
            processor = processor[0]
        
        text_inputs = processor(text=TAG_LIST, return_tensors="np", padding=True)
        
        onnx_text_inputs = {
            'input_ids': np.array(text_inputs['input_ids']).astype(np.int64),
            'attention_mask': np.array(text_inputs['attention_mask']).astype(np.int64)
        }
        
        text_outputs = text_session.run(None, onnx_text_inputs)
        tag_features = np.asarray(text_outputs[0])
        tag_features /= np.linalg.norm(tag_features, axis=-1, keepdims=True)
        
        ml_models.update({
            "text_session": text_session,
            "vision_session": vision_session,
            "aesthetic_session": aesthetic_session,
            "processor": processor,
            "tag_features": tag_features
        })
        
        logger.info(f"ML models loaded successfully. Providers: {PROVIDERS}")
    
    except Exception as e:
        print(f"FATAL: Could not load models. Error: {e}")

    yield
    
    # --- Shutdown ---
    logger.info("Shutting down ML service...")
    ml_models.clear()

app = FastAPI(
    title="Theia ML Service (ONNX)",
    version="0.3.0",
    description="A service that uses ONNX models to annotate images with tags, scores and diverse results.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health Check"])
async def read_root():
    """A simple endpoint to check if the API is running and the model is loaded."""
    if not all(k in ml_models for k in ["vision_session", "processor", "tag_features"]):
        return {"status": "ML Service is running, but models are NOT loaded."}
    return {"status": "ML Service is running with models loaded."}

@app.post("/threshold/", response_model=List[schemas.AnnotationResponse], tags=["Threshold Calculation"])
async def get_image_threshold(data: List[schemas.AnnotationResponse]):
    """Applies a dynamic threshold to filter resultant images based on score."""
    if not data:
        return []
    
    scores = np.array([res.score for res in data])
    dynamic_threshold = np.mean(scores) + (np.std(scores) / 2)

    return [
        schemas.AnnotationResponse(
            filename=item.filename,
            tags=item.tags,
            score=item.score,
        ) for item in data if item.score >= dynamic_threshold
    ]

@app.post("/annotate/", response_model=List[schemas.AnnotationResponse], tags=["Image Annotation"])
async def annotate_images_endpoint(files: List[UploadFile] = File(...)):
    """
    Accepts multiple images, processes them with ONNX models, and returns a diverse
    set of relevant tags and scores for the top images.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No image files were uploaded.")
    if not all(k in ml_models for k in ["vision_session", "processor", "tag_features"]):
        raise HTTPException(status_code=503, detail="ML Models are not available.")

    image_data = []
    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            logger.warning(f"Skipping non-image file: {file.filename}")
            continue
        try:
            contents = await file.read()
            image_data.append((file.filename, contents))
        except Exception as e:
            logger.error(f"Unexpected error processing {file.filename}: {e}")
            continue
    
    all_results = []
    for i in range(0, len(image_data), BATCH_SIZE):
        batch = image_data[i:i+BATCH_SIZE]
        batch_results = process_images_batch(batch)
        all_results.extend(batch_results)

    if not all_results:
        return []

    diverse_results = rank_diverse_results(all_results, top_n=len(all_results), threshold=DIVERSITY_THRESHOLD)

    return [
        schemas.AnnotationResponse(
            filename=item["filename"],
            tags=item["tags"],
            score=item["score"],
        ) for item in diverse_results
    ]

def process_images_batch(img_data):
    """Process a batch of images and return annotations with embeddings."""
    images, valid_filenames = [], []

    for filename, raw_bytes in img_data:
        try:
            img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
            images.append(img)
            valid_filenames.append(filename)
        except (IOError, UnidentifiedImageError) as e:
            logger.warning(f"Could not process image {filename}: {e}")
            continue

    if not images:
        return []

    processor = ml_models["processor"]
    vision_session = ml_models["vision_session"]
    tag_features = ml_models["tag_features"]
    

    inputs = processor(images=images, return_tensors="np", padding=True)
    pixel_values = inputs["pixel_values"]
    img_features = vision_session.run(None, {"pixel_values": pixel_values})[0]
    img_features /= np.linalg.norm(img_features, axis=-1, keepdims=True)

    aesthetic_scores = compute_aesthetic_scores(pixel_values)

    logits_per_image = 100 * img_features @ tag_features.T
    exp_logits = np.exp(logits_per_image - np.max(logits_per_image, axis=-1, keepdims=True))
    similarity_scores = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)

    results = []
    for i, scores in enumerate(similarity_scores):
        top_indices = np.argsort(scores)[::-1][:TOP_K_TAGS]
        filtered_tags = [
            TAG_LIST[idx] for idx in top_indices if scores[idx] > TAG_THRESHOLD
        ]
        
        results.append({
            "filename": os.path.basename(valid_filenames[i]),
            "tags": filtered_tags,
            "score": float(aesthetic_scores[i]),
            "embedding": img_features[i]
        })

    return results


def compute_aesthetic_scores(images_np: np.ndarray) -> List[float]:
    """Compute aesthetic scores for a batch of images."""
    aesthetic_session = ml_models.get("aesthetic_session")
    if aesthetic_session is None:
        raise RuntimeError("Aesthetic model is not loaded.")
    input_name = aesthetic_session.get_inputs()[0].name
    outputs = aesthetic_session.run(None, {input_name: images_np})
    return outputs[0].flatten()


def rank_diverse_results(results: List[Dict[str, Any]], top_n: int, threshold: float) -> List[Dict[str, Any]]:
    """Select diverse results based on embedding similarity."""
    if not results:
        return []

    candidates = sorted(results, key=lambda x: x["score"], reverse=True)
    diverse_results = []
    
    while candidates and len(diverse_results) < top_n:
        best_candidate = candidates.pop(0)
        diverse_results.append(best_candidate)
        
        if not candidates:
            break
            
        best_embedding = best_candidate["embedding"].reshape(1, -1)
        remaining_embeddings = np.array([res["embedding"] for res in candidates])
        similarities = (best_embedding @ remaining_embeddings.T).flatten()
        
        candidates = [
            cand for i, cand in enumerate(candidates) if similarities[i] < threshold
        ]

    return diverse_results