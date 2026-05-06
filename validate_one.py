# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "lxml>=6.1.0",
# ]
# ///

"""
Validate a single ThermML XML file against the XSD schema and Schematron rules.

Usage:
    python validate_one.py path/to/file.xml
    python validate_one.py path/to/file.xml --schema schema/thermml-schema.xsd
    python validate_one.py path/to/file.xml --schematron schematron/thermml.sch
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lxml import etree

from schematron.run_schematron import (
    DEFAULT_SCHEMATRON_PATH,
    SchematronFinding,
    load_schematron,
    validate_document as validate_schematron_document,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate one ThermML XML file against the XSD schema."
    )
    parser.add_argument("xml_file", help="Path to the XML file to validate.")
    parser.add_argument(
        "--schema",
        default="schema/thermml-schema.xsd",
        help="Path to the XSD schema file (default: schema/thermml-schema.xsd).",
    )
    parser.add_argument(
        "--schematron",
        default=str(DEFAULT_SCHEMATRON_PATH),
        help="Path to the Schematron file (default: schematron/thermml.sch).",
    )
    return parser.parse_args()


def print_schematron_finding(finding: SchematronFinding) -> None:
    print(f"  {finding.level} {finding.rule_id}")
    print(f"    {finding.message}")
    print(f"    Location: {finding.location}")


def main() -> int:
    args = parse_args()
    schema_path = Path(args.schema)
    schematron_path = Path(args.schematron)
    xml_path = Path(args.xml_file)

    if not schema_path.is_file():
        print(f"SCHEMA ERROR: File not found: {schema_path}")
        return 1

    if not schematron_path.is_file():
        print(f"SCHEMATRON ERROR: File not found: {schematron_path}")
        return 1

    if not xml_path.is_file():
        print(f"XML ERROR: File not found: {xml_path}")
        return 1

    try:
        schema_doc = etree.parse(str(schema_path))
        schema = etree.XMLSchema(schema_doc)
    except etree.XMLSchemaParseError as error:
        print(f"SCHEMA ERROR: Failed to parse {schema_path}")
        for entry in error.error_log:
            print(f"  {entry}")
        return 1

    try:
        schematron = load_schematron(schematron_path)
    except etree.XMLSyntaxError as error:
        print(f"SCHEMATRON ERROR: Failed to parse {schematron_path}")
        print(f"  {error}")
        return 1
    except etree.SchematronParseError as error:
        print(f"SCHEMATRON ERROR: Failed to compile {schematron_path}")
        print(f"  {error}")
        return 1

    try:
        doc = etree.parse(str(xml_path))
    except etree.XMLSyntaxError as error:
        print(f"XML ERROR: Failed to parse {xml_path}")
        print(f"  {error}")
        return 1

    xsd_valid = schema.validate(doc)
    schematron_valid, schematron_errors, schematron_warnings = (
        validate_schematron_document(doc, schematron)
    )

    overall_valid = xsd_valid and schematron_valid
    if overall_valid and schematron_warnings:
        print(f"PASS WITH WARNINGS  {xml_path}")
    elif overall_valid:
        print(f"PASS  {xml_path}")
    else:
        print(f"FAIL  {xml_path}")

    print(f"  XSD: {'PASS' if xsd_valid else 'FAIL'}")
    if schematron_errors:
        print("  Schematron: FAIL")
    elif schematron_warnings:
        print("  Schematron: PASS WITH WARNINGS")
    else:
        print("  Schematron: PASS")

    if not xsd_valid:
        seen = set()
        for error in schema.error_log:
            message = str(error)
            if message not in seen:
                seen.add(message)
                print(f"  {message}")

    for finding in schematron_errors:
        print_schematron_finding(finding)

    for finding in schematron_warnings:
        print_schematron_finding(finding)

    return 0 if overall_valid else 1


if __name__ == "__main__":
    sys.exit(main())