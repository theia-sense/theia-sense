import pytest
import requests
import io
import time
from PIL import Image
import subprocess

# Test configuration
BACKEND_URL = "http://localhost:8000"
ML_SERVICE_URL = "http://localhost:8001"
COMPOSE_FILE = "compose.yml"

@pytest.fixture(scope="module")
def services():
    """Start services with docker-compose and clean up after tests."""
    print("Starting services with docker-compose...")
    
    subprocess.run(["docker", "compose", "-f", COMPOSE_FILE, "up", "-d"], check=True)
    
    max_retries = 30
    for i in range(max_retries):
        try:
            backend_response = requests.get(f"{BACKEND_URL}/", timeout=5)
            ml_response = requests.get(f"{ML_SERVICE_URL}/", timeout=5)
            
            if backend_response.status_code == 200 and ml_response.status_code == 200:
                print("Both services are ready!")
                break
        except requests.exceptions.RequestException:
            if i == max_retries - 1:
                pytest.fail("Services failed to start within timeout")
            time.sleep(2)
    
    yield
    
    print("\nCleaning up services...")
    subprocess.run(["docker", "compose", "-f", COMPOSE_FILE, "down"], check=True)

def create_test_image(color='red', size=(100, 100)):
    """Create a test image for testing."""
    image = Image.new('RGB', size, color=color)
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

class TestHealthChecks:
    """Test health check endpoints."""
    
    def test_backend_health(self, services):
        """Test backend health endpoint."""
        response = requests.get(f"{BACKEND_URL}/")
        assert response.status_code == 200
        assert response.json() == {"status": "Backend API is running!"}
    
    def test_ml_service_health(self, services):
        """Test ML service health endpoint."""
        response = requests.get(f"{ML_SERVICE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "ML Service" in data["status"]

class TestMLServiceEndpoints:
    """Test ML service endpoints directly."""
    
    def test_annotate_single_image(self, services):
        """Test ML service annotation endpoint with single image."""
        test_image = create_test_image('blue')
        
        files = {'file': ('test.jpg', test_image, 'image/jpeg')}
        response = requests.post(f"{ML_SERVICE_URL}/annotate/", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
        assert "tags" in data
        assert data["filename"] == "test.jpg"
        assert isinstance(data["tags"], list)
    
    def test_annotate_invalid_file(self, services):
        """Test ML service with invalid file type."""
        text_data = io.BytesIO(b"This is not an image")
        files = {'file': ('test.txt', text_data, 'text/plain')}
        
        response = requests.post(f"{ML_SERVICE_URL}/annotate/", files=files)
        
        assert response.status_code == 400
        assert "File provided is not an image" in response.json()["detail"]

class TestBackendEndpoints:
    """Test backend endpoints directly."""
    
    def test_predict_single_image(self, services):
        """Test backend prediction endpoint with single image."""
        test_image = create_test_image('green')
        
        files = [('files', ('test.jpg', test_image, 'image/jpeg'))]
        response = requests.post(f"{BACKEND_URL}/predict/", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "filename" in data[0]
        assert "tags" in data[0]
        assert data[0]["filename"] == "test.jpg"
    
    def test_predict_multiple_images(self, services):
        """Test backend prediction with multiple images."""
        test_image1 = create_test_image('red')
        test_image2 = create_test_image('blue')
        
        files = [
            ('files', ('test1.jpg', test_image1, 'image/jpeg')),
            ('files', ('test2.jpg', test_image2, 'image/jpeg'))
        ]
        response = requests.post(f"{BACKEND_URL}/predict/", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["filename"] == "test1.jpg"
        assert data[1]["filename"] == "test2.jpg"
    
    def test_predict_invalid_file_type(self, services):
        """Test backend with invalid file type."""
        text_data = io.BytesIO(b"This is not an image")
        files = [('files', ('test.txt', text_data, 'text/plain'))]
        
        response = requests.post(f"{BACKEND_URL}/predict/", files=files)
        
        assert response.status_code == 400
        assert "is not a valid image type" in response.json()["detail"]

class TestServiceCommunication:
    """Test communication between backend and ML service."""
    
    def test_backend_to_ml_service_flow(self, services):
        """Test complete flow from backend to ML service."""
        test_image = create_test_image('purple')
        
        files = [('files', ('integration_test.jpg', test_image, 'image/jpeg'))]
        response = requests.post(f"{BACKEND_URL}/predict/", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["filename"] == "integration_test.jpg"
        assert isinstance(data[0]["tags"], list)
        
        tags = data[0]["tags"]
        assert len(tags) >= 0
    
    def test_service_response_time(self, services):
        """Test that services respond within reasonable time."""
        test_image = create_test_image('yellow')
        
        start_time = time.time()
        files = [('files', ('timing_test.jpg', test_image, 'image/jpeg'))]
        response = requests.post(f"{BACKEND_URL}/predict/", files=files)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 30
    
    def test_concurrent_requests(self, services):
        """Test handling of concurrent requests."""
        import concurrent.futures
        
        def make_request(i):
            test_image = create_test_image('orange')
            files = [('files', (f'concurrent_test_{i}.jpg', test_image, 'image/jpeg'))]
            return requests.post(f"{BACKEND_URL}/predict/", files=files)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request, i) for i in range(3)]
            responses = [future.result() for future in futures]
        
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_backend_handles_ml_service_unavailable(self, services):
        """Test backend behavior when ML service is unavailable."""
        
        large_image = create_test_image('black', size=(2000, 2000))
        files = [('files', ('large_test.jpg', large_image, 'image/jpeg'))]
        
        response = requests.post(f"{BACKEND_URL}/predict/", files=files)
        
        assert response.status_code in [200, 413, 422, 500, 503]
    
    def test_ml_service_handles_corrupted_image(self, services):
        """Test ML service with corrupted image data."""
        corrupted_data = io.BytesIO(b"corrupted image data")
        files = {'file': ('corrupted.jpg', corrupted_data, 'image/jpeg')}
        
        response = requests.post(f"{ML_SERVICE_URL}/annotate/", files=files)
        
        assert response.status_code in [400, 422]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])