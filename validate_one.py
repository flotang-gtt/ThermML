# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "lxml>=6.1.0",
# ]
# ///

"""Validate a ThermML XML file, or the database XML stored in an OPTX file.

The public Python entry point is :func:`validate_file`. Run ``--help`` for the
command-line interface.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from lxml import etree
from lxml.isoschematron import Schematron

from schematron.run_schematron import (
    DEFAULT_SCHEMATRON_PATH,
    SchematronFinding,
    load_schematron,
    validate_document as validate_schematron_document,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_SCHEMA_PATH = ROOT / "schema" / "thermml-schema.xsd"
OPTX_MANIFEST_MEMBER = "manifest.json"


class ValidationLoadError(Exception):
    """An input document or validator could not be loaded."""

    def __init__(
        self, component: str, message: str, details: tuple[str, ...] = ()
    ) -> None:
        super().__init__(message)
        self.component = component
        self.details = details


@dataclass(frozen=True)
class ValidationReport:
    """Structured XSD and Schematron results for one ThermML document."""

    input_path: Path
    document_label: str
    archive_member: str | None
    xsd_valid: bool
    xsd_errors: tuple[str, ...]
    schematron_valid: bool
    schematron_errors: tuple[SchematronFinding, ...]
    schematron_warnings: tuple[SchematronFinding, ...]

    @property
    def is_valid(self) -> bool:
        """Whether the document passed both validation layers."""

        return self.xsd_valid and self.schematron_valid

    @property
    def status(self) -> str:
        """Return ``PASS``, ``PASS WITH WARNINGS``, or ``FAIL``."""

        if not self.is_valid:
            return "FAIL"
        if self.schematron_warnings:
            return "PASS WITH WARNINGS"
        return "PASS"


@dataclass(frozen=True)
class _InputDocument:
    input_path: Path
    document_label: str
    archive_member: str | None
    tree: etree._ElementTree


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a ThermML XML file, or the database XML referenced by "
            "manifest.json in an .optx archive, against XSD and Schematron rules."
        )
    )
    parser.add_argument(
        "input_file",
        help="Path to a ThermML .xml file or an .optx archive.",
    )
    parser.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA_PATH),
        help=f"Path to the XSD schema file (default: {DEFAULT_SCHEMA_PATH}).",
    )
    parser.add_argument(
        "--schematron",
        default=str(DEFAULT_SCHEMATRON_PATH),
        help=f"Path to the Schematron file (default: {DEFAULT_SCHEMATRON_PATH}).",
    )
    return parser.parse_args(argv)


def _parse_xml_bytes(xml_bytes: bytes, document_label: str) -> etree._ElementTree:
    try:
        return etree.parse(BytesIO(xml_bytes), base_url=document_label)
    except etree.XMLSyntaxError as error:
        raise ValidationLoadError(
            "XML", f"Failed to parse {document_label}", (str(error),)
        ) from error


def _load_optx_document(input_path: Path) -> _InputDocument:
    try:
        with ZipFile(input_path) as archive:
            try:
                manifest_bytes = archive.read(OPTX_MANIFEST_MEMBER)
            except KeyError as error:
                raise ValidationLoadError(
                    "OPTX",
                    f"Archive has no {OPTX_MANIFEST_MEMBER}: {input_path}",
                ) from error

            try:
                manifest = json.loads(manifest_bytes)
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise ValidationLoadError(
                    "OPTX",
                    f"Invalid {OPTX_MANIFEST_MEMBER} in {input_path}",
                    (str(error),),
                ) from error

            if not isinstance(manifest, dict):
                raise ValidationLoadError(
                    "OPTX",
                    f"{OPTX_MANIFEST_MEMBER} must contain a JSON object: {input_path}",
                )

            members = manifest.get("members")
            database_member = (
                members.get("database") if isinstance(members, dict) else None
            )
            if not isinstance(database_member, str) or not database_member:
                raise ValidationLoadError(
                    "OPTX",
                    f"{OPTX_MANIFEST_MEMBER} has no string members.database: "
                    f"{input_path}",
                )
            if Path(database_member).suffix.lower() != ".xml":
                raise ValidationLoadError(
                    "OPTX",
                    "The database member referenced by "
                    f"{OPTX_MANIFEST_MEMBER} is not XML: {database_member}",
                )

            try:
                xml_bytes = archive.read(database_member)
            except KeyError as error:
                raise ValidationLoadError(
                    "OPTX",
                    f"Database member not found in {input_path}: {database_member}",
                ) from error
    except (BadZipFile, OSError, RuntimeError) as error:
        raise ValidationLoadError(
            "OPTX", f"Failed to read ZIP archive: {input_path}", (str(error),)
        ) from error

    document_label = f"{input_path}!/{database_member}"
    return _InputDocument(
        input_path=input_path,
        document_label=document_label,
        archive_member=database_member,
        tree=_parse_xml_bytes(xml_bytes, document_label),
    )


def _load_input_document(input_path: Path) -> _InputDocument:
    if not input_path.is_file():
        component = "OPTX" if input_path.suffix.lower() == ".optx" else "XML"
        raise ValidationLoadError(component, f"File not found: {input_path}")

    if input_path.suffix.lower() == ".optx":
        return _load_optx_document(input_path)

    try:
        tree = etree.parse(str(input_path))
    except (OSError, etree.XMLSyntaxError) as error:
        raise ValidationLoadError(
            "XML", f"Failed to parse {input_path}", (str(error),)
        ) from error
    return _InputDocument(input_path, str(input_path), None, tree)


def _load_schema(schema_path: Path) -> etree.XMLSchema:
    if not schema_path.is_file():
        raise ValidationLoadError("SCHEMA", f"File not found: {schema_path}")

    try:
        return etree.XMLSchema(etree.parse(str(schema_path)))
    except OSError as error:
        raise ValidationLoadError(
            "SCHEMA", f"Failed to read {schema_path}", (str(error),)
        ) from error
    except (etree.XMLSyntaxError, etree.XMLSchemaParseError) as error:
        details = tuple(str(entry) for entry in error.error_log) or (str(error),)
        raise ValidationLoadError(
            "SCHEMA", f"Failed to compile {schema_path}", details
        ) from error


def _load_schematron(schematron_path: Path) -> Schematron:
    if not schematron_path.is_file():
        raise ValidationLoadError(
            "SCHEMATRON", f"File not found: {schematron_path}"
        )

    try:
        return load_schematron(schematron_path)
    except (OSError, etree.XMLSyntaxError, etree.SchematronParseError) as error:
        raise ValidationLoadError(
            "SCHEMATRON",
            f"Failed to compile {schematron_path}",
            (str(error),),
        ) from error


def validate_file(
    input_file: str | Path,
    *,
    schema_path: str | Path = DEFAULT_SCHEMA_PATH,
    schematron_path: str | Path = DEFAULT_SCHEMATRON_PATH,
) -> ValidationReport:
    """Validate a ThermML ``.xml`` file or the database in an ``.optx`` file.

    OPTX input is read in memory. Its ``manifest.json`` must provide a string
    ``members.database`` entry naming an XML member in the archive.

    Raises:
        ValidationLoadError: If an input or validation resource cannot be read,
            parsed, or compiled.
    """

    input_document = _load_input_document(Path(input_file))
    schema = _load_schema(Path(schema_path))
    schematron = _load_schematron(Path(schematron_path))

    xsd_valid = schema.validate(input_document.tree)
    xsd_errors = tuple(dict.fromkeys(str(entry) for entry in schema.error_log))
    schematron_valid, schematron_errors, schematron_warnings = (
        validate_schematron_document(input_document.tree, schematron)
    )

    return ValidationReport(
        input_path=input_document.input_path,
        document_label=input_document.document_label,
        archive_member=input_document.archive_member,
        xsd_valid=xsd_valid,
        xsd_errors=xsd_errors,
        schematron_valid=schematron_valid,
        schematron_errors=tuple(schematron_errors),
        schematron_warnings=tuple(schematron_warnings),
    )


def _format_schematron_finding(finding: SchematronFinding) -> list[str]:
    return [
        f"  {finding.level} {finding.rule_id}",
        f"    {finding.message}",
        f"    Location: {finding.location}",
    ]


def format_report(report: ValidationReport) -> str:
    """Render a :class:`ValidationReport` in the CLI's text format."""

    lines = [f"{report.status}  {report.document_label}"]
    lines.append(f"  XSD: {'PASS' if report.xsd_valid else 'FAIL'}")
    if report.schematron_errors:
        lines.append("  Schematron: FAIL")
    elif report.schematron_warnings:
        lines.append("  Schematron: PASS WITH WARNINGS")
    else:
        lines.append("  Schematron: PASS")

    lines.extend(f"  {error}" for error in report.xsd_errors)
    for finding in report.schematron_errors:
        lines.extend(_format_schematron_finding(finding))
    for finding in report.schematron_warnings:
        lines.extend(_format_schematron_finding(finding))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = validate_file(
            args.input_file,
            schema_path=args.schema,
            schematron_path=args.schematron,
        )
    except ValidationLoadError as error:
        print(f"{error.component} ERROR: {error}")
        for detail in error.details:
            print(f"  {detail}")
        return 1

    print(format_report(report))
    return 0 if report.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
