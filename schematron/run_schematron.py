# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "lxml>=6.1.0",
# ]
# ///

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import lxml.etree as etree
from lxml.isoschematron import Schematron


SVRL_NS = {"svrl": "http://purl.oclc.org/dsdl/svrl"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate one XML file against the bundled Schematron sample."
    )
    parser.add_argument("xml_file", help="Path to the XML file to validate.")
    parser.add_argument(
        "--schematron",
        default=str(Path(__file__).with_name("thermml.sch")),
        help="Path to the Schematron .sch file.",
    )
    return parser.parse_args()


def load_schematron(schematron_path: Path) -> Schematron:
    schematron_doc = etree.parse(str(schematron_path))
    return Schematron(schematron_doc, store_report=True)


def iter_failed_asserts(report: etree._ElementTree):
    yield from report.xpath("//svrl:failed-assert", namespaces=SVRL_NS)


def iter_successful_reports(report: etree._ElementTree):
    yield from report.xpath("//svrl:successful-report", namespaces=SVRL_NS)


def render_message(entry: etree._Element) -> str:
    return " ".join(
        chunk.strip()
        for chunk in entry.xpath("./svrl:text//text()", namespaces=SVRL_NS)
        if chunk.strip()
    )


def resolve_location_node(
    doc: etree._ElementTree, location: str
) -> etree._Element | None:
    if not location or location == "<unknown-location>":
        return None

    try:
        matches = doc.xpath(location)
    except etree.XPathError:
        return None

    for match in matches:
        if isinstance(match, etree._Element):
            return match
    return None


def render_location(doc: etree._ElementTree, location: str) -> str:
    node = resolve_location_node(doc, location)
    if node is None:
        return location

    parts: list[str] = []
    if node.sourceline is not None:
        parts.append(f"line {node.sourceline}")

    phase_name = node.xpath("string(ancestor-or-self::t:phase[1]/@name)", namespaces={"t": "http://calphad.org/thermml/0.1"})
    if phase_name:
        parts.append(f"phase={phase_name}")

    tag_name = etree.QName(node.tag).localname
    parts.append(f"element={tag_name}")

    return ", ".join(parts)


def print_finding(level: str, entry: etree._Element, doc: etree._ElementTree) -> None:
    rule_id = entry.get("id", "<unlabeled-rule>")
    location = entry.get("location", "<unknown-location>")
    text = render_message(entry)
    print(f"  {level} {rule_id}")
    print(f"    {text}")
    print(f"    Location: {render_location(doc, location)}")


def main() -> int:
    args = parse_args()
    xml_path = Path(args.xml_file)
    schematron_path = Path(args.schematron)

    if not schematron_path.is_file():
        print(f"SCHEMATRON ERROR: File not found: {schematron_path}")
        return 1

    if not xml_path.is_file():
        print(f"XML ERROR: File not found: {xml_path}")
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

    is_valid = schematron.validate(doc)
    report = schematron.validation_report
    if report is None:
        if is_valid:
            print(f"PASS  {xml_path}")
            return 0

        print(f"FAIL  {xml_path}")
        print("  Schematron validation failed, but no SVRL report was produced.")
        return 1

    failed_asserts = list(iter_failed_asserts(report))
    successful_reports = list(iter_successful_reports(report))

    if failed_asserts:
        print(f"FAIL  {xml_path}")
        for failed_assert in failed_asserts:
            print_finding("ERROR", failed_assert, doc)

        if successful_reports:
            for successful_report in successful_reports:
                print_finding(
                    successful_report.get("role", "WARNING").upper(),
                    successful_report,
                    doc,
                )
        return 1

    if successful_reports:
        print(f"PASS WITH WARNINGS  {xml_path}")
        for successful_report in successful_reports:
            print_finding(
                successful_report.get("role", "WARNING").upper(),
                successful_report,
                doc,
            )
        return 0

    print(f"PASS  {xml_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())