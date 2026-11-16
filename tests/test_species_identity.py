# /// script
# requires-python = ">=3.13"
# dependencies = ["lxml>=6.1.0", "pytest>=9.0.3"]
# ///
"""Names identify species; a repeated formula is only an advisory finding."""

import sys
from copy import deepcopy
from pathlib import Path

import pytest
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schematron.run_schematron import load_schematron, validate_document
from validate_one import format_report, main, validate_file

URI = "http://calphad.org/thermml/v0"
XSI_URI = "http://www.w3.org/2001/XMLSchema-instance"
XSI = f"{{{XSI_URI}}}type"
NS = {"t": URI}
FORMULA_WARNING = "VAL-WARN-SPECIES-DUPLICATE-STOICHIOMETRY"
NATIVE_SPECIES = [("Fe", "Fe"), ("Fe3+", "Fe"), ("Cu", "Cu"), ("Cu2+", "Cu")]


def find(doc, path):
    return doc.xpath(path, namespaces=NS)[0]


@pytest.fixture(scope="module")
def validators():
    return (
        etree.XMLSchema(etree.parse(str(ROOT / "schema/thermml-schema.xsd"))),
        load_schematron(ROOT / "schematron/thermml.sch"),
    )


def replace_phases(phase):
    doc = etree.parse(str(ROOT / "examples/quasichemical.xml"))
    phases = find(doc, "//t:phases")
    phases[:] = [phase]
    return doc


@pytest.fixture
def mqm():
    phase = etree.Element(
        f"{{{URI}}}phase",
        {XSI: "ModifiedQuasichemicalPhaseType", "name": "SUBG", "state": "liquid"},
        nsmap={None: URI, "xsi": XSI_URI},
    )
    species = etree.SubElement(phase, f"{{{URI}}}species")
    for name, composition in NATIVE_SPECIES:
        etree.SubElement(
            species, f"{{{URI}}}specie", name=name, composition=composition,
            charge="1", group="1",
        )
    etree.SubElement(
        species, f"{{{URI}}}specie", name="Cl", composition="Cl", charge="-1", group="2"
    )
    endmembers = etree.SubElement(phase, f"{{{URI}}}endmembers")
    for index, (name, _) in enumerate(NATIVE_SPECIES):
        endmember = etree.SubElement(endmembers, f"{{{URI}}}endmember", name=f"state-{index}")
        constituents = etree.SubElement(endmember, f"{{{URI}}}constituents")
        for constituent in [name, "Cl"]:
            site = etree.SubElement(constituents, f"{{{URI}}}site")
            etree.SubElement(site, f"{{{URI}}}const", species=constituent)
        prop = etree.SubElement(endmember, f"{{{URI}}}property", {XSI: "MQM-G"})
        etree.SubElement(prop, f"{{{URI}}}expr").text = str(index)
        etree.SubElement(prop, f"{{{URI}}}zeta").text = "2.4"
    quadruplets = etree.SubElement(phase, f"{{{URI}}}quadruplets")
    quadruplet = etree.SubElement(quadruplets, f"{{{URI}}}quadruplet", name="native-states")
    for site, name in [("a", "Fe"), ("b", "Fe3+"), ("x", "Cl"), ("y", "Cl")]:
        etree.SubElement(quadruplet, f"{{{URI}}}{site}", species=name, Z="2")
    interactions = etree.SubElement(phase, f"{{{URI}}}interactions")
    for pair in [("Fe", "Fe3+"), ("Cu", "Cu2+")]:
        interaction = etree.SubElement(interactions, f"{{{URI}}}interaction", name=",".join(pair))
        constituents = etree.SubElement(interaction, f"{{{URI}}}constituents")
        mixing = etree.SubElement(constituents, f"{{{URI}}}site")
        for name in pair:
            etree.SubElement(mixing, f"{{{URI}}}const", species=name)
        fixed = etree.SubElement(constituents, f"{{{URI}}}site")
        etree.SubElement(fixed, f"{{{URI}}}const", species="Cl")
        prop = etree.SubElement(interaction, f"{{{URI}}}property", {XSI: "MQM-L-PF"})
        etree.SubElement(prop, f"{{{URI}}}expr", i="0", j="0").text = "1"
    return replace_phases(phase)


def prefix_types(doc):
    root = doc.getroot()
    replacement = etree.Element(root.tag, nsmap={**root.nsmap, "model": URI})
    replacement.attrib.update(root.attrib)
    replacement.extend(deepcopy(list(root)))
    for element in replacement.iter():
        if XSI in element.attrib:
            element.set(XSI, f"model:{element.get(XSI)}")
    return etree.ElementTree(replacement)


@pytest.mark.parametrize("prefixed", [False, True])
def test_native_subg_states_with_identical_formula_and_model_valence_remain_distinct(
    mqm, validators, prefixed
):
    if prefixed:
        mqm = prefix_types(mqm)
    before = etree.tostring(mqm)
    assert validators[0].validate(mqm), str(validators[0].error_log)
    valid, errors, warnings = validate_document(mqm, validators[1])
    assert valid and not errors
    assert [finding.rule_id for finding in warnings] == [FORMULA_WARNING] * 2
    assert all(finding.level == "WARNING" for finding in warnings)
    assert etree.tostring(mqm) == before
    assert mqm.xpath("//t:species/t:specie/@name", namespaces=NS) == [
        *[name for name, _ in NATIVE_SPECIES], "Cl"
    ]
    assert mqm.xpath(
        "//t:endmember/t:constituents/t:site[1]/t:const/@species", namespaces=NS
    ) == [name for name, _ in NATIVE_SPECIES]
    assert mqm.xpath(
        "//t:interaction/t:constituents/t:site[1]/t:const/@species", namespaces=NS
    ) == [name for name, _ in NATIVE_SPECIES]
    assert mqm.xpath("//t:quadruplet/t:b/@species", namespaces=NS) == ["Fe3+"]


def test_cef_same_formula_species_with_distinct_names_are_valid(validators):
    phase = etree.fromstring(f"""
      <phase xmlns="{URI}" xmlns:xsi="{XSI_URI}"
             xsi:type="CEFPhaseType" name="CEF_STATES" state="solid">
        <species>
          <specie name="Fe-high" composition="Fe"/>
          <specie name="Fe-low" composition="Fe"/>
        </species>
        <structure><sublattices multiplicities="1">
          <site constituents="Fe-high Fe-low"/>
        </sublattices></structure>
        <endmembers>
          <endmember name="high"><constituents><site><const species="Fe-high"/></site></constituents>
            <property xsi:type="G"><expr>0</expr></property></endmember>
          <endmember name="low"><constituents><site><const species="Fe-low"/></site></constituents>
            <property xsi:type="G"><expr>1</expr></property></endmember>
        </endmembers>
      </phase>
    """)
    doc = replace_phases(phase)
    assert validators[0].validate(doc), str(validators[0].error_log)
    valid, errors, warnings = validate_document(doc, validators[1])
    assert valid and not errors
    assert [finding.rule_id for finding in warnings] == [FORMULA_WARNING]


def test_duplicate_native_species_names_remain_invalid(mqm, validators):
    species = find(mqm, "//t:species")
    species.append(deepcopy(species[0]))
    assert not validators[0].validate(mqm)
    assert "phaseSpeciesKey" in str(validators[0].error_log)


@pytest.mark.parametrize("path", [
    "//t:endmember//t:const", "//t:interaction//t:const", "//t:quadruplet/t:a",
])
def test_unknown_species_references_remain_invalid(mqm, validators, path):
    find(mqm, path).set("species", "unknown-native-name")
    assert not validators[0].validate(mqm)
    assert "key-sequence" in str(validators[0].error_log)


def test_formula_warning_normalizes_whitespace_ignores_missing_formula_and_scopes_phase():
    doc = etree.ElementTree(etree.fromstring(f"""
      <database xmlns="{URI}"><phases>
        <phase name="first"><species>
          <specie name="a" composition=" Fe " charge=" +1 "/>
          <specie name="b" composition="Fe" charge="+1"/>
          <specie name="missing" charge="+1"/>
          <specie name="empty" composition="   " charge="+1"/>
          <specie name="different-charge" composition="Fe" charge="+2"/>
        </species></phase>
        <phase name="second"><species>
          <specie name="a" composition="Fe" charge="+1"/>
        </species></phase>
      </phases></database>
    """))
    validator = load_schematron(ROOT / "schematron/rules/species-duplicate-stoichiometry/rule.sch")
    valid, errors, warnings = validate_document(doc, validator)
    assert valid and not errors
    assert [finding.rule_id for finding in warnings] == [FORMULA_WARNING]
    assert "b" in warnings[0].message


@pytest.mark.parametrize("family,rule_id,count", [
    ("species-duplicate-stoichiometry", FORMULA_WARNING, 2),
    ("ionic-liquid-constituents", "VAL-WARN-IONIC-DUPLICATE-SPECIES", 3),
])
def test_standalone_formula_warning_fixtures_are_advisory(family, rule_id, count):
    folder = ROOT / "schematron/rules" / family
    validator = load_schematron(folder / "rule.sch")
    valid, errors, warnings = validate_document(
        etree.parse(str(folder / "valid.xml")), validator
    )
    assert valid and not errors and not warnings
    valid, errors, warnings = validate_document(
        etree.parse(str(folder / "warning.xml")), validator
    )
    assert valid and not errors
    assert [finding.rule_id for finding in warnings] == [rule_id] * count
    assert all(finding.level == "WARNING" for finding in warnings)


def test_public_validator_accepts_native_species_with_formula_warnings(mqm, tmp_path, capsys):
    path = tmp_path / "native-subg.xml"
    mqm.write(str(path), encoding="UTF-8", xml_declaration=True)
    report = validate_file(path)
    assert report.xsd_valid and report.schematron_valid and report.is_valid
    assert report.status == "PASS WITH WARNINGS"
    assert not report.schematron_errors
    assert [finding.rule_id for finding in report.schematron_warnings] == [FORMULA_WARNING] * 2
    assert "PASS WITH WARNINGS" in format_report(report)
    assert main([str(path)]) == 0
    output = capsys.readouterr().out
    assert "PASS WITH WARNINGS" in output
    assert FORMULA_WARNING in output
