from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ml_service_url: str = "https://theiasense-theia-sense.hf.space"
    ml_service_timeout: float = 300.0
    hf_token: str | None = None

    batch_size: int = 64
    max_file_size: int = 10 * 1024 * 1024  # 10 MB
    allowed_extensions: list[str] = [".jpg", ".jpeg", ".png", ".webp", ".bmp"]

    cors_allow_origins: list[str] | str = "*"
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] | str = "GET,POST,OPTIONS"
    cors_allow_headers: list[str] | str = "*"

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return ["*"] if v == "*" else [s.strip() for s in v.split(",") if s.strip()]
        return v

    @field_validator("cors_allow_methods", mode="before")
    @classmethod
    def parse_cors_methods(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    @field_validator("cors_allow_headers", mode="before")
    @classmethod
    def parse_cors_headers(cls, v):
        if isinstance(v, str):
            return ["*"] if v == "*" else [s.strip() for s in v.split(",") if s.strip()]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

ML_SERVICE_BASE_URL = settings.ml_service_url
ML_SERVICE_URL_ANNOTATE = f"{ML_SERVICE_BASE_URL}/annotate/"
ML_SERVICE_URL_THRESHOLD = f"{ML_SERVICE_BASE_URL}/threshold/"
