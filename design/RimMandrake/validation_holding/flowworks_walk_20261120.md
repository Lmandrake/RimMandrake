# FlowWorks walk of 2026-11-20 (HELD, not yet ingested into any validation ladder)

Item: RIMMANDRAKE_SORT_FLOWWORKS_WALK_REPORT_KNOWN_OR_NEW (a detached BENCH helper of the Conductor, 2026-11-20). Format and
rules: `README.md` here. Sorted offline: nobody touched the game, the bridge, the Mods folder, ModsConfig or his saves.

- **Save:** `FLOWWORKS_OWNER_REVIEW_VISIT2_FULL_20261119_2327` (Saves folder, not in the repo), staged by
  `src/RimMandrake/FlowWorks/northstar/owner_review_stage.py`; staging log
  `design/concepts/FlowWorks/version/in_game/visit_2/evidence/owner_review_stage_full.log`; the 64 stations:
  `D:\ClaudeWork\rimmandrake\stage_fw_walk\stations.txt`.
- **Build:** deployed FlowWorks = origin/main of the walk morning (deploy dry-run "in sync", DLL source stamp MATCH); the DLL
  is the 2026-11-19 13:35 build. Four commits after the save touch only tests and the test scene (pre-walk page).
- **Mod list:** 316 active mods, camera zoom mod and all five DLC in (`D:\ClaudeWork\rimmandrake\stage_fw_walk\progress.md`,
  06:20 check) [measured].
- **When:** he walked between 06:29 PST (staging done, progress.md) and 06:41 PST (his six pictures were saved 06:41:09;
  the sort item was filed 06:42:51) [measured]. The brief's "about 7:25 AM" does not fit those times.
- **Pictures:** `flowworks_walk_20261120/1.png` .. `6.png` here (copied; the source folder is temporary). 1 = stations 5 and
  6 · 2 = stations 17, 18, 19 · 3 = the steam geyser above stations 20 to 22 · 4 = stations 7, 8, 9 (one side drained) · 5 =
  station 33, a colonist lying in 2 m of water · 6 = station 47, a colonist on the plank cover. A seventh picture (a pit with
  "-5" marks, saved 06:55) came after this brief and is not sorted here.
- **The black frame round every station is the pit's own outline**, not a marker of the review scene: `Outline()` in
  `src/RimMandrake/FlowWorks/Source/Superdeep/RM_ExcavationWalls.cs:216` draws it black on every pit edge (setting
  `pitOutlineEnabled`, thick on the south lining); the stage script draws only the number signs [measured].

## His words, verbatim

> [Image #1] There appears to be a pale rectangle superimposed over the pit wall art, prominent in spikes wet. Not a good look. [Image #2] Water has somehow managed to become too transparent again. Barely reads at shallower depths. And the 0.2m still shows 0.5m depth upon hover over. [Image #3] Why do steam geysers have this pale area surrounding them? It's ugly. Stations 9 & 10 would be more effective if you had two different heights of water on either side of the closed sluice gate that I could open and watch normalize. 1-16 your signs are fine, zooming in changes so that the signs do NOT overlap the ladder. 7-16: No, the water should be more legible (less transparent). [Image #4] In this shot I drained out the liquid on one side of each closed sluice gate. The water was still shown extending past the Sluice gate but no further (occupying the same block as the Sluice and a bit beyond, rippling actively). I then opened the sluice gate and it correctly equilibriated the water. 21/22: I think we need a full design pass on what water SHOULD be in Rimworld. Color, transparency, waves... I need some help getting this right as a function of depth. 25-27: Style is not right. Stations are all set to scrapper. Changing one of the elements to other styles works, but does NOT propagate to everything along that line as it should. [Image #5] "wetted" graphic on pawns looks ridiculous (clearly placeholder, just two blue regions superimposed) 30: happy to report that "walking around" a pit now works sensibly. 42 vs 47. 42 is a 2m deep pit with a ladder. Pawn "walks" path through the ladder, slows down over ladder correctly, then enters pit. For 47, same setup without ladder. But the ground is pale for some reason. Pawn walks directly over same walls quite fast, removing the need for a ladder at all and making it seem wasteful. OH!! It's a covered pit. That's broken then... [Image #6] Here look at the covered pit 47. Reads like the surrounding ground (good!) but there's clearly the pit graphic remaining, the very thing that should be obscured (walls/outline). And character walking on the cover does not cause it to collapse, clearly. Bridges 48-58 actually look pretty good! NOTE: should check with explosive knockback to see if the railings on the bridge do indeed prevent you from getting blown over them: that's their entire reason for existence other than look. Item 60 Jetty doesn't seem to exist nor does 59 steel jetty.

## His points, one observation per row

Classes: MOD WRONG · SCENE WRONG (the review map's staging failed) · CHECK OR SIGN WRONG · APPROVAL · REQUEST · BY DESIGN (the
mod does what its design says; his words question the design). Tags: [measured] = the code path that produces it was read;
[guess ~N%] otherwise. All file paths are under `src/RimMandrake/FlowWorks/` unless they start with `src/` or `design/`.

| # | station | what he saw | class | known or new | likely cause | next |
|---|---|---|---|---|---|---|
| 1 | 5, 6 | A pale frame lies over the pit's wall art; strongest in the wet spikes pit. | MOD WRONG | NEW → RIMMANDRAKE_DIM_FLOWWORKS_DROWNED_WALLS_PALE_FRAME_IN_WATER | The drowned wall strips are drawn opaque and lit with a cream wash (colour 255,248,232 at the wall-light alpha) under the water sheet, and `SideUnder` draws its face and wash the full cell height but its sheet only up to `wetTop`, so the north corners stay lit and unsheeted (`Source/Superdeep/RM_ExcavationWalls.cs:512`, `:547-550`) [measured]. That this is all of the pale frame he saw [guess ~60%]. | fix item |
| 2 | 17-19 | Water is too transparent again; shallow water barely reads. | MOD WRONG (a look) | KNOWN: RIMMANDRAKE_TUNE_WATER_CLARITY_DARKER_AND_HALF_AS_OPAQUE. Its text asks for the opposite direction (half as opaque), so it does not cover this | Nothing changed since his 11-13 approval: the law (`Seen`, `Source/Superdeep/RM_UnderLiquid.cs:173`; deep opacity 0.90 at 4 m, curve power 1.4, fresh water seeThrough 0.45) is commit 9a5bbf7a66 of 11-12 21:22, inside the fe7c271f4b build he approved; later commits only add functions and a finer level note [measured]. His FlowWorks settings file holds no under-liquid key, so the defaults run [measured]. The law hides 6% at 0.2 m, 15% at 0.5 m, 30% at 1 m, 56% at 2 m, 90% at 5 m [measured, computed from the constants]. What depths the 11-13 save showed him: not recorded (no capture) [unknown]. Today's map shows 0.5 m and 1 m side by side on pale arid ground, where 15-30% of a dark sheet reads as grey [guess ~60% that this, not a change, is why it reads worse]. | open for him: the water design pass (below) |
| 3 | 17 | The "0.2 m" strip says 0.5 m on hover. | SCENE WRONG | KNOWN (pre-walk page; the staging log's NOTE readouts: "Hole 0.5 m · Water 0.50 m" on all 5 squares) | The readout is right for what the scene built: every square is a 0.5 m hole with 0.5 m of water [measured]. | builder item RIMMANDRAKE_RESTAGE_FLOWWORKS_REVIEW_SIGNS_OVER_UNBUILT_SCENES |
| 4 | above 20-22 (also inside 21's water) | A ring of pale whole squares round a steam geyser, paler squares inside it. | MOD WRONG (whose mod: unknown) | NEW → RIMMANDRAKE_TRACE_FLOWWORKS_GEYSER_PALE_RING_NOT_STEAM | Not steam (steam draws round puffs that drift; this is whole squares that stay). Not FlowWorks: no FlowWorks code draws or writes ground round a geyser on undug ground; its geyser code is for sunk geysers only (`Source/Superdeep/RM_GeyserPit.cs`, `RM_SubmergeDraw.cs`) [measured]. It shows over station 21's water sheet (render queue 2449), so it is an overlay drawn late, not a terrain [guess ~70%]. Its size matches EnvironmentalHazards' vapor-column field (radius 6 round every steam geyser, `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_VaporColumns.cs:59`), but that field has no drawer [measured]. | one live read: hover a ring square, read its terrain line and the active overlays |
| 5 | 9, 10 | Asks for two water heights on either side of a closed sluice, to open and watch level. | REQUEST (scene) | NEW | — | builder item |
| 6 | 1-16 | The signs are fine; zoomed in they do not overlap the ladder. | APPROVAL | settles the label half of RIMMANDRAKE_JUDGE_FLOWWORKS_REVIEW_MAP_LABELS_HIDE_THEIR_PITS | — | close that item (its sprinkler half is #11 and #12) |
| 7 | 7-16 | "No": the water in the canals should be more legible, less transparent. | MOD WRONG (a look) + answer | KNOWN as #2. Reads as his answer "No" to q1 of RIMMANDRAKE_JUDGE_FLOWWORKS_REVIEW_SAVE_FOUR_LOOK_QUESTIONS (does the dry canal read as a low wall?) [guess ~70%] | Same law as #2: 1 m of water hides 30% [measured]. | confirm the q1 reading once; design pass |
| 8 | 7-9 | With one side drained, water still shows on the gate's own square and a little beyond, rippling. | MOD WRONG | KNOWN: RIMMANDRAKE_SEAL_SLUICE_AT_ITS_PANEL_NOT_ITS_SQUARE. Same cause; its text names only the opposite case (gate square dry inside a full pit) | The kernel seals the gate's whole square: "a square liquid neither enters nor leaves this pulse" (`Source/RM_FlowKernel.cs:438-442`), so the square keeps whatever it held: dry on 11-14, wet today [measured]. The "bit beyond": the drained neighbour's wall band drawn at the gate square's level [guess ~50%]. | note on that item |
| 9 | 7-9 | Opened, the gate levels the water correctly. | APPROVAL | bar `sluice_drains_on_command`; no open item names it [guess ~80%] | — | record only; note on the sluice item |
| 10 | 21, 22 | Asks for a full design pass on water: colour, transparency, waves, by depth. | REQUEST (design) | answers q2 of the four-look item (5 m brighter than 2 m) by deferring it to the pass | — | OPEN FOR HIM (below); not filed as work |
| 11 | 24-27 | All four sprinkler stations wear Scrapper. | SCENE WRONG | KNOWN that the looks failed (pre-walk page); the cause is new | The scene's look pick never matched: `objects_sheet.choose_look(run=True)` keeps only menu rows that contain "whole connected run" (`northstar/objects_sheet.py:175`), but since PIPE_STYLE_PRUNE_WHOLE_RUN_ONLY the pipe menu rows read just "<Look>" (`Source/Machinery/PipeLook.cs:181`), so nothing is picked and every net keeps the default look [measured]; the log reads "asked Futuristic, game reads None" for all four. That the default look draws as Scrapper [guess ~80%]. | builder item |
| 12 | 24-27 | A look picked on one element does not spread along the whole line. | MOD WRONG | NEW → RIMMANDRAKE_SPREAD_FLOWWORKS_LOOK_ALONG_LINE_NOT_PIPES_ONLY | The pipe's button restyles only pipes of the same def (`PipeLook.RunOf`, `Source/Machinery/PipeLook.cs:126`, `:135`); a tank or pump restyles itself or the selected ones (`CompTankLook`, `:254`); the sprinkler head has no look button [measured]. Which element he changed is not recorded; the 2026-10-23 ruling covered the pipe run only, so tanks, pumps and heads following is new scope. | fix item |
| 13 | 33 | The "wet" look on a pawn in water is two flat blue patches, a placeholder. | MOD WRONG | KNOWN look: RIMMANDRAKE_JUDGE_FLOWWORKS_DROWNED_BODY_COVER_BY_EYE asked for this verdict, and his words are a fail. The fix is NEW → RIMMANDRAKE_REDRAW_FLOWWORKS_SUNK_PAWN_NOT_TWO_BLUE_PATCHES | `CoverPawn` covers the drowned part with the body's silhouette (`r.SilhouetteGraphic`: the body sprite only, not head, hair or clothes) in the water colour at 1 - Seen (`Source/Superdeep/RM_SubmergeDraw.cs:559-617`); the whole-picture cover runs only for a lying, wholly drowned pawn with a cached frame (`:608`) [measured]. Which path drew this pawn [guess ~65% the silhouette band]. | fix item; note on the judge item |
| 14 | 30 | Walking round a pit now works. | APPROVAL | settles RIMMANDRAKE_FIX_DRAFTED_MOVE_IN_BIG_PIT_WALKS_SOUTH (fix 32374da5e3; his 11-14 words said the same) | — | close that item |
| 15 | 42 | A colonist walks through the ladder, slows on it, then enters the pit. | APPROVAL | no open item [guess ~80%] | — | record only |
| 16 | 47 | A colonist crosses the concealed pit at ground speed, so a ladder seems wasteful. | BY DESIGN | — | While a cover stands its square is ground for walkers, path cost 1 (`Source/Pits/Building_PitCover.cs:18-21`, `Defs/Pits/ThingDefs/RM_PitCovers.xml:71`) [measured]: a trap must look and walk like ground. His point stands as a design question: a concealed pit is also a ground-speed crossing for his own people, so a ladder beside it looks wasteful. | question for him |
| 17 | 47 | The cover reads like ground (good), but the pit's walls and outline still show through it. | MOD WRONG (+ approval of the ground print) | NEW → RIMMANDRAKE_HIDE_FLOWWORKS_PIT_WALLS_UNDER_CONCEALED_COVER. Breaks bar `covered_pit_springs` ("the pit is visible as a pit under its cover" is its false pass) | The cover prints the ground in that terrain's own material, render queue 2000 + precedence (`Source/Pits/Building_PitCover.cs:276-281`); the pit faces, light and outline draw at queues 2440-2449 (`Source/Superdeep/RM_FaceMaterial.cs:28-46`), so they draw after the cover whatever its altitude, and the wall drawer never asks whether a square is covered [measured]. | fix item |
| 18 | 47 | A colonist on the cover does not make it give way. | BY DESIGN | — | Your own people are spared unless the setting "your own pit takes your own people" is on, and planks give way only past 120 kg on the whole deck (`Defs/Pits/ThingDefs/RM_PitCovers.xml:61`, `Source/Pits/Trigger/PitCoverTier.cs:25-33`); bar `covered_pit_springs` says "a light colonist walks a twin" without falling [measured]. The sign said only "planks". | question for him |
| 19 | 48-58 | The bridges look good. | APPROVAL | no open item names their look [guess ~80%] | — | record only |
| 20 | 48-58 | Asks for a check that bridge railings stop a pawn blown over them by an explosion. | REQUEST (test) | NEW → RIMMANDRAKE_PROVE_FLOWWORKS_RAILINGS_HOLD_AGAINST_BLAST_THROWS | A railing counts as a rail for blast throws (`Source/Pits/Suspension/Building_SuspensionDeck.cs:417`, `Source/Superdeep/RM_FallRails.cs:43`) [measured]; no live row reads it [guess ~80%]. | test item |
| 21 | 59, 60 | The steel and heavy jetties are not there. | SCENE WRONG | NEW (the pre-walk page did not know) | The scene drags each jetty 4 squares out (`northstar/owner_review_stage.py:873`) but a jetty reaches at most 2 (`JettyMaxCells`, `Source/RM_SuspensionMath.cs:687`), so `TryDesignate` refuses and nothing is placed; `ProofJetty` answers "JETTY ok=False ..." and the stage's `proof()` notes only replies that start "REFUSED" or calls that fail, so the refusal went unlogged [measured]. The defs exist (`Defs/Pits/ThingDefs/RM_SuspensionBridges.xml:595`, `:645`) and loaded (a missing def would have thrown in the designator and been noted) [guess ~85%]. | builder item |

Stations 11 (sluice "held open" reads closed) and 40-41 (the trench shooter has no ranged weapon) are scene failures the
pre-walk page already listed; he did not mention them. They go into the builder item with 3, 5, 11 and 21.

## Correction to the pre-walk page

`D:\ClaudeWork\rimmandrake\conductor\flowworks_walk_known_20261120.md` said "A pale patch is vanilla geyser steam." That is
false for what he saw: steam draws round drifting puffs, and the pale patch is a ring of whole squares (#4). The line is
corrected in place.

## OPEN FOR HIM: the water design pass (colour, transparency, waves as a function of depth)

Whether the pass is in FlowWorks 0.1.0 (Convergent) or the next version (Divergent) is his call. Estimates [guess, weighted
tokens, Opus-equivalent]:

| choice | feasibility | build effort | test effort | distance from passing 0.1.0 |
|---|---|---|---|---|
| A. Convergent, colour and transparency only: re-tune the one law (`RM_UnderLiquid.Seen`, the body colour, the settings defaults) from a sheet of depth swatches 0.2-5 m on three grounds, he picks | high: one function, four settings, an offline twin already kept equal (`model/underliquid.py`) | ~1-2 M | parity selftest exists; one staged depth matrix and his look | one more look round; no new bars |
| B. Convergent, the whole pass including waves | medium: moving water needs a new surface draw or flecks, and it touches every liquid | ~4-8 M | new looks to judge per liquid; frame-rate check on a big map | adds new looks to 0.1.0 and at least one more round; 0.1.0 stays open longer |
| C. Divergent, all of it in 0.2.0 | high | as A + B, later | as A + B | 0.1.0 passes with today's water, which he has now called too transparent (#2, #7), so that defect stays open in a passed version |

Recommendation: A in 0.1.0 (his words already say the transparency is wrong, which is a Problem in the current version), waves
filed for 0.2.0 [guess ~70% that this split matches what he means].

## Still unanswered by him (ask once)

1. Stations 7-16: does a dry canal read as a low wall? His "7-16: No, the water should be more legible" looks like "No" plus
   a water note [guess ~70%]: confirm.
2. Stations 34 and 39: should a colonist's depth show on the pawn (0.5 m and 8 m holes draw alike)?
3. Stations 1-4 and 42-46: do the ladders show through the water, and do the shadows stay inside the pit?
4. Stations 21 and 22 (5 m of water brighter than 2 m): he answered with the design-pass request (#10).
5. New: a concealed pit holds his own colonists and lets them cross at ground speed, by design (#16, #18). Keep that, or
   should it give way under anyone, or slow walkers?
6. Not mentioned: stations 56 (the second concealed pit), 61-64 (the steel bridge in four looks), 23 (the dry hole).
