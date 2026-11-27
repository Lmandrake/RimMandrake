# Comparison strictness census — 2026-11-27

Item `RIMMANDRAKE_LOOSEN_REPEAT_COMPARISONS_TO_GAMEPLAY_FISH_TRIPPED`. Rule: `infrastructure/agents/CHARTER.md`
§A test is as strict as the harm it guards. One pass over the places that the brief names. The pass stopped when each
comparison found there had a class.

Classes: IDENTITY IS THE PROMISE · WRONG LEVEL · RIGHT LEVEL ALREADY · NOT REACHED.

## Count

| class | count |
|---|---|
| WRONG LEVEL (changed, test first) | 2 |
| IDENTITY IS THE PROMISE (one line added beside each, or the existing text already says so) | 6 |
| RIGHT LEVEL ALREADY | 17 |
| NOT REACHED | 8 |

## Census

### The bridge and the pipeline

| comparison | class | evidence | note |
|---|---|---|---|
| reset digest, the station part (`station_digest`, `_diffs`) | RIGHT LEVEL ALREADY | `src/RimMandrake/Utils/scene_repeats.py:55-82, 103-112` | It hashes what the stamp made: the op, the cell relative to the station, and the read-back fields that the plan asked for. Ids and absolute cells are left out. |
| reset digest, the mod part (`mod_digests`, `_diffs`) | RIGHT LEVEL ALREADY | `scene_repeats.py:85-112` | Each mod names its own per-scene state in its `[RMDigest]`. An unproven digest is never equal. |
| `jawa/mod_hooks` proof and reset (`dirty != clean`, `after == clean`) | RIGHT LEVEL ALREADY | `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchModHooksCore.cs:289-328` | It compares the digest that the mod chose. A reset promises to bring that state back to clean. |
| LuminousPigment `[RMDigest]` | RIGHT LEVEL ALREADY | `src/RimMandrake/LuminousPigment/Source/DeepfireTestHooks.cs:17`, `GameComponent_Deepfire.cs:84-87` | It digests the god-coat events and the impressed quadrum, which are counters that change play. It is the only mod hook. |
| `prove_scene_repeats.py` R1 and R2 (`rescue_outcome`, `judge_r1`, `judge_r2`) | RIGHT LEVEL ALREADY | `src/RimMandrake/bridgetools/prove_scene_repeats.py:100-148` | The victim lies in its own spot. A BREACH is a rescuer on the cell of another copy. |
| `prove_scene_repeats.py` R3 (`RESET_DIGEST_DIFFERS`) | RIGHT LEVEL ALREADY | `prove_scene_repeats.py:22-26`, `scene_repeats.py:149-176` | This is the mod digest above. |
| `jawa/rand_trace` and `rand_trace_verdict.py` (`part`, `verdict`) | IDENTITY IS THE PROMISE | `src/RimMandrake/Utils/rand_trace_verdict.py` docstring (line added) | It is an instrument. Its question is which draws part the stream, and it decides no bar and no resave. |
| plan `colony_drift_rand.py` (tracks on `Verse.Rand` `iterations` and `seed`) | IDENTITY IS THE PROMISE | `src/RimMandrake/Utils/scene_compare_plans/colony_drift_rand.py:1-3` (its docstring says so) | The plan is an experiment on the draw stream. It is not a test of a mod. |
| `scene_compare.compare` (PLAY against STEP) | RIGHT LEVEL ALREADY | `src/RimMandrake/Utils/scene_compare.py:30, 87-140`; `design/specs/2026-11-24-play-vs-step/boundary.md` §WHAT IS COMPARED | It compares the tracks that the plan names, and it names what may differ (`WALL`). The strictness is set by the plan. |
| the gate "an arm counts for a bar only when it was compared" | NOT REACHED | `src/RimMandrake/rimflow/scene_verdicts.py:164`; no program sets `compared` (`grep`: only `scene_judge.py:489` copies it) | Its design text asked for traces that agree, which nothing can give (below). That text is corrected. |
| `05_build_design.md` decision 2: "compared with the reference and agreed" | design text, corrected | `design/specs/2026-11-23-bridge-v2/05_build_design.md` §Decision 2 | "Agreed" now means agreed at the level of play: the scene's outcome and the state that its claim reads. Identical draws and identical steps of a pawn that the claim does not name are not asked. |

### Gimme Some Slack

| comparison | class | evidence | note |
|---|---|---|---|
| `proof_all.py` SL3, the floor cords (`V._cord_set`) | **WRONG LEVEL → changed** | `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py:905`, `src/RimMandrake/GimmeSomeSlack/validation.py` `_cord_set` | Before: the strand count and the CableTie count were compared. Both follow the curve that GSS takes again after a load. The run of 2026-10-22 had already cut the edge hashes and the geometry hash under his "Strike that". Readings are below. |
| `validation.py --triplet` (`run_triplet`) | NOT REACHED | no test table row runs it; `PROOF_HARNESS_BUILD_SAVELOAD_TRIPLET` is done | It reads the same `_cord_set`. So since `5e0a5db3` it also compares at the level of play. Its selftest (`src/RimMandrake/Utils/selftest_saveload_triplet.py`) passes 65 of 65. |
| `save_wire_down.compare` (`WD_reload_true_to_grid`, `WD_reload_live_dead_ends_equal`) | RIGHT LEVEL ALREADY | `src/RimMandrake/GimmeSomeSlack/northstar/save_wire_down.py` `compare` | It compares the cords by their two ends (`sorted(edgeHashes)` gives the names, not the hashes), each end live or dead, the pole links and the lamps. |
| `proof_all.py` SL3, aerial, mast styles, run styles | RIGHT LEVEL ALREADY | `validation_aerial.py:1793` `_aerial_set`; `validation_style.py:766, 793` | It compares the anchors, the link states, the fallen halves, the net groups, and the style and look that the player sees. |
| `proof_all.py` D1 (zero-tick re-reads) and D2 (fresh builder) | IDENTITY IS THE PROMISE | `proof_all.py:761-767` (lines added) | No tick passed, so a read must change nothing. The cache and a fresh builder are two paths that must give the same output. |
| `validation.py` D1 (fresh build) and M5 (local invalidation) | IDENTITY IS THE PROMISE | `validation.py:998-1004` (lines added) | A conduit built here must not lay again a cord that the player did not touch. That cord would move on the screen. |

### FlowWorks

| comparison | class | evidence | note |
|---|---|---|---|
| `proof_hose.py` SL3, the settled `geometryHash` | **WRONG LEVEL → changed** | `src/RimMandrake/FlowWorks/northstar/proof_hose.py` `sl3_verdict`; read whole by `src/RimMandrake/FlowWorks/validation.py:359-377` | Before: a reloaded hose had to lay on the same curve. Now: each hose that had a lay has one again, and no hose is lost or gained. Readings are below. |
| `proof_hose.py` SL3 scribed keys, SL4 carry states | RIGHT LEVEL ALREADY | `proof_hose.py:1079-1153` | It compares the ends, state, laid, flowing, transitions, look, style and the carry of each hose. |
| `validation_hose.py` H10 (`--save-load`, `_hose_set` with `geometryHash`) | NOT REACHED | `src/RimMandrake/FlowWorks/validation_hose.py:438-487`; no test table row, run by hand only | It still compares the curve. Do not use it for a verdict before it gets the SL3 level. |
| `validation_style_hose.py` R4 (`--save`, `_snapshot` with `geometryHash`) | NOT REACHED | `src/RimMandrake/FlowWorks/validation_style_hose.py:286-325`; run by hand only | The same as H10. |
| `sheet_overflow_proof.py` `SAVE_LOAD_CONTINUES_IDENTICAL` | IDENTITY IS THE PROMISE | `src/RimMandrake/FlowWorks/northstar/sheet_overflow_proof.py` `save_load` docstring (line added) | It hashes `RM_SheetMath.Save`, which is integer dL math with no draws. A load that does not continue that state exactly floods or dries other cells later. |
| `validation_v2.py` `E2_twins_identical`, `E2_rerun_determinism`, `G_every_cell_vs_oracle` | IDENTITY IS THE PROMISE | `src/RimMandrake/FlowWorks/northstar/validation_v2.py:1789` (lines added) | The kernel is deterministic. The kernel and its oracle are two implementations. |
| `live_session.py` B7 and `climb_proof.py` `save_reload_pockets_identical` | NOT REACHED | `src/RimMandrake/FlowWorks/northstar/climb_proof.py:54` (OWED, always UNMEASURED) | |
| `deep_lake_proof.py` `DL_save_reload_bowl_identical` | NOT REACHED | `src/RimMandrake/FlowWorks/northstar/deep_lake_proof.py:24, 44` (OWED) | |

### Explosive Knockback

| comparison | class | evidence | note |
|---|---|---|---|
| `scene_save_in_air.py` `SA_EACH_ONCE` (triplet over the census) | RIGHT LEVEL ALREADY | `src/RimMandrake/ExplosiveKnockback/proof/scene_save_in_air.py:81-107, 268-271` | It compares the staged ids, the duplicates and the stack counts. Where each thing lies is evidence and is not compared. |
| `validation.py` walk raid `A_RELOAD_NO_DUP_LOST` (triplet) | RIGHT LEVEL ALREADY | `src/RimMandrake/ExplosiveKnockback/validation.py:660-706` | It compares the ids that exist and the things that the load made. |
| `pawn_flight_saveload.py` | RIGHT LEVEL ALREADY | `src/RimMandrake/ExplosiveKnockback/proof/pawn_flight_saveload.py:87-103` | The pawn exists once and no flyer is left. |
| `map_agreement.py` (the model against the game) | RIGHT LEVEL ALREADY | `src/RimMandrake/ExplosiveKnockback/proof/map_agreement.py:1-15` | Each thing must end on a cell that the model allows, with the same pit state and the same covers. |

### Pyrelands

| comparison | class | evidence | note |
|---|---|---|---|
| `walk_small_live.py` `reload_verdict` (`sc_reload_keeps_the_burn`) | RIGHT LEVEL ALREADY | `src/RimMandrake/Pyrelands/walk_small_live.py:56-80` | It compares the fire cells within `RELOAD_FIRE_SLACK`, the fruit cells, and the scar within `SCAR_SLACK`. |
| `validation.py` `walk_digest` and `digests_match` (`sc_walk`) | NOT REACHED | `src/RimMandrake/Pyrelands/validation.py:4457-4508`; `sc_walk` was replaced by two small scenes (`design/concepts/Pyrelands/version/test_table.json`) | Its probe fields that a reload does not keep are already named and dropped. |

### WreckedMachines

| comparison | class | evidence | note |
|---|---|---|---|
| `study_survives_reload` (`timesDone` before and after) | RIGHT LEVEL ALREADY | `src/RimMandrake/WreckedMachines/validation.py:1223-1243` | |
| `wreck_stands_while_repaired_and_after_reload` (levels) | RIGHT LEVEL ALREADY | `src/RimMandrake/WreckedMachines/validation.py:1301-1319` | |
| `sc_old_save` | NOT REACHED | `design/concepts/WreckedMachines/version/test_table.md:76` (specified, not built) | |

**Pictures.** No live test of these five mods compares two pictures for exact equality. One pass looked for image
diff calls (`ImageChops`, `getdata` pairs, `array_equal`, picture hashes). The hits measure the colour of one picture,
or they come from art tools. None of them asks whether a picture is the same as before.

**Bars.** No locked bar of the five mods demands exact identity. The comparisons that changed are checks, not bars.

## Changed comparisons (Job 2)

| file | what must match now | red reading | green reading | commit |
|---|---|---|---|---|
| `src/RimMandrake/GimmeSomeSlack/validation.py` `_cord_set` (used by `proof_all.py` SL3 and `--triplet`) | which cords exist (each edge by its two ends), the node kinds, the conduit cells, the cord count, each end's cell, wall and live state, and the decals other than CableTie. May differ: `geometryHash`, each edge's hash value, the strand count and the CableTie count. | `selftest_proof_all.py` check 14 on the parent: the re-lay with the same ends FAILED (differs `decals, edgeHashes, geometryHash, strands`). On the change, each planted change of play FAILs: a cord gone, a live end read dead, a conduit cell lost, a fray gained, a grid node lost. | On the change, the same re-lay PASSes (differs `[]`). `selftest_proof_all.py` ALL PASS, `selftest_saveload_triplet.py` 65/65, `selftest_gss_small_scenes.py` 86/86. | `5e0a5db3` |
| `src/RimMandrake/FlowWorks/northstar/proof_hose.py` `sl3_verdict` | the scribed keys as before, and after the re-lay each hose that had a lay has one again, with no hose lost or gained. May differ: the curve of the re-lay (`geometryHash`), which is named as evidence in `relaidOtherCurve`. | `selftest_proof_hose.py` on the parent: "the settled re-lay takes another curve with the same ends" FAILED. On the change, these FAIL: a laid hose with no lay after the settle (`noLay`), a hose gone, and `Proof.save_load` with reel (2,1) still unlaid. | On the change, the other-curve case PASSes in `sl3_verdict` and through `Proof.save_load`. `selftest_proof_hose: PASS (0 failing)`. | `70390d63` |
| `src/RimMandrake/FlowWorks/northstar/selftest_falsepass_late.py` 8.2 (a repaired check) | SL3 compares the floor cord sets. It now reads the body `_save_load`; before, it read the wrapper `save_load`. | It was red on the parent, before this run's change, because the wrapper holds no `_cord_set`. A planted SL3 without `_cord_set` reads False. | It reads True on the real build, and the suite reads `all ok`. | `70390d63` |

## The tick-53 reading (Job 3)

**What was compared.** Three STEP runs of the plan `colony_drift_rand.py`, each from `rm_fixture_play_vs_step.rws` with the
random state written back and the fish shadow draws held off the stream
(`isolate=Verse.FishShadowComponent:MapComponentTick`), 300 ticks on ArchBig: the runs of
`design/specs/2026-11-23-bridge-v2/experiments/rand_trace_runs_isolated.json`. Their scene traces are still on disk
(`D:\ClaudeWork\rimmandrake\scratch\scene_runs\20261127T1005*_script_ArchBig_32280\trace_run_*.jsonl`), and each trace is
whole (`hands.trace_fault`: none). Compared with `scene_compare`, track by track, without the `Verse.Rand` tracks:
`Position` and `CurJobDef` of Human193, Human196, Human199 and Donkey12045, and the world tracks (weather, conditions,
temperature, hour, camera, windows).

**Reading.** The three runs part at the level of play. The first difference that the traces show is on offset 101 (tick
103): **Human196's position**. In run 0 Human196 is at (109,125), in run 1 at (109,124), and in run 2 at (110,123). The
rows at offset 51 (tick 53) read the same cell, (109,124), in all three runs. Next come the jobs: on offset 207, Human196 is on GotoWander in
one run and on Wait_MaintainPosture in another; on offset 256, Human199 the same. The other cast members and every world
track are equal through 300 ticks. So the input that parts the draws on tick 53 (one pawn enters a cell on another tick,
`rand_trace_result.md` point 5) has a consequence in play: the steps of a wandering colonist differ by one cell. The
consequence touches no staged act.

**Not compared.** These traces do not record health, things spawned or destroyed, or fires. The position rows in these
traces fall about 50 ticks apart. So this reading cannot place a difference closer than that. Why the rows fall that far
apart (the sample rate, or pawns that stand still) was not read. No new live run was started. These traces already decide the question (the runs part),
and a new run on ArchSmall would need the 26-mod list of the fixture and the new companion deployed there first. It
could move the first difference earlier, but it could not change the answer. The command for a run that also tracks
health and things: `python.exe src\RimMandrake\Utils\rand_trace.py --game ArchSmall --arms step --n 3 --window 300
--isolate Verse.FishShadowComponent:MapComponentTick --plan <a plan with those tracks> --out <json>` (UNRUN).

## Bars or design text that demand exact identity (for the Conductor)

- No locked bar of the five mods demands exact identity.
- Design text, corrected in this change: `design/specs/2026-11-23-bridge-v2/05_build_design.md` §Decision 2. It said that
  an arm counts after its traces "agreed" with the reference. It now says that the agreement is at the level of play.
