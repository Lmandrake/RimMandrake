# FlowWorks Artisan, aspect 1 (pits and depth): progress

## Pass 3 (2026-11-07): what I saw, what I changed

Game A on Steve, `flowworks` list, quick-test maps (temperate dirt, desert sand) at 09:00-11:00. Weather: 0 dead games,
0 dropped ssh, 3 deploy+restart cycles (bridge up in ~34 s); `bad_cpus` read [6] then [4] (no result surprised me after a
restart was due, none taken). Retired on the context gate (~350k).

**The depth look: three treatments shot side by side, oblique cut chosen (commit 0a357c4bcb, deployed, seen).**
`pitLookMode` 0 bevel / 1 oblique cut / 2 shadow well, live-switchable (`ralph/live/bars3.py`, save `fw3_bars` on Steve).
Sheets: `shots\pass3\contrast_depth_looks_r20.png` / `_r11.png`, every hole occupied (drafted colonists, 0..8 m).
L0 = black box, 4/8 m occupants drawn south of the hole. L2 = people standing in dark squares, 4 m = 8 m. L1 = the far face
hangs `pitSinkPerLevel` a notch (the occupant's own sink), lit rim to dark foot, a line a metre, soft side/near-lip shade,
no outline; occupants tinted by the hole's light (GetDrawParms postfix). Tuned once (darker, x1.45 rim light). AFTER the
deployed tune I replaced the hard cap with an ease into the opening so 4 m and 8 m hang apart (2-row pit: 1.35 vs 1.71
cells) — built and committed, NOT SEEN. L1 is the default: my call, in `ralph/LOOK.md`.

**His story replayed at root 20 (`ralph/live/story3.sh`; ran in L0 by mistake — bars3 then reset the look to 0, fixed).**
540-pt Neanderthal raid, 7 tribals: one fell through the covered spiked pit, one chopped wood and began a rescue ladder
(`RM_RaiderChopForLadder` -> `RM_RaiderSetLadder`), then 1,200 ticks later all left: "satisfied with the damage done".
Measured (`ralph/live/dmg2.py`, damage_log pawnsOnly=false): walls took ~983 (raiders bashing the blocked passage ~884,
our archers' missed arrows ~99) > vanilla's 900 minimum. So the story ends in a blink. Fix in flight (below), QUESTIONS 1.

**Owner card 19:03 handled:** starting water bottles (Patches/Scenarios_StartingWaterBottles.xml, xpaths validated);
Pyrelands' dig-keeps-progress patch landed as written (built; not watched live); rescue-ladder warning: in flight.

**Code review of pass 2's rescue + prison (done, 8 findings, no crash/patch-target faults):** worst: a fetcher under fire
loses its claimed ladder (RM_RaiderRescue.cs:264); downed bedless captives starve silently (his story's "injured prisoners");
stale talk-lip memo -> 10-jobs-in-a-tick loop; food counted outside the prisoner's room.

## IN FLIGHT AT RETIREMENT — uncommitted in this working tree, check `git status` first
1. A builder subagent was fixing the 8 review findings + the owner's rescue-ladder message + (10) postpone vanilla's
   "satisfied" exit while a raid is actively fetching a fallen comrade (prefix on Trigger_FractionColonyDamageTaken.ActivateOn,
   capped ~5,000 ticks). Files: Superdeep/RM_RaiderRescue.cs, RM_BedlessPitPrison.cs, RM_PitRooms.cs, RM_RaiderTrench.cs,
   RM_PitStuckAlert.cs, Keyed strings, SelfTest/*Checks.cs. Review its diff, build, run `selftest_flowworks_stock.py`
   (expected reds: RiverSwitchFlip_weirWhiteWater, PitCapture_follows, LW1), check the new types are in the DLL, commit.
2. An art subagent was making climbing-gear art: new ground sprite + worn `_north/_south/_east` under
   Textures/Things/Pawn/Humanlike/Apparel/FlowWorks/RM_ClimbingGear/, wornGraphicPath on RM_ClimbingGear
   (Defs/Canals/ThingDefs/FlowWorks_PitAccess.xml), offline sheet `shots\climbing_gear_offline_sheet.png`. Judge it, commit.
3. `ralph/live/look4.sh` was running on Steve (fw3_bars map, X0 = origin+25): sod BEFORE/AFTER in a grass field at r20 + seam
   at r11, 4 wall ladders (N/S lowered, E/W raised), portable ladder in 2 m and 4 m pits, open spikes, timber bridge with a
   colonist walking under. Shots `b2_sod_*`, `b2_ladders4_*`, `b2_portable_*`, `b2_spikes_open_*`, `b2_under_*` in Steve's
   Screenshots; log `Transient/ralph_fw/bars4.out`; save `fw3_look4`. Fetch with
   `ralph/steve.sh run` + tar (see `ralph/live/getshots.sh`, but tar only this run's files: old prefixes are huge).

## Next (in order)
1. Land 1-2 above; deploy; replay his story in L1 (`bash ralph/live/story3.sh 600 TribeRoughNeanderthal <tag>` on Steve;
   it starts a fresh map; set pitLookMode 1 first if the settings file still says 0). Watch for the rescue completing
   under arrows, the warning message, Capture-down from the lip, a warden feeding from the lip, the downed-captive alert.
2. Look at the look4 shots: ladders/rails/portable lean/bridge sag/under-deck under L1 — then fix what reads wrong
   (pass 2 found: south-wall ladder invisible, walker drawn on top of the deck, bridges flat strips, no rails).
3. Four fixes, never timed yet: ProofCliffTiming("reset"|"") after reloading a save with a big dig;
   Pits.Building_PitCover.ProofCoverScan("") on a 20x20 covered deck; two maps via jawa/world_tile_map_generate (read its
   schema first) + set_current_map, compare thisMapDerives. TakenByLand reload: needs aspect 2's river.
4. GPT pass-2 leads still unplayed: (5) interrupt the rescue (shoot the rescuer), (6) three days with a wounded captive,
   save/reload, left-behind ladder.
Traps paid for this pass: `export WSLENV=X` REPLACES Steve's WSLENV and Windows python loses RM_DATA_ROOT — append;
`start_debug_game_ready` only works from the main menu (fresh.py goes there first); fwb.py `call` truncates at 20k chars.

## Running count (seen in game, root 11/20; L1 rows are staged 2x2 holes on an ordinary map, not yet the story)
- pit_depth_ladder_legible: false — L1 tuned (contrast_depth_looks_r20): 0.5..4 m distinct, 4 m vs 8 m too close; the eased fix is unseen
- pawn_height_ladder_legible: false — L1: waist, chest, shoulders, head-only at 4/8 m read; 0.5 m vs undug barely differs at r20
- pawn_lowers_on_deeper_cell: unseen — no walk filmed
- pawn_rises_on_shallower_cell: unseen — no walk filmed
- pit_reads_as_hole: true — L1 contrast_depth_looks_r20: dark hole, lit far rim, no box
- pit_walls_have_visible_depth: true — L1: far face descends rim to floor, taller per depth
- pit_not_vanilla_trap: true — nothing like the spike trap (both sheets)
- pit_reads_at_size: true — L1 6x5 2 m pit at r11 (b3_p3a_L1_big_r11) reads as one place, no grid
- pit_occupant_below_floor: true — L1: occupants inside the opening, legs behind the near lip (contrast r11)
- pit_occupied_distinguishable: true — L1: even at 8 m the occupant's head shows at the lip (contrast r20)
- pit_trapped_reads_as_trapped: true — L1 2 m+: wall rises well over the head (more than a fifth)
- pit_covered_invisible: unseen — sod built, look4 shot pending
- pit_covered_seam_at_max_zoom: unseen — look4 r11 shot pending
- ladder_state_legible: false — last seen pass 2; under L1 pending (look4)
- sluice_gate_state_legible: false — pass 2: a few pixels at r20
- spikes_read_distinct: unseen — L0 story shots show spike texture at r20; L1 pending
- trench_wall_cover_shown: true — game's own tooltip string, 44% at 1 m, 74% at 1.5 m (pass 2 bars2_trench7.out); hover shot owed
- raiders_never_shelter_in_a_cage: unseen — not staged
- wall_ladder_rides_on_rails: false — pass 2: no rails
- portable_ladder_leans_on_its_wall: false — pass 2; L1 pending
- climbing_gear_reads_as_kit: false — worn draws nothing; art in flight
- geared_pawn_climbs_out: false — pass 2 frame drew him on the lip (L0); L1 unseen
- jump_into_pit_lands_unhurt: unseen — jump pack and creatures not tried
- geared_pawn_scales_built_wall: unseen — refusal not shot
- suspension_bridge_reads_hung: false — pass 2 flat strips
- pawn_walks_under_deck: false — pass 2 walker drawn on top; look4 pending
- pit_cover_unlike_bridge: false — cover-passes-for-ground half unseen in grass
- digging_takes_hours: unseen — dig job rewritten (Pyrelands patch), not watched
- never_snared_standing (cannot): true — falls end on the floor (story replay)
- never_reads_as_building (cannot): true — L1 has no outline; reads as a hole (contrast sheets)

Count: 10 true, 12 false, 8 unseen.

## Between this and done
| kind | what | evidence | next observation |
|---|---|---|---|
| blocker | raid leaves 20 s after the fall | dmg2.py: walls 983 dmg > 900 | story replay with the postponement built |
| unknown | L1 in the story (raider in the pit, ladder over the face) | story ran in L0 | story3 replay in L1 |
| unknown | rescue fixes, warning message, downed-captive alert, prison feeding | in flight | the same replay to the prison |
| unknown | sod, seam, ladders, bridge under L1 | look4 shots on Steve | fetch and look |
| blocker | ladder rails/lean, hung bridge, under-deck draw | pass 2 + look4 | fix after looking |
| unknown | the four fixes' cost | probes built, not run | Next 3 |
| decision | postpone "satisfied" exit during a rescue | QUESTIONS 1 | his answer (built as B) |
