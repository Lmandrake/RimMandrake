# FOUNDRY_REBOOT_HANDOFF_202609072130 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609070656`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

A brand-new `--codex-home` used to trigger a Windows UAC "create local account"
dialog per new home (no way to script past it — interrupted the owner twice
today). Fixed: `codex_image.py`'s `seed_codex_home()` now seeds a captured,
already-elevated template (`C:\Users\Mandrake\.codex_sandbox_seed`) into every
new home, so no future worker/new-home use of the Codex image pipeline should
ever pop that dialog again — verified live on a genuinely fresh home (45s, zero
dialogs). If it ever DOES pop again, the template is stale/missing; see
`sandbox_seed_template()`'s own loud stderr warning for the fix.

## What the owner should see

- Two live rulings he made THIS window are done and closed: **vehicle fuel
  widening now filters to the five draught carts only** (`VEHICLE_FUEL_PATCH_UNFILTERED_1`,
  verified live no VVE truck accepts potatoes anymore), and the **Codex N-worker
  queue was built as originally spec'd** (`CODEX_PARALLEL_WORKERS_1`) — 4 jobs/2
  workers measured a real ~1.7x speedup, per-job manifests + rate-limit logging
  both work.
- `IKEE_MYNOCK_ART_REGEN_1`: he said "Do (b)" (go ahead) on this art regen. Ikee's
  south facing is a clean PASS. North facing took 6 live-quota attempts and the
  best candidate is still ~13% off on aspect — paused deliberately (art quality
  is a Fable-tier/his-eye call, not mine to keep grinding solo). Mynock hasn't
  started at all: its donor art is packed in a Unity AssetBundle in 1.6 (no loose
  PNG), so it needs `reading-rimworld-graphics`-style extraction before any
  reference-based generation can begin.
- **Diagnosed but NOT fixed**: Armoury's Proton artillery/mortar damage
  (`OuterRim_Proj_ProtonArtillery`/`ProtonMortar`) is stuck at an un-tuned value
  every load — `Armoury_RangedDamage.xml`'s Replace on `damageAmountBase` runs
  before `Turrets_DamageDoctrine.xml`'s Add creates the field (filed
  `ARMOURY_CROSSFILE_ADD_REPLACE_ORDER_1`, three fix options written, none
  applied). **This overlaps BENCH's own `ARMOURY_PATCH_INNER_MISS_1`**, filed the
  same evening from the identical `harvest_log.py` evidence (8 vs baseline 5
  patch failures) — BENCH found the SAME Add/Replace-ordering pattern on a
  DIFFERENT def pair (`DP_Cannonball`, Dungeon Pack). Neither item cross-
  references the other. Both point at `gen_armoury_patch.py`/
  `gen_armour_patch.py` emitting Add-then-Replace pairs into files whose
  filename order doesn't guarantee the Add runs first — worth fixing as ONE
  generator-level defect rather than two per-defName patches. Whoever picks
  either item up should read both first.
- Two more findings filed this window, neither urgent nor owner-blocked:
  `ARMOURY_DECLARER_ATTRIBUTION_FLIP_1` (a generator-attribution flip needing a
  tiebreak fix) and `ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1` (the Oracle mod's
  shipped About.xml still describes the superseded API-key architecture — the
  2026-09-05 `claude -p` rewrite was never actually turned into tracked work
  until now).

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `BUILDING_THEFT_HAULER_1` — carried, not touched this window. Still exactly as
  filed 2026-09-01; no progress notes since. Next action: read the spec fresh
  (doctrine may have moved since filing) and claim/start.
- `COLD_LOAD_RUN_SHEET_4` — carried, not touched this window. `needs: game-up`;
  game IS up right now (bridge free) — this is the item most ready to pick up
  next. Three specific readings are named in its own spec (FLUID_CANAL_DEBUG_SURFACE_1
  type-visibility probe, DEV_LOG_AUTOOPEN_SUPPRESS_1's two-part test, the
  Behemoth Pack-texture live confirmation); none needs the others.
- `DROID_FDE_GOODWILL_CAP_1` — carried, not touched this window. Filed by BENCH
  2026-09-06; no FOUNDRY notes on it since. Its own spec cites
  `restraining_bolt_technical.md` — note this session ALSO built and verified
  `mandrake.rut.restrainingbolts` (a GoodwillSituationDef capping goodwill by
  bolted-droid count) during the standing review loop; check whether this item
  is already satisfied by that mod before starting fresh work.
- `GRAFFITI_FRAMEWORK_BUILD_1` — carried, not touched this window. Filed
  2026-08-31; no progress notes since. Large scope (five mark families, taunt
  funnel) — read the spec fresh before claiming.
- `IKEE_MYNOCK_ART_REGEN_1` — MY OWN item this window, genuinely mid-flight.
  Ikee south facing: shippable (validate_sprite.py PASS). Ikee north facing: 6
  live-quota attempts, best candidate (`ikee_north_raw_v5.png` in the item's own
  notes) still ~13% off on aspect vs the reference — paused for a Fable-tier/
  owner look rather than continued solo iteration. Mynock: not started at all;
  next action is extracting its donor art from the Unity AssetBundle
  (`mlie.starwarsanimalcollection`, 1.6 has no loose PNG) via the
  `reading-rimworld-graphics` skill before any generation can begin.
- `LIGHTFALL_CHASM_AUTHORING_1` — carried, not touched this window. `needs:
  bridge`. Filed 2026-09-06 with the site already owner-ratified; no FOUNDRY
  notes since filing. Next action: claim, take the bridge, author per
  `forsaken_crags.md` §3.
- `MAPGEN_CONVERGENCE_LOOP_1` — carried, not touched this window. `needs:
  bridge`. Commit log shows OTHER FOUNDRY/BENCH activity landed on the sibling
  `MAPGEN_PAINTER_V1_1`/`MAPGEN_GL_SHEET_1` items this same evening (round-2
  fixes) — read those before touching this one, since "converge until great"
  depends on both inputs being current.
- `SETTLEMENT_VERBS_WAVE_1` — carried, not touched this window. Large build
  (crime/salvage/commerce/social verbs), filed 2026-09-01, no progress notes.
  Depends conceptually on `SETTLEMENT_VISIT_LOOP_1` landing first (same filing
  batch, "two mods" per the owner's own words).
- `SETTLEMENT_VISIT_LOOP_1` — carried, not touched this window. See above; check
  whether `SETTLEMENT_VERBS_WAVE_1` is still blocked on this one specifically
  before starting either.
- `UNUSED_MUTATORS_WORLD_ASSIGNMENT_1` — carried, not touched this window.
  ⚠️ rimflow's own staleness warning: 2 commits (9faf0e43, 23cadd0d) cite this ID
  but neither touches its item file — read `git log --oneline -F --grep=
  "UNUSED_MUTATORS_WORLD_ASSIGNMENT_1:"` before assuming it's unstarted; the
  prose here may already be stale.
- `WORLDMAP_DESERT_BAND_REPAIR_1` — carried, not touched this window. Filed
  2026-09-06, no progress notes since. Ends in a savegame re-freeze — read
  `GAME_STATE_WORKFLOW.md` before touching the frozen world save.

## Traps learned

All four filed to `LESSONS_INBOX.md` this window:
- Codex sandbox-setup UAC trap + fix — see "The one thing to carry forward" above.
- `rimflow claim/start/reassign/bridge take --owner-said "..."` makes YOU act AS
  OWNER (a seat-boundary override), not "record that the owner told my own seat
  to do this" — a routine claim done this way put an item under OWNER instead
  of FOUNDRY and had to be `reassign`'d back.
- A full in-place regen of a generator (`gen_armour_patch.py`) to fix ONE
  targeted bug silently flipped unrelated ops' own/donor attribution
  (`declarer()`'s def-dedup pick is not stable run-to-run) — diff a regen
  before trusting it; hand-edit the one op you meant to fix.
- `jawa/get_def` exposes top-level ThingDef fields but not nested ones like
  `projectile/damageAmountBase` — a Player.log "Failed to find a node" line is
  the more reliable live proof for a patch-op failure than trying to read the
  result back through this tool.

## Closed since the last handoff (24)

- `MODSET_BUILDER_RESTORE_STALE_1` — abc1e7cd
- `RIMMANDRAKE_PITS_BUILD_1` — abc1e7cd
- `PROPERTY_FABRIC_BUILD_1` — ae21392d52ce05e652df917864d73aa42dec362c
- `CODEX_WRAPPER_HARVEST_FIX_1` — 814d4223
- `BUILD_PY_TOOLNAME_SCAN_FALSE_LOSS_1` — 3a8978bfd71cf4c7046fbe0418a63db2a8389b26
- `GL_EMITTER_OBJECT_GAP_1` — 431e0c1ee1145a8731f9eb3d7f5476679dafa9d6
- `FORSAKEN_CRAGS_PREDATORS_BUILD_1` — 620be27ea37c083929951b6e423de123fcc845f9
- `STRUCTUREINJ_RUT_TEMPLATE_DEFECTS_1` — 8ab4d5a68c333a70f3b9cad04f6342dbb539ce70
- `KOTORCORE_ABSORPTION_MISSING_TEXTURES_1` — e5a344af8b2703e5ed1d1166a47918dfba60b0cf
- `DROID_KOTORDROIDS_PORT_WAVE1_1` — 04e05aa50895e66fbccd5b539da983ad9d8c2da1
- `MOISTURE_VAPORATOR_WALL_CLIP_1` — 3b19bf5be87d6c3d7ec35a4c4d64938001bd3f06
- `NINEFOLD_HOOK_DOWNS_NOT_JUST_DEATHS_1` — 0a8e1b5811ad278bc3f153efcb1d974c73806826
- `PAWNFLAVOR_MEGAFAUNA_GEN_DESYNC_1` — 76b485ae7c4519916895b5d8ff3868a3a3002679
- `KOTORWEAPONS_ABSORPTION_CONTENT_NITS_1` — 08ecf392b6a6a568b4c57ad25e0146a365e5d317
- `EDIBLE_GENEPACK_NATIVE_1` — 77c041a43c4250ec562dd7fb763983882e939aae
- `NIGHTSIDE_ICE_DEF_1` — 064d8c99d05e3b0407188744082883909a3b524b
- `CONTAGION_BIOME_PLACEMENT_1` — c0f0b60245089815597eae12889ac38e41d6a3f1
- `HORRORWASTES_BIOME_DISSOLVE_1` — bb437a16
- `LIQUID_BIOMES_MAP_1` — 182c698429e0a7a6c9132f3c7a2334d1f1280f26
- `CORPUS_STATS_VANILLA_CONTROLS_1` — cdaffdcd77190d6cff5cfbd8930d0a8d07caec26
- `DROID_FACTIONS_IN_FROZEN_SAVE_1` — cb0f7506c4dffd0e2c1724d97b210c47248f8e29
- `DROID_DONOR_REFGREP_1` — a7dd778266f52d37d9c323a1c79758a0975cbe74
- `VEHICLE_FUEL_PATCH_UNFILTERED_1` — d4fcfcf2760e968b144d332c6435908fe2af8884
- `CODEX_PARALLEL_WORKERS_1` — 855cb4e6d4b0a2c944c1a64a56864c82d4ec1718

## Filed and still open (12) — the next seat's queue

- `OASIS_LANDMARK_PLACEMENT_1` — Hand-place and hand-name the Oasis landmarks on Weeping Stones tiles with per-site mutator loadouts (uplink/haven/stockpile/dead ring); seep-oasis sit
- `OASIS_MUTATOR_PATCH_1` — Whitelist ZBiome_DesertOasis into vanilla TileMutatorDef Oasis; strip donor snow weathers; re-point forageability; alien-flora swap in additionalWildP
- `KOTORCORE_ADAPTIVESTORAGE_PARENTNAME_1` — Absorbed_Kotorcore_AdaptiveStorageFramework_HiddenSmugglingCompartmentPanels.xml: guy762_SecretFloorPanel_BASE ParentName=AdaptiveStorageBase resolves
- `PAWNFLAVOR_GEN_BEHIND_1` — PawnFlavorPhase2 patches are far behind gen_pawn_flavor_phase2_apply.py, plus two small drifts
- `ARMOURY_DECLARER_ATTRIBUTION_FLIP_1` — gen_armour_patch.py's declarer() flips guy762_*/KotOR* ops between own-mod (Conditional) and donor (FindMod) attribution run-to-run
- `IKEE_MYNOCK_ART_REGEN_1` — Regenerate Ikee (AA_Eyeling) and Mynock art via the improved Codex/native-transparency pipeline
- `SCALD_RIVER_REPAINT_1` — Redirect the Scald's rivers outward on the painted worldmap to match R1 -- R18 step 2, blocked on ASHKARR_RIVER_LEDGER_1, verify tile-by-tile
- `BLIZZARISK_DONOR_CUT_1` — Cherry Picker cut of the Blizzarisk donor def -- R20, owner: donor creature not our canon, remove it from the game
- `GEOTHERMAL_DENSITY_FIELD_1` — Geothermal vent/geyser density field: high at dayside mountain ranges, decaying with distance, zero at the terminator -- R12, stop geysers spawning on
- `ARMOURY_CROSSFILE_ADD_REPLACE_ORDER_1` — Armoury_RangedDamage.xml's Replace on OuterRim_Proj_ProtonArtillery/ProtonMortar damageAmountBase runs before Turrets_DamageDoctrine.xml's Add creates
- `ARMOURY_PATCH_INNER_MISS_1` — Jawa Armoury Rebalance: 3 FindMod blocks report failure though all 3 mods are ACTIVE -- an inner xpath is missing (patch failures 8 vs baseline 5)
- `ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1` — Rewrite OracleHttpClient to shell out to claude -p, per owner's 2026-09-05 in-game-LLM ruling (never tracked as an item)

## Commits

```
b82cdab2 DIRTY_CODE_REVIEW_STANDING_LOOP_1: UtinniShell art-tooling wave complete
65dfc154 UtinniShell art tooling: remove dead Shimmer class, simplify no-op math
5820943b BIOME_FREEZE: owner rulings R31-R34 -- all five Scald rivers flow OUT, elevation is not an argument
3f430593 DIRTY_CODE_REVIEW_STANDING_LOOP_1: UtinniPatches liquid-biomes wave
a07448e6 DIRTY_CODE_REVIEW_STANDING_LOOP_1: RestrainingBolts + RaidRedesigner wave
79d533fe RaidRedesigner: fix stale RoleTag.Released comment citing a nonexistent API
b1655903 DIRTY_CODE_REVIEW_STANDING_LOOP_1: Livestock + SeaBeasts wave, all clean
c745301c DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark Doctrine + DesertVehicleReskin clean
f51159cb Doctrine: add missing sarg.alphabiomes to loadAfter, regen MegafaunaYield
0f2ac051 DIRTY_CODE_REVIEW_STANDING_LOOP_1: 6-file wave, all clean
e3fe4617 DIRTY_CODE_REVIEW_STANDING_LOOP_1: Oracle/StructureInjectionsRUT wave
803338da Worldmap prep: river graph + FungalForest merge plan committed; both items rewritten to the rulings
64a52a6c ARMOURY_PATCH_INNER_MISS_1: filed -- 3 Armoury FindMod blocks fail with all 3 mods ACTIVE
16167308 BIOME_FREEZE: owner rulings R29-R30 -- FungalForest merge follows the paint, the Rot's arc amended
368cec1d rimflow: file ARMOURY_CROSSFILE_ADD_REPLACE_ORDER_1
3d288c12 rimflow: close CODEX_PARALLEL_WORKERS_1
855cb4e6 codex_image.py: seed a new CODEX_HOME's sandbox setup, skip the UAC prompt
aaa7cf15 R18a: river direction is riverDist, not link order -- 'reverse the links' is a no-op
dfbebcff BIOME_FREEZE: propagate R28's mechanical half -- R9 crowns stripped, R20 Blizzarisk removed, R21/R8 fixes, Miasma arc corrected
f2c9ee5f rimflow: block CODEX_PARALLEL_WORKERS_1 on the sandbox-setup finding
abdd9343 CODEX_PARALLEL_WORKERS_1: N-worker codex exec queue, grumpiness detector
01e13dc9 rimflow: BIOME_FREEZE_FABLE_REVIEW_1 started; eight items filed from the R1-R28 rulings
f4ee97b6 BIOME_FREEZE_FABLE_REVIEW_1: owner rulings R26-R28 + the Miasma/Grey Sea measurement
898fbf8f BIOME_FREEZE_FABLE_REVIEW_1: owner rulings R22-R25 + the arc 40-50 measurement
0d199cbd rimflow: IKEE_MYNOCK_ART_REGEN_1 progress note (south facing PASS, north near-miss)
04597ab2 BIOME_FREEZE_FABLE_REVIEW_1: owner rulings R18-R21 -- Blizzarisk cut, river ledger before repaint
ea9333a0 BIOME_FREEZE_FABLE_REVIEW_1: owner rulings R13-R17
fc63c56f BIOME_FREEZE_FABLE_REVIEW_1: owner rulings R9-R12 -- R9 retires the whole superlative-crown group
ffe8710f rimflow: close VEHICLE_FUEL_PATCH_UNFILTERED_1
d4fcfcf2 DesertVehicleReskin: filter fuel widening to draught vehicles only
82f0beb7 BIOME_FREEZE_FABLE_REVIEW_1: owner rulings R5-R8 (fuel finding rejected, water truce, Pyrelands ban, vapour)
57154c18 BIOME_FREEZE_FABLE_REVIEW_1: owner rulings R1-R4 (Scald outflow, river ends, growth law, the planetary wind)
21ff8f46 rimflow: file ARMOURY_DECLARER_ATTRIBUTION_FLIP_1, mark 12 Armoury files clean
972798af Armoury: gate slugthrower AP rule on VERB_MARKERS to stop it hitting IonSlug
4f987088 rimflow: bridge released after COLD_LOAD_RUN_SHEET_4 pass
a87af067 rimflow: COLD_LOAD_RUN_SHEET_4 status note (45c051fb), stays doing
45c051fb COLD_LOAD_RUN_SHEET_4: work the 6-entry run sheet on a fresh full-list load
b12aafb0 rimflow: VEHICLE_FUEL_PATCH_UNFILTERED_1 -- deploy staleness confirmed resolved
d6095c09 rimflow: DROID_FDE_KINDS_REPOINT_1 blocked -- no concrete Droidworks race exists yet
71304431 rimflow: DROID_FDE_GOODWILL_CAP_1 status note, stays doing (123fac9d)
123fac9d DROID_FDE_GOODWILL_CAP_1: implement the restraining-bolt goodwill cap
febf29c3 rimflow: DROID_DONOR_REFGREP_1 closed at a7dd7782
a7dd7782 DROID_DONOR_REFGREP_1: verify the haiku sweep, correct the ABF citation
bd4afd0f rimflow: DROID_FACTIONS_IN_FROZEN_SAVE_1 closed at cb0f7506, cross-note on ASIMOV retirement
cb0f7506 DROID_FACTIONS_IN_FROZEN_SAVE_1: census the frozen world's droid factions/kinds/needs
bf70b43b BIOME_FREEZE_FABLE_REVIEW_1 executed: six Fable dimension reviewers + cross-check over all 30 sheets — ~62 findings (43 above LOW, 11 founding-doc cards incl. THE SCALD OUTFLOW conflict and the Blizzarisk hyperweave violation); _freeze_review_2026-09-07.md (the write-up), _freeze_matrix.csv (30x12 data table), freeze headers stamped on 34 sheets; item stays open for the owner's card rulings
212eec22 rimflow: MAPGEN_CONVERGENCE_LOOP_1 status note, stays doing
ed4d7038 rimflow: MAPGEN_GL_SHEET_1 round-2 note (5cf66cda)
5cf66cda MAPGEN_GL_SHEET_1 round 2: fix screenshot framing, clean mod list, retry logic
f42e1cb9 the_twilight_deep.md: the last sheet — the last ordinary sea; the mat as roof; skylights, kelp, real crowding scoped below; dry-looking bottom rivers; the Deepwater Compact revealed as ark-keepers (dwellings v1, full settlement v2); terminator_sea.md gains the surface/bottom scoping line. THE BIOME CAMPAIGN IS COMPLETE.
d5ec1418 the_grey_deep.md: the Grey Sea's bottom ratified — the statuary; brine pools with underwater shores; the pillar forest as blind navigation; the crusted ill-tempered giant (scrape-sign, glow-mark dread); the ossuary shrimp (man-sized, skeletal-seeming, shy, watching); soluble-mineral treasury; implementation deferred to the diving mods per standing ruling; next = the Twilight Deep
fa90e018 rimflow: MAPGEN_PAINTER_V1_1 round-2 note (e58b94f2)
e58b94f2 mapgen_paint: round 2 -- fix salt-and-pepper regions, recover perim/area
ada283e9 the_scald.md: the last biome sheet — the boiler of the dayside; fouled heart, clean breath; the Contagion revealed as the distillery's filter; welcome blankets, bottom-walker herds, silver shoals, bubble-sailors; two-faith shore; FOUNDRY's salinity question ruled (fouled, not toxic); SCALD_MECHANICS_1 filed. Every biome def on the planet now has a sheet.
6a882ede mode: AFK — owner going offline overnight, no needs:owner items until morning
71c3e0b7 rimflow: CORPUS_STATS_VANILLA_CONTROLS_1 closed at cdaffdcd
cdaffdcd corpus_stats: vanilla control maps + fixed chokepoint proxy
6f7f3eea the_forge.md: biome sheet ratified — three defs one massif; the only unstolen fire; foundry towers as the god-project's smeltery; boiling closed rain and flash-interval flora; fireweed heat-gear economy; Beldons produce tibanna and the Empire holds the harvest (TIBANNA_EMBARGO_PLOT_1 campaign clock); two faiths, no correction; FORGE_MECHANICS_1 filed; next and last = the Scald
b84a5b9e the_pyrelands.md: biome sheet ratified — assembly on the 2026-08-15 fire canon + FireEcology mod; Rakatan quickgrass (taproot+feral crop, the what-you-do-with-it theme); four igniters incl. fire-hawks and furnace-beasts; three families; flame harvest, fire raids, the Sun-Debt reconciliation; PYRELANDS_MECHANICS_1 filed
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-07T19:14:05Z

Uncommitted (say for each whether it is yours or another seat's):

```
M infrastructure/state/codebase_health_last.json
 M src/RimStarWars/BeastLairs/About/About.xml
 M src/RimStarWars/BeastLairs/Defs/ThingDefs_Buildings/RSW_BeastLairs_Buildings.xml
?? "D:\\Luke\\dev\\Rimworld\\Transient\\bench_tools_dump.json"
?? claude_sha.txt
?? design/Jawa/art/gods/busts/.gitignore
?? "design/Jawa/worldbuilding/lua suggestions/"
?? design/Jawa/worldbuilding/review/creature_art/
?? design/Jawa/worldbuilding/review/creature_register.fiftyone_export.json
?? design/Jawa/worldbuilding/review/deck/creature_deck.pptx
?? design/Jawa/worldbuilding/review/deck/creature_deck_manifest.json
?? design/Jawa/worldbuilding/review/furniture_art/
?? infrastructure/state/CODE_REVIEW_STATUS.json.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260902_181509.xml
?? infrastructure/state/codebase_health_last.json.lock
?? infrastructure/state/facts/mlie_creature_defname_map_wave_a.json
?? research/RimMandrake/inspiration/map_injection_2026-09-06/p2_createprefab_export.xml
?? src/RimMandrake/LoadTracer/Assemblies/
```

