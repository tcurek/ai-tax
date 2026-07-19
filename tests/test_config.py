from pathlib import Path

from ai_tax.config import AppConfig, load_config


def test_load_config_returns_defaults_for_missing_file(tmp_path: Path) -> None:
    config = load_config(tmp_path / "missing.yaml")

    assert config == AppConfig()


def test_load_config_reads_yaml_settings(tmp_path: Path) -> None:
    config_path = tmp_path / "app.yaml"
    config_path.write_text(
        "source_tax_documents_dir: custom-documents\n"
        "output_files_dir: custom-outputs\n"
        "rounding_precision: whole_dollar\n",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.source_tax_documents_dir == Path("custom-documents")
    assert config.output_files_dir == Path("custom-outputs")
    assert config.rounding_precision == "whole_dollar"
