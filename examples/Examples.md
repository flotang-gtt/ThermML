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

`ionic-liquid.xml` contains the canonical ionic representation of the Lindwall
Fe-Al-O model: four cation-pair endmembers and two neutral-only endmembers,
six explicit piecewise Gibbs functions, and ten interactions. Neutral-only
terms retain their complete source-prefactored energy without introducing an
artificial cation site. Source attribution and DAT line references are kept in
the XML itself.
