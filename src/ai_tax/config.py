"""Application configuration for AI Tax."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

RoundingPrecision = Literal["whole_dollar", "nearest_cent"]
DEFAULT_ROUNDING_PRECISION: RoundingPrecision = "nearest_cent"

DEFAULT_CONFIG_PATH = Path("config/app.yaml")
CONFIG_PATH_ENV_VAR = "AI_TAX_CONFIG"


class AppConfig(BaseModel):
    """Top-level application configuration."""

    source_tax_documents_dir: Path = Path("tax-documents")
    output_files_dir: Path = Path("tax-outputs")
    rounding_precision: RoundingPrecision = Field(
        default=DEFAULT_ROUNDING_PRECISION,
        description="Currency rounding option: 'whole_dollar' rounds 50.349 to 50; 'nearest_cent' rounds 50.349 to 50.35.",
    )


def get_config_path() -> Path:
    """Return the configured app config path."""
    return Path(os.environ.get(CONFIG_PATH_ENV_VAR, DEFAULT_CONFIG_PATH))


def load_config(path: Path | None = None) -> AppConfig:
    """Load app config from YAML, or return defaults if no config file exists."""
    config_path = path or get_config_path()

    if not config_path.exists():
        return AppConfig()

    with config_path.open("r", encoding="utf-8") as config_file:
        data = yaml.safe_load(config_file) or {}

    return AppConfig.model_validate(data)
