# Endmember Duplicate Constituents

Rule family:

- `VAL-ERR-ENDMEMBER-DUPLICATE-CONSTITUENTS`

Files in this directory keep the rule and its focused fixtures together.

- `rule.sch`: Schematron rule family
- `valid.xml`: passing fixture (distinct arrays, a site-order variant, and the same array reused across phases)
- `invalid.xml`: failing fixture with two endmembers sharing an identical constituent array

The check is intentionally syntactic. Within a single phase's `<endmembers>` block it
compares a per-site species signature built from `constituents/site/const/@species`, as a
plain string. Site order is significant, so `[Fe|Va]` and `[Va|Fe]` are different
endmembers.

The signature is a bounded concat over explicit site positions (up to 8 sublattice
sites), because the XPath 1.0 / XSLT Schematron toolchain has no string-join over an
arbitrary-length sequence; this mirrors the CEF endmember-count rule. Endmembers are
expected to carry exactly one constituent per site (standard CEF endmember); only the
first constituent of each site participates in the signature. The scope is per phase; the
same constituent array may appear in a different phase without being reported.

CEF phases with `state="gas"` are excluded because multiple named thermodynamic
states may intentionally refer to the same constituent array. Those phases use
the coverage and Gibbs-expression checks in `gas-endmember-consistency`.

`IonicLiquidPhaseType` is also excluded: ionic endmember multiplicity is permitted.
The dedicated ionic rule checks species identity and site membership, not
endmember-array uniqueness. Other phase types do not gain an exemption merely
by setting `state="gas"`. Type names are matched by their resolved namespace and
local name, independently of the chosen XML prefix.
