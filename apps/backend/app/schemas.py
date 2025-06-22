from pydantic import BaseModel, Field
from typing import List

class AnnotationResponse(BaseModel):
    """
    Defines the structure for the response of an annotated image.
    """
    filename: str
    content_type: str | None = None
    labels: List[str] = Field(..., json_schema_extra=["cat", "person"])

class HealthCheckResponse(BaseModel):
    """
    Defines the structure for the health check endpoint.
    """
    status: str = "ok"
    message: str