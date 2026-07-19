"""Tool definitions for AI Tax agents."""

from ai_tax.tools.currency_tools import CURRENCY_TOOLS, convert_currency_to_usd, list_supported_currencies
from ai_tax.tools.irs_tools import (
    IRS_TOOLS,
    fetch_irs_document,
    fetch_irs_xml_source,
    preload_irs_documents,
    search_irs_documents,
    search_irs_xml_sources,
)
from ai_tax.tools.math_tools import MATH_TOOLS, add, divide, multiply, subtract

AI_TAX_TOOLS = [*MATH_TOOLS, *CURRENCY_TOOLS, *IRS_TOOLS]

__all__ = [
    "AI_TAX_TOOLS",
    "CURRENCY_TOOLS",
    "IRS_TOOLS",
    "MATH_TOOLS",
    "add",
    "subtract",
    "multiply",
    "divide",
    "convert_currency_to_usd",
    "fetch_irs_document",
    "fetch_irs_xml_source",
    "list_supported_currencies",
    "preload_irs_documents",
    "search_irs_documents",
    "search_irs_xml_sources",
]
