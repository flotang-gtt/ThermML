"""
Validate all ThermML example XML files against the XSD schema.

Usage:
    uv run --with lxml python validate_all.py
"""
import glob
import sys
from lxml import etree


def main():
    schema_path = "schema/thermml-schema.xsd"
    examples_pattern = "examples/*.xml"

    # Parse the schema
    try:
        schema_doc = etree.parse(schema_path)
        schema = etree.XMLSchema(schema_doc)
    except etree.XMLSchemaParseError as e:
        print(f"SCHEMA ERROR: Failed to parse {schema_path}")
        for error in e.error_log:
            print(f"  {error}")
        return 1

    xml_files = sorted(glob.glob(examples_pattern))
    if not xml_files:
        print(f"No XML files found matching {examples_pattern}")
        return 1

    print(f"Validating {len(xml_files)} files against {schema_path}\n")

    passed = 0
    failed = 0
    errors_by_file = {}

    for xml_file in xml_files:
        try:
            doc = etree.parse(xml_file)
            if schema.validate(doc):
                print(f"  PASS  {xml_file}")
                passed += 1
            else:
                print(f"  FAIL  {xml_file}")
                errors_by_file[xml_file] = list(schema.error_log)
                failed += 1
        except etree.XMLSyntaxError as e:
            print(f"  FAIL  {xml_file} (XML syntax error)")
            errors_by_file[xml_file] = [str(e)]
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")

    if errors_by_file:
        print(f"\n{'='*60}")
        print("Error details:\n")
        for xml_file, errors in errors_by_file.items():
            print(f"--- {xml_file} ---")
            seen = set()
            for error in errors:
                msg = str(error)
                # Deduplicate identical error messages
                if msg not in seen:
                    seen.add(msg)
                    print(f"  {msg}")
            print()

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
