# Generated XML Structural Concerns

## Purpose

This document records structural and modeling concerns observed in the emitted XML corpus during the validation pass.

These concerns were **not** normalized away in the schema update because the requested scope was to make validation pass with the smallest necessary XSD changes.

## Concern 1: `selected` is semantically under-specified

Observed in emitted MQM interaction properties such as:

- `MQM-L-PF` entries in `CrNbNi.dat.xml` and `JMDB_CsLiTh-FICl.dat.xml`
- `MQM-L-RK` entries in `large_SUBQ.dat.xml`

Current emitted pattern:

- a property already identifies participating species through its parent `interaction/constituents` structure;
- a trailing `selected` string then names one species again, for example `Cr`, `Ni`, `Cs`, `Al`, `Fe`, or `Si`.

Why this is structurally weak:

- the meaning of `selected` is not self-describing from the XML shape alone;
- it is a free string rather than a typed reference to one of the constituents;
- it duplicates information already present in the structured constituent array;
- nothing in the schema can guarantee that the named species actually belongs to the interaction in which it appears.

Why it matters:

- emitter and consumer can silently disagree on what `selected` means;
- a typo or stale species name would still validate under the current minimal schema;
- the information is model-critical but only weakly encoded.

Recommended later direction:

- replace `selected` free text with a structured selector tied to the interaction constituents;
- at minimum, define whether it refers to a species identity, a sublattice position, or a ternary interpolation branch.

## Concern 2: `MQM-L-RM` and `MQM-L-RS` are schema-admitted but not formally modeled

Observed in emitted XML:

- `MQM-L-RM` in `FTHall_rkmp_func.dat.xml`, `JMDB_CsLiTh-FICl.dat.xml`, and `KMgNa-ClF_FTsalt_v7.3.dat.xml`
- `MQM-L-RS` in `KMgNa-ClF_FTsalt_v7.3.dat.xml`

Why this is structurally weak:

- the type names carry domain semantics, but the schema has no canonical explanation of what `RM` and `RS` mean mathematically;
- the admitted structure was derived from current emitter output, not from a formal ThermML model definition;
- cardinality and parameterization are only minimally constrained because the current data set provides too little information to infer a stronger model safely.

Why it matters:

- other emitters or future versions of the same emitter may produce different shapes for these type names;
- consumers cannot rely on the XSD alone to understand whether these are regular-model, reciprocal-model, or some other MQM parameter families.

Recommended later direction:

- document the exact thermodynamic meaning of each MQM subtype in the schema and project documentation;
- decide whether these types should remain distinct concrete names or collapse into a more explicit parameter family with structured attributes.

## Concern 3: `variant` encodes model semantics as an opaque string

Observed in emitted XML:

- `MQM-L-RS` with `variant="X-AY-BY"` in `KMgNa-ClF_FTsalt_v7.3.dat.xml`

Why this is structurally weak:

- the value is opaque and currently unconstrained;
- it appears to encode model form or coefficient interpretation, but that meaning is not machine-readable;
- the schema cannot distinguish allowed values, equivalent spellings, or future incompatible variants.

Why it matters:

- the same physical concept can drift into multiple spellings;
- consumers have to hard-code string parsing rules instead of relying on schema structure;
- future variants could accidentally reuse the same field with incompatible semantics.

Recommended later direction:

- decide whether `variant` should be an enumeration, a structured element, or an explicit subtype split;
- document the allowed vocabulary and the meaning of each value.

## Concern 4: important MQM semantics are split across `xsi:type`, local shape, and free text

Across the failing examples, meaning is distributed across three separate mechanisms:

- `xsi:type` names such as `MQM-L-PF`, `MQM-L-RK`, `MQM-L-RM`, and `MQM-L-RS`;
- local `expr` index attributes such as `rank`, `i`, `j`, and `k`;
- free-text fields such as `selected` and `variant`.

Why this is structurally weak:

- the same logical concept is not represented in one normalized place;
- some semantics are strongly typed while others are opaque strings;
- validation can confirm surface shape but not model consistency.

Why it matters:

- the XML remains valid while still being under-specified for downstream interpretation;
- schema evolution becomes harder because semantics are encoded partly in names and partly in ad hoc fields.

Recommended later direction:

- define a more explicit MQM interaction-property vocabulary;
- move model-defining choices from free text into typed elements or constrained attributes where possible.

## Practical Recommendation

For the current branch, these concerns should remain documentation only.

The implemented schema changes are intentionally minimal and validation-driven. A later design pass can tighten the model once the intended semantics of MQM interaction variants and ternary selection are agreed.