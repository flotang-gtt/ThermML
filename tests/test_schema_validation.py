# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "lxml>=6.1.0",
#     "pytest>=9.0.3",
# ]
# ///

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

from lxml import etree
import pytest


NS = {
    "t": "http://calphad.org/thermml/v0",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "thermml-schema.xsd"
EXAMPLE_PATH = Path(__file__).resolve().parents[1] / "examples" / "quasichemical.xml"
BASIC_EXAMPLE_PATH = Path(__file__).resolve().parents[1] / "examples" / "basic-example.xml"
SIMPLE_SOLUTION_PATH = Path(__file__).resolve().parents[1] / "examples" / "simple_solution.xml"


@pytest.fixture
def schema() -> etree.XMLSchema:
    return etree.XMLSchema(etree.parse(str(SCHEMA_PATH)))


@pytest.fixture
def example_doc() -> etree._ElementTree:
    return etree.parse(str(EXAMPLE_PATH))


@pytest.fixture
def basic_example_doc() -> etree._ElementTree:
    return etree.parse(str(BASIC_EXAMPLE_PATH))


@pytest.fixture
def simple_solution_doc() -> etree._ElementTree:
    return etree.parse(str(SIMPLE_SOLUTION_PATH))


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


def test_phase_stoichiometry_components_must_exist(
    schema: etree.XMLSchema, basic_example_doc: etree._ElementTree, tmp_path: Path
) -> None:
    stoich = basic_example_doc.xpath(
        './t:phases/t:phase[1]/t:stoichiometry/t:stoich[1]', namespaces=NS
    )[0]
    stoich.attrib["component"] = "Xx"

    is_valid, errors = validate_tree(
        schema, basic_example_doc, tmp_path, "bad-stoichiometry-component.xml"
    )

    assert not is_valid
    assert_has_error(
        errors,
        type_name="SCHEMAV_CVC_IDC",
        contains="phaseStoichiometryComponentMustExist",
    )


def test_ordered_phase_must_reference_declared_disordered_phase(
    schema: etree.XMLSchema, simple_solution_doc: etree._ElementTree, tmp_path: Path
) -> None:
    phases = simple_solution_doc.xpath('./t:phases', namespaces=NS)[0]
    ordered_phase = deepcopy(simple_solution_doc.xpath('./t:phases/t:phase[1]', namespaces=NS)[0])
    ordered_phase.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] = 'CEFOrderedPhaseType'
    ordered_phase.attrib['name'] = 'FCC_A1_ORDERED'
    ordered_phase.attrib['disorderedPhase'] = 'MISSING_PHASE'
    phases.append(ordered_phase)

    is_valid, errors = validate_tree(
        schema, simple_solution_doc, tmp_path, 'bad-ordered-phase.xml'
    )

    assert not is_valid
    assert_has_error(
        errors,
        type_name='SCHEMAV_CVC_IDC',
        contains='orderedPhaseMustReferenceDeclaredDisorderedPhase',
    )


def test_phase_function_references_must_exist(
    schema: etree.XMLSchema, basic_example_doc: etree._ElementTree, tmp_path: Path
) -> None:
    function_ref = basic_example_doc.xpath(
        './t:phases/t:phase[1]/t:property/t:ref', namespaces=NS
    )[0]
    function_ref.attrib['name'] = 'Missing#Function'

    is_valid, errors = validate_tree(
        schema, basic_example_doc, tmp_path, 'bad-function-reference.xml'
    )

    assert not is_valid
    assert_has_error(
        errors,
        type_name='SCHEMAV_CVC_IDC',
        contains='phaseFunctionReferenceMustExist',
    )


def test_ternary_site_locator_must_be_scalar(
    schema: etree.XMLSchema, example_doc: etree._ElementTree, tmp_path: Path
) -> None:
    phase = get_mqm_phase(example_doc)
    const = phase.xpath(
        './t:ternaryInterpolations/t:interpolation[1]/t:constituents/t:site[1]/t:const[1]',
        namespaces=NS,
    )[0]
    const.attrib['site'] = 'i j'

    is_valid, errors = validate_tree(
        schema, example_doc, tmp_path, 'bad-ternary-site-locator.xml'
    )

    assert not is_valid
    assert_has_error(
        errors,
        type_name='SCHEMAV_CVC_ENUMERATION_VALID',
        contains='i',
    )


def test_function_of_must_use_known_scalar_variable_set(
    schema: etree.XMLSchema, basic_example_doc: etree._ElementTree, tmp_path: Path
) -> None:
    property_element = basic_example_doc.xpath(
        './t:phases/t:phase[1]/t:property[1]', namespaces=NS
    )[0]
    property_element.attrib['function_of'] = 'T P'

    is_valid, errors = validate_tree(
        schema, basic_example_doc, tmp_path, 'bad-function-of.xml'
    )

    assert not is_valid
    assert_has_error(
        errors,
        type_name='SCHEMAV_CVC_ENUMERATION_VALID',
        contains='T,P',
    )


def test_mqm_species_group_may_use_any_positive_integer(
    schema: etree.XMLSchema, example_doc: etree._ElementTree, tmp_path: Path
) -> None:
    phase = get_mqm_phase(example_doc)
    specie = phase.xpath('./t:species/t:specie[1]', namespaces=NS)[0]
    specie.attrib['group'] = '3'

    is_valid, errors = validate_tree(schema, example_doc, tmp_path, 'mqm-group-3.xml')

    assert is_valid, [f"{error.type_name}: {error.message}" for error in errors]


def test_mqm_species_group_must_be_positive_integer(
    schema: etree.XMLSchema, example_doc: etree._ElementTree, tmp_path: Path
) -> None:
    phase = get_mqm_phase(example_doc)
    specie = phase.xpath('./t:species/t:specie[1]', namespaces=NS)[0]
    specie.attrib['group'] = '0'

    is_valid, errors = validate_tree(schema, example_doc, tmp_path, 'bad-mqm-group.xml')

    assert not is_valid
    assert_has_error(
        errors,
        type_name='SCHEMAV_CVC_DATATYPE_VALID_1_2_1',
        contains='MQMSpeciesGroupType',
    )


def test_sublattice_multiplicities_must_be_numeric_list(
    schema: etree.XMLSchema, simple_solution_doc: etree._ElementTree, tmp_path: Path
) -> None:
    sublattices = simple_solution_doc.xpath(
        './t:phases/t:phase[1]/t:structure/t:sublattices', namespaces=NS
    )[0]
    sublattices.attrib['multiplicities'] = '1.0 two'

    is_valid, errors = validate_tree(
        schema, simple_solution_doc, tmp_path, 'bad-multiplicities.xml'
    )

    assert not is_valid
    assert any(
        error.type_name == 'SCHEMAV_CVC_DATATYPE_VALID_1_2_1' for error in errors
    ), [f"{error.type_name}: {error.message}" for error in errors]
    assert any(
        'list type' in error.message and 'multiplicities' in error.message
        for error in errors
    ), [f"{error.type_name}: {error.message}" for error in errors]


def test_cef_magnetic_structure_accepts_renamed_factor_fields(
    schema: etree.XMLSchema, simple_solution_doc: etree._ElementTree, tmp_path: Path
) -> None:
    structure = simple_solution_doc.xpath(
        './t:phases/t:phase[1]/t:structure', namespaces=NS
    )[0]
    magnetic = etree.fromstring(
        '''
        <magnetic xmlns="http://calphad.org/thermml/v0"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  xsi:type="IHJMagneticType">
            <AFMFactor>1 - 0.5*T</AFMFactor>
            <structureFactorP>0.28</structureFactorP>
        </magnetic>
        '''
    )
    structure.insert(1, magnetic)

    is_valid, errors = validate_tree(
        schema, simple_solution_doc, tmp_path, 'cef-magnetic-renamed-factors.xml'
    )

    assert is_valid, [f"{error.type_name}: {error.message}" for error in errors]


def test_phase_name_must_not_contain_whitespace(
    schema: etree.XMLSchema, basic_example_doc: etree._ElementTree, tmp_path: Path
) -> None:
    phase = basic_example_doc.xpath('./t:phases/t:phase[1]', namespaces=NS)[0]
    phase.attrib['name'] = 'SiO2 quartz'

    is_valid, errors = validate_tree(schema, basic_example_doc, tmp_path, 'bad-phase-name.xml')

    assert not is_valid
    assert any(
        error.type_name == 'SCHEMAV_CVC_PATTERN_VALID' for error in errors
    ), [f"{error.type_name}: {error.message}" for error in errors]
    assert any(
        'name' in error.message and 'value' in error.message for error in errors
    ), [f"{error.type_name}: {error.message}" for error in errors]


def test_cef_specie_name_must_not_contain_whitespace(
    schema: etree.XMLSchema, simple_solution_doc: etree._ElementTree, tmp_path: Path
) -> None:
    specie = simple_solution_doc.xpath(
        './t:phases/t:phase[1]/t:species/t:specie[1]', namespaces=NS
    )[0]
    specie.attrib['name'] = 'Fe metal'

    is_valid, errors = validate_tree(schema, simple_solution_doc, tmp_path, 'bad-cef-specie-name.xml')

    assert not is_valid
    assert any(
        error.type_name == 'SCHEMAV_CVC_PATTERN_VALID' for error in errors
    ), [f"{error.type_name}: {error.message}" for error in errors]


def test_mqm_specie_name_must_not_contain_whitespace(
    schema: etree.XMLSchema, example_doc: etree._ElementTree, tmp_path: Path
) -> None:
    phase = get_mqm_phase(example_doc)
    specie = phase.xpath('./t:species/t:specie[1]', namespaces=NS)[0]
    specie.attrib['name'] = 'Cu [1+]'

    is_valid, errors = validate_tree(schema, example_doc, tmp_path, 'bad-mqm-specie-name.xml')

    assert not is_valid
    assert any(
        error.type_name == 'SCHEMAV_CVC_PATTERN_VALID' for error in errors
    ), [f"{error.type_name}: {error.message}" for error in errors]


def test_metadata_created_must_use_iso_date_format(
    schema: etree.XMLSchema, example_doc: etree._ElementTree, tmp_path: Path
) -> None:
    created = example_doc.xpath('./t:metadata/t:created', namespaces=NS)[0]
    created.text = '2025/04/24'

    is_valid, errors = validate_tree(schema, example_doc, tmp_path, 'bad-created-date.xml')

    assert not is_valid
    assert any(
        error.type_name == 'SCHEMAV_CVC_DATATYPE_VALID_1_2_1' for error in errors
    ), [f"{error.type_name}: {error.message}" for error in errors]
    assert any(
        'created' in error.message and '2025/04/24' in error.message for error in errors
    ), [f"{error.type_name}: {error.message}" for error in errors]


def test_system_component_refstate_must_not_contain_whitespace(
    schema: etree.XMLSchema, basic_example_doc: etree._ElementTree, tmp_path: Path
) -> None:
    component = basic_example_doc.xpath(
        './t:systemComponents/t:systemComponent[@symbol="Mo"]', namespaces=NS
    )[0]
    component.attrib['refstate'] = 'BCC A2'

    is_valid, errors = validate_tree(schema, basic_example_doc, tmp_path, 'bad-refstate.xml')

    assert not is_valid
    assert any(
        error.type_name == 'SCHEMAV_CVC_DATATYPE_VALID_1_2_3' for error in errors
    ), [f"{error.type_name}: {error.message}" for error in errors]
    assert any(
        'refstate' in error.message and 'OptionalNoWhitespaceString' in error.message
        for error in errors
    ), [f"{error.type_name}: {error.message}" for error in errors]


def test_system_component_refstate_may_be_empty(
    schema: etree.XMLSchema, basic_example_doc: etree._ElementTree, tmp_path: Path
) -> None:
    component = basic_example_doc.xpath(
        './t:systemComponents/t:systemComponent[@symbol="Mo"]', namespaces=NS
    )[0]
    component.attrib['refstate'] = ''

    is_valid, errors = validate_tree(
        schema, basic_example_doc, tmp_path, 'empty-refstate.xml'
    )

    assert is_valid, [f"{error.type_name}: {error.message}" for error in errors]


def test_revision_version_element_may_precede_date(
    schema: etree.XMLSchema, basic_example_doc: etree._ElementTree, tmp_path: Path
) -> None:
    metadata = basic_example_doc.xpath('./t:metadata', namespaces=NS)[0]
    revisions = metadata.xpath('./t:revisions', namespaces=NS)[0]
    revision = etree.SubElement(revisions, '{http://calphad.org/thermml/v0}revision')
    version = etree.SubElement(revision, '{http://calphad.org/thermml/v0}version')
    version.text = '1.0'
    date = etree.SubElement(revision, '{http://calphad.org/thermml/v0}date')
    date.text = '2025-04-01'
    author = etree.SubElement(revision, '{http://calphad.org/thermml/v0}author')
    author.text = 'Test Author'
    description = etree.SubElement(revision, '{http://calphad.org/thermml/v0}description')
    description.text = 'Schema regression test.'

    is_valid, errors = validate_tree(
        schema, basic_example_doc, tmp_path, 'revision-version-first.xml'
    )

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


@pytest.mark.parametrize(
    ("target_xpath", "constraint_name", "file_name"),
    [
        (
            './t:quadruplets/t:quadruplet[1]/t:a',
            'phaseQuadrupletASpeciesMustExist',
            'bad-quadruplet-a.xml',
        ),
        (
            './t:quadruplets/t:quadruplet[1]/t:b',
            'phaseQuadrupletBSpeciesMustExist',
            'bad-quadruplet-b.xml',
        ),
        (
            './t:quadruplets/t:quadruplet[1]/t:x',
            'phaseQuadrupletXSpeciesMustExist',
            'bad-quadruplet-x.xml',
        ),
        (
            './t:quadruplets/t:quadruplet[1]/t:y',
            'phaseQuadrupletYSpeciesMustExist',
            'bad-quadruplet-y.xml',
        ),
    ],
)
def test_phase_quadruplet_species_references_must_exist(
    schema: etree.XMLSchema,
    example_doc: etree._ElementTree,
    tmp_path: Path,
    target_xpath: str,
    constraint_name: str,
    file_name: str,
) -> None:
    phase = get_mqm_phase(example_doc)
    site = phase.xpath(target_xpath, namespaces=NS)[0]
    site.attrib['species'] = 'P'

    is_valid, errors = validate_tree(schema, example_doc, tmp_path, file_name)

    assert not is_valid
    assert_has_error(
        errors,
        type_name='SCHEMAV_CVC_IDC',
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
        property_element, '{http://calphad.org/thermml/v0}selected'
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
