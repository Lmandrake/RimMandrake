# Traps by topic

Lessons folded in from the lessons inbox, by the section of `../SKILL.md` they belong to.

## 1. Clean first — kill hostiles, then clear the ground

- **Never per-id kill a wild Boomalope on a paused game:** it ignites ~25 fires within 5 ticks. Clear wildlife with `jawa/destroy_bulk filter=factionlessAnimals` (no death, no fire).

## 5. The shot — light, weather, fog, UI, frame

- **OS-level screenshots (`system_screenshot.py`) capture whatever window is on top**, including the owner's terminals. For review shots use `rimworld/take_screenshot`, which saves under the game's own Screenshots folder.
- **`RM_LiquidLookProof.Tune` re-applies only the members of the liquid or fluid it names:** tune `RM_Liquid_Tar` for the pond (suite) and `RM_Fluid_Tar` for canal fill terrains, then read `RM_LiquidLookProof.Material` to confirm the real graphic colour before judging a screenshot.
- **Camera zoom is not predictable and it lerps.** `rimworld/set_camera_zoom rootSize` gives no predictable px/cell (9 and 7 both gave ~457 px/cell, 30 gave ~17); for any on-screen size measurement use `jawa/artboard_capture` with an explicit `ppc`. On tiers with `SimpleCameraSetting`, `set_camera_zoom` lerps, so a `take_screenshot` ~1 s later captures a mid-zoom frame (asked rootSize 6, got a 45-cell view): wait ~3 s, read `rimworld/get_camera_state` `viewRect`, shoot, and crop from that `viewRect` (cells = `viewRect.height-1` over the image height; ~101 px/cell at rootSize 6 on a 3467x1826 screen). `rimworld/frame_cell_rect` then `jawa/take_screenshot` frames reliably; `jump_camera_to_cell` + `set_camera_zoom` framed the wrong cells.
- **A paused pawn is drawn at a stale spot.** Vanilla `PawnTweener` (1.6) springs `DrawPos` toward the logical position at `0.09*deltaTime*60*TickRateMultiplier` per frame, so a walking pawn draws ~0.85 cell behind `Position` at any speed, and while PAUSED the tween freezes: `step_game_ticks` + capture shows pawns at stale spots. Any draw math keyed on `pawn.Position` but applied to `DrawPos` (pit sink clamp, wall-sunbathe fix) must key on the drawn position instead.
- **Drawbridge review staging.** A raised leaf draws as an upright post running N cells north of its hinge, so stations need at least leaf length + 2 cells between rows (6 apart overlapped; 8 is clean). Rebuilding on a `ProofResetRect`'d site leaves old leaf records (`ProofLeaf` still answers) and wreckage in the moat, and the new lowered deck did not draw (`ProofResetRect` also does NOT remove plants): restage on fresh ground. Put `review_label` centres ~12 cells west of a station at size small; medium labels at 4 cells covered the bridges.
- **Never use `jawa/set_fog action=unfogAll` on a modlist with NWN Real Fog of War.** On a 250x250 map it changed 62,500 cells, wedged the game for about 4 minutes (`Responding=False`, CPU climbing) and the fog came straight back, because Real FoW recomputes field of view per cell and re-applies its own shading; `unfogAll` clears only the vanilla fog layer. Real FoW has no enable/disable setting (27 tuning fields); its genuine full off switch is `onlyOutsideColony` in `Config/Mod_3391128917_RealFoWModStarter.xml`, which applies live (no restart) but only on `IsPlayerHome` maps. On the owner's list the fog is stripped by CAI 5000 (`krkr.rule56`) via `FogOfWar_DisableOnPlayerMap = True` in `Mod_3673768803_CombatAIMod.xml`; do not confuse it with `FogOfWar_Enabled = False` (CAI's own feature), and dropping CAI would remove the thing removing the fog. The `unfogAll`-before-capture advice elsewhere assumes no Real FoW.

## 8. The scripts this composes

- **A `--mock` rehearsal must write to its own folder.** `owner_review_stage --mock` and `live_session --mock` once wrote synthetic pictures over the live captures that an open item cited; point mock output elsewhere.

## This vs a review sheet — and why neither verdict is final

- **Before staging any owner look, read the item's whole family** (its caused/child items and the last week of OWNER notes naming the subject), not just the item. A NEEDS-YOU row is not current until its successors are checked: one staging showed the owner a build he had already ruled against while his newer spec sat unbuilt on a sibling item.

## 9. When a shot still comes out wrong — the checklist

- **Before offering any map for review, check that the running mod list matches the tier under review, then screenshot and READ the result yourself.** A map opened on the wrong tier's list never spawned its conduit, and the owner caught three visible defects the agent never looked at.

## 4. Placement — verify every cell is open and the right terrain

- **Review maps are numbered and dense (owner standing requirement).** (owner) "You should label and number these stations to make it easier to follow them BTW, this is a standing requirement." and "the sprinkler stations could all be shown much closer to each other so they can be reviewed much faster. This is what I mean by dense review rather than sparse." In any staged review save or sheet, put an in-world numbered label at each station matching the row list and pack the stations close, so he does not hunt coordinates across a sparse map. Structures that span something (bridges, ladders) are staged over pits, not on flat ground.
