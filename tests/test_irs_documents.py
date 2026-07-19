from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from ai_tax.utils.irs_documents import (
    IrsDocument,
    IrsDocumentRepository,
    IrsDocumentType,
    classify_irs_document,
)


class FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


@dataclass
class FakeMarkdownResult:
    markdown: str


class FakeConverter:
    def __init__(self) -> None:
        self.sources: list[Path] = []

    def convert(self, source: str | Path) -> FakeMarkdownResult:
        self.sources.append(Path(source))
        return FakeMarkdownResult("# IRS document\n\nConverted content.")


def test_search_returns_forms_instructions_and_publications_for_year(tmp_path: Path) -> None:
    html = """
    <a href="/pub/irs-prior/f1040--2024.pdf">Form 1040</a>
    <a href="/pub/irs-prior/i1040gi--2024.pdf">Instruction 1040</a>
    <a href="/pub/irs-prior/p17--2024.pdf">Publication 17</a>
    <a href="/pub/irs-prior/f1040--2023.pdf">Form 1040</a>
    """
    opened_urls: list[str] = []

    def fake_opener(request: Any) -> FakeResponse:
        opened_urls.append(request.full_url)
        return FakeResponse(html.encode() if "page=0" in request.full_url else b"")

    results = IrsDocumentRepository(root=tmp_path, opener=fake_opener).search("1040", 2024, max_pages=2)

    assert [(document.filename, document.document_type) for document in results] == [
        ("f1040--2024.pdf", IrsDocumentType.FORM),
        ("i1040gi--2024.pdf", IrsDocumentType.INSTRUCTION),
        ("p17--2024.pdf", IrsDocumentType.PUBLICATION),
    ]
    assert opened_urls == [
        "https://www.irs.gov/prior-year-forms-and-instructions?find=1040&items_per_page=200&page=0",
        "https://www.irs.gov/prior-year-forms-and-instructions?find=1040&items_per_page=200&page=1",
    ]


def test_fetch_and_convert_stores_forms_without_markdown(tmp_path: Path) -> None:
    converter = FakeConverter()
    document = IrsDocument(
        year=2024,
        product_number="f1040",
        title="Form 1040",
        source_url="https://www.irs.gov/pub/irs-prior/f1040--2024.pdf",
        filename="f1040--2024.pdf",
        document_type=IrsDocumentType.FORM,
    )

    stored = IrsDocumentRepository(
        root=tmp_path,
        converter=converter,
        opener=lambda request: FakeResponse(b"%PDF form"),
    ).fetch_and_convert(document)

    assert stored.pdf_path == tmp_path / "2024" / "forms" / "f1040--2024.pdf"
    assert stored.pdf_path.read_bytes() == b"%PDF form"
    assert stored.markdown_path is None
    assert converter.sources == []


def test_fetch_and_convert_stores_instruction_pdf_and_markdown(tmp_path: Path) -> None:
    converter = FakeConverter()
    document = IrsDocument(
        year=2024,
        product_number="i1040gi",
        title="Instruction 1040",
        source_url="https://www.irs.gov/pub/irs-prior/i1040gi--2024.pdf",
        filename="i1040gi--2024.pdf",
        document_type=IrsDocumentType.INSTRUCTION,
    )

    stored = IrsDocumentRepository(
        root=tmp_path,
        converter=converter,
        opener=lambda request: FakeResponse(b"%PDF instruction"),
    ).fetch_and_convert(document)

    assert stored.pdf_path == tmp_path / "2024" / "instructions" / "i1040gi--2024.pdf"
    assert stored.markdown_path == tmp_path / "2024" / "markdown" / "i1040gi--2024.md"
    assert stored.pdf_path.read_bytes() == b"%PDF instruction"
    assert stored.markdown_path.read_text(encoding="utf-8") == "# IRS document\n\nConverted content."
    assert converter.sources == [stored.pdf_path]


def test_fetch_and_convert_skips_existing_pdf_and_markdown(tmp_path: Path) -> None:
    document = IrsDocument(
        year=2024,
        product_number="i1040gi",
        title="Instruction 1040",
        source_url="https://www.irs.gov/pub/irs-prior/i1040gi--2024.pdf",
        filename="i1040gi--2024.pdf",
        document_type=IrsDocumentType.INSTRUCTION,
    )
    pdf_path = tmp_path / "2024" / "instructions" / "i1040gi--2024.pdf"
    markdown_path = tmp_path / "2024" / "markdown" / "i1040gi--2024.md"
    pdf_path.parent.mkdir(parents=True)
    markdown_path.parent.mkdir(parents=True)
    pdf_path.write_bytes(b"existing pdf")
    markdown_path.write_text("existing markdown", encoding="utf-8")

    def failing_opener(request: Any) -> FakeResponse:
        raise AssertionError("download should be skipped")

    converter = FakeConverter()
    stored = IrsDocumentRepository(
        root=tmp_path,
        converter=converter,
        opener=failing_opener,
    ).fetch_and_convert(document)

    assert stored.pdf_path.read_bytes() == b"existing pdf"
    assert stored.markdown_path is not None
    assert stored.markdown_path.read_text(encoding="utf-8") == "existing markdown"
    assert converter.sources == []


@pytest.mark.parametrize(
    ("product_number", "title", "expected"),
    [
        ("f1040", "Form 1040", IrsDocumentType.FORM),
        ("i1040gi", "Instruction 1040", IrsDocumentType.INSTRUCTION),
        ("p17", "Publication 17", IrsDocumentType.PUBLICATION),
        ("x123", "Notice 123", IrsDocumentType.OTHER),
    ],
)
def test_classify_irs_document(product_number: str, title: str, expected: IrsDocumentType) -> None:
    assert classify_irs_document(product_number=product_number, title=title) is expected


@pytest.mark.parametrize("year", [1899, 10000])
def test_search_rejects_invalid_years(tmp_path: Path, year: int) -> None:
    with pytest.raises(ValueError, match="four-digit year"):
        IrsDocumentRepository(root=tmp_path).search("1040", year)
