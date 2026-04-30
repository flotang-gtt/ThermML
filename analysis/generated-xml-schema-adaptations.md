# Generated XML Schema Adaptations

## Scope

This document records the minimal schema changes made on branch `schema-validation-generated-xml` so that the emitted XML corpus in `C:\Users\GTT\ChemSage\udo\test-data\generated-xml` validates against the ThermML XSD set.

The goal of this pass was intentionally narrow:

- make the current emitted XML validate;
- avoid changing or deleting any emitted XML files;
- avoid broadening the schema beyond the concrete structures required by the failing files;
- record separately any structural concerns that should be addressed later in the emitter or model design.

## Baseline Validation Result Before Changes

Validation was run against 34 emitted XML files using `lxml` with `schema/thermml-schema.xsd`.

Before the schema update, 29 files passed and 5 files failed:

- `CrNbNi.dat.xml`
- `FTHall_rkmp_func.dat.xml`
- `JMDB_CsLiTh-FICl.dat.xml`
- `KMgNa-ClF_FTsalt_v7.3.dat.xml`
- `large_SUBQ.dat.xml`

The failures reduced to three concrete incompatibilities:

1. `selected` child elements appeared after `expr` in some `MQM-L-PF` and `MQM-L-RK` interaction properties, but the schema allowed only `expr`.
2. `MQM-L-RM` was used as an `xsi:type`, but no corresponding XSD type existed.
3. `MQM-L-RS` was used as an `xsi:type`, and one emitted instance also carried a `variant` attribute, but neither the type nor that attribute existed in the schema.

## Files Changed

- [schema/phases/quasichemical-phase.xsd](schema/phases/quasichemical-phase.xsd)

No emitted XML files were modified.

## Exact Schema Changes

### 1. Allowed optional `selected` for `MQM-L-PF`

In [schema/phases/quasichemical-phase.xsd](schema/phases/quasichemical-phase.xsd), the `MQM-L-PF` complex type now accepts:

- one or more `expr` elements, as before;
- followed by an optional `selected` element.

Reason:

- emitted ternary interaction records in files such as `CrNbNi.dat.xml` and `JMDB_CsLiTh-FICl.dat.xml` place a `selected` element after the indexed expression term;
- without this addition, those properties fail with `Element 'selected': This element is not expected`.

Why this was kept minimal:

- the change was limited to `MQM-L-PF`, where the failing corpus actually uses `selected`;
- no attempt was made to generalize `selected` across unrelated property families.

### 2. Allowed optional `selected` for `MQM-L-RK`

In [schema/phases/quasichemical-phase.xsd](schema/phases/quasichemical-phase.xsd), the `MQM-L-RK` complex type now accepts:

- one or more `expr` elements, as before;
- followed by an optional `selected` element.

Reason:

- emitted MQM interaction records in `large_SUBQ.dat.xml` use `selected` after the rank-indexed Redlich-Kister term;
- the previous schema rejected those records for the same reason as above.

Why this was kept minimal:

- only the specific failing type was widened;
- no additional attributes or alternate orderings were added.

### 3. Added concrete `MQM-L-RM` type

In [schema/phases/quasichemical-phase.xsd](schema/phases/quasichemical-phase.xsd), a new concrete type `MQM-L-RM` was added under the MQM interaction-property hierarchy.

Its admitted structure is intentionally narrow:

- base: `MQMInteractionPropertyType`;
- inherited optional metadata: `ref`, `comment`;
- exactly one `expr` child of type `xs:string`.

Meaning clarified from the SUBQ interaction design note:

- `MQM-L-RM` is the reciprocal middle parameter for a reciprocal interaction `A,B:X,Y`;
- it represents the fully symmetric center term of the reciprocal square;
- because the term is uniquely defined by the four constituents, it does not carry rank or selector indices.

Reason:

- emitted files `FTHall_rkmp_func.dat.xml`, `JMDB_CsLiTh-FICl.dat.xml`, and `KMgNa-ClF_FTsalt_v7.3.dat.xml` use `xsi:type="MQM-L-RM"`;
- the schema previously had no such type, so validation failed at type resolution before content could be checked.

Why this was kept minimal:

- only the shape observed in the emitted corpus was admitted;
- no extra attributes, no repeated expressions, and no inferred mathematical constraints were introduced.

### 4. Added concrete `MQM-L-RS` type with optional `variant`

In [schema/phases/quasichemical-phase.xsd](schema/phases/quasichemical-phase.xsd), a new concrete type `MQM-L-RS` was added under the MQM interaction-property hierarchy.

Its admitted structure is intentionally narrow:

- base: `MQMInteractionPropertyType`;
- inherited optional metadata: `ref`, `comment`;
- exactly one `expr` child with required integer attributes `i`, `j`, and `k`;
- optional `variant` attribute on the property itself.

Meaning clarified from the SUBQ interaction design note:

- `MQM-L-RS` is a reciprocal side parameter for a reciprocal interaction `A,B:X,Y`;
- `variant` identifies which side of the reciprocal square is parameterized;
- the current design note uses the vocabulary `A-BX-BY`, `B-AX-AY`, `X-AY-BY`, and `Y-AX-BX` for those side variants;
- the stored `i`, `j`, `k` attributes are ChemSage serialization indices whose mapping to physical side/corner exponents depends on that variant.

Reason:

- `KMgNa-ClF_FTsalt_v7.3.dat.xml` emits `xsi:type="MQM-L-RS"` with `variant="X-AY-BY"` and one indexed `expr` term;
- the previous schema rejected both the missing type and the unknown `variant` attribute.

Why this was kept minimal:

- the schema was expanded only to the exact structure present in the failing corpus;
- no enumeration or normalization of `variant` values was attempted;
- no support for repeated `expr` elements was added because the current emitted XML did not require it.

### 5. Updated local documentation on `MQMInteractionType`

The annotation text in [schema/phases/quasichemical-phase.xsd](schema/phases/quasichemical-phase.xsd) was updated so the documented list of supported MQM interaction property types matches the concrete schema after the additions above.

This is documentation-only and does not change validation behavior.

## Deliberate Non-Changes

The following were intentionally not changed in this pass:

- no emitted XML files were edited;
- no other schema modules were changed;
- no attempt was made to reinterpret the semantics of `selected`, `MQM-L-RM`, `MQM-L-RS`, or `variant` beyond what was necessary for validation;
- no stronger typing, cross-reference constraints, enumerations, or model-level refactors were introduced.

Those topics are recorded separately in [analysis/generated-xml-structural-concerns.md](analysis/generated-xml-structural-concerns.md).

## Validation After Changes

Two validation checks were run after the schema edit.

### Emitted XML corpus

- target set: 34 XML files in `C:\Users\GTT\ChemSage\udo\test-data\generated-xml`
- result: 34 passed, 0 failed

### Repository example corpus

The existing repository validation script was also rerun:

- command: `c:/Users/GTT/ThermML/.venv/Scripts/python.exe validate_all.py`
- result: 3 passed, 0 failed

Validated example files:

- `examples/basic-example.xml`
- `examples/quasichemical.xml`
- `examples/simple_solution.xml`

## Summary

The schema change set was restricted to one file, [schema/phases/quasichemical-phase.xsd](schema/phases/quasichemical-phase.xsd), and only to the emitted MQM interaction forms that were demonstrably failing validation.

This resolves the current validation mismatch without broad schema redesign.