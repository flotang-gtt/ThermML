# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "lxml>=6.1.0",
#     "pytest>=9.0.3",
# ]
# ///

from __future__ import annotations

from pathlib import Path
import sys

from lxml import etree
import pytest


NS = {
    "t": "http://calphad.org/thermml/0.1",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "thermml-schema.xsd"
EXAMPLE_PATH = Path(__file__).resolve().parents[1] / "examples" / "quasichemical.xml"


@pytest.fixture
def schema() -> etree.XMLSchema:
    return etree.XMLSchema(etree.parse(str(SCHEMA_PATH)))


@pytest.fixture
def example_doc() -> etree._ElementTree:
    return etree.parse(str(EXAMPLE_PATH))


def validate_tree(
    schema: etree.XMLSchema, doc: etree._ElementTree, tmp_path: Path, file_name: str
) -> tuple[bool, list[etree._LogEntry]]:
    xml_path = tmp_path / file_name
    doc.write(
        str(xml_path),
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=True,
    )
    reparsed = etree.parse(str(xml_path))
    is_valid = schema.validate(reparsed)
    return is_valid, list(schema.error_log)


def assert_has_error(
    errors: list[etree._LogEntry],
    *,
    type_name: str,
    contains: str,
) -> None:
    assert any(
        error.type_name == type_name and contains in error.message for error in errors
    ), [f"{error.type_name}: {error.message}" for error in errors]


def get_mqm_phase(doc: etree._ElementTree):
    return doc.xpath(
        './t:phases/t:phase[@xsi:type="ModifiedQuasichemicalPhaseType"]',
        namespaces=NS,
    )[0]


def test_quasichemical_example_is_valid(
    schema: etree.XMLSchema, example_doc: etree._ElementTree, tmp_path: Path
) -> None:
    is_valid, errors = validate_tree(schema, example_doc, tmp_path, "valid.xml")

    assert is_valid, [f"{error.type_name}: {error.message}" for error in errors]


@pytest.mark.parametrize(
    ("target_xpath", "constraint_name", "file_name"),
    [
        (
            './t:endmembers/t:endmember[1]/t:constituents/t:site[2]/t:const',
            'phaseEndmemberConstituentSpeciesMustExist',
            'bad-endmember.xml',
        ),
        (
            './t:interactions/t:interaction[1]/t:constituents/t:site[1]/t:const[1]',
            'phaseInteractionConstituentSpeciesMustExist',
            'bad-interaction.xml',
        ),
        (
            './t:ternaryInterpolations/t:interpolation[1]/t:constituents/t:site[2]/t:const[1]',
            'phaseTernaryInterpolationConstituentSpeciesMustExist',
            'bad-ternary-interpolation.xml',
        ),
    ],
)
def test_phase_constituent_species_references_must_exist(
    schema: etree.XMLSchema,
    example_doc: etree._ElementTree,
    tmp_path: Path,
    target_xpath: str,
    constraint_name: str,
    file_name: str,
) -> None:
    phase = get_mqm_phase(example_doc)
    const = phase.xpath(target_xpath, namespaces=NS)[0]
    const.attrib["species"] = "P"

    is_valid, errors = validate_tree(schema, example_doc, tmp_path, file_name)

    assert not is_valid
    assert_has_error(
        errors,
        type_name="SCHEMAV_CVC_IDC",
        contains=constraint_name,
    )


def test_selected_must_reference_current_interaction_constituent(
    schema: etree.XMLSchema, example_doc: etree._ElementTree, tmp_path: Path
) -> None:
    phase = get_mqm_phase(example_doc)
    property_element = phase.xpath(
        './t:interactions/t:interaction[1]/t:property[@xsi:type="MQM-L-PF"]',
        namespaces=NS,
    )[0]
    selected = etree.SubElement(
        property_element, '{http://calphad.org/thermml/0.1}selected'
    )
    selected.text = 'Fe[2+]'

    is_valid, errors = validate_tree(schema, example_doc, tmp_path, "bad-selected.xml")

    assert not is_valid
    assert_has_error(
        errors,
        type_name="SCHEMAV_CVC_IDC",
        contains="mqmInteractionSelectedMustReferenceConstituent",
    )


def test_mqm_rs_variant_must_use_known_enum_value(
    schema: etree.XMLSchema, example_doc: etree._ElementTree, tmp_path: Path
) -> None:
    phase = get_mqm_phase(example_doc)
    property_element = phase.xpath(
        './t:interactions/t:interaction[1]/t:property[@xsi:type="MQM-L-PF"]',
        namespaces=NS,
    )[0]
    property_element.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] = 'MQM-L-RS'
    property_element.attrib['variant'] = 'WRONG'

    exprs = property_element.xpath('./t:expr', namespaces=NS)
    for extra_expr in exprs[1:]:
        property_element.remove(extra_expr)
    exprs[0].attrib['k'] = '1'

    is_valid, errors = validate_tree(schema, example_doc, tmp_path, "bad-variant.xml")

    assert not is_valid
    assert_has_error(
        errors,
        type_name="SCHEMAV_CVC_ENUMERATION_VALID",
        contains="A-BX-BY",
    )


if __name__ == "__main__":
    sys.exit(pytest.main([str(Path(__file__).resolve()), *sys.argv[1:]]))
