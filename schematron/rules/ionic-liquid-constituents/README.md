# Ionic-liquid constituents

XSD defines the ionic model independently of CEF:

- `IonicLiquidSpecieType` requires a non-empty composition and explicit charge.
- Group restrictions require positive cations, negative anions and zero-charge neutrals.
- `IonicLiquidEndmemberType` has one or two sites with one constituent each.
- `IonicLiquidInteractionType` has one or two sites, allowing multiple constituents per site.
- Phase-local XSD keys check species-name uniqueness and referenced species existence.

Schematron adds the relational checks that XSD 1.0 cannot express:

- `VAL-ERR-IONIC-DUPLICATE-SPECIES`: differently named species in a group cannot
  have the same normalized composition and charge. Distinct oxidation states
  remain allowed. Formula strings are compared literally, not chemically canonicalized.
- `VAL-ERR-IONIC-CONSTITUENT-SITE-MEMBERSHIP`: endmember and interaction references
  use one site for neutral-only terms (excluding a vacancy identified by name
  or composition `Va`, case-insensitively), or two sites with cations
  on site 1 and anions or neutrals, including Va, on site 2.

Anions may be empty if neutrals supply the second group. Required endmembers
and valid species references prevent an empty second group. Neutral-only Gibbs
expressions include their source prefactors; DAT cation-charge expansion is not
part of this representation.

This family does not reject duplicate endmember arrays or require complete
endmember coverage, interaction energies, or endmember energies. Those can be
left as placeholders while developing a model.

`valid.xml` and `invalid.xml` are minimal fixtures for the standalone `rule.sch`.
The complete database example is `examples/ionic-liquid.xml` at repository root.
