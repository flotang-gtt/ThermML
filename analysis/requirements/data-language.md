# Data Language Requirements

This document identifies and elaborates the requirements that the data language in which ThermML is implemented must satisfy.

## Draft Requirements

This section lists requirements without elaboration, to make it easy and quick to capture thoughts and ideas.

There are none for the moment.

## Machine Usable

**Requirement type**: Non-functional

The data language must allow data files files to be readable and writable by computers through software.

### Rationale

The content of ThermML files needs to be read and written by CALPHAD software tools.

### Performance

ThermML files need to be readable with existing generally-available libraries in the following programming languages:

- Fortran
- C
- C++
- Java
- Python
- Rust

### Verification

Compliance with this requirement must be verified by implementing testing routines in the listed languages, which read all of the content of ThermML files, and printing this content to the terminal in a neat format that is human readable.

### Notes and Discussion

None.

## Human Usable

**Requirement type**: Non-functional

The data language must allow data files files to be readable and writable by human users.

### Rationale

Members of the CALPHAD community must be able to read, create, and edit ThermML data files, to allow them to learn, communicate with each other, identify problems, build databases, and implement new software tools with as little friction and misunderstanding as possible.
A clear data file format can accelerate learning of new members, thereby growing and strengthening the CALPHAD community.

### Performance

TODO: complete

Data structures and data fields must be explicitly and clearly named in the data file.
explicit is better than implicit
a human must be able to read data files as largely self-contained documents.
it should not be needed, for the most part, to read another document to be able to underestand a data file.

### Verification

TODO: complete

### Notes and Discussion

TODO: Incorporate Brandon's initial requirement: Should still be relatively pleasant to edit manually and format in a way that is convenient enough to make small edits and modifications by hand.

## Validatable

**Requirement type**: Non-functional

The data language must allow simple, automated validation of data files with libraries and tools that are readily accessible to CALPHAD community members.

### Rationale

TODO: complete

### Performance

TODO: complete

### Notes and Discussion

None.
