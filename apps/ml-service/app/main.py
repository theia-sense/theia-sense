from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image, UnidentifiedImageError
import io
import numpy as np
import onnxruntime as ort
from transformers import CLIPProcessor
from typing import List, Dict, Any
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
THRESHOLD = 0.09
PROVIDERS = ['CUDAExecutionProvider'] if ort.get_device() == 'GPU' else ['CPUExecutionProvider']
MODEL_ID = "openai/clip-vit-base-patch32"
ONNX_PATH = Path("new_onnx_models")
TEXT_MODEL_PATH = ONNX_PATH / "clip_text.onnx"
VISION_MODEL_PATH = ONNX_PATH / "clip_vision.onnx"


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

        text_session = ort.InferenceSession(str(TEXT_MODEL_PATH), providers=PROVIDERS)
        vision_session = ort.InferenceSession(str(VISION_MODEL_PATH), providers=PROVIDERS)
        
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

@app.post("/annotate/", response_model=schemas.AnnotationResponse, tags=["Image Annotation"])
async def annotate_image_endpoint(file: UploadFile = File(...)):
    """
    Receives an image, processes it with the ONNX CLIP model, and returns relevant tags.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    if not all(k in ml_models for k in ["vision_session", "processor", "tag_features"]):
        raise HTTPException(status_code=503, detail="ML Model is not available.")

    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Preprocess the image
        inputs = ml_models["processor"](images=image, return_tensors="np")
        onnx_vision_inputs = {'pixel_values': inputs['pixel_values']}

        # Run inference
        vision_outputs = ml_models["vision_session"].run(None, onnx_vision_inputs)
        img_features = vision_outputs[0]

        # Calculate similarity
        img_features /= np.linalg.norm(img_features, axis=-1, keepdims=True)
        logits_per_image = 100.0 * img_features @ ml_models["tag_features"].T
        exp_logits = np.exp(logits_per_image - np.max(logits_per_image))
        similarity = exp_logits / np.sum(exp_logits)
        sim_scores = similarity[0]
        top_indices = np.argsort(sim_scores)[::-1][:TOP_K]
        
        filtered_tags = [
            TAG_LIST[idx] for idx in top_indices if sim_scores[idx] > THRESHOLD
        ]
        
        return schemas.AnnotationResponse(
            filename=file.filename or "unknown.jpg",
            tags=filtered_tags
        )
        
    except (IOError, UnidentifiedImageError) as e:
        logger.warning(f"Image processing error for {file.filename}: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Failed to process image. It may be corrupt or in an unsupported format."
        )
    
    except Exception as e:
        logger.error(f"Unexpected error processing {file.filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected internal server error occurred: {str(e)}"
        )