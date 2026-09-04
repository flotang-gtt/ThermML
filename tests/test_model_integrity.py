# /// script
# requires-python = ">=3.13"
# dependencies = ["lxml>=6.1.0", "pytest>=9.0.3"]
# ///

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schematron.run_schematron import load_schematron, validate_document

URI = "http://calphad.org/thermml/v0"
NS = {"t": URI}
XSI = "{http://www.w3.org/2001/XMLSchema-instance}type"
RULES = ROOT / "schematron/rules"
NEW_FAMILIES = []


ALL_FIXTURES = sorted(RULES.glob("*/*.xml"))


def find(doc, xpath):
    return doc.xpath(xpath, namespaces=NS)[0]



@pytest.fixture(scope="module")
def validators():
    return (
        etree.XMLSchema(etree.parse(str(ROOT / "schema/thermml-schema.xsd"))),
        load_schematron(ROOT / "schematron/thermml.sch"),
    )



@pytest.fixture
def cef():
    return etree.parse(str(ROOT / "examples/simple_solution.xml"))



def error_ids(doc, validators):
    return {f.rule_id for f in validate_document(doc, validators[1])[1]}



def assert_valid(doc, validators):
    assert validators[0].validate(doc), str(validators[0].error_log)
    assert not error_ids(doc, validators)



def with_type_prefix(doc, prefix="tm", whitespace=False):
    root = doc.getroot()
    replacement = etree.Element(root.tag, nsmap={**root.nsmap, prefix: URI})
    replacement.attrib.update(root.attrib)
    replacement.text = root.text
    replacement.extend(deepcopy(list(root)))
    for el in replacement.iter():
        if XSI in el.attrib:
            local = el.get(XSI).strip().split(":")[-1]
            el.set(XSI, f"  {prefix}:{local}  " if whitespace else f"{prefix}:{local}")
    return etree.ElementTree(replacement)



@pytest.mark.parametrize(
    "fixture", ALL_FIXTURES, ids=lambda p: f"{p.parent.name}/{p.name}"
)
def test_type_prefixes_preserve_all_rule_findings(fixture):
    validator = load_schematron(fixture.parent / "rule.sch")
    doc = etree.parse(str(fixture))

    def result(tree):
        valid, errors, warnings = validate_document(tree, validator)
        return valid, [f.rule_id for f in errors], [f.rule_id for f in warnings]

    expected = result(doc)
    assert result(with_type_prefix(doc)) == expected
    assert result(with_type_prefix(doc, prefix="other", whitespace=True)) == expected



def test_type_namespace_is_checked_not_just_local_name():
    doc = etree.parse(str(RULES / "cef-endmember-cartesian-count/invalid.xml"))
    doc = with_type_prefix(doc)
    xml = etree.tostring(doc).replace(
        b'xmlns:tm="http://calphad.org/thermml/v0"', b'xmlns:tm="urn:foreign"'
    )
    validator = load_schematron(RULES / "cef-endmember-cartesian-count/rule.sch")
    valid, errors, warnings = validate_document(
        etree.ElementTree(etree.fromstring(xml)), validator
    )
    assert valid and not errors and not warnings



def test_prefixed_cef_type_cannot_bypass_cartesian_check(cef, validators):
    endmembers = find(cef, "//t:endmembers")
    endmembers.remove(endmembers[-1])
    doc = with_type_prefix(cef)
    assert validators[0].validate(doc)
    assert "VAL-ERR-CEF-ENDMEMBER-CARTESIAN-COUNT-MISMATCH" in error_ids(
        doc, validators
    )
