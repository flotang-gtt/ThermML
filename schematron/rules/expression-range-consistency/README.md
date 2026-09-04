# Expression range consistency

Applies to ranges with `low` and `high` attributes anywhere inside a database,
including global expressions, inline pure-phase functions and H-S-Cp ranges.
Checks compare sibling ranges belonging to the same function.

- `VAL-ERR-EXPRESSION-RANGE-BOUNDS`: lower bound must not exceed upper bound.
- `VAL-ERR-EXPRESSION-RANGE-ORDER`: records are sorted by nondecreasing lower bound.
- `VAL-ERR-EXPRESSION-RANGE-OVERLAP`: positive-width intervals must not overlap,
  including non-adjacent or nested intervals.

Positive-width intervals use `[low, high)` boundaries; adjacent intervals can
share a boundary. Zero-width records remain allowed and do not contribute an
overlap, including when located inside a positive-width interval. They must
still respect lower-bound ordering. Gaps remain allowed for incomplete models.
No continuity of values or derivatives is required.

`valid.xml` and `invalid.xml` are minimal fixtures for the standalone `rule.sch`.
