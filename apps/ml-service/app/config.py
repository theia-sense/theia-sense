from pathlib import Path

import onnxruntime as ort
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).parent.parent
    categories_json_path: Path = base_dir / "config" / "combined_categories.json"
    onnx_path: Path = base_dir / "new_onnx_models"

    @property
    def text_model_path(self) -> Path:
        return self.onnx_path / "clip_text.onnx"

    @property
    def vision_model_path(self) -> Path:
        return self.onnx_path / "clip_vision.onnx"

    @property
    def aesthetic_model_path(self) -> Path:
        return self.onnx_path / "aesthetic.onnx"

    model_id: str = "openai/clip-vit-base-patch32"
    providers: list[str] = Field(
        default_factory=lambda: (
            ["CUDAExecutionProvider"]
            if ort.get_device() == "GPU"
            else ["CPUExecutionProvider"]
        )
    )

    top_k_tags: int = 20
    top_n_categories: int = 5
    batch_size: int = 64
    tag_threshold: float = 0.215
    diversity_threshold: float = 0.95

    class Config:
        env_prefix = "theia_ml_"
        case_sensitive = False


settings = Settings()
