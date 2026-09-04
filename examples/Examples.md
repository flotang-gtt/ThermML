## Examples

This directory is meant to be a place to collect example files that the schema
should be able to validate. 

Validate a single example from the project root with:

```powershell
uv run validate_one.py .\examples\basic-example.xml
```

Validate all examples from the project root with:

```powershell
Get-ChildItem .\examples\*.xml | ForEach-Object { uv run .\validate_one.py $_.FullName }
```

Both commands run the XSD schema in `schema/thermml-schema.xsd` and the bundled
Schematron rules in `schematron/thermml.sch`.

`subq-interaction-models.xml` is the canonical compact example for ChemSage
Modified Quasichemical interaction serialization. It covers all seven emitted
interaction property types, reciprocal variants, selected ternary terms,
quadruplets, and ternary interpolation models.

`ionic-liquid.xml` demonstrates the dedicated ionic types: cations on site 1,
anions or neutral vacancies on site 2, and one occupant per endmember site.
Ionic interactions use the same two-site ordering and allow multiple occupants
per site. XSD validates the shape and charge signs; Schematron validates group
membership and duplicate species. Energy definitions can remain placeholders.
