# Ionic-liquid constituents

XSD defines the ionic model independently of CEF:

- `IonicLiquidSpecieType` requires a non-empty composition and explicit charge.
- Group restrictions require positive cations, negative anions and zero-charge neutrals.
- `IonicLiquidEndmemberType` has one or two sites with one constituent each.
- `IonicLiquidInteractionType` has one or two sites, allowing multiple constituents per site.
- Phase-local XSD keys check species-name uniqueness and referenced species existence.

Schematron adds the following checks and advisory:

- `VAL-WARN-IONIC-DUPLICATE-SPECIES`: differently named species in a group sharing
  normalized composition and charge trigger an advisory warning. Those attributes
  determine site ratios and stoichiometry, but do not establish thermodynamic
  identity. Native names and independent parameters must be preserved. Formula
  and charge strings are compared literally, not chemically canonicalized.
- `VAL-ERR-IONIC-CONSTITUENT-SITE-MEMBERSHIP`: endmember and interaction references
  use one site for neutral-only terms (excluding a vacancy identified by
  composition `Va`, case-insensitively), or two sites with cations
  on site 1 and anions or neutrals, including Va, on site 2.

- `VAL-ERR-IONIC-VACANCY-CHARGE`: composition `Va` requires zero formal charge.
  Species names are aliases: `hole` with composition `Va` is a vacancy, while
  `Va` or `Vacancy` with a chemical composition is an ordinary species. Names
  neither determine vacancy identity nor cause validation errors.

Anions may be empty if neutrals supply the second group. Required endmembers
and valid species references prevent an empty second group. Neutral-only Gibbs
expressions include their source prefactors; DAT cation-charge expansion is not
part of this representation.

This family does not reject duplicate endmember arrays or require complete
endmember coverage, interaction energies, or endmember energies. Those can be
left as placeholders while developing a model.

The former `VAL-ERR-IONIC-DUPLICATE-SPECIES` error is replaced by the warning
above. Species-name uniqueness, charge signs, vacancy charge and site membership
remain strict. This follows the general name-based identity policy documented in
[`species-duplicate-stoichiometry`](../species-duplicate-stoichiometry/README.md).

`valid.xml`, `warning.xml` and `invalid.xml` are minimal fixtures for the standalone `rule.sch`.
The complete database example is `examples/ionic-liquid.xml` at repository root.
