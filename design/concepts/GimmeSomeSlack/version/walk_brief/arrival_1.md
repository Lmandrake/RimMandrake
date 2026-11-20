# GimmeSomeSlack 0.1.0: walk brief, arrival 1
written_by: rm-detached-bench-rimmandrake-steward-gimmesomeslack-pre-h-1795194494

Written 2026-11-20 9:20 AM PST by a fresh reader that made none of this version's evidence writes. Sources: `D:\Luke\dev\RimMandrake\design\concepts\GimmeSomeSlack\version\stage_record.json`, `D:\Luke\dev\RimMandrake\design\concepts\GimmeSomeSlack\version\in_game\visit_3\SUMMARY.md` (with its `rows.jsonl` and `strange.jsonl`), `build_match.py check --mod GimmeSomeSlack`, `D:\Luke\dev\RimMandrake\design\concepts\GimmeSomeSlack\journal.md`, `git log` on `D:\Luke\dev\RimMandrake\src\RimMandrake\GimmeSomeSlack` since the version's first move (2026-11-14 4:02 PM PST; the record has no earlier walk of yours), and the mod's open items.

## What to open

- **Savegame:** `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\GSS_VISIT3_WALK_20261120.rws` (12.3 MB, saved 2026-11-20 7:35 AM PST). It is the 31-station labelled review map, built on the deployed build and saved before any test touched it. Your earlier review save, `GSS_OWNER_LOOK_20261116.rws`, is unchanged; the visit loaded it once and did not save over it.
- **Mod list:** your full list, 315 mods, all 5 DLC, with Camera+ (`brrainz.cameraplus`) for zoom. The stored copy is `D:\Luke\dev\RimMandrake\infrastructure\state\modlists\ModsConfig.FULL.LATEST.xml` (315 mods, Gimme Some Slack and Camera+ in it) [measured]. **The live `ModsConfig.xml` holds 10 mods now (the visit's last tier, without Gimme Some Slack)** [measured 9:15 AM PST], so the full list must go back before this save loads. The sitting that stages your walk does that.
- **Build:** Gimme Some Slack DLL from commit 345366aa49, deployed folder hash `sha256:f8936daf…`. The build match counts all 197 in-game verdicts as made on this build: 197 of 197, 0 to re-run [measured].
- **Where to look first:**
  1. Station 12, WALL + ROCK ENTRIES: a cord into a wall or rock face now ends in one fitting and nothing else. This is the double end you saw on 2026-11-16.
  2. Stations 16 (ELECTRIC ROOM) and 22 (CONVERGING HUB): every cord end now meets its stub at the stub's position and slope, including in crowded rooms. This is the rule you asked for on 2026-11-16.
  3. Stations 6 (OVERHEAD: FOUR LOOKS) and 21 (LONG SPAN + DIAGONALS), unpaused: pole wires now swing like hanging wires (Rope look by default). Ground cords no longer move in wind.
  4. Station 13 (CUT + FALLEN SPAN): see "What I noticed first".
- **Key sheet:** `D:\Luke\dev\RimMandrake\src\RimMandrake\GimmeSomeSlack\review\KEYSHEET.md` (or `keysheet.html` beside it) says, for each station, what to poke and what to look for. `human_review.py --goto N` jumps the camera to station N.

## What changed since his last look

The version's first move was 2026-11-14. Your words are quoted with their dates (Pacific time). Each change has its commit.

- **Cord ends join at the stub's position and slope.** You said on 2026-11-16 at 6:24 AM: *"wires should join at the location AND the angle/slope to match their next piece … It should be true for every art piece that has stubs/connectors."* At 6:39 AM you said: *"So we need offline checks and online checks to protect against this angle stuff. It's a big deal."* Changes:
  - a new bar, cords_join_stubs_on_position_and_slope, with an offline sweep (red first) and a live probe (9472c5cbdf);
  - switch and device-box stubs drawn only where used, plug seats kept (11643d9c82; stub textures installed through the art ledger, cd1fa27156);
  - live-end joins rebuilt in your order: broad bend, then small hook (6ecfb14c82);
  - three of the lay's own rules removed (9ed2b6e1d7), and two regressions caught by the whole census (8128d8b461, a2de43e4bd);
  - every end on its stub's line and slope in crowded rooms (a8d27a3f6b).
- **A wall or rock dead end is one loose end, not a fitting plus a sparking end.** You said on 2026-11-16 at 5:50 AM: *"there was both a hanging out sparking end as well as the wire plugging into the same point on the wall. That's not ok."* Changes: 99aa8bdc4c, 34b811961c.
- **Sway is for pole wires only.** You said on 2026-11-16 at 6:49 AM: *"Wires swaying in the wind were supposed to be about power pole wires. Wind wasn't supposed to mess with conduit-based wiring at all, nor about terminal wires in walls extending cable hanging out."* You also said: *"They're too stiff."* Changes: ground sway, shader sway and floor ripple removed (b560ff91e8); pole wires swing as hanging wires in three looks, Pendulum, Rope and Gust, with Rope the default (51e6569883).
- **Short cords lie slack.** Your card of 2026-11-14 at 2:09 PM said: *"Loosen the short cords."* Changes: cut leads slack and round, short leads drawn from their own seed (0416599c69); equal short leads no longer twins (47f2dac1eb); faulted pieces and heap cables redrawn, fallen strands slackened (a264e7b55d); unforced bends 4 to 0 on the judge's 80 scenes (6f8bfb47c4).
- **Cords draw under items.** Your card of 2026-11-14 asked for bars for cords under a battery and under items, and a scene for the cords bar. Change: the scene sc_cords_under_items (73ae08c273).
- **No hose words in Gimme Some Slack.** The Mod Settings header no longer promises "flexible pipes" (396433f04a). It now reads "Drawn wires to better display simple circuit-like plans underneath." Dropped FlowWorks cords still bite with overhead lines off (6d2aeb9c3f).
- **Fixes found by the tests (fault fixes, no new behaviour):**
  - an off-screen live flip is laid again (1d580847bd);
  - per-game reset of a static trace (164931fd94);
  - the census reads only after the build finishes (345366aa49).
- The in-game acceptance ran three visits. Visit 3 (2026-11-20, 7:29 to 8:53 AM PST) ended with all 197 checks PASS on their last row. It made no fix to the mod; one test harness was repaired (b346975f10).

## Known, not fixed: you need not report these

- **One red error on your full list that is not Gimme Some Slack's:** `Tried to get ThingsOfDef of MinifiedThing, use ThingsMatching(...) instead`, with no stack. The caller is FlowWorks (`RM_PitAccess.SparePortable`, `RM_PitAccess.cs:277`). It shows when a FlowWorks pit is near a portable spare. Item `RIMMANDRAKE_TRACE_SLACK_FLOWWORKS_TIER_MINIFIED_LOOKUP_ERROR`, with the one-line FlowWorks fix.
- **Fallen wires can lie longer than their cable.** In 13 of 1500 seeded falls, the coils and bends add length that the cable does not have (for example, 14.3 cells drawn for a 5.7-cell cable). Look at station 29 (FALLEN WIRE HAZARDS) and station 13. Item `RIMMANDRAKE_TRIM_GSS_FALLEN_WIRE_COILS_OUTGROW_CABLE` (Polish).
- **Gimme Some Slack draws FlowWorks pipe-pole spans.** That is by your 2026-10-22 ruling ("their own switch"). The no-hose bar's words do not say so yet. Item `RIMMANDRAKE_REWORD_GSS_NO_HOSE_BAR_POLES_DRAW_PIPES` (Polish).
- **Stealing power from more than one faction can charge goodwill to the wrong one.** A fix was built (c29007b6b6), and sc_tap_theft PASS this visit. The item still owes its own live row: `GSS_POWER_THEFT_FIX_WRONG_VICTIM`.
- **Up to about 1.4 MB of garbage per cord-lay frame at 8 lattices** (mean 452 KB). On a big rewire you may see a hitch. Item `GSS_FRAME_GARBAGE_SHRINK_HALF_MEG_LEFT`.
- These cannot be seen in play; they are listed so a log line or a settings read does not surprise you:
  - hose-named symbols in the shipped DLL, from a shared draw-order table (`RIMMANDRAKE_SPLIT_GSS_DLL_HOSE_DRAW_ORDER_SHARED_TABLE`, `RIMMANDRAKE_SEE_GSS_DLL_HOSE_NAMES_HIDDEN_IN_TAILS`);
  - About text read by no test (`RIMMANDRAKE_SCAN_GSS_ABOUT_TEXT_HOSE_CLAIMS_UNREAD`);
  - a no-hose clause with no self-mutant (`RIMMANDRAKE_GUARD_GSS_NOHOSE_FLEXIBLE_PIPES_CLAUSE_UNMUTATED`);
  - restring time on a NaN speed (`RIMMANDRAKE_GUARD_GSS_RESTRING_TICKS_NAN_NEVER_IN_GAME`);
  - an orphan selftest that holds the build lock (`RIMMANDRAKE_KILL_GSS_ORPHAN_SELFTEST_HOLDING_BUILD_LOCK`).

## What I noticed first

1. **The reworked bars were never read live on your full list.** The bars you asked for on 2026-11-16 (stub position and slope, the sparking wall end, cords under items, the off-screen flip, the pipe-pole menu) were read live only on the 12- and 13-mod test lists. Visit 3 ran sc_stub_joins on your review save, but loaded on the 12-mod list. On your 315-mod list, only the walk's own recipe ran (cords, soak, UI, save and reload); that recipe reads none of those bars. So your walk is the first full-list look at them. A clash with another mod would show there first. Item `RIMMANDRAKE_READ_SLACK_REWORK_BARS_ON_FULL_LIST` (open, needs the game) holds the four existing live tests to run in the same sitting.
2. **The key sheet told you to judge ground-cord wind sway.** Station 1's motion note in the key sheet said "the sway in the wind". That note outlived your 2026-11-16 ruling. I corrected the committed `KEYSHEET.md` and `keysheet.html`. **The sign book for station 1 inside the walk save may still carry the old line** [guess ~60%], and so does the generator that writes the sheet. Item `RIMMANDRAKE_MEND_SLACK_KEYSHEET_GROUND_SWAY_LINE_OUTLIVED_RULING`.
3. **The key sheet calls the tangle's look a "KNOWN GAP".** Stations 1 to 4 say that the tangle's pieces "still follow the DEFAULT look, not the run's". The visit-3 grayscale read of those four stations saw a different tangle piece for each look: square boxes for Scrapper, boxes with glands for Industrial, power strips for Modern, cross connectors for Futuristic (`D:\Luke\dev\RimMandrake\design\concepts\GimmeSomeSlack\version\in_game\visit_3\evidence\steward_judge_read.json`). So the note is probably stale [guess ~70%]. It is worth one glance at station 1 or 2: Restyle the run, then see whether the tangle follows.
4. **Station 13: the cut span's two fallen halves end about one cell apart.** The mast side has sparking tips, the far side limp tips. The test of the halves' line (M15d) PASS. Your card asked for halves that "meet at ONE point". Whether a one-cell gap at the cut reads as meeting is a look for your eye; nothing is filed. The visit's reader guessed it is fine [guess ~70%].
5. **Station 12: one claim is still unsettled.** It is that ground cords might hide a 0.24-cell wall clip under the wall art. The visit's capture at its zoom showed no clip [guess ~65%]. If you zoom in with Camera+ at a wall entry, you settle it.
6. **The four-looks judge was not blind.** Each capture kept its floating label, which names the look. So only "the four looks are told apart by eye" was judged, never "named". Your eye on stations 1 to 4 is the first independent naming.
