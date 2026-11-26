# Pyrelands: next version (after 0.1.0)

Divergent work: anything that shifts or extends the 0.1.0 vision (`../vision.md`). Each entry is a pre-written ticket with its acceptance test, who proposed it, when, and why it was not taken now. **Protected: append-only for agents; removing an entry is his call.** Nothing here changes a 0.1.0 bar.

*Empty at entry on 2026-11-13: no open judge gap sorted as next version.* Watch: g2's inventory re-audit may find built behaviour outside the vision; such a find is filed here, not added to the 0.1.0 bars.

## Re-judge coverage under a calibrated brief when the next version opens

- **What:** this mod's coverage signature was made before the coverage brief read CALIBRATED (`coverage_judge.unproven_signatures` flags it; flagged, never voided). When its next Design Version opens, its coverage is judged again by a coverage brief that reads CALIBRATED at that time.
- **Who, when, why not now:** owner, by question card 2026-11-16 11:36 PM PST (point 19), picked "Leave them, re-judge at next version": "two of the three are already in live in-game visits, which find real failures better than a paper re-read. Buys: no spend or delay now; each gets a tested judge when its next Design Version opens." Filed by RIMMANDRAKE_LAND_JUDGE_PROMPT_CALLS_FOUR_ANSWERED_BY_CARD.
- **Acceptance test:** `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --no-run` reads `coverage_judge` CALIBRATED, and `python3 -c "import sys; sys.path.insert(0, 'src/RimMandrake/rimflow'); import coverage_judge as C; print([u['concept'] for u in C.unproven_signatures('.')])"` no longer lists `design/concepts/Pyrelands`.
- **0.2.0 sort (2026-11-26, Designer run RIMMANDRAKE_OPEN_PYRELANDS_NEXT_VERSION_HE_ASKED_FASTER_FIRE):** work that adds no bar. STALE, so its work is dropped: both halves of its acceptance test hold today. `refusal_contract.py calibrate --no-run` reads `coverage_judge CALIBRATED 12 planted case(s)`, and `unproven_signatures` lists FlowWorks, GimmeSomeSlack and Graffiti, not Pyrelands: `coverage_verdict.json` reads `covered` under a `CALIBRATED` brief, 2026-11-17T20:33:49Z (measured 2026-11-26).

## Black rain fills the moat and the water tanks

- **What:** a black rain is "a rare chance to fill your moat against the fire and fill your water tanks" (owner, 2026-11-13, walk_season_on_the_pyre). Today nothing fills: FlowWorks liquid tanks fill only over the liquid net, a limited water body refills about 0.06 units a cell over a 2.4 h black rain, and a moat dug dry into ash may not count as water at all. Owed: a Designer pass on how much a black rain fills (an open-sky tank; a dug moat or canal on the Pyrelands) and whether it is Pyrelands-only or any heavy rain; a change to FlowWorks' water code; a Mod Setting; a test; a live look. Build item: `RIMMANDRAKE_BUILD_BLACK_RAIN_FILLS_MOATS_TANKS_STAY_DRY`.
- **Who, when, why not now:** owner, by question card 2026-11-17 6:33 AM PST ("Rain fills" → "Next version (Recommended)", OWNER:1794926131273790638): 0.1.0 is not yet passing its own fire and grass bars, and this needs another mod's code changed; 0.1.0 ships on the bars it has, with no rain harvest at first release. Recorded by RIMMANDRAKE_REWORD_DESIGNER_BARS_PINNING_NUMBERS_NOT_HIS.
- **Acceptance test:** none yet: the fill amounts are unset until the Designer sets them, and the Designer's spec writes the red-first test (a FlowWorks kernel row: N hours at rainRate 1.1 fills an open-sky tank and a dug moat by the stated amount), then one short staged scene reads it live.
- **0.2.0 sort (2026-11-26, Designer run RIMMANDRAKE_OPEN_PYRELANDS_NEXT_VERSION_HE_ASKED_FASTER_FIRE):** Divergent. NOT in 0.2.0. By `GUIDING_PRINCIPLES.md` entry 1 rain that fills an open-sky tank or a dug channel is a water mechanic that works by its conditions (any heavy rain), so its code is FlowWorks' water code, and FlowWorks 0.1.0 has not passed. The Pyrelands half cannot stand alone: what it would add is only that black rain counts as heavy rain, and black rain is already the rain-rated weather of the table. The entry stays here; its build item `RIMMANDRAKE_BUILD_BLACK_RAIN_FILLS_MOATS_TANKS_STAY_DRY` is FlowWorks' design work when FlowWorks opens its next version.

## A choking-smoke weather of the Pyrelands' own

- **What:** "the choking smoke that sometimes comes as its own weather" (owner, 2026-11-13, walk_season_on_the_pyre). Today the RM_Pyrelands weather table holds no smoke weather; our one smoke weather, `RM_SmokeHazeCondition`, is the Long Shade's relief haze. Build a Pyrelands smoke weather that rolls on its own, reads as smoke, and hampers or harms pawns out in it with a readable sign; RM_FE_BlackRain stays the only rain-rated weather in the table; a Mod Setting (on/off, weight). Build item: `RIMMANDRAKE_BUILD_PYRE_SMOKE_WEATHER_ONLY_LONGSHADE_HAS_ONE`.
- **Who, when, why not now:** owner, by question card 2026-11-17 6:33 AM PST ("Smoke" → "Next version (Recommended)", OWNER:1794926132427945325): it is outside the locked bars and 4 of its 6 checks fail; 0.1.0 should first pass what it already promises, so the first release has no smoke weather. Recorded by RIMMANDRAKE_REWORD_DESIGNER_BARS_PINNING_NUMBERS_NOT_HIS.
- **Acceptance test:** `python3 src/RimMandrake/rimflow/acceptance/pyre_smoke_weather_accept.py` exits 0 with `PASS 6/6` (read `PASS 2/6` at a68d89e622 and again at 448168490b, 2026-11-17), and one short staged scene reads it in the game.
- **0.2.0 sort (2026-11-26, Designer run RIMMANDRAKE_OPEN_PYRELANDS_NEXT_VERSION_HE_ASKED_FASTER_FIRE):** Divergent. IN 0.2.0, bar `pyre_smoke_weather_chokes`. His card of 2026-11-17 deferred it because 0.1.0 had first to pass what it promised; 0.1.0 passed at his walk of 2026-11-24, so that reason is spent. Build item `RIMMANDRAKE_BUILD_PYRE_SMOKE_WEATHER_ONLY_LONGSHADE_HAS_ONE`; its acceptance test reads PASS 2/6 today (measured 2026-11-26).

## Fire catches and spreads faster (Divergent)

- **What:** a grass fire on the Pyrelands catches more readily and walks faster than 0.1.0's. The owner's words at his walk of 0.1.0, 2026-11-24 6:59 PM PST: "The fire barely catches, to be honest. I had expected faster spread." Then, 7:03 PM PST: "Yes, slow fire is a pass for this version, next version puts more aggressive fire." Owed: a Designer pass that states what "more aggressive" means as an experience bar (how soon a lit edge becomes a front the player must answer), then the burn kernel and its Mod Settings follow.
- **Who, when, why not now:** owner, at his walk, 2026-11-24 (ledger, item RIMMANDRAKE_SHOW_PYRE_HIS_WALK_FOUR_PICKS_ULLAI_FIRST); he passed 0.1.0 with the slow fire. Recorded by RIMMANDRAKE_SETTLE_PYRE_AFTER_PASS_REVIEW_SAVE_PENS_ART_KEPT.
- **Acceptance test:** none yet: the bar is an experience that the Designer writes first, with its red-first check; then one short staged burn on the Pyrelands decides it live.
- **0.2.0 sort (2026-11-26, Designer run RIMMANDRAKE_OPEN_PYRELANDS_NEXT_VERSION_HE_ASKED_FASTER_FIRE):** Divergent. IN 0.2.0, bar `fire_catches_and_runs`: the spark takes, a front forms the same day, the head walks downwind faster than 0.1.0's, and it is still a line, never a flood. A "Fire pace" slider in Mod Settings.

## Roofed grass declines where the player can see it, and leaves dead grass (Divergent)

- **What:** under a roof, ember grass now dies all at once and leaves bare ground. The owner, 2026-11-24 6:59 PM PST: "the grass just suddenly all dies at the same time. Kinda weird. And it doesn't turn into dead grass, just... barren nothing. You can't see grass health, so it was quite abrupt." He added: "But for this version, that's a pass." Owed: roofed grass shows its decline (a visible state or graphic) over its wither time, the plants die at different times, and a dead plant leaves dead grass (or another visible remains), not nothing. The code is `CompWithersUnderRoof` (`src/RimMandrake/Pyrelands/Source/CompWithersUnderRoof.cs`).
- **Who, when, why not now:** owner, at his walk, 2026-11-24 (same ledger event); he passed 0.1.0 with it. Recorded by RIMMANDRAKE_SETTLE_PYRE_AFTER_PASS_REVIEW_SAVE_PENS_ART_KEPT.
- **Acceptance test:** none yet: the Designer writes the bar (what the player sees as roofed grass declines), then a staged roofed patch is watched live for a day.
- **0.2.0 sort (2026-11-26, Designer run RIMMANDRAKE_OPEN_PYRELANDS_NEXT_VERSION_HE_ASKED_FASTER_FIRE):** Divergent. IN 0.2.0, bar `roofed_grass_declines_visibly`, with the Problem below folded into the same kill path.

## Roofed ember grass logs an exception each time it dies (Problem)

- **What:** each ember grass plant that the roof kills logs `Exception ticking RM_FE_Plant_EmberGrass<id>: System.NullReferenceException` once. The walk load of 2026-11-24 on ArchSmall logged 25 of them (Player.log lines 271-336, `D:\ClaudeWork\rimmandrake\instances\b\Player.log`), the same 25 on every load of that save. Cause [measured from the decompiled 1.6 source]: `CompWithersUnderRoof.CompTickLong` deals the last hit point, so the plant is destroyed inside vanilla `Plant.TickLong`; vanilla checks `Destroyed` only before `base.TickLong()` and then calls `PlantUtility.GrowthSeasonNow(Position, Map)` with a null map, which throws in `RegionAndRoomQuery.RegionAt`. Fix: run the wither before vanilla's growth step and stop the tick when it killed the plant (a Harmony prefix on `Plant.TickLong` for plants with this comp), or let the kill land outside the plant's own tick. Not fixed in the 0.1.0 settle run: it is a global patch on a hot tick of a passed version, and the roofed-grass redesign above rewrites this kill path. Fix it with that redesign, test first.
- **Who, when, why not now:** found in the walk log by RIMMANDRAKE_SETTLE_PYRE_AFTER_PASS_REVIEW_SAVE_PENS_ART_KEPT, 2026-11-24.
- **Acceptance test:** a live staged check: ember grass on a roofed cell at 1 hit point, one long tick later the plant is gone and Player.log holds 0 new `Exception ticking RM_FE_Plant_EmberGrass` lines (on the 0.1.0 build it reads 1).
- **0.2.0 sort (2026-11-26, Designer run RIMMANDRAKE_OPEN_PYRELANDS_NEXT_VERSION_HE_ASKED_FASTER_FIRE):** Problem. IN 0.2.0: still true in the code of now (`CompWithersUnderRoof.CompTickLong` deals the last hit point inside vanilla `Plant.TickLong`). Decided by `sc_roofed_grass_declines` (0 new `Exception ticking RM_FE_Plant_EmberGrass` lines), the deciding scene of bar `roofed_grass_declines_visibly`.

## "CurKindLifeStage from humanlike pawn Flea" at load (Problem, home not proven)

- **What:** every load of the Pyrelands walk save logs once `Tried to get CurKindLifeStage from humanlike pawn Flea` (Player.log line 270 on 2026-11-24; 1 in each of 6 logs). Vanilla `Pawn_AgeTracker` logs it once a session and returns null; "Flea" is a pawn's name. No stack trace is in the log. Likely caller [guess ~75%]: FlowWorks `src/RimMandrake/FlowWorks/Source/Swimming/RM_Swim.cs:468` (`ProfileOf` reads `CurKindLifeStage` with no humanlike guard), then `RM_PitFillEffects.cs:24` (`IsSwimmer`). Fix if so: guard both with `!pawn.RaceProps.Humanlike`; behaviour does not change, because vanilla already returns null for a humanlike.
- **Who, when, why not now:** found in the walk log by RIMMANDRAKE_SETTLE_PYRE_AFTER_PASS_REVIEW_SAVE_PENS_ART_KEPT, 2026-11-24. The caller is a guess and the likely home is FlowWorks, not Pyrelands: the first step is a stack trace (a Harmony prefix on the getter that logs the stack once, on a debug build).
- **Acceptance test:** a reload of the Pyrelands walk save logs 0 lines `Tried to get CurKindLifeStage from humanlike pawn`.
- **0.2.0 sort (2026-11-26, Designer run RIMMANDRAKE_OPEN_PYRELANDS_NEXT_VERSION_HE_ASKED_FASTER_FIRE):** Problem. IN 0.2.0 as work that adds no bar (the log floor of `floor.json`): the first step, a stack trace on a debug build, runs when Stage 6 has a game; the fix lands in the file the trace names (FlowWorks `RM_Swim.cs:468` is the guess, ~75%). Acceptance test as written above.

## Startup config errors of the Pyrelands small list (Problem, the first one fixed)

- **What:** the Pyrelands small-list load of 2026-11-24 logged 8 errors at startup. The first, `Could not find type named VEF.Plants.DualCropExtension` from `RM_CrackedLands_DonorPorts.xml`, dropped the whole def `RM_GargantuanLithops`: Vanilla Expanded Framework is not on that list. It is fixed (a `MayRequire` on the extension; check in `src/RimMandrake/CrackedLands/selftest_crackedlands_static.py`, red before the fix). Left: four of ours, `RUT_Jawa_Homestead_Grunt`, `_Heavy`, `_Specialist` and `RUT_Jawa_Junkers_Specialist`, whose cheapest weapon costs more than the kind's weaponMoney minimum (`src/RimUtinni/UtinniPatches`); three on vanilla defs (CannibalPirate and PirateYttakin required memes not allowed; BasicMechtech techprints), which may come from our patches [guess ~50%].
- **Who, when, why not now:** found by RIMMANDRAKE_SETTLE_PYRE_AFTER_PASS_REVIEW_SAVE_PENS_ART_KEPT, 2026-11-24. The weapon-money errors are UtinniPatches' (another mod's defs); they are not Pyrelands' to fix.
- **Acceptance test:** a startup on the Pyrelands small list logs 0 `Config error` lines and no `Could not find type named VEF` line.
- **0.2.0 sort (2026-11-26, Designer run RIMMANDRAKE_OPEN_PYRELANDS_NEXT_VERSION_HE_ASKED_FASTER_FIRE):** Problem, NOT Pyrelands' to fix: the VEF error is fixed; the four weapon-money errors are UtinniPatches' defs (`src/RimUtinni/UtinniPatches`), filed as their own item, and the three vanilla-def errors are not proven ours. No 0.2.0 bar.

## Caller scenario tests from the mined live bugs: pyre_fire_duty_starves, pyre_fire_no_flee, pyre_wetroots_season, pyre_furnace_heat_cap, pyre_burrower_flees

- **What:** five offline scenario tests. Each one runs our real caller code on real game types outside the game, as `design/RimMandrake/2026-11-07-pocock-design/pilot_realtypes/` does. Trial 1 found that the offline tests catch no fault planted in a caller (0 of 31), and the live record holds 47 caller bugs out of 66 (`design/RimMandrake/2026-11-07-pocock-design/06-mined-live-bugs.md`). Each scenario, in play terms:
  - `pyre_fire_duty_starves` (`ThinkNode_ConditionalPyrelandsColonist`, `RM_PyreEatBeforeFireDuty.xml`): an undrafted colonist at urgent hunger on a Pyrelands map eats before taking fire duty. A drafted pawn, a raider, another biome and the mod switched off are not gated. **Already written** in `pilot_realtypes/` (5 scenarios, 6 of 6 mutants red); move it into the mod's tests.
  - `pyre_fire_no_flee` (`PyrelandsFireSense`, `RM_PyreStepAwayFromFire.xml`): a colonist next to burning grass is off every burning cell within 60 ticks, and a downed colonist crawls to a burned-out cell. Needs a map: pull the decision out into a predicate that the caller calls, and test that predicate.
  - `pyre_wetroots_season` (`PyrelandsWetRoots`, its patch on vanilla `PlantUtility.GrowthSeasonNow`): a watered rice plant on ash at 58.8 C is in growth season and grows. Needs a cell temperature: test the patched gate with the temperature given.
  - `pyre_furnace_heat_cap` (`CompFurnaceWarmthAura`, `FurnaceWarmthMath`): at the biome's own 50 C, a closed room with a furnace-beast reads hotter than a matched empty room. Its live row once passed on false staging (both rooms chilled to 10 C).
  - `pyre_burrower_flees` (`RM_BurrowHeatReaction`): a domed ashwallow 3 cells from a front stays domed, and a standing one in dive range dives. Test the flee-gate predicate.
- **Who, when, why not now:** the owner adopted the scenario policy by card 2026-11-08 ("Policy plus real-types pilot"; item `RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL`, `design/RimMandrake/2026-11-07-pocock-design/06-mined-live-bugs.md` §Seed set). The seed is a live-found caller bug: its fix is on the build, and no offline test reads the caller. It moves no bar of the current version. It adds a cheaper regression check beside the live scene that decides the bar today. The Conductor decides at filing whether it stays here (recommended: next version).
- **Acceptance test:** each scenario runs offline from the mod's tests, and `maturation.py red-seen Pyrelands <test id>` records it red on a planted fault that reverts its fix's caller line, and green on the build. A scenario that needs a map, and that has no predicate that can be pulled out, becomes one bridge quicktest scene, not an offline row.
- **0.2.0 sort (2026-11-26, Designer run RIMMANDRAKE_OPEN_PYRELANDS_NEXT_VERSION_HE_ASKED_FASTER_FIRE):** work that adds no bar. IN 0.2.0 for the three callers that the conversion rewrites: `pyre_fire_duty_starves` (row code 9), `pyre_fire_no_flee` (code 8) and `pyre_burrower_flees` (code 2), as the support rows `T_SCENARIO_FIRE_DUTY`, `T_SCENARIO_FIRE_NO_FLEE` and `T_SCENARIO_BURROWER_FLEES`. `pyre_wetroots_season` and `pyre_furnace_heat_cap` stay here: 0.2.0 does not touch their callers.

## 0.2.0 proposed, 2026-11-26: what the proposal takes from this list (not opened)

Appended by the Designer run `RIMMANDRAKE_OPEN_PYRELANDS_NEXT_VERSION_HE_ASKED_FASTER_FIRE` (no entry above is removed).
0.2.0 is NOT open: the owner reviews the scope first (his words, 10:41 AM PST 2026-11-26: "If we're opening 0.2.0 for
Pyrelands, I want to review what we might put into it, ok? That's not an automatic decision"). Each "IN 0.2.0" in the
sort lines above is a recommendation. The page for him is `scope_proposal_0.2.0.md` in this folder. `../VERSION.json`
still reads 0.1.0. The draft bars, their test rows and the vision lines are kept in commit `faa90e801d`; the Conductor took
them out of the live files on 2026-11-26, until he answers.

- **Bars from this list:** `fire_catches_and_runs` (his walk, 2026-11-24), `roofed_grass_declines_visibly` (his walk, with the
  exception of roofed grass folded in), `pyre_smoke_weather_chokes` (his walk of 2026-11-13).
- **Bar from the conversion list:** `mechanics_switch_plain_no_biome` (`design/specs/2026-11-21-guiding-principles/conversion_list.md`,
  section Pyrelands).
- **Work that adds no bar:** the stack trace and fix of the `CurKindLifeStage` line; the three caller scenario tests whose
  callers the conversion rewrites.
- **Left here:** black rain fills the moat and the tanks (FlowWorks' water code, by conditions); the two scenario tests whose
  callers 0.2.0 does not touch.
- **Dropped as stale:** the coverage re-judge (it was re-judged covered under a CALIBRATED brief on 2026-11-17).
- **Not Pyrelands':** the UtinniPatches weapon-money config errors.

## 0.2.0 opened, 2026-11-26: what it took from this list

Appended by the Designer run `RIMMANDRAKE_OPEN_PYRELANDS_NEXT_VERSION_HE_ASKED_FASTER_FIRE`, after his two scope cards
(11:50 AM PST, OWNER:1795722774284846701, and 12:44 PM PST, OWNER:1795725937729027309). No entry above is removed. The
section "0.2.0 proposed" above was written before his answers; this section says what was opened.

- **Took, as bars:** "Fire catches and spreads faster" (`fire_catches_and_runs`), "Roofed grass declines where the player
  can see it" (`roofed_grass_declines_visibly`), "A choking-smoke weather" (`pyre_smoke_weather_chokes`), and the conversion
  of `design/specs/2026-11-21-guiding-principles/conversion_list.md` (`mechanics_switch_plain_no_biome`), by his first card.
  From the scope page's part two, by his second card: `crestfeather_has_its_own_look` and `grass_still_seen_under_ash`
  (its first step is one live look on a fresh map after an ash fall).
- **Took, as work that adds no bar:** "Roofed ember grass logs an exception" (fixed in the kill path of
  `roofed_grass_declines_visibly`), the `CurKindLifeStage` line, the startup config errors (the check is the Pyrelands
  small list's startup; the weapon-money fix lands in UtinniPatches' defs), the three caller scenario tests
  `pyre_fire_duty_starves`, `pyre_fire_no_flee`, `pyre_burrower_flees`, new words for `walk_season_on_the_pyre`, and the
  23 polish lines of the five groups (each stays on `../polish.md` until its builder does it). The Problems are in by the
  Conductor's call: a defect stays with the open version.
- **Left here:** "Black rain fills the moat and the water tanks" (FlowWorks work, by his first card); the scenario tests
  `pyre_wetroots_season` and `pyre_furnace_heat_cap` (0.2.0 does not touch their callers).
- **Dropped:** "Re-judge coverage under a calibrated brief" (done 2026-11-17).
- **Not in 0.2.0, by his second card:** every capability of the Deep Desert Tribes (his words: "We are not ready to do
  faction work yet. The tribes sleep until we start faction work much later."), the "Fire clock" switch's live check with
  them, and the Struck Glass rite, burning a field on purpose and caravan warmth ("Keep all three later").
- The whole list of 0.2.0: `../vision.md` §0.2.0, and `../VERSION.json`.
