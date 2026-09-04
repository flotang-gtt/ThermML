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

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schematron.run_schematron import load_schematron, validate_document  # noqa: E402


RULES = ROOT / "schematron" / "rules"
AGGREGATE = ROOT / "schematron" / "thermml.sch"
GAS_FIXTURES = RULES / "gas-endmember-consistency"


@pytest.fixture(scope="module")
def schematron():
    return load_schematron(AGGREGATE)


def validate_fixture(schematron, path: Path):
    doc = etree.parse(str(path))
    return validate_document(doc, schematron)


def test_ch_plasma_derived_gas_states_pass_cleanly(schematron) -> None:
    is_valid, errors, warnings = validate_fixture(
        schematron, GAS_FIXTURES / "valid.xml"
    )

    assert is_valid
    assert errors == []
    assert warnings == []


def test_gas_integrity_failures_are_reported(schematron) -> None:
    is_valid, errors, warnings = validate_fixture(
        schematron, GAS_FIXTURES / "invalid.xml"
    )

    assert not is_valid
    assert {finding.rule_id for finding in errors} == {
        "VAL-ERR-CEF-GAS-STRUCTURE-CONSTITUENTS-DECLARED",
        "VAL-ERR-CEF-GAS-ENDMEMBER-COVERAGE",
        "VAL-ERR-CEF-GAS-ENDMEMBER-CONSTITUENT",
        "VAL-ERR-CEF-GAS-ENDMEMBER-NAME-UNIQUE",
        "VAL-ERR-CEF-CONSTITUENT-SITE-MEMBERSHIP",
    }
    assert warnings == []


def test_same_constituent_and_gibbs_expression_warns(schematron) -> None:
    is_valid, errors, warnings = validate_fixture(
        schematron, GAS_FIXTURES / "warning.xml"
    )

    assert is_valid
    assert errors == []
    assert [finding.rule_id for finding in warnings] == [
        "VAL-WARN-CEF-GAS-ENDMEMBER-DUPLICATE-GIBBS"
    ]


@pytest.mark.parametrize(
    ("fixture", "rule_id"),
    [
        (
            RULES / "cef-endmember-cartesian-count" / "invalid.xml",
            "VAL-ERR-CEF-ENDMEMBER-CARTESIAN-COUNT-MISMATCH",
        ),
        (
            RULES / "endmember-duplicate-constituents" / "invalid.xml",
            "VAL-ERR-ENDMEMBER-DUPLICATE-CONSTITUENTS",
        ),
    ],
)
def test_non_gas_cef_rules_remain_strict(schematron, fixture: Path, rule_id: str) -> None:
    is_valid, errors, _warnings = validate_fixture(schematron, fixture)

    assert not is_valid
    assert rule_id in {finding.rule_id for finding in errors}
