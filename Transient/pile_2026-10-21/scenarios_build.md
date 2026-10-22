# REVIEW_SCENARIOS_BUILD_ALL_TWELVE_AT_ONCE — build progress (BENCH)

Started 2026-10-21. Skeleton first; filled as work proceeds.

## Phase 1 (offline)
- [x] item claimed (lease token OWNER.pid10726.8600d2d5)
- [x] design read (C1-C12, §5 build order, GPT amendments)
- [x] staging modules written
- [x] selftest passes (107)
- [x] key sheet generated
- [ ] committed + pushed

## Phase 2 (live)
- [ ] bridge free? — at start: HELD by BENCH (FlowWorks live queue: fallen cord, pit cover, pitfall). Phase 2 likely skipped.

## Per-scenario status (all mock-OK)
| id | name | map | staged | DEFERRED |
|---|---|---|---|---|
| C1 | The Thirsty Terraces | R | 15 | overflow onto the field (D2/D3); half-girth pipes, much thinner hoses; terrace 2's front frozen half way |
| C2 | The Drowned Keep | C | 19 | doors leaking slowly under water (D4): the postern; the winch's GSS power cord (cut it); machine digging the 4 m gatehouse pit; guardrail art; defenders holding fire until drafted (raid branch) |
| C3 | The Labyrinth Rescue | C | 19 | pump power as a GSS power cord; swim-out of a flooded SHEER pit; machine digging Hobb's pit; thinner hose art |
| C4 | The Wet Quarry | C | 13 | a colonist refusing a dig past 2 m; machine digging past 2 m (the sump); deepstone stratum finds |
| C5 | The Fuel Depot | C | 13 | fuel overflow spreads and burns (D5); an acid canal beside the chemfuel; half-girth pipe art |
| C6 | The Tar Seep | C | 9 | the vat's product thing; the drill on a survey hit |
| C7 | The Bathhouse and Water Tower | C | 13 | a blueprint for the two missing pipe cells; the overflowing bath (D2/D4: leaking under the door) |
| C8 | The Canal Lock | C | 11 | Mode B: level holder + sink switched off; a boat; machine-dug 3 m reaches |
| C9 | The Trench Line | C | 9 | wet foxhole: cold feet, shaky aim; defenders holding fire until drafted; raider ladder / fill-in rows proven live |
| C10 | The Rain Basin | C | 11 | overflow Stage 1+ (D1, D2, D6); a limitless BODY marker on a natural pond; rain (global weather) |
| C11 | Prospector's Creek | R | 9 | a rope suspension bridge over the deep run; panners assigned |
| C12 | The Oubliette and the Kennel | C | 15 | flyers and floaters (pit travel); machine-digging the 3-5 m pits |

## Owed C# surfaces
- a Place* 'off' flag (or a toggle proof) so a level holder and a sink can be staged switched OFF (C8 Mode B, idle-stable)
- a fire-at-will/hold-fire bridge surface (raid-branch defenders hold fire until drafted)
- a fire-at-will/hold-fire bridge surface so raid-branch defenders hold fire until drafted (C2, C9)

## Log
- staging vocabulary read: review_map.Review (build_gallery/stage/late_hoses/gizmo_cycle), RM.sign_book/label_line, static_call args '|'-split, IntVec3 'x,z'
- plan: northstar/scenarios/{common,mock_bridge,c01..c12,stage0_swim_pit}.py + northstar/scenarios_map.py + selftest_scenarios_map.py
- 21:45 scenario modules c01..c12 written (data only, plot-local setups)
- 21:52 driver scenarios_map.py + mock_bridge + stage0_swim_pit written; --plan OK after fixes it found (guardrail stuff, ladder on spikes, Mech_Centipede -> Mech_CentipedeBlaster, style refs)
- 21:58 selftest_scenarios_map.py: 107 PASS (probes, layout, signs, pieces, defs, coverage 81/81 bars, MOCK build 10/10 + map R, Stage 0 harness). --mock/--dry-run OK (5308 calls map C). Key sheet written. Bridge HELD by another BENCH helper (reach map option 3) -> Phase 2 skipped: ready for live build.
