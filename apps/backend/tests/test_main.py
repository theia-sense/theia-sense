from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import io
from PIL import Image
import httpx

from app.main import app

client = TestClient(app)

# Health Check Test
def test_read_root():
    """Test the backend health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Backend API is running!"}

# Prediction Tests
def test_predict_single_image_success():
    """Test successful prediction with single image."""
    with patch("app.main.httpx.AsyncClient") as mock_async_client:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "filename": "test.jpg",
            "tags": ["building", "urban"]
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        test_image = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        response = client.post(
            "/predict/",
            files=[("files", ("test.jpg", img_bytes, "image/jpeg"))]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["filename"] == "test.jpg"
        assert data[0]["tags"] == ["building", "urban"]

def test_predict_invalid_file_type():
    """Test prediction with non-image file."""
    text_data = io.BytesIO(b"This is not an image")
    
    response = client.post(
        "/predict/",
        files=[("files", ("test.txt", text_data, "text/plain"))]
    )
    
    assert response.status_code == 400
    assert "is not a valid image type" in response.json()["detail"]

def test_predict_ml_service_error():
    """Test handling of ML service errors."""
    with patch("app.main.httpx.AsyncClient") as mock_async_client:
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.text = "Service unavailable"
        
        http_error = httpx.HTTPStatusError(
            "Service unavailable", 
            request=MagicMock(), 
            response=mock_response
        )
        mock_response.raise_for_status.side_effect = http_error
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        test_image = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        response = client.post(
            "/predict/",
            files=[("files", ("test.jpg", img_bytes, "image/jpeg"))]
        )
        
        assert response.status_code == 503
        assert "Error from ML service" in response.json()["detail"]

def test_predict_connection_error():
    """Test handling of connection errors."""
    with patch("app.main.httpx.AsyncClient") as mock_async_client:
        connection_error = httpx.RequestError("Connection failed")
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.side_effect = connection_error
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        test_image = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        response = client.post(
            "/predict/",
            files=[("files", ("test.jpg", img_bytes, "image/jpeg"))]
        )
        
        assert response.status_code == 503
        assert "Could not connect to the ML service" in response.json()["detail"]