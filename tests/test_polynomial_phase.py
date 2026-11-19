# /// script
# requires-python = ">=3.13"
# dependencies = ["lxml>=6.1.0", "pytest>=9.0.3"]
# ///
"""Regression coverage of the polynomial wire format and its semantic boundary."""

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

URI = 'http://calphad.org/thermml/v0'
XSI = '{http://www.w3.org/2001/XMLSchema-instance}type'
NS = {'t': URI}
FOLDER = ROOT / 'schematron/rules/polynomial-phase-semantics'


def find(doc, path):
    return doc.xpath(path, namespaces=NS)[0]


@pytest.fixture(scope='module')
def validators():
    return (
        etree.XMLSchema(etree.parse(str(ROOT / 'schema/thermml-schema.xsd'))),
        load_schematron(ROOT / 'schematron/thermml.sch'),
    )


@pytest.fixture
def doc():
    return etree.parse(str(ROOT / 'examples/single-sublattice-polynomial.xml'))


def assert_clean(doc, validators):
    assert validators[0].validate(doc), str(validators[0].error_log)
    valid, errors, warnings = validate_document(doc, validators[1])
    assert valid and not errors and not warnings, (errors, warnings)


def remove(doc, path):
    el = find(doc, path)
    el.getparent().remove(el)


def test_complete_example(doc, validators):
    assert_clean(doc, validators)


@pytest.mark.parametrize('filename', ['ternary-interpolation.xsd', 'single-sublattice-polynomial-phase.xsd'])
def test_new_schema_modules_compile_independently(filename):
    etree.XMLSchema(etree.parse(str(ROOT / 'schema/phases' / filename)))


@pytest.mark.parametrize('magnetic', [False, True])
def test_single_species_and_all_zero_magnetic_variant(doc, validators, magnetic):
    for path in ['//t:interactions', '//t:ternaryInterpolations']:
        remove(doc, path)
    for path in ['//t:species', '//t:endmembers']:
        el = find(doc, path)
        for child in list(el)[1:]:
            el.remove(child)
    find(doc, '//t:sublattices/t:site').set('constituents', 'Fe')
    remove(doc, '//t:property[@*[local-name()="type"]="M"]')
    if not magnetic:
        remove(doc, '//t:magnetic')
    assert_clean(doc, validators)


@pytest.mark.parametrize('value', ['0', '-1', 'NaN', 'INF', '-INF', '1e999'])
def test_coordination_number_must_be_finite_positive(doc, validators, value):
    find(doc, '//t:endmember').set('coordinationNumber', value)
    assert not validators[0].validate(doc)


@pytest.mark.parametrize('value', ['0.125', '1', '1e2'])
def test_fractional_and_exponent_notation_coordination_numbers(doc, validators, value):
    find(doc, '//t:endmember').set('coordinationNumber', value)
    assert_clean(doc, validators)


@pytest.mark.parametrize('value', ['1', '3', '2147483648', '4294967296'])
def test_group_is_positive_integer_without_consumer_storage_limit(doc, validators, value):
    find(doc, '//t:specie').set('group', value)
    assert_clean(doc, validators)


@pytest.mark.parametrize('attribute,value', [('group', '0'), ('group', '-1'), ('group', '-2147483648'), ('group', '1.2')])
def test_invalid_groups(doc, validators, attribute, value):
    find(doc, '//t:specie').set(attribute, value)
    assert not validators[0].validate(doc)


@pytest.mark.parametrize('value', ['-1', '1.5', '4294967296'])
def test_exponent_unsigned_int32_domain(doc, validators, value):
    find(doc, '//t:property[@*[local-name()="type"]="PolynomialL"]/t:expr').set('i', value)
    assert not validators[0].validate(doc)


@pytest.mark.parametrize('attribute', ['rank', 'range', 'selected'])
def test_polynomial_expression_rejects_rk_and_range_attributes(doc, validators, attribute):
    find(doc, '//t:property[@*[local-name()="type"]="PolynomialL"]/t:expr').set(attribute, '0')
    assert not validators[0].validate(doc)


@pytest.mark.parametrize('arity', [2, 3, 4])
@pytest.mark.parametrize('k,l', [(False, False), (True, False), (False, True), (True, True)])
def test_optional_zero_exponents_match_arity(doc, validators, arity, k, l):
    expr = find(doc, f'//t:interaction[count(t:constituents/t:site/t:const)={arity}]/t:property/t:expr')
    for key, present in [('k', k), ('l', l)]:
        expr.attrib.pop(key, None)
        if present:
            expr.set(key, '0')
    assert validators[0].validate(doc), str(validators[0].error_log)
    errors = {e.rule_id for e in validate_document(doc, validators[1])[1]}
    expected_valid = (k, l) == {2: (False, False), 3: (True, False), 4: (True, True)}[arity]
    assert ('VAL-ERR-POLYNOMIAL-EXPONENT-ARITY' not in errors) == expected_valid


@pytest.mark.parametrize('path,attribute,value,rule_id', [
    ('//t:sublattices/t:site', 'constituents', 'Fe Ni Co', 'STRUCTURE-SPECIES-COUNT'),
    ('//t:sublattices/t:site', 'constituents', 'Fe Fe Co Mn', 'STRUCTURE-SPECIES-MEMBERSHIP'),
    ('//t:sublattices/t:site', 'constituents', 'Fe Ni Co Unknown', 'STRUCTURE-SPECIES-MEMBERSHIP'),
    ('//t:endmember', 'name', 'renamed', 'ENDMEMBER-NAME'),
    ('//t:specie', 'composition', '', 'SPECIES-COMPOSITION'),
    ('//t:interaction/t:constituents/t:site/t:const[2]', 'species', 'Fe', 'INTERACTION-DISTINCT-SPECIES'),
    ('//t:interpolation//t:const[2]', 'site', 'i', 'INTERPOLATION-LABELS'),
])
def test_semantic_attribute_failures(doc, validators, path, attribute, value, rule_id):
    find(doc, path).set(attribute, value)
    assert validators[0].validate(doc), str(validators[0].error_log)
    errors = {e.rule_id for e in validate_document(doc, validators[1])[1]}
    assert f'VAL-ERR-POLYNOMIAL-{rule_id}' in errors


@pytest.mark.parametrize('path,rule_id', [
    ('//t:magnetic', 'MAGNETIC-STRUCTURE'),
    ('//t:endmember[last()]', 'ENDMEMBER-COVERAGE'),
    ('//t:interaction/t:constituents/t:site/t:const[2]', 'INTERACTION-ARITY'),
])
def test_semantic_missing_data(doc, validators, path, rule_id):
    remove(doc, path)
    assert validators[0].validate(doc), str(validators[0].error_log)
    errors = {e.rule_id for e in validate_document(doc, validators[1])[1]}
    assert f'VAL-ERR-POLYNOMIAL-{rule_id}' in errors


@pytest.mark.parametrize('property_type', ['L', 'G', 'M', 'MQM-L-PF'])
def test_reject_other_interaction_properties(doc, validators, property_type):
    prop = find(doc, '//t:interaction/t:property')
    prop.set(XSI, property_type)
    errors = {e.rule_id for e in validate_document(doc, validators[1])[1]}
    assert 'VAL-ERR-POLYNOMIAL-INTERACTION-PROPERTY' in errors


@pytest.mark.parametrize('where', ['same-property', 'other-property', 'other-interaction'])
def test_duplicates_ignore_name_coefficient_and_integer_spelling(doc, validators, where):
    prop = find(doc, '//t:interaction/t:property')
    expr = deepcopy(prop[0])
    expr.set('i', '000')
    expr.set('j', '02')
    expr.text = '9999'
    if where == 'same-property':
        prop.append(expr)
    elif where == 'other-property':
        other = etree.SubElement(prop.getparent(), f'{{{URI}}}property', {XSI: 'PolynomialL'})
        other.append(expr)
    else:
        interaction = deepcopy(prop.getparent())
        interaction.set('name', 'different-name')
        other = find(interaction, './t:property')
        other.clear()
        other.set(XSI, 'PolynomialL')
        other.append(expr)
        prop.getparent().getparent().append(interaction)
    assert validators[0].validate(doc), str(validators[0].error_log)
    errors = {e.rule_id for e in validate_document(doc, validators[1])[1]}
    assert 'VAL-ERR-POLYNOMIAL-DUPLICATE-TERM' in errors


def test_reversed_constituents_and_separate_phases_remain_distinct(doc, validators):
    interaction = deepcopy(find(doc, '//t:interaction'))
    site = find(interaction, './t:constituents/t:site')
    site[:] = reversed(list(site))
    find(doc, '//t:interactions').append(interaction)
    phase = deepcopy(find(doc, '//t:phase'))
    phase.set('name', 'ANOTHER')
    find(doc, '//t:phases').append(phase)
    assert_clean(doc, validators)


def test_distinct_powers_can_span_properties_and_named_interactions(doc, validators):
    prop = find(doc, '//t:interaction/t:property')
    expr = prop[-1]
    prop.remove(expr)
    other = etree.SubElement(prop.getparent(), f'{{{URI}}}property', {XSI: 'PolynomialL'})
    other.append(expr)
    interaction = deepcopy(prop.getparent())
    interaction.set('name', 'other-name')
    for e in interaction.xpath('./t:property/t:expr[@i]', namespaces=NS):
        e.set('i', '4294967295')
    find(doc, '//t:interactions').append(interaction)
    assert_clean(doc, validators)


@pytest.mark.parametrize('where', ['endmember', 'other-phase'])
def test_polynomial_property_cannot_escape_its_model(doc, validators, where):
    prop = deepcopy(find(doc, '//t:interaction/t:property'))
    if where == 'endmember':
        find(doc, '//t:endmember').append(prop)
    else:
        other = etree.parse(str(ROOT / 'examples/simple_solution.xml'))
        find(other, '//t:interaction').append(prop)
        doc = other
    assert validators[0].validate(doc), str(validators[0].error_log)
    errors = {e.rule_id for e in validate_document(doc, validators[1])[1]}
    assert 'VAL-ERR-POLYNOMIAL-PROPERTY-SCOPE' in errors


@pytest.mark.parametrize('alias_mode', ['site', 'siteIndex', 'both'])
@pytest.mark.parametrize('example', ['single-sublattice-polynomial.xml', 'subq-interaction-models.xml'])
def test_canonical_locator_and_third_species_toop(validators, alias_mode, example):
    doc = etree.parse(str(ROOT / 'examples' / example))
    for const in doc.xpath('//t:interpolation//t:const[@site]', namespaces=NS):
        if alias_mode != 'site':
            const.set('siteIndex', const.get('site'))
        if alias_mode == 'siteIndex':
            del const.attrib['site']
    # ij is allowed to select the third constituent k.
    ij = find(doc, '//t:interpolation/t:ij')
    ij.clear()
    ij.set(XSI, 'Toop')
    etree.SubElement(ij, f'{{{URI}}}constant').text = 'k'
    if alias_mode == 'site':
        assert_clean(doc, validators)
    else:
        assert not validators[0].validate(doc)
        errors = {e.rule_id for e in validate_document(doc, validators[1])[1]}
        assert 'VAL-ERR-TERNARY-INTERPOLATION-LOCATOR-ATTRIBUTE' in errors


def test_standalone_fixtures_cover_all_polynomial_rules():
    validator = load_schematron(FOLDER / 'rule.sch')
    valid, errors, warnings = validate_document(etree.parse(str(FOLDER / 'valid.xml')), validator)
    assert valid and not errors and not warnings
    valid, errors, _ = validate_document(etree.parse(str(FOLDER / 'invalid.xml')), validator)
    expected = {r['id'] for r in json.loads((FOLDER / 'catalog.json').read_text())['rules']}
    assert not valid and {e.rule_id for e in errors} == expected


@pytest.mark.parametrize('path,attribute', [
    ('//t:specie', 'group'),
    ('//t:endmember', 'coordinationNumber'),
    ('//t:sublattices', 'multiplicities'),
])
def test_required_model_metadata(doc, validators, path, attribute):
    del find(doc, path).attrib[attribute]
    assert not validators[0].validate(doc)


@pytest.mark.parametrize('path', ['//t:sublattices/t:site', '//t:interpolation/t:constituents/t:site'])
def test_second_site_rejected_by_xsd(doc, validators, path):
    site = find(doc, path)
    site.getparent().append(deepcopy(site))
    assert not validators[0].validate(doc)


@pytest.mark.parametrize('path', ['//t:interaction/t:constituents/t:site', '//t:endmember/t:constituents/t:site'])
def test_second_constituent_site_rejected_by_shared_rules(doc, validators, path):
    site = find(doc, path)
    site.getparent().append(deepcopy(site))
    assert validators[0].validate(doc), str(validators[0].error_log)
    assert not validate_document(doc, validators[1])[0]


def test_nonunit_multiplicity_rejected(doc, validators):
    find(doc, '//t:sublattices').set('multiplicities', '2')
    assert not validators[0].validate(doc)


@pytest.mark.parametrize('path', ['//t:endmember//t:const', '//t:interaction//t:const', '//t:interpolation//t:const'])
def test_constituent_references_must_exist(doc, validators, path):
    find(doc, path).set('species', 'unknown')
    assert not validators[0].validate(doc)


def test_duplicate_species_names_rejected_by_xsd(doc, validators):
    species = find(doc, '//t:species')
    species.append(deepcopy(species[0]))
    assert not validators[0].validate(doc)


def test_structure_token_spacing_and_order_are_not_species_identity(doc, validators):
    find(doc, '//t:sublattices/t:site').set('constituents', '  Mn\tCo\nNi   Fe  ')
    assert_clean(doc, validators)


@pytest.mark.parametrize('path,rule_id', [
    ('//t:interpolation//t:const[2]', 'VAL-ERR-TERNARY-INTERPOLATION-DISTINCT-SPECIES'),
    ('//t:interpolation//t:const[1]', 'VAL-ERR-TERNARY-INTERPOLATION-LOCATOR-ATTRIBUTE'),
    ('//t:interpolation/t:ij/t:constant', 'VAL-ERR-TERNARY-INTERPOLATION-TOOP-LOCATOR'),
])
@pytest.mark.parametrize('both_aliases', [False, True])
def test_shared_interpolation_failures(doc, validators, path, rule_id, both_aliases):
    if both_aliases:
        for const in doc.xpath('//t:interpolation//t:const', namespaces=NS):
            const.set('siteIndex', const.get('site'))
    el = find(doc, path)
    if rule_id.endswith('DISTINCT-SPECIES'):
        el.set('species', 'Fe')
    elif rule_id.endswith('LOCATOR-ATTRIBUTE'):
        el.set('siteIndex', 'j')
    else:
        el.text = 'outside'
    errors = {e.rule_id for e in validate_document(doc, validators[1])[1]}
    assert rule_id in errors


def test_no_polynomial_diagnostics_for_foreign_type_names(doc):
    root = doc.getroot()
    replacement = etree.Element(root.tag, nsmap={**root.nsmap, 'foreign': 'urn:foreign'})
    replacement.attrib.update(root.attrib)
    replacement.extend(deepcopy(list(root)))
    for el in replacement.iter():
        if XSI in el.attrib:
            el.set(XSI, 'foreign:' + el.get(XSI))
    find(replacement, '//t:sublattices/t:site').set('constituents', 'bad')
    valid, errors, warnings = validate_document(etree.ElementTree(replacement), load_schematron(FOLDER / 'rule.sch'))
    assert valid and not errors and not warnings


def test_empty_interaction_container_valid_but_empty_record_invalid(doc, validators):
    interactions = find(doc, '//t:interactions')
    interaction = deepcopy(interactions[0])
    interactions.clear()
    assert_clean(doc, validators)
    for prop in list(interaction)[1:]:
        interaction.remove(prop)
    interactions.append(interaction)
    assert validators[0].validate(doc), str(validators[0].error_log)
    assert 'VAL-ERR-POLYNOMIAL-INTERACTION-PROPERTY' in {
        e.rule_id for e in validate_document(doc, validators[1])[1]
    }


def test_empty_polynomial_expression_list_rejected_by_xsd(doc, validators):
    prop = find(doc, '//t:interaction/t:property')
    for expr in list(prop):
        prop.remove(expr)
    assert not validators[0].validate(doc)


def test_matching_polynomial_stoichiometry_is_advisory(doc, validators):
    find(doc, '//t:specie[2]').set('composition', 'Fe')
    assert validators[0].validate(doc), str(validators[0].error_log)
    valid, errors, warnings = validate_document(doc, validators[1])
    assert valid and not errors, errors
    assert 'VAL-WARN-SPECIES-DUPLICATE-STOICHIOMETRY' in {w.rule_id for w in warnings}


@pytest.mark.parametrize('example', ['single-sublattice-polynomial.xml', 'subq-interaction-models.xml'])
@pytest.mark.parametrize('method,accepted', [('Muggianu', True), ('Muggiano', False)])
def test_correct_interpolation_method_spelling_only(validators, example, method, accepted):
    tree = etree.parse(str(ROOT / 'examples' / example))
    ij = find(tree, '//t:interpolation/t:ij')
    ij.clear()
    ij.set(XSI, method)
    assert validators[0].validate(tree) == accepted
    if accepted:
        assert_clean(tree, validators)


@pytest.mark.parametrize('example,rule_id', [
    ('single-sublattice-polynomial.xml', 'VAL-ERR-POLYNOMIAL-INTERPOLATION-LABELS'),
    ('subq-interaction-models.xml', 'VAL-ERR-SUBQ-INTERPOLATION-LABELS'),
])
def test_mixing_constituent_requires_canonical_role(validators, example, rule_id):
    tree = etree.parse(str(ROOT / 'examples' / example))
    del find(tree, '//t:interpolation//t:const[@site]').attrib['site']
    assert validators[0].validate(tree), str(validators[0].error_log)
    assert rule_id in {e.rule_id for e in validate_document(tree, validators[1])[1]}


def test_subq_requires_its_fixed_constituent_context(validators):
    tree = etree.parse(str(ROOT / 'examples/subq-interaction-models.xml'))
    remove(tree, '//t:interpolation/t:constituents/t:site[count(t:const)=1]')
    assert not validators[0].validate(tree)
    assert 'VAL-ERR-SUBQ-INTERPOLATION-LABELS' in {
        e.rule_id for e in validate_document(tree, validators[1])[1]
    }


@pytest.mark.parametrize('expression', ['{ASSESSMENT_FUNCTION}', 'T**4 + SIN(T)', 'A+B*T'])
def test_polynomial_expression_contract_is_independent_of_dat_lowering(doc, validators, expression):
    find(doc, '//t:interaction/t:property/t:expr').text = expression
    find(doc, '//t:magnetic/t:AFMFactor').text = '1-0.5*T'
    assert_clean(doc, validators)


@pytest.mark.parametrize('example', ['single-sublattice-polynomial.xml', 'subq-interaction-models.xml'])
def test_reject_alias_on_fixed_or_mixing_constituents(validators, example):
    tree = etree.parse(str(ROOT / 'examples' / example))
    const = find(tree, '//t:interpolation/t:constituents/t:site[last()]/t:const')
    const.set('siteIndex', 'i')
    assert not validators[0].validate(tree)
    assert 'VAL-ERR-TERNARY-INTERPOLATION-LOCATOR-ATTRIBUTE' in {
        e.rule_id for e in validate_document(tree, validators[1])[1]
    }
