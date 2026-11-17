# The open pipeline work items, as filed

These are existing tickets in the Maturation Pipeline's own machinery (not mod content), each
reproduced verbatim from `infrastructure/state/items/<ID>.md`. They are the work queue the three
proposed changes would join.


## RIMMANDRAKE_DECIDE_COVERAGE_LOOK_BEFORE_EXAM_SIX_EXAMS_RETAKEN
```
# RIMMANDRAKE_DECIDE_COVERAGE_LOOK_BEFORE_EXAM_SIX_EXAMS_RETAKEN

## spec
A decision for the Conductor, from `design/specs/2026-11-15-cheap-guards-at-every-door.md` (section 7). Not a build.
The Designer takes its exam (stage 4) before the coverage judge looks (stage 5); a coverage refusal returns the concept
to stage 3 and the exam is then taken again. Measured from the Designer run records and each stage.json, 2026-11-04 to
11-15: 13 of 16 exam runs passed (Gimme Some Slack failed one, PyrelandsMechanics' control failed twice); 3 of 14
coverage looks signed. Six exam retakes followed a coverage refusal: Gimme Some Slack USD 2.61, 2.54, 5.06; Pyrelands
2.67, 2.80; Graffiti 3.11; USD 18.79 in all.
The question: should the coverage judge look before the exam, with the exam taken once on the tree the judge signs (and
again only if the exam itself changes the tree)? For: the check that usually refuses runs first. Against, unmeasured:
whether the judge's reading leans on an exam-passed tree (`maturation_autonomy.exam_gate` makes the judge skip when the
exam does not pass, which says someone wanted that order), and his card of 2026-11-14 kept both as gates before a lock
without ruling on their order.
If yes: file the build with its acceptance test (the stage machine's order, `exam_gate`, the locked-change chain).
If no: close this with the reason, so it is not found again.

The builder does not edit the acceptance test; a clause believed wrong goes to the Conductor with the evidence.
A guard that cannot run says "did not run" and lets the work through; every refusal carries evidence, would_pass and
smallest_fix (standing_rulings.md, A refusal carries its path to pass).

## refs
file: design/specs/2026-11-15-cheap-guards-at-every-door.md
file: src/RimMandrake/rimflow/maturation_autonomy.py
file: src/RimMandrake/rimflow/designer_stage.py

## verify
none (a decision)

## criteria
- A1: closed with the decision and its reason in the close note.

## acceptance
Acceptance test: none, a stage-order decision; a build that follows from it is filed with its own test.
```

## RIMMANDRAKE_DRAIN_ITEMS_WAITING_ON_A_JUDGE_THAT_RETIRED
```
## spec
Found by the pipeline sleeper census (`design/RimMandrake/pipeline_sleepers_census_2026-11-15.md`). Relentless was
retired 2026-11-13 with nothing to resume, and with it the only program that ran its binding-repair judge
(`RELENTLESS_WIRE_BINDING_JUDGE_NOBODY_RUNS` already said no program launched it). 46 open items were still blocked
with kind `judge` by a Relentless snag (43 `binding_repair`) on 2026-11-15; most of their block reasons say the work
already landed (a sha on origin) and only the proof line was unrunnable in Relentless's box. Nothing will ever lift
these blocks, and `rimflow next` never offers a blocked item.

For each item listed by the acceptance test: if its block names a landed sha on origin/main, run its proof in a plain
shell (the rebind the block describes), record `rimflow verify --sha <sha> --level L0`, unblock and close on that sha;
if the proof fails, unblock to ready with the corrected proof line in the item; if the item is dead, drop it with the
probe. `ARENA_TRIAL_RETIRE_HUNDRED_GIGS_IDLE` is the worked example (landed 1f0e666566dc, pass recorded 2026-11-07).
Mod-content items in the list go through the same steps; they are listed because their block is pipeline machinery.

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/judge_blocked_drained_accept.py` exits 0 printing
`PASS 0 open items wait on the retired judge`. Watched failing on 464c69ccf0 (45 listed after the census's drops).
```

## RIMMANDRAKE_GATE_STAGE_THREE_ON_UNBUILT_BEHAVIOUR_FROZEN_RECORD
```
# RIMMANDRAKE_GATE_STAGE_THREE_ON_UNBUILT_BEHAVIOUR_FROZEN_RECORD

## spec
Graffiti 0.1.0 moved offline_build -> blind_challenge (2026-11-16 13:37 PST) with a locked bar whose behaviour does not exist:
raider_pressure / inv_raider_future_marks (no raider-pressure code in src/RimMandrake/Graffiti/Source, 0 grep hits for
"pressure"; 8 settings ship, the bar wants 11; build item RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_LETTER_NAMES_THE_WALL
open). The Stage 3 exit (maturation.py, offline_build: every_bar_has_a_check_that_runs, table_version) counts a live-only bar
runnable when its scene entry exists, so an unbuilt behaviour passes Stage 3 and is first found at Stage 6. The spec's
Stage 3 purpose is "build/implement"; its exit text does not say "the behaviour exists".
Fix unknown, handed to the Conductor: the obvious data source, record.json `impl: absent`, is frozen at the lock and stale
for every mod (ExplosiveKnockback 7, FlowWorks 3, GimmeSomeSlack 2, LeaningScrub 5, Pyrelands 2 locked rows still read
absent, several since built), and an open `item` behind a decider is normal for every mod's live scenes. A gate needs a
live "behaviour built" signal per bar (e.g. the build item's implemented event) that does not exist yet; adding an exit
clause is a change to a stage exit marked HIS by agreement.

## verify
Acceptance test: none, the gate's data source is undecided (see spec).

## criteria
- A mod with a locked bar whose behaviour is unbuilt cannot leave Stage 3, by a signal that is live, not the frozen record.
```

## RIMMANDRAKE_GRANT_BLIND_JUDGE_A_JUDGE_WRITER_VERDICTS_REFUSED
```
# RIMMANDRAKE_GRANT_BLIND_JUDGE_A_JUDGE_WRITER_VERDICTS_REFUSED

## spec

The GimmeSomeSlack blind cycle 5 run (run-1794814806, role blind_judge) was launched with `RM_MODLEDGER_WRITER=HOLDER.run-1794814806`.
`modledger.json` writers.HOLDER has no `finding.verified` or `finding.open`, and `modledger.py` refuses a HOLDER process
writing the `JUDGE.<run>` shard ("a holder never writes a judge's finding"). So the cycle's verdicts on the 17 claimed-fixed
findings (the steward's stated reason for opening the cycle) and its new findings could not be written to the mod ledger;
they are in `design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_5/SUMMARY.md` only. Separately, the holder lease
lapsed after 45 idle minutes because the run wrote rimflow notes but no modledger event; only DISPATCH can regrant it, so the
run's closing `session.checkpoint` was refused too (NO_CHECKPOINT expected).

Not fixed by the finder: the fix changes the ledger's fencing (which process may write a judge's verdict), a design call for
the Conductor. Options: launch a blind_judge run with a JUDGE.<run> writer (and its checkpoints as JUDGE notes), or let a
HOLDER whose lease role is blind_judge write finding.verified/finding.open; and say in the brief that any modledger append
renews the lease, so a run must append at least every 45 minutes.

## verify

Acceptance test: none yet, the design is the Conductor's; once chosen, a selftest that a blind_judge launch can append
`finding.verified` for a claimed_fixed finding and a holder-role launch cannot.
```

## RIMMANDRAKE_COUNT_ADVANCE_REFUSALS_SO_A_LOOP_RINGS
```
## spec
Plan `design/plans/2026-11-14-maturation-pipeline-build.md` slice 2, second half, and
`design/RimMandrake/maturation_pipeline.md` §9 "Designed but not built": `maturation.py advance` refusals go through
`refusal_contract.submit`, so a stage refused again and again raises `REFUSAL_NOTHING_COULD_EVER_PASS` instead of
looping. Today `maturation.py` calls `RC.check` on a verdict (line ~653) but never `RC.submit`, so repeated advance
refusals count nowhere. Found by the pipeline sleeper census (`design/RimMandrake/pipeline_sleepers_census_2026-11-15.md`).

Acceptance test: none written yet, because the plan's own test (`RM_REFUSAL_DIR=<tmp> python3
src/RimMandrake/rimflow/selftest_maturation.py --submit`) PASSES on base 464c69ccf0 (the flag is ignored), so it is not
an oracle. The builder writes first a case that runs a refused `advance` in a sandbox with `RM_REFUSAL_DIR` set and
asserts one submitted row there (and the alarm row after the repeat limit), watches it fail on base, then builds.
```

## RIMMANDRAKE_RECORD_RED_SEEN_PER_TEST_OR_PASSED_GREEN
```
# RIMMANDRAKE_RECORD_RED_SEEN_PER_TEST_OR_PASSED_GREEN

## spec
The fourth clause of the pre-judgement certificate, `red_seen`, of `design/specs/2026-11-15-cheap-guards-at-every-door.md` (section 4). After
RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN.
Protects against: a deciding test that cannot fail. Evidence: the Knockback cycle-3 judge filed
RIMMANDRAKE_PROVE_PROOF_GATE_EXIT_AN_OR_PASSED_GREEN (a gate whose OR passed green) and
RIMMANDRAKE_RUN_STOREROOM_RESTORE_WAIVER_TAKEN_ON_TRUST; ten of the Gimme Some Slack cycle-2 judge's planted faults were
weakenings of test files that nothing caught. That it would have caught the first is a guess (~60%): one probable
incident, so no backfill is ordered.

Build in `judge_certificate.py`: `red_seen(root, mod, test_id, patch=...)` (apply the patch, run the test, want a
non-zero exit, reverse the patch, prove the files byte-identical; a test that stays green is NOT recorded),
`grandfather(root, mod)` (written once), the verbs `maturation.py red-seen <Mod> <TEST> --patch FILE` and
`certificate <Mod> --grandfather`, and the clause: PASS on a recorded red for the test file as it is now, WARN
"grandfathered" for a test unchanged since the list was written, REFUSED for a new or edited deciding test with no
proof. Run `--grandfather` once for each advancing mod in the same change and commit the lists, so nothing that exists
today is refused. Tell the builders: the Stage 3 builder brief (`maturation.brief_text`) gains one line naming the verb.

The builder does not edit the acceptance test; a clause believed wrong goes to the Conductor with the evidence.
A guard that cannot run says "did not run" and lets the work through; every refusal carries evidence, would_pass and
smallest_fix (standing_rulings.md, A refusal carries its path to pass).

## refs
item: RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/acceptance/guard_judge_certificate_accept.py
file: design/specs/2026-11-15-cheap-guards-at-every-door.md

## verify
python3 src/RimMandrake/rimflow/acceptance/guard_judge_certificate_accept.py --red-seen

## criteria
- A1: the acceptance test with `--red-seen` prints `PASS 28/28` and exits 0 (it reruns the first ticket's clauses).
- A2: the grandfather lists are committed for every advancing mod and `certificate` still certifies whatever it certified before this change.
- A3: one real test of one mod is proven with a real planted fault through the verb; the record is committed and named in the close note.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/guard_judge_certificate_accept.py --red-seen` exits 0 with `PASS 28/28`.
Watched failing at ed7e3b5389: `FAIL 2/28`, exit 1 (no module; the two that pass are the "source is restored" clauses, true
when nothing ran, which a correct build must keep). Not yet run against any implementation.
```

## RIMMANDRAKE_MEND_COVERAGE_RECORD_SELFTEST_RED_SINCE_BAR_RULE
```
# RIMMANDRAKE_MEND_COVERAGE_RECORD_SELFTEST_RED_SINCE_BAR_RULE

Found 2026-11-16 by the steward run RIMMANDRAKE_STEWARD_LEANINGSCRUB_PREFLIGHT_STAGE, when ./publish ran the pipeline checks for a change to `src/RimMandrake/rimflow/maturation.py` and refused on this test. Measured red on an export of origin/main at 2626f90d0b (no local change in it), so it is not caused by that change.

## spec
`python3 src/RimMandrake/rimflow/selftest_coverage_refusal_record.py` fails one case:
`FAIL bad row fixed on re-ask: both refusals stand, the contract accepts the whole look  got: ('not_covered', None, [['leaf_wall'], ['inv_throw']])`.
Guess (not measured): the case's `inv_throw` gap ("the throw scene reads no distance") may now be read by the bar rule of 579eb06168 (coverage judge: a passing bar is an experience, never a tuning number) so the contract field comes back None. Find whether the code or the case is wrong; a weakened assertion is not a fix.

## criteria
- The case passes for a reason the test states; no assertion weakened, skipped or deleted.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_coverage_refusal_record.py` ends `PASS` with 0 failures. Watched failing 2026-11-16 on origin/main 2626f90d0b: `FAIL (1)`.

## refs
file: src/RimMandrake/rimflow/selftest_coverage_refusal_record.py
file: src/RimMandrake/rimflow/coverage_judge.py
```

## RIMMANDRAKE_RECORD_BUILD_IDENTITY_IN_LIVE_ROWS
```
# RIMMANDRAKE_RECORD_BUILD_IDENTITY_IN_LIVE_ROWS

## spec
Found while building `RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO` (his ruling of 2026-11-17: a verdict whose
mod hash or game build differs from the build he walks does not count; its line item is re-run). The Stage 6 exit now
runs `src/RimMandrake/rimflow/build_match.py`, which needs every in-game row to carry `mod_hash`, `game_build`,
`active_mods`, `tier` or `full_list`, and `unit`: the JSON line `build_match.py identity --mod <Mod> --tier <T>` (or
`--full`) prints. The in-game brief in `maturation.py` tells the runner to merge it. Nothing else does yet:
- the SteveDesktop test queue jobs (`src/RimMandrake/Utils/testq/`) write no identity fields;
- every existing visit's rows (Gimme Some Slack, Pyrelands, FlowWorks, Explosive Knockback) lack them, so
  `build_match.py check --mod <Mod>` reads every check "re-run it" (measured on Gimme Some Slack:
  `D:\ClaudeWork\rimmandrake\conductor\bm_live_check_gss.txt`). That is as ruled, not a defect.
- no stage-6 test in Pyrelands' test table (45 checks) declares `tier` or `why_full_list`, so each is read as a
  minimal-list test whose tier comes from its row.

Work: make the queue runner and any scripted in-game driver call `build_match.py identity` after the deploy and the
list swap and merge it into each row; make the test-table makers write each stage-6 check's `tier` (or
`why_full_list`).

## verify
A queue job run offline on a fixture writes rows that `build_match.py check` counts; a row written before a redeploy
reads "re-run it".

## criteria
- every row a live driver or queue job writes carries the fields `build_match.py identity` prints;
- each stage-6 check in a test table declares `tier` or `why_full_list`.
```

## RIMMANDRAKE_UNFENCE_LIVE_HOLDER_WHEN_RIVAL_NEVER_STARTED
```
## spec
Dispatch launched two road-back fixers on ExplosiveKnockback a minute apart (2026-11-17, `design/concepts/ExplosiveKnockback/ledger/DISPATCH.jsonl`):
lease.grant run-1794896914 token 12 at 06:28:40Z, then lease.grant run-1794896974 token 13 at 06:29:41Z, whose run.end reads
never_started at 06:29:48Z. `modledger.grant` makes every new lease fence all older ones, so the live holder (run-1794896914)
had its 06:39 lease.renew counted as fenced and every later append refused ("stale token 12 ... this run must stop"),
its closing checkpoint included. Commit 9b5014c74e shows the same shape on run-1794896854.

Fix (choose one in `src/RimMandrake/rimflow/modledger.py` / `maturation_dispatch.py`): Dispatch refuses to launch a
second holder on a mod whose current lease is live (not released, last event under 45 min); or a never_started run's
end revokes its lease and `fenced()` ignores a revoked lease that never wrote, so the older live lease is current again.

## criteria
Acceptance test: `env -u RM_MODLEDGER_WRITER python3 src/RimMandrake/rimflow/fixtures/repro_modledger_never_started_fences_live_holder.py`
exits 0 printing `PASS live holder A still writes after B never started` (1 case). Watched red on 3792dbb557: exit 1,
`FAIL live holder A fenced by a never-started run: stale token 2`. If the fix is "refuse the second launch", the repro's
second `launch` raising is also a pass: adjust the repro to expect that refusal, never to skip A's append.

## verify
Run the repro and modledger's own selftests; check the next two-item road back on one mod launches one holder at a time.
```

## RIMMANDRAKE_HOLD_TICK_LAUNCHES_ON_STALE_CLONE_GHOST_STEWARD
```
## spec
The Dispatch tick (`maturation_dispatch.py tick --apply`, run from /home/mandrake/rm/dispatch) decides and launches from
its own clone's tree, but measured the clone's distance from origin/main only AFTER launching. On 2026-11-16 the clone
sat 51 behind / 9 ahead for 51 min (last level 2:14 AM PST); cycle 6's record with its exit block landed at 02:57
(290ce0c736) and at 03:02 the tick, reading the 02:07 lane-1 copy (`## Exit (pending)`), filed and launched
RIMMANDRAKE_COMPLETE_GIMMESOMESLACK_CYCLE_SIX_RECORD_NO, a steward run for a record gap that did not exist.
Fix: measure the clone before the launch step; while it is measured behind past the OPS_DISPATCH_CLONE_BEHIND_UNSTICK
alarm's threshold (5 min), launch nothing (decision `stale_clone`, a Needs Conductor line) and hold the run seals,
run.end and spend rows (idempotent: the first level tick writes them). The same 02:59 publish from the stale clone
sealed JUDGE.judge-1794822790 as 0 lines (19 landed), flagged its run.end NO_VERDICTS (false: the judge wrote 19 lines)
and dropped the 02:31 re-seal line (DISPATCH:d5cbe4dc4bce5af2), so selftest_modledger_tree refused every publish;
repaired by re-sealing both shards from the landed tree and rebuilding the views (the false NO_VERDICTS flag stays in
that run.end line). Same root as RIMMANDRAKE_SEAL_JUDGE_SHARD_FROM_SYNCED_CLONE_SEALED_EMPTY. A lag under 5 min holds
nothing; an UNMEASURED fetch holds nothing (errs toward allowing, as before). Unjamming the clone stays Operations'
alarm (RIMMANDRAKE_UNJAM_DISPATCH_CLONE_TWO_WRITERS_BLOCK_EACH_REBASE).

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_maturation_dispatch.py` → rc 0, 0 FAIL (172 PASS).
Watched red on the base (rc 1: 1 FAIL "a clone 10 min behind launches nothing", 170 PASS; then the seal-hold check
red alone, 171 PASS).

## criteria
A tick whose clone is measured behind > 5 min launches no run and writes no seal, run.end or spend
row; the first tick behind still launches.
```
