# The counting rules behind `relentless trust` (2026-11-01)

Item: RA_S00_BASELINE_MEASURE_BEFORE_BOASTING. Relentless design §9: each measure gets a written counting rule before its first report. This file was committed before any Marker saw a seed. A rule changed later names its date here, and old numbers are recomputed under it or marked as counted under the old rule.

## The case bank

- **Source:** the arena replay bank, `kind` python-util or tooling, whose proof is a named selftest and whose `base_sha` is the parent of the real fix. Nothing is invented by a model.
- **One form:** every case is `base` + one commit, built by one path (`relentless_seeds.py`). It reaches the Marker with one neutral commit message, one evidence template, an opaque item id, and the bank's task words as the item text.
- **Sets:** tune, E1, E2, by hash of the task id with a fixed salt, frozen in `seeds/split.json` before any proof ran. A task is in one set for ever. Tuning work may read tune only. E1 serves steps 0 and 3; E2 stays unseen until step 4, when it replaces E1 as the evaluation.
- **A seed per task:** at most one in a set, because two seeds from one fix are not independent. A control may share a task with a seed.
- **Choice of cases:** by hash order inside each class, from the census, which runs proofs and no model. No Marker outcome ever selects a case. Once a set has been run, its case list does not change.

## Classes

| Class | Candidate | Census condition | Ground truth |
|---|---|---|---|
| `all_red` | The fix with all its source taken out, tests kept | Proof red, green at the fix | The stated proof fails |
| `hunk_red` | The fix with one source hunk taken out | Proof red, green at the fix, file compiles | The stated proof fails |
| `hunk_green` | The fix with one source hunk taken out | Proof green, green at the fix, file compiles | A part of the real fix is gone and the stated proof cannot see it |
| `escaped` | The real fix whole, label `Escaped` | None | The fix shipped and a later rework found it wrong |
| `control` | The real fix whole | Proof green | See below |

**Control:** independently known good, by evidence that is not the Marker. Fix at least `control_age_days` old (5), label not `Escaped`, no rework, no rework candidate, proof green at the fix. This is young: the work has had 5 to 20 days to fail, so a control is "no escape found yet".

## Measures

- **Caught:** the Marker's verdict on a seed is FAIL. **On target:** FAIL and its reasons name the reverted file's basename, or for `all_red` any fix file. `escaped` has no mechanical on-target test, and reports caught only. A FAIL off target is still a blocked fault, and it is reported apart because a Marker can fail a seed for a reason that has nothing to do with the fault.
- **Catch rate:** caught ÷ counted, per class. Classes are never pooled into one headline without the per-class line beside it.
- **Miss:** a seed with verdict PASS. A miss in `hunk_green` is second-read before it counts. The reader, another vendor's model, sees the item words and the taken-out hunk and says `observable` (the item asks for what the hunk did) or `equivalent` (the item does not need it, or nothing observable changes). `equivalent` removes the case from the denominator and it is listed as removed. An unread miss counts as a miss.
- **Control false fail:** FAIL on a control ÷ counted controls. Each one is reported with its reasons, because a control's FAIL can be a true defect the bank did not know of. It stays a false fail in the number unless a person or second model shows the defect, and then it is listed apart.
- **No verdict:** a run with no verdict is not caught and not a miss. It is reported as lost, per class. It is retried once. The second result stands.
- **Contaminated:** a run whose transcript reads the keys, the bank, or the future (a seat clone, the books clone beyond the verdict command) is dropped from every denominator and listed. Before the wall this can happen. After it, one such run is a wall defect.
- **Bound:** every rate carries its counts and a 95% Wilson interval. With 0 misses the upper bound is by the rule of three, 3/n.
- **Wording:** the report says "accepted by Judge", never "trusted". Bars are his and stay unset.

## What the number can never say

The bank holds faults a real fix once mended, in Python tooling with a selftest. So the number says nothing about C#, XML, live game behaviour, art or design work, and nothing about faults nobody has yet found. It measures one model at one prompt on one day. A rate on E1 reused after tuning measures adaptation, which is why E2 exists.

## Other measures of TRUST.md

From the live store, computed by `relentless trust`: **finish rate** is done ÷ enrolled and ended, by enrol week, with `unaided` unmeasured until intake exists (step 5). **Marker fail rate** is first-check FAIL ÷ first checks; it is a rate on unseeded work, and it is not a catch rate. **Escaped defects, contaminated packets, repeat work, true stops, help value** stay UNMEASURED until the step that makes them exists; a measure with no source prints UNMEASURED, never 0.
