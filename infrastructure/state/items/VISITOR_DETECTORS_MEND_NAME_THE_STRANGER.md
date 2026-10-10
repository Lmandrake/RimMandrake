
## spec

Map awareness phase 1 (Python harness). Design `Transient/foundry_map_awareness_design_20261010.md`, reviews
`..._review_opus_20261010.md` / `..._review_gpt_20261010.md` (Transient, ~14 days). Owner decisions by question card
2026-10-10: build the full programme; an unexpected visitor in a validation/north-star run is RECORDED and REMOVED
and the run carries on, a redo only on EVIDENCE of disruption (CLEAN / DISRUPTED / INDETERMINATE).

Built (offline, `src/RimMandrake/Utils/modcheck/`): bounded per-test expectations (`max_count`, never by mod
package); `strangers_near_anchor`/`hostile_pawns` text names id/kind/faction/state; `player_joiner`,
`pawn_arrived` (set diff), `pawn_state_changed` (recruit/tame); `contract.py` (RunValidity, disruption
evidence, spawn receipts); `watch.py` owner rule; `scene_report.py` (batched first look); `helpers.quiet_world`
(+ logRaidInfo, wild-spawner block when the companion has it, read-back); `skills/rimbridge/references/first_look.md`.
Selftest `modcheck/selftest_awareness.py`.

## criteria

- A1 L0: selftest_awareness.py green (owner rule, receipts, set diff, joiner, recruit, bounded contract, scene report, quiet world)
- A2 L2: live on a quicktest map, a substituted spawn's receipt shows requested vs actual from an independent read (MAP_AWARENESS_PROVE_ON_A_QUIET_MAP)
- A3 L2: live, abort_proof's hostile_raid case records + removes the visitors and the run stays CLEAN; the predator case ends DISRUPTED
- A4 L2: live, scene_report.py on a map with a manhunter and a player joiner prints both with decomposed hostility and origin unknown
