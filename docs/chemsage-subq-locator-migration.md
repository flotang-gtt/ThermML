# ChemSage emitter/consumer handoff: ThermML 0.2.0

**Unreleased; not signed off.** Applies to SUBQ and polynomial integration.

- **Locator:** emit only `site="i|j|k"` (already canonical in the writer).
  Remove the `@siteIndex` alias in `udo/src/models/xml.rs` and explicitly reject
  it, including agreeing dual attributes; silently ignoring it is insufficient.
- **Method name:** change `Muggiano` to `Muggianu` in XML serialization,
  deserialization, matching enums and fixtures. No old-name alias.
- **Groups:** require polynomial `group > 0` on intake, mutation and emission.
  The schema uses positive integers without a 32-bit cap; report consumer range
  limits explicitly instead of wrapping or renumbering values.
- **SUBQ reader fix:** `TernaryExtrapolation::from_xml` in `udo/src/phase/subq.rs`
  currently uses positions. Resolve i/j/k from `site` and locate the unlabeled
  fixed site by structure. Valid XML may reorder constituents/sites. Reject
  unknown species instead of the current fallback to species index zero.
- **Preserve representation:** retain SUBQ's fixed constituent; polynomial
  interpolation has none. Toop may select the third ternary species. XML pair
  order is ij/jk/ik; DAT order is ij/ik/jk.
- **Polynomial validation:** reject property-free interaction records and empty
  coefficient text. Preserve explicit zero powers and magnetic structure even
  with zero parameters. Existing arity, identity and property restrictions remain.
- **Bundle:** import the complete XSD/Schematron tree, including the new shared
  interpolation XSD and renamed `ternary-interpolation-semantics` rule directory.
  Keep 0.2.0 version handling coordinated. The branch also permits MQM charges
  through magnitude 20.

Migrate old locator/method spellings explicitly; resolve conflicting locators
and nonpositive groups at the source. Test spelling rejection, reordered SUBQ
roles, group bounds, empty records and zero-value roundtrips. Consumer expression
limitations remain separate from schema validity.

See [the full representation review](single-sublattice-polynomial.md) for details.
