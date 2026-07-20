# SUBQ Interaction Semantics

This rule family checks cross-tree constraints for
`ModifiedQuasichemicalPhaseType` that cannot be expressed reliably in XSD 1.0:

- `selected` is limited to PF, SP, Quasichemical, and RK properties and must
  reference a constituent of a ternary interaction.
- Selected PF, SP, and Quasichemical expressions carry an explicit `k >= 1`.
- RM, RS, and RC reciprocal properties use two constituents on each of two
  sites.
- Ternary interpolation constituents label the ternary site exactly once with
  each of `i`, `j`, and `k`, alongside one unlabeled fixed site.

`valid.xml` demonstrates all passing shapes. `invalid.xml` deliberately violates
each rule while remaining useful as a focused Schematron fixture.
