# Player-truth sweep, second trial: wider set, and a truth baked into a fixer (2026-11-13)

Item RIMMANDRAKE_EXTEND_PLAYER_TRUTH_SWEEP_LADDER_WAS_ONE. Owner, 2026-11-12: "Let's re-examine Player truth sweep, yes,
run more trials perhaps. Maybe bake it into certain kinds of fixers as we already did today with the ladder."
Pilot: `design/RimMandrake/player_truth_testing_pilot_2026-10-26.md`. Ladder pattern: 029034d0ef (the truth "a hung
ladder meets its drawn wall face", swept over every depth x fill x rotation inside the submerge fix's own selftest).
Offline only. Evidence: `D:\ClaudeWork\rimmandrake\truthsweep_20261113\`.

## 1. Trial set and results

| Truth family | Instrument | Reach | Run time | Violations | False alarms |
|---|---|---|---|---|---|
| Ladders, pits, hoses, levelling (PT00-PT12) | `selftest_flowworks_stock.py --only 'PlayerTruth_*'` | FlowWorks | 274 s incl. build (PT10 62 s) | 0 (13/13) | 0 |
| Ladder art, pipe atlas (PT13-PT19) | `FlowWorks/Tools/selftest_player_truths_art.py` | 74 assets | 1.2 s | 0 (PT17's 156 seam jogs fixed since the pilot) | 0 |
| A creature is the same size from every side and does not hop when it turns | `art/facing_scale_lint.py gate --repo` | 744 of our creature pictures, all mods | 156 s | **16 open** (gate was green 2026-11-01, aaeefef442) | 0 of the 16 on an E/S/N look; 5 are small hops (0.035-0.07 of the canvas, tolerance 0.03) |
| Every thing has a picture (no magenta) | `art/texture_gap_lint.py` | 3,497 texPaths | 142 s | 0 (34 UNRESOLVED, allowlisted) | 0 |
| A creature turns when it walks (every facing wired) | `facing_art_census.py --check` | every PawnKindDef | 1 s | 0 | 0 |
| A ground texture tiles with no seam (new, trial only) | wrap step vs the texture's own neighbour step, probes bite | 50 repo TerrainDef textures | 3 s | 0 confirmed | 4 of 5 flags are panel floors whose edges are drawn on purpose; AB_Polymer has a faint 1 px border line, too small to file |

## 2. Where the violations came from

15 of the 16 facing flags are pictures installed after the 2026-11-01 green gate, by art-eval decisions the models
judged ACCEPT (the FACING_AUDIT_BUILD_REDRAW_BATCH (redraw the 169 failed creature facing sets) rounds and the
auto-judge timer). The 11-01 fixer (`facing_regen_batch.py`) held candidates to the gate's own check; the art-eval
runner never did: it showed the models an advisory 15% height-spread line and let them decide.

Replay of every committed creature ACCEPT since 2026-11-01 whose files still exist (58; 8 gone):
9 would now be refused, 7 of them on today's open list (Heemin, Vhakk, Vizhik, Neebray, Fanback V_C, Tarruq,
Mirrik). The other 9 open flags came from paths the runner does not see (reseat-less installs, a Graphic_Multi swap,
the night-horror lair art, an October bulk accept).

## 3. The fixer wired (03564e16cf)

`facing_scale_lint.truth(files, view, plan)` is the gate's own check (body-plan size band + feet row) on any files.
`art_eval/runner.evaluate()` runs it on a creature card's candidate set before any model call; a FLAG becomes a
deterministic REGEN (finding `F_FACING_TRUTH`, the measured fix in the prompt), ESCALATE at the round cap. Our art
only (view elevation), waivers honoured, UNMEASURED never blocks. Selftest
`art_eval/selftest_facing_truth_gate.py`: 13 checks, 7 watched failing on the base; three mutants (no feet row, no
waiver, no gate) each caught. On real art it agrees with the gate on all 744 pictures (50 FLAG, 694 ok).

## 4. Fixer kinds not wired, and why

- Pipe atlas fixers (`fix_pipe_*`, `fix_ns_end_caps.py`): 0 violations today, one-shot tools already applied.
- Terrain seam healer (`heal_tile_seams.py`): its truth found nothing real across 50 textures.
- `facing_scale_lint.py fix` / `reseat` and `facing_regen_batch.py`: already judge their output with the lint.

## 5. Filed

16 items, one per creature, each with an acceptance test that fails on the base (rc=1, watched): the RESEAT/RESCALE/
REDRAW items named for Heemin, Harvester, Skerrel, Vizhik, Murrin, Drazzik, Mynock, Neebray, Tarruq, Fanback V_C,
Brathek, Bulwark, Drommath, Mirrik, Prowler and Vhakk (`rimflow queue BENCH`).
