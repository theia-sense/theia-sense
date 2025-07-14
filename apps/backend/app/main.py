import os
from typing import List
import httpx
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
from . import schemas

ML_SERVICE_BASE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8001")

ML_SERVICE_URL_ANNOTATE = f"{ML_SERVICE_BASE_URL}/annotate/"
ML_SERVICE_URL_THRESHOLD = f"{ML_SERVICE_BASE_URL}/threshold/"

BATCH_SIZE = 64

app = FastAPI(
    title="Theia API",
    version="0.1.0",
    description="Backend service to handle image uploads and communicate with the ML service for annotation.",
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
    """A simple endpoint to check if the API is running."""
    return {"status": "Backend API is running!"}


@app.post("/predict/", response_model=List[schemas.BackendResponse], tags=["Image Processing"])
async def create_upload_files(files: List[UploadFile] = File(...)):
    """
    Receives multiple image files, sends them in batches to the ML service asynchronously,
    and returns the annotation results for each image.

    Args:
        files (List[UploadFile]): A list of images uploaded by the user.

    Returns:
        List[schemas.BackendResponse]: A list of objects, each containing the
                                       filename and the tags returned by the ML service.
    """
    if not files: 
        raise HTTPException(status_code=400, detail = "NO files uploaded")

    image_data = []
    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' is not a valid image type."
            )
        try:
            contents = await file.read()
            image_data.append((file.filename, contents, file.content_type))    
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"An error occured while processing {file.filename}: {str(e)}"
            )

    # Split into batches
    batches = [image_data[i:i+BATCH_SIZE] for i in range(0, len(image_data), BATCH_SIZE)]


    async def process_batch(batch):
        try:
            files_to_send = [("files", (filename, content, content_type)) for filename,content, content_type in batch]
            async with httpx.AsyncClient() as client:
                response = await client.post(ML_SERVICE_URL_ANNOTATE, files=files_to_send, timeout=300)
                response.raise_for_status()
                data= response.json()

                return [ 
                    schemas.BackendResponse(
                        filename=item.get("filename"),
                        tags=item.get("tags"),
                        score=item.get("score")
                        )
                        for item in data
                    ]

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error from ML service: {e.response.text}",
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Could not connect to the ML service: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while batch processing: {str(e)}",
            )

    # Process all batches concurrently
    all_results = await asyncio.gather(*[process_batch(batch) for batch in batches])

    flattened_results = [result for batch_result in all_results for result in batch_result]
    try:
        input_data = [
            {
                "filename": res.filename, 
                "tags": res.tags, 
                "score": res.score
            } 
            for res in flattened_results
        ]
        
        async with httpx.AsyncClient() as client:
            threshold_response = await client.post(
                ML_SERVICE_URL_THRESHOLD, 
                json=input_data, 
                timeout=300.0,
                headers={"Content-Type": "application/json"}
            )
            threshold_response.raise_for_status()
            threshold_data = threshold_response.json()
        
        return [
            schemas.BackendResponse(
                filename=item["filename"],
                tags=item["tags"], 
                score=item["score"]
            ) for item in threshold_data
        ]
        
    except (httpx.HTTPStatusError, httpx.RequestError, Exception) as e:
        logging.warning(f"Threshold Filtering Failed: {str(e)}")
        return flattened_results