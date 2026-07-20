# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "lxml>=6.1.0",
#     "pytest>=9.0.3",
# ]
# ///

from __future__ import annotations

import json
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validate_one import (  # noqa: E402
    ValidationLoadError,
    format_report,
    main,
    validate_file,
)


BASIC_EXAMPLE = ROOT / "examples" / "basic-example.xml"


def write_optx(
    path: Path,
    *,
    database_member: str = "database.xml",
    database_bytes: bytes | None = None,
    manifest: object | None = None,
) -> None:
    if manifest is None:
        manifest = {"members": {"database": database_member}}
    if database_bytes is None:
        database_bytes = BASIC_EXAMPLE.read_bytes()

    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        archive.writestr(database_member, database_bytes)


def test_validate_file_accepts_manifest_selected_optx_database(tmp_path: Path) -> None:
    optx_path = tmp_path / "saved-run.optx"
    write_optx(optx_path, database_member="nested/thermml.xml")

    report = validate_file(optx_path)

    assert report.is_valid
    assert report.status == "PASS"
    assert report.input_path == optx_path
    assert report.archive_member == "nested/thermml.xml"
    assert report.document_label == f"{optx_path}!/nested/thermml.xml"


def test_validate_file_preserves_plain_xml_support() -> None:
    report = validate_file(BASIC_EXAMPLE)

    assert report.is_valid
    assert report.archive_member is None
    assert report.document_label == str(BASIC_EXAMPLE)


def test_optx_requires_manifest_database_entry(tmp_path: Path) -> None:
    optx_path = tmp_path / "missing-database.optx"
    write_optx(optx_path, manifest={"members": {}})

    with pytest.raises(ValidationLoadError, match="members.database") as caught:
        validate_file(optx_path)

    assert caught.value.component == "OPTX"


def test_optx_reports_malformed_embedded_xml(tmp_path: Path) -> None:
    optx_path = tmp_path / "malformed.optx"
    write_optx(optx_path, database_bytes=b"<database>")

    with pytest.raises(ValidationLoadError, match="database.xml") as caught:
        validate_file(optx_path)

    assert caught.value.component == "XML"


def test_cli_report_names_archive_and_member(tmp_path: Path, capsys) -> None:
    optx_path = tmp_path / "saved-run.optx"
    write_optx(optx_path)

    exit_code = main([str(optx_path)])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert f"PASS  {optx_path}!/database.xml" in output
    assert "  XSD: PASS" in output
    assert "  Schematron: PASS" in output


def test_format_report_exposes_both_validation_layers() -> None:
    report = validate_file(BASIC_EXAMPLE)

    rendered = format_report(report)

    assert rendered.startswith(f"PASS  {BASIC_EXAMPLE}")
    assert "  XSD: PASS" in rendered
    assert "  Schematron: PASS" in rendered
