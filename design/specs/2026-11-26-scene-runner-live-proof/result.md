# The shared scene runner, live: same verdict rows as knockback_runner.py, fewer bridge calls

Item: `RIMMANDRAKE_PROVE_SCENE_RUNNER_LIVE_SAME_ROWS_FEWER_CALLS` (child of `RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE`).
Run on ArchSmall, 2026-11-26, on the `explosiveknockback_visit` tier, with the Explosive Knockback PROOF build
(`-p:RmProofs=true`, source d48ab953ad8e) and the JawaBench companion built from this change. Each pair ran on one
quicktest map: the new arm first (it reloads its scene-begin save after itself), then the old arm on that same map.

The check: `python3 design/specs/2026-11-26-scene-runner-live-proof/compare.py` (exit 0 holds). It goes red on a flipped
status, a dropped scene, more calls in the new arm, an old INVALID against a new PASS, an unverified reload, and on the
cut evidence of pair 1 (`compare.py design/specs/2026-11-26-scene-runner-live-proof/evidence/pair1_cut_evidence`).

## Result (pair 2, 01:24 to 01:25 PST: `evidence/`)

| scene | knockback_runner.py | scene_runner.py |
|---|---|---|
| storeroom_bomb_pit | PASS | PASS (VERDICT), and OUTSIDE haulables on the pit rows = 2 >= 1, PASS |
| storeroom_bomb_pit_control | PASS | PASS |

| arm | bridge calls | wall time |
|---|---|---|
| old: `knockback_runner.py --scenes storeroom_bomb_pit,storeroom_bomb_pit_control --ticks 900` | 302 (285 `jawa/mod_settings_field`, 9 `jawa/static_call`, 8 `jawa/safe_advance`) | 34.7 s |
| new: `scene_runner.py --type RimMandrake.ExplosiveKnockback.RM_KnockbackScenes` | 17 (1 `jawa/run_scenes`; the other 16 are the scene-begin save and its verified reload) | 18.5 s (save 4.5, run 5.3, reload 8.7) |

- The two verdicts agree clause for clause: east, south, goods, container, heavy, pit and cover are True in both arms.
  Only thing ids, the launch tick and the launched pawn's mass and impact differ, as two fresh stagings do.
- The Outside row (a vanilla count of haulables on the pit rows) agrees with the main verdict's `pit=True`.
- Pair 1 (01:09 to 01:12 PST, `evidence/pair1_cut_evidence/`) gave the same statuses: old 302 calls in 35.3 s, new 15 calls
  in 14.2 s. Its new-arm evidence was cut (second fault below).
- The new arm's time is mostly its save and reload, which the old arm does not do: the old arm leaves the map changed.

## Faults found and fixed in this run

1. The scene-begin save was refused (`evidence/new_arm_first_try_save_refused.txt`, `NO_RUN`). `scene_snapshot.py` saved
   through `test_site_saves.save_site`, which expands the compressed thing grid to make a portable fixture. The expand
   refuses a map that holds a modded compressible def (hash 64117 on this tier) and deletes the save. A scene snapshot is
   reloaded in the same session on the same list, so it needs no expand: `save_site(..., expand=False)` keeps the grid as
   the game wrote it, and `scene_snapshot.py` passes it. Red, then green: `selftest_scene_snapshot.py`, "a snapshot of a
   map with a modded compressible def saves, kept as written".
2. The verdict's evidence was cut at 400 characters (`JawaBenchSceneRunnerCore.Clip` on every row's measured and
   cause, a text cut that named no danger). Pair 1's new-arm JSON lost the container, heavy, pit and cover clauses that
   its PASS rests on. The row table now keeps measured and cause whole; `Clip` stays only on the tools' refusal and
   exception messages. Red, then green: `selftest_scene_runner_core.py`, unit `verdict_and_row_evidence_kept_whole`.

## Evidence

- `evidence/new_arm.json`, `evidence/new_arm.txt`: scene_runner.py's report and its printout.
- `evidence/old_arm.jsonl`, `evidence/old_arm.txt`: knockback_runner.py's run (rows and journal) and its printout.
- `evidence/old_arm_calls.json`: the old arm's calls by tool, counted by `count_old_arm.py` (it wraps
  `RimBridge.call` and runs knockback_runner.py unchanged).
