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
