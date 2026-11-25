# FlowWorks 0.1.0: walk brief, arrival 4
written_by: rm-detached-bench-rimmandrake-steward-flowworks-pre-human-1795637096

Written 2026-11-25 about 12:20 PM PST by a fresh reader. This reader made no stage move and no in-game row of this
version. Sources: `D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\version\stage_record.json`, visit 13
(`D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\version\in_game\visit_13\SUMMARY.md`, `rows.jsonl`,
`strange.jsonl`, `fix_reviews.jsonl`, `polish.md`, `evidence\walk_stage.log`, and the overview and two row pictures in
`screenshots\`), `build_match.py check --mod FlowWorks`, `D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\journal.md`,
`git log` on `src\RimMandrake\FlowWorks`, the open FlowWorks items, and arrival 3
(`D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\version\walk_brief\arrival_3.md`).

Arrival 3 (2026-11-25 1:01 AM PST) never reached you: at 2:17 AM PST the tick sent the mod back to Stage 6 because
in-game checks were owed. Your last walk is still walk 2, 2026-11-22, on your full 315-mod list. Visit 13 (2026-11-25,
9:34 AM to about 11:00 AM PST) ran the 22 owed checks: 10 on Steve2, 12 on ArchBig, all PASS on build `617ca4999a`. The
build match counts all 35 in-game checks, 0 to run again [measured 12:10 PM PST]. One fresh reader read the only mod
change of the sitting, `033392ed2d`, and found it sound (`6470bcda9d`).

## What to open

- **Savegame:** `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT13_SMALL_20261125_0957.rws`
  (7,651,129 bytes, saved 2026-11-25 10:00 AM PST) [measured]. Open this one, not the visit 12 save.
- **Game:** ArchBig. **Mod list:** `flowworks_list`, 20 mods: Harmony, the base game and all five expansions,
  RimBridgeServer, Dubs Bad Hygiene Lite, Cherry Picker, Vanilla Factions Expanded Core, Simple Camera Setting (the
  zoom mod), More Ritual Seats, Vanilla Chemfuel Expanded, and our Gimme Some Slack, FlowWorks, Huge Things, Luminous
  Pigment, Biomes and Patches.
- **ArchBig is on the wrong list now.** At 12:14 PM PST its live `ModsConfig.xml` held 23 mods, the `evening_20261113`
  list that visit 13 used for the big-pit check (it has Cold Storage, Explosive Knockback, Kinetic Arms, Weather Suite,
  SW Bestiary and Utinni Patches, and lacks Dubs Bad Hygiene Lite, More Ritual Seats and Vanilla Chemfuel Expanded)
  [measured]. The item `RIMMANDRAKE_STAGE_FLOWWORKS_WALK_SAVE_ARCHBIG_SITS_ON_WRONG_LIST` puts ArchBig on
  `flowworks_list` and loads the save. Until it is closed, do not load this save on the list that ArchBig shows.
- **Build:** ArchBig's FlowWorks is in sync with source (deploy dry run: "in sync (1079 files, 317 held)") [measured
  12:18 PM PST]. The last change to the mod's DLL, defs or textures is `033392ed2d`, and visit 13 ran on it.
- **Map:** the same 250x250 calm AridShrubland site and the same 79 stations as arrival 3, each with a sign book;
  `walk_twins.py check`: 79 signs, 0 aftermath. No creature pens: FlowWorks adds no creature. Where to look:
  - (28-60, 100-160), the west block: ladders 1-4, spikes 5-6, sluice gates 7-11, grate doors 12-16, water depths 17-23,
    sprinklers in the four looks 24-27.
  - (178-210, 100-160), the east block: water in holes 28-33, dry pits with a colonist 34-39, trench 40-41, ladders and
    climbing gear 42-46, concealed pit 47, the eight bridges 48-55, concealed pit 56, bridge kinds and jetties 57-60,
    the steel bridge in four looks 61-64.
  - (211-236, 146-165), north/south examples: 65-68 the steel bridge in four looks, 69 a timber bridge over 1 m of
    unlit chemfuel (light it to see fire under a deck), 70-75 the six suspension bridge kinds, 76-79 steel and heavy
    jetties reaching north and south.

## What changed since his last look

Since your walk of 2026-11-22. Arrival 3 lists these changes with their commits and your words, and they still hold:
the pale frames at water edges are gone and no water shows over an east/west sluice gate (`09db578145`); station 11 is
held open (`88c959af4e`); Choose style restyles the whole connected line (`c0316b55e4`, `4cc37a7758`); pawns walk under
every pit cover, and a cover fades see-through over a pawn (`ba94149031`); a pawn in a liquid is her own picture cut at
the surface, concept A (`741bacc090`, `76248133b7`); stepped pit floors, the look you approved on 2026-11-24
(`52182cca96` and four more); your art picks installed (`422fe83fb9` and four more); the drawbridge (`5d9004b9ce`,
`847041c634`, `b51c6d6cb1`); pits and fights (`3f9fd194ee` and three more); twelve GPT-review faults (`49224d51e7`,
`78f51ace1d`); pit rescue (`5d9004b9ce`, `be2e32c377`); raid proof moved to 0.2.0 by your word of 2026-11-23.

New since arrival 3 (2026-11-25 1:01 AM PST):

- **A Jawa and a droid are no longer rat-sized to water and tar** (`033392ed2d`). Before, every humanlike under body
  size 0.75 got a rat's 0.5 m height: 0.5 m of tar hid a Jawa and a T3 droid whole, and a Jawa drowned in 0.5 m
  shallows. Now a humanlike is 1.75 m x the square root of its body size (a Jawa 1.24 m, a T3 droid 1.41 m); animals
  keep their old heights. A Jawa now wades in 0.5 m of brine. The live pawn matrix on ArchBig read both cut at the
  surface, in line with their pictures (2026-11-25 3:28 AM PST). This answers the find on your liquid grid of
  2026-11-22 (`RIMMANDRAKE_CLASS_DROID_AND_JAWA_GONE_IN_SHALLOW_TAR`, closed).
- No other change to what you see or play. The other commits since then change tests, the review-map stager and the
  harness only (`0a6c3358d2`, `f303a90f1f`, `9f434a10d1`, `0c140ac0ae`, `6b07457e86`, `877010b1c7`, `617ca4999a`,
  `35eb8208a1`, `99c476351c`).

## Known, not fixed: you need not report these

Open FlowWorks items for this version [measured 12:12 PM PST, `rimflow show`]:
- `RIMMANDRAKE_MEND_FLOWWORKS_LIQUID_RULES_FIVE_OLD_DEFECTS`: **a shut sluice still seals its whole square** (your
  stations 7-10 find). Also deep sand reads as fresh water, a bottle refuses a small pond, fuel sap never ignites,
  colonists ignore liquid spill filth.
- `RIMMANDRAKE_FIX_FLOWWORKS_REVIEW_MAP_THREE_TICKETS_ONE_TOOL`: the walk map. Stations 7-10 and 12-15 still show one
  water height on both sides of the shut gate (seen in visit 13's sluice picture); you asked for two. Some things are
  still not shown, and some stations have no hose lead-out.
- `RIMMANDRAKE_ADD_COVERED_PITS_TO_FLOWWORKS_WALK_MAP_HE_ASKED`: no station has a colonist under a cover. To test the
  walk under a cover and the see-through fade, put a colonist in pit 47 or 56 yourself.
- `RIMMANDRAKE_DRAW_PAWN_OWN_PICTURE_CUT_AT_LIQUID_SURFACE_NOT_ICON`: built; it waits for your look at the liquid grid
  (`D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_DRAW_PAWN_OWN_PICTURE_CUT_AT_LIQUID_SURFACE_NOT_ICON\`) or the keeper
  save `RM_PawnInLiquidMatrix_20261122`. You may look at it in this sitting. The grid's worn-gear rows were restaged
  with garments that Cherry Picker does not cut (`877010b1c7`).
- `RIMMANDRAKE_SIGN_WILD_ANIMAL_UNDER_TAR_HAS_NO_LABEL_TO_SHOW`: a wild animal wholly under an opaque liquid shows
  nothing on the map (colonists keep their label, and a click still selects it).
- `RIMMANDRAKE_CLASS_SEVEN_THIRST_FAILS_SITE_FULL_OF_PATIENTS` (filed 2026-11-25): on a direct re-run of the thirst
  proof on ArchBig, six thirst rows and the irrigate-then-drown crop row read FAIL. The first reading blames the staged
  scene for most of them (colonists busy tending patients), but one may be the mod: a baseliner's thirst rose on a
  hemogen pack. Not classed yet. `sc_faucet_drink` keeps its earlier PASS.
- `RIMMANDRAKE_DRAW_TALL_CARGO_XTALL_TANKS_IN_HIS_PICKED_DESIGNS`: only the base 2x2 tank has your picked art; the
  tall, cargo and extra-tall tanks still show the old art.
- `RIMMANDRAKE_TEACH_FLOWWORKS_BRIDGE_TOOL_HIS_THREE_WALK_ASKS`: a built bridge has no Choose style button, a bridge
  will not span ruined bridge scrap, and the drag tool does not say to start on the landing.
- `RIMMANDRAKE_DROP_FLOWWORKS_MATERIAL_WORD_STEEL_STEEL_JETTY`: a stuff-made bridge part reads "Steel steel jetty" or
  "Wooden timber suspension bridge" on mouse-over.
- `RIMMANDRAKE_RESCUE_FLOWWORKS_STRANDED_COLONIST_REACHABLE_LADDER`, `RIMMANDRAKE_FIX_FLOWWORKS_RAIDER_LADDERS_FOUR_FAULTS_ONE_PATH`,
  `RIMMANDRAKE_MEND_FLOWWORKS_HOSES_SIX_OLD_FAULTS_ONE_SYSTEM`, `RIMMANDRAKE_FINISH_FLOWWORKS_RIVERS_PLACERS_EIGHT_OLD_TICKETS`,
  `RIMMANDRAKE_DARKEN_PIT_FLOOR_BELOW_GROUND_SLATE_DRAWS_BRIGHTER`, `RIMMANDRAKE_SLOW_RAIN_FILL_PIT_BRIMS_IN_ONE_NIGHT`,
  `RIMMANDRAKE_WARN_WHEN_RAIN_IS_FILLING_AN_OCCUPIED_PIT_KEEP_THE_FLOOD`, `RIMMANDRAKE_REFUSE_PITS_IN_LOOSE_GROUND_EVEN_BY_BRIDGE`,
  `RIMMANDRAKE_CHECK_SHOOTING_RULE_OFF_PICKS_FARTHER_PIT_FOE`, `RIMMANDRAKE_LIST_FLOWWORKS_SHALLOW_OPACITY_SO_SECTION_RESET_REACHES_IT`,
  `RIMMANDRAKE_DESIGN_FLOWWORKS_DIG_INTERFACE_CONSOLIDATION`, `RIMMANDRAKE_JUDGE_FLOWWORKS_REVIEW_SAVE_FOUR_LOOK_QUESTIONS`,
  `RIMMANDRAKE_PROVE_FLOWWORKS_NINE_LIVE_ROWS_OWED_ONE_VISIT` (includes the railings-against-blast row),
  `RIMMANDRAKE_REPAIR_FLOWWORKS_HARNESS_SEVEN_RED_OR_BLIND_ROWS`, `RIMMANDRAKE_REPAIR_FLOWWORKS_WRONG_CHECKS_SIX_OLD_TICKETS`.

**Open raid bars:** none. Visit 13's exit has no paused raid scene [measured: `maturation.py next FlowWorks` names
none].

**Moved to the next version (0.2.0), so do not look for them:**
- by your card of 2026-11-14 about 9:43 PM PST, next version: `inv_irrigation`, `canal_wets_two_squares`,
  `wetting_is_not_flood`, `wetness_probe`;
- by your word of 2026-11-23 about 11:05 PM PST, next version: `moat_raid_sequence`, `raiders_fetch_their_fallen`,
  `inv_raider_fetch_fallen`, and the raider halves `raiders_shelter_only_where_they_can_climb_out` and
  `raiders_break_a_winch_and_escape`. `moat_drains_and_burns` (the moat without raiders) stays in 0.1.0.
- Texts: `D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\version\next_version\`.

## What I noticed first

1. **ArchBig must change lists before you load the save** (above). The save was made on the 20-mod list; the game now
   sits on a 23-mod list. `RIMMANDRAKE_STAGE_FLOWWORKS_WALK_SAVE_ARCHBIG_SITS_ON_WRONG_LIST` carries it.
2. **A re-pin of the version's design waits, and it may reach your walk.** The Conductor ruled at 2026-11-25 about
   4:15 AM PST to take the FlowWorks re-pin and the Stage 4 retake after visit 13 ends
   (`RIMMANDRAKE_DECIDE_FLOWWORKS_REPIN_THAT_VOIDS_ITS_LOCKED_EXAM`). Its item says the re-pin "voids stage 4's exam
   and unlocks 0.1.0". Visit 13 has ended. If the re-pin runs while you walk, the stage record can move under you. Your
   two cards of 2026-11-14 and 2026-11-23 changed the design after the exam froze, and that is why the re-pin is owed.
3. **The jetties still read as wood in some looks.** In visit 13's north/south picture, the steel jetties 76-77 and the
   heavy jetties 78-79 show brown plank decks, and 59-60 look the same. Your jetty picks were drawn in the Industrial
   look only (`05014cbca2`), so a jetty built in another look keeps its old art [guess ~60% that this is the cause].
   Your eye decides; I filed nothing.
4. **Station 56 looks empty, on purpose.** It is a concealed pit under planks beside the bridges: it should pass for
   ground, where a bridge does not.
5. **The sluice picture shows the gates as they stand:** the shut gates at 7-10 and 12-15 have water at one height on
   both sides, and 11 and 16 are held open (read open=True seals=False). The one-height look is the known sluice fault
   above, not a new one.
6. **Two things from the calm test site are not ours:** a large grey fallen monolith beside station 40 (Anomaly's Void
   Monolith; it gives no cover) and a steam geyser north-east of stations 22-23. Both are outside the station rects.
7. **Sprinklers show no spray while the game is paused, and the station-69 fire is unlit**, as in arrival 3. Unpause
   to see spray; light the chemfuel to see a fire under a deck.
