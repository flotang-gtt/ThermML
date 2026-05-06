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

## Validation

Validate a single XML file against the XSD schema and bundled Schematron rules
using [lxml](https://lxml.de/):

```bash
uv run --with lxml python validate_one.py path/to/file.xml
```

This parses `schema/thermml-schema.xsd`, compiles `schematron/thermml.sch`, and
validates the given XML file against both layers, reporting pass/fail status and
detailed errors or warnings for any findings.

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
