# CEF Endmember Cartesian Count

Rule family:

- `VAL-ERR-CEF-ENDMEMBER-CARTESIAN-COUNT-MISMATCH`

Files in this directory keep the rule and its minimal pass/fail fixtures together.

- `rule.sch`: Schematron rule family
- `valid.xml`: passing fixture
- `invalid.xml`: failing fixture

The exact Cartesian-product count applies to non-gaseous CEF phases. Phases
with `state="gas"` are semantically single-sublattice gas models and may contain
several thermodynamic states for the same constituent, so they are handled by
the `gas-endmember-consistency` rule family instead.
