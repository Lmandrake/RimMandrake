# FlowWorks 0.1.0: walk brief, arrival 2
written_by: rm-detached-bench-rimmandrake-steward-flowworks-pre-human-1795347255

Written 2026-11-22 about 3:45 AM PST by a fresh reader. This reader made none of this version's evidence writes (no stage
move, no in-game row). Sources: `D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\version\stage_record.json`, the
summaries, `rows.jsonl` and `strange.jsonl` of visits 5, 6 and 7
(`D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\version\in_game\visit_5\` to `visit_7\`), `build_match.py check --mod
FlowWorks`, `D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\journal.md`, `git log` on `src\RimMandrake\FlowWorks`, the
open items, and the arrival 1 brief (`D:\Luke\dev\RimMandrake\design\concepts\FlowWorks\version\walk_brief\arrival_1.md`).

**Arrival 1 still holds for everything up to 2026-11-21 6:14 PM PST.** The record's last `his_walk` move is 2026-11-21
6:14 PM PST. Eighteen minutes later the pipeline took the mod back to the in-game stage, before you walked. The pipeline
did that so that your walk is not the first reader of the pit looks on the rebuilt draw. So you have not walked since
2026-11-20. This brief gives what changed after arrival 1. It also corrects arrival 1 where arrival 1 is now wrong. Read
arrival 1's lists for the changes since your walk of 2026-11-20.

## What to open

- **Savegame:** the same one as arrival 1,
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws`
  (13,594,283 bytes, saved 2026-11-21 5:29 PM PST) [measured 3:38 AM PST]. No visit made a new walk save. The map is the
  64-station review map. Arrival 1 has the station list.
- **Mod list:** your full list. **The live `ModsConfig.xml` now holds your full list: 315 active mods, with FlowWorks and
  Camera+** [measured 3:38 AM PST]. Visit 7 ran `sc_walk` on that list. This corrects arrival 1, which said that the live
  list held 13 mods. You need not restore anything before you load the save.
- **Build:** game a's FlowWorks is in sync with the source at `496604468f` (deploy dry run: "in sync (1038 files)")
  [measured 3:38 AM PST]. The save was staged on the older build `bdd56c6ff6`. Since then only C# code changed, in
  fire, deck and pit-prisoner logic. No Def, Patch or texture changed [measured: `git diff --stat bdd56c6ff6..HEAD`]. So
  the save loads the new build with nothing missing.
- **Build match:** all 31 in-game checks count, and 0 must run again [measured]. Each check that the C# changes after
  `bdd56c6ff6` touch was run again on the newer build (visits 6 and 7).
- **Where to look first:** the six places from arrival 1 are the same, because the pit, water, sprinkler, jetty and
  trench work has not changed since. These are new:
  1. **A deck over a fire.** A solid-deck rider over a burning chemfuel pit now catches fire at most about 0.4 per burn.
     A grated-deck rider still catches fire nearly every time (next section). No station on the map has a fire under a
     deck [guess ~75%: arrival 1's station list names none]. To see this, light a chemfuel pit under a suspension bridge
     yourself.
  2. **A prisoner in a pit who stands and can feed himself** is no longer hand-fed. Vanilla does the same.

## What changed since his last look

The mod's code changed in two commits. Neither one comes from your words. Each one comes from a design text or from
vanilla's rule:

- **Fire under a deck reads the deck** (`65c45b6e98`, 2026-11-21 10:25 PM PST). An inferno's in-cell and beside fire
  chances now read the deck rule in `RM_FuelFireMath` (bridges design §4.1: a solid deck gives a low chance, a grated deck
  a high chance). Before this, a solid-deck rider had the same chance as a grated-deck rider.
- **A solid deck's low chance is one roll per burn** (`496604468f`, 2026-11-22 12:56 AM PST). The rule above still set
  fire to nearly every solid-deck rider over one burn (0.35 per 60-tick check). A steward made this decision as a
  delegated call under your Evidence-for-Ask ruling: §4.1 says "low", not "none", so the chance that a solid-deck rider
  catches fire over one burn stays at or below 0.4. It is in your digest. It is not your words. If you meant a solid deck
  to give full protection, that is your call to make. Item
  `RIMMANDRAKE_DECIDE_FLOWWORKS_SOLID_DECK_LOW_CHANCE_SATURATES_IN_ONE_BURN` (done).
- **A standing prisoner in a pit is fed as vanilla feeds him** (`65c45b6e98`). The `ShouldBeFed` postfix no longer
  hand-feeds a prisoner who stands. An awake prisoner with wounds gets an ordinary meal delivery. The intermittent "awake
  prisoner gets no meal" is closed (`RIMMANDRAKE_TRACE_FLOWWORKS_AWAKE_PRISONER_MEAL_SKIPPED_ONE_RUN_IN_TWO`, done: three
  PASS runs in a row in visit 6).

Changes to tests and scenes only, with no change to the mod:
- The island-restore fill "stall" was a staged worker with Mining 0. The mod was correct. The scene now stages Mining 8
  (`647bc9b0db`; `RIMMANDRAKE_UNSTICK_FLOWWORKS_FILL_JOB_HOLDS_GRAVEL_BESIDE_THE_HOLE`, done).
- The crush row reads harm by kind, body part and severity, not by a count (`581e6f4baf`). The shot rows give the gunner
  a gun (`b1cc65afe2`).
- Selftest deadlines are one hang guard (`4b996a6a74`, tooling only).

**In-game acceptance since arrival 1:** three visits.
- Visit 5 (2026-11-21 6:42-8:00 PM PST, game a): 24 checks on the save's own build, 23 PASS. The failure was
  `sc_hung_bridge` (the deck fire). The pit looks (`sc_pit_reads`, `sc_covered_pit`) and `PIT_LOOK_1114_LIVE` were among
  the PASS checks.
- Visit 6 (11:05 PM to 12:13 AM PST, game b): 8 checks on `65c45b6e98`. `sc_hung_bridge` failed again, on two lines.
- Visit 7 (1:57-3:10 AM PST, game a): 5 checks on `496604468f`, all PASS. `sc_hung_bridge` passed three times in a row.
  Grated against solid fire counts were 9/4, 13/9 and 13/5 [measured]. `sc_walk` passed on your 315-mod list.
- No visit filed a mod fault that is still open.

## Known, not fixed: you need not report these

Every item from arrival 1's list is still open, except the items below [measured 3:40 AM PST, `rimflow show`]. Arrival 1
gives what each item means for your walk:
`RIMMANDRAKE_REDRAW_FLOWWORKS_SUNK_PAWN_NOT_TWO_BLUE_PATCHES`, `RIMMANDRAKE_SPREAD_FLOWWORKS_LOOK_ALONG_LINE_NOT_PIPES_ONLY`,
`RIMMANDRAKE_SEAL_SLUICE_AT_ITS_PANEL_NOT_ITS_SQUARE`, `RIMMANDRAKE_ADD_FLOWWORKS_CHOOSE_STYLE_TO_BUILT_BRIDGES`,
`RIMMANDRAKE_SAY_FLOWWORKS_BRIDGE_DRAG_STARTS_ON_THE_LANDING`, `RIMMANDRAKE_LET_FLOWWORKS_BRIDGE_SPAN_OVER_RUINED_BRIDGE_SCRAP`,
`RIMMANDRAKE_PROVE_FLOWWORKS_RAILINGS_HOLD_AGAINST_BLAST_THROWS`, `RIMMANDRAKE_RESTAGE_FLOWWORKS_REVIEW_SIGNS_OVER_UNBUILT_SCENES`
(station 11 closed, station 17 at 0.5 m, no water step at stations 9-10),
`RIMMANDRAKE_BUILD_RAIDERS_TRY_SHORT_LADDER_AT_FOUR_METRE_PIT`, `RIMMANDRAKE_FIX_STRANDED_COLONIST_READS_UNTRAPPED_NO_RESCUE`,
`RIMMANDRAKE_TRACE_PALE_BLOCKS_IN_PIT_HE_DOUBTS_THE_FORGE_HAZE`, `RIMMANDRAKE_TRACE_SLACK_MINIFIED_LOOKUP_ERROR_WITH_FLOWWORKS`.

Corrections to arrival 1:
- **Interrupted digs:** arrival 1 listed "an interrupted dig starts again from zero"
  (`RIMMANDRAKE_KEEP_DIG_PROGRESS_ACROSS_MEALS_AND_NAPS`) as not fixed. The fix (`d23e9b6a83`, 2026-11-13: dig and fill
  work is kept per square across breaks) is in the build that game a loads [measured: an ancestor of HEAD, deploy in
  sync]. The item is still open because no in-game check has read the behaviour yet. If a dig you start is interrupted
  and then starts again from zero, report it on that item.
- **One more open item that you can see:** the check that a colonist under a water sheet casts no surface shadow
  (`OL_OWNER_LOOK_READS`, row `OL_no_surface_shadow_under_sheet`) reads UNMEASURED. The instrument cannot see the draw
  order (`RIMMANDRAKE_REPORT_SUBMERGE_SHADOW_QUEUE_JUDGE_CANNOT_SEE_ORDER`). The check decides no bar. Your eye at
  stations 28-33 is the only reader.

Moved to 0.2.0 by your cards: as arrival 1 lists them, with no change.

## What I noticed first

1. **Arrival 1's main caution is resolved.** Arrival 1 said that the pit looks counted from a build before the pit
   rebuild. Visit 5 ran `sc_pit_reads`, `sc_covered_pit` and `PIT_LOOK_1114_LIVE` again on `bdd56c6ff6`, the save's own
   build. All three PASS. Visit 6 ran `sc_pit_reads` again on `65c45b6e98`: PASS [measured, rows.jsonl].
   `RIMMANDRAKE_DECLARE_FLOWWORKS_SCENE_CSHARP_PIT_REDRAW_UNSEEN` is done. But these reads ran on the 13-mod test list,
   so on your 315-mod list, your eye is still the first check of the pit draw.
2. **"A solid deck shields its riders" is now "low", not "none".** In visit 7, solid-deck riders still caught fire 0 to 9
   times per run, against 7 to 13 on the grated deck [measured]. If a burning colonist on a solid deck looks wrong to
   you, say so: the steward's reading of §4.1 decided this, not your words.
3. **Every check except `sc_walk` still ran on the 13-mod list or on game b.** The deck-fire rule and the prisoner-feeding
   rule ran live only on the test list. Only `sc_walk` (12 rows) ran on your full list after these changes.
4. **Two open items are stale, not faults:** `RIMMANDRAKE_PASS_FLOWWORKS_COATING_WASH_SCENE_NEVER_PASSED` (`sc_coating_wash`
   PASS in visit 5) and `RIMMANDRAKE_RETEST_FLOWWORKS_TOSS_FLAME_SINCE_JOBDEF_BUILT` (`sc_toss_flame` PASS in visits 5-7)
   [measured]. You need not look for those two faults. I filed nothing for this: closing an item is bookkeeping and
   touches no mod.
5. **Each item that arrival 1 listed as open from your walk of 2026-11-20 is still open** (arrival 1, point 1). No
   commit since arrival 1 touched their code. The pipeline reached
   your walk again because its exit reads the bars, and none of those items is a bar line.
