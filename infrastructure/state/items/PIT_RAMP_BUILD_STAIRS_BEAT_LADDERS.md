# PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS

Spec: `design/RimMandrake/relative_depth_climb_design_2026-10-12.md` §8.2 (player text, modifiers), §8.4 (ramps, ladders)
— build item 3 of three in §8.7. Builds on `PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS` (masks, ladder joins).

## state (BENCH, 2026-10-14) — built OFFLINE, live checks owed; ART OWED (placeholder in place)

Nothing deployed; the bridge was not touched.

**Built (FlowWorks):**
- `RM_PitRamp` ThingDef (Structure menu, 25 wood/stone blocks, work 900, not an edifice, rotatable; rotation = uphill) with
  `RM_Building_PitRamp` (spawn/despawn bump the climb generation; inspect line says what it joins) and
  `PlaceWorker_PitRamp` (dug square or dry pond bed; must face a square 1..span shallower; never on a ladder; ghost marks
  the facing square). `RM_PitRamp.Joins` feeds the cliff masks, the step floor, the step cost (flat walk) and the pocket
  grid (`RM_PitRamp.Pairs` → `RM_PocketGridMath.Label`'s ramp joins) — structural, every band, enemies too.
- Ladders: join their square to ANY shallower N/S/E/W neighbour (item 2), each level costing "Ladder slowness" normal
  climbs. Placement now needs a wall (a shallower cardinal neighbour) and refuses a ramp square; a dry pond bed counts as dug.
- Mod Settings (Pits section): "Ramps" (`pitRampsEnabled`, on), "Levels a ramp spans" (`pitRampMaxSpan`, 1–3, 3),
  "Ladder slowness" (`pitLadderSlowness`, 1–4, 2). Ramp settings re-derive pockets and masks. Registry: 117 toggles.
- §8.2 modifiers: `Patches/Canals/FlowWorks_ClimbAbility.xml` gives `RM_ClimbAbility` +1 to Megascarab, Spelopede,
  Megaspider, Monkey, Squirrel (climbers) and Hare, Snowhare, Cat, Lynx (leapers). PROVISIONAL list.
- Player text: the size table is in the "Pits trap by relative height" tooltip (item 1); a pawn standing in a hole now
  shows "Climbs out of steps up to K deep." FlowWorks has no pit guide entry to carry the table (none exists).
- Bridge: `RM_NorthstarProofs.ProofRamp("x,z;rot" | "x,z;off")`; climb_proof gains pit E and rows
  `CLIMB_ramp_frees_and_retraps`, `CLIMB_ramp_walk_out`.

Selftests: FlowWorks C# 318/318 (`Ramp_beats_ladder_and_both_join`, `Ramp_wiring_pinned_at_call_sites`); selftest_climb_proof
(ramp verdicts); settings registry + northstar 117.

## ART (owner needed)
The ramp draws vanilla's `UI/Overlays/Arrow` as a clearly-marked PLACEHOLDER (XML comment + "(Placeholder art.)" in its
description). Real ramp art (and its rotations) must go through the art ledger with the owner before ship.

## live checks owed (also in Transient/experiment_2026-10-14/live_worklist.md)
- `climb_proof.py`: `CLIMB_ramp_frees_and_retraps`, `CLIMB_ramp_walk_out` PASS (plus item 2's rows).
- Build menu: place a ramp facing the D 1 shelf (accepted) and facing D 0 from D 4 (refused, "1 to 3 levels"); a ladder in a
  pit's middle is refused ("against a wall"); the placeholder arrow rotates with the ramp.
- Load log: no XML/patch error from `FlowWorks_ClimbAbility.xml`; a cat's inspect pane in a D 2 hole says "up to 2".
- Owed by design (still UNMEASURED): raider never crosses a ramped moat over its wall; hauler fetches from a ramped floor.

## criteria
- O1 L0: ramp/ladder math + wiring selftests pass — done (318/318)
- A1 L2: ramp rows of climb_proof PASS live — OWED
- H1 L4: owner approves ramp art through the art ledger — OWED
