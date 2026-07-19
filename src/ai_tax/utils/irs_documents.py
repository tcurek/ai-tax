"""Search, cache, and convert IRS forms/instructions/publications."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


DEFAULT_IRS_ROOT = Path(__file__).resolve().parents[1] / "irs"
DEFAULT_IRS_SEARCH_URL = "https://www.irs.gov/prior-year-forms-and-instructions"
DEFAULT_USER_AGENT = "ai-tax/0.1 (+https://github.com/earendil-works/ai-tax)"


class IrsDocumentType(StrEnum):
    """IRS product categories relevant to local storage/conversion."""

    FORM = "form"
    INSTRUCTION = "instruction"
    PUBLICATION = "publication"
    OTHER = "other"


class MarkdownConverter(Protocol):
    """Protocol for MarkItDown-compatible converters."""

    def convert(self, source: str | Path) -> object:
        """Convert a document source and return an object with markdown text."""


@dataclass(frozen=True, slots=True)
class _IrsPriorYearLink:
    href: str
    text: str


class _IrsPriorYearLinkParser(HTMLParser):
    """Extract prior-year PDF links from the IRS search results page."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[_IrsPriorYearLink] = []
        self._current_href: str | None = None
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return

        href = dict(attrs).get("href")
        if href and "/pub/irs-prior/" in href and href.endswith(".pdf"):
            self._current_href = href
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_href is not None:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self._current_href is None:
            return

        self.links.append(
            _IrsPriorYearLink(
                href=self._current_href,
                text=" ".join("".join(self._current_text).split()),
            )
        )
        self._current_href = None
        self._current_text = []


@dataclass(frozen=True, slots=True)
class IrsDocument:
    """A searchable/fetchable IRS PDF product."""

    year: int
    product_number: str
    title: str
    source_url: str
    filename: str
    document_type: IrsDocumentType

    @classmethod
    def from_prior_year_link(cls, link: _IrsPriorYearLink, year: int) -> IrsDocument | None:
        """Build a document from an IRS prior-year search link, if it matches ``year``."""
        filename = PurePosixPath(link.href).name
        if not filename.endswith(f"--{year}.pdf"):
            return None

        product_number = filename.removesuffix(f"--{year}.pdf")
        return cls(
            year=year,
            product_number=product_number,
            title=link.text or product_number,
            source_url=urljoin(DEFAULT_IRS_SEARCH_URL, link.href),
            filename=filename,
            document_type=classify_irs_document(product_number=product_number, title=link.text),
        )


def classify_irs_document(*, product_number: str, title: str = "") -> IrsDocumentType:
    """Classify an IRS product from its product number/title."""
    normalized_title = title.casefold().strip()
    normalized_product = product_number.casefold().strip()

    if normalized_product.startswith("f") or normalized_title.startswith("form "):
        return IrsDocumentType.FORM
    if normalized_product.startswith("i") or normalized_title.startswith("instruction "):
        return IrsDocumentType.INSTRUCTION
    if normalized_product.startswith("p") or normalized_title.startswith("publication "):
        return IrsDocumentType.PUBLICATION
    return IrsDocumentType.OTHER


@dataclass(frozen=True, slots=True)
class IrsStoredDocument:
    """Local cache paths for an IRS document."""

    document: IrsDocument
    pdf_path: Path
    markdown_path: Path | None = None

    @property
    def converted_to_markdown(self) -> bool:
        """Return whether this document has a Markdown cache path."""
        return self.markdown_path is not None


class IrsDocumentRepository:
    """Search IRS products and cache PDFs/Markdown locally.

    Storage layout:
    - Forms: ``irs/<year>/forms/<filename>``; forms are never converted here.
    - Instructions: ``irs/<year>/instructions/<filename>`` and Markdown in
      ``irs/<year>/markdown/<stem>.md``.
    - Publications: ``irs/<year>/publications/<filename>`` and Markdown in
      ``irs/<year>/markdown/<stem>.md``.
    - Other PDFs: ``irs/<year>/other/<filename>`` and Markdown in
      ``irs/<year>/markdown/<stem>.md``.
    """

    def __init__(
        self,
        root: Path | str = DEFAULT_IRS_ROOT,
        *,
        converter: MarkdownConverter | None = None,
        opener: Callable[..., Any] = urlopen,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        self.root = Path(root)
        self._converter = converter
        self._opener = opener
        self._user_agent = user_agent

    def search(self, query: str, year: int, *, max_pages: int = 5) -> list[IrsDocument]:
        """Search IRS prior-year products for ``query`` and return matching PDFs for ``year``."""
        self._validate_year(year)
        if not query.strip():
            raise ValueError("query must not be blank")
        if max_pages < 1:
            raise ValueError("max_pages must be at least 1")

        documents_by_filename: dict[str, IrsDocument] = {}
        for page in range(max_pages):
            links = self._fetch_prior_year_links(search_query=query, page=page)
            if not links:
                break

            for link in links:
                document = IrsDocument.from_prior_year_link(link, year)
                if document is not None:
                    documents_by_filename.setdefault(document.filename, document)

        return sorted(documents_by_filename.values(), key=lambda document: document.filename)

    def fetch(self, document: IrsDocument, *, overwrite: bool = False) -> IrsStoredDocument:
        """Download/cache ``document`` without Markdown conversion."""
        pdf_path = self.pdf_path_for(document)
        self._download_pdf(document.source_url, pdf_path, overwrite=overwrite)
        return IrsStoredDocument(document=document, pdf_path=pdf_path)

    def fetch_and_convert(self, document: IrsDocument, *, overwrite: bool = False) -> IrsStoredDocument:
        """Download/cache ``document`` and convert non-form PDFs to Markdown.

        Forms are intentionally not converted because a dedicated form-editing
        agent will operate on the source PDFs in ``irs/<year>/forms``.
        """
        stored = self.fetch(document, overwrite=overwrite)
        if document.document_type is IrsDocumentType.FORM:
            return stored

        markdown_path = self.markdown_path_for(document)
        self._convert_pdf_to_markdown(stored.pdf_path, markdown_path, overwrite=overwrite)
        return IrsStoredDocument(document=document, pdf_path=stored.pdf_path, markdown_path=markdown_path)

    def preload(
        self,
        year: int,
        queries: Iterable[str],
        *,
        max_pages_per_query: int = 2,
        max_results_per_query: int | None = None,
        overwrite: bool = False,
    ) -> list[IrsStoredDocument]:
        """Search and cache selected IRS documents for common upfront needs."""
        stored_documents: list[IrsStoredDocument] = []
        seen_filenames: set[str] = set()
        for query in queries:
            results = self.search(query, year, max_pages=max_pages_per_query)
            if max_results_per_query is not None:
                results = results[:max_results_per_query]

            for document in results:
                if document.filename in seen_filenames:
                    continue
                seen_filenames.add(document.filename)
                stored_documents.append(self.fetch_and_convert(document, overwrite=overwrite))

        return stored_documents

    def pdf_path_for(self, document: IrsDocument) -> Path:
        """Return the local PDF cache path for ``document``."""
        return self.root / str(document.year) / self._pdf_subdir(document.document_type) / document.filename

    def markdown_path_for(self, document: IrsDocument) -> Path:
        """Return the local Markdown cache path for a non-form document."""
        if document.document_type is IrsDocumentType.FORM:
            raise ValueError("IRS forms are not converted to Markdown")
        return self.root / str(document.year) / "markdown" / f"{Path(document.filename).stem}.md"

    def _fetch_prior_year_links(self, *, search_query: str, page: int) -> list[_IrsPriorYearLink]:
        query = urlencode({"find": search_query, "items_per_page": "200", "page": str(page)})
        request = Request(
            f"{DEFAULT_IRS_SEARCH_URL}?{query}",
            headers={"User-Agent": self._user_agent},
        )
        try:
            with self._opener(request) as response:
                html = response.read().decode("utf-8", errors="replace")
        except HTTPError as exc:
            raise RuntimeError("IRS prior-year search page is unavailable") from exc
        except URLError as exc:
            raise RuntimeError("Unable to search IRS prior-year forms and instructions") from exc

        parser = _IrsPriorYearLinkParser()
        parser.feed(html)
        return parser.links

    def _download_pdf(self, url: str, destination: Path, *, overwrite: bool = False) -> Path:
        if destination.exists() and not overwrite:
            return destination

        destination.parent.mkdir(parents=True, exist_ok=True)
        request = Request(url, headers={"User-Agent": self._user_agent})
        try:
            with self._opener(request) as response:
                data = response.read()
        except HTTPError as exc:
            raise RuntimeError(f"IRS PDF not found or unavailable: {url}") from exc
        except URLError as exc:
            raise RuntimeError(f"Unable to download IRS PDF: {url}") from exc

        destination.write_bytes(data)
        return destination

    def _convert_pdf_to_markdown(self, pdf_path: Path, markdown_path: Path, *, overwrite: bool = False) -> Path:
        if markdown_path.exists() and not overwrite:
            return markdown_path

        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        if self._converter is None:
            from markitdown import MarkItDown

            converter: MarkdownConverter = MarkItDown()
        else:
            converter = self._converter

        result = converter.convert(pdf_path)
        markdown = getattr(result, "markdown", None)
        if not isinstance(markdown, str):
            raise RuntimeError(f"MarkItDown did not return markdown for {pdf_path}")

        markdown_path.write_text(markdown, encoding="utf-8")
        return markdown_path

    @staticmethod
    def _pdf_subdir(document_type: IrsDocumentType) -> str:
        match document_type:
            case IrsDocumentType.FORM:
                return "forms"
            case IrsDocumentType.INSTRUCTION:
                return "instructions"
            case IrsDocumentType.PUBLICATION:
                return "publications"
            case IrsDocumentType.OTHER:
                return "other"

    @staticmethod
    def _validate_year(year: int) -> None:
        if year < 1900 or year > 9999:
            raise ValueError("year must be a four-digit year")


def search_irs_documents(query: str, year: int, *, root: Path | str = DEFAULT_IRS_ROOT, max_pages: int = 5) -> list[IrsDocument]:
    """Function-callable wrapper for IRS document search."""
    return IrsDocumentRepository(root=root).search(query=query, year=year, max_pages=max_pages)


def fetch_irs_document(document: IrsDocument, *, root: Path | str = DEFAULT_IRS_ROOT, overwrite: bool = False) -> IrsStoredDocument:
    """Function-callable wrapper for downloading/caching one IRS PDF."""
    return IrsDocumentRepository(root=root).fetch(document=document, overwrite=overwrite)


def fetch_and_convert_irs_document(
    document: IrsDocument,
    *,
    root: Path | str = DEFAULT_IRS_ROOT,
    overwrite: bool = False,
) -> IrsStoredDocument:
    """Function-callable wrapper for caching one IRS PDF and Markdown when appropriate."""
    return IrsDocumentRepository(root=root).fetch_and_convert(document=document, overwrite=overwrite)


def preload_irs_documents(
    year: int,
    queries: Iterable[str],
    *,
    root: Path | str = DEFAULT_IRS_ROOT,
    max_pages_per_query: int = 2,
    max_results_per_query: int | None = None,
    overwrite: bool = False,
) -> list[IrsStoredDocument]:
    """Function-callable wrapper for upfront IRS document caching."""
    return IrsDocumentRepository(root=root).preload(
        year=year,
        queries=queries,
        max_pages_per_query=max_pages_per_query,
        max_results_per_query=max_results_per_query,
        overwrite=overwrite,
    )
