# Species Duplicate Stoichiometry

Rule family:

- `VAL-WARN-SPECIES-DUPLICATE-STOICHIOMETRY`

Files in this directory keep the rule and its focused fixtures together.

- `rule.sch`: Schematron rule family
- `valid.xml`: passing fixture without warnings (different charges and formulas reused across phases)
- `warning.xml`: valid fixture with distinct names sharing composition and charge

Species identity is the phase-local `name` used by constituent references, not the
pair `(composition, charge)`. Distinct named species may have the same composition
and charge while retaining independent thermodynamic parameters or native model
identities. This applies across phase families, so formula coincidences are
advisory warnings rather than an MQM-specific exception to a general error.

For example, an MQM assessment can distinguish native names `Fe` and `Fe3+`, or
`Cu` and `Cu2+`, with equal compositions and a formal model valence of one for
each species. Preserve those names and the source model's `charge` values. MQM
`charge` represents formal model valence; it need not match a physical oxidation
state or a suffix in the native name. The current format does not provide a
separate physical-charge field. Merging species or replacing their model valences
with inferred oxidation states would change the assessment.

The comparison remains intentionally syntactic. Within one phase's `<species>`
block it compares normalized `composition` and `charge` strings. It does not parse
or canonicalize formulas (`Fe1` versus `Fe`, or reordered elements) or charge
spellings (`+1` versus `1`). Missing and empty compositions are not compared.
Different charges and formulas reused in different phases do not trigger a warning.
Matching strings invite review; they neither establish nor exhaust duplicate identity.

The former error ID `VAL-ERR-SPECIES-DUPLICATE-STOICHIOMETRY` is replaced by the
warning ID above. XSD still rejects duplicate species names and broken references.
Actual constituent-array checks and model-specific charge restrictions remain
errors. Ionic-liquid constituent groups use the analogous
`VAL-WARN-IONIC-DUPLICATE-SPECIES` advisory in their own rule family.
