# BOUNDARY: the scene verdict ledger (scene_verdicts.py), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/scene_verdicts.py`, and its use in `maturation.py` (`read_ingame_exit`,
`_ledger_relation`). Item `RIMMANDRAKE_BUILD_SCENE_VERDICT_LEDGER_RECEIPT_IS_NOT_VERDICT`. Design: Bridge v2 decision 12
(`design/specs/2026-11-23-bridge-v2/05_build_design.md`). The rules of kinds A, B and C are `live_kinds.py`'s
(`design/specs/2026-11-23-live-kinds-exit-reader/boundary.md`): this module decides which runs are samples that may count
for a bar and hands only those to `live_kinds.reading`. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_scene_verdicts.py`, which also plants a fault in each part of the ledger and sees a test
go red.

Words: a **run line** is one run of a scene, copied from its receipt. A **class line** classes or re-judges a run line that
is already there. The **claim** is the hash of the scene's plan. A **sample** is a run line that is not a replay and whose
receipt is not seen before. A **cluster** is a set of side-by-side copies with one `cluster` id.

## ACCEPTS (the only inputs this is built for)

- **a-ledger.** `design/concepts/<Mod>/version/scene_runs.jsonl`, one JSON object a line, appended only.
- **a-run-line.** `rec: run`, with `run`, `scene` (the test table's check id), `claim`, `build` (the mod sha), `outcome`
  (one of the seven) and `receipt` (the receipt's hash). The receipt's marks: `overlay` (`none` or the stamp), `tainted`
  (bool), `arm` (`reference`, or another arm with `compared`), `build_kind` (`RELEASE` or `PROOF`), `map_kind`. Optional:
  `cluster`, `replay_of`, `forbidden`, `spoiled_by`, `serious`, `symptom`, `hunt` (`what`, `why_it_matters`,
  `next_step`, `cost`).
- **a-class-line.** `rec: class`, with `run`, `outcome`, `why` (six words at least), `by`, `how` (`classed` or
  `rejudged`), and `spoiled_by` for an ENVIRONMENT FAULT.
- **a-test.** The test table's spec of the check: `test_kind`, `tag_evidence`, `budget`, `x_of_y`, and `map_kinds` (the
  map kinds that the bar accepts; absent is `settlement`).

## DOES NOT SURVIVE (not promised)

- A ledger edited by hand in place: the history is what the file holds.
- Two writers that append the same run id at the same moment: `flock` orders them, and the second is not refused.
- **No producer writes a run line yet.** `scene.py accept` does not append to the ledger, because the receipt has no taint
  mark, arm or build kind yet (the overlay and deviation-record tickets add them). Until then only `scene_verdicts.py add`
  writes a line, and the exit reads no line for a mod whose ledger is absent.

## PROMISES (each one is owed a test of the same name)

- **kind-a-one-success-passes.** One counted SUCCESS of a kind A scene reads PASS.
- **kind-a-one-mod-failure-fails.** One counted MOD FAILURE of a kind A scene reads FAIL, and a later SUCCESS on the same
  claim and build does not hide it. A run with a forbidden effect is a MOD FAILURE, whatever its outcome word.
- **kind-b-one-success-passes.** One counted SUCCESS of a kind B scene reads PASS.
- **kind-b-mod-failure-blocks-the-pass.** A MOD FAILURE on the same claim and build makes a kind B scene FAIL.
- **kind-b-unresolved-blocks-the-pass.** An UNRESOLVED run on the same claim and build holds a kind B pass (HELD).
- **spent-budget-is-inconclusive.** A kind B budget spent with no SUCCESS reads INCONCLUSIVE; our own faults (APPARATUS
  FAULT, COULD NOT LOOK) spend no trial.
- **x-of-y-short-is-held-for-the-conductor.** A scene that ends short of its X of Y reads SHORT, held for the Conductor's
  call (`shortfall.py`); X successes read PASS.
- **unresolved-holds-until-classed.** An UNRESOLVED run holds the pass until a class line with a why of six words or more
  classes it.
- **reclassification-keeps-the-history.** A class line is added; the run line stays as it was written, and the run shows
  every outcome in order.
- **a-replay-is-not-a-sample.** A run with `replay_of`, or a receipt hash seen before on any claim, counts as no sample.
- **a-cluster-counts-as-one.** A cluster is one sample. Each copy is read as `live_kinds` reads it (a forbidden effect
  is a MOD FAILURE; an ENVIRONMENT FAULT without `spoiled_by` is UNRESOLVED). The cluster reads MOD FAILURE if any copy
  does, then UNRESOLVED, then SUCCESS.
- **a-stamped-run-reads-tuned.** A run with an overlay stamp other than `none` reads TUNED and counts for nothing.
- **the-taint-mark-counts-for-nothing.** A run with `tainted: true`, or a taint mark that is not established, reads TUNED
  and counts for nothing, also when `overlay` reads `none`.
- **an-uncompared-arm-counts-for-nothing.** A run on an arm other than the reference counts only with `compared: true`.
- **a-proof-build-or-a-map-the-bar-refuses-counts-for-nothing.** A PROOF build, or a map kind that the test's
  `map_kinds` does not accept, counts for nothing. An empty `map_kinds` accepts no map; only an absent one defaults.
- **an-untouched-change-keeps-the-verdict.** A run on an earlier build counts only when the relation says that the
  change does not touch what the scene reads; touched and unknown count for nothing.
- **a-serious-unresolved-opens-a-hunt-notice.** A serious UNRESOLVED run, or a symptom seen on a second UNRESOLVED run,
  gives one notice with the four parts of `hunt_open.py`, the parts that are missing, and the `hunt_open.py` command.
  This module writes no log and no note.
- **zero-none-could-not-look-and-failed-are-four-answers.** The summary's state is NONE (no run of the scene), ZERO
  (runs, none counted), COULD NOT LOOK (the ledger cannot be read) or FAILED (the test's tag cannot be used), each with
  its own exit code and no verdict, apart from READ.
- **a-rejudged-run-shows-both-outcomes.** A re-judged run shows the first and the new outcome; the new one speaks.
- **a-line-without-identity-is-refused.** A run line without its identity, or a second run line for one run id, is
  refused by name and nothing is written.
- **a-planted-run-counts-for-nothing.** A run line whose stamps are not empty counts for no bar: a red run of `scene.py
  both-ways` (stamp `PLANTED <mutant>`) reads "NOT COUNTED: a red run", a TUNED stamp reads TUNED, any other stamp (EXPLORED)
  reads NOT COUNTED (`scene_mutants.py`, `design/specs/2026-11-23-bridge-v2/boundary.md` §MUTANTS AND SHOWN BOTH WAYS).
- **exit-holds-a-pass-the-ledger-refuses.** The Stage 6 exit keeps a check's `pass` only when the ledger has no line for
  its scene or reads PASS. A tuned or tainted run gives `spoiled`, an UNRESOLVED run `unresolved`, and the exit is not
  met. A check with no ledger line is not touched.

## LIMITS

- None. The module reads one file and runs no command.

Later lists beside this page: `polish.md`.
