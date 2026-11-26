# Pyrelands 0.1.0 — blind offline challenge (Stages 4 and 5), cycle 1

## Start time
2026-11-15T08:35:40Z (UTC), before any input was opened. Judge: detached helper RIMMANDRAKE_CHALLENGE_PYRELANDS_BLIND_JUDGE_REFUSED_FIRST (seat BENCH).

## Lane 1
Recorded before any lane-2 input was opened (journal, exam, evidence, test table, builder selftests: unopened).
`lane1/run_lane1.py` (C# `BlindLane1.cs` over the six kernel files + Python def/text rows): **97 rows: 83 PASS, 1 FAIL,
5 INFO, 8 UNSETTLED** [measured, `lane1/lane1_rows.jsonl`].
- FAIL `herd_anchor_never_fresh_ash` (bar `ullai_graze_old_burns`): with only a fresh burn in the history,
  `RM_BurnKernel.HistoryIndexAgo` falls back to the OLDEST sample (an hour old) and `FollowBurnDecision` sends the herd to
  it, i.e. to fresh ash. Shrunk form: one sample 2500 ticks old, lag 2 days. Kernel-level; whether a caller rejects a
  too-young anchor is lane 2's.
- INFO rows: the watered/dry sliders can invert the water lift; the 2-day quiet spell before a relight; a burn grid
  defaulting to 0 would read as burned (ScarStampTick/BurnBonus); `MarkOnce` clears the whole roll set past its bound;
  a herd with no record drifts to the nearest ash of any age.
- UNSETTLED (not_kernel, owed to Stage 6): the walk, the sprayer, the rite hook, the three skies' look, venom severity in
  play, the live census, grass green shares, the art.

## Lane 2 reruns
`lane2/rerun_offline.py` over the 18 `kind: offline` tests of `version/test_table.json`: **18 of 18 verdicts match** the
record [measured, `lane2/reruns.jsonl`]; after the fixes, 18 of 18 again [measured, `lane2/reruns_after_fix.jsonl`].
`T_SETTINGS_SCREENS` exits 1 by design and is judged by its own rows: 14 Pyrelands rows, 0 red (the suite prints no per-mod
tally; the recorded "14 rows for this mod, 0 red" was the recorder's words, so the rerun counts the rows itself).
`RECORD_ART_SHEET` (a record) had no command; the reconcile gave it one (`rimflow/record_check.py`, the event's line
hash pinned) and its rerun reads PASS (last row of `lane2/reruns_after_fix.jsonl`). Seven recorded `last` lines are not a prefix of
today's (T_FUZZ's timing, T_SITE's last row name, etc.); every verdict matches.

## Planted
`lane2/planted_faults.json` (22 faults), `lane2/plant_faults.py`, `lane2/planted_results.jsonl` (baseline first,
`tree_clean_after: true` last) [measured]. **20 of 22 caught** (offline deciders 14, blind lane 1 17).
- Offline bars: probe 4, engineered text 2, firebreak 2, lightning breaker 2, settings gate 5, art and text 2. Callers or
  patches: 6 (probe caller, bed-ignition gate, herd caller, rain postfix, the ash-storm patch, the fertility cap).
- Missed by both: `PF_PROBE_CALLER_NEVER_WET` and `PF_HERD_CALLER_ANCHOR_ALWAYS`, game-side callers only a live scene reads
  (owed to Stage 6).
- Missed by the deciders, caught by lane 1: the negated "never genetically engineered" text, the firebreak and fulgurite
  names back in C#, a missing texPath (filed `RIMMANDRAKE_HARDEN_PYRE_DECIDERS_FOUR_PLANTS_SLIPPED_PAST`).
- Chunked under the 540 s limit; lane 1 was extended mid-loop (the negation check, the fertility cap, patch-added weathers,
  a stricter rain wiring check), the baseline was rerun with it (still 0 FAIL) and the four faults it bears on were rerun.

## Faults
`lane2/faults.json`, refusal records, each filed in rimflow. **Problems 2 (both FIXED), Polish 5 (NOTED_FOR_CONDUCTOR).**
- Problem `RIMMANDRAKE_FIX_HERD_ANCHOR_FALLS_BACK_TO_FRESH_ASH` (bar `ullai_graze_old_burns`): with every burn under two
  days old, the herd anchor fell back to the oldest sample, a burn an hour old; for the first two days of every fresh map
  wild ullai walked toward the opening front. Seen first in lane 1; confirmed in the caller (`MapComponent_BurnLine.BurnCenterAgo`).
- Problem `RIMMANDRAKE_FIX_FORCED_WEATHER_SKIPS_THE_RAIN_LIST` (bar `no_ordinary_rain`): see the rain question.
- Polish: `RIMMANDRAKE_RECONCILE_DRY_ASH_TEXT_WITH_VERY_FERTILE_BAR` (bar words "very fertile" against its 70% dry oracle and
  the text "barely feeds a crop": the neutral fixer's), `RIMMANDRAKE_EXTEND_NO_RAIN_SCENE_WITH_FORCED_WEATHER`,
  `RIMMANDRAKE_REWORD_ABOUT_FIRE_PAYS_HE_SAID_SOLACE` (guess ~60% that his reword was meant to reach About),
  `RIMMANDRAKE_DROP_DONOR_GRASSLANDS_FROM_PYRE_MAP_LIST`, `RIMMANDRAKE_HARDEN_PYRE_DECIDERS_FOUR_PLANTS_SLIPPED_PAST`.
- Coverage gaps g1 to g14: not re-judged, not fixed.

## Fixes
One commit, `de0aae4a1b556a6768e3107996e04cb015a01b19` (parent `0f209f1db58d`), red first [measured, `lane2/fixes.jsonl`]:
- `RM_BurnKernel.HistoryIndexAgo` answers -1 when no sample is lag-old. Red: lane 1 `herd_anchor_never_fresh_ash` FAIL
  (rc 1) and the builder's fuzz with the corrected spec FAILED (rc 1) on the parent kernel; green: both rc 0.
- `PyrelandsNoOrdinaryRain.cs`: a postfix on `WeatherDecider.ChooseNextWeather` turns Rain, FoggyRain, RainyThunderstorm and
  TorrentialRain into `RM_FE_BlackRain` on a Pyrelands map with the gate on (kernel `RM_FireEcoKernel.RainBecomesBlackRain`).
  Red: lane 1 on the parent tree rc 1; green rc 0; `winbuild.py` 0 errors; DLL and `.srchash` committed, not deployed.
  **Untested live**: the postfix has never run in a game (owed to `sc_no_rain`, see the Polish item).
- Code review: every changed C# file reads DIRTY (`code_review_status.py`; they were DIRTY before this run); none marked clean.

## Tests edited
`tests_edited.json`: the builder's `PyrelandsFuzz.cs` (its spec line pinned the fallback; now -1, as strict), and the blind
judge's own `BlindLane1.cs` and `run_lane1.py` (rows added, none weakened). Lane 1 after the fixes and extensions: 100 rows,
87 PASS, 0 FAIL, 5 INFO, 8 UNSETTLED [measured, `lane2/green_lane1_rows.jsonl`]; `lane1/lane1_rows.jsonl` stays as recorded.

## Rain question
**Yes, something can choose ordinary rain** [measured from the vanilla source via RimSage and our defs]. The biome's list
(`Defs/BiomeDefs/Pyrelands.xml`) and the one patch that adds to it (`UtinniPatches/Patches/AshStorms_Pyrelands.xml`,
RM_VolcanicAsh) hold none, but `WeatherDecider.ChooseNextWeather` has two roads off the list: (1) a game condition's forced
weather is returned first, and Royalty's weather controller (`CompCauseGameCondition_ForceWeather.RandomizeSettings`, the
joiner-threat "weather control satellite" and the WeatherController site) picks any `isBad` weather, RainyThunderstorm and
FoggyRain included; (2) `CurrentWeatherCommonality` adds tile-mutator commonality after the biome loop, and Odyssey's
`WetClimate` adds 10 to Rain, RainyThunderstorm and FoggyRain. So no Polish proposal to drop `sc_no_rain` to "supports":
it stays the decider and is filed as a Problem, fixed in code (above); its scene owes the forced case. Evidence:
`lane2/faults.json`, ids `RIMMANDRAKE_FIX_FORCED_WEATHER_SKIPS_THE_RAIN_LIST` and `RIMMANDRAKE_EXTEND_NO_RAIN_SCENE_WITH_FORCED_WEATHER`.
Anomaly's blood rain and toxic rain are left alone (not ordinary). Whether any Pyrelands tile carries WetClimate is the
world paint's question (painted once, at the end).

## Unsettled
- Lane 1's 8 `not_kernel` rows (walk, sprayer, rite hook, the skies' look, venom severity, live census, grass green shares,
  art): Stage 6.
- The rain postfix's live behaviour; the probe and herd callers (planted faults no offline test sees).
- `bonus_fades_by_day6_own_clock` reads the six-day end, not the fade's shape; the builder's fuzz holds the linear shape.

## Exit
```
offline_bars: {ash_fertility_probe: green, biome_text_says_engineered: green, inv_firebreak_firefoam: green, inv_lightning_breaker: green, inv_settings_gate: green, inv_art_and_text: green}
problems_open: 0
exit_met: true
```
Green = every decider PASS on the rerun after the fixes (`lane2/reruns_after_fix.jsonl`), `RECORD_ART_SHEET` included.
The 14 coverage gaps are advisory and not counted.

## Owed
- The Conductor: read this, then `maturation.py ... --to in_game --steward-confirms "..."` or `--to blind_challenge`.
  A cycle-2 judge reads the changed files (`RM_BurnKernel.cs`, `RM_FireEcoKernel.cs`, `MapComponent_BurnLine.cs`,
  `PyrelandsNoOrdinaryRain.cs`, `FireEcologyHook.csproj`, `PyrelandsFuzz.cs`) and the bars `ullai_graze_old_burns`, `no_ordinary_rain`.
- The five NOTED Polish items; Stage 6 owes the rain postfix live (forced RainyThunderstorm on a Pyrelands pad) and the two
  callers lane 2 could not see.
- Spend: about $10.3 of the $20 bound [measured, the session budget line]; wall about 1 h (08:35 to about 09:35 UTC).

## Reconcile (2026-11-15, BENCH, same item)
`maturation.py next` read this cycle not met for three reasons; none was the judge's build. (1) The two `fixes.jsonl` rows
wrote `red`/`green` as lists of runs, which the reader did not read, and their commands held `<parent>`: both reds and
greens were rerun for real (parent tree exported from `0f209f1db58d`, lane 1 at `8f67415cc5`; red rc 1, green rc 0) and
appended as the last row per fault [measured, `lane2/reconcile/`]. (2) `lane1_rows.jsonl` keeps its blind FAIL by design;
lane 1 after the fixes is now `lane2/lane1_rows_after_fix.jsonl`: 100 rows, 87 PASS, 0 FAIL [measured]. (3)
`RECORD_ART_SHEET` got a rerun command (above). The reader now reads list-shaped runs and the after-fix lane 1, and says
by name when a record decider has no command. All offline tests rerun at `8f67415cc5`: 18 of 18 PASS [measured,
`lane2/reconcile/reruns_head_8f67415cc5.jsonl`]. Still owed to Stage 6: with no anchor, a herd off ash walks to the nearest
ash of any age within 25 cells (`RM_PyrelandsGiants.JobFor`), so fresh ash is not excluded there.

