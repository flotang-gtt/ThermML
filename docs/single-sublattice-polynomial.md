# Single-sublattice polynomial integration: 0.2.0 development

This branch adds `SingleSublatticePolynomialPhaseType` for the ChemSage QKTO/QKTOM
representation. The phase derives from `PhaseType` and reuses CEF species,
endmember, interaction and magnetic structures. It uses explicit `PolynomialL`
composition powers rather than ordinary CEF `L` ranks.

These changes target **ThermML 0.2.0, unreleased and not signed off**. Representation
validity is the schema's responsibility. Equations, normalization conventions,
model evaluation and a consumer's supported expression basis are outside this
schema review; their documentation is not a prerequisite for this integration.

## Decisions

| Topic | Schema decision |
| --- | --- |
| Chemical groups | Require `xs:positiveInteger`, as for SUBQ: 1, 2, 3, ...; zero, negative and fractional values fail XSD. Do not derive this domain from ChemSage's signed storage type. No implementation-specific 32-bit limit is imposed. |
| Model identity | Retain one descriptive phase type; `structure/magnetic` selects QKTOM even when all magnetic parameters are zero or omitted. |
| Powers | Keep explicit unsigned 32-bit i, j, k, l powers in listed constituent order. Zero powers are valid. Require exactly i/j for two constituents, i/j/k for three, and i/j/k/l for four. These are not RK ranks or temperature-range selectors. |
| Term identity | Ordered constituent/power tuples must be unique throughout a phase, even across properties or differently named interactions. Reversed constituent lists remain distinct. Coefficient text and names do not distinguish parameters. |
| Coordination number Z | Require finite positive doubles, including fractional values. Z is distinct from sublattice multiplicity and preprocessing scaling. |
| Species/endmembers | List every declared species exactly once on the sole sublattice, with one endmember per species and matching literal names. Require nonempty compositions. Existing XSD keys enforce species-name uniqueness and reference validity. |
| Preprocessing | Preserve literal names, fractional compositions and Gibbs functions; do not add a second scaling field. |
| Properties | Polynomial interactions accept only PolynomialL, TCL and BML. PolynomialL cannot appear on endmembers or other phase families. Endmembers reuse G, M and the existing physical-property types. |
| Empty records | An omitted or empty interactions container is valid; a declared interaction must have a property. A PolynomialL property must have at least one nonempty expr; explicit zero is valid. |
| Magnetism | M, TCL and BML require a magnetic structure. Keep magnetic RK ranks separate from composition powers. A structure with no magnetic properties does not receive the CEF warning. |
| Ternary methods | Both models use the same Kohler, Toop and Muggianu types and the same ij/jk/ik XML sequence. |
| Ternary context | Retain one mixing site for polynomial phases; SUBQ additionally requires a fixed constituent on the other site. This is a representation difference, not a different interpolation method. |
| Locator | `site` is the sole authoritative attribute for the i/j/k role. `siteIndex` is rejected, even when both attributes have identical values. Require each mixing role exactly once; the fixed SUBQ constituent has no role. |
| Toop | constant selects any labeled member of the ternary, including the third species outside the named pair. |
| Muggianu | Correct the type name to `Muggianu` in the XSD and every active example/fixture. The old misspelling is not an alias. This deliberately breaks old XML and consumer code during 0.2.0 development. |

## Why the ternary constituent containers differ

The original DAT records share this layout (DAT pair order is ij, ik, jk):

```text
i  j  k  method(ij) i j  method(ik) i k  method(jk) j k  fixed
```

Two concrete records in ChemSage's
`udo/test-data/FTOxid_20271231_Schott.dat` demonstrate the distinction:

```text
SUBQ, Slag-liq, line 4294:
1 2 3 K 1 2 T1 1 3 T2 2 3 27

QKTOM, Monoxide, line 9697:
1 2 4 T1 1 2 K 1 4 T4 2 4 0
```

The corresponding generated XML identifies the species:

| Record | i, j, k species | Final DAT field | ThermML sites |
| --- | --- | --- | --- |
| Slag-liq, SUBQ | Na, K, Al | 27 = O, a real fixed constituent | `[Na,K,Al] [O]` |
| Monoxide, QKTOM | FeO, (Fe2O3):2, MgO | 0 = no other-sublattice constituent | `[FeO,(Fe2O3):2,MgO]` |

Thus the methods and role locators are identical, but omitting SUBQ's fixed O
would lose part of the record. Adding a dummy zero species to the one-lattice
model would introduce a species that does not exist. `InterpolationType` keeps
the two-site SUBQ context, and `PolynomialInterpolationType` keeps the one-site
context; both reuse `TernaryInterpolationConstituentType`,
`TernaryInterpolationMethodsGroup` and `InterpolationMethodType`.

This is also explicit in ChemSage's parsers: `udo/src/phase/subq.rs` resolves the
last field as a real species and stores it in `TernaryExtrapolation.t`;
`udo/src/phase/qkto.rs` requires that final field to be zero. The DAT records and
their corresponding XML representations were inspected directly, without copying
external fixtures or changing ChemSage files.

## Canonical locator and migration

`site` is preferred because the ChemSage writer already emits it and the existing
examples use it. It is a symbolic role, i/j/k, so `siteIndex` misleadingly suggests
a numerical sublattice index. The trade-off is that `site` sits inside a `<site>`
element with a different purpose. The documentation now distinguishes the outer
sublattice container from the inner species role explicitly.

Keeping both spellings would preserve two ways to express the same fact and
require a conflict policy. For 0.2.0 there is exactly one representation:

```xml
<const species="Na" site="i"/>
```

Migration is explicit:

- Rename old `siteIndex` attributes to `site`. If both exist and agree, retain
  only `site`; if they disagree, resolve the data conflict instead of guessing.
- Rename `xsi:type="Muggiano"` to `xsi:type="Muggianu"`. There is no compatibility alias.
- Correct nonpositive group IDs at the source; do not silently take absolute
  values or renumber groups, which could change group relationships.
- Update ChemSage's XML type names and positive-group validation when importing
  this schema. The schema's acceptance domain is authoritative for ThermML.

Expression strings remain expression strings: the schema does not adopt the
current DAT reader's six-basis restriction or its restrictions on function
references. Those belong to consumers. A schema-valid document need not be
executable by every consumer.

## Validation and separate findings

The [complete synthetic example](../examples/single-sublattice-polynomial.xml)
and [regression tests](../tests/test_polynomial_phase.py) cover explicit zero
powers, positive groups, fractional Z, magnetic variants, one/two-site topology,
property ownership, duplicate identities, strict locator spelling and corrected
Muggianu spelling. Tests also exercise symbolic coefficient expressions without
imposing consumer evaluation restrictions.

The original nonmagnetic ChemSage example passes unchanged (two polynomial
phases, groups 1-2). Its magnetic example correctly fails XSD on one obsolete
method name; explicitly renaming that type in memory makes the complete example
pass XSD and Schematron (one polynomial phase, groups 1-3). All 39 polynomial
phases from the original Schott XML pass both validators unchanged; their groups
are all 1 or 2. No group remapping or source-file edits were needed.

No blanket duplicate-species or duplicate-endmember exception is needed for the
polynomial model. The complete Schott export has separate duplicate-stoichiometry
findings in other phase families, including Spinel. The working tree's existing
MQM charge-domain extension to +/-20 is retained, so the formerly rejected charges
12 and 16 are no longer an issue. This integration does not alter that change.

New polynomial/interpolation modules and the polynomial example target 0.2.0.
The changelog remains unreleased; no release tag, publication or sign-off is made.
The remaining schema version markers can be synchronized during 0.2.0 release
preparation. The database version attribute currently checks SemVer syntax rather
than enforcing model availability by version.
