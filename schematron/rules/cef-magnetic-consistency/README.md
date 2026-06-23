# CEF Magnetic Consistency

Rule family:

- `VAL-WARN-CEF-MAGNETIC-STRUCTURE-WITHOUT-PARAMETERS`
- `VAL-WARN-CEF-MAGNETIC-PARAMETERS-WITHOUT-STRUCTURE`

A CEF phase can describe its magnetic behaviour in two complementary places:

- the **structure**, through a `<magnetic>` element inside `<structure>` (the
  Inden-Hillert-Jarl model factors `AFMFactor` and `structureFactorP`), and
- the **parameters**, through magnetic properties on endmembers and
  interactions: `xsi:type="M"` on an endmember (Curie/Néel temperature and
  magnetic moment), and `xsi:type="BML"` / `xsi:type="TCL"` on an interaction
  (magnetic moment and magnetic transition-temperature interaction terms).

In a well-formed assessment these two sides go together. A phase that declares a
magnetic model but lists no magnetic parameters is usually missing data, and a
phase that lists magnetic parameters but declares no magnetic model is usually
missing its structural magnetic description. Each direction emits a warning so
the omission can be confirmed or fixed; neither is hard-rejected, because edge
cases exist.

## Scope

The rule only fires on `xsi:type="CEFPhaseType"` phases. Ordered phases
(`xsi:type="CEFOrderedPhaseType"`) are deliberately excluded: they routinely
inherit the magnetic model of their parent disordered phase in `<structure>`
while declaring no magnetic parameters of their own, which is correct and would
otherwise trip the first warning on every ordered phase. This mirrors the
scoping already used by the `cef-endmember-cartesian-count` family.

## Files

- `rule.sch`: standalone Schematron wrapper for this family
- `module.sch`: the shared rule module
- `valid.xml`: passing fixture (one phase with both sides, one phase with
  neither)
- `warning.xml`: passing fixture that emits one warning of each kind
