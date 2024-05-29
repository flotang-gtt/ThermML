# ThermML

## Objective

`ThermML` is an xml schema definition structure that should be able to describe
thermodynamic databases across multiple software tools, with the intention of
providing a mechanism to validate structure and data of thermodynamic databases.

The schema is meant to be extendable, e.g. by providing adequate hooks for
additional schemata as well as providing a reasonable platform of common type
definitions that the extensions should adhere to.

The project uses XML Schema Definition as the validation schema. This repository
is supposed to be implementation agnostic, as the XML validation tools for all
major languages are mature and robust enough.

## Project structure

The `examples` directory contains examples of files that validate or qualify to
be validated against the schema. A proper testing pipeline needs to be
implemented at a later point in time.

The `schema` directory contains the schema definition files.

The `requirements` directory contains the requirements used as basis for driving 
and directing development.

## How to contribute

As of the drafting stage of this project, every contribution is welcome. Pull
requests may add examples or requirements. Most current implementations can be
seen as discussable items. The issues section is good place to start discussions.




