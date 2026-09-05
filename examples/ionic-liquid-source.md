# Source of the ionic-liquid example

`ionic-liquid.xml` is an independent transcription of the first `IONIC_LIQ` /
`SUBI` phase in the user-supplied FactSage export:

```text
C:\FactSage84\ChemSage\AlFeO_Lindwall.dat
SHA-256: 796fecca05798a3c1999924e9e91e069ba978a3a7896c7d530a30e848f577887
```

The source block occupies lines 229–387. The second block, lines 388–546, is
identical, including its phase name. The example includes one copy of this
ionic model, not the gas, solids, or the entire Fe–Al–O database. Neither the
TDB nor the ChemSage repository or its emitted XML was used.

## Constituents and endmembers

The header defines Fe, Al and O with molar masses 55.84500000, 26.98153860 and
15.99940000. Its eight additional electron bookkeeping components have zero
coefficients throughout this ionic block and are omitted from this example.
Va is a site constituent, not a chemical system component.

Lines 330–338 give two cations, four second-site constituents, their role
values, and two explicit arrays mapping the eight endmembers to their sites:

```text
Cations:              Al[+3]  Fe[+2]
Second site:          O[-2]   Va   AlO1.5   FeO1.5
Cation values:        3      2
Second-site values:   2      1    0        0
First-site indices:   1 2 1 1 2 2 1 2
Second-site indices:  2 2 1 3 3 1 4 4
```

Names and endmember ordering are preserved. The source stoichiometry below
is copied from each record; it must not be reconstructed by simply adding
the two referenced species compositions.

| Endmember | Site 1 | Site 2 | Source Fe, Al, O coefficients | Gibbs ranges | DAT lines |
| --- | --- | --- | --- | --- | --- |
| Al+3Va | Al[+3] | Va | 0, 1, 0 | 5 | 231–248 |
| Fe+2Va | Fe[+2] | Va | 1, 0, 0 | 2 | 249–257 |
| Al+3O-2 | Al[+3] | O[-2] | 0, 2, 3 | 5 | 258–275 |
| Al+3AlO1.5 | Al[+3] | AlO1.5 | 0, 3, 4.5 | 5 | 276–293 |
| Fe+2AlO1.5 | Fe[+2] | AlO1.5 | 0, 2, 3 | 5 | 294–311 |
| Fe+2O-2 | Fe[+2] | O[-2] | 2, 0, 2 | 1 | 312–317 |
| Al+3FeO1.5 | Al[+3] | FeO1.5 | 3, 0, 4.5 | 1 | 318–323 |
| Fe+2FeO1.5 | Fe[+2] | FeO1.5 | 2, 0, 3 | 1 | 324–329 |

## Gibbs functions

All eight functions use the existing `FunctionTypeCSdat` representation.
Each `<chemsage>` contains the original `4 <range-count>` function header
and verbatim thermodynamic rows. The source stoichiometry vector is removed
from that header and retained in the endmember comment and the table above.

This preserves all 25 temperature ranges, their upper limits, coefficients,
and additional coefficient/power pairs, including the small final interval
ending at 6000.00001 K in Al+3Va. No first-range lower boundary is invented.
Endmember Gibbs properties refer to these functions by their braced names.
No energy normalization, coefficient fitting, or phase-energy rescaling is
performed.

## Interactions

The interaction tuples in lines 339–386 are decoded against the flattened
constituent order `Al[+3], Fe[+2], O[-2], Va, AlO1.5, FeO1.5`. The tuple's final
integer gives the number of coefficient sets. These are retained in order
as ranks 0, 1, ... of an `L` property. Both sublattice ordering and constituent
ordering within each site are preserved.

Every coefficient set in this block has only a constant and an optional
linear-temperature term; its remaining four temperature coefficients are
zero. The resulting expressions are:

| DAT indices | Constituent array | Expressions in rank order | DAT lines |
| --- | --- | --- | --- |
| 1,2,3,4 | Al[+3],Fe[+2] : O[-2],Va | -740767.460 | 339–342 |
| 1,2,4 | Al[+3],Fe[+2] : Va | -91976.5000 + 22.1314000*T; -5672.58000 + 4.87280000*T; 121.900000 | 343–350 |
| 1,3,4 | Al[+3] : O[-2],Va | -829000.000 + 106.000000*T | 351–354 |
| 1,4,5 | Al[+3] : Va,AlO1.5 | 110000.000 + 46.0000000*T | 355–358 |
| 1,4,6 | Al[+3] : Va,FeO1.5 | 110000.000 | 359–362 |
| 2,3,4 | Fe[+2] : O[-2],Va | 176681.000 - 16.3680000*T; -65655.0000 + 30.8690000*T | 363–368 |
| 2,3,5 | Fe[+2] : O[-2],AlO1.5 | -40000.0000 + 25.0000000*T | 369–372 |
| 2,3,6 | Fe[+2] : O[-2],FeO1.5 | -26362.0000; 13353.0000 | 373–378 |
| 2,4,5 | Fe[+2] : Va,AlO1.5 | 178992.380 | 379–382 |
| 2,4,6 | Fe[+2] : Va,FeO1.5 | 110000.000 | 383–386 |

For format background, ChemApp identifies `SUBI` as the two-sublattice ionic
formalism in its [model documentation](https://gtt-technologies.de/ca-doc/index.html).
The six-temperature-coefficient basis and extra-power records are described
in [ORNL/SPR-2018/864, Appendix B](https://info.ornl.gov/sites/publications/Files/Pub111424.pdf).
All numerical values in this example come from the supplied DAT.

## What this example exposes in the schema

The source distinguishes Va from neutral oxides: its second-site role value
is 1, while AlO1.5 and FeO1.5 have 0. The current schema has no explicit
vacancy-role field. This example places Va in `neutrals` with `charge="0"`
as the existing storage convention, and documents the source role separately.
That zero must not be interpreted as the vacancy's effective SUBI charge.

Likewise, the source's endmember stoichiometry and function normalization
are recorded in comments because the ionic endmember type has no explicit
stoichiometry field. For example, Fe+2AlO1.5 has **no Fe** in its source
stoichiometry despite the first-site label.

The document passes XSD and Schematron validation. It is a source-backed
serialization example, not a claim that a consumer evaluating ordinary CEF
mixing or treating Va as an ordinary neutral species will reproduce SUBI
equilibria. An explicit vacancy role and documented ionic normalization
semantics are the next schema questions raised by this real dataset.
