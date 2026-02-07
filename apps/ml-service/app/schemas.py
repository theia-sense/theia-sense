from pydantic import BaseModel, Field


class AnnotationResponse(BaseModel):
    filename: str = Field(..., json_schema_extra={"example": "image1.jpg"})
    tags: list[str] = Field(..., json_schema_extra={"example": ["nature", "sky", "tree"]})
    score: float = Field(None, json_schema_extra={"example": 4.567})
