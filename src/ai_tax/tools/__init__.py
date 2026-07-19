"""Tool definitions for AI Tax agents."""

from ai_tax.tools.currency_tools import CURRENCY_TOOLS, convert_currency_to_usd, list_supported_currencies
from ai_tax.tools.math_tools import MATH_TOOLS, add, divide, multiply, subtract

AI_TAX_TOOLS = [*MATH_TOOLS, *CURRENCY_TOOLS]

__all__ = [
    "AI_TAX_TOOLS",
    "CURRENCY_TOOLS",
    "MATH_TOOLS",
    "add",
    "subtract",
    "multiply",
    "divide",
    "convert_currency_to_usd",
    "list_supported_currencies",
]
