# Data Schema Requirements

This document identifies and elaborates the requirements that the ThermML data schema in which ThermML is implemented must satisfy.

## Draft Requirements

This section lists requirements without elaboration, to make it easy and quick to capture thoughts and ideas.

### Working with Data Files

1. Ease of Data File Comparison
1. Ease of Data File Combination

### Non-chemical Potentials

The schema must explicitly make provision for an unlimited number or non-chemical potentials.
Examples include:

1. Temperature T: This is the most obvious one.
1. Pressure p: See Alexander Navrotsky's talk at CALPHAD 2024.
1. Stress ϵ
1. Gravity φ
1. Surface energy γ
1. Electric potential Φ
1. Electric field strength E
1. Magnetic field strength B: See Rainer's talk at CALPHAD 2024.

TODO: I call these "non-chemical potentials", and this may not be the most appropriate terminology. Please help to make sure that we use meaningful terminology for this.

## Capture Metadata

**Requirement type**: Functional

The schema must be able to capture metadata like:

1. version history;
1. clear references to source documents such as literature, other databases, etc.;
1. background and descriptions; and
1. author notes.

## Capture System Component Reference State Data

**Requirement type**: Functional

The schema must capture system component reference state data explicitly.

### Notes and Discussion

TODO: Incorporate Brandon's initial requirement: Chemical element reference states need first-class support. This also supports database merging by helping to surface reference state incompatibilities.

## Extensible

**Requirement type**: Non-functional

The schema must be extensible, and allow introduction of, for example, new phase models.

### Notes and Discussion

TODO: Incorporate Brandon's initial requirement: Should have clear hooks for extensibility, e.g. new types of parameters or models
