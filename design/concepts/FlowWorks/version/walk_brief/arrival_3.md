# FlowWorks 0.1.0: walk brief, arrival 3
written_by: rm-detached-bench-rimmandrake-steward-flowworks-pre-human-1795595216

Written 2026-11-25 about 1:00 AM PST by a fresh reader. This reader made no stage move and no in-game row of this
version. Sources: `D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\version\stage_record.json`, visit 12
(`D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\version\in_game\visit_12\SUMMARY.md`, `rows.jsonl`,
`strange.jsonl`, `evidence\walk_stage_bars_bridges_ns_20261124T233745.log`), `build_match.py check --mod FlowWorks`,
`D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\journal.md`, `git log` on `src\RimMandrake\FlowWorks` since your
walk of 2026-11-22, the open FlowWorks items, and your walk 2 result
(`D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\version\walk_brief\walk_2_result.md`).

Your last walk was 2026-11-22, about 1:15 to 3:00 PM PST, on your full 315-mod list. This walk is on the small list.
Visits 8 to 12 ran after that walk. Visit 12 (2026-11-24, 10:17 PM to about 11:40 PM PST, ArchBig) ran 18 checks on
build `e32272585f`: 18 PASS. The build match counts all 30 in-game checks on that build, and 0 must run again
[measured 12:45 AM PST].

## What to open

- **Savegame:** `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT12_SMALL_20261124_2337.rws`
  (7,638,079 bytes, saved 2026-11-24 11:40 PM PST) [measured]. Do not open `..._2329.rws` beside it: it is the first
  save of the visit, and its station 11 is wrong.
- **Game:** ArchBig. **Mod list:** `flowworks_list`, 20 mods: Harmony, the base game and all five expansions,
  RimBridgeServer, Dubs Bad Hygiene Lite, Cherry Picker, Vanilla Factions Expanded Core, Simple Camera Setting (the
  zoom mod), More Ritual Seats, Vanilla Chemfuel Expanded, and our Gimme Some Slack, FlowWorks, Huge Things, Luminous
  Pigment, Biomes and Patches. The live `ModsConfig.xml` holds exactly this list now [measured 12:40 AM PST]. At 12:40 AM
  another of our runs held ArchBig ("tap certificate session"), so read `ModsConfig.xml` again before you load.
- **Build:** ArchBig's FlowWorks is in sync with source (deploy dry run: "in sync (1079 files)") [measured 12:50 AM
  PST]. No mod file changed after `e32272585f`.
- **Map:** 250x250 calm AridShrubland site, 79 stations, each with a sign book; `walk_twins.py check`: 79 signs, 0
  aftermath. No creature pens: FlowWorks adds no creature. Where to look:
  - (28-60, 100-160), the west block: ladders 1-4, spikes 5-6, sluice gates 7-11, grate doors 12-16, water depths 17-23,
    sprinklers in the four looks 24-27.
  - (178-210, 100-160), the east block: water in holes 28-33, dry pits with a colonist 34-39, trench 40-41, ladders and
    climbing gear 42-46, concealed pit 47, the eight bridges 48-56, bridge kinds and jetties 57-60, the steel bridge in
    four looks 61-64.
  - (211-236, 146-165), new since your last walk: **north/south examples**, as you asked. 65-68 the steel bridge in four
    looks, 69 a timber bridge over 1 m of unlit chemfuel (light it yourself to see fire under a deck), 70-75 the six
    suspension bridge kinds, 76-79 steel and heavy jetties reaching north and south.

## What changed since his last look

Each change since your walk of 2026-11-22, from your words where you gave them:

- **Pale frames at water edges are gone** (`09db578145`). You: "Those white frames are everywhere there is water."
  The pale waterline line at every water edge is deleted. The white blocks in the 2 m pit were the same lines.
  Look at stations 6, 7 and 21-22.
- **No water over an east/west sluice gate** (`09db578145`). You: "There should be no water shown over an E/W Sluice
  gate." Station 7 and 8.
- **Station 11 is held open now** (`88c959af4e`, in visit 12). Before this, every walk save showed it shut.
- **Choose style restyles the whole line** (`c0316b55e4`, `4cc37a7758`). You: "Clicking 'change style' on an object is
  supposed to change everything along its connected length." Now Choose style on any FlowWorks item restyles every
  FlowWorks item on the connected line (tank, pump, pipes, heads, hoses), not Gimme Some Slack items. Stations 24-27
  were staged with this tool, and visit 12 read each look back.
- **Pawns walk under every pit cover, and a cover fades see-through over a pawn** (`ba94149031`). You: "She should
  be able to walk beneath it" and "I want it in this version (transparency and ability to walk beneath pit covers)."
- **A pawn in a liquid is her own picture cut at the surface** (`741bacc090`, `76248133b7`), concept A of your pick.
  By your card, A is in 0.1.0; the tide mark, the surface reaction and the body under a clear surface (B, C, D) are
  next version.
- **Stepped pit floors** (`52182cca96`, `6f6516d654`, `c27bc10311`, `34f56e0d5e`, `5c870d5a36`): the inner cliff stops at
  the upper floor's depth, shadows come from the game's sun and moon and fade under lamps and roofs, the north shelf is
  no longer narrow, deeper floors draw darker. You approved this look from the BEFORE/AFTER picture on 2026-11-24 about
  1:25 AM PST: "I like the BEFORE AFTER stepped pit in game look very much. Nice job, approved." Stations 34-39.
- **Your art picks are installed** (`422fe83fb9`, `b061ba8aa0`, `05014cbca2`, `1343324282`, `6447d14771`): Industrial
  tank C, Modern tank R1 (weathered), Futuristic tank A, Modern pipe A (dusty), Modern sprinkler B (field worn); steel
  jetty B, heavy jetty B, heavy bridge B, steel bridge Scrapper C / Industrial A / Modern A / Futuristic A; the four
  true-oblique pump looks you accepted on 2026-11-23, with a south pipe drawn over the pump's cap (`e86d494b90`,
  `b4293975d8`). Stations 24-27, 59-68, 76-79.
- **Drawbridge** (`5d9004b9ce`, `847041c634`, `b51c6d6cb1`): one leaf, no plank stack (your rulings of 2026-11-03), a
  gate frame and taut near lines, occupants stay beneath it, steel needs its own powered winch. No station shows a
  drawbridge.
- **Pits and fights** (`3f9fd194ee`, `d15dd762b2`, `1c053b325b`, `3944c20b4c`): melee across a pit's edge needs reach,
  by the climb rule (your word of 2026-11-23); a rescuer on the rim of a 4 m pit no longer lifts a man out without a
  ladder; a held raider is no longer set over a pit wall.
- **Twelve faults from the GPT code reviews** (`49224d51e7`, `78f51ace1d`): wardens feed a captive out of reach, a
  blocked rim melee ends, a cover hides spikes, a hose click on a pump joins its side port, Pour moves a tank's
  remainder, a hose keeps its liquid over a reload, a sealed cell no longer stops Pour, water over a solid deck washes
  a coat.
- **Pit rescue** (`5d9004b9ce`, `be2e32c377`): a stranded colonist gets a rescue, and an unreachable spare ladder is
  skipped; the rescue no longer logs an error on every search.
- **Raid proof moved to 0.2.0** by your word of 2026-11-23 about 11:05 PM PST (below).

## Known, not fixed: you need not report these

Open FlowWorks items for this version [measured 12:30 AM PST, `rimflow show`]:
- `RIMMANDRAKE_MEND_FLOWWORKS_LIQUID_RULES_FIVE_OLD_DEFECTS`: **a shut sluice still seals its whole square** (your
  stations 7-10 find of 2026-11-20 and 2026-11-22: the gate's square keeps its water when one side is drained). Also
  deep sand reads as fresh water, a bottle refuses a small pond, fuel sap never ignites, colonists ignore liquid spill
  filth.
- `RIMMANDRAKE_FIX_FLOWWORKS_REVIEW_MAP_THREE_TICKETS_ONE_TOOL`: the walk map. Stations 9-10 still have one water
  height on both sides of the shut gate; you asked for two. Some things are still not shown, and some stations have no
  hose lead-out.
- `RIMMANDRAKE_ADD_COVERED_PITS_TO_FLOWWORKS_WALK_MAP_HE_ASKED`: no station has a colonist under a cover. To test the
  walk under a cover and the see-through fade, put a colonist in pit 47 or 56 yourself.
- `RIMMANDRAKE_DRAW_PAWN_OWN_PICTURE_CUT_AT_LIQUID_SURFACE_NOT_ICON`: built, and waits for your look at the test grid
  or the keeper save `RM_PawnInLiquidMatrix_20261122` (worn gear, animals, mechanoids, a Jawa, as you asked). You may
  look at it in this sitting.
- `RIMMANDRAKE_DRAW_TALL_CARGO_XTALL_TANKS_IN_HIS_PICKED_DESIGNS`: only the base 2x2 tank has your picked art; the
  tall, cargo and extra-tall tanks still show the old art.
- `RIMMANDRAKE_TEACH_FLOWWORKS_BRIDGE_TOOL_HIS_THREE_WALK_ASKS`: a built bridge has no Choose style button, a bridge
  will not span ruined bridge scrap, and the drag tool does not say to start on the landing.
- `RIMMANDRAKE_RESCUE_FLOWWORKS_STRANDED_COLONIST_REACHABLE_LADDER` (rescue cases left after `5d9004b9ce`),
  `RIMMANDRAKE_FIX_FLOWWORKS_RAIDER_LADDERS_FOUR_FAULTS_ONE_PATH`, `RIMMANDRAKE_MEND_FLOWWORKS_HOSES_SIX_OLD_FAULTS_ONE_SYSTEM`,
  `RIMMANDRAKE_FINISH_FLOWWORKS_RIVERS_PLACERS_EIGHT_OLD_TICKETS`, `RIMMANDRAKE_DARKEN_PIT_FLOOR_BELOW_GROUND_SLATE_DRAWS_BRIGHTER`,
  `RIMMANDRAKE_SLOW_RAIN_FILL_PIT_BRIMS_IN_ONE_NIGHT`, `RIMMANDRAKE_WARN_WHEN_RAIN_IS_FILLING_AN_OCCUPIED_PIT_KEEP_THE_FLOOD`,
  `RIMMANDRAKE_REFUSE_PITS_IN_LOOSE_GROUND_EVEN_BY_BRIDGE`, `RIMMANDRAKE_CHECK_SHOOTING_RULE_OFF_PICKS_FARTHER_PIT_FOE`,
  `RIMMANDRAKE_LIST_FLOWWORKS_SHALLOW_OPACITY_SO_SECTION_RESET_REACHES_IT`, `RIMMANDRAKE_DESIGN_FLOWWORKS_DIG_INTERFACE_CONSOLIDATION`,
  `RIMMANDRAKE_JUDGE_FLOWWORKS_REVIEW_SAVE_FOUR_LOOK_QUESTIONS`, `RIMMANDRAKE_PROVE_FLOWWORKS_NINE_LIVE_ROWS_OWED_ONE_VISIT`
  (includes the railings-against-blast row).
- `RIMMANDRAKE_DROP_FLOWWORKS_MATERIAL_WORD_STEEL_STEEL_JETTY` (filed in visit 12): a stuff-made bridge part reads
  "Steel steel jetty" or "Wooden timber suspension bridge" on mouse-over.

**Open raid bars:** none. Visit 12 has no paused raid scene (`paused_raids` is empty) [measured].

**Moved to the next version (0.2.0), so do not look for them:**
- by your card of 2026-11-14 about 9:43 PM PST, next version: `inv_irrigation`, `canal_wets_two_squares`,
  `wetting_is_not_flood`, `wetness_probe`;
- by your word of 2026-11-23 about 11:05 PM PST, next version: `moat_raid_sequence`, `raiders_fetch_their_fallen`,
  `inv_raider_fetch_fallen`, and the raider halves `raiders_shelter_only_where_they_can_climb_out` and
  `raiders_break_a_winch_and_escape`. `moat_drains_and_burns` (the moat without raiders) stays in 0.1.0.
- Texts: `D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\version\next_version\`.

## What I noticed first

1. **Every item from your walk 2 is closed or carried by a named item.** The five "your pick" items closed this
   morning on your picks of 2026-11-22 and 2026-11-24. Their builds landed under the items they made. Two of those are
   still open (the pawn-in-liquid look, the tall tanks; above). I closed the five as a delegated call; see the steward
   note on `RIMMANDRAKE_STEWARD_FLOWWORKS_PRE_HUMAN_STAGE_RUN_THREE`.
2. **This walk is on the 20-mod small list, not your 315-mod list.** The white frames that you saw "everywhere there is
   water" were seen on the full list. Visit 12's list of strange things (4 rows) names no pale frame on the small list
   [measured], but I did not look at its pictures myself. If the frames come back only on the full list, suspect another
   mod. Report it on
   `RIMMANDRAKE_REMOVE_WHITE_FRAMES_AT_EVERY_WATER_EDGE_HE_SAW_THEM_EVERYWHERE`.
3. **Your jetty picks were drawn in the Industrial look only** (`05014cbca2`: "Jetty and heavy-bridge picks exist only
   in the Industrial look; other looks keep their old art"). The jetties at stations 59-60 and 76-79 show whichever
   look they were built in. If one still reads as wood, that is this gap [guess ~60% that a non-Industrial jetty still
   reads as wood]. I filed nothing: your eye decides it.
4. **Station 17 says 0.2 m of water in 0.5 m holes.** Visit 12 read 0.2 m and 400 L in each of its five squares. If
   the mouse-over shows 0.5 m, it is the hole depth, not the water [guess ~70%].
5. **Sprinklers show no spray while the game is paused.** The spray draws only while the clock runs. All four heads
   read "Spraying" (visit 12). Unpause to see it.
6. **The station-69 fire is unlit.** Light the chemfuel to see a fire under a deck. Since 2026-11-22, a solid-deck rider
   catches fire much less often than a grated-deck rider. That was a steward's reading of the bridges design, not your
   words (arrival 2, point 2).
