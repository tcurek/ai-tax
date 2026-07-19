# AI Tax

A simple Python project for an AI-assisted app that will help process and complete taxes.

> Early scaffold only: this app currently prints a hello-world message.

## Tech stack

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for modern Python environment and dependency management

## Getting started

Install `uv` if you do not already have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create/sync the environment:

```bash
uv sync
```

Run the app:

```bash
uv run ai-tax
```

Or run the module directly:

```bash
uv run python -m ai_tax.main
```

Expected output:

```text
Hello, AI Tax!
Source tax documents dir: tax-documents
```

## Configuration

The app loads YAML config from:

```text
config/app.yaml
```

You can start from the example file:

```bash
cp config/app.example.yaml config/app.yaml
```

Or point to a different config file:

```bash
AI_TAX_CONFIG=/path/to/app.yaml uv run ai-tax
```

Current config fields:

- `source_tax_documents_dir`: directory containing source tax documents
- `output_files_dir`: directory where generated output files should be written
- `rounding_precision`: currency rounding mode; either `nearest_cent` or `whole_dollar`

Taxpayer details such as name, address, and SSN are intentionally not configured upfront. Future agents should derive needed taxpayer info from provided tax documents and guided user intake.

`config/app.yaml`, `tax-documents/`, and `tax-outputs/` are ignored by git because they may contain sensitive tax data.

## Project layout

```text
.
├── pyproject.toml
├── README.md
├── AGENTS.md
├── .python-version
├── config/
│   └── app.example.yaml
├── src/
│   └── ai_tax/
│       ├── __init__.py
│       ├── config.py
│       ├── main.py
│       ├── agents/
│       └── tools/
└── tests/
```

## Next steps

- Define the user workflow for tax intake and document upload.
- Choose an AI provider and data privacy/security approach.
- Add tests and CI.
- Add a web or CLI interface for tax document processing.

## Disclaimer

This project is not tax, legal, or financial advice. Any future tax assistance features should be reviewed by qualified tax professionals and designed with strict privacy/security controls.
