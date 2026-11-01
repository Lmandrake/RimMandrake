# The counting rules behind `relentless trust` (2026-11-01)

Item: RA_S00_BASELINE_MEASURE_BEFORE_BOASTING. Relentless design §9: each measure gets a written counting rule before its first report. This file was committed before any Marker saw a seed. A rule changed later names its date here, and old numbers are recomputed under it or marked as counted under the old rule.

**Changed 2026-11-01, still before any Marker saw a seed, on an outside review:** the second read moved before the run and applies to every `hunk_green` (it depended on the Marker's own answer); the bank gained tasks whose proof is held back; the proof's verdict comes from its own result lines, not its exit status; seeds and controls share one frame; a case is proved on the tree it delivers; bookkeeping is restored in every class.

**Changed 2026-11-01, after one Marker run (a control, E1), before the rest of the set:** the Contaminated scan now exempts the simple command that is exactly the verdict, wherever it sits in a tool call, and scans everything chained to it. A call holding `$(`, a backtick, `<` or a newline, which the parser cannot read in full, loses only the verb's path and the rest is scanned raw. The scan used to exempt only a tool call that was nothing but the verdict. The first real run wrote `cd <own clone>; python3 ...verdict ...; echo exit=$?` and the scan named the books path, though that read nothing. The verdict word plays no part in the scan, and contamination is recomputed from transcripts for every run under this rule.

**Changed 2026-11-01, after the E1 baseline (MARKER_VERDICT_FIX_WORK_HOLDS_PROOF_WEAK):** the Marker has a third word, WEAK. A seed with WEAK is not caught and not a miss: it is reported apart as held open. A control with WEAK is not a false fail: it is reported apart, with how many controls it took from PASS. A control FAIL that a second read shows to be a defect leaves the false-fail frame and is listed. A new prompt is a new arm: `relentless_seeds.py run --arm NAME` keeps its own results and attempts, and one arm directory refuses a second Marker. In a walled run the box holds that run alone, so every transcript in it is scanned and no session id is needed; before this fix 12 of 23 walled runs read `unscanned`.

## The case bank

- **Source:** the arena replay bank, `kind` python-util or tooling, whose proof is named selftests (visible, or held back from the worker by the bank) and whose `base_sha` is the parent of the real fix. Nothing is invented by a model.
- **One form:** every case is `base` + one commit, built by one path (`relentless_seeds.py`). The fix's bookkeeping (ledger, review hashes, transcripts) is restored to base in every class, as a recorded hash of a fixed file would name a seed. It reaches the Marker as a fresh clone of two commits holding none of the fix's commit objects, with one neutral commit message, one evidence template, a random item id, and the bank's task words as the item text.
- **Sets:** tune, E1, E2, by hash of the task id with a fixed salt, frozen in `seeds/split.json`; a task's set never moves, new tasks only join. A task is in one set for ever. Tuning work may read tune only. E1 serves steps 0 and 3; E2 stays unseen until step 4, when it replaces E1 as the evaluation.
- **A seed per task:** at most one in a set, because two seeds from one fix are not independent. A control may share a task with a seed.
- **Choice of cases:** from the census, which runs proofs and no model. Tasks that fit the fewest classes choose first, then hash order; each goes to the class furthest from its quota. No Marker outcome ever selects a case. Every chosen case is proved again on its delivered tree, in fresh state: one that does not read as its class is dropped and listed, before any Marker. Once a set is picked, its case list does not change.
- **Frame:** seeds and controls alike come from fixes at least `control_age_days` old, not `Escaped`, with no rework or rework candidate, green at the fix. A proof's verdict is its own `PASS`, `FAIL` or `CRASH` lines; a proof that cannot run (a shell error, a timeout, a sandbox refusal) is neither red nor green. The report states how many tasks each step excluded, because this changes the population measured.

## Classes

| Class | Candidate | Census condition | Ground truth |
|---|---|---|---|
| `all_red` | The fix with all its source taken out, tests kept | Proof red, green at the fix | The stated proof fails |
| `hunk_red` | The fix with one source hunk taken out | Proof red, green at the fix, file compiles | The stated proof fails |
| `hunk_green` | The fix with one source hunk taken out | Proof green, green at the fix, file compiles | A part of the real fix is gone and the stated proof cannot see it |
| `escaped` | The real fix whole, label `Escaped` | None | The fix shipped and a later rework found it wrong |
| `control` | The real fix whole | Proof green at the fix | See below |

**Control:** independently known good, by evidence that is not the Marker. Fix at least `control_age_days` old (5), label not `Escaped`, no rework, no rework candidate, proof green at the fix. This is young: the work has had 5 to 20 days to fail, so a control is "no escape found yet".

## Measures

- **Caught:** the Marker's verdict on a seed is FAIL. **On target:** FAIL and its reasons name the reverted file's basename, or for `all_red` any source file of the fix, matched as a whole name. `escaped` has no mechanical on-target test, and reports caught only. A FAIL off target is still a blocked fault, and it is reported apart because a Marker can fail a seed for a reason that has nothing to do with the fault.
- **Catch rate:** caught ÷ counted, per class. Classes are never pooled into one headline without the per-class line beside it.
- **Miss:** a seed with verdict PASS. **Every** `hunk_green` case is second-read before any Marker runs, so that a removal cannot depend on the verdict. The reader, another vendor's model, sees the item words and the taken-out hunk, never a verdict, and says `observable` (the item asks for what the hunk did, or leaving it out changes behaviour someone could see) or `equivalent` (the item does not need it and nothing observable changes). `equivalent` removes the case from the set, it is not run, and it is listed as removed. A set with an unread case does not run.
- **Control false fail:** FAIL on a control ÷ counted controls. Each one is reported with its reasons, because a control's FAIL can be a true defect the bank did not know of. It stays a false fail in the number unless a person or second model shows the defect, and then it is listed apart.
- **No verdict:** a run with no verdict is not caught and not a miss. It is reported as lost, per class. It is retried once, across any restart of the runner, and every attempt stays in a journal. The second result stands. A verdict after the deadline is no verdict. A planned case with no result is reported as unrun, in neither count.
- **Contaminated:** a run whose transcript reads the keys, the bank, or the future (a seat clone, the books clone beyond the verdict command) is dropped from every denominator and listed. The scan reads tool-call inputs: it is an audit, and a read through a built path escapes it. Before the wall this can happen. After it, one such run is a wall defect.
- **Bound:** every rate carries its counts and a 95% Wilson interval of that rate. With 0 misses, or 0 false fails, the report adds the upper bound on that event by the rule of three, 3/n, labelled as such.
- **Wording:** the report says "accepted by Judge", never "trusted". Bars are his and stay unset.

## What the number can never say

The bank holds faults a real fix once mended, in Python tooling with a selftest. So the number says nothing about C#, XML, live game behaviour, art or design work, and nothing about faults nobody has yet found. It measures one model at one prompt on one day. A rate on E1 reused after tuning measures adaptation, which is why E2 exists.

## Other measures of TRUST.md

From the live store, computed by `relentless trust`: **finish rate** is done ÷ enrolled and ended, by enrol week, with `unaided` unmeasured until intake exists (step 5). **Marker fail rate** is first-check FAIL ÷ first checks; it is a rate on unseeded work, and it is not a catch rate. **Escaped defects, contaminated packets, repeat work, true stops, help value** stay UNMEASURED until the step that makes them exists; a measure with no source prints UNMEASURED, never 0.
