# FlowWorks 0.1.0: walk brief, arrival 1
written_by: rm-detached-bench-rimmandrake-steward-flowworks-pre-human-1795312974

Written 2026-11-21 about 6:20 PM PST by a fresh reader. This reader made none of this version's evidence writes (no stage
move, no in-game row). Sources: `D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\version\stage_record.json`,
`D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\version\in_game\visit_4\SUMMARY.md` (with its `rows.jsonl`,
`strange.jsonl` and the stage log `evidence\owner_review_stage_full2.log`), the earlier visits' rows,
`build_match.py check --mod FlowWorks`, `D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\journal.md`, the sort of your
last walk (`D:\Luke\dev\RimMandrake\design\RimMandrake\validation_holding\flowworks_walk_20261120.md`), your dated rulings
(`owner_rulings.py`), `git log` on `src\RimMandrake\FlowWorks` and the open items.

## What to open

- **Savegame:** `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws`
  (13.6 MB, saved 2026-11-21 5:29 PM PST) [measured]. It is the same 64-station review map as your walk of 2026-11-20,
  staged again on your full list on the walk build. It was saved under save_guard (554 keeper saves backed up, none
  changed) [measured, stage log]. The two earlier saves of the same map today (`..._1603`, `..._1625`) are superseded; they
  lack the jetty and sprinkler repairs.
- **Mod list:** your full list, 315 mods, all 5 DLC, with Camera+ (`brrainz.cameraplus`) for zoom. The stored copy is
  `D:\Luke\dev\RimMandrake\infrastructure\state\modlists\ModsConfig.FULL.LATEST.xml` (315 active, FlowWorks and Camera+
  in it) [measured]. **The live `ModsConfig.xml` holds 13 mods now** (the flowworks test tier, without Camera+) [measured
  6:04 PM PST]. So the full list must go back before this save loads.
- **Build:** FlowWorks at commit bdd56c6ff6, mod hash `sha256:33f817434c71`, DLL md5 `06b39ad42e68` [measured by visit 4].
  The build match reads 31 of 31 in-game checks as counted, 0 to rerun [measured]. Read point 2 under "What I noticed
  first" before you trust that number for the pit looks.
- **The map:** AridShrubland, 250 x 250, calm site, paused, noon, clear. Each station has a numbered sign north of it.
  - **West block (stations 1-27, x 36-72):** ladders 1-4; spikes 5-6; sluice gates 7-11; grate doors 12-16; water depths
    17-23; sprinklers 24-27 (one per look).
  - **East block (stations 28-64, x 186-224):** water in holes 28-33; dry holes with a colonist 34-39; trench cover 40-41;
    ladders, climbing gear and concealed pits 42-47; suspension bridges 48-56; grated decks, jetties and the steel bridge
    in four looks 57-64.
- **Where to look first** (the things you named on 2026-11-20 that have a fix now):
  1. **Any pit with a step in its floor**, and stations 34-39 (dry 0.5 m to 8 m): pits are now drawn as relative terrain.
     Each cut is drawn again, the floor gets darker with depth, and a face shows at every step. Dig a stepped pit
     yourself, as you did on 2026-11-20, to see a step between two deep rows.
  2. **Stations 47 and 56 (concealed planks):** no pit wall or outline should show through the cover.
  3. **Stations 5-6 and 28-33 (water in pits):** the pale frame over the drowned walls should be gone. The water should
     read firmer at shallow depths (it was "too transparent again" on 2026-11-20).
  4. **Stations 24-27:** four different looks: Futuristic, Industrial, Modern, Scrapper. On 2026-11-20 all four were
     Scrapper.
  5. **Stations 59-60:** the steel and heavy jetties now stand. Each reaches 2 squares, the most a jetty can reach.
  6. **Stations 40-41:** each shooter has a rifle, and each colonist stands against the trench's east wall. The trench
     cover reads 0.441 waist-deep and 0.662 chest-deep [measured, stage log].
- **Earlier visits' captures**, for comparison: `D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\version\in_game\visit_4\screenshots\`
  (`review2_overview.jpg` for the west block, `review2_row_bars_access_labelled.jpg` for stations 34-64).

## What changed since his last look

The record has no `his_walk` move. So by the rule, "his last look" is the version's first move, 2026-11-14 11:49 PM PST.
You walked the review map on 2026-11-20 (about 6:40-7:00 AM PST). The list marks what changed after that walk.

**After your walk of 2026-11-20:**
- **Pits drawn as relative terrain** (e2288f4c84, 2026-11-20 5:58 PM). You said: *"Clearly you have not implemented the pit
  visuals as relative terrain representation, just "pit or no pit" floor. That won't do. Need more generalization."* Your
  card: "In 0.1.0, full rebuild". The same commit hides the pit walls under a concealed cover (you: *"there's clearly the
  pit graphic remaining, the very thing that should be obscured"*) and removes the pale frame on drowned walls (you:
  *"There appears to be a pale rectangle superimposed over the pit wall art"*).
- **Water firm from the first step, to the written target** (b80104f7a7, 2026-11-20 9:16 PM). You said: *"Water has somehow
  managed to become too transparent again. Barely reads at shallower depths."* Your card: colour and clarity now, waves in
  0.2.0. The target is `D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\version\water_by_depth_target.json`. The
  bottom distortion is not built (cc5ff3acc6): vanilla's only moving-texture shader paints lava colours.
- **The pale ring round steam geysers** is TheForge's haze, not FlowWorks. It now draws on Forge maps only (d07e03a938,
  2026-11-21). You said: *"I didn't mind the steam so much, but the meaningless pale region around steamgeysers I
  definitely did."*
- **Raiders fetch a comrade the pit holds** (58cfa254e8, 2026-11-21): they set a ladder on the pit's edge square. Your
  card of 2026-11-21 ("Try, and fall short") for a 4 m pit is not built yet: see the next section.
- **The island raid no longer maroons itself** (bdd56c6ff6): a raider sent at a drawbridge winch spares the leaf that it
  would cross. Your words of 2026-11-04 on the island bridges: *"Not today"*.
- **A cut through a frozen pond leaves crushed ice** (f3f597ccc6). **A flow sink drains a pond's film to the last
  decilitre** (2083f92acb).
- **Review map repairs (scene only, no mod change):** jetties 59-60 (02df5f8f4a); sprinkler looks 24-27 and armed trench
  shooters 40-41 (af8babff42). You said: *"25-27: Style is not right. Stations are all set to scrapper. Item 60 Jetty
  doesn't seem to exist nor does 59 steel"*.

**From 2026-11-14 to your walk of 2026-11-20 (you saw these on that walk):**
- **The toss-a-flame order** (30cc533cf3). Your card of 2026-11-05: *"a new order where a colonist walks to the rim and
  tosses a flame onto the square the player picks."*
- **Oil, tar, blood or slime coats a pawn who wades out; water washes it off** (ade1f4d429; bar `inv_liquid_coating`, added
  on 2026-11-14).
- **Raiders fetch their fallen from a pit** (636550d40b). Your vision line 5: "raiders make a ladder to fetch comrades who
  fell in".
- **Settings that fed nothing are removed** (27aad5783b, 5671ade040). Your cards of 2026-11-14: "Remove them now".
- **A map-control source pours what fits** (d6fb92a61c). Your card of 2026-11-14: "Pour whatever fits".
- Smaller fixes: the sprinkler valve pays the exact-fit cell (4b37a37db9); the crop-drown week holds at every flow pulse
  (663a2edf7a).

**In-game acceptance:** four visits (2026-11-15 to 2026-11-21). Visit 4 (3:48-5:39 PM PST today) ran 7 checks on this
build: 6 PASS, 1 UNMEASURED (`OL_OWNER_LOOK_READS`, one blocked row on the shadow's draw order; it decides no bar). It made
no change to the mod.

## Known, not fixed: you need not report these

**From your walk of 2026-11-20, still open (each is filed; none was fixed):**
- **A pawn in water is drawn with two flat blue patches** (station 33). You said: *"clearly placeholder"*.
  `RIMMANDRAKE_REDRAW_FLOWWORKS_SUNK_PAWN_NOT_TWO_BLUE_PATCHES`.
- **A look picked on one element does not spread along the line** (only pipes of the same kind follow).
  `RIMMANDRAKE_SPREAD_FLOWWORKS_LOOK_ALONG_LINE_NOT_PIPES_ONLY`.
- **A shut sluice keeps its own square's water** (stations 7-10). You saw this on 2026-11-14 and on 2026-11-20.
  `RIMMANDRAKE_SEAL_SLUICE_AT_ITS_PANEL_NOT_ITS_SQUARE`.
- **A built bridge has no Choose style button**. `RIMMANDRAKE_ADD_FLOWWORKS_CHOOSE_STYLE_TO_BUILT_BRIDGES`.
- **The bridge drag must start on the landing, and the game does not say so.**
  `RIMMANDRAKE_SAY_FLOWWORKS_BRIDGE_DRAG_STARTS_ON_THE_LANDING`.
- **A bridge will not place over a ruined bridge's scrap.** `RIMMANDRAKE_LET_FLOWWORKS_BRIDGE_SPAN_OVER_RUINED_BRIDGE_SCRAP`.
- **No check yet reads that bridge railings stop a pawn thrown by a blast.**
  `RIMMANDRAKE_PROVE_FLOWWORKS_RAILINGS_HOLD_AGAINST_BLAST_THROWS`.

**The review map still has scenes that do not match their signs** (`RIMMANDRAKE_RESTAGE_FLOWWORKS_REVIEW_SIGNS_OVER_UNBUILT_SCENES`, open):
- **Station 11 "EW E OPEN" is closed.** The stage log of this save reads `open=False seals=True` [measured]. Station 16 (the
  grate) is open, as signed.
- **Station 17 "0.2 m" holds 0.5 m of water in 0.5 m holes**, the same as station 18 [measured: all five squares read
  "Hole 0.5 m, Water 0.50 m (1,000 L)"]. The scene sets the whole body's level to 0.5 m, so the strip never levels to
  0.2 m. You said on 2026-11-20: *"the 0.2m still shows 0.5m depth upon hover over."*
- **Stations 9 and 10 have no water step** across the shut gate (your 2026-11-20 request). **No bridge runs north-south**
  (you built some yourself).

**Other open items that you can see in play:**
- **Raiders at a 4 m prison pit do not try a ladder yet.** Your card of 2026-11-21, "Try, and fall short", is filed as
  `RIMMANDRAKE_BUILD_RAIDERS_TRY_SHORT_LADDER_AT_FOUR_METRE_PIT` (not built). A 3 m pit has the working fetch.
- **A colonist stranded in a sealed 4 m pit reads as not trapped; no rescue starts.**
  `RIMMANDRAKE_FIX_STRANDED_COLONIST_READS_UNTRAPPED_NO_RESCUE`.
- **An interrupted dig starts again from zero** after a meal or a nap. `RIMMANDRAKE_KEEP_DIG_PROGRESS_ACROSS_MEALS_AND_NAPS`.
- **White hazy blocks inside the 2 m water pit near station 21**: you doubt that it is TheForge's haze. On the walk save's
  map (not a Forge map), visit 4 saw only round steam puffs over the vent and the pit's north face through the water;
  no square blocks (`...\visit_4\screenshots\shallows_station21_zoom.jpg`). No judge has read that capture yet.
  `RIMMANDRAKE_TRACE_PALE_BLOCKS_IN_PIT_HE_DOUBTS_THE_FORGE_HAZE`.
- **One red log line on lists that also load Gimme Some Slack:** `Tried to get ThingsOfDef of MinifiedThing`, with no stack.
  `RIMMANDRAKE_TRACE_SLACK_MINIFIED_LOOKUP_ERROR_WITH_FLOWWORKS`.

**Moved to 0.2.0 by your cards (not in this walk):** canal-side wetting and the thin film; the swale as a soaking floor
(the metal-slide swale is still in 0.1.0); the dig interface's large grid of options; the melee shove into a pit; water
waves and ripple fixes; pits refused in loose ground; floor and wall types in pits.

## What I noticed first

1. **Most of the faults that you named on 2026-11-20 meet you again.** That walk filed 13 new items and added to the
   sluice item. Five are closed: the pit rebuild (relative terrain, concealed-cover walls, pale frame), the water target,
   and the geyser ring (it is TheForge's). Waves went to 0.2.0. The review map repaired 2 of its scenes. Still open: six
   mod faults with the sluice item, one owed check (railings), and the review map's other scenes (the list above). The pipeline reached your walk because its
   exit reads the 57 bars, and none of those items is a bar line. I did not file anything new for this: each fault has its
   own item.
2. **The in-game verdicts on the pit looks were made before the pit rebuild.** `sc_pit_reads` (bar `pit_reads_as_hole`)
   and `sc_covered_pit` (bar `covered_pit_springs`) count from visit 2, build 65926ef481 (2026-11-19 7:37 PM PST). The
   pit draw was rebuilt after that build (e2288f4c84, `RM_ExcavationWalls.cs` +274 lines) [measured]. The build match
   still counts them because no FlowWorks in-game check declares any C# file: it relates only Python changes, so every
   C# change reruns only `sc_walk` [measured: 31 of 31 checks have no `exercises`; 65 changed files listed as UNDECLARED].
   Six more checks also count from that build (`sc_sluice`, `sc_one_network`, `sc_slime`, `sc_river`, `sc_fill_tiers`,
   `sc_dig_and_read`). The pit looks were read again after the rebuild by `PIT_LOOK_1114_LIVE` and the pit-relief part of
   the OL check (visit 3, PASS). But nothing read "a pit reads as a hole" and "the cover hides the pit" as those two
   scenes stage them. So your eye on stations 34-39, 47 and 56 is the first check of those two bars on this draw. Filed
   for the Conductor: `RIMMANDRAKE_DECLARE_FLOWWORKS_SCENE_CSHARP_PIT_REDRAW_UNSEEN` (with its acceptance test, seen red).
3. **Every scene except the walk recipe ran on the 13-mod test list.** On your 315-mod list, only `sc_walk` (12 rows) and
   the staging of this save ran on this build. The islands, ice and sink fixes were seen live only on test lists.
4. **The mod ledger's bar verdicts are older than the visit record.** The ledger packet still reads FAIL for
   `moat_raid_sequence`, `inv_toss_flame` and `inv_liquid_coating`. The visit record that the exit read has
   `sc_moat_raid`, `sc_toss_flame` and `sc_coating_wash` PASS (visit 3, build ff767a627d) [measured]. The flagship raid
   (moat, swim, drain, prison, fire) has no station on this map. It was proved only in its scene, so a test of the whole
   sequence in your walk means you stage a raid yourself.
5. **Not seen by you on 2026-11-20:** station 23 (the dry 1 m hole), 56 (the second concealed pit) and 61-64 (the steel
   bridge in four looks). They are on this map again.
