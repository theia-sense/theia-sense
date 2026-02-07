from pydantic import BaseModel, ConfigDict, Field, field_validator


class BackendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    filename: str = Field(..., json_schema_extra={"example": "image1.jpg"})
    tags: list[str] | None = Field(None, json_schema_extra={"example": ["nature", "sky", "tree"]})
    score: float | None = Field(None, json_schema_extra={"example": 4.567})

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v):
        if not v or not v.strip():
            raise ValueError("Filename cannot be empty")
        return v.strip()


class HealthResponse(BaseModel):
    status: str
    ml_service_connected: bool
    version: str
    reason: str | None = None
