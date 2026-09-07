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
NEW_FAMILIES = [
    "cef-constituent-occupancy",
    "expression-range-consistency",
    "ionic-liquid-constituents",
    "sublattice-multiplicities",
]


def find(doc, xpath):
    return doc.xpath(xpath, namespaces=NS)[0]


@pytest.fixture(scope="module")
def validators():
    return (
        etree.XMLSchema(etree.parse(str(ROOT / "schema/thermml-schema.xsd"))),
        load_schematron(ROOT / "schematron/thermml.sch"),
    )


@pytest.fixture
def ionic():
    return etree.parse(str(ROOT / "tests/fixtures/ionic-liquid-minimal.xml"))


@pytest.fixture
def cef():
    return etree.parse(str(ROOT / "examples/simple_solution.xml"))


def error_ids(doc, validators):
    return {f.rule_id for f in validate_document(doc, validators[1])[1]}


def assert_valid(doc, validators):
    assert validators[0].validate(doc), str(validators[0].error_log)
    assert not error_ids(doc, validators)


@pytest.mark.parametrize("family", NEW_FAMILIES)
def test_standalone_fixtures_cover_every_new_assertion(family):
    folder = RULES / family
    validator = load_schematron(folder / "rule.sch")
    valid, errors, warnings = validate_document(
        etree.parse(str(folder / "valid.xml")), validator
    )
    assert valid and not errors and not warnings
    valid, errors, warnings = validate_document(
        etree.parse(str(folder / "invalid.xml")), validator
    )
    expected = {
        rule["id"]
        for rule in json.loads((folder / "catalog.json").read_text())["rules"]
    }
    assert not valid
    assert {finding.rule_id for finding in errors} == expected


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


ALL_FIXTURES = sorted(RULES.glob("*/*.xml"))


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


def test_ionic_example_and_explicit_ionic_types_are_valid(ionic, validators):
    find(ionic, "//t:endmember").set(XSI, "IonicLiquidEndmemberType")
    assert_valid(ionic, validators)
    assert_valid(with_type_prefix(ionic), validators)


def test_lindwall_ionic_example_preserves_source_model(validators):
    doc = etree.parse(str(ROOT / "examples/ionic-liquid.xml"))
    assert_valid(doc, validators)
    assert doc.xpath("//t:systemComponent/@symbol", namespaces=NS) == ["Fe", "Al", "O"]
    phase = find(doc, "//t:phase")
    assert phase.get("name") == "IONIC_LIQ"
    assert phase.xpath("./t:constituents/*/t:specie/@name", namespaces=NS) == [
        "Al[+3]",
        "Fe[+2]",
        "O[-2]",
        "Va",
        "AlO1.5",
        "FeO1.5",
    ]
    endmembers = phase.xpath("./t:endmembers/t:endmember", namespaces=NS)
    assert len(endmembers) == 6
    neutrals = [e for e in endmembers if len(find(e, "./t:constituents")) == 1]
    assert {e.get("name") for e in neutrals} == {"AlO1.5", "FeO1.5"}
    functions = doc.xpath("//t:globalExpressions/t:expression", namespaces=NS)
    assert len(functions) == 6
    assert all(e.get(XSI) == "FunctionTypeExpr" for e in functions)
    expected_sites = {
        "Al+3Va": ["Al[+3]", "Va"],
        "Fe+2Va": ["Fe[+2]", "Va"],
        "Al+3O-2": ["Al[+3]", "O[-2]"],
        "Fe+2O-2": ["Fe[+2]", "O[-2]"],
        "AlO1.5": ["AlO1.5"],
        "FeO1.5": ["FeO1.5"],
    }
    assert {e.get("name") for e in endmembers} == set(expected_sites)
    assert {f.get("name") for f in functions} == {
        name + "#IONIC_LIQ" for name in expected_sites
    }
    for endmember in endmembers:
        name = endmember.get("name")
        assert endmember.xpath(
            "./t:constituents/t:site/t:const/@species", namespaces=NS
        ) == expected_sites[name]
        assert find(endmember, "./t:property/t:expr").text == (
            "+1*{" + name + "#IONIC_LIQ}"
        )
    assert all("DAT lines" in find(e, "./t:comment").text for e in endmembers)
    text = etree.tostring(doc).decode()
    assert "T**7" in text and "T**(-9)" in text
    interactions = phase.xpath("./t:interactions/t:interaction", namespaces=NS)
    assert len(interactions) == 10
    assert [
        len(i.xpath("./t:property/t:expr", namespaces=NS)) for i in interactions
    ] == [1, 3, 1, 1, 1, 2, 1, 2, 1, 1]
    assert interactions[0].xpath(
        "./t:constituents/t:site/t:const/@species", namespaces=NS
    ) == ["Al[+3]", "Fe[+2]", "O[-2]", "Va"]
    assert find(interactions[0], "./t:property/t:expr").text == "-740767.460"


@pytest.mark.parametrize(
    "mutation",
    [
        "missing-site",
        "extra-site",
        "multiple-occupants",
        "empty-composition",
        "blank-composition",
        "cef-endmember",
    ],
)
def test_ionic_xsd_rejects_invalid_shapes(ionic, validators, mutation):
    constituents = find(ionic, "//t:endmember/t:constituents")
    if mutation == "missing-site":
        constituents.clear()
    elif mutation == "extra-site":
        constituents.append(deepcopy(constituents[0]))
    elif mutation == "multiple-occupants":
        constituents[0].append(deepcopy(constituents[0][0]))
    elif mutation in {"empty-composition", "blank-composition"}:
        find(ionic, "//t:cations/t:specie").set(
            "composition", "" if mutation == "empty-composition" else " \t "
        )
    else:
        find(ionic, "//t:endmember").set(XSI, "CEFEndmemberType")
    assert not validators[0].validate(ionic)


def test_ionic_swapped_sites_fail_semantic_validation(ionic, validators):
    sites = find(ionic, "//t:endmember/t:constituents")
    sites[0][0].set("species", "C[4-]")
    sites[1][0].set("species", "Fe[2+]")
    assert validators[0].validate(ionic)
    assert "VAL-ERR-IONIC-CONSTITUENT-SITE-MEMBERSHIP" in error_ids(ionic, validators)


@pytest.mark.parametrize("group", ["cations", "anions", "neutrals"])
def test_ionic_duplicate_species_fail_but_distinct_charges_pass(
    ionic, validators, group
):
    container = find(ionic, f"//t:constituents/t:{group}")
    duplicate = deepcopy(container[0])
    duplicate.set("name", "other-name")
    container.append(duplicate)
    assert validators[0].validate(ionic)
    assert "VAL-ERR-IONIC-DUPLICATE-SPECIES" in error_ids(ionic, validators)
    if group != "neutrals":
        duplicate.set("charge", "+3" if group == "cations" else "-3")
        assert_valid(ionic, validators)


def add_ionic_interaction(ionic):
    phase = find(ionic, "//t:phase")
    interactions = etree.SubElement(phase, f"{{{URI}}}interactions")
    interaction = etree.SubElement(interactions, f"{{{URI}}}interaction")
    array = deepcopy(find(ionic, "//t:endmember/t:constituents"))
    interaction.append(array)
    etree.SubElement(array[1], f"{{{URI}}}const", species="Va")
    return interaction


def test_ionic_interactions_allow_mixing_but_enforce_site_membership(ionic, validators):
    interaction = add_ionic_interaction(ionic)
    interaction.set(XSI, "IonicLiquidInteractionType")
    assert_valid(ionic, validators)
    interaction[0][0][0].set("species", "Va")
    assert validators[0].validate(ionic)
    assert "VAL-ERR-IONIC-CONSTITUENT-SITE-MEMBERSHIP" in error_ids(ionic, validators)


@pytest.mark.parametrize("mutation", ["missing-site", "extra-site", "cef-type"])
def test_ionic_interaction_shape_is_specialized(ionic, validators, mutation):
    interaction = add_ionic_interaction(ionic)
    if mutation == "missing-site":
        interaction[0].clear()
    elif mutation == "extra-site":
        interaction[0].append(deepcopy(interaction[0][0]))
    else:
        interaction.set(XSI, "CEFInteractionType")
    assert not validators[0].validate(ionic)


@pytest.mark.parametrize("state", ["liquid", "gas"])
def test_ionic_duplicate_endmembers_remain_allowed(ionic, validators, state):
    find(ionic, "//t:phase").set("state", state)
    endmembers = find(ionic, "//t:endmembers")
    duplicate = deepcopy(endmembers[0])
    duplicate.set("name", "another-state")
    endmembers.append(duplicate)
    assert_valid(ionic, validators)


def test_explicit_cef_endmember_type_is_preserved(cef, validators):
    find(cef, "//t:endmember").set(XSI, "CEFEndmemberType")
    assert_valid(cef, validators)


def test_prefixed_cef_type_cannot_bypass_cartesian_check(cef, validators):
    endmembers = find(cef, "//t:endmembers")
    endmembers.remove(endmembers[-1])
    doc = with_type_prefix(cef)
    assert validators[0].validate(doc)
    assert "VAL-ERR-CEF-ENDMEMBER-CARTESIAN-COUNT-MISMATCH" in error_ids(
        doc, validators
    )


@pytest.mark.parametrize("phase_type", ["CEFPhaseType", "CEFOrderedPhaseType"])
def test_cef_wrong_site_and_multiple_occupants_are_rejected(
    cef, validators, phase_type
):
    phase = find(cef, "//t:phase")
    if phase_type == "CEFOrderedPhaseType":
        parent = deepcopy(phase)
        parent.set("name", "DISORDERED")
        phase.getparent().append(parent)
        phase.set("disorderedPhase", "DISORDERED")
    phase.set(XSI, phase_type)
    const = find(phase, "./t:endmembers/t:endmember/t:constituents/t:site")
    const.append(etree.Element(f"{{{URI}}}const", species="C"))
    assert validators[0].validate(cef)
    assert {
        "VAL-ERR-CEF-ENDMEMBER-SINGLE-OCCUPANCY",
        "VAL-ERR-CEF-CONSTITUENT-SITE-MEMBERSHIP",
    } <= error_ids(cef, validators)


def test_occupancy_rule_has_no_eight_site_limit():
    doc = etree.parse(str(RULES / "cef-constituent-occupancy/valid.xml"))
    sites = find(doc, "//t:sublattices")
    array = find(doc, "//t:endmember/t:constituents")
    for _ in range(7):
        sites.append(deepcopy(sites[0]))
        array.append(deepcopy(array[0]))
    interactions = find(doc, "//t:interactions")
    interactions.getparent().remove(interactions)
    validator = load_schematron(RULES / "cef-constituent-occupancy/rule.sch")
    assert validate_document(doc, validator)[0]
    array[-1][0].set("species", "Va")
    assert not validate_document(doc, validator)[0]


def test_occupancy_matches_whole_tokens_and_normalizes_whitespace():
    doc = etree.parse(str(RULES / "cef-constituent-occupancy/valid.xml"))
    sites = find(doc, "//t:sublattices")
    sites[0].set("constituents", "\tFe  Mn\n")
    validator = load_schematron(RULES / "cef-constituent-occupancy/rule.sch")
    assert validate_document(doc, validator)[0]
    sites[0].set("constituents", "Fe2 Mn")
    assert not validate_document(doc, validator)[0]


@pytest.mark.parametrize("values", ["-1 1", "0 1", "", "NaN 1"])
def test_multiplicities_must_be_nonempty_positive_decimals(cef, validators, values):
    find(cef, "//t:sublattices").set("multiplicities", values)
    assert not validators[0].validate(cef)


def test_multiplicity_count_and_whitespace(cef, validators):
    sites = find(cef, "//t:sublattices")
    sites.set("multiplicities", " \t0.5\n 2 ")
    assert_valid(cef, validators)
    sites.set("multiplicities", "0.5")
    assert validators[0].validate(cef)
    assert "VAL-ERR-SUBLATTICE-MULTIPLICITY-COUNT" in error_ids(cef, validators)


@pytest.mark.parametrize(
    "function_type",
    ["FunctionTypeExpr", "RangedTemperatureExpr", "HSCPTemperatureExpr"],
)
def test_range_bounds_apply_to_all_global_expression_shapes(
    cef, validators, function_type
):
    expression = find(cef, "//t:globalExpressions/t:expression")
    expression.clear()
    expression.set("name", "range-probe")
    expression.set(XSI, function_type)
    if function_type == "HSCPTemperatureExpr":
        etree.SubElement(expression, f"{{{URI}}}h298", value="0")
        etree.SubElement(expression, f"{{{URI}}}s298", value="0")
    interval = etree.SubElement(expression, f"{{{URI}}}range", low="1000", high="200")
    if function_type == "HSCPTemperatureExpr":
        etree.SubElement(interval, f"{{{URI}}}term", coeff="1", fun="T^0")
    else:
        interval.text = "1"
    assert validators[0].validate(cef)
    assert "VAL-ERR-EXPRESSION-RANGE-BOUNDS" in error_ids(cef, validators)


@pytest.mark.parametrize(
    ("bounds", "expected"),
    [
        ([(200, 500), (500, 1000)], set()),
        ([(200, 500), (800, 1000)], set()),
        ([(200, 500), (300, 300), (500, 500), (500, 1000)], set()),
        ([(500, 500), (500, 500)], set()),
        ([(1000, 200)], {"VAL-ERR-EXPRESSION-RANGE-BOUNDS"}),
        ([(500, 1000), (200, 400)], {"VAL-ERR-EXPRESSION-RANGE-ORDER"}),
        ([(200, 500), (400, 1000)], {"VAL-ERR-EXPRESSION-RANGE-OVERLAP"}),
        ([(200, 1000), (300, 300), (500, 800)], {"VAL-ERR-EXPRESSION-RANGE-OVERLAP"}),
    ],
)
def test_range_boundaries_gaps_and_nonadjacent_overlap(bounds, expected):
    doc = etree.parse(str(RULES / "expression-range-consistency/valid.xml"))
    function = find(doc, "//t:function")
    function.clear()
    for low, high in bounds:
        etree.SubElement(
            function, f"{{{URI}}}range", low=str(low), high=str(high)
        ).text = "1"
    validator = load_schematron(RULES / "expression-range-consistency/rule.sch")
    _, errors, _ = validate_document(doc, validator)
    assert {error.rule_id for error in errors} == expected


def test_gas_placeholders_remain_valid_without_duplicate_gibbs_warnings(validators):
    doc = etree.parse(str(RULES / "gas-endmember-consistency/valid.xml"))
    for prop in doc.xpath("//t:endmember/t:property", namespaces=NS):
        prop.getparent().remove(prop)
    valid, errors, warnings = validate_document(doc, validators[1])
    assert valid and not errors and not warnings


@pytest.mark.parametrize("target", ["endmember", "interaction"])
@pytest.mark.parametrize("invalid_species", [None, "Va", "Fe[2+]", "vacancy-alias"])
def test_neutral_only_ionic_terms(ionic, validators, invalid_species, target):
    find(ionic, "//t:anions").clear()
    neutrals = find(ionic, "//t:neutrals")
    etree.SubElement(
        neutrals, f"{{{URI}}}specie", name="C", composition="C", charge="0"
    )
    endmembers = find(ionic, "//t:endmembers")
    endmember = deepcopy(endmembers[0])
    endmembers.clear()
    endmembers.append(endmember)
    array = find(endmember, "./t:constituents")
    array.remove(array[0])
    array[0][0].set("species", "C")
    phase = find(ionic, "//t:phase")
    interactions = etree.SubElement(phase, f"{{{URI}}}interactions")
    interaction = etree.SubElement(interactions, f"{{{URI}}}interaction")
    interaction.append(deepcopy(array))
    assert_valid(ionic, validators)
    if invalid_species:
        if invalid_species == "vacancy-alias":
            find(neutrals, "./t:specie[@name='Va']").set("name", "vacancy-alias")
        tested_array = (
            array if target == "endmember" else find(interaction, "./t:constituents")
        )
        tested_array[0][0].set("species", invalid_species)
        assert validators[0].validate(ionic), str(validators[0].error_log)
        assert "VAL-ERR-IONIC-CONSTITUENT-SITE-MEMBERSHIP" in error_ids(
            ionic, validators
        )
    else:
        neutrals.getparent().remove(neutrals)
        assert not validators[0].validate(ionic) or error_ids(ionic, validators)
