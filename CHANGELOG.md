# Changelog

All notable changes to the ThermML schema will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Canonical ChemSage SUBQ interaction support for `MQM-L-RC`, ternary
  `MQM-L-SP` and `MQM-L-Quasichemical`, and the reader alias `MQM-L-Q`
- Dedicated expression types for I/J/K, Redlich-Kister, reciprocal mean,
  reciprocal side, and reciprocal corner parameter shapes
- Schematron checks for selected ternary terms, reciprocal two-by-two
  constituent cardinality, and ternary interpolation labels
- Compact `subq-interaction-models.xml` interoperability example covering all
  seven canonical emitted interaction families

### Changed

- SUBQ expression indices are restricted to unsigned 16-bit values
- `MQM-L-RS` and `MQM-L-RC` require family-specific reciprocal variants
- `numberOfDatComponents` is non-negative, quadruplets use canonical child
  order, and ternary interpolations contain exactly two sites

## [0.1.0] - 2026-06-21

First version to be expressed with Semantic Versioning. The schema major
version is now encoded in the namespace (`v0`) and the full version is carried
on each database via the new `version` attribute.

### Added
- `SemanticVersionType` simple type validating Semantic Versioning 2.0.0 strings
- Required `version` attribute on the `<database>` element holding the targeted
  schema version, starting at `0.1.0` (distinct from the content-oriented
  `<metadata><version>` element)

### Changed
- Bumped namespace from `http://calphad.org/thermml/0.1` to
  `http://calphad.org/thermml/v0`; only the major version is encoded in the
  namespace, so minor and patch iterations no longer require a namespace change
- Aligned every `xs:schema/@version` to the semver form `0.1.0`

## [0.1] - 2026-06-01

### Added
- Ordered phase schema with required `disorderedPhase` attribute
- `AbstractInteractionType` as shared base for CEF and MQM interactions
- Unified `ConstituentArrayType` for attribute-based constituent specification
- MQM interaction property types: `MQM-L-SP`, `MQM-L-Reciprocal`, `MQM-L-Quasichemical`
- `<endmembers>` and `<interactions>` wrapper elements for CEF phases
- `<numberOfDatComponents>` element for MQM serialization metadata
- Optional `<comment>` on MQM endmembers
- Optional `k` attribute on `MQM-L-PF` for ternary pair-fraction interactions
- Optional `<version>` element on revisions
- `MagneticFactorValueType` allowing CEF magnetic factors to be a numeric literal or expression string
- XSD identity constraints enforcing references for system components, global functions, ordered phases, and MQM species/quadruplets
- Schematron rule layer (`schematron/`) for semantic checks beyond XSD grammar: Redlich-Kister rank, CEF endmember Cartesian count, ternary interpolation locator aliases, and empty-or-zero global expression content
- Per-rule fixtures (valid/invalid/warning) and a runtime Schematron catalog generated from per-rule JSON, with a CI check enforcing catalog freshness
- HTML rule catalogs (XSD and Schematron) published under `docs/validation/`
- `validate_one.py` CLI running XSD plus bundled Schematron validation with combined error/warning reporting

### Changed
- Bumped namespace from `http://calphad.org/thermml/0.0` to `http://calphad.org/thermml/0.1`
- Reworked CEF phase structure to strict sequence with wrapper elements
- Reworked MQM phase structure to strict sequence with new element ordering
- MQM quadruplet child element renamed from `<quad>` to `<quadruplet>`
- MQM quadruplet site elements changed from uppercase (`<A>`, `<B>`, `<X>`, `<Y>`) to lowercase
- MQM quadruplet site attribute renamed from `value` to `Z`
- Ternary interpolation constituents converted to attribute-based format
- `FunctionIDType` pattern relaxed to accept any non-whitespace string
- `chargeValues` changed from enumeration to pattern (`0|[+-]?[1-8]`)
- Renamed `molar_mass` to `molarMass`
- Renamed `assessed_systems` to `assessedSystems`
- Renamed child `<species>` to `<specie>` inside species containers
- `MQMEndmemberPropertyType` now extends `PhasePropertyType`
- Renamed CEF magnetic factor fields: `structureFactor` to `AFMFactor`, `pFactor` to `structureFactorP`
- Tightened phase/species identifiers, sublattice multiplicities, component refstates, expression selector types, MQM species groups, and metadata `<created>` dates
- Relaxed refstate and MQM group constraints, and allowed zero-width expression ranges and braced expression references

### Fixed
- Metadata constraints relaxed to allow empty `<authors>`, `<revisions>`, `<references>`
- `<created>` type changed to `xs:string` to allow empty values
- `ConstituentSpeciesType` pattern updated to allow surrounding whitespace
- Corrected documentation for `L` and `BML` property types

## [0.0] - 2024-01-01

Initial release of the ThermML XML schema.

### Added
- Core schema structure with database, metadata, system components, expressions, phases, and potentials
- CEF (Compound Energy Formalism) phase model
- MQM (Modified Quasichemical Model) phase model
- Pure substance phase definitions
- Expression framework with temperature-dependent functions
- Simple type definitions for species, constituents, and matter states
- Example XML files for basic, CEF, and quasichemical databases
