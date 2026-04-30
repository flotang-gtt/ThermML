from __future__ import annotations

from pathlib import Path

from lxml import etree

from semantic_validation import validate_document_semantics


NS = {"t": "http://calphad.org/thermml/0.1"}
SIMPLE_SOLUTION_PATH = Path(__file__).resolve().parents[1] / "examples" / "simple_solution.xml"
BASIC_EXAMPLE_PATH = Path(__file__).resolve().parents[1] / "examples" / "basic-example.xml"


def test_simple_solution_example_is_semantically_valid() -> None:
    doc = etree.parse(str(SIMPLE_SOLUTION_PATH))

    assert validate_document_semantics(doc) == []


def test_basic_example_is_semantically_valid() -> None:
    doc = etree.parse(str(BASIC_EXAMPLE_PATH))

    assert validate_document_semantics(doc) == []


def test_semantic_validation_rejects_malformed_range_expression() -> None:
    doc = etree.parse(str(SIMPLE_SOLUTION_PATH))
    range_node = doc.xpath(
        './t:globalExpressions/t:expression[@name="Mn#FCC_A1"]/t:range[1]',
        namespaces=NS,
    )[0]
    range_node.text = (
        '-3439.3  +  131.884*T  +  -24.5177*T*LN(T)0.006*T**2  +  69600*T**(-1)'
    )

    errors = validate_document_semantics(doc)

    assert len(errors) == 1
    assert 'Invalid range expression syntax' in errors[0].message
    assert 'Unexpected token' in errors[0].message


def test_semantic_validation_rejects_inverted_range_bounds() -> None:
    doc = etree.parse(str(SIMPLE_SOLUTION_PATH))
    range_node = doc.xpath(
        './t:globalExpressions/t:expression[@name="Fe#HSER"]/t:range[1]',
        namespaces=NS,
    )[0]
    range_node.attrib['low'] = '1811.0'
    range_node.attrib['high'] = '298.15'

    errors = validate_document_semantics(doc)

    assert len(errors) == 1
    assert 'Invalid range bounds' in errors[0].message


def test_semantic_validation_rejects_overlapping_ranges() -> None:
    doc = etree.parse(str(SIMPLE_SOLUTION_PATH))
    range_node = doc.xpath(
        './t:globalExpressions/t:expression[@name="Fe#HSER"]/t:range[2]',
        namespaces=NS,
    )[0]
    range_node.attrib['low'] = '1700.0'

    errors = validate_document_semantics(doc)

    assert len(errors) == 1
    assert 'Overlapping or out-of-order ranges' in errors[0].message


def test_semantic_validation_rejects_unknown_symbolic_range_reference() -> None:
    doc = etree.parse(str(SIMPLE_SOLUTION_PATH))
    range_node = doc.xpath(
        './t:globalExpressions/t:expression[@name="Fe#FCC_A1"]/t:range[1]',
        namespaces=NS,
    )[0]
    range_node.text = '-1462.4 + 8.282*T + Missing#HSER'

    errors = validate_document_semantics(doc)

    assert len(errors) == 1
    assert "Unknown symbolic reference 'Missing#HSER'" in errors[0].message