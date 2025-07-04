import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import numpy as np
import io
from PIL import Image

from app.main import app, ml_models

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def mock_onnx_model_loading():
    """
    Mocks the ONNX model loading process that happens on app startup.
    This patch persists for all tests in this module.
    """
    with patch("app.main.ort.InferenceSession") as mock_ort_session, \
         patch("app.main.CLIPProcessor.from_pretrained") as mock_clip_processor, \
         patch("app.main.Path.exists", return_value=True):

        mock_text_session = MagicMock()
        mock_vision_session = MagicMock()
        mock_processor_instance = MagicMock()
        
        mock_ort_session.side_effect = [mock_text_session, mock_vision_session]
        mock_clip_processor.return_value = mock_processor_instance
        
        mock_tag_features = np.random.randn(19, 512).astype(np.float32)
        mock_text_session.run.return_value = [mock_tag_features]
        
        mock_processor_instance.return_value = {
            'input_ids': np.random.randint(0, 1000, (19, 77)).astype(np.int64),
            'attention_mask': np.ones((19, 77)).astype(np.int64)
        }
        
        ml_models["text_session"] = mock_text_session
        ml_models["vision_session"] = mock_vision_session
        ml_models["processor"] = mock_processor_instance
        ml_models["tag_features"] = mock_tag_features
        
        yield

        ml_models.clear()


# Health Check Tests
def test_read_root_model_loaded():
    """Test the health check when the ONNX models are loaded (mocked)."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ML Service API is running and ONNX models are loaded."}


def test_read_root_model_not_loaded():
    """Test health check when ONNX models are not loaded."""
    original_models = ml_models.copy()
    ml_models.clear()
    
    try:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"status": "ML Service is running, but models are NOT loaded."}
    finally:
        ml_models.update(original_models)


# Annotation Tests
def test_annotate_image_success():
    """Test successful image annotation."""
    test_image = Image.new('RGB', (224, 224), color='red')
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    mock_processor_return = {
        'pixel_values': np.random.randn(1, 3, 224, 224).astype(np.float32)
    }
    
    ml_models["processor"].side_effect = None
    ml_models["processor"].return_value = mock_processor_return
    
    mock_vision_output = np.random.randn(1, 512).astype(np.float32)
    ml_models["vision_session"].run.return_value = [mock_vision_output]
    
    response = client.post(
        "/annotate/",
        files={"file": ("test.jpg", img_bytes, "image/jpeg")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert "tags" in data
    assert data["filename"] == "test.jpg"
    assert isinstance(data["tags"], list)


def test_annotate_image_invalid_content_type():
    """Test annotation with non-image file."""
    text_data = io.BytesIO(b"This is not an image")
    
    response = client.post(
        "/annotate/",
        files={"file": ("test.txt", text_data, "text/plain")}
    )
    
    assert response.status_code == 400
    assert "File provided is not an image" in response.json()["detail"]


def test_annotate_image_model_not_loaded():
    """Test annotation when models are not loaded."""
    original_models = ml_models.copy()
    ml_models.clear()
    
    try:
        test_image = Image.new('RGB', (224, 224), color='blue')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        response = client.post(
            "/annotate/",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        
        assert response.status_code == 503
        assert "ML Model is not available" in response.json()["detail"]
    finally:
        ml_models.update(original_models)