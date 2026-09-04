# Gas Endmember Consistency

Gas phases are represented with `CEFPhaseType` as their storage shape in the
current schema, but are semantically single-sublattice gas models rather than
compound-energy phases. They may contain multiple named thermodynamic states
for a single constituent. This family replaces strict Cartesian equality and
blanket duplicate-array rejection for `CEFPhaseType` phases with `state="gas"`.

The rules require:

- every structure constituent to be declared in the phase species list;
- every structure constituent to have at least one endmember;
- every endmember to reference exactly one declared structure constituent; and
- unique endmember names within the phase.

Multiple endmembers may share a constituent without a finding when their
normalized Gibbs expressions differ. Differently named endmembers that share
both the constituent and a non-empty Gibbs expression produce a warning because they are
indistinguishable to this validation layer.

`valid.xml` is derived from the ChemSage `CH-plasma.dat` representation and
includes charged hydrogen plus three distinct thermodynamic states for
`H2N2(g)`. `invalid.xml` exercises every error, while `warning.xml` demonstrates
an apparent duplicate Gibbs definition.

Missing or empty energy definitions remain valid placeholders and do not trigger
duplicate-Gibbs warnings. QName prefixes do not change which phase or property
types are matched.
