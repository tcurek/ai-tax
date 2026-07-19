"""Math tools for AI Tax agents."""

from __future__ import annotations

from langchain_core.tools import tool

from ai_tax.utils.rounding import round as round_using_config


@tool
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@tool
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@tool
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


@tool
def round(value: float) -> float | int:
    """Round a number using the configured currency rounding option."""
    return round_using_config(value)


MATH_TOOLS = [add, subtract, multiply, divide, round]
