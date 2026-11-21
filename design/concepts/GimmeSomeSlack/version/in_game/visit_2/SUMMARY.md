# GimmeSomeSlack 0.1.1 — in-game acceptance, visit 2

Run: detached helper on RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_VISIT_TWO_RUN_THREE, game a on Archmagi (Steam's install).
Started 2026-11-21 3:23 AM PST. Six checks: sc_walk (full list), sc_stub_joins, sc_switch_off_ends, sc_no_roof_over_pole,
sc_switch_light, P_Z_log_budget; owed P_M8_break_two_ends_live_dead.

## Progress
- 3:23 AM precondition `in_game 0.1.1` [measured]; item claimed; game a found cold-loading his full list (315 mods, started
  3:21 AM, bridge free); bridge archmagi taken by BENCH. GSS deploy dry run: in sync (362 files). Saves backed up (503 files) to
  D:\ClaudeWork\rimmandrake\backups\saves_gss_011_visit2_20261121.
- 3:37-3:38 AM bridge up; JawaBench companion FRESH (source hash 9035ca4a8950); build_match identity --full: 315 mods,
  mod_hash sha256:e9c2b80d6890, game 1.6.4871 rev590 (evidence/identity_full.json).
- 3:38-3:42 AM review map built on a full-list quicktest (human_review.py --build --fresh-map: 31 stations, 62 labels, 31 sign
  books, every build read back) and saved as GSS_011_VISIT2_WALK_20261121.rws (one new file, none changed).
- 3:42-3:44 AM sc_walk (gss_playtest_runner.py --recipe full --timeout 380 --load-wait 300): PASS [measured]: cords, soak
  (8 blasts), ui 24/24, save_reload_b 7/7 (cords laid 4.12 s after the load).
- 3:46-3:58 AM exploration on the full list: walk save reloaded, all 31 stations captured (screenshots/full_sheet0-7.jpg) and
  looked at; 5 strange things, all explained (strange.jsonl), one by a master on/off/on experiment.

- 3:58-3:59 AM game a stopped and relaunched on the gimmesomeslack tier (12 mods, all 5 DLC; started directly, Steam
  answered WaitingPrevProcess beside game b; bridge up 30 s). build_match identity --tier gimmesomeslack: same mod_hash.
  Offline gate (proof_all.py --offline-gate): 0 red [measured].
- 3:59-4:01 AM proof_all.py --live --no-shots --skip-offline --only core: 49/49 PASS, P_M8 and Z_log_budget among them
  (tap polls 51, lost 0) [measured].
- 4:01 AM scene_switch_light PASS (6 rows), scene_switch_off_ends PASS (2), scene_no_roof_over_pole PASS (3) [measured].
- 4:02 AM the switch lamp looked at in each state on the scene's site (screenshots/switch_light_states.jpg).
- 4:03 AM sc_stub_joins on his review save GSS_OWNER_LOOK_20261116 (md5 a1c76e27c41e before and after): PASS, 375 stubs,
  0 off line, 0 off slope, 15 live tails, 0 pinched, 0 loose wall ends [measured].
- 4:05 AM build_match.py check --visit 2: 203 cases read, 203 count, 0 to run [measured].

## What ran
- Game a on Archmagi (Steam's install), RimWorld 1.6.4871 rev590. GSS deployed folder sha256:e9c2b80d6890 (source
  d0b6483f04; deploy dry run in sync, 362 files; the running DLL sha256 b26ea241368d). JawaBench companion FRESH.
- His full list (315 mods, all 5 DLC) for sc_walk, the walk save and the exploration; the gimmesomeslack tier (12) for
  everything else. Each row carries build_match.py identity for its list (evidence/identity_full.json,
  evidence/identity_tier_gimmesomeslack.json).
- Order: the full list was already loading when this run began, so sc_walk ran first (the brief says last). No mod fix was
  made, so every row names the same build.

## Results [measured]
6 checks to run: 6 PASS, 0 FAIL, 0 UNMEASURED. sc_walk PASS (full list), sc_stub_joins PASS, sc_switch_off_ends PASS,
sc_no_roof_over_pole PASS, sc_switch_light PASS (its first in-game run), P_Z_log_budget PASS. 197 checks keep their PASS
from visit 1 (rerun_relation.py: the change touches nothing they read). No failed line, so nothing to class. No mod fix,
no check repaired, no check removed. One polish line (polish.md): sc_walk's observes text names more than the runner reads.

## Owed cases from the blind challenge (cycle 1)
- PF_G_TAPS_DOUBLE_CLAIM_SURPLUS: would NOT have been seen by sc_tap_theft or sc_statics_new_game [read, not run;
  guess ~85%]: every tap row stages one tap per victim net, where the fault changes nothing. Visit 1's own row stands
  (UNMEASURED, class HARNESS); neither check is touched by the change since, so neither ran here.
- PF_G_LINK_RANGE_DOUBLED: would have been seen [read, not run; guess ~90%]: M13d asks for OutOfRange at 24 cells with a
  20-cell range; doubled to 40 it links, so M13d and sc_spans FAIL. sc_spans keeps its visit 1 PASS.
- PF_P_SWITCH_NOT_STYLEABLE (listed twice in the brief): an equivalent mutant (planted_faults.json: the loaded defs do not
  change); no check can see it. sc_switch_off_ends PASS here; sc_four_looks keeps its visit 1 PASS.
- The 34 lane-1 not_kernel rows: each named check has a PASS last row (visit 1, or this visit for sc_walk, sc_stub_joins,
  sc_switch_off_ends). not_kernel_walk_scavenger_base, open after visit 1, is settled: sc_walk PASS on his full list.

## Owed from the road back (unrun.jsonl)
- RIMMANDRAKE_MEND_SLACK_STYLED_RUNS_FRESH_BUILD_DIVERGES -> sc_walk: PASS on his full list, on this visit's labelled
  review map: cords live == fresh at connect, disconnect and reconnect (167/167 edges), soak live == fresh after 8 blasts,
  reload 7/7 lines.
- RIMMANDRAKE_SETTLE_SLACK_CUT_CENSUS_DEAD_END_POLL_LATE -> P_M8_break_two_ends_live_dead: PASS (runA_core, the owed
  command: proof_all.py --live --no-shots --skip-offline --only core).

## Beyond the checks
All 31 stations of the walk save captured on his full list (screenshots/full_sheet0-7.jpg; PNGs in
D:\ClaudeWork\scratch\gss_011_v2\shots) and looked at; the switch lamp captured in five states. 5 strange things, all
explained (strange.jsonl), 0 filed, 0 open. The light patches on stations 13 and 31 were settled by experiment: identical with
the GSS master on, off and on again.

## Savegame for his walk
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\GSS_011_VISIT2_WALK_20261121.rws`: the
31-station labelled review map (sign books in the save; floating labels re-pinned by `human_review.py --labels`), built on his
full list (315 mods) on the deployed build and saved before any walk run touched the map. The walk runs loaded it and never
saved over it. Saves backed up first (D:\ClaudeWork\rimmandrake\backups\saves_gss_011_visit2_20261121). His keepers
(GSS_OWNER_LOOK_20261116*) untouched.

## Game and bridge at the end
Game a left running on the gimmesomeslack tier with the scene site loaded (healthy, paused); his list not restored (owner,
2026-10-24). Bridge archmagi released by BENCH.

## Exit
```
ingame_rows: {sc_walk: pass, sc_stub_joins: pass, sc_switch_off_ends: pass, sc_no_roof_over_pole: pass, sc_switch_light: pass, P_Z_log_budget: pass, P_M8_break_two_ends_live_dead: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\GSS_011_VISIT2_WALK_20261121.rws
exit_met: true
```
