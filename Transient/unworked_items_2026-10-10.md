# Unworked items — GimmeSomeSlack, FlowWorks (2026-10-10)

Offline sweep by a BENCH helper. Nothing filed, nothing edited.

## GimmeSomeSlack

State going in (MEASURED 2026-10-10): offline `validation.py` 8/8 PASS (core selftest 836/836, aerial 96/96, hose 129/129,
oracle 44/44). Last live runs 2026-10-09: core 40/40 PASS, aerial 22/22, hose matrix H0 18 PASS + 1 SKIP. Last full
`proof_all` 2026-10-05 (143 PASS). North star DRAFT; owner "conditionally accepted" 2026-10-06
(`GIMMESOMESLACK_NORTHSTAR_VALIDATE_1`, proposed). GS-1/2/4/5/6 from the 2026-10-08 design pass are filed and built
(each owes its own live check). All 5 "items to file" from the GPT full review (VERDICTS.md) were filed; 4 are done,
`CORD_GRAPH_TOPOLOGY_REVISION_1` stays proposed (perf, needs a live frame-time measure first). No code TODO/stub remains
except the theft hook below (grep of Source/, MEASURED).

| what's unworked | evidence | already covered by item? | size | needs owner? |
|---|---|---|---|---|
| **Hose reels never show real flow.** The FlowWorks adapter reflects for `lastMovedUnits`/`lastMovedTick`; FlowWorks has 0 such fields (grep, MEASURED), and 0 defs carry `HosePortExtension`. A reel plumps only from the dev gizmo or a relay. FlowWorks meanwhile shipped its OWN `RM_LiquidHose` (conduit-style tubing, vanilla-conduit placeholder art), so there are two unrelated hoses. The north-star bar `NS_hose_plumps_only_from_powered_pump` is declared UNBUILT. | `GimmeSomeSlack/Source/Hose/HoseFlow.cs:20-24,35`; `Hose/HoseSettings.cs:46-49` ("none is built yet"); `Hose/HosePorts.cs:11`; `validation.py:1508-1510`; `FlowWorks/Defs/Machinery/RM_LiquidLogistics.xml:4-19`; `FlowWorks/Source/LiquidTypes/Building_LiquidPump.cs` | none (FLOWWORKS_HOSE_DEPLOY_DRAG_1 closed as a design note; FLOWWORKS_BUILD_PROGRAM_1 Phase 8 built RM_LiquidHose without touching the reel) | M | **y**: two hoses exist. Is GSS's reel the drawn look of FlowWorks' hose, a separate portable hose, or should one retire? |
| **Power theft has no consequences.** `TapEvents.Drained` has no subscriber; design pass GS-3 says "owner ruling first" (brown-out, discovery, goodwill hit, raiders target the clamp). | `Aerial/CompPowerTap.cs:152` ("NOT designed yet (owner ruling pending)"); `gpt_reviews/DESIGN_PASS_2026-10-08.md:84` | none (ledger grep for theft/TapEvents: 0 GSS hits, MEASURED) | M | **y**: touches goodwill, so it needs a card |
| **Unroutable cords (GPT read A7).** These are still drawn even when routing failed. Classified 2026-10-06 with diagrams, "waiting on his ruling" on the dive-in/dive-out model. 221 unroutable in 5,670 random-base leads, 0 in live records. | `gss_gpt_source_read_2026-10-06.md:68-72`; `Transient/gss_unroutable_examples_2026-10-06/README.md` (Transient, expires ~10-20) | none (ledger grep "unroutable": 0, MEASURED) | S | **y**: his model ruling |
| **No full live re-proof since the fix waves.** About 27 GPT-read fixes landed 2026-10-06 ("None of these has been run live yet"), then GS-1/2/4/5/6 landed 2026-10-09. The 10-09 runs covered core, aerial and the H0 hose matrix only. Carry, relay, maze, style and style-hose were last run 10-04/05, before B11-B13 changed the hose-order code. | `gss_gpt_source_read_2026-10-06.md:60-63`; `northstar/validation_hose_{carry,relay,maze}_202610{04,05}*.json`; `northstar/proof_all_20261005T085243.json` is the latest | partial: GIMMESOMESLACK_NORTHSTAR_VALIDATE_1 (owner validation, not a re-run); each GS item owes only its own row | S (one bridge session) | n |
| **About 20 aerial/hose Mod Settings switches are never flipped by any script.** `validation.py` `suite.toggles` covers the 24 core keys only. By name match these are never set: explosionsCut, fallenWire{Shock,Knockback,Ignites}, keepWiresOnGravship, kineticSway, maxStrands, swayStrength, tapRate, diveThrough, autoResumeDroppedHose, couplingSpacing, defaultFluid, fillWobble, handlingTime, maxLengthDefaults, plumpAmount, tintByContents, useFlowWorksPumps, windCellsPerSecond. | Settings keys: 60 Scribe keys (MEASURED); name-match sweep over `*.py` + `SelfTest/*.cs`: 20 of 31 aerial/hose keys unnamed (MEASURED). A probe that sets keys reflectively under another spelling would be missed, so treat 20 as an upper bound. | partial: FALLEN_WIRE_SHOCK_1 and GRAVSHIP_WIRES_SURVIVE_LAUNCH_1 owe their own toggles | M | n |
| Perf: per-frame DrawMotion rescans per material | VERDICTS.md GSS #11/#12 | CORD_GRAPH_TOPOLOGY_REVISION_1 (proposed; needs live frame-time first) | S | n |
| Render-path PLAUSIBLES A9 (roof change double-draw) and A11 (long ripple cord culled by midpoint) were never looked at | `gss_gpt_source_read_2026-10-06.md:49-50,80` ("left for the looks board") | none (low value; `floorRipple` is off by default) | S | n |
| Multiplayer sync and Scribe job-driver class names were never reviewed | `gss_gpt_source_read_2026-10-06.md:84-85` | none; SL2 row partly covers the second | S | y, only if multiplayer is a goal at all |

## FlowWorks

The sweep was done by a Sonnet helper and its two biggest claims were re-checked by hand. The helper found three things
already in good shape: all 32 GPT review claims are adjudicated in VERDICTS.md and their 8 follow-up items exist
(`FLOW_ORDER_EXTERNAL_INPUT_1` is still proposed); the Mod Settings screen has no gap (a heuristic check); and a first
functional script exists (`validation.py`, `northstar/`, `live_probes/fw_*.py`). The only source TODO is
`LiquidCorrosion.cs:91`, which is latent, low value and S.

| what's unworked | evidence | already covered by item? | size | needs owner? |
|---|---|---|---|---|
| **The lava LiquidDef registry row was ruled into v1 and never built.** The owner card of 2026-09-24 said "Promote lava now". `RM_LiquidDefRegistry.xml` has 0 lava mentions (MEASURED). The Forge has lava terrain, but no FlowWorks liquid row, so no flood, pour or matrix behaviour comes from the registry. | `flowworks_liquid_matrix.md:40-42` (also :105, :132, :178-180); `FlowWorks/Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml` | none live. THEFORGE_RM_MOD_BUILD_1 and FORGE_LAVA_TERRAIN_1 both closed **done** without it, and FLOWWORKS_BUILD_PROGRAM_1 only records the ruling | M | n for the build (already ruled). y only for scope: is lava pumpable, bottleable, flood-capable? |
| **12 generated liquid TerrainDefs are orphans.** Ammonia, Coolant, FuelSap, Ichor, Ooze and WaterMineral, each Shallow and Deep. Each defName occurs in exactly 1 file under `src/` (MEASURED), and none has a LiquidDef. The matrix says coolant and ammonia "stay deferred". | `flowworks_liquid_matrix.md` law 7 (:37-40); grep over `src/` | none | S audit / M build | **y**: delete them (the deletion rule), keep them as a palette, or give them registry rows? |
| **11 river Mod Settings toggles have no proof component**: carryAnimals, carryItems, carryStrangers, countSeasonalFloods, countTorrentialRainFloods, crossingHazardsEnabled, floodSurgeEnabled, pathfinderAvoidsCurrents, riverWorksEnabled, scaleWithRiverSize, weirCatchesDrift | `FlowWorks/validation.py:199-205` `RIVER_TOGGLES_OWED` | partial: SURFACE_RIVER_WEIRS_1 (validated, needs bridge; weirs only) | M | n |
| **The FlowWorksRivers walk has 10 UNCOVERED must-be-true lines**: flier never moved, flood surge, size scaling, carried-item bruise, undrafted routing, drift relevant to the biome, stake-line snap order, all toggles off, levee under a live flood, and others | `design/validation_walks/RimMandrake/FlowWorksRivers.md` (`grep -c UNCOVERED` = 10, MEASURED) | partial: SURFACE_RIVER_WEIRS_1 | M | n. The flier and flood lines need him present (flyer rule) |
| Hose reel and FlowWorks pump are not joined (see the GimmeSomeSlack table, row 1). FlowWorks is the side that owes `lastMovedUnits`/`lastMovedTick` on the pump, or `HosePortExtension` on tanks | `GimmeSomeSlack/Source/Hose/HoseFlow.cs:20-24` | none | (counted once, under GSS) | y |

Already covered, do not re-file: blood-bottle rot (LIQUID_BOTTLE_LOOP_1, BLOCKED); sluice and panning
(FLOWWORKS_QUARRY_DIGGING_1, proposed); ladder art (art is paused); and pits (PIT_SUPERDEEP_COLLAPSE_1,
PIT_TEMPERATURE_SOFTENING_1, FLOWWORKS_PIT_*). UNMEASURED: whether Utinni patches outside the four roots scanned use
the coloured-water terrains.

## File these

Every name below passed `rimflow namecheck` (MEASURED).

1. `HOSE_REEL_WIRE_TWO_HOSES_NO_WATER`: join the GSS reel to FlowWorks pumps and tanks, or rule one hose out. Owner card first.
2. `POWER_THEFT_DECIDE_CLAMP_GETS_CAUGHT`: GS-3, consequences of power theft. Owner card (goodwill).
3. `UNROUTABLE_CORD_DECIDE_DIVE_OR_DRAW`: GPT read A7. Owner ruling on the dive-in/dive-out model; the diagrams are already in Transient.
4. `GSS_PROOF_ALL_RETRY_AFTER_THIRTY_FIXES`: one live `proof_all` covering carry, relay, maze and style after the 10-06 and 10-09 fix waves.
5. `GSS_SWITCHES_PROVE_TWENTY_UNFLIPPED`: settings-flip rows for the aerial and hose tabs.
6. `LAVA_LIQUID_BUILD_PROMISED_BY_CARD`: the ruled lava registry row.
7. `DEFERRED_LIQUID_TERRAIN_AUDIT_TWELVE_ORPHANS`: needs the owner (delete, palette, or rows).
8. `RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED` and `RIVER_WALK_UNCOVERED_PROVE_TEN_LINES`: these could merge into one item.
