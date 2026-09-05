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

`ionic-liquid.xml` is transcribed directly from the first `IONIC_LIQ` / `SUBI`
block in the user-supplied FactSage export `AlFeO_Lindwall.dat`. It includes
all eight endmembers, ten interactions and eight original ChemSage-format
Gibbs functions. See [the source notes](ionic-liquid-source.md) for constituent
indices, source line numbers, normalization and the vacancy-role limitation
exposed by this real dataset.
