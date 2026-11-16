# RIMMANDRAKE_CUTOVER_PILOT_MODS_TO_LEDGER_SAME_DAY

Plan step 4 (`design/plans/2026-11-15-holder-pipeline-fusion-build.md`; spec `design/specs/2026-11-15-holder-pipeline-fusion.md` §3.2 and §3.8 step 4). After a mod's shadow views have agreed with its old files
(compare every dispatcher tick for a few days, and a judge who did not write the backfill reads the packet against the
old files), archive its hand-written stores read-only with their provenance and redirect or refuse every writer to them,
on the same day for that mod. Spec §4.10: "A ledger plus old files still written is store number 18."

## spec

- Shadow compare at every dispatcher tick (`modledger_backfill.compare`), its result recorded; cutover per mod only when
  it agrees, or each disagreement is a named, explained difference (the Explosive Knockback compare at 872a7657e2: the
  journal says every in-game scene is UNRUN against 112 backfilled live rows; stage.json's `stage` is the Designer's inner
  step 5, a homonym; stage.json's blocked_on still names a refusal the lock lifted; 16 FIXED blind faults carry no judge verdict).
- `stage.json`, `journal.md`, `version/stage_record.json` become generated views or move to `archive_pre_ledger/` read-only.
- Every module writing them (designer_stage.py, coverage_judge.py, maturation*.py, maturation_now.py, concept_tree.py, ...)
  writes through `modledger append` instead, or is refused.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/modledger_cutover_accept.py ExplosiveKnockback GimmeSomeSlack FlowWorks`
— expected `PASS 13/13`. Watched failing at filing on 6a171f08f2: `FAIL 12 of 13` (every old store hand-written; 8
candidate writers outside modledger; only Explosive Knockback's ledger lint passed).

## criteria

- the acceptance test passes; the pipeline door tests stay green; nothing old is deleted (archived with provenance).
