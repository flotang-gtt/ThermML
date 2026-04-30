# Schematron Validation Candidates

## Purpose

This document records the deeper validation rules that are reasonable candidates for Schematron.

The intent is not to replace XSD or a Python semantic validator.

Recommended split of responsibility:

- XSD 1.0 for structure, cardinality, simple datatypes, enums, and key/keyref;
- Schematron for XML-tree-aware, conditional, context-sensitive assertions;
- Python validation for expression parsing, dialect-specific syntax, and thermodynamic semantics.

## Is Schematron Reasonable Here?

Yes, with a narrow scope.

Schematron is a good fit when a rule depends on:

- `xsi:type` or some other contextual branch in the XML tree;
- relationships between siblings, ancestors, or descendants;
- conditional requirements that are awkward in XSD 1.0;
- a need for clear, domain-specific error messages.

Schematron is not a good fit for:

- full mathematical expression parsing;
- TDB or CSdat grammar validation;
- operator precedence, tokenization, or AST checks;
- heavier numerical consistency rules.

## Practical Integration Note

The current Python stack can support ISO Schematron without changing languages.

Observed locally:

- `lxml` version `6.1.0` is installed;
- `lxml.isoschematron` imports successfully in the current environment.

That means a practical implementation path is:

1. keep the current XSD validation step;
2. add a Schematron validation step after XSD validation;
3. report XSD and Schematron failures separately in tests and scripts.

## Recommended Schematron Scope

Use Schematron only for rules that are both:

- important enough to justify machine enforcement; and
- naturally expressible as XPath-based assertions over the XML tree.

If a rule starts to require tokenizing expression text, evaluating arithmetic, or reimplementing a grammar, move it to Python instead.

## Candidate Rule Set

## Rule Family 1: MQM conditional rules

- `selected` should only appear on property types that actually use the selected-corner concept.
- If `selected` appears, it should refer to one of the current interaction constituents.
- If an MQM property is ternary-asymmetric and requires a selected corner, `selected` should be required, not merely optional.
- `MQM-L-RS` should use only the allowed `variant` vocabulary.
- If `variant` is present, the associated property type must be `MQM-L-RS`.

Why Schematron fits:

- the rule depends on property `xsi:type`;
- the rule often needs to inspect both the property node and its enclosing interaction;
- the error message should explain the model expectation, not just the XML shape.

## Rule Family 2: MQM charge and group consistency

- Species with positive charge should be in the cation group.
- Species with negative charge should be in the anion group.
- Species with zero charge should either be forbidden in MQM or assigned according to an explicitly documented policy.

Why Schematron fits:

- the rule is a co-constraint between two fields on the same node;
- it is declarative and easy to explain;
- it is stronger than a plain enum but does not require expression parsing.

## Rule Family 3: Ternary interpolation locator consistency

- For an interpolation, `i`, `j`, and `k` should each appear exactly once in the designated ternary site.
- The Toop `constant` value should match one of the located constituents for the relevant interpolation branch.
- `site` and `siteIndex` should not contradict each other when both are present.
- Interpolation locator usage should be disallowed outside the contexts that actually use ternary labeling.

Why Schematron fits:

- the rule depends on local context under one interpolation block;
- XPath can count and compare these values directly;
- the assertions are structural rather than grammatical.

## Rule Family 4: CEF and structure consistency

- The number of sublattice `site` elements should match the number of multiplicities.
- Endmember constituent site count should match the parent phase sublattice count.
- Interaction constituent site count should match the parent phase sublattice count.
- Crystallographic mapping `from` and `to` values should correspond to declared sites or site labels.

Why Schematron fits:

- these are cross-node consistency checks within the same phase subtree;
- XSD 1.0 can express the structure but not the count relationships cleanly.

## Rule Family 5: Ordered/disordered phase compatibility

- An ordered phase should reference a disordered phase that exists.
- Ordered and disordered phases should have compatible sublattice structures.
- If ordering metadata is present, it should be consistent with the linked disordered phase.

Why Schematron fits:

- the first part can be done in XSD with a keyref, but the structure-comparison logic is a better Schematron rule;
- the rule is cross-tree and model-aware but still declarative.

## Rule Family 6: Function range consistency

- Function ranges should be ordered by increasing lower bound.
- Each range should satisfy `low < high`.
- Adjacent ranges should not overlap.
- Optional later rule: adjacent ranges should either touch exactly or leave a documented gap.

Why Schematron fits:

- these checks compare sibling elements and their attributes;
- they do not require parsing the expression body itself.

## Rule Family 7: Metadata and citation consistency

- If a citation key field is introduced later, it should match a declared metadata reference key.
- If both free-text reference text and citation key are present, they should not be empty.
- Revision entries should be internally complete when present.

Why Schematron fits:

- these are document-level consistency rules over normal XML nodes and attributes.

## Conditional and Context-Sensitive Validation Patterns

The following patterns are where Schematron adds the most value in this project.

### Type-dependent requirements

These rules activate only when a node has a specific `xsi:type`.

Examples:

- only `MQM-L-RS` may carry `variant`;
- only Toop interpolations may carry a `constant` selector;
- only certain MQM property families may carry `selected`.

### Cross-field co-constraints

These rules compare multiple values on the same node.

Examples:

- charge sign versus MQM group;
- one attribute requiring or forbidding another;
- ensuring optional aliases do not conflict when both are present.

### Parent-child consistency

These rules compare a child node against declarations or counts in its parent scope.

Examples:

- endmember site count must match parent sublattice count;
- interaction constituents must align with the containing phase model;
- interpolation locators must be unique within the relevant site.

### Sibling-order and sibling-relationship checks

These rules compare one sibling element to another.

Examples:

- range ordering and overlap checks;
- ensuring only one of a set of mutually exclusive branches is populated;
- checking that mapped sites form a complete or non-duplicated set.

### Cross-tree lookup checks

These rules compare a local node with another declaration elsewhere in the document.

Examples:

- ordered phase structure compared to the referenced disordered phase;
- future citation keys matched to metadata reference entries;
- structure mappings validated against declared crystallographic sites.

## Rules That Should Stay Out of Schematron

- Parsing `expr` text into operators, identifiers, and numeric literals.
- Verifying TDB block syntax.
- Verifying CSdat block syntax.
- Checking whether an expression is thermodynamically meaningful.
- Evaluating continuity or differentiability of functions from parsed formulas.

These belong in a Python semantic validator.

## Proposed Implementation Strategy

### Phase 1: Keep Schematron small and high-value

Start with 5 to 10 rules that are clearly:

- stable in meaning;
- easy to explain to users;
- difficult or awkward to express in XSD 1.0.

Suggested first batch:

- MQM `selected` conditional usage;
- MQM `variant` conditional usage;
- charge versus group consistency;
- interpolation locator uniqueness;
- range ordering and non-overlap.

### Phase 2: Add a dedicated validation script or test layer

Suggested files:

- [tests/test_schematron_validation.py](tests/test_schematron_validation.py)
- [validate_all.py](validate_all.py)

Suggested validation order:

1. XSD validation
2. Schematron validation
3. Python semantic validation

### Phase 3: Keep rule ownership explicit

For each new validation rule, record why it lives in:

- XSD;
- Schematron; or
- Python.

This avoids gradual duplication across validation layers.

## Decision Recommendation

Introducing Schematron is reasonable if the project wants a middle layer between XSD and Python.

It is worth adding only if the team intends to enforce a concrete set of XPath-friendly, context-sensitive rules. If the backlog stays small, Python alone may be simpler. If the backlog grows into repeated cross-field and type-dependent checks, Schematron becomes a good fit.

Current recommendation:

1. land the safe XSD fixes first;
2. add a small Schematron layer for the best XPath-shaped rules;
3. keep expression parsing and other language-like validation in Python.