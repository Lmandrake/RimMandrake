# FlowWorks — what is still missing (inventory, 2026-10-05)

Owner request (2026-10-05): *"finish building all remaining functionality in flow works that's missing
across any tickets."* Swept from `rimflow queue FOUNDRY`, `rimflow show` on every FlowWorks-related id,
`infrastructure/state/items/*.md`, the FlowWorks walk and `northstar/validation_v2.py`'s UNBUILT
register (now empty — every walk bar's feature has landed; live proof is separate).

Status key: **BUILT** = built offline this pass or earlier, live verify owed · **BUILD** = buildable
offline, this pass · **OWNER** = needs his ruling · **DEP** = gated on an unbuilt non-FlowWorks item ·
**OUT** = not FlowWorks (boundary: FlowWorks owns what a liquid IS and DOES; machines that transform
one liquid into another live elsewhere).

## Already done before this pass (for the record)

SUPERDEEP_SEAM_MEASURE_1, SUPERDEEP_HOLDER_RETIRE_1, PIT_LEGACY_CODE_RETIRE_1 (e79f8de4f) ·
CANAL_BOTTOM_SPIKES_1 (05b688a81) · LADDER_PRISON_DOOR_1 (cf789dc80) · PIT_COVER_FALL_REWIRE_1
(9d6cefabd) · DEPTH_FILL_COST_MATRIX_1 · FLOWWORKS_CHANNEL_OSCILLATION_1 (ddb473416) ·
FLOWWORKS_DOOR_FAMILY_1 (6359e69b5) · Phase 6 fire (RM_LiquidFire) · PIT_FILL_EFFECTS_1 (eabc44700) ·
PIT_DEPTH_DRAW_OFFSET_1 (0d599e5cd) · PIT_TEMPERATURE_SOFTENING_1 core (5025f7d9a) ·
LIQUID_BODY_FLUID_IDENTITY_1 steps 1, 2b (0a7f01680, 5025f7d9a) · RiverWorks slice 1 (eab81a095).

## Remaining capabilities

| # | Capability | Item | Status | Offline? | Blocker / note |
|---|---|---|---|---|---|
| 1 | ✅ 73408b80e — Enclosed D=4 area is its own room (LAW 2 exception [D]); bed → prison; capture down / convert down from the lip; width rule gates it | SUPERDEEP_PRISON_ROOM_1 | BUILD | yes | Seam measured: walkable D=4 is the same region type as its lip → needs a region/district patch |
| 2 | ✅ 73408b80e — Exposed Prisoner nulled by ideoligion like beggar refusal (Charity precepts' structure) | PIT_TEMPERATURE_SOFTENING_1 | BUILD | yes | Structure ruled ("borrow their structure"); numbers stay PROVISIONAL for his word |
| 3 | Per-body fluid: stock capacity/refill per body.fluid, debug fills per fluid, null-palette log | LIQUID_BODY_FLUID_IDENTITY_1 step 3 | BUILT (earlier today; ledger lagged) | — | closed this pass at 5d5e6cc12 |
| 4 | ✅ revert 73408b80e (rot: no blood row, deferred) — Bottle revert timer (boiling/icy → fresh) and rot (blood → hemopack) from row data | LIQUID_BOTTLE_LOOP_1 | BUILD | yes | Fill-job live failure (2026-09-25) needs a fresh-log live read; source review this pass |
| 5 | ✅ (see log) — Fire: ignition from an explosion with no Fire; extinguishing (rain, foam) | FLOWWORKS_BUILD_PROGRAM_1 Phase 6 owed | BUILD | yes | — |
| 6 | ✅ core (see log) — Canal-dig finds (Quarry concept): lump on the bank, letter on first find per material per map, deep cuts reach deep-drill minerals, mineral-less biome → local rock chunks | FLOWWORKS_QUARRY_DIGGING_1 (FlowWorks half) | BUILD (core) | yes | Per-biome numbers come from MINERALS_WHERE_THEY_BELONG_1's registry (owner numbers review unapproved) — core reads the MAP's own geology until the registry lands |
| 7 | Phase 8 hardware: universal pump (body ↔ tank through §8 TryDebit/TryCredit), barrels | FLOWWORKS_BUILD_PROGRAM_1 Phase 8 | BUILD (slice) | yes | Hoses, per-net adapters (VE PipeSystem) are a later slice |
| 8 | Every mechanic has a Mod Settings toggle | MOD_OPTIONS_RETROFIT_1 (FlowWorks part) | BUILD (audit) | yes | — |
| 9 | Sluice-opening route for drowning; occupant effects live | PIT_FILL_EFFECTS_1 | BUILT | — | live verify; scripting belongs to the validation owner |
| 10 | Wall-face art at 4 depths, spikes art | EXCAVATION_WALL_ART_1 | see below | partly | Census 2026-10-05: no art exists or is ruled |
| 11 | Ladder art (A vs B concepts) | EXCAVATION_WALL_ART_1 | OWNER | — | src/RimMandrake/FlowWorks/art_source/phone_review_2026-09-16/RUT_Ladder_A/B.png unpicked; placeholder stays |
| 12 | Surface-river works slice 2 (weir, stake-line, silt trap, fish catch, drift, breach, ferry) | SURFACE_RIVER_WEIRS_1 | BUILD | yes | Separate mod (RiverWorks); built by a parallel builder this pass |
| 13 | Sluice box + panning | FLOWWORKS_QUARRY_DIGGING_1 (River Works half) | DEP | — | Rivers-carry column of MINERALS_WHERE_THEY_BELONG_1 not built |
| 14 | Water cleaning chain wired to DBH thirst | LIQUID_THIRST_CHAIN_1 | DEP | — | Blocked on LIQUID_BOTTLE_LOOP_1 live fill |
| 15 | Found industrial liquid works (desal, detox, tar refinery, pumping station) | LIQUID_INDUSTRY_SETPIECES_1 | DEP/OUT | — | Wreck-tier set pieces: art + Phase 8 hardware; transformation machines are technology |
| 16 | worldTag authoring + shore repaint on the frozen map | WORLDMAP_LIQUID_TAGS_1 | DEP | — | Code built and loads; authoring waits on the one-time world paint (CLAUDE.md: paint once at the end) |
| 17 | Distillation module | WRECKED_DISTILLATION_MODULE_1 | OUT | — | WreckedMachines; boundary rule |
| 18 | Slime pit solvent, rainbow pools, Forge cycle, Sump kits | GELATINOUSSLIME_PIT_SOLVENT_1, WARSCAR_RAINBOW_POOLS_1, FORGE_CYCLE_MECHANICS_1, SUMP_* | OUT | — | Biome kits that consume FlowWorks; not FlowWorks mechanics |
| 19 | Workshop name check "FlowWorks" | FLOWWORKS_BUILD_PROGRAM_1 Phase 0 | OUT (web) | — | Not a mechanic |

## Progress log (appended as rows land)

- 73408b80e: SUPERDEEP_PRISON_ROOM_1 built + closed; Charity-precept gate on RM_ExposedPrisoner; bottle revert timer.
  Closed on criteria met offline: SUPERDEEP_PRISON_ROOM_1, LIQUID_BODY_FLUID_IDENTITY_1, PIT_FILL_EFFECTS_1, PIT_DEPTH_DRAW_OFFSET_1.
  ⚠️ selftest_flowworks_northstar.py's settings-parity check fails until northstar/site_spec.py SETTINGS lists the
  four new settings (superdeepRoomsEnabled, captureDownEnabled, wardenFromLipEnabled, bottleRevertEnabled) — that
  file belongs to the northstar/densify owner this pass.
