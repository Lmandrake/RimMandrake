# belt bridge7 — fold cleanup deploy + full-list cold load + live checks, 2026-10-09 (helper #6)

## Status
- 22:20 started; read predecessor log + ART_OVERRIDE_FOLD_ALL_1 deploy note.

## (1) Kill, deploy owners, remove 59 ArtOverride mods
- 22:22 killed game (pid 20980). Backups: Player.log -> scratch; ModsConfig -> deployed/config/ModsConfig.before-bridge7_20261009.xml.
- Dry run: Biomes compose already in sync (3290 files, bridge6). Drift applied (all VERIFIED in sync): Shokk (+4 ~1), UtinniPatches (+105 ~1, fold art), JawaRules (DLL hood fix 04916d360), SWBestiary --prune (3 stale swanimals/Dewback masks; masks now at the fold path). FlowWorks game-only leftovers left alone (as bridge6).
- Deleted all 59 *ArtOverride game folders (0 absent, 0 leftover *artoverride dirs). ModsConfig parsed: 612 -> 565 active, 47 artoverride entries dropped (matches the item's 47).

### Decide strings (written before launch)
- Load up: `Bridge token:`. Dead load: `Recovered from incompatible or corrupted mods` / `Caught exception while loading play data`.
- F3 log half: 0 `Failed to find any textures` naming `RimStarWars/SWBestiary/`, `RimStarWars/Shokk/`, `RimUtinni/UtinniPatches/` (and none naming a fold creature at `Things/Pawn/Animal/Megathrips`).
- Fold patches: 0 lines naming `ArtFold` with error; 0 `Could not resolve cross-reference` new vs bridge6 baseline.
- Leather texPath fix: 0 texture errors naming RM_ToxinSealant / RM_RoyalRind / RM_GreatboleGrubSpines / RSW_TelluroxShell.
- Missing-mod warnings for artoverride ids expected 0 (entries dropped).
## (2) Relaunch, Player.log decide strings, art gaps
- 22:24:07 launched via `steam.exe -applaunch 294100` on 565 active.
- F1 offline: art_fold_check 60 creatures, 0 red, 0 unmeasured, Silooth probe PASS.
- Art gaps (offline, during the load):
  - FIXED in src (deploy after this load; takes effect next load): RUT_Fuzz texPath Things/Plant/RUT_Fuzz (never existed) -> Things/Plant/RM_Fuzz (same species, LeaningScrub art). RSW_Zakkro dessicated (no art) -> vanilla Things/Pawn/Animal/Bear/Dessicated_Bear.
  - FILED ART_TEXTURE_GAPS_FOLLOWUP_1: RM_Braskeen/RM_Ismerrow (artpipe renders exist, need art install), KOTOR_SmallCrystal x7(+7 GravTide twins) (art only in the unloaded absorbed donor 3254370945), AA_Swarmling (TheRot points it at RotSpecies/Swarmling, art deleted by card enactment 07ff006d0).
  - Dalgo/Iriaz (same-path SWBestiary), Nuna, Megathrips (same-path UtinniPatches): checked by the log + F3 render below.
- 22:42:11 `Bridge token:` (18 min load, 565 mods). Decide strings (Transient/belt_bridge7_logcheck_20261009r.txt): dead-load 0; texture errors on fold paths (SWBestiary/Shokk/UtinniPatches/Megathrips/Dalgo/Iriaz/Nuna) 0; ArtFold errors 0; artoverride mentions 0; cross-reference errors 0; leather fix errors 0; zersium/alloy errors 0; removed-def/Silooth errors 0; JawaRules errors 0; Config errors 29 (same count as bridge6 baseline). ALL PASS. Only texture miss in the whole log: AA_Swarmling RotSpecies/Swarmling x3 (filed).
- Deployed RUT_Fuzz + Zakkro XML fixes (VERIFIED; next load). Started debug quicktest (start_debug_game_ready).
- texture_audit (27808 paths): 24 dead (was 28: the 4 leather texPaths fixed). Remaining = the filed set + RUT_Fuzz/Zakkro (fixed, next load) + donor Yobshrimp dessicated. No fold path. Transient/belt_bridge7_texaudit_20261009r.txt

## (3) Jawa hood proof on a swimmer — A1 PASS
- Quicktest map is RM_TheRot at ~0-8 C: vanilla GoSwimming FailOns outdoors below 10 C, and still refused after a heat wave (a world-scope condition likely blocks AllowEnjoyableOutsideNow). Fix: walled + roofed pool (Transient/belt_bridge7_hood_room.py).
- TRAP (bridge6 hood script): `jawa/pawn_gear` default action is `equip`; equipping the hood as EQUIPMENT left a pawn throwing NRE in EquipmentTrackerTick every tick (3322 log lines, log window popped over screenshots). Use action=`wear`. Cleared with action=clear clearWhat=equipment.
- Swimming hooded Jawa (GoSwimming, swimming=True, flags=0): applies=True kept=True restoredCan=True canDraw=True. bridge6 read restoredCan=False before 04916d360. -> JAWA_SWIM_HOOD_KEEP_1 validated (A2 L2 / A3 L4 owed).

## (4) Live checks (ZERSIUM_FORGE_BIOME_1, SHIP_ALLOY_FORGE_1 L5, MATERIAL_MERGES_CLEANUP_1, SILOOTH_ART_FOLD_1, ART_OVERRIDE_FOLD_ALL_1 F3)
- SHIP_ALLOY_FORGE_1 L5 PASS: forge prereq [RM_WM_AlloyForgeRestoration], plasteel process prereq [RM_WM_PlasteelAlloying]; RSW_AlloyDurasteel absent by design (no RSW_Durasteel yet). -> validated (L4 owner owed).
- MATERIAL_MERGES_CLEANUP_1 L7 PASS: 11 removed defs notFound, 10 survivors found, 0 cross-ref errors. -> done.
- SILOOTH_ART_FOLD_1: already done (bridge6); this load 0 Silooth errors.
- ZERSIUM_FORGE_BIOME_1 L4 PASS; L5 PARTIAL: Forge player-home maps 250x250 hills carried 24/0/0/0 ore cells, 150 flat 0; non-Forge 0; toggle-off 0 (indistinguishable). Density far below the item's ~660/map estimate; noted in the item. Also fixed validation.py: `RUT_ZersiumForgeProof.Probe` takes one string, so args="" -> "No public static Probe with 0 params"; now args="x". scenelib.biome_map maps are faction-less -> Base_Faction -> never run the GenStep (Transient/belt_bridge7_zersium2.py founds a player home first).
- ART_OVERRIDE_FOLD_ALL_1: implemented at 475863020; F1 L0 PASS; F3 PASS (def texPaths on fold paths, close-ups read, grid Transient/belt_bridge7_f3_grid_20261009r.png; Megathrips occluded, Kreetle/Nuna unframed but defs+audit clean). -> done. F2 note: 3 tracked deployed/config/ModsConfig.before-tier-*.xml still name OLDER artoverride ids (barbslinger, firewasp, boomsnake...) that are not among the 59.
## (5) Remaining acceptance rows
- Triaged the 27 L1 rows; none of the rest is a cheap read on this list/map: UNFINISHED_LINE_* (mod not active in the 565 list), SETTINGS_SCREEN_KIT_1 A5 (known FAIL in bridge2: kit Draw() adopted by no screen; unchanged), TICKER_NEVER_FIRES_FIX_1 A4 (reworded to suppress+repel; needs a powered+fuelled blower and a wild animal in the arc), LASSO A2 (game-down config), the rest need sea-floor / Abyss / FeverWood / Chill maps or save+load. Not attempted.

## Commits
- 5435af0f6 skeleton · 9cf566e55 RUT_Fuzz/Zakkro texPaths + ART_TEXTURE_GAPS_FOLLOWUP_1 · 6b8712529 verifies, item moves, zersium Probe args fix, evidence · final log landing.

## Status at close
- Game UP on the full list minus the fold (565 active), debug quicktest (RM_TheRot, tile 80070), scratch only, never saved. Kobe's broken equipment cleared (log spam stopped). Bridge released.
- Next load picks up RUT_Fuzz + RSW_Zakkro dessicated fixes (deployed).
- OWED: ZERSIUM_FORGE_BIOME_1 density retune then L5 reread (note in item); ART_TEXTURE_GAPS_FOLLOWUP_1; JAWA_SWIM_HOOD_KEEP_1 A2 L2 / A3 L4.
