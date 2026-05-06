# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pytest>=9.0.3",
# ]
# ///

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schematron.generate_catalog import load_rule_families, render_catalog_payload


def test_generator_loads_all_rule_families() -> None:
    families = load_rule_families()

    assert [family.slug for family in families] == [
        "cef-endmember-cartesian-count",
        "redlich-kister-rank",
        "ternary-interpolation-locator-aliases",
    ]
    assert sum(len(family.rules) for family in families) == 5


def test_rendered_catalog_payload_contains_filterable_rule_data() -> None:
    payload = json.loads(render_catalog_payload(load_rule_families()))

    assert payload["generatedFrom"] == "schematron/rules/*/catalog.json"
    rows = payload["rows"]
    levels = {row["level"] for row in rows}
    rule_ids = {row["ruleId"] for row in rows}

    assert levels == {"error", "warning"}
    assert "VAL-SEM-RK-HIGH-RANK-SUSPICIOUS" in rule_ids
    assert any(
        row["familyName"] == "Redlich-Kister rank"
        and any(example["name"] == "warning.xml" for example in row["examples"])
        for row in rows
    )

def test_runtime_html_fetches_generated_catalog_json() -> None:
    html = (ROOT / "docs" / "validation" / "schematron-catalog.html").read_text(
        encoding="utf-8"
    )

    assert 'fetch("./schematron-catalog.json"' in html
    assert 'id="catalog-family-count"' in html
    assert 'id="catalog-error"' in html
    assert re.search(r'id="catalog-search"', html) is not None