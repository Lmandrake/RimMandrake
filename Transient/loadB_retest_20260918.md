# Load B Retest — 2026-09-18 (gizka deactivated, FlowWorks redeployed)

Context: full 634-mod list threw a deterministic NRE in `new Game()` →
RimWorld.ReadingPolicyDatabase.GenerateStartingPolicies on every load earlier tonight.
gizkastowaway deactivated (the untested activation delta), FlowWorks DLL redeployed.
This file proves whether `new Game()` works now and delivers two blocked screenshots.

## 1. new Game() works?
**PASS — the ReadingPolicyDatabase NRE is GONE.**

- Triggered `rimworld/start_debug_game_ready {readiness:playable, pauseIfNeeded:true}` from the menu at ~08:49 UTC.
- `get_game_info` → `status: game_loaded, mapCount: 1, ticksGame: 0`. A map generated; `new Game()` completed.
- Player.log appended region (from byte 2595997) searched for `GenerateStartingPolicies` / `ReadingPolicyDatabase` / `NullReferenceException` in `new Game()`: **NONE.** Log shows `Initializing new game with mods:` then normal map generation.
- VERDICT: deactivating gizkastowaway fixed the deterministic `new Game()` crash. Campaign load is unblocked.

Non-fatal note: one `Error in GenStep: NullReferenceException` at `MapPreview.Patches.Patch_RimWorld_TerrainPatchMaker.GetHashCode` (MapPreview × Geological Landforms interaction, GenStep_Terrain). It is a pre-existing map-preview mod bug, NOT the reading-policy crash — the map still generated to a playable state. Left a few terrain cells null in one patch; cosmetic, does not block.

## 2. Campaign save loads?
**PASS.** Loaded `CANONICAL_ASHKARR_START_2026-09-12.rws` via `rimworld/load_game`.

- Compatibility: `compatible`, recordedModCount 632 / activeModCount 634, missingModCount 0.
- Reached `game_loaded, mapCount: 1, ticksGame: 126810` (real campaign tick count). Now PAUSED.
- Log since load: NO `GenerateStartingPolicies` / `ReadingPolicyDatabase` NRE. The only 2 NRE lines are benign unrelated mod noise (GravTide duplicate-ref, `RimFridge.RimFridgeComponent.StartedOrLoadedGame`) — not the blocker.
- The campaign is loadable again. Save NOT overwritten; game left paused.

## 3. Pyrelands density screenshot
**DELIVERED:** `/mnt/d/Luke/dev/Rimworld/Transient/pyrelands_density3_final_20260918.png` (+ `_sm.png`).

- "Pyrelands" = biome `RM_FE_Pyrelands` (mod `mandrake.rm.pyrelands`), confirmed LIVE plantDensity **3.0**, animalDensity 2.1. (NOT the campaign's `RUT_ExtremeDesert`, which is 0.008 — a naming collision that cost time.)
- Old pyrelands saves (`PYRELANDS_REVIEW.rws` etc.) will NOT load — they need the now-retired `mandrake.rut.fireecology` mod. So I generated a fresh Pyrelands map: set tile 17009 → RM_FE_Pyrelands, `world_commit`, `world_tile_map_generate` → mapId 5, 250×250, 30,952 things. Planted 2 PlayerColony colonists to make it a home map (survives daylight stepping), killed the settlement's hostiles, unfogged all, forced Clear weather, framed a dense fire-grass cluster (~104,128), captured at 8AM.
- The shot shows the tripled density reading clearly: a dense carpet of rust/orange EmberGrass + green Quickgrass fire-flora.
- HONEST CAVEAT: RM_FE_Pyrelands is a FIRE-ecology biome — terrain is mostly RM_FE_Ash_Heavy/Sand with fire-grass clustered on the soil/gravel patches, and the generated map came with an ancient-ruins Settlement parent (walls, derelict trucks) plus a central sand clearing. So it is dense fire-grass on ash, not a uniform lush field. If the owner wants a cleaner field, regenerate with a non-Settlement map parent and clear buildings in-frame.

## 4. FireHawk screenshot
**DELIVERED (with caveats):** `/mnt/d/Luke/dev/Rimworld/Transient/firehawk_wingflap_final_20260918.png` (+ `_sm.png`).

- Loaded `PYRELANDS_REVIEW_20260918.rws` (loads clean, compatible, no NRE). BUT its pre-staged "5 FireHawks at map center" did NOT appear on the loaded map: the save has 4 mapInfo entries yet only ONE map loads (mapId 3, RUT_ExtremeDesert — a Jawa colony under mech attack, garrison NOT cleared). `list_pawns` and `list_things RUT_FireHawk` both find ZERO FireHawks on the loaded map; the 71 `RUT_FireHawk` refs in the save file are a body-size mod's `BS_CachePawnID` cache, not live pawns. So the described setup could not be used.
- FALLBACK: spawned 5 RUT_FireHawks myself, faced south, and captured a close-up (root 11).
- RENDER TRAP worth recording: freshly bridge-spawned FireHawks first read as INVISIBLE in screenshots (present/alive/lit, but pawn layer not captured) — cost several shots. FIX = `game_focus.preflight()` + a ~1.5s settle before `take_screenshot`; colonists rendered fine throughout, so it was capture timing, not missing art. Textures ARE deployed (`FireHawk_Body/_Wing_*.png`), no load errors.
- WHAT I SAW (the still can't prove animation): 5 FireHawks render as pale grey-green segmented flying creatures with curved wing appendages and a faint red under-glow; the wings sit at DIFFERENT flap positions across the birds — i.e. the `PawnRenderNodeProperties_Spastic` wing-flap render tree is live and working. Art reads as a stylized armored flyer, NOT an obviously fiery/orange hawk — owner should eyeball whether that colour read is intended.
- FRAMING CAVEAT: background is dark gravship/lab floor, not clean sand — the map's open-sand cells read as "not visible area" (irregular visible region), and those were the only lit spots that rendered the birds. Save NOT overwritten; game left paused.

## Summary
1. **new Game() — PASS.** The deterministic `ReadingPolicyDatabase.GenerateStartingPolicies` NRE is GONE. Deactivating gizkastowaway fixed the campaign-load blocker.
2. **Campaign save — PASS.** `CANONICAL_ASHKARR_START_2026-09-12.rws` loads to Playing, no reading-policy NRE. Campaign is loadable again.
3. **Pyrelands density — DELIVERED.** `Transient/pyrelands_density3_final_20260918.png` — generated a fresh RM_FE_Pyrelands map (plantDensity 3.0 confirmed live); dense rust+green fire-flora reads clearly. Caveat: fire-ecology biome (ash + clustered fire-grass), generated with a ruins-Settlement parent.
4. **FireHawk — DELIVERED w/ caveats.** `Transient/firehawk_wingflap_final_20260918.png` — the named save's pre-staged birds weren't present on the loaded map (only 1 of its 4 maps loads); spawned 5 fresh, close-up shows the wing-flap render tree working; art reads pale grey-green, not fiery.

State left: game RUNNING, map PAUSED, no save deleted/overwritten. Non-fatal map-gen NRE noted (MapPreview × Geological Landforms TerrainPatchMaker) — pre-existing, cosmetic, does not block loads.
