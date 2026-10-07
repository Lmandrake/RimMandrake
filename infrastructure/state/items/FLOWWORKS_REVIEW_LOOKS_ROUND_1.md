# FLOWWORKS_REVIEW_LOOKS_ROUND_1

Owner's review of the fresh FlowWorks review map (`RM_fw_review_20261006b`), 2026-10-06 ~19:00, typed mid-turn
(verbatim):

> Reviewing FlowWorks sheet: Dirty Oil looks EXCELLENT in the pit. Dirty slime as well. Scorched dirt and stone
> doesn't look like anything at all, it needs blast marks and blackened bits. The Stone Tar looks oddly blue. It
> should not be blue, it should be dark grey no matter what. Not transparent. Dirt tar should look the same as stone
> tar. I'm seeing strange words in the description like flooded channel and excavation pit. We should just list the
> water by depth, just like it does for riverbanks and shores. Deep, shallow, etc. Need many more of the fluids online
> here. Blood. Chemfuel. Astrofuel. White slime. Red Slime.

## Work
1. KEEP: dirty oil and dirty slime pit looks (approved).
2. Scorched dirt / scorched stone: add visible blast marks and blackened patches.
3. Tar: dark grey, never blue, opaque — on stone AND dirt alike (supersedes the 2026-10-06 mid-grey tint 0.58,0.56,0.60 where it reads blue/transparent).
4. Inspect/label text: drop "flooded channel" / "excavation pit" wording; name water by depth the way vanilla riverbanks and shores do (Deep / Shallow …).
5. More fluids online on the review map and in the mod: blood, chemfuel, astrofuel, white slime, red slime.
6. Rebuild the review map, screenshot and check it myself, save a new keeper, then show him.
7. Owner, 2026-10-06 (verbatim, added to this round): *"acid should be an eerie yellow-green and bubbling. slimes should lightly bubble too. Boiling liquid should bubble quite a bit."* — acid eerie yellow-green + bubbling; slimes light bubbling; boiling liquid heavy bubbling.
8. Owner, 2026-10-06 (verbatim): *"Make propane a medium-pale grey"* — propane's liquid colour becomes a medium-pale grey (hue/value only; keep its existing alpha).
9. Owner, 2026-10-06 (verbatim): *"people stuck inside a pit do NOT walk slowly... they walk at normal speed. Only when they are climbing in or out do they move slowly. Falling into a pit is FAST. Walking around within the pit is normal."* — a move between two cells of the SAME depth costs normal; only a move that changes depth (climbing in/out, ladder included) is slow; a forced fall in is fast. Pit hold / ladder behaviour unchanged.
10. Owner, 2026-10-06 (verbatim): *"Is it possible to still show the pit walls/floor beneath the translucent water? That would be MUCH more effective than just a blue liquid surface."* — feasibility first; if cheap, keep the pit floor + walls drawn (depth-shaded) under a translucent liquid layer per liquid (water clear-ish; slime/tar/oil stay opaque; tar opaque dark grey).
11. Owner, 2026-10-06 (verbatim): *"And when something falls into a covered pit, of course it is no longer covered"* — any fall through a pit cover (pawn now; items/corpses later via Explosive Knockback) leaves the cover broken/removed. Verify; test if already so, fix if not.

## Offline pass (BENCH helper, 2026-10-06) — built, NOT deployed, nothing seen live yet
- 2 scorch: blast-mark starbursts on the floor and on the ground round the rim, near-black patches, stronger/wider rim ring (`RM_ExcavationWalls`, numbers in `RM_WallFaceMath`).
- 3 tar: was the vanilla WATER shader — blue depth ramp under any tint, blending with the ground beneath (why soil and granite tar differed). Now the opaque Flow shader (as the approved oil/slime) with an R=G=B dark-grey tint.
- 4 labels: every fill tier is "shallow / chest-deep / deep / very deep <liquid>"; dry cuts "shallow pit / pit / deep pit / very deep pit"; no "channel"/"excavation" left in any canal terrain text.
- 5 fluids: new canal FluidDefs RM_Fluid_Blood / _Chemfuel / _Astrofuel (fuels detonate; blood does not burn) with fill ladders and looks; review map visuals +5 stations (39) incl. white and red slime. Mod Settings: per-liquid "can fill a cut" toggles (refused at `TrySetDriverFill`).
- 7 bubbles: `RM_Fleck_LiquidBubble` (Biotech vat bubble, tinted) thrown by an in-view emitter; acid yellow-green + bubbling, slime light, boiling heavy. Settings: on/off + density.
- 8 propane: medium-pale grey on a plain white texture, water shader unchanged.
- 9 pit walking: `RM_PitStepCost` — a dry step at one depth costs nothing extra, a climb costs the deeper cell's dry cost, a drop into superdeep is free (falls were already instant teleports). Route planning unchanged. Setting `pitWalkNormalEnabled`. Runner depth_fill expectation updated (JawaBench source only; rebuild owed at next shutdown window).
- 10 see-through: feasible and built — for liquids with `seeThrough` > 0 the cut's floor (depth-darkened) and drowned far face are redrawn semi-transparent OVER the liquid terrain (the occluder was the liquid's own terrain replacing the floor). Water 0.55, acid 0.35, fuels 0.25–0.35; tar/oil/slime/blood 0.
- 11 cover: already true — `Spring` destroys the whole deck before any faller descends; flyer landings need an open pit. Pinned by `selftest_flowworks_cover_breaks.py`.
- Live look owed (step 6): deploy, rebuild the review map, screenshot and check before showing him.
