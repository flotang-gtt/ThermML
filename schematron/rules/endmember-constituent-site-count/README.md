# Endmember Constituent Site Count

Rule family:

- `VAL-ERR-ENDMEMBER-CONSTITUENT-SITE-COUNT-MISMATCH`

Files in this directory keep the rule and its focused fixtures together.

- `rule.sch`: Schematron rule family
- `valid.xml`: passing fixture (endmembers with correct site counts for their phase; two phases with different sublattice counts)
- `invalid.xml`: failing fixture (endmembers with too few or too many sites relative to phase sublattices)

The check validates structural consistency: an endmember is a specific compound occupying each
sublattice site; therefore the number of constituent sites must equal the number of sublattices
declared by the phase.

The rule applies to all phases. For phases without a declared structure, the expected site
count is zero; endmembers with non-zero sites would fail, which is correct (indicating a
structure mismatch). For phases with structure (CEF and related models), the counts must
match exactly.
