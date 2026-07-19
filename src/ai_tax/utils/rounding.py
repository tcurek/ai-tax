"""Rounding utilities that follow application configuration."""

from __future__ import annotations

import builtins

from ai_tax.config import AppConfig, load_config


def round(value: float, config: AppConfig | None = None) -> float | int:
    """Round a number using the configured currency rounding option."""
    app_config = config or load_config()

    if app_config.rounding_precision == "whole_dollar":
        return builtins.round(value)

    return builtins.round(value, 2)
