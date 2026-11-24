# Experiment A: result of the live run, 2026-11-23

Item `RIMMANDRAKE_RUN_BRIDGE_EXPERIMENT_PYTHON_ACT_AGAINST_IN_GAME_ACT`. Design: `08_where_tests_live.md`, "The experiment".

Game: ArchSmall, tier `flowworks` (13 mods), a quicktest map (temperate forest, 250 x 250), 5:46 PM to 6:23 PM PST.
Loaded companion, read from `jawa/companion_handshake` in the running game: build `6ac9a7490885`, which contains the
slice `5cebf3567fe1` with no change to its two files; profile `test`. Numbers per run: `exp_a_evidence.json` beside this
page. Full traces: `D:\ClaudeWork\rimmandrake\scratch\bridge_exp_a\`. Each number below is measured unless it says
`[guess]`.

## Answer

**The tick is the same. The result is not always the same.** An act from Python on a paused game lands on its tick and
its effect is seen on the next tick, every time. When the act writes FlowWorks ground, the game's verdict in the next 32
to 40 ticks is different: the pit "holds" the pawn at once, and in running play it holds the pawn up to 60 ticks later.
The difference is the paused frame after the act. A bare pause (no act in it) changes nothing.

| arm | scene | against the act inside the game |
|---|---|---|
| P, act from Python on the paused game | 1, a cut on a colonist | **same tick**: 20 of 20 |
| KP, act inside, then a bare pause | 1 | **same tick**: 20 of 20 |
| P and KP, whole state of three colonists | 1 replayed from one save | **not decided** (below): the in-game arm does not repeat itself |
| P, dig on the paused game, 20 to 30 ticks after an earlier dig | FlowWorks pit | **different**: 14 of 14 against 0 of 11 |
| RP, dig on the running game, then a bare pause | FlowWorks pit | **same** as running: 0 of 13 |
| P, the same dig 200 ticks after the earlier one | FlowWorks pit | **same** verdict: 4 of 4 (rebuild at +0 against +1) |
| P, kill on the paused game whose blast destroys a ramp in a later tick | FlowWorks ramp | **same**: 6 of 6 against 6 of 6 |

## Scene 1: the tick

Offsets from the start of the run. The cut is asked for at +60 and the run ends at +200.

| arm | speed | trials | act | injury first seen at the end of | end | wall time, median (range) |
|---|---|---|---|---|---|---|
| K, inside the tick | Normal | 10 | +60 | +61 | +200 | 3.55 s (3.45 to 3.78) |
| P, from Python | Normal | 10 | +60 | +61 | +200 | 4.06 s (3.66 to 4.30) |
| KP, pause only | Normal | 10 | +60 | +61 | +200 | not timed |
| K | Ultrafast | 10 | +60 | +61 | +200 | 0.44 s (0.39 to 0.57) |
| P | Ultrafast | 10 | +60 | +61 | +200 | 1.01 s (0.93 to 1.15) |
| KP | Ultrafast | 10 | +60 | +61 | +200 | not timed |
| **planted**: P one tick late | Normal, Ultrafast | 3 + 3 | +61 | +62 | +200 | red in 6 of 6 |

- The clock did not move in any pause. One act costs about 0.5 s of wall time: 164 ms (74 to 181) of paused game at
  Normal and 95 ms (71 to 157) at Ultrafast for three calls (read the tick, act, read the tick), the rest is the second
  run's start, status polls (0.3 s apart) and trace read. P makes 8 calls, K makes 3.
- Why 10 trials at each speed: the decision rule of `08` asks for 20, and one disagreement would end the tick claim. Ten
  agreeing trials show a fault that always happens; they do not prove equality. "End" agrees by construction (the run's
  own condition names the tick). "Seen" is the reading that can fail, and the planted fault shows that it does.

## Scene 1, replayed from one save: state

One save, loaded before each run, the random seed set to one number, 23 tracks (cell, job, injuries, hunger, rest of three
colonists) compared tick by tick. 11 K, 10 P, 10 KP, 3 planted P1. Why 10: enough pairs to see a difference larger than the
noise that K shows against itself.

| pair | pairs | differ before the act | differ at +61 or +62 | differ later | never |
|---|---|---|---|---|---|
| K against K (the noise) | 55 | 0 | 34 (62%) | 14 | 7 |
| K against KP | 110 | 0 | 68 (62%) | 36 | 6 |
| K against P | 110 | 0 | 83 (75%) | 25 | 2 |
| K against P1 (planted) | 33 | 0 | 33 | 0 | 0 |

- **This scene cannot decide the state question.** The cut that the slice makes rolls dice (one cut makes 1 to 5
  injuries), and the dice are drawn on frames also, so the in-game act does not repeat itself from one save and one seed.
- Injuries per cut, unseeded (scene 1's own runs): K 3.14, KP 2.68, P 2.86, 28 runs each. P against the two in-game arms
  together: no difference (shuffle test, p = 0.89). In the seeded replay P gave more (2.6 against 1.75, p = 0.011); the
  two sets together p = 0.34. I read the seeded reading as one seed and a different count of frames drawn before the act
  `[guess ~75%]`.
- No run differed before the act. A verdict that depends on a dice roll is not repeatable in **either** route.

## FlowWorks: the state after the act differs

The scene (`exp_a_state_after_act.py --scene pocket`): a person of no faction stands stunned; a cell 4 cells away is dug;
20 to 30 ticks later the person's own cell is dug 4 notches deep. Arms: **R** the dig call lands on the running game,
between two frames (no paused frame sees it); **RP** the same, then a bare pause; **P** the dig on the paused game. The reading
is `RM_NorthstarProofs.ProofTrap` (held) and `RM_PocketGrid.ProofEdge` (tick of the last grid rebuild).

| arm | runs | held at the first read (+4 to +27 ticks; P +10) | held at +100 | grid rebuilt, ticks after the dig |
|---|---|---|---|---|
| R, Normal | 10 | **0 of 10** | 10 of 10 | +33 to +38 |
| RP, Normal | 11 | **0 of 11** | 11 of 11 | +32 to +38 |
| P, Normal | 11 | **11 of 11** | 11 of 11 | 0 |
| R / RP, Fast | 1 / 2 | 0 of 1, 0 of 2 | 1, 2 | +11 to +27 |
| P, Fast | 3 | 3 of 3 | 3 | 0 |
| quiet (last rebuild 200 ticks earlier): R / RP / P | 4 / 4 / 4 | all held | all held | +1 / +1 (one +0) / 0 |

- Runs, not chance: 11 of 11 against 0 of 21 with no overlap. The quiet rows are the control that the reading is not blind:
  there the three arms give one verdict.
- The mechanism is the code that was read beforehand (`RM_PocketGrid.UpdatePaused`): a ground write made on a paused
  game is rebuilt on the next paused frame; a write made in running time waits until 60 ticks after the last rebuild.
- Void runs are not counted and are marked: 1 R at Normal and 2 R + 1 RP at Fast (plus the first Fast set, 3 R and 3 RP,
  overwritten), because the call landed after the run had paused. At Fast, Python hit its tick 0 times in 6. This is the
  known limit of a Python act on a running game.
- A wall-time comparison does not apply: 2.9 to 4.4 s per run in all three arms. The dig call took 72 to 130 ms.

**An act really inside the tick** (`--scene blast`): the slice's own cut kills a boomalope at +20; its blast destroys a
pit ramp on the next tick. K (killed inside the tick) and P (killed on the paused game): the ramp was gone at +21 in 12 of
12, and the last grid rebuild was 60 ticks after the ramp was placed, not at once, in 11 of 12 (the twelfth, a K run, had a
later change and a second rebuild at +120; its first is inferred from the count). So a ground write made inside a tick is throttled as R's is, and an act from Python is harmless when the
FlowWorks write happens in a later tick. The difference needs a write made **while the game is paused**.

**The two hands that repair it** (added 2026-11-23, after `jawa/run_until` was built; SteveDesktop, tier `flowworks`, testq job
`J20261124T061237Z-8f43fd`, `--arms P,G,T --trials 3`, Normal). G: the dig is an act at 0, done in the hop that starts the clock. T:
the dig is an act on a tick inside one run.

| arm | runs | held at +10 | held at +100 | grid rebuilt, ticks after the dig |
|---|---|---|---|---|
| P | 3 | 3 of 3 | 3 of 3 | 0 |
| G | 3 | **0 of 3** | 3 of 3 | +40 |
| T | 3 | **0 of 3** | 3 of 3 | +40 |

Both read as running play does. A batch alone on this scene was not run.

## What it means for the held ticket

1. The tick claim stands. Nothing here asks for the whole in-game scene player (`RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`):
   keep it held.
2. The state claim is false for one scene shape: an act that writes FlowWorks ground, read within 60 ticks. By the decision
   rule of `08` that part goes into the game. The smallest piece is one generic choice in
   `RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH`: acts that are **done in the same main-thread hop that unpauses the
   game** (act and go), and acts on a named tick inside the run. Both carry any present tool call, no scene and no verdict.
   The R arm shows why it works: the first frame that FlowWorks sees is not a paused one.
3. `jawa/act_batch` alone does not repair it: the batch is done on the paused game, and the next frame is still paused
   `[guess ~90%, from the code and the P arm; not run]`.
4. Until then: a scene that acts on FlowWorks ground waits 61 ticks before it reads, or is recorded as an act on the paused
   game and not counted. Scenes whose act is a pawn, a thing, an explosion or a job show no difference here, on
   one scene each (20 trials, and 6 runs per arm).
5. Today's FlowWorks proofs stage digs with `jawa/flowworks_excavation_drive` on a paused game, so they read a pit that
   already holds. Whether any verdict of theirs sits inside those 60 ticks is unmeasured.

## Faults found in the script, fixed test-first in this run

- **Every trial would have read DIFFER.** The first sample of arm P's second run, read on the paused game after the act,
  was counted as the end of tick +60. Three selfcheck cases with traces as the slice writes them (red before, green after):
  12 of 12.
- **Blind from trial 4.** 4 points of cut, three arms, ten trials on one 40-point torso. The pawn is healed before each arm.
- Asking for a quicktest map in a running game waits out its 280 s timeout. The map is now asked for only from the menu.
- New: `--late 1` plants the fault. New file `exp_a_state_after_act.py`, selfcheck 4 of 4.

## UNRUN

| part | why | command |
|---|---|---|
| 2, the Knockback storeroom pair | needs the PROOF build deployed | `python.exe src\RimMandrake\ExplosiveKnockback\knockback_runner.py --scenes storeroom_bomb_pit,storeroom_bomb_pit_control`, then `python.exe src\RimMandrake\Utils\scene_runner.py --type RimMandrake.ExplosiveKnockback.RM_KnockbackScenes --out ...\exp_a_runscenes.json` |
| 3, two cuts on one tick, two calls against one batch against in the game, the fill of ten ticks | needs the act batch and acts on a tick (the widened slice) | no script yet; the pit scene above is its one-act half |
| 4, 500 reactions | needs the bounded rule | no script yet |

Re-run of what ran (ArchSmall; hold its lock; `$S` is any Windows folder):

```
python.exe exp_a_python_act_vs_kernel_act.py --trials 10 --out $S\normal            # --speed Ultrafast; --late 1 = planted
python.exe exp_a_state_after_act.py --scene replay --trials 10 --out $S\replay
python.exe exp_a_state_after_act.py --scene pocket --trials 6 --z0 90 --out $S\pocket   # --quiet --trials 4 --z0 130
python.exe exp_a_state_after_act.py --scene pocket --trials 5 --slack 20 --z0 190 --out $S\pocket_slack
python.exe exp_a_state_after_act.py --scene pocket --trials 3 --speed Fast --slack 25 --z0 30 --out $S\pocket_fast
python.exe exp_a_state_after_act.py --scene blast --trials 6 --ramphit 51 --x0 57 --z0 75 --out $S\blast    # burns the map
```
