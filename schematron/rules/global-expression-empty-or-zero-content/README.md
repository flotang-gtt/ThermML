# Global Expression Empty Or Zero Content

Rule family:

- `VAL-WARN-GLOBAL-EXPRESSION-EMPTY-OR-ZERO-CONTENT`

Files in this directory keep the warning rule and its focused fixtures together.

- `rule.sch`: Schematron rule family
- `valid.xml`: passing fixture without warnings
- `warning.xml`: passing fixture that emits warnings for empty and zero literal textual function bodies

The check is intentionally literal. It only inspects text-bearing global-expression content nodes: `range`, `tdb`, and `chemsage`. It warns when their normalized text is empty or when the full content parses as the numeric value zero under the repository's XPath 1.0 Schematron toolchain. It does not attempt symbolic simplification, and it intentionally does not treat structured `HSCPTemperatureExpr` terms as free-text expressions.