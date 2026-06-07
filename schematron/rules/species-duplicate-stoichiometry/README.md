# Species Duplicate Stoichiometry

Rule family:

- `VAL-ERR-SPECIES-DUPLICATE-STOICHIOMETRY`

Files in this directory keep the rule and its focused fixtures together.

- `rule.sch`: Schematron rule family
- `valid.xml`: passing fixture (same composition differing by charge, and the same formula reused across phases)
- `invalid.xml`: failing fixture with two species sharing an identical stoichiometric formula

The check is intentionally syntactic. Within a single phase's `<species>` block it
compares the normalized `composition` attribute together with the normalized `charge`,
as plain strings. It does **not** parse or canonicalize chemical formulas, so `Fe1` and
`Fe`, or `Al2Si1` and `Si1Al2`, are treated as different formulas.

Charge participates in the comparison on purpose: ions such as `Cu[1+]`/`Cu[2+]` or
`Fe[2+]`/`Fe[3+]` share a composition string but are genuinely distinct species and are
not flagged. Species without a `composition` are not compared. The scope is per phase;
the same formula may appear in a different phase without being reported.
