# ThermML XML Serializer Migration Guide

This document describes all changes required in the XML serializer to produce output that validates against the updated ThermML XSD schema.

---

## 1. Wrapper Elements for CEF Phases

Endmembers and interactions must be wrapped in container elements.

**Before:**
```xml
<phase xsi:type="CEFPhaseType" name="FCC" state="solid">
    <endmember name="Al:Va">...</endmember>
    <endmember name="Cr:Va">...</endmember>
    <interaction name="Al,Cr:Va">...</interaction>
</phase>
```

**After:**
```xml
<phase xsi:type="CEFPhaseType" name="FCC" state="solid">
    <endmembers>
        <endmember name="Al:Va">...</endmember>
        <endmember name="Cr:Va">...</endmember>
    </endmembers>
    <interactions>
        <interaction name="Al,Cr:Va">...</interaction>
    </interactions>
</phase>
```

---

## 2. CEF Phase Element Order

The CEF phase must follow this strict sequence. All elements except `species` and `endmembers` are optional.

```xml
<phase xsi:type="CEFPhaseType" name="..." state="...">
    <description>...</description>
    <species>...</species>
    <structure>...</structure>
    <assessedSystems>...</assessedSystems>
    <ordering>...</ordering>
    <endmembers>...</endmembers>
    <interactions>...</interactions>
</phase>
```

---

## 3. MQM Phase Element Order

The MQM phase must follow this strict sequence. Only `species` and `endmembers` are required. Note that `quadruplets` comes **before** `interactions`.

```xml
<phase xsi:type="ModifiedQuasichemicalPhaseType" name="..." state="...">
    <numberOfDatComponents>7</numberOfDatComponents>
    <description>...</description>
    <species>...</species>
    <endmembers>...</endmembers>
    <quadruplets>...</quadruplets>
    <interactions>...</interactions>
    <ternaryInterpolations>...</ternaryInterpolations>
</phase>
```

---

## 4. Attribute Renames

| Old Name | New Name | Element | Notes |
|---|---|---|---|
| `molar_mass` | `molarMass` | `<systemComponent>` | camelCase convention |
| `assessed_systems` | `assessedSystems` | CEF phase child | camelCase convention |

---

## 5. Species Child Element Rename

Inside `<species>` containers, each child element is now `<specie>` (singular).

**Before:**
```xml
<species>
    <species name="Al" composition="Al1" />
    <species name="Va" composition="Va" />
</species>
```

**After:**
```xml
<species>
    <specie name="Al" composition="Al1" />
    <specie name="Va" composition="Va" />
</species>
```

---

## 6. Constituent Arrays (Endmembers and Interactions)

All constituent arrays for endmembers and interactions use the `<const species="..."/>` attribute-only format. Text content is not allowed.

**Before (if using text content):**
```xml
<constituents>
    <site>
        <const>Al</const>
        <const>Cr</const>
    </site>
    <site>
        <const>Va</const>
    </site>
</constituents>
```

**After:**
```xml
<constituents>
    <site>
        <const species="Al"/>
        <const species="Cr"/>
    </site>
    <site>
        <const species="Va"/>
    </site>
</constituents>
```

---

## 7. Ternary Interpolation Constituents

Ternary interpolation constituents now also use the attribute-based format. The species is specified via the `species` attribute, and the ternary site locator via `site` or `siteIndex`.

**Before:**
```xml
<ternaryInterpolations>
    <interpolation>
        <constituents>
            <site>
                <const siteIndex="i">
                    Na[+]
                </const>
                <const siteIndex="j">
                    K[+]
                </const>
                <const siteIndex="k">
                    Mg[2+]
                </const>
            </site>
            <site>
                <const>Cl[-]</const>
            </site>
        </constituents>
        <ij xsi:type="Kohler"/>
        <jk xsi:type="Muggiano"/>
        <ik xsi:type="Toop"><constant>i</constant></ik>
    </interpolation>
</ternaryInterpolations>
```

**After:**
```xml
<ternaryInterpolations>
    <interpolation>
        <constituents>
            <site>
                <const species="Na[+]" site="i"/>
                <const species="K[+]" site="j"/>
                <const species="Mg[2+]" site="k"/>
            </site>
            <site>
                <const species="Cl[-]"/>
            </site>
        </constituents>
        <ij xsi:type="Kohler"/>
        <jk xsi:type="Muggiano"/>
        <ik xsi:type="Toop"><constant>i</constant></ik>
    </interpolation>
</ternaryInterpolations>
```

Both `site` and `siteIndex` are accepted by the schema, but prefer `site` for new output.

---

## 8. MQM Quadruplets

Three changes to quadruplet serialization:

| Change | Old | New |
|---|---|---|
| Child element name | `<quad>` | `<quadruplet>` |
| Site element names | `<A>`, `<B>`, `<X>`, `<Y>` | `<a>`, `<b>`, `<x>`, `<y>` |
| Coordination attribute | `value` | `Z` |

**Before:**
```xml
<quadruplets>
    <quad name="Na[+]:Cl[-]">
        <A species="Na[+]" value="6"/>
        <B species="Na[+]" value="6"/>
        <X species="Cl[-]" value="6"/>
        <Y species="Cl[-]" value="6"/>
    </quad>
</quadruplets>
```

**After:**
```xml
<quadruplets>
    <quadruplet name="Na[+]:Cl[-]">
        <a species="Na[+]" Z="6"/>
        <b species="Na[+]" Z="6"/>
        <x species="Cl[-]" Z="6"/>
        <y species="Cl[-]" Z="6"/>
    </quadruplet>
</quadruplets>
```

---

## 9. MQM Interaction Property Types

MQM interaction properties use `xsi:type` to select the concrete model. Available types:

| xsi:type | Expr Attributes | Description |
|---|---|---|
| `MQM-L-PF` | `i`, `j`, optional `k` | Pair-fraction polynomial |
| `MQM-L-RK` | `rank` | Redlich-Kister polynomial |
| `MQM-L-SP` | `i`, `j` | Simple polynomial |
| `MQM-L-Reciprocal` | `i`, `j`, `k` | Reciprocal interaction |
| `MQM-L-Quasichemical` | `i`, `j` | Quasichemical equilibrium |

Example:
```xml
<interaction name="Na[+],K[+]:Cl[-]">
    <constituents>
        <site>
            <const species="Na[+]"/>
            <const species="K[+]"/>
        </site>
        <site>
            <const species="Cl[-]"/>
        </site>
    </constituents>
    <property xsi:type="MQM-L-PF">
        <expr i="0" j="0">-1234.5 + 0.5*T</expr>
        <expr i="1" j="0">-567.8</expr>
    </property>
</interaction>
```

---

## 10. MQM Endmember Properties

MQM endmember properties use `xsi:type` on the `<property>` element. The base type is `PhasePropertyType`, which also allows general physical properties.

```xml
<endmember name="NaCl">
    <constituents>
        <site><const species="Na[+]"/></site>
        <site><const species="Cl[-]"/></site>
    </constituents>
    <property xsi:type="MQM-G">
        <ref>source</ref>
        <comment/>
        <expr>NaCl#Liquid</expr>
        <zeta>2.4</zeta>
        <coordinationNumbers>
            <cation>6.0</cation>
            <anion>6.0</anion>
        </coordinationNumbers>
    </property>
</endmember>
```

---

## 11. CEF Interaction Structure

CEF interactions now extend `AbstractInteractionType` with structured constituents and typed property elements.

```xml
<interaction name="Al,Cr:Va">
    <constituents>
        <site>
            <const species="Al"/>
            <const species="Cr"/>
        </site>
        <site>
            <const species="Va"/>
        </site>
    </constituents>
    <ref>99Ans</ref>
    <comment/>
    <property xsi:type="L">
        <ref/>
        <expr rank="0">-10000 + 5*T</expr>
    </property>
</interaction>
```

---

## 12. Ordered Phases

`CEFOrderedPhaseType` now requires a `disorderedPhase` attribute naming the associated disordered phase.

```xml
<phase xsi:type="CEFOrderedPhaseType" name="B2_BCC" state="solid" disorderedPhase="BCC_A2">
    ...
</phase>
```

---

## Quick Reference Checklist

- [ ] Wrap CEF endmembers in `<endmembers>` container
- [ ] Wrap CEF interactions in `<interactions>` container
- [ ] Rename `molar_mass` to `molarMass`
- [ ] Rename `assessed_systems` to `assessedSystems`
- [ ] Rename species children from `<species>` to `<specie>`
- [ ] Use `<const species="..."/>` for all constituent arrays (no text content)
- [ ] Use `<const species="..." site="i"/>` for ternary interpolation constituents
- [ ] MQM element order: endmembers, quadruplets, interactions, ternaryInterpolations
- [ ] Rename `<quad>` to `<quadruplet>`, lowercase site elements, `value` to `Z`
- [ ] Add `disorderedPhase` attribute on ordered phases
- [ ] Use `xsi:type` dispatch for MQM interaction properties
