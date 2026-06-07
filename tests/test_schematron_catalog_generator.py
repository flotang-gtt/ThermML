# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pytest>=9.0.3",
# ]
# ///

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schematron.generate_catalog import load_rule_families, render_catalog_payload


def test_generator_loads_all_rule_families() -> None:
    families = load_rule_families()

    assert [family.slug for family in families] == [
        "cef-endmember-cartesian-count",
        "endmember-duplicate-constituents",
        "global-expression-empty-or-zero-content",
        "redlich-kister-rank",
        "species-duplicate-stoichiometry",
        "ternary-interpolation-locator-aliases",
    ]
    assert sum(len(family.rules) for family in families) == 8


def test_rendered_catalog_payload_contains_filterable_rule_data() -> None:
    payload = json.loads(render_catalog_payload(load_rule_families()))

    assert payload["generatedFrom"] == "schematron/rules/*/catalog.json"
    rows = payload["rows"]
    levels = {row["level"] for row in rows}
    rule_ids = {row["ruleId"] for row in rows}

    assert levels == {"error", "warning"}
    assert "VAL-WARN-RK-HIGH-RANK" in rule_ids
    assert any(
        row["familyName"] == "Redlich-Kister rank"
        and any(example["name"] == "warning.xml" for example in row["examples"])
        for row in rows
    )

def test_runtime_html_fetches_generated_catalog_json() -> None:
    html = (ROOT / "docs" / "validation" / "schematron-catalog.html").read_text(
        encoding="utf-8"
    )

    # Verify the page is wired to fetch the catalog JSON at runtime.
    assert 'fetch("./schematron-catalog.json"' in html

    # Verify key UI elements exist (by semantic role, not brittle IDs, so refactors don't break the test).
    assert '<table id="catalog-table">' in html, "missing catalog results table"
    assert 'type="search"' in html, "missing search input"
    assert 'id="catalog-error"' in html, "missing error message container"