# Single-sublattice polynomial semantics

See [the integration review](../../../docs/single-sublattice-polynomial.md) for model semantics, compatibility decisions and the scope of representation validation.

XSD validates numeric domains, structure cardinality and phase-local species references. Shared Schematron rules validate endmember occupancy, constituent membership, multiplicities and the canonical ternary locator. This family adds the polynomial-specific constraints below.

- `VAL-ERR-POLYNOMIAL-STRUCTURE-SPECIES-COUNT`: The single sublattice must list exactly as many tokens as there are declared species.

- `VAL-ERR-POLYNOMIAL-MAGNETIC-STRUCTURE`: Magnetic M, TCL and BML properties require an IHJ magnetic structure. An all-zero magnetic structure is valid.

- `VAL-ERR-POLYNOMIAL-STRUCTURE-SPECIES-MEMBERSHIP`: Each declared species must occur exactly once in the single sublattice token list.

- `VAL-ERR-POLYNOMIAL-ENDMEMBER-COVERAGE`: Each polynomial species must have exactly one endmember.

- `VAL-ERR-POLYNOMIAL-SPECIES-COMPOSITION`: Polynomial species require a nonempty composition, including any preprocessed stoichiometric scaling.

- `VAL-ERR-POLYNOMIAL-ENDMEMBER-NAME`: A polynomial endmember name must match its constituent species name literally.

- `VAL-ERR-POLYNOMIAL-ENDMEMBER-PROPERTY`: Polynomial endmembers accept G, M and the existing physical-property types, not interaction or MQM properties.

- `VAL-ERR-POLYNOMIAL-INTERACTION-ARITY`: A polynomial-phase interaction must contain one site with two to four constituents.

- `VAL-ERR-POLYNOMIAL-INTERACTION-PROPERTY`: Each polynomial-phase interaction requires at least one property, and accepts only PolynomialL, TCL or BML.

- `VAL-ERR-POLYNOMIAL-INTERACTION-DISTINCT-SPECIES`: Interaction constituents must be distinct; their listed order defines the exponent positions.

- `VAL-ERR-POLYNOMIAL-PROPERTY-SCOPE`: PolynomialL is valid only on an interaction of a SingleSublatticePolynomialPhaseType phase.

- `VAL-ERR-POLYNOMIAL-EXPONENT-ARITY`: Polynomial exponents must match constituent arity: i,j; i,j,k; or i,j,k,l. Explicit zero powers are valid.

- `VAL-ERR-POLYNOMIAL-EXPRESSION-NONEMPTY`: A polynomial coefficient expression must contain text; an explicit zero is valid.

- `VAL-ERR-POLYNOMIAL-DUPLICATE-TERM`: Ordered constituent/exponent identities must be unique across all PolynomialL properties and interactions in a phase, regardless of interaction names or coefficient text.

- `VAL-ERR-POLYNOMIAL-INTERPOLATION-LABELS`: Polynomial interpolation requires one site containing exactly one i, j and k locator, using the site attribute.

`valid.xml` and `invalid.xml` are focused Schematron fragments. The complete example is [single-sublattice-polynomial.xml](../../../examples/single-sublattice-polynomial.xml).
