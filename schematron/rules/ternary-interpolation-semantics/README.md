# Ternary interpolation semantics

SUBQ and single-sublattice polynomial phases share these representation checks:

- `VAL-ERR-TERNARY-INTERPOLATION-LOCATOR-ATTRIBUTE`: `site` is the sole i/j/k
  locator. `siteIndex` is forbidden even if both attributes agree. XSD also
  rejects it; the Schematron rule provides the same check to standalone callers.
- `VAL-ERR-TERNARY-INTERPOLATION-DISTINCT-SPECIES`: species must be distinct
  within each interpolation site.
- `VAL-ERR-TERNARY-INTERPOLATION-TOOP-LOCATOR`: `Toop/constant` must select a
  labeled member of the ternary. The third species outside the named pair is valid.

The polynomial and SUBQ rule families enforce their respective one-site/two-site
contexts and exactly one i, j and k role. The fixed SUBQ constituent has no role.
The method types and role vocabulary are identical for both families.

`rule.sch` is the standalone wrapper for `module.sch`; `valid.xml` and
`invalid.xml` cover each assertion. This family replaces the development-only
locator-alias checks. See [the 0.2.0 integration review](../../../docs/single-sublattice-polynomial.md)
for source DAT evidence and migration instructions.
