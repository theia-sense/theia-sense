from pydantic import BaseModel, Field
from typing import List

class AnnotationResponse(BaseModel):
    """
    Defines the structure of the JSON response for the /annotate/ endpoint.
    """
    filename: str = Field(..., description="The name of the uploaded image file.", json_schema_extra={"example": "image1.jpg"})
    tags: List[str] = Field(..., description="A list of tags classifying the image content.", json_schema_extra={"example": ["nature", "sky", "tree"]})
    score: float = Field(None, description="The aesthetic score for the image content.", json_schema_extra={"example": 4.567})