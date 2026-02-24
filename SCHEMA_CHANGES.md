# ThermML Schema Changes Documentation

This document summarizes all schema and XML changes made to achieve full validation of 33 example XML files against the ThermML XSD schema. It also documents remaining design issues and required serializer updates.

---

## Summary

Starting state: 1/33 files passing validation
Final state: **33/33 files passing validation**

---

## Schema Changes

### 1. Metadata Relaxation (WI-8)
**File:** `schema/metadata/main.xsd`
- `AuthorsType`: child `<author>` minOccurs changed from `1` to `0` (allow empty authors block)
- `RevisionsType`: child `<revision>` minOccurs changed from `1` to `0`
- `ReferencesType`: child `<reference>` minOccurs changed from `1` to `0`
- `<created>`: type changed from `xs:date` to `xs:string` (allows empty string)

### 2. CEF Phase Structure Rework (WI-1, WI-18, H2)
**File:** `schema/phases/cef-phase.xsd`
- `CEFPhaseType`: Replaced `xs:choice` with strict sequence: `description`, `species`, `structure`, `assessedSystems`, `ordering`, `endmembers` (wrapper), `interactions` (wrapper)
- Added `<endmembers>` wrapper containing `<endmember>` children
- Added `<interactions>` wrapper containing `<interaction>` children
- `CEFInteractionType`: Now extends `AbstractInteractionType` with `<property type="PhasePropertyType">` children
- `CEFEndmemberType`: constituents now uses unified `ConstituentArrayType`
- `CEFSpeciesType`: child element renamed from `<species>` to `<specie>` (I1)
- `assessedSystems` renamed from `assessed_systems` (I3)

### 3. Ordered Phase (WI-6)
**File:** `schema/phases/ordered-phase.xsd`
- Added `disorderedPhase` attribute (xs:string, required) to `CEFOrderedPhaseType`

### 4. MQM Phase Structure (WI-4, WI-10, WI-17)
**File:** `schema/phases/quasichemical-phase.xsd`
- `ModifiedQuasichemicalPhaseType`: Replaced `xs:choice` with strict sequence: `numberOfDatComponents`, `description`, `species`, `endmembers`, `quadruplets`, `interactions`, `ternaryInterpolations`
- Element ordering: `quadruplets` comes **before** `interactions` (matching serializer output)
- Added `<numberOfDatComponents>` element for serialization metadata
- `MQMEndmemberType`: `description` made optional, added optional `<comment>`, `stoichiometry` made optional
- `MQM-G`: `expr` element now has `type="xs:string"`

### 5. MQM Quadruplet Changes
**File:** `schema/phases/quasichemical-phase.xsd`
- Renamed container child from `<quad>` to `<quadruplet>`
- Renamed site elements from uppercase `<A>`, `<B>`, `<X>`, `<Y>` to lowercase `<a>`, `<b>`, `<x>`, `<y>`
- `MQMquadSite`: Renamed `value` attribute to `Z` (coordination number), made both `species` and `Z` required

### 6. New MQM Interaction Property Types (WI-3)
**File:** `schema/phases/quasichemical-phase.xsd`
- Added `MQM-L-SP` (Simple Polynomial interaction)
- Added `MQM-L-Reciprocal` (Reciprocal interaction with i, j, k indices)
- Added `MQM-L-Quasichemical` (Quasichemical equilibrium constant)
- `MQM-L-PF`: added optional `k` attribute for ternary pair-fraction interactions

### 7. Ternary Interpolation Changes
**Files:** `schema/phases/quasichemical-phase.xsd`, `schema/phases/core.xsd`
- `<ternaryInterpolations>`: child `<interpolation>` minOccurs changed from `1` to `0` (allows empty container)
- `core.xsd` ternary interpolation `<const>`: converted from `simpleContent` (text-based) to attribute-based format matching `ConstituentArrayType`
- Species is now specified via a **required** `species` attribute: `<const species="..." site="i"/>`
- Both `site` and `siteIndex` attributes are accepted as ternary interpolation locators
- All XML files updated: `<const siteIndex="i">SpeciesName</const>` → `<const species="SpeciesName" site="i"/>`

### 8. Unified Constituent Array Type (H3/WI-5/WI-9)
**File:** `schema/phases/quasichemical-phase.xsd`
- Created `ConstituentArrayType`: unified type shared by CEF and MQM models for endmember and interaction constituents
- `<const>` element uses a strict attribute-only format: `<const species="..."/>`
- `species` attribute is **required** (`use="required"`) — species must always be specified as an attribute, never as text content
- The ternary interpolation constituent type (`core.xsd`) now follows the same attribute-based pattern

### 9. Abstract Interaction Type (H2)
**File:** `schema/phases/quasichemical-phase.xsd`
- Created `AbstractInteractionType` (abstract): shared base for `CEFInteractionType` and `MQMInteractionType`
- Contains: `name` attribute, `constituents`, `description`, `ref`, `comment`

### 10. Property Type Hierarchy (H1/WI-11)
**File:** `schema/phases/quasichemical-phase.xsd`
- `MQMEndmemberPropertyType` now extends `PhasePropertyType` (was `AbstractPhasePropertyType`)
- Enables MQM endmembers to use physical properties (MolarVolume, ThermalExpansion, etc.) via `xsi:type`

### 11. chargeValues Pattern (WI-14)
**File:** `schema/phases/quasichemical-phase.xsd`
- Changed from enumeration to pattern: `0|[+-]?[1-8]`

### 12. FunctionIDType Pattern Relaxation
**File:** `schema/expressions/core.xsd`
- Pattern relaxed from strict alphanumeric to `[^ \t\r\n]+` (any non-whitespace)
- Needed to accommodate function names with `-`, `/`, `.`, `<>`, `,`, `#` prefix, etc.

### 13. ConstituentSpeciesType Pattern
**File:** `schema/simple-types/main.xsd`
- Pattern changed from `[^ \t\r\n]+` to `\s*[^ \t\r\n]+\s*`
- Allows surrounding whitespace in multi-line XML text content

### 14. Phase Property Documentation (I4/I5)
**File:** `schema/phases/phase-properties.xsd`
- `L` type: documentation corrected to describe Redlich-Kister polynomial interaction parameter
- `BML` type: documentation corrected to describe magnetic Redlich-Kister interaction parameter

### 15. Naming Conventions (I1, I3)
- Child `<species>` → `<specie>` inside species containers (all XML files)
- `molar_mass` → `molarMass` (schema + all XML files)
- `assessed_systems` → `assessedSystems` (schema + all XML files)

---

## XML File Changes

### Bulk changes applied to all/most example XML files:
1. `<species name="..."/>` → `<specie name="..."/>` (child elements inside `<species>` containers)
2. `molar_mass=` → `molarMass=`
3. `assessed_systems` → `assessedSystems`
4. Added `<endmembers>`/`<interactions>` wrapper elements where missing

### Hand-crafted example file updates:
- **`basic-example.xml`**: Added metadata block, renamed molarMass
- **`simple_solution.xml`**: Full rewrite to new wrapper format
- **`quasichemical.xml`**: Full rewrite — MQM constituents to species attr, wrappers, `<quad>` → `<quadruplet>`, uppercase → lowercase site elements, `value` → `Z`, reordered quadruplets before interactions

---

## Required Serializer Changes

The XML serializer must be updated to match the new schema. Here are the specific changes:

### Element Structure
1. **CEF phases**: Emit `<endmembers><endmember>...</endmember></endmembers>` wrappers (not bare `<endmember>` children)
2. **CEF phases**: Emit `<interactions><interaction>...</interaction></interactions>` wrappers
3. **MQM phases**: Use strict element order: `numberOfDatComponents` → `description` → `species` → `endmembers` → `quadruplets` → `interactions` → `ternaryInterpolations`
4. **MQM quadruplets**: Use `<quadruplet>` (not `<quad>`) as child element name
5. **MQM quadruplet sites**: Use lowercase `<a>`, `<b>`, `<x>`, `<y>` elements
6. **MQM quadruplet sites**: Use `Z` attribute (not `value`) for coordination numbers

### Attribute Naming
7. `molar_mass` → `molarMass` on `<systemComponent>`
8. `assessed_systems` → `assessedSystems` on `<phase>`
9. Species child elements: `<specie name="..."/>` (not `<species>`)

### Type System
10. **CEF interactions**: Use `AbstractInteractionType` base with structured `<constituents>` element (not string attribute)
11. **MQM endmember properties**: Use `PhasePropertyType` base with `xsi:type` dispatch (e.g., `xsi:type="MQM-G"`, `xsi:type="MolarVolume"`)
12. **MQM interaction properties**: Use `MQMInteractionPropertyType` base with `xsi:type` dispatch (e.g., `xsi:type="MQM-L-PF"`, `xsi:type="MQM-L-RK"`, `xsi:type="MQM-L-SP"`, `xsi:type="MQM-L-Reciprocal"`, `xsi:type="MQM-L-Quasichemical"`)

### Constituent Arrays
13. Endmember/interaction constituents: **Must** use `<constituents><site><const species="..."/></site></constituents>` structure — the `species` attribute is required, text content is not allowed
14. Ternary interpolation constituents (in `core.xsd`): **Must** use `<const species="..." site="i"/>` attribute-based format — text content is no longer accepted. Both `site` and `siteIndex` attributes are valid for the ternary locator

### New Optional Elements
15. `<numberOfDatComponents>` on MQM phases (serialization metadata)
16. `<comment>` on MQM endmembers
17. Optional `k` attribute on `MQM-L-PF` expr elements (for ternary interactions)

---

## Remaining Design Issues

### 1. `siteIndex` vs `site` Attribute Duplication
In the ternary interpolation constituent type (`core.xsd`), both `site` and `siteIndex` attributes are accepted as locators. This creates ambiguity — both should not be set simultaneously. The serializer should prefer `site` as the canonical attribute name, but must accept `siteIndex` on input.

### 2. FunctionIDType Pattern is Very Permissive
The `FunctionIDType` pattern was relaxed to `[^ \t\r\n]+` (any non-whitespace string). This is intentionally permissive to accommodate the diverse function naming conventions in existing databases, but provides minimal validation. A stricter pattern could be defined once all naming conventions are catalogued.

### 3. Empty Container Elements
Several container elements allow empty children (`<ternaryInterpolations/>`, `<interactions/>`, etc.). The serializer should either omit empty containers entirely or handle them gracefully.

### 4. `chargeValues` Allows Unsigned Integers
The pattern `0|[+-]?[1-8]` allows charges without explicit sign (e.g., `1` instead of `+1`). The serializer should normalize to always include the sign prefix for clarity, but the schema accepts either form.

---

## Validation

Run the validation script to verify all 33 files pass:

```bash
uv run --with lxml python validate_all.py
```

Expected output: `Results: 33 passed, 0 failed, 33 total`
