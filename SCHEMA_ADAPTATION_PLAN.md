# ThermML Schema Adaptation Plan

This document details all changes needed to make the new example XML files validate against the ThermML XSD schema. Changes are grouped into logical work items, with semantic documentation for each element/attribute for your review.

---

## Validation Strategy

**Recommended approach:** Use Python with `lxml` to validate all XML files against the schema, run via `uv`.

```bash
uv run --with lxml python validate_all.py
```

A simple validation script (e.g. `validate_all.py`) would:
1. Parse `schema/thermml-schema.xsd` into an `XMLSchema` object
2. Iterate over all `examples/*.xml` files
3. Validate each, collecting and reporting errors per file
4. Return exit code 0 only if all files pass

This gives deterministic, repeatable proof of validation.  We should create this script as part of Work Item 0.

---

## Work Item 0: Create Validation Test Script

Create `validate_all.py` at the repository root that uses `lxml` to validate all example XMLs against the schema and reports errors. This should be the first step so we can run it iteratively after each schema change.

---

## Work Item 1: CEF Phase Structure Rework (`<endmembers>` and `<interactions>` Wrappers)

### Problem

The current schema defines `CEFPhaseType` with endmember and interaction elements directly inside a `<xs:choice>`:

```xml
<xs:choice maxOccurs="unbounded">
    <xs:element name="endmember" type="CEFEndmemberType" ... />
    <xs:element name="interaction" ... />
</xs:choice>
```

All new XML files (26 of them) use **wrapper elements** `<endmembers>` and `<interactions>`:

```xml
<endmembers>
    <endmember name="..."> ... </endmember>
</endmembers>
<interactions>
    <interaction name=""> ... </interaction>
</interactions>
```


### Changes Required
- Replace direct elements with wrapper-only pattern

### Documentation

- **`<endmembers>`**: Container element grouping all endmember definitions of a CEF phase. Endmembers represent the pure compounds that occupy the sublattice sites, each with defined thermodynamic properties.
- **`<interactions>`**: Container element grouping all interaction parameters of a CEF phase. Interactions describe excess mixing energies or other properties between endmembers using Redlich-Kister or other polynomial expansions.

---

## Work Item 2: CEF Interaction Type Rework

### Problem

The current `CEFInteractionType` uses a `constituents` **attribute** (string):

```xml
<xs:attribute use="required" name="constituents" type="xs:string" />
```

The new XML files use a **completely different structure**: a `name` attribute plus child `<constituents>` element with structured `<site>/<const>` children, plus an optional `<description>` element:

```xml
<interaction name="">
    <constituents>
        <site>
            <const species="Cr"/>
            <const species="Ni"/>
        </site>
        <site>
            <const species="Va"/>
        </site>
    </constituents>
    <description/>
    <property xsi:type="L"> ... </property>
</interaction>
```

### Changes Required

This should be implemented as part of the interaction type unification (see **H2**):

- Create an abstract `AbstractInteractionType` with the shared structure: `name` attribute, `<constituents>` child element, optional `<description>`, `<ref>`, `<comment>`
- Derive `CEFInteractionType` from `AbstractInteractionType`, adding `<xs:element name="property" type="PhasePropertyType"/>` (schema-level base type; instances use `xsi:type` to select concrete subtypes like `L`, `BML`, `G`, `M`)
- Derive `MQMInteractionType` from `AbstractInteractionType`, adding `<xs:element name="property" type="MQMInteractionPropertyType"/>` (schema-level base type; instances use `xsi:type` to select `MQM-L-PF`, `MQM-L-RK`, etc.)
- The `constituents` child element should use the unified `ConstituentArrayType` (see **H3**)
- Remove the old `constituents` string attribute from `CEFInteractionType`

### Documentation

- **`<interaction>`**: Represents an excess energy interaction between two or more constituents mixing on the same sublattice site. The interaction constituents are defined structurally (via nested `<site>/<const>` elements) rather than as a flat string.
- **`name` attribute**: Human-readable label for the interaction, typically in the form `"A,B:C"` denoting which species interact on which sublattice. May be empty.
- **`<constituents>` (child element)**: Structured definition of which species participate in the interaction, organized by sublattice site. Uses the unified `ConstituentArrayType`.
- **`<description>`**: Optional free-text description or annotation for the interaction.

---

## Work Item 3: New MQM Interaction Property Types

### Problem

The schema defines `MQM-L-PF` (pair fraction) and `MQM-L-RK` (Redlich-Kister) as concrete subtypes of `MQMInteractionPropertyType`. The new XML files use three additional subtypes that do not exist in the schema:

1. **`MQM-L-SP`** - "Simple Polynomial" interaction model (used in 4 files)
2. **`MQM-L-Reciprocal`** - Reciprocal interaction parameter (used in 3 files)
3. **`MQM-L-Quasichemical`** - Quasichemical interaction parameter (used in 2 files)

All three share the same `<expr>` element structure as `MQM-L-PF`, with `i` and `j` integer attributes. `MQM-L-Reciprocal` additionally uses a `k` attribute.

### Changes Required

Add three new complex types extending `MQMInteractionPropertyType`:

**`MQM-L-SP`** (Simple Polynomial):
- Extends `MQMInteractionPropertyType`
- Contains `<expr>` elements with `i` and `j` integer attributes (same structure as `MQM-L-PF`)
- Semantics: Represents a Simple Polynomial (SP) interaction model where the excess energy is expressed as a polynomial in pair fractions, used when a simple polynomial multiplication represents the mixing interaction.

**`MQM-L-Reciprocal`**:
- Extends `MQMInteractionPropertyType`
- Contains `<expr>` elements with `i`, `j`, **and `k`** integer attributes
- Semantics: Represents a reciprocal interaction in systems with more than two sublattices (e.g., cation-cation mixing on one sublattice with simultaneous anion-anion mixing on another). The third index `k` addresses the additional degree of freedom from the reciprocal reaction.

**`MQM-L-Quasichemical`**:
- Extends `MQMInteractionPropertyType`
- Contains `<expr>` elements with `i` and `j` integer attributes (same structure as `MQM-L-PF`)
- Semantics: Represents interaction parameters expressed directly in the quasichemical formalism, as opposed to pair-fraction or Redlich-Kister expansions. These are polynomial coefficients applied to the quasichemical equilibrium constant.

### Note on `<expr>` attribute `k`

The `MQM-L-PF` type also uses a `k` attribute in some ternary contexts (see `KMgNa-ClF_FTsalt_v7.3.dat.xml` line 1216: `<expr i="0" j="0" k="1">`). The existing `MQM-L-PF` schema only defines `i` and `j`. An optional `k` attribute should be added to `MQM-L-PF` as well, for ternary pair-fraction interactions.

### Disambiguation Recommendation

All MQM interaction property types share a similar `<expr>` structure but differ semantically in how the polynomial coefficients are applied within the model. Using `xsi:type` is appropriate and sufficient for disambiguation. No structural changes are needed beyond defining the types in the schema hierarchy.

---

## Work Item 4: MQM Phase Structure Additions

### Problem

The `ModifiedQuasichemicalPhaseType` schema is missing several elements present in the new XML files.

### 4a: `<numberOfDatComponents>` Element

**Used in**: 6 files (FTHall, KMgNa-ClF, JMDB, Fe-Nb-Ni, Shishin, large_SUBQ). Should be present in all SUBQ-Phase elements.

```xml
<phase xsi:type="ModifiedQuasichemicalPhaseType" name="LIQUID" state="liquid">
    <numberOfDatComponents>55</numberOfDatComponents>
    <description/>
    ...
```

This element appears **before** `<description>` and `<species>` in the sequence.

- **Semantics**: An integer indicating how many species (dat-file constituents) are defined in this phase model. This is a serialization artifact from the ChemSage `.dat` format and serves as a consistency check.
- **Type**: `xs:integer`, optional, `minOccurs="0"`

### 4b: MQM Interaction Structure

The schema defines `<interactions>` inside a `<xs:choice>` with specific child structure. The new XML files use the same `<interactions>/<interaction>` pattern but:

- Add a `name` attribute on `<interaction>` elements (e.g., `name="Fe,Nb:Va"`)
- Use `<constituents>` with `<site>/<const species="..."/>` child elements (using `species` attribute, not text content)
- Allow `<ref>` and `<comment>` to be optional (minOccurs="0") - currently schema requires minOccurs="1"

### Changes Required

- Add optional `<numberOfDatComponents>` element (xs:integer) at the beginning of `ModifiedQuasichemicalPhaseType` sequence, before `<description>`
- Add `name` attribute (xs:string, optional) to the MQM `<interaction>` inline type
- Change `<ref>` and `<comment>` in MQM `<interaction>` from `minOccurs="1"` to `minOccurs="0"`
- Change MQM interaction `<const>` elements to use `species` attribute (like CEF) instead of text content, OR support both patterns

### Documentation

- **`<numberOfDatComponents>`**: Serialization metadata from ChemSage .dat format. Indicates the number of distinct species constituents in this quasichemical model. Used for format-level consistency validation, not for thermodynamic computation.
- **`name` (on interaction)**: Human-readable label identifying the interacting species pair (e.g., `"Na[+],Mg[2+]:Cl[-]"`). Serves as documentation, not as a programmatic key.

---

## Work Item 5: MQM Interaction Constituents - `species` Attribute vs. Text Content

### Problem

The MQM interaction constituent array (`MQMInteractionConstituentArrayType`) defines `<const>` elements that use **text content** for the species name:

```xml
<!-- Schema expects: -->
<const>Na+</const>

<!-- New files use: -->
<const species="Na[+]"/>
```

All new MQM files consistently use the `species` **attribute** pattern (matching the CEF `CEFConstituentArrayType` convention).

### Changes Required

**Unify with CEF pattern**
- Modify `MQMInteractionConstituentArrayType` to use `species` attribute on `<const>`, matching `CEFConstituentArrayType`
- Potentially merge into a single shared constituent array type
- The old schema representation can be removed

---

## Work Item 6: CEFOrderedPhaseType - `disorderedPhase` Attribute

### Problem

`CEFOrderedPhaseType` extends `CEFPhaseType` but is currently empty (contains only a TODO comment). The new XML files use a `disorderedPhase` attribute:

```xml
<phase xsi:type="CEFOrderedPhaseType" name="BCC_B2" disorderedPhase="BCC_A2" state="solid">
```

**Used in**: 3 files (AlCoFeNi_SUBO, Fe-Nb-Ni_OptD85Start, FeAlCNiCrMnSiVCo_FSSteel)

### Changes Required

- Add `disorderedPhase` attribute (xs:string, required) to `CEFOrderedPhaseType`

### Documentation

- **`disorderedPhase`**: References the name of the parent disordered phase from which this ordered phase derives. In the CALPHAD approach, ordered phases (e.g., B2, L12) are modeled as a partitioning of the sublattice model of a parent disordered phase (e.g., BCC_A2, FCC_A1). The Gibbs energy of the ordered phase is computed as G_ordered = G_disordered + delta_G_ordering. This attribute establishes that link.

---

## Work Item 7: `SystemComponentIdType` Pattern Expansion

### Problem

The current `SystemComponentIdType` uses the pattern `[A-Z][a-z]?`, which matches standard element symbols (e.g., "Al", "Fe", "O").

However, there is a question of whether element symbols with 3+ characters (not encountered yet) or other non-standard symbols might be needed in the future. 

### Changes Required

No change needed for current files - e.g. `Qe` matches `[A-Z][a-z]?`. But this should be verified against all example files.

**Verified**: All `symbol` values across examples are standard 1-2 letter chemical element symbols or `Qe`. No changes needed.

---

## Work Item 8: Metadata Relaxation - Empty Elements

### Problem

All new XML files use empty elements for metadata fields:

```xml
<metadata>
    <title/>
    <version>1.0</version>
    <description/>
    <license/>
    <authors/>
    <created/>
    <revisions/>
    <references/>
</metadata>
```

The current schema requires:
- `<title>` as `xs:string` (required) - empty string should be fine
- `<license>` as `xs:string` (required) - empty string should be fine
- `<authors>` as `AuthorsType` (optional) - but `AuthorsType` requires at least one `<author>` child element
- `<revisions>` as `RevisionsType` (optional) - requires at least one `<revision>` child
- `<references>` as `ReferencesType` (optional) - requires at least one `<reference>` child
- `<created>` as `xs:date` (optional) - empty string is NOT a valid `xs:date`

Self-closing tags like `<authors/>` are equivalent to `<authors></authors>`, which means empty content. For complex types that require child elements, this will fail validation.

### Changes Required

- `<authors>`: Change the element type to allow empty content (e.g., make it nillable, or change the child `<author>` to `minOccurs="0"`)
- `<revisions>`: Same - allow empty content by setting child `<revision>` to `minOccurs="0"`
- `<references>`: Same - allow empty content by setting child `<reference>` to `minOccurs="0"`
- `<created>`: Either make it a union type (xs:date | empty string), or use nillable="true", or change the type to xs:string with an optional pattern
- Alternatively, consider making all these elements truly optional (`minOccurs="0"`) so they can be omitted entirely

### Documentation

These are metadata fields. Making them optional or allowing empty content is appropriate for draft/generated databases where metadata may not be fully populated yet.

---

## Work Item 9: MQM Endmember Constituent `<const>` - `species` Attribute

### Problem

The `MQMConstituentArrayType` defines `<const>` as type `ConstituentSpeciesType` (a simple type using text content):

```xml
<!-- Schema expects: -->
<const>Na+</const>
```

But all new MQM files use a `species` attribute:

```xml
<const species="Al"/>
```

This is the same pattern used in CEF `CEFConstituentArrayType`.

### Changes Required

- Modify `MQMConstituentArrayType` to use `species` attribute on `<const>` (same as `CEFConstituentArrayType`)
- Or introduce a shared `ConstituentArrayType` used by both CEF and MQM

### Documentation

- **`<const species="...">`**: References a species by name. The species must be defined in the parent phase's `<species>` block. Using an attribute rather than text content is consistent with the CEF pattern and avoids whitespace ambiguity.

---

## Work Item 10: MQM Endmember Structure - `<comment>` Element and Optional Fields

### Problem

The `MQMEndmemberType` requires `<description>` as a mandatory element. New XML files include both `<description/>` (empty) and `<comment/>` elements:

```xml
<endmember name="Al">
    <description/>
    <comment/>
    <constituents>...</constituents>
    <property xsi:type="MQM-G">...</property>
</endmember>
```

The `<comment>` element is not defined in `MQMEndmemberType`.

### Changes Required

- Add optional `<comment>` element (xs:string, minOccurs="0") to `MQMEndmemberType`, after `<description>`
- Make `<description>` optional (minOccurs="0")

---

## Work Item 11: MQM Endmember Properties - Physical Properties (MolarVolume, etc.)

### Problem

MQM endmembers use `PhasePropertyType`-derived property types via `xsi:type` (e.g., `MolarVolume`, `ThermalExpansion`, `Compressibility`, `BulkModulusDerivative`), but the `MQMEndmemberType` schema only allows `MQMEndmemberPropertyType`:

```xml
<xs:element name="property" type="MQMEndmemberPropertyType" minOccurs="1" maxOccurs="unbounded" />
```

The physical property types (`MolarVolume`, `ThermalExpansion`, etc.) extend `PhasePropertyType`, not `MQMEndmemberPropertyType`. So they can't be used as `xsi:type` substitutions.

### Changes Required

**Reparent `MQMEndmemberPropertyType` to extend `PhasePropertyType`** (see H1 for full rationale):
- Change `MQMEndmemberPropertyType` to extend `PhasePropertyType` instead of `AbstractPhasePropertyType`
- Keep `MolarVolume`, `ThermalExpansion`, `Compressibility`, `BulkModulusDerivative` extending `PhasePropertyType` (no change needed for these)
- Change `MQMEndmemberType`'s property element to `<xs:element name="property" type="PhasePropertyType"/>` (schema-level base type)

This allows MQM endmembers to use `xsi:type` to select both MQM-specific properties (e.g., `xsi:type="MQM-G"`) and general physical properties (e.g., `xsi:type="MolarVolume"`), while ensuring MQM interaction types (`MQM-L-PF`, etc.) are blocked because they don't extend `PhasePropertyType`.

### How `type` and `xsi:type` work together

The schema `type` attribute on `<xs:element>` declares the **base type family**. In the XML instance, the `xsi:type` attribute selects a **concrete subtype**. XSD validation enforces that the `xsi:type` value must be a subtype of the declared `type`. This is how polymorphic dispatch works in XSD - it requires both levels.

---

## Work Item 12: CEF Endmember Properties - Using `xsi:type` Dispatch

### Problem

The `CEFEndmemberType` defines properties as:

```xml
<xs:element name="property" type="PhasePropertyType" minOccurs="0" maxOccurs="unbounded" />
```

The new XML files use `xsi:type` on `<property>` to dispatch to concrete types (`G`, `M`, `MolarVolume`, `ThermalExpansion`, etc.):

```xml
<property xsi:type="G">
    <ref/>
    <comment/>
    <expr>+1*{AlVa#BCC_A2}</expr>
</property>
```

For `xsi:type` substitution to work, the schema-level `type` on `<xs:element>` must be a **base type or ancestor** of the `xsi:type` value used in the XML instance. Since `G`, `M`, `L`, `BML`, `MolarVolume`, etc. all extend `PhasePropertyType`, the current schema declaration `<xs:element name="property" type="PhasePropertyType"/>` allows instances to use `xsi:type="G"`, `xsi:type="M"`, `xsi:type="MolarVolume"`, etc.

### Verification Needed

Confirm that `PhasePropertyType` is the correct schema-level base. If any property type used on CEF endmembers extends a different base (not `PhasePropertyType`), the schema `type` would need to be broadened to `AbstractPhasePropertyType`.

### Changes Required

Likely **no schema change needed** for CEF endmember properties, but validate with the test script. The existing schema `type="PhasePropertyType"` should support `xsi:type` dispatch to all its subtypes.

---

## Work Item 13: CEF Interaction Properties - `xsi:type` Dispatch

### Problem

Similar to Work Item 12, CEF interactions need to use `xsi:type` dispatch for properties. The current `CEFInteractionType` schema has `<property>` typed as `PhasePropertyType`. Interaction properties use types like `L`, `BML`, `G`, `M`, etc.

### Changes Required

The `CEFInteractionType` restructuring (Work Item 2) should ensure the `<property>` element declares `type="PhasePropertyType"` in the schema. This allows XML instances to use `xsi:type="L"`, `xsi:type="BML"`, `xsi:type="G"`, `xsi:type="M"`, etc. - all of which extend `PhasePropertyType` and are therefore valid substitutions.

---

## Work Item 14: `chargeValues` Type Expansion

### Problem

The MQM `chargeValues` type uses a fixed enumeration of "+1" to "+8" and "-1" to "-8". However, the new XML files sometimes use charge values like `"1"` and `"-1"` (without explicit `+` sign):

```xml
<specie name="Al" composition="Al" charge="1" group="1"/>
<specie name="Va" composition="Va" charge="-1" group="1"/>
```

The value `"1"` (without `+`) is **not** in the enumeration - only `"+1"` is.

### Changes Required

Use a pattern restriction: `[+-]?[1-8]` or `(\+?[1-8])|(-[1-8])`.

`"0"` should be a valid charge. CEF uses `SignedIntegerString` for charges, which allows `"0"`. For consistency, MQM should probably also allow neutral species.

---

## Work Item 15: MQM `<coordinationNumbers>` - Element Order Flexibility

### Problem

The `MQM-G` type defines `<coordinationNumbers>` with a strict sequence: `<comment>`, `<cation>`, `<anion>`. The new XML files sometimes omit `<comment>`:

```xml
<coordinationNumbers>
    <cation>1</cation>
    <anion>-1</anion>
</coordinationNumbers>
```

The `<comment>` element is already `minOccurs="0"`, so this should work. However, verify that the `<cation>` and `<anion>` elements are also flexible enough (the schema has `maxOccurs="1"` which is fine).

### Changes Required

Likely **none** - verify with validation script.

---

## Work Item 16: MQM `<zeta>` and `<coordinationNumbers>` - Optional Elements

### Problem

In some MQM endmembers, the `MQM-G` property may not include `<zeta>` or `<coordinationNumbers>` if they use default values. Verify whether the schema makes these required or optional.

Currently: Both `<zeta>` and `<coordinationNumbers>` are **required** in the `MQM-G` type (no `minOccurs="0"`).

### Changes Required

The XML files need to be fixed to always contain these fields. If any XML files omit `<zeta>` or `<coordinationNumbers>`, modify the xml files accordingly. Check all files.

**Note**: This is a change to the serializer and all existing XML files. Therefore, edit the xml files and document the changes into a file that can be handed to the XML generator code to include the changes.


---

## Work Item 17: `MQM-G` `<expr>` Element - Untyped

### Problem

The `MQM-G` type's `<expr>` element has no type:

```xml
<xs:element name="expr" />
```

This is technically valid XML Schema (defaults to `xs:anyType`), but it should be explicitly typed for clarity and validation. In all XML files, it's used as a string:

```xml
<expr>+1*{Al#LIQUID}</expr>
```

### Changes Required

- Add `type="xs:string"` to the `<expr>` element in `MQM-G`. Stronger guarantees (that it is a valid math equation) are beyond the scope of this schema.

---

## Work Item 18: CEF `<endmember>` and `<interaction>` - Missing Type on Inline Elements

### Problem

In `CEFPhaseType`, the `<interaction>` element has no type:

```xml
<xs:element name="interaction" minOccurs="0" maxOccurs="unbounded" />
```

This defaults to `xs:anyType` and will accept anything. It should be changed to `CEFInteractionType` (after Work Item 2 rework).

### Changes Required

- Set `type="CEFInteractionType"` on the `<interaction>` element within `CEFPhaseType`

---

---

# Inconsistencies and Naming Issues

This section lists naming inconsistencies, attribute order differences, and style issues found across the schema and XML files.

## I1: `specie` vs `species` (singular/plural inconsistency)

The CEF model uses:
- `<species>` (container) containing `<species>` (child elements) - confusing same-name nesting
- e.g., `<species><species name="Al" .../></species>`

The MQM model uses:
- `<species>` (container) containing `<specie>` (child elements) - correct singular/plural
- e.g., `<species><specie name="Al" .../></species>`

**Recommendation**: The CEF pattern (`<species>/<species>`) is confusing because both the container and child use the same element name. Consider renaming the CEF child elements to `<specie>` (matching MQM). Modify the existing files.

**Note**: This is a change to the serializer and all existing XML files. Therefore, edit the xml files and document the changes into a file that can be handed to the XML generator code to include the changes.


## I2: Attribute Order Inconsistencies

The XML files show varying attribute orders on elements. While XML attribute order is not semantically significant, consistent ordering improves readability:

### `<systemComponent>` attributes
- Schema order: `symbol`, `molar_mass`, `refstate`, `h298`, `s298`
- New XML files: `symbol`, `refstate`, `molar_mass`, `h298`, `s298` (refstate before molar_mass)

This will be taken care of in the XML serialization code, it should stay as the schema says.

**Note**: This is a breaking change to the serializer and all existing XML files. Therefore, edit the xml files and document the changes into a file that can be handed to the XML generator code to include the changes.


### `<endmember>` attributes
- Schema order: `name`, `charge`
- XML files: same (consistent)

### `<property>` attributes (MQM-L-PF `<expr>`)
- Some files: `i` before `j` before `k`
- Consistent across files

**Recommendation**: Attribute order is a serialization concern, not a schema concern. XSD does not enforce attribute order. If desired, the serializer should be configured to emit attributes in a canonical order.

## I3: `snake_case` vs `camelCase` Attribute Naming

The schema mixes naming conventions:
- `snake_case`: `molar_mass`, `function_of`, `assessed_systems`
- `camelCase`: `scalingFactor`, `structureFactor`, `pFactor`, `refstate`, `systemComponent`, `nonChemicalPotential`
- `PascalCase` (for types): `PhasePropertyType`, `CEFEndmemberType`

Every field name should be adapted to `camelCase`, which is most common in XML schemas. The XML serialization code will be updated accordingly.

Affected attributes:
- `molar_mass` -> `molarMass`
- `function_of` -> `functionOf`
- `assessed_systems` -> `assessedSystems` (element name)

**Note**: This is a breaking change to the serializer and all existing XML files. Therefore, edit the xml files and document the changes into a file that can be handed to the XML generator code to include the changes.

## I4: Inconsistent Documentation Placeholders

Many types in the schema have placeholder documentation from copy-paste. For example:
- `MQMEndmemberPropertyType`: documentation says "A sublattice in a phase" (incorrect, copied from SublatticeSiteType)
- `MQM-L-PF`: documentation says "A sublattice in a phase" (incorrect)
- `MQM-L-RK`: documentation says "A sublattice in a phase" (incorrect)
- `chargeValues`: documentation says "A sublattice in a phase" (incorrect)

**Improvement**: Fix all placeholder documentation. Correct documentation for these types:
- `MQMEndmemberPropertyType`: "Abstract base type for thermodynamic properties of quasichemical model endmembers."
- `MQM-L-PF`: "Pair-fraction excess energy interaction parameter for the Modified Quasichemical Model. Coefficients are indexed by i,j exponents of the constituent pair fractions."
- `MQM-L-RK`: "Redlich-Kister excess energy interaction parameter for the Modified Quasichemical Model. Coefficients are indexed by polynomial rank."
- `chargeValues`: "Formal charge values for ionic species in the quasichemical model, ranging from -8 to +8."

## I5: `L` Type Documentation

The `L` type documentation says "Magnetic interaction properties according to IHJ formalism (using RK)" but `L` is actually a general Redlich-Kister interaction parameter, not specific to magnetism. The magnetic-specific variant is `BML`.

**Correct documentation**:
- `L`: "Redlich-Kister polynomial interaction parameter for excess Gibbs energy. Each `<expr>` element represents one term of the polynomial expansion, indexed by rank (0, 1, 2, ...)."
- `BML`: "Magnetic contribution to the Redlich-Kister interaction parameter, following the Inden-Hillert-Jarl formalism. Same structure as `L` but applies to the magnetic moment or transition temperature. The expression can only be of form A+B*T"

---

# Type Hierarchy Recommendations

## H1: Property Type Hierarchy - Reparenting for Controlled Polymorphism

Current hierarchy:
```
AbstractPhasePropertyType (abstract)
├── PhasePropertyType (non-abstract, used as base for CEF properties)
│   ├── G, M, L, BML, MolarVolume, ThermalExpansion, Compressibility, BulkModulusDerivative
├── MQMEndmemberPropertyType (non-abstract, used for MQM endmember properties)
│   └── MQM-G
└── MQMInteractionPropertyType (non-abstract, used for MQM interaction properties)
    ├── MQM-L-PF, MQM-L-RK
    └── (new: MQM-L-SP, MQM-L-Reciprocal, MQM-L-Quasichemical)
```

**Issue**: MQM endmembers need to use both MQM-specific properties (like `MQM-G`) AND general physical properties (like `MolarVolume`, `ThermalExpansion`). Since `MolarVolume` extends `PhasePropertyType` and `MQM-G` extends `MQMEndmemberPropertyType`, there's no single type that covers both.

**Solution**: Reparent `MQMEndmemberPropertyType` to extend `PhasePropertyType` instead of `AbstractPhasePropertyType`. This places MQM endmember properties within the `PhasePropertyType` branch, so `PhasePropertyType` becomes the common ancestor of both general and MQM-endmember properties. Meanwhile, `MQMInteractionPropertyType` stays in its own separate branch under `AbstractPhasePropertyType`.

New hierarchy:
```
AbstractPhasePropertyType (abstract)
├── PhasePropertyType
│   ├── G, M, L, BML
│   ├── MolarVolume, ThermalExpansion, Compressibility, BulkModulusDerivative
│   └── MQMEndmemberPropertyType
│       └── MQM-G
└── MQMInteractionPropertyType
    ├── MQM-L-PF, MQM-L-RK
    └── MQM-L-SP, MQM-L-Reciprocal, MQM-L-Quasichemical
```

Schema-level element declarations (using `type` to set the base type that `xsi:type` must be a subtype of):

```xml
<!-- CEF endmembers and CEF interactions (in schema): -->
<xs:element name="property" type="PhasePropertyType" />
<!-- XML instances then use xsi:type="G", xsi:type="L", xsi:type="MolarVolume", etc. -->

<!-- MQM endmembers (in schema): -->
<xs:element name="property" type="PhasePropertyType" />
<!-- XML instances then use xsi:type="MQM-G", xsi:type="MolarVolume", etc. -->

<!-- MQM interactions (in schema): -->
<xs:element name="property" type="MQMInteractionPropertyType" />
<!-- XML instances then use xsi:type="MQM-L-PF", xsi:type="MQM-L-RK", etc. -->
```

The schema `type` attribute sets the **allowed type family**. The instance `xsi:type` attribute selects the **concrete subtype**. XSD validation ensures that the `xsi:type` value is a subtype of the declared `type`.

**What this achieves:**

| Context | Schema `type` | Allowed `xsi:type` values | Blocked `xsi:type` values |
|---|---|---|---|
| CEF endmembers | `PhasePropertyType` | `G`, `M`, `MolarVolume`, `ThermalExpansion`, `Compressibility`, `BulkModulusDerivative` | `MQM-L-PF`, `MQM-L-RK`, `MQM-L-SP`, etc. |
| CEF interactions | `PhasePropertyType` | `L`, `BML`, `G`, `M` | `MQM-L-PF`, `MQM-L-RK`, `MQM-L-SP`, etc. |
| MQM endmembers | `PhasePropertyType` | `MQM-G`, `MolarVolume`, `ThermalExpansion`, `Compressibility`, `BulkModulusDerivative`, `G`, `M` | `MQM-L-PF`, `MQM-L-RK`, `MQM-L-SP`, etc. |
| MQM interactions | `MQMInteractionPropertyType` | `MQM-L-PF`, `MQM-L-RK`, `MQM-L-SP`, `MQM-L-Reciprocal`, `MQM-L-Quasichemical` | `G`, `M`, `MolarVolume`, `MQM-G`, etc. |

**Residual leak**: Since `MQM-G` is now a subtype of `PhasePropertyType`, it is technically valid on CEF endmembers too. XSD 1.0 has no mechanism to exclude a specific subtype while allowing its siblings. This is acceptable because:
1. The serializer will never produce `MQM-G` on a CEF endmember (it's semantically nonsensical)
2. Application-level validation can enforce this rule if needed
3. The important restriction (MQM interaction types blocked from CEF) **is** enforced at the schema level

## H2: Interaction Type Unification

Currently, CEF and MQM interactions are defined completely independently:

- **CEF**: `CEFInteractionType` is a named complex type with a `constituents` **attribute** (string) and `<property>` children (schema base type: `PhasePropertyType`, instances use `xsi:type` for concrete subtypes). It does not extend any abstract base.
- **MQM**: The MQM interaction is an **anonymous inline type** inside `ModifiedQuasichemicalPhaseType`, with `<ref>`, `<comment>`, `<constituents>` (child element), and `<property>` children (schema base type: `MQMInteractionPropertyType`, instances use `xsi:type`).

However, in the new XML files, both CEF and MQM interactions use the **exact same structural pattern**:

```xml
<interaction name="...">
    <constituents>
        <site><const species="..."/>...</site>
    </constituents>
    <description/>  <!-- or <ref/> -->
    <property xsi:type="...">...</property>
</interaction>
```

**Recommendation**: Create an abstract `AbstractInteractionType` that captures the shared structure, then derive CEF and MQM interaction types from it:

```
AbstractInteractionType (abstract)
├── attribute: name (xs:string, optional)
├── element: constituents (ConstituentArrayType)
├── element: description (xs:string, optional)
├── element: ref (xs:string, optional)
├── element: comment (xs:string, optional)
│
├── CEFInteractionType extends AbstractInteractionType
│   └── element: property (schema type="PhasePropertyType", unbounded)
│       instances use xsi:type="L", xsi:type="BML", xsi:type="G", xsi:type="M", etc.
│
└── MQMInteractionType extends AbstractInteractionType
    └── element: property (schema type="MQMInteractionPropertyType", unbounded)
        instances use xsi:type="MQM-L-PF", xsi:type="MQM-L-RK", etc.
```

**What this achieves:**
1. Shared structure is defined once (DRY principle)
2. The property type restriction is enforced per model via the schema-level `type`: CEF interactions declare `type="PhasePropertyType"` so only `PhasePropertyType` subtypes are valid `xsi:type` values (`L`, `BML`, `G`, `M`); MQM interactions declare `type="MQMInteractionPropertyType"` so only `MQMInteractionPropertyType` subtypes are valid (`MQM-L-PF`, `MQM-L-RK`, `MQM-L-SP`, etc.)
3. The MQM interaction is promoted from anonymous inline to a proper named type (`MQMInteractionType`), matching the CEF pattern
4. Both use `xsi:type` dispatch for property polymorphism within their respective branches

**Note on XSD limitation**: In XSD 1.0, a derived type can only ADD elements after the base type's sequence - it cannot insert elements in the middle. Since `<property>` elements must come after the shared elements (constituents, description, ref, comment), this works naturally. The base type defines the metadata elements, and each derived type appends its own `<property>` element with the appropriate type restriction.

## H3: Constituent Array Type Unification

Currently there are three separate constituent array types:
- `CEFConstituentArrayType` - uses `<const species="..."/>` (attribute)
- `MQMConstituentArrayType` - uses `<const>text</const>` (text content)
- `MQMInteractionConstituentArrayType` - uses `<const>text</const>` + optional `site` attribute

The new XML files use the `species` attribute pattern uniformly across both CEF and MQM. Consider unifying into a shared base type.

**Recommendation**: Create a single `ConstituentArrayType` with `<const species="..." site="..."/>` where `site` is optional (used only in ternary interpolation contexts). Use this as the base for both CEF and MQM constituent arrays. This also feeds naturally into H2 (interaction type unification), since the shared `AbstractInteractionType` can reference this unified type.

---

# Implementation Order

Suggested order for implementing the work items:

1. **WI-0**: Create validation script (enables iterative testing)
2. **WI-8**: Metadata relaxation (quick fix, unblocks many files)
3. **WI-14**: `chargeValues` expansion (quick fix)
4. **WI-17**: Fix untyped `<expr>` in MQM-G (quick fix)
5. **WI-18**: Type the CEF `<interaction>` element (quick fix)
6. **WI-1**: CEF endmembers/interactions wrappers (structural change)
7. **WI-2**: CEF interaction type rework (structural change)
8. **WI-6**: CEFOrderedPhaseType `disorderedPhase` attribute
9. **WI-5**: MQM interaction constituents - species attribute
10. **WI-9**: MQM endmember constituents - species attribute
11. **WI-10**: MQM endmember comment + optional fields
12. **WI-4**: MQM phase structure additions (numberOfDatComponents, interaction name)
13. **WI-3**: New MQM interaction property types
14. **WI-11**: MQM endmember properties - physical property types
15. **WI-12, WI-13**: Verify xsi:type dispatch works for CEF
16. **WI-15, WI-16**: Verify MQM optional elements
17. **Inconsistencies I1-I5**: Address naming/documentation issues
18. **H1, H2**: Type hierarchy consolidation

After each step, run the validation script to verify progress and catch regressions.
