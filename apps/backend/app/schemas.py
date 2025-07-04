from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class BackendResponse(BaseModel):
    """
    Defines the structure of the final response sent back to the client
    for each processed image.
    """
    model_config = ConfigDict(from_attributes=True)
    
    filename: str = Field(..., description="The name of the uploaded image file.", json_schema_extra={"example": "image1.jpg"})
    tags: Optional[List[str]] = Field(None, description="A list of tags classifying the image content.", json_schema_extra={"example": ["nature", "sky", "tree"]})