"""
Validate a single ThermML XML file against the XSD schema.

Usage:
    python validate_one.py path/to/file.xml
    python validate_one.py path/to/file.xml --schema schema/thermml-schema.xsd
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lxml import etree

from semantic_validation import validate_document_semantics


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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    schema_path = Path(args.schema)
    xml_path = Path(args.xml_file)

    if not schema_path.is_file():
        print(f"SCHEMA ERROR: File not found: {schema_path}")
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
        doc = etree.parse(str(xml_path))
    except etree.XMLSyntaxError as error:
        print(f"XML ERROR: Failed to parse {xml_path}")
        print(f"  {error}")
        return 1

    if schema.validate(doc):
        semantic_errors = validate_document_semantics(doc)
        if semantic_errors:
            print(f"FAIL  {xml_path}")
            for error in semantic_errors:
                print(f"  {error.path}: {error.message}")
            return 1
        print(f"PASS  {xml_path}")
        return 0

    print(f"FAIL  {xml_path}")
    seen = set()
    for error in schema.error_log:
        message = str(error)
        if message not in seen:
            seen.add(message)
            print(f"  {message}")
    return 1


if __name__ == "__main__":
    sys.exit(main())