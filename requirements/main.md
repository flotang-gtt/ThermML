# ThermML Requirements

This directory hosts the set of requirements that focuses and directs development of the ThermML markup language.

We use formal requirement analysis and specification to make sure that design and implementation are directed by a thorough understanding of what is important and needed.
It also allows us to engage with the CALPHAD community regarding their needs, concerns, frustrations, and preferences.
This should reduce the risk of making naive and unwise design and implementation decisions.
It should also enhance the probability of the community adopting ThermML as a standard.

## Brandon's Initial List

The list below is included here to make sure that we address all items explicitly in formal requirements.
Once this has been done, we can remove the list.

1. The new format should be an interchange format that's machine readable and human readable

   **TRANSFERRED**: [Data Language: Machine Usable, Human Usable]

1. Software implementations can use any format they like internally (for performance, etc.), as long as they can read/write to the interchange format

   **IGNORED**: This is addequately addressed by [Data Language: Machine Usable].

1. Should be able to describe metadata like version history and give better references to related publications or other databases containing parameters, reference state data, general metadata, etc.

   **TRANSFERRED**: [Data Schema: Capture Metadata, Capture System Component Reference State Data]

1. Should still be relatively pleasant to edit manually and format in a way that is convenient enough to make small edits and modifications by hand

   **TRANSFERRED**: [Data Language: Human Usable].

1. Should make it easier to compare and combine databases

   **TRANSFERRED**: [Data Schema: Ease of Data File Comparison, Ease of Data File Combination]

1. Should have clear hooks for extensibility, e.g. new types of parameters or models

   **TRANSFERRED**: [Data Schema: Extensible].

1. Should give clear guidance to what data can be added in a parameter. The TDB may be too rigid, but we also don't want a wild west of complicated parameters/types

1. Machine-readability should lend itself to automated data collection, indexing and retrieval. For example, it should be easy to expose the databases and metadata by an API or to aggregate statistics about a collection of databases.

1. Support global phase identifiers and aliases (SIGMA_D8B, SIGMA, D8B all are valid local names that refer to the same phase)

1. Should contain a mechanism that facilities optimizing variables

1. Mechanism for including uncertainties or sensitivities? Like TDBX? Consider different representations, like the uncertainty being described by a closed-form distribution or MCMC-like samples from a posterior.

1. Consider the possibility of interphase properties (e.g., interfacial energy). This requires the ability to describe linkages between one or more phases. This is already required for models like the two-phase order-disorder model, but it could potentially be implemented in a more robust way versus the "type definition" approach of the TDB format.

1. Nice-to-have: Trivial merging/sub-setting of databases. This would require that all node elements be able to either copied verbatim, or excluded, from such an operation. Attributes could not contain information which would need to be modified for a combined system or sub-system. So, `<Phase constituents="AL,ZN">` would not be allowed, but instead written as something like `<Phase><Constituent subl="0"><Element ref="AL" /></Constituent> <Constituent subl="0"><Element ref="ZN" /></Constituent> </Phase>`. This probably trades heavily against concise syntax.

1. Chemical element reference states need first-class support. This also supports database merging by helping to surface reference state incompatibilities.

   **TRANSFERRED**: [Data Schema:Capture System Component Reference State Data]
