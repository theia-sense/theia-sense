import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Tests the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Welcome to the API!"}

def test_annotate_single_image():
    """Tests the /annotate/ endpoint with a single dummy image file."""
    dummy_image_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc`\x00'
        b'\x00\x00\x02\x00\x01\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    
    # The client expects a list of tuples for multiple files
    files_to_upload = [
        ('files', ('test_image.png', io.BytesIO(dummy_image_bytes), 'image/png'))
    ]

    response = client.post("/annotate/", files=files_to_upload)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    result = data[0]
    assert result["filename"] == "test_image.png"
    assert "labels" in result
    assert isinstance(result["labels"], list)
    assert len(result["labels"]) > 0

def test_annotate_multiple_images():
    """Tests the /annotate/ endpoint with multiple dummy image files."""
    dummy_image_bytes_1 = b'\x89PNG...' # Use your actual dummy bytes
    dummy_image_bytes_2 = b'\x89PNG...' # A different one if needed, or the same

    files_to_upload = [
        ('files', ('image1.png', io.BytesIO(dummy_image_bytes_1), 'image/png')),
        ('files', ('image2.png', io.BytesIO(dummy_image_bytes_2), 'image/png'))
    ]

    response = client.post("/annotate/", files=files_to_upload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["filename"] == "image1.png"
    assert data[1]["filename"] == "image2.png"

def test_annotate_invalid_file_type():
    """Tests uploading a non-image file, which should fail."""
    files_to_upload = [
        ('files', ('test.txt', io.BytesIO(b"this is not an image"), 'text/plain'))
    ]
    response = client.post("/annotate/", files=files_to_upload)
    assert response.status_code == 400
    assert response.json() == {"detail": "File 'test.txt' is not a valid image."}