# Changelog

All notable changes to the ThermML schema will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1] - 2026-02-24

### Added
- Ordered phase schema with required `disorderedPhase` attribute
- `AbstractInteractionType` as shared base for CEF and MQM interactions
- Unified `ConstituentArrayType` for attribute-based constituent specification
- MQM interaction property types: `MQM-L-SP`, `MQM-L-Reciprocal`, `MQM-L-Quasichemical`
- `<endmembers>` and `<interactions>` wrapper elements for CEF phases
- `<numberOfDatComponents>` element for MQM serialization metadata
- Optional `<comment>` on MQM endmembers
- Optional `k` attribute on `MQM-L-PF` for ternary pair-fraction interactions

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
