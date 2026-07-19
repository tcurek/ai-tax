# Agent Instructions

## Project goal

Build an AI-assisted tax processing application that can eventually help users organize tax documents, answer guided intake questions, and prepare tax outputs.

## Current state

This repository is a minimal Python scaffold using `uv` and a `src/` layout. The app currently prints `Hello, AI Tax!`.

## Development commands

- Sync environment: `uv sync`
- Run app: `uv run ai-tax`
- Run module: `uv run python -m ai_tax.main`
- Run tests: `uv run pytest`

## Coding guidelines

- Use Python 3.12+.
- Keep application code under `src/ai_tax/`.
- Keep tests under `tests/`.
- Prefer small, typed, well-documented functions.
- Do not commit secrets, API keys, tax documents, or personal data.
- Treat all user tax information as highly sensitive.

## Tax/privacy notes

- Do not present generated outputs as professional tax advice without review.
- Prioritize auditability, clear disclaimers, and human review flows.
- Design future document handling with encryption, access controls, and minimal retention.
