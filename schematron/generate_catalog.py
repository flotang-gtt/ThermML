# /// script
# requires-python = ">=3.13"
# ///

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
RULES_DIR = Path(__file__).with_name("rules")
OUTPUT_PATH = ROOT / "docs" / "validation" / "schematron-catalog.json"
METADATA_FILE_NAME = "catalog.json"
ALLOWED_LEVELS = {"error", "warning"}


@dataclass(frozen=True)
class RuleEntry:
    rule_id: str
    purpose: str
    level: str
    examples: tuple[str, ...]


@dataclass(frozen=True)
class RuleFamily:
    slug: str
    family_name: str
    family_summary: str
    rules: tuple[RuleEntry, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate docs/validation/schematron-catalog.json from per-rule metadata."
    )
    parser.add_argument(
        "--fail-on-change",
        action="store_true",
        help="Exit with status 1 if writing the output changed the generated file.",
    )
    return parser.parse_args()


def require_string(data: dict[str, object], key: str, metadata_path: Path) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{metadata_path}: expected non-empty string field '{key}'")
    return value.strip()


def require_string_list(
    data: dict[str, object], key: str, metadata_path: Path
) -> tuple[str, ...]:
    raw_values = data.get(key)
    if not isinstance(raw_values, list) or not raw_values:
        raise ValueError(f"{metadata_path}: expected non-empty list field '{key}'")

    values: list[str] = []
    for index, raw_value in enumerate(raw_values):
        if not isinstance(raw_value, str) or not raw_value.strip():
            raise ValueError(
                f"{metadata_path}: expected '{key}[{index}]' to be a non-empty string"
            )
        values.append(raw_value.strip())
    return tuple(values)


def make_relative_href(target: Path) -> str:
    return Path(os.path.relpath(target, OUTPUT_PATH.parent)).as_posix()


def load_rule_family(rule_dir: Path) -> RuleFamily:
    metadata_path = rule_dir / METADATA_FILE_NAME
    if not metadata_path.is_file():
        raise FileNotFoundError(
            f"Missing metadata file for rule family '{rule_dir.name}': {metadata_path}"
        )

    raw_data = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(raw_data, dict):
        raise ValueError(f"{metadata_path}: expected top-level JSON object")

    for required_file in ("module.sch", "rule.sch", "README.md"):
        required_path = rule_dir / required_file
        if not required_path.is_file():
            raise FileNotFoundError(f"Missing required file: {required_path}")

    rules_data = raw_data.get("rules")
    if not isinstance(rules_data, list) or not rules_data:
        raise ValueError(f"{metadata_path}: expected non-empty list field 'rules'")

    rules: list[RuleEntry] = []
    for index, raw_rule in enumerate(rules_data):
        if not isinstance(raw_rule, dict):
            raise ValueError(f"{metadata_path}: expected 'rules[{index}]' to be an object")

        level = require_string(raw_rule, "level", metadata_path).lower()
        if level not in ALLOWED_LEVELS:
            raise ValueError(
                f"{metadata_path}: unsupported level '{level}' in rules[{index}]"
            )

        examples = require_string_list(raw_rule, "examples", metadata_path)
        for example_name in examples:
            example_path = rule_dir / example_name
            if not example_path.is_file():
                raise FileNotFoundError(
                    f"Metadata example file does not exist: {example_path}"
                )

        rules.append(
            RuleEntry(
                rule_id=require_string(raw_rule, "id", metadata_path),
                purpose=require_string(raw_rule, "purpose", metadata_path),
                level=level,
                examples=examples,
            )
        )

    return RuleFamily(
        slug=rule_dir.name,
        family_name=require_string(raw_data, "family_name", metadata_path),
        family_summary=require_string(raw_data, "family_summary", metadata_path),
        rules=tuple(rules),
    )


def load_rule_families(rules_dir: Path = RULES_DIR) -> list[RuleFamily]:
    families = [load_rule_family(path) for path in sorted(rules_dir.iterdir()) if path.is_dir()]
    if not families:
        raise ValueError(f"No rule families found in {rules_dir}")
    return families


def build_catalog_rows(families: list[RuleFamily]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for family in families:
        rule_dir = RULES_DIR / family.slug
        source_path = rule_dir / "rule.sch"
        source_label = f"schematron/rules/{family.slug}/rule.sch"
        for rule in family.rules:
            rows.append(
                {
                    "familyName": family.family_name,
                    "familySlug": family.slug,
                    "familySummary": family.family_summary,
                    "ruleId": rule.rule_id,
                    "purpose": rule.purpose,
                    "level": rule.level,
                    "source": {
                        "href": make_relative_href(source_path),
                        "label": source_label,
                    },
                    "examples": [
                        {
                            "name": example_name,
                            "href": make_relative_href(rule_dir / example_name),
                        }
                        for example_name in rule.examples
                    ],
                }
            )
    return rows


def render_catalog_payload(families: list[RuleFamily]) -> str:
    rows = build_catalog_rows(families)
    payload = {
        "generatedFrom": "schematron/rules/*/catalog.json",
        "rows": rows,
    }
    return json.dumps(payload, indent=2) + "\n"


def write_catalog_payload(output_path: Path = OUTPUT_PATH) -> tuple[Path, bool, int, int]:
    families = load_rule_families()
    rendered = render_catalog_payload(families)
    previous = output_path.read_text(encoding="utf-8") if output_path.exists() else None
    changed = previous != rendered
    output_path.write_text(rendered, encoding="utf-8")
    return output_path, changed, len(families), sum(len(family.rules) for family in families)


def main() -> int:
    args = parse_args()

    try:
        output_path, changed, family_count, rule_count = write_catalog_payload()
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(f"CATALOG ERROR: {error}")
        return 1

    print(
        f"Wrote {output_path.relative_to(ROOT).as_posix()} with {family_count} rule families and {rule_count} rules."
    )

    if changed and args.fail_on_change:
        print(
            "CATALOG OUT OF DATE: the generator updated docs/validation/schematron-catalog.json. Review the diff and stage the file before committing."
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())