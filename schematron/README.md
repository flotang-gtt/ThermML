# Schematron

This directory contains the current Schematron validation layer and a small set of runnable fixtures.

- `thermml.sch`: combined entrypoint for all currently published Schematron rules in this repo.
- `rules/<rule-family>/`: one directory per Schematron rule family, with its source and fixtures kept together.

The repository-level `validate_one.py` command compiles and runs `thermml.sch`
as the Schematron phase of the normal validation flow. The standalone runner in
this directory remains useful for fixture work and focused rule-family testing.

The combined entrypoint uses Schematron `include` directives to pull in shared rule modules from the rule-family directories. Each standalone `rule.sch` does the same, so the actual rule body exists in one place per family, and allows isolated testing.

The two-file split is a consequence of how the current `lxml.isoschematron` based toolchain processes Schematron `include` directives.

- `module.sch` is the reusable source-of-truth for one rule family.
- `rule.sch` is only a runnable wrapper.

The current rule families are:

- `rules/ternary-interpolation-locator-aliases/`
- `rules/redlich-kister-rank/`
- `rules/cef-endmember-cartesian-count/`

Each rule-family directory contains:

- `module.sch`: the shared rule module included by other Schematron entrypoints
- `rule.sch`: standalone wrapper for validating only that family
- `README.md`: the rule IDs carried by that family, explanations and examples, 
  if warranted
- one or more example XML fixtures showing pass, fail, or warning behavior

## Running Fixtures

Fixture names follow a simple convention:

- `valid.xml`: should pass without errors
- `invalid.xml`: should fail at least one assert
- `warning.xml`: should pass but emit warning reports when that rule family has them

To test the combined rule set of all rules against an arbitrary XML file:

```powershell
uv run .\schematron\run_schematron.py path\to\file.xml
```

Use a rule-family wrapper when you want to run a specific rule family only:

```powershell
uv run .\schematron\run_schematron.py path\to\file.xml --schematron .\schematron\rules\<rule-family>\rule.sch
```

Example:

```powershell
uv run .\schematron\run_schematron.py .\schematron\rules\redlich-kister-rank\warning.xml --schematron .\schematron\rules\redlich-kister-rank\rule.sch
```

The runner prints failed assertions and warning reports separately, including
the rule id, message, and location extracted from the SVRL report.

The current implementation purposefully only uses XSLT 1.0-style Schematron
bindings, for better support across libraries and platforms.

## Adding a new rule

To add a new rule, make sure to

- Create a new rule-name based directory under `rules/`
- provide a `README.md` with a reasonable, human-centric explanation
- `rule.sch` can be copied from any other rule
- `module.sch` needs to implement the actual Schematron rule
- If possible or needed, add examples for invalid and warning cases
- Add the rule name to the `thermml.sch` aggregate file
- Add the rule to the `docs/validation/schematron-catalog.html` overview of rules.