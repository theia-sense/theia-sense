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

# --- ONNX Model Configuration ---
TAG_LIST = [
    "building", "architecture", "urban", "car", "automobile", "tree", "park",
    "nature", "landscape", "person", "dog", "family", "selfie", "food",
    "tasty", "happy", "colorful", "moody", "aesthetic"
]
TOP_K = 10
TOP_L = 2
BATCH_SIZE = 64
THRESHOLD = 0.09
PROVIDERS = ['CUDAExecutionProvider'] if ort.get_device() == 'GPU' else ['CPUExecutionProvider']
MODEL_ID = "openai/clip-vit-base-patch32"
ONNX_PATH = Path("new_onnx_models")
TEXT_MODEL_PATH = ONNX_PATH / "clip_text.onnx"
VISION_MODEL_PATH = ONNX_PATH / "clip_vision.onnx"
AESTHETIC_MODEL_PATH = ONNX_PATH / "aesthetic.onnx"


ml_models: Dict[str, Any] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's lifespan. Loads ONNX models and processor on startup.
    """
    # --- Startup ---
    logger.info("Application startup: Loading ML assets...")
    try:
        if not (TEXT_MODEL_PATH.exists() and VISION_MODEL_PATH.exists()):
            raise FileNotFoundError(
                f"ONNX model files not found: {TEXT_MODEL_PATH}, {VISION_MODEL_PATH}"
            )

        if not AESTHETIC_MODEL_PATH.exists():
            raise FileNotFoundError(f"ONNX model files not found: {AESTHETIC_MODEL_PATH}")

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
        
        ml_models["text_session"] = text_session
        ml_models["vision_session"] = vision_session
        ml_models["aesthetic_session"] = aesthetic_session
        ml_models["processor"] = processor
        ml_models["tag_features"] = tag_features
        
        logger.info(f"ML models loaded successfully. Providers: {PROVIDERS}")
    
    except Exception as e:
        print(f"FATAL: Could not load models. Error: {e}")

    yield
    
    # --- Shutdown ---
    logger.info("Shutting down ML service...")
    ml_models.clear()

app = FastAPI(
    title="Theia ML Service (ONNX)",
    version="0.2.0",
    description="A service that uses an ONNX CLIP model to annotate images with relevant tags.",
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
    return {"status": "ML Service API is running and ONNX models are loaded."}

@app.post("/annotate/", response_model=List[schemas.AnnotationResponse], tags=["Image Annotation"])
async def annotate_images_endpoint(files: List[UploadFile] = File(...)):
    """
    Accepts multiple images, processes them with the ONNX CLIP model, and returns relevant tags and scores for each image.
    """

    if not files:
        raise HTTPException(status_code=400, detail="No image files were uploaded.")

    if not all(k in ml_models for k in ["vision_session", "processor", "tag_features"]):
        raise HTTPException(status_code=503, detail="ML Model is not available.")

    image_data = []
    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"'{file.filename}' is not a valid image.")
        try:
            contents = await file.read()
            image_data.append((file.filename, contents))
               
        except (IOError, UnidentifiedImageError) as e:
            logger.warning(f"Image processing error for {file.filename}: {e}")
            # raise HTTPException(
            #     status_code=422,
            #     detail="Failed to process image. It may be corrupt or in an unsupported format."
            # )
            continue
    
        except Exception as e:
            logger.error(f"Unexpected error processing {file.filename}: {e}")
            # raise HTTPException(
            #     status_code=500,
            #     detail=f"An unexpected internal server error occurred: {str(e)}"
            # )
            continue
    
    results = []
    for i in range(0, len(image_data), BATCH_SIZE):
        batch = image_data[i:i+BATCH_SIZE]
        batch_results = annotate_images_batch(batch)
        results.extend(batch_results)

    return [
        schemas.AnnotationResponse(
            filename=item["filename"],
            tags=item["tags"],
            score=item["score"],
        ) for item in results 
    ]


def annotate_images_batch(img_data):
    """
    Accepts a list of (filename, image_bytes), decodes and processes with ONNX CLIP model,
    and returns top tags and scores.

    Parameters:
    - img_data: List of tuples (filename, image_bytes)

    Returns:
    - List of dicts with filename, tags, and scores
    """

    images = []
    valid_filenames = []
    preprocessed_np = []
    output = []

    for filename, raw_bytes in img_data:
        try:
            img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
            images.append(img)
            valid_filenames.append(filename)

            # Preprocess for aeesthetic model
            img_array = np.array(img.resize((224,224))).astype(np.float32) / 255.0
            img_array = np.transpose(img_array, (2, 0, 1)) # HWC -> CHW
            preprocessed_np.append(img_array)

        except Exception as e:
            logger.warning(f"Error processing {filename}: {e}")
            continue

    if not images:
        return []

    processor = ml_models["processor"]
    vision_session = ml_models["vision_session"]
    tag_features = ml_models["tag_features"]
    
    # ANNOTATION
    inputs = processor(images=images, return_tensors="np", padding=True)
    onnx_inputs = {"pixel_values": inputs["pixel_values"]}

    # Run OONX inference
    img_features = vision_session.run(None, onnx_inputs)[0]
    img_features /= np.linalg.norm(img_features, axis=-1, keepdims=True)

    # Compute cosine similarities and softmax over tags
    logits_per_image = 100 * img_features @ tag_features.T
    exp_logits = np.exp(logits_per_image - np.max(logits_per_image, axis=-1, keepdims=True))
    similarity = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)

    # CULLING
    preprocessed_np = np.stack(preprocessed_np)  # shape: [N, 3, 224, 224]
    aesthetic_scores = compute_aesthetic_scores(preprocessed_np)

    for i, sim_scores in enumerate(similarity):
        top_indices = np.argsort(sim_scores)[::-1][:TOP_K]
        filtered = [
            (TAG_LIST[idx], float(sim_scores[idx]))
            for idx in top_indices if sim_scores[idx] > THRESHOLD
            ]
        output.append({
            "filename": os.path.basename(valid_filenames[i]),
            "tags": [tag for tag,_ in filtered],
            "score": float(aesthetic_scores[i])
            })

    
    output.sort(key=lambda x: x["score"], reverse=True)
    return output[:TOP_L]


def compute_aesthetic_scores(images_np: np.ndarray) -> List[float]:
    """
    Runs the aesthetic model on preprocessed image batch.
    Returns list of aesthetic scores (float) for each image.
    """
    aesthetic_session = ml_models.get("aesthetic_session")
    if aesthetic_session is None:
        raise RuntimeError("Aesthetic model is not loaded.")

    input_name = aesthetic_session.get_inputs()[0].name
    outputs = aesthetic_session.run(None, {input_name: images_np})
    return outputs[0]
