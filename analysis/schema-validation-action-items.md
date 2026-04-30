# Schema Validation Action Items

## Purpose

This document turns the current schema-validation review into an actionable backlog.

The goal is to separate:

- safe XSD 1.0 improvements that should be easy to land;
- tighter constraints that need data cleanup or a model decision first; and
- higher-level semantic validation work that should not be forced into plain XSD.

## Recommended Order

1. Implement the safe XSD 1.0 items first.
2. Add tests for each new constraint as it is introduced.
3. Clean up example data and confirm intended semantics where the model is still ambiguous.
4. Add semantic validation for expression and model-level rules.
5. Add Schematron only for the XML-tree rules that remain awkward after the XSD pass.

## Safe XSD 1.0 Wins

- [x] Add a database-level key for `systemComponents/systemComponent/@symbol` in [schema/databases/main.xsd](schema/databases/main.xsd).
  Outcome: system-component identifiers become globally referenceable within a database.
  Acceptance check: add a failing test where `stoich/@component` names a missing component.

- [x] Add a keyref from `stoichiometry/stoich/@component` to the system-component key.
  Files to touch:
  [schema/databases/main.xsd](schema/databases/main.xsd)
  [schema/phases/core.xsd](schema/phases/core.xsd)
  [tests/test_schema_validation.py](tests/test_schema_validation.py)

- [x] Add a database-level key for `phases/phase/@name`.
  Outcome: phase names become valid schema-level identifiers, not just display strings.

- [x] Add a keyref from `CEFOrderedPhaseType/@disorderedPhase` to the phase-name key.
  Files to touch:
  [schema/databases/main.xsd](schema/databases/main.xsd)
  [schema/phases/ordered-phase.xsd](schema/phases/ordered-phase.xsd)
  [tests/test_schema_validation.py](tests/test_schema_validation.py)

- [x] Add a database-level key for `globalExpressions/expression/@name`.
  Outcome: global function declarations become referenceable in the same way phase species already are.

- [x] Add a keyref from `FunctionReferenceType/@name` to the global-expression key.
  Files to touch:
  [schema/databases/main.xsd](schema/databases/main.xsd)
  [schema/expressions/main.xsd](schema/expressions/main.xsd)
  [schema/phases/pure-substances.xsd](schema/phases/pure-substances.xsd)
  [tests/test_schema_validation.py](tests/test_schema_validation.py)

- [x] Add a phase-local keyref for MQM quadruplet species back to the phase species list.
  Files to touch:
  [schema/phases/quasichemical-phase.xsd](schema/phases/quasichemical-phase.xsd)
  [tests/test_schema_validation.py](tests/test_schema_validation.py)
  Acceptance check: a quadruplet with an unknown `a`, `b`, `x`, or `y` species should fail validation.

- [x] Replace `TernarySiteLocatorType` with a scalar enum instead of a list type.
  Files to touch:
  [schema/expressions/core.xsd](schema/expressions/core.xsd)
  [schema/phases/core.xsd](schema/phases/core.xsd)
  Why: current usage is scalar in all observed call sites.

- [x] Redesign `FunctionVariableType` so it matches the intended domain exactly.
  Files to touch:
  [schema/expressions/core.xsd](schema/expressions/core.xsd)
  [schema/phases/pure-substances.xsd](schema/phases/pure-substances.xsd)
  Candidate outcome: allow `T`, `P`, or `T,P` explicitly instead of a whitespace list.

- [x] Restrict MQM `specie/@group` to an enum of `1` or `2`.
  Files to touch:
  [schema/phases/quasichemical-phase.xsd](schema/phases/quasichemical-phase.xsd)
  [tests/test_schema_validation.py](tests/test_schema_validation.py)
  Note: this only tightens the lexical domain, not the full cation/anion semantics.

- [x] Replace `MultiplicitiesStringType` with a list of numeric values.
  Files to touch:
  [schema/phases/cef-phase.xsd](schema/phases/cef-phase.xsd)
  Why: numeric parsing should be delegated to XSD instead of a permissive regex.

## Tightenings That Need a Design Decision or Data Cleanup

- [x] Decide whether phase names are display labels or true identifiers.
  Relevant files:
  [schema/phases/core.xsd](schema/phases/core.xsd)
  [examples/basic-example.xml](examples/basic-example.xml)
  [examples/simple_solution.xml](examples/simple_solution.xml)
  Decision needed: can names contain spaces, commas, parentheses, or only identifier-safe characters?

- [x] Decide whether CEF and MQM `specie/@name` should move from `xs:string` to `NoWhitespaceString` or a dedicated identifier type.
  Relevant files:
  [schema/phases/cef-phase.xsd](schema/phases/cef-phase.xsd)
  [schema/phases/quasichemical-phase.xsd](schema/phases/quasichemical-phase.xsd)

- [ ] Normalize `refstate` before constraining it.
  Relevant files:
  [schema/system-components/main.xsd](schema/system-components/main.xsd)
  [examples/basic-example.xml](examples/basic-example.xml)
  [examples/quasichemical.xml](examples/quasichemical.xml)
  Status: partially tightened to no-whitespace tokens and the bogus default value was removed, but the actual reference-state vocabulary is still unresolved.

- [ ] Decide whether metadata `license` should be free text or an SPDX-style identifier.
  Relevant file:
  [schema/metadata/main.xsd](schema/metadata/main.xsd)

- [x] Decide whether metadata `created` should be `xs:date` or remain optional free text.
  Relevant file:
  [schema/metadata/main.xsd](schema/metadata/main.xsd)
  Recommendation: prefer `xs:date` and omit the element when unknown.

- [ ] Split citation-key references from free-text references.
  Relevant files:
  [schema/metadata/main.xsd](schema/metadata/main.xsd)
  [schema/expressions/main.xsd](schema/expressions/main.xsd)
  [schema/phases/phase-properties.xsd](schema/phases/phase-properties.xsd)
  Suggested direction: keep `ref` as descriptive text and add `citationKey` as a separately validated field.

## Semantic Validation Backlog

- [x] Add a Python validation pass for expression syntax.
  Why: schema validation currently accepts malformed expressions embedded as strings.
  Example anchor:
  [examples/simple_solution.xml](examples/simple_solution.xml)
  Acceptance check: malformed expression text must fail semantic validation.

- [ ] Parse each expression dialect with its own validator.
  Candidate dialects:
  `expr`
  `h-s-cp`
  `tdb`
  `CSdat`
  `gibbs`
  Status: generic arithmetic expressions in `expr` and text-based `range` nodes are now parsed semantically; dedicated TDB and CSdat validators remain open.

- [x] Validate temperature ranges semantically.
  Checks to add:
  `low < high`
  monotonic order
  no overlaps
  optional continuity warnings at touching boundaries

- [x] Validate symbolic function references inside expression text after parsing.
  Outcome: names such as `Fe#FCC_A1` or `C#HSER` can be checked against declared functions instead of only being treated as text.
  Scope note: the current implementation validates symbolic references inside generic global range expressions.

- [x] Validate MQM group and charge consistency once the intended semantics are agreed.
  Candidate rule: positive charge implies cation group, negative charge implies anion group.

- [x] Validate structure-specific consistency rules that depend on multiple fields at once.
  Examples:
  sublattice count versus multiplicity count
  interpolation locator uniqueness
  ordered/disordered phase compatibility

## Testing Backlog

- [ ] Extend [tests/test_schema_validation.py](tests/test_schema_validation.py) for every new XSD key, keyref, or enum restriction.

- [x] Add a second test module for non-XSD semantic validation once the Python validator exists.
  Suggested file:
  [tests/test_semantic_validation.py](tests/test_semantic_validation.py)

- [ ] Add regression fixtures for malformed but currently schema-valid examples.
  First candidate:
  [examples/simple_solution.xml](examples/simple_solution.xml)
  Status: the malformed Mn range expression was fixed in the example corpus and is now covered by a semantic regression that mutates the document back to the invalid form.

## Proposed Milestone Split

### Milestone 1: Low-risk schema tightening

- system-component key and keyref
- phase-name key and ordered-phase keyref
- global-expression key and function-reference keyref
- MQM quadruplet species keyrefs
- scalar enum fixes for site locators and group values

### Milestone 2: Model cleanup decisions

- identifier conventions for phase and species names
- `refstate` vocabulary
- metadata normalization
- citation-key split

### Milestone 3: Deeper validation

- semantic expression parser and validator
- range-ordering checks
- model-level consistency checks
- optional Schematron layer for XML-tree assertions