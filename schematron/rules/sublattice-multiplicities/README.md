# Sublattice multiplicity count

XSD's `MultiplicitiesStringType` requires a non-empty list of strictly positive
`xs:decimal` values. Fractional multiplicities are allowed.

`VAL-ERR-SUBLATTICE-MULTIPLICITY-COUNT` checks the remaining relationship:
there must be exactly one multiplicity per declared sublattice site.
Whitespace is normalized before counting tokens, so spaces, tabs and newlines
are equivalent separators.

The standalone Schematron family checks count only. Run the combined validator
to also reject zero, negative or nonnumeric entries through XSD.

`valid.xml` and `invalid.xml` are minimal fixtures for the standalone `rule.sch`.
