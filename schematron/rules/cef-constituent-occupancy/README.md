# Sublattice constituent occupancy

- `VAL-ERR-CEF-ENDMEMBER-SINGLE-OCCUPANCY`: exactly one constituent per endmember site.
- `VAL-ERR-CEF-INTERACTION-SITE-COUNT`: interaction arrays have one site per sublattice.
- `VAL-ERR-CEF-CONSTITUENT-SITE-MEMBERSHIP`: every endmember and interaction
  reference belongs to the corresponding structure site's constituent list.

The existing `endmember-constituent-site-count` family checks endmember array length.
Interactions may contain multiple constituents per site.

For each reference, the rule counts preceding sibling sites to obtain its site
index and looks for the species as a whole whitespace-delimited token in that
structure site's list. It does not enumerate Cartesian products and has no
fixed site-count ceiling. `Fe` cannot accidentally match `Fe2`.

Structural matching applies to phases that declare sublattices, including
`CEFOrderedPhaseType`. Ionic liquids use their own group-membership rule.

`valid.xml` and `invalid.xml` are minimal fixtures for the standalone `rule.sch`.
