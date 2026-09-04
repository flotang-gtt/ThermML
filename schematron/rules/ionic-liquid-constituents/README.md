# Ionic-liquid constituents

XSD defines the ionic model independently of CEF:

- `IonicLiquidSpecieType` requires a non-empty composition and explicit charge.
- Group restrictions require positive cations, negative anions and zero-charge neutrals.
- `IonicLiquidEndmemberType` has exactly two sites with one constituent each.
- `IonicLiquidInteractionType` has exactly two sites, allowing multiple constituents per site.
- Phase-local XSD keys check species-name uniqueness and referenced species existence.

Schematron adds the relational checks that XSD 1.0 cannot express:

- `VAL-ERR-IONIC-DUPLICATE-SPECIES`: differently named species in a group cannot
  have the same normalized composition and charge. Distinct oxidation states
  remain allowed. Formula strings are compared literally, not chemically canonicalized.
- `VAL-ERR-IONIC-CONSTITUENT-SITE-MEMBERSHIP`: endmember and interaction references
  must name cations on site 1 and anions or neutrals (including the fixture's
  neutral vacancy) on site 2.

This family does not reject duplicate endmember arrays or require complete
endmember coverage, interaction energies, or endmember energies. Those can be
left as placeholders while developing a model.

`valid.xml` and `invalid.xml` are minimal fixtures for the standalone `rule.sch`.
The complete database example is `examples/ionic-liquid.xml` at repository root.
