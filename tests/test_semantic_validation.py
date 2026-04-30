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