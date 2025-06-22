from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ml_models.services import ml_service
from . import schemas

app = FastAPI(
    title="Theia API",
    version="0.1.0",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/annotate/", response_model=List[schemas.AnnotationResponse])
async def create_upload_file(files: List[UploadFile] = File(...)):
    """
    Accepts one or more image files, processes them with a mock ML model,
    and returns the predicted labels for each image.

    - **file**: A list of image file to be uploaded. Must be in a common format
                like JPEG or PNG.
    """
    results = []
    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' is not a valid image."
            )

        try:
            contents = await file.read()
            labels = await ml_service.annotate_image(contents)
            results.append({
                "filename": file.filename,
                "content_type": file.content_type,
                "labels": labels
            })
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while processing {file.filename}: {e}"
            )
        finally:
            await file.close()

    if not results:
        raise HTTPException(
            status_code=400,
            detail="No files were processed successfully."
        )
    
    return results

@app.get("/", response_model=schemas.HealthCheckResponse)
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "Welcome to the API!"}
