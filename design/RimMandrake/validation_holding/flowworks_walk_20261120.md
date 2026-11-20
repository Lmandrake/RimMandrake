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
- **When:** part 1 was typed about 6:42 AM PST (his six pictures were saved 06:41:09; the sort item was filed 06:42:51) [measured];
  part 2 about 7:00 AM PST, with picture 7 (saved 06:55); he ended the walk and saved `FLOWWORKS_OWNER_WALK_END_20261120` at 07:00.
- **Pictures:** `flowworks_walk_20261120/1.png` .. `6.png` here (copied; the source folder is temporary). 1 = stations 5 and
  6 · 2 = stations 17, 18, 19 · 3 = the steam geyser above stations 20 to 22 · 4 = stations 7, 8, 9 (one side drained) · 5 =
  station 33, a colonist lying in 2 m of water · 6 = station 47, a colonist on the plank cover. 7 = a 3x3 pit he dug himself, with a step in its floor (part 2).
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
| 2 | 17-19 | Water is too transparent again; shallow water barely reads. | MOD WRONG (a look) | KNOWN: RIMMANDRAKE_TUNE_WATER_CLARITY_DARKER_AND_HALF_AS_OPAQUE asked for the opposite (half as opaque); it is now superseded by RIMMANDRAKE_MOCK_FLOWWORKS_WATER_BY_DEPTH_ON_REAL_GROUND | Nothing changed since his 11-13 approval: the law (`Seen`, `Source/Superdeep/RM_UnderLiquid.cs:173`; deep opacity 0.90 at 4 m, curve power 1.4, fresh water seeThrough 0.45) is commit 9a5bbf7a66 of 11-12 21:22, inside the fe7c271f4b build he approved; later commits only add functions and a finer level note [measured]. His FlowWorks settings file holds no under-liquid key, so the defaults run [measured]. The law hides 6% at 0.2 m, 15% at 0.5 m, 30% at 1 m, 56% at 2 m, 90% at 5 m [measured, computed from the constants]. What depths the 11-13 save showed him: not recorded (no capture) [unknown]. Today's map shows 0.5 m and 1 m side by side on pale arid ground, where 15-30% of a dark sheet reads as grey [guess ~60% that this, not a change, is why it reads worse]. | decided by his card (SETTLED BY HIM); filed as RIMMANDRAKE_MOCK_FLOWWORKS_WATER_BY_DEPTH_ON_REAL_GROUND |
| 3 | 17 | The "0.2 m" strip says 0.5 m on hover. | SCENE WRONG | KNOWN (pre-walk page; the staging log's NOTE readouts: "Hole 0.5 m · Water 0.50 m" on all 5 squares) | The readout is right for what the scene built: every square is a 0.5 m hole with 0.5 m of water [measured]. | builder item RIMMANDRAKE_RESTAGE_FLOWWORKS_REVIEW_SIGNS_OVER_UNBUILT_SCENES |
| 4 | above 20-22 (also inside 21's water) | A ring of pale whole squares round a steam geyser, paler squares inside it. | MOD WRONG (whose mod: unknown) | NEW → RIMMANDRAKE_TRACE_FLOWWORKS_GEYSER_PALE_RING_NOT_STEAM | Not steam (steam draws round puffs that drift; this is whole squares that stay). Not FlowWorks: no FlowWorks code draws or writes ground round a geyser on undug ground; its geyser code is for sunk geysers only (`Source/Superdeep/RM_GeyserPit.cs`, `RM_SubmergeDraw.cs`) [measured]. It shows over station 21's water sheet (render queue 2449), so it is an overlay drawn late, not a terrain [guess ~70%]. Its size matches EnvironmentalHazards' vapor-column field (radius 6 round every steam geyser, `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_VaporColumns.cs:59`), but that field has no drawer [measured]. | one live read: hover a ring square, read its terrain line and the active overlays |
| 5 | 9, 10 | Asks for two water heights on either side of a closed sluice, to open and watch level. | REQUEST (scene) | NEW | — | builder item |
| 6 | 1-16 | The signs are fine; zoomed in they do not overlap the ladder. | APPROVAL | settles the label half of RIMMANDRAKE_JUDGE_FLOWWORKS_REVIEW_MAP_LABELS_HIDE_THEIR_PITS | — | close that item (its sprinkler half is #11 and #12) |
| 7 | 7-16 | "No": the water in the canals should be more legible, less transparent. | MOD WRONG (a look) + answer | KNOWN as #2. Reads as his answer "No" to q1 of RIMMANDRAKE_JUDGE_FLOWWORKS_REVIEW_SAVE_FOUR_LOOK_QUESTIONS (does the dry canal read as a low wall?) [guess ~70%] | Same law as #2: 1 m of water hides 30% [measured]. | q1 answered in part 2 (#27): No |
| 8 | 7-9 | With one side drained, water still shows on the gate's own square and a little beyond, rippling. | MOD WRONG | KNOWN: RIMMANDRAKE_SEAL_SLUICE_AT_ITS_PANEL_NOT_ITS_SQUARE. Same cause; its text names only the opposite case (gate square dry inside a full pit) | The kernel seals the gate's whole square: "a square liquid neither enters nor leaves this pulse" (`Source/RM_FlowKernel.cs:438-442`), so the square keeps whatever it held: dry on 11-14, wet today [measured]. The "bit beyond": the drained neighbour's wall band drawn at the gate square's level [guess ~50%]. | note on that item |
| 9 | 7-9 | Opened, the gate levels the water correctly. | APPROVAL | bar `sluice_drains_on_command`; no open item names it [guess ~80%] | — | record only; note on the sluice item |
| 10 | 21, 22 | Asks for a full design pass on water: colour, transparency, waves, by depth. | REQUEST (design) | answers q2 of the four-look item (5 m brighter than 2 m) by deferring it to the pass | — | decided by his card (SETTLED BY HIM): colour and clarity in 0.1.0, waves in 0.2.0; both filed |
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

## Part 2 (typed about 7:00 AM PST, one picture, end of walk)

> For the bridges, they have Styles like Industrial but no UI button to select it. No North/South runs shown to view yet. I made some. Selector tool worked to place it, but it should tell you that you start on the landing, not the span, in order to work. Would not place over a pit that had the scrap of a ruined bridge in it, even though it likely still should. The geyser white squares surrounding it may be some kind of overlay option on the map (lower right clickable layers). I couldn't identify any, but could be. For your questions, no dry canal does not read as low wall. Though a darker floor would likely help (I thought pits had a darker floor, why not the canals? They're all the same thing, aren't they? Please check that pits and canals are the precise same thing in the code.) For your 39 should depth show on pawn? We can leave it like this. I used to like having them partially covered by the southern edge but it seemed to cause drawing conflicts, so I'll take this if that's the cost. For shadows: people's shadows in the pit extend outward, I don't even know if that's possible to stop. Nice to have if easy, don't go crazy trying for it. [Image #7] Uh oh... what you are looking at is a pit I dug myself. It is 3.5x3, 3.5x3, 5x3 depth (with northern row first and southern row last). Yet there is NO visual discernment of this change of altitude. Character in pit does correctly not walk from southern deeper 5m row north even when asked to, but we need to really do better at how the ground is portrayed when there is a change in elevation. Clearly you have not implemented the pit visuals as relative terrain representation, just "pit or no pit" floor. That won't do. Need more generalization. Yes, ladders show through water. End of walk.

His end-of-walk save `FLOWWORKS_OWNER_WALK_END_20261120` (Saves folder, 07:00) was read from a copy, never opened in the game.

| # | what he said | class | known or new | likely cause | next |
|---|---|---|---|---|---|
| 22 | Bridges have looks (Industrial and others) but no button to choose one. | MOD WRONG | NEW → RIMMANDRAKE_ADD_FLOWWORKS_CHOOSE_STYLE_TO_BUILT_BRIDGES | A built bridge has no Choose style button: its parts carry only `CompProperties_Styleable` (`src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml:149` and the rest) [measured]. The build button's look menu exists in code (`Source/Machinery/PipeLook.cs:268-271`, decks registered at `Source/Pits/Suspension/RM_SuspensionPatches.cs:978-990`) [measured]; why he did not see it is unread [guess ~50% it did not open]. | fix item |
| 23 | The review map has no north-south bridge runs; he built some. | SCENE WRONG (missing scene) | added to RIMMANDRAKE_RESTAGE_FLOWWORKS_REVIEW_SIGNS_OVER_UNBUILT_SCENES | The bridge rows lay every span east-west (`northstar/owner_review_stage.py`, `row_bars_bridges`, `row_bars_bridge_kinds`) [measured]. | builder item |
| 24 | The bridge tool works only when the drag starts on the landing, and does not say so. | MOD WRONG (a message) | NEW → RIMMANDRAKE_SAY_FLOWWORKS_BRIDGE_DRAG_STARTS_ON_THE_LANDING | The rule is in the button text (`Source/Pits/Suspension/Designator_SuspensionBridge.cs:34`) and in the single-click message (`:56`) [measured]; which refusal a drag started on the span shows is unread [unknown]. | fix item |
| 25 | A bridge will not place over a pit holding a ruined bridge's scrap. | MOD WRONG | NEW → RIMMANDRAKE_LET_FLOWWORKS_BRIDGE_SPAN_OVER_RUINED_BRIDGE_SCRAP | `RM_SuspensionWreck` is an impassable Building on the pit floor (`Defs/Pits/ThingDefs/RM_SuspensionBridges.xml:700-708`); the bridge designator never mentions a wreck, so placement refuses the square [measured that nothing handles it]. | fix item |
| 26 | The geyser's pale squares may be a map overlay (the lower-right toggles). | (point 4) | KNOWN: RIMMANDRAKE_TRACE_FLOWWORKS_GEYSER_PALE_RING_NOT_STEAM | Tested on his walk-end save: the terrain grid holds one terrain at the ring, inside and outside it; no area, zone or FlowWorks grid marks a disc round the geyser at 59,141 [measured]. The overlays on at 07:00 were zones, beauty and room stats [measured: `playSettings`]; none of those draws filled squares. An overlay switched on for picture 3 and off before the save stays possible [guess ~40%]. | one live read |
| 27 | ANSWER: the dry canal does not read as a low wall; a darker floor would help. HIS ORDER: check that pits and canals are the same thing in the code. | SETTLED (q1) + REQUEST | q1 of RIMMANDRAKE_JUDGE_FLOWWORKS_REVIEW_SAVE_FOUR_LOOK_QUESTIONS; the floor ramp goes into RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN | See "Are pits and canals the same thing in the code?" below. | in the rebuild |
| 28 | ANSWER: depth on the pawn (34, 39) may stay as it is. | SETTLED | q3 of the four-look item | — | none |
| 29 | Pawn shadows in a pit reach outside it. "Nice to have if easy, don't go crazy trying for it." | POLISH | no ticket: one line on `design/concepts/FlowWorks/version/polish.md` | The pawn ground shadow is already skipped for a pawn drawn sunk in a cut (`RM_Patch_PitHidesShadow`, `Source/Superdeep/RM_PitDepthDraw.cs:417-436`) [measured]; which shadow he saw is unread; no cheap fix found offline. | polish line |
| 30 | ANSWER: ladders show through the water. | APPROVAL | confirms the ladder half of RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL live (fix 441c321a20, 9a0a6daa03) | — | note on that item |
| 31 | His own pit (3.5 m, 3.5 m and 5 m rows) draws as one flat floor; movement obeys the step. "Clearly you have not implemented the pit visuals as relative terrain representation". | MOD WRONG | NEW → RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN (his card) | See "What the pit draw keys on today" below. | the rebuild |
| 32 | Picture 7 shows "-5" on all nine squares. | not a fault | — | It is the vanilla beauty overlay, not a depth: `showBeauty` is on in his save, and the dug floor past 2 m (`RM_Channel_Superdeep`) has Beauty -5 (`Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml:120-135`) [measured]. The depth grid holds 7, 7 and 11 notches (3.5, 3.5 and 5.5 m) [measured]. | none |

### Are pits and canals the same thing in the code?

Yes, in everything that decides shape: one depth grid (`RM_MapComponent_Excavation.depthGrid`, notches of 0.5 m), one dig path
(`DeepenWithin`, `Source/RM_MapComponent_Excavation.cs:1700-1745`, from the one designator `Designator_DigCanal`), one draw layer
(`SectionLayer_RMExcavationWalls`, `Source/Superdeep/RM_ExcavationWalls.cs:28`) for every dug square, and the one readout
"Pit, X.X m deep" [measured]. "Canal" is only a name for a shallow dig. The differences, all keyed on depth, never on kind:
- **Floor material and colour:** the floor is the square's terrain, one of four by depth (`Source/RM_ExcavationDepth.cs:80-92`):
  0.5 m `RM_Channel_Empty` plain Gravel at full brightness, 1 m `RM_Channel_Mid` 0.78, 1.5 m `RM_Channel_Deep` 0.58, 2 m and deeper
  `RM_Channel_Superdeep` 0.38 (`Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml:32`, `:59-63`, `:85-89`, `:120-124`) [measured]. **This is
  why a canal floor draws lighter than a pit floor:** the shallow terrain is untinted gravel. Every depth past 2 m is one floor.
- **Path cost and beauty:** 30, 45, 80, 300; beauty -2 to -5, the same four terrains [measured].
- **The 2 m line** (`RM_ExcavationDepth.Superdeep` = 4 notches, `:39`): at 2 m and deeper a square is a trap that holds who falls in,
  may bound a room (`RM_PitRooms`), and is counted as a pit (`RM_MapComponent_Excavation.cs:1733-1737`); shallower squares bound nothing
  (`RM_ExcavationDepth.cs:20-24`) [measured]. That is the one place the code means "pit" as a kind.
- **Wall faces:** the same code for both; the face height grows with the drop up to 2.5 m and then stops (`Source/RM_WallFaceMath.cs:26`,
  `NorthMax`) [measured].

### What the pit draw keys on today (the relative-terrain finding)

- **The wall planner is already relative** [measured]: for every dug square it reads the north, west and east neighbours' depths
  (`NeighbourLevel`, `RM_ExcavationWalls.cs:595-602`) and draws a face from the drop `myDepth - neighbourDepth`
  (`RM_UnderLiquid.Exposed`, `Source/Superdeep/RM_UnderLiquid.cs:278-284`); the outline draws every side whose neighbour is shallower
  (`RM_ExcavationWalls.cs:216-239`). By that code his 5.5 m row carries a 0.50-cell face under the 3.5 m rows.
- **But the picture is never redrawn for a step past 2 m** [measured code path]: the walls layer re-prints only on a terrain or look
  change (`RM_ExcavationWalls.cs:37`); `DeepenWithin` writes the new depth and calls `ApplyFillTerrain`, which returns when the floor
  terrain is unchanged (`RM_MapComponent_Excavation.cs:3682`); every depth past 2 m is the same terrain. So his rows, each cut on past
  2 m, kept the picture drawn when they crossed 2 m [guess ~80% that it was drawn at equal depths].
- **And past 2 m every floor is one colour** and faces stop growing past a 2.5 m drop, so even a redrawn step between two deep rows
  shows only a face, never a floor shade [measured].
- His standing preference "geometry solved offline in Python first" and `design/RimMandrake/standing_rulings.md` §A pit is a SUPERDEEP cell
  (owner 2026-09-17: *"I'm not really sure a pit is any different than a deep canal."*; a pit is depth 4 on the one depth grid) both
  point to one height-field draw; that section names no "pit or no pit" art and no height-field ruling [measured: section and a
  search of the file for height field, relative height, geometry offline].
- **Acceptance test, watched red:** `src/RimMandrake/FlowWorks/acceptance_pit_relative_terrain.py` reads 1 of 3 PASS on the base
  (planner keys on the drop: PASS; deepening redraws: FAIL; floor shade past 2 m: FAIL); 3 of 3 on a planted fix; case 1 turns red when
  the planner is broken to "pit or no pit" [measured].
- **Part-1 faults the rebuild absorbs** (noted on each item): the walls under the concealed cover (#17; same layer, never asks about a
  cover) [measured cause, guess ~80% that the rebuild fixes it]; the pale frame in water (#1; same file, `SideUnder`) [guess ~70%]; the
  halo at the deepest pit (RIMMANDRAKE_FADE_DEEP_PIT_HALO_DARKENS_THE_BANK; the bank collar and halo are drawn in the same layer,
  `RM_ExcavationWalls.cs:66-74`) [guess ~50%]; the lighter canal floor (the colour ramp) [measured].

## SETTLED BY HIM

- Signs 1-16 are fine (#6). Walking round a pit works (#14). The ladder at 42 (#15). Bridges 48-58 look good (#19). An opened sluice
  levels the water (#9). Ladders show through water (#30).
- The dry canal does not read as a low wall (#27). Depth on the pawn stays as it is (#28). Pawn shadows outside a pit: polish only (#29).
- By card, 2026-11-20 about 7:08 AM PST: **water colour and clarity now, in 0.1.0; waves in 0.2.0**, with his write-in "(1) and it needs
  to be on representative terrain (put some different textures on the ground as well as furniture, bodies, etc)."; and **pits drawn
  as relative terrain: in 0.1.0, full rebuild**. The estimates put to him were: water colour and clarity in 0.1.0 ~1-2 M weighted
  tokens and one look; waves ~4-8 M, now 0.2.0; the pit rebuild 2 to 4 runs, geometry offline first, then one look [guess].
- What his 11-13 water approval saw [measured, `D:\ClaudeWork\rimmandrake\conductor\afk_20261112_night\live\REVIEW_ME.md` lines 10-12]:
  the big-pit series at 0.5, 1, 2, 3 and 4 m of water and 1.5 m of tar; a spill that night raised those pits by 1 m each (line 64), so
  the depths at his look are not recorded [unknown].

## OPEN FOR HIM

1. A concealed pit holds his own colonists and lets them cross at ground speed, by design (#16, #18). The north-star leaf
   `covered_pit_springs` says: "A raider, and the player watching, cannot see a covered pit at play zoom (only a faint seam at max
   zoom); a heavy enemy stepping on it drops onto the spikes below; spikes read as spikes and the cover never reads as a bridge", with
   "a light colonist walks a twin" in its scene. Keep that, or should it give way under anyone, or slow walkers?
2. Not seen by him on this walk: station 56 (the second concealed pit), 61-64 (the steel bridge in four looks), 23 (the dry hole).

## FILED

| cause | item |
|---|---|
| walls and outline show through a concealed cover (#17) | RIMMANDRAKE_HIDE_FLOWWORKS_PIT_WALLS_UNDER_CONCEALED_COVER (absorbed by the rebuild) |
| pale frame on drowned walls (#1) | RIMMANDRAKE_DIM_FLOWWORKS_DROWNED_WALLS_PALE_FRAME_IN_WATER (absorbed by the rebuild) |
| pawn in water covered by two flat patches (#13) | RIMMANDRAKE_REDRAW_FLOWWORKS_SUNK_PAWN_NOT_TWO_BLUE_PATCHES |
| a look does not spread along a line (#12) | RIMMANDRAKE_SPREAD_FLOWWORKS_LOOK_ALONG_LINE_NOT_PIPES_ONLY |
| pale ring of squares round the geyser (#4, #26) | RIMMANDRAKE_TRACE_FLOWWORKS_GEYSER_PALE_RING_NOT_STEAM |
| review map signs scenes it did not build; his north-south runs and two water heights (#3, #5, #11, #21, #23) | RIMMANDRAKE_RESTAGE_FLOWWORKS_REVIEW_SIGNS_OVER_UNBUILT_SCENES |
| railings against blast throws, untested (#20) | RIMMANDRAKE_PROVE_FLOWWORKS_RAILINGS_HOLD_AGAINST_BLAST_THROWS |
| pits drawn as relative terrain (#31, #27) | RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN (0.1.0, his card) |
| water colour and clarity by depth, no written target (#2, #7, #10) | RIMMANDRAKE_MOCK_FLOWWORKS_WATER_BY_DEPTH_ON_REAL_GROUND (0.1.0, his card; replaces RIMMANDRAKE_TUNE_WATER_CLARITY_DARKER_AND_HALF_AS_OPAQUE) |
| waves (#10) | RIMMANDRAKE_DESIGN_FLOWWORKS_WATER_WAVES_FOR_THE_NEXT_VERSION (0.2.0, Divergent) |
| no Choose style on a built bridge (#22) | RIMMANDRAKE_ADD_FLOWWORKS_CHOOSE_STYLE_TO_BUILT_BRIDGES |
| bridge drag must start on the landing, unsaid (#24) | RIMMANDRAKE_SAY_FLOWWORKS_BRIDGE_DRAG_STARTS_ON_THE_LANDING |
| bridge refused over a wreck (#25) | RIMMANDRAKE_LET_FLOWWORKS_BRIDGE_SPAN_OVER_RUINED_BRIDGE_SCRAP |
| the closed sluice keeps its square's water (#8) | extends RIMMANDRAKE_SEAL_SLUICE_AT_ITS_PANEL_NOT_ITS_SQUARE (no new item) |
