"""IRS document tools for tax agents."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

from ai_tax.utils.irs_documents import (
    IrsDocument,
    IrsDocumentType,
    IrsStoredXmlSource,
    IrsXmlSourceDocument,
    fetch_and_convert_irs_document as fetch_and_convert_irs_document_func,
    fetch_irs_xml_source as fetch_irs_xml_source_func,
    preload_irs_documents as preload_irs_documents_func,
    search_irs_documents as search_irs_documents_func,
    search_irs_xml_sources as search_irs_xml_sources_func,
)


def _document_to_dict(document: IrsDocument) -> dict[str, str | int]:
    return {
        "year": document.year,
        "product_number": document.product_number,
        "title": document.title,
        "source_url": document.source_url,
        "filename": document.filename,
        "document_type": document.document_type.value,
    }


def _stored_document_to_dict(stored: Any) -> dict[str, str | int | bool | None]:
    return {
        **_document_to_dict(stored.document),
        "pdf_path": str(stored.pdf_path),
        "markdown_path": str(stored.markdown_path) if stored.markdown_path is not None else None,
        "converted_to_markdown": stored.converted_to_markdown,
    }


def _xml_source_to_dict(document: IrsXmlSourceDocument) -> dict[str, str | int]:
    return {
        "year": document.year,
        "product_number": document.product_number,
        "title": document.title,
        "revision": document.revision,
        "posted": document.posted,
        "source_url": document.source_url,
        "filename": document.filename,
        "document_type": document.document_type.value,
    }


def _stored_xml_source_to_dict(stored: IrsStoredXmlSource) -> dict[str, str | int]:
    return {
        **_xml_source_to_dict(stored.document),
        "zip_path": str(stored.zip_path),
    }


def _document_from_tool_args(
    *,
    year: int,
    product_number: str,
    title: str,
    source_url: str,
    filename: str,
    document_type: str,
) -> IrsDocument:
    return IrsDocument(
        year=year,
        product_number=product_number,
        title=title,
        source_url=source_url,
        filename=filename,
        document_type=IrsDocumentType(document_type),
    )


def _xml_source_from_tool_args(
    *,
    year: int,
    product_number: str,
    title: str,
    revision: str,
    posted: str,
    source_url: str,
    filename: str,
    document_type: str,
) -> IrsXmlSourceDocument:
    return IrsXmlSourceDocument(
        year=year,
        product_number=product_number,
        title=title,
        revision=revision,
        posted=posted,
        source_url=source_url,
        filename=filename,
        document_type=IrsDocumentType(document_type),
    )


@tool
def search_irs_documents(query: str, year: int, max_pages: int = 5) -> list[dict[str, str | int]]:
    """Search IRS prior-year PDFs for a query/year without downloading anything.

    Use this first to find candidate forms, instructions, or publications.
    Returned dictionaries contain all fields needed by fetch_irs_document.
    """
    return [
        _document_to_dict(document)
        for document in search_irs_documents_func(query=query, year=year, max_pages=max_pages)
    ]


@tool
def fetch_irs_document(
    year: int,
    product_number: str,
    title: str,
    source_url: str,
    filename: str,
    document_type: str,
    overwrite: bool = False,
) -> dict[str, str | int | bool | None]:
    """Download/cache one IRS PDF and convert non-form PDFs to Markdown.

    Forms are stored in ``irs/<year>/forms`` and are not converted to Markdown.
    Instructions/publications/other PDFs are stored by type and converted into
    ``irs/<year>/markdown``.
    """
    document = _document_from_tool_args(
        year=year,
        product_number=product_number,
        title=title,
        source_url=source_url,
        filename=filename,
        document_type=document_type,
    )
    return _stored_document_to_dict(fetch_and_convert_irs_document_func(document, overwrite=overwrite))


@tool
def preload_irs_documents(
    year: int,
    queries: list[str],
    max_pages_per_query: int = 2,
    max_results_per_query: int | None = None,
    overwrite: bool = False,
) -> list[dict[str, str | int | bool | None]]:
    """Search/cache IRS docs for upfront preload queries.

    This is useful for loading essential instructions/publications/forms before
    an agent starts a tax workflow. Forms are cached as PDFs only.
    """
    return [
        _stored_document_to_dict(stored)
        for stored in preload_irs_documents_func(
            year=year,
            queries=queries,
            max_pages_per_query=max_pages_per_query,
            max_results_per_query=max_results_per_query,
            overwrite=overwrite,
        )
    ]


@tool
def search_irs_xml_sources(query: str, year: int, max_pages: int = 5) -> list[dict[str, str | int]]:
    """Search IRS instructions/publications XML source ZIPs without downloading anything.

    Use this for cleaner structured source data from
    https://www.irs.gov/instructions-and-publications-xml-source-files.
    Returned dictionaries contain all fields needed by fetch_irs_xml_source.
    """
    return [
        _xml_source_to_dict(document)
        for document in search_irs_xml_sources_func(query=query, year=year, max_pages=max_pages)
    ]


@tool
def fetch_irs_xml_source(
    year: int,
    product_number: str,
    title: str,
    revision: str,
    posted: str,
    source_url: str,
    filename: str,
    document_type: str,
    overwrite: bool = False,
) -> dict[str, str | int]:
    """Download/cache one IRS XML source ZIP under ``irs/<year>/xml``."""
    document = _xml_source_from_tool_args(
        year=year,
        product_number=product_number,
        title=title,
        revision=revision,
        posted=posted,
        source_url=source_url,
        filename=filename,
        document_type=document_type,
    )
    return _stored_xml_source_to_dict(fetch_irs_xml_source_func(document, overwrite=overwrite))


IRS_TOOLS = [
    search_irs_documents,
    fetch_irs_document,
    preload_irs_documents,
    search_irs_xml_sources,
    fetch_irs_xml_source,
]
