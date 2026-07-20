# ThermML

## Objective

`ThermML` is an xml schema definition structure that should be able to describe
thermodynamic databases across multiple software tools, with the intention of
providing a mechanism to validate structure and data of thermodynamic databases.

The schema is meant to be extendable, e.g. by providing adequate hooks for
additional schemata as well as providing a reasonable platform of common type
definitions that the extensions should adhere to.

The project uses XML Schema Definition for structural validation and Schematron
for repository-managed rule checks. This repository is supposed to be
implementation agnostic, as the XML validation tools for all major languages
are mature and robust enough.

## Project structure

The `analysis` directory contains `requirements` and `user-stories` used as basis
for driving and directing development.

The `examples` directory contains examples of files that validate against the
schema.

The `schema` directory contains the schema definition files.

## Versioning

ThermML follows [Semantic Versioning](https://semver.org/). The version is
expressed in two complementary places:

- The **target namespace** encodes only the major version, e.g.
  `http://calphad.org/thermml/v0`. A breaking (major) change introduces a new
  namespace (`v1`, `v2`, ...).
- The **`version` attribute** on the root `<database>` element carries the full
  `MAJOR.MINOR.PATCH` string a document targets, starting at `0.1.0`. Minor and
  patch iterations change this attribute while staying within the same
  namespace.

This keeps minor and patch revisions compatible within a namespace while
reserving namespace changes for breaking, major releases.

Note that this schema `version` attribute is distinct from the
`<metadata><version>` element, which versions the *content* of a particular
database rather than the schema it conforms to.

## Validation

Validate either a ThermML XML file or the database XML stored in a Calphad
Optimizer `.optx` save file against the XSD schema and bundled Schematron rules
using [lxml](https://lxml.de/):

```bash
uv run validate_one.py path/to/file.xml
uv run validate_one.py path/to/saved-run.optx
```

This parses `schema/thermml-schema.xsd`, compiles `schematron/thermml.sch`, and
validates the selected XML document against both layers. For `.optx` input,
`validate_one.py` reads `manifest.json` and validates the archive member named by
`members.database`; it does not extract the archive. The command reports
`PASS`, `PASS WITH WARNINGS`, or `FAIL`, followed by detailed XSD errors and
Schematron findings. It exits with status `0` for either passing result and `1`
for validation failures or unreadable inputs/validators.

Use custom validation resources when needed:

```bash
uv run validate_one.py INPUT \
  --schema path/to/thermml-schema.xsd \
  --schematron path/to/thermml.sch
```

The Python API returns the same result as structured data:

```python
from validate_one import ValidationLoadError, format_report, validate_file

try:
    report = validate_file("path/to/saved-run.optx")
except ValidationLoadError as error:
    print(f"{error.component} ERROR: {error}")
else:
    print(format_report(report))
    if report.is_valid:
        print("database is valid")
```

`validate_file(input_file, *, schema_path=..., schematron_path=...)` accepts a
string or `pathlib.Path` and returns a `ValidationReport`. Its main fields are
`input_path`, `document_label`, `archive_member`, `xsd_valid`, `xsd_errors`,
`schematron_valid`, `schematron_errors`, and `schematron_warnings`; `is_valid`
and `status` are convenience properties. It raises `ValidationLoadError` when
an input, its OPTX manifest/database member, the XSD, or the Schematron cannot
be loaded. `format_report(report)` renders the command-line report as a string.

For example-specific validation commands, including how to run all example XML
files in one shell loop, see `examples/Examples.md`.

## How to contribute

As of the drafting stage of this project, every contribution is welcome. Pull
requests may add examples or requirements. Most current implementations can be
seen as discussable items. The issues section is good place to start discussions.

For local guardrails, install the repository pre-commit hooks once after
cloning:

```bash
uv run --with pre-commit pre-commit install
```

That hook currently refreshes `docs/validation/schematron-catalog.json` and
fails the commit if the generated file changed, so the catalog diff must be
reviewed and staged explicitly. GitHub Actions also re-runs the same check on
push and pull request updates.
