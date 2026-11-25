# FlowWorks 0.1.0 — in-game acceptance, visit 12

Driver: detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_TWELVE, ArchBig on Archmagi.
Bridge taken 2026-11-24 10:17 PM PST.

## Build and lists

- Deployed source e32272585f (`DEPLOYED_SHA`; deploy dry run "in sync"; FlowWorks DLL 1512e786c38e, loaded = repo, read by
  live_session B0_assembly_identity). RimWorld 1.6.4871 rev590. The mod's C#, defs and settings did not change in the visit.
- ArchBig was on another run's 27-mod list; it was restarted three times: the 13-mod `flowworks` tier (16 checks), the
  16-mod `fw_gss_sitting` tier (sc_source_pays), then `flowworks_list`, his 20-mod walk list (sc_walk, the three walk-stage
  items, the walk save). ArchBig is left running on `flowworks_list` with the walk save's map loaded.

## Results [measured]: 18 PASS, 0 FAIL, 0 UNMEASURED of 18

All 18 checks the brief names PASS, each with its site checked. Two spoiled runs beside them, APPARATUS FAULT, no class:
- sc_pawn_height: my runner's limit of 260 s cut a scene that needs about 340 s (every earlier PASS 335-389 s); rerun at
  525 s PASS.
- sc_source_pays on the 13-mod tier: its lake case loads the river site save, which is built on `fw_gss_sitting` and logs
  cross-ref errors elsewhere (the same in visits 2, 3 and 9). Rerun on `fw_gss_sitting` PASS, lake reads Endless. The test
  table's command now names that tier (88c959af4e).
- sc_ways_out ran twice: the first PASS had no site assertion; the second ran on the calm site loaded and verified first,
  PASS, with B4_access_jump_pack_in_no_fall PASS (Longjump via Hemogenic + LongjumpLegs). Rows B4_rail_unrailed_control and
  B4_dehydration_rate read UNMEASURED inside it, as in earlier visits; neither decides ways_in_and_out.
- sc_hung_bridge's row: site_checked set from the proof's own `site_calm` block (ok true: storyteller off, wild spawner
  blocked and read back, 0 threat structures) — the runner reads only a concept scene's site block.

## The road back (unrun.jsonl), each run [measured]

- walk_stage_sprinklers (RIMMANDRAKE_FIX_FLOWWORKS_LINE_LOOK_CAST_THROWS_WHEN_TANK_TOUCHES_PIPE): PASS. No "pipe look for
  net N: asked X, game reads" note, so choose_look returned the asked look on all four nets; the picture shows Futuristic,
  Industrial, Modern and Scrapper apart (screenshots/row_sprinklers_labelled.jpg). save_guard VERIFIED.
- walk_stage_shallows (RIMMANDRAKE_TRACE_FLOWWORKS_TWO_NOTCH_STRIP_READS_FIVE_THOUSAND_LITRES): PASS. The five strip squares
  read water_m 0.2 and 400 L each; no NOT AS SIGNED note.
- walk_stage_bars_bridges_ns (RIMMANDRAKE_FIX_FLOWWORKS_REVIEW_STAGER_NS_ROW_IN_EDGE_BAND_READ_AS_BUILT): PASS. "origin moved
  to (28, 100)"; no proof REFUSED/failed note; stations 65-79 each hold anchors and decks or jetties (list_things,
  evidence/bars_bridges_ns_things.txt). Plant `--origin 36,100`: REFUSED exit 4, naming the 10-square no-build edge. Run
  with `--save-name` (it staged the walk save) in place of `--no-save`.
- sc_ways_out (RIMMANDRAKE_RUN_FLOWWORKS_WAYS_OUT_WHERE_CHERRY_PICKER_KEEPS_JUMP_PACK): PASS, above.

## Owed from blind challenge cycle 4 (on the sc_garden row as `owed_cases`)

- Converter caller rate and sun: shown. The filter at throughput 4.1 made 32 batches in its window [32, 33]; the still drew
  0 in the 10 night chunks of 24 and drew by day.
- Film never drowns crops, sheet settings units, drill reads its setting: not shown. No row reads crop survival; the scene
  runs the sheet at its defaults and the drill with its setting on. UNMEASURED in game; their offline cases stand.
- Planted faults, would sc_garden have seen each: CALLER_CONV_RATE_SETTING_IGNORED yes [guess ~90%: about 1/4.1 of the
  batches, far under the window]; CALLER_CONV_SUN_FACTOR_SKIPPED no [guess ~85%: the row caps each chunk at the full-sun
  rate only; the drops list would show night draws to a reader]; CALLER_DRILL_IGNORES_SETTING no; CALLER_SHEET_DOOR_PERCENT_AS_PERMILLE
  no [guess ~80%: the yard has no door]. CHANGED_FUZZ_SINK_UNREPORTED: sc_fill_front and sc_one_surface PASS and would not
  have seen it [guess ~75%: they read levels, not the kernel's sink report]. CHANGED_GLOW_ROOM_SHORT: no check of this
  visit runs glow_tank_live.py. None of the planted faults was played in a game.
- Lane-1 unsettled: thirst half settled (the faucet draws its tank, GARDEN_faucet_drinks_from_its_tank); sheet game side and
  drill survey roll not settled.

## Beyond the checks: the walk save and what was seen

- Walk save, staged on `flowworks_list`, calm site (250x250, AridShrubland), by owner_review_stage.py under save_guard
  (VERIFIED: no keeper changed, 750 keepers backed up; the save is new and well-formed). 79 stations with a sign book each;
  `walk_twins.py check`: 79 signs, 0 aftermath, ok.
- Looked at: the overview and 13 row pictures (screenshots/, JPG copies under 1 MB). strange.jsonl: 4 rows, 3 explained (one of them a stager fault fixed in the run), 1 filed:

  - Fixed, 88c959af4e: station 11 "RM_Sluice ... HELD OPEN" read open=False seals=True in every walk save since the gate
    rebuild. The stager pressed "Hold open", which a sluice no longer has (it has its own Gate toggle). It now orders the lift
    and applies it with god-mode Force open: open=True seals=False, then the walk save was staged again. rerun_relation: 0
    checks touched. A first walk save of this visit (…_2329) holds the old station 11; it is superseded, not deleted.
  - Filed RIMMANDRAKE_DROP_FLOWWORKS_MATERIAL_WORD_STEEL_STEEL_JETTY: stuff-made bridge parts read "Steel steel jetty",
    "Wooden timber suspension bridge" (recommend: Polish list; the Conductor decides).
  - Explained: sprinklers show no spray in a paused picture (the jet is flecks drawn only while the clock runs, in view; all
    four heads read "Spraying"); a bright blob near stations 22-23 is a vanilla steam geyser.
- No raid, no flyer. polish.md: three lines.

## Items filed

RIMMANDRAKE_DROP_FLOWWORKS_MATERIAL_WORD_STEEL_STEEL_JETTY

## Exit
```
ingame_rows: {sc_fill_front: pass, sc_one_surface: pass, sc_source_pays: pass, sc_pawn_height: pass, sc_ways_out: pass, sc_hose_look: pass, sc_trench_cover_pawns: pass, sc_hung_bridge: pass, sc_ice: pass, sc_pit_crowd: pass, sc_moat_walkers: pass, sc_hole_prison: pass, sc_toss_flame: pass, sc_islands_walker: pass, sc_walk: pass, sc_garden: pass, sc_geyser_tub: pass, sc_coating_wash: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT12_SMALL_20261124_2337.rws
exit_met: true
```
