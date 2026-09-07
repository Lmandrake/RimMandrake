# FOUNDRY_REBOOT_HANDOFF_202609070656 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609070526`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

The frozen `world/ASHKARR_WORLDMAP_tiles.csv` (a git-tracked, hand-authored planet,
21,872 rows) is edited by small, dry-run-by-default `ashkarr_*.py` scripts under
`src/RimMandrake/Utils/` — never `ashkarr_paint.py`, which regenerates the whole file
from scratch and silently regresses every hand edit since 2026-08-21 (it is refused by
`world/ASHKARR_WORLDMAP_tiles.csv.frozen.json`, which also carries the full provenance
log of every surgical edit made since freezing). The workflow this session used for four
separate biome placements — compute the exact tile list from the CSV + design sheet,
calibrate against a KNOWN sub-total from a sibling doc before trusting a wider
computation, write a small `ashkarr_<name>.py` (dry-run then `--apply`), restamp the
freeze, commit immediately — is now the established pattern; copy it rather than
reinventing per-item. **None of the four edits below have been pushed into the live
running game or the actual `.rws` savegame** — they are CSV-only, matching how every
prior surgical edit in this file's history was done (e.g. commit `e3eb2882`, "the
nightside becomes layers"). Whether a live sync + re-freeze needs to happen before the
owner next plays is worth asking him directly rather than assuming either way.

## What the owner should see

- **Four biome placements painted onto the frozen world this session, CSV-only, not yet
  live-synced**: the widened Contagion (170 tiles), the HorrorWastes/CrystalCaverns/
  IceSheet dissolve into a five-lobe mosaic (2,338 tiles: Blue Desert / `RUT_NightsideIce`
  / PropaneLakes), and the three named seas getting their own biomes (1,135 tiles: the
  Scald / Twilight Sea / Grey Sea). Full derivation and every judgment call flagged in
  each: `design/Jawa/worldbuilding/contagion_placement_candidates.md`,
  `horrorwastes_dissolve_execution.md`, `LIQUID_BIOMES_MAP_1_RECONCILIATION.md`. **Two
  judgment calls in the Contagion pass are real interpretive choices, not measured facts,
  and worth his eye specifically**: which biomes count as "green" and protected (only the
  three the sheet names by defName, not other jungle-reading biomes), and whether Scald
  Spine's own rain=0 tiles should have stayed in "the core" despite the rain-gate rule.
- **A concurrent BENCH/Fable commit (`bb437a16`, "the_sump.md: biome sheet ratified...")
  swept up two of my staged edits via the shared working tree** (the HorrorWastes dissolve
  and part of the NightsideIce paint) — verified byte-for-byte correct against what I
  computed before closing the items, so nothing was lost, but that commit's message and
  attribution don't describe the world-tile work it also contains. Purely a hygiene note,
  not a data problem.
- **The propane lake was NOT painted** — `RUT_PropaneLake` is authored but Umbra's 802
  land tiles all read `water=0`; there is no water tile yet to designate "the lake
  proper," and picking that subset needs the owner's own render review, same as the
  Contagion and dissolve passes got before I painted those.
- One offline research task (`EDIBLE_GENEPACK_NATIVE_1`) fully decompiled a donor DLL and
  wrote the complete native-reimplementation spec, but the actual C# is deliberately
  unwritten — it needs a mod to live in, and that mod needs the Slime gene machine's
  curated gene lists authored with him first (`the_slime.md`'s own Owed list, item one).

## What is half-done, and where it stops

<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `UNUSED_MUTATORS_WORLD_ASSIGNMENT_1` — mine, this window. Step 1 (the full offline
  census: 343 total TileMutatorDefs, 255 unused, each with label/mod/workerClass/
  categories) is genuinely complete now — a first pass wrongly claimed it needed bridge
  access; it doesn't, `TileMutatorDef` dumps offline like any other def type. Next action:
  step 2, a bridge contact-sheet quicktest (one map per candidate mutator), then the
  owner's own keep/cut picks on the review sheet — real bridge + owner work, not mine to
  force through alone.
- `BUILDING_THEFT_HAULER_1` — NOT touched this window; claimed/started 2026-09-07T01:04
  by the prior wave, left there. Mechanism built and clean on a 592-mod load; the
  `MuckrakerChassis_TheftHauler.xml` wiring patch is `MayRequire`-gated on
  `mandrake.rsw.droidworks`, which is NOT active on the owner's live mod list — so there
  is no droid on this modset that can run the theft job at all. Next action needs a
  decision (`DROID_SYSTEM_BUILD_1`) about enabling Droidworks on the full list, not more
  code.
- `GRAFFITI_FRAMEWORK_BUILD_1` — NOT touched this window; claimed/started 2026-09-07T00:06
  by the prior wave. Both remaining C# mechanisms (a reusable `ThoughtWorker` and a
  Harmony postfix on `BreachingGrid.FindBuildingToBreach`) are built and compile clean,
  but were last left UNDEPLOYED (a file-lock hit mid-restart during a sibling fork's
  work). Content — the actual sacred/mural/jest/taunt/cant text and defs — is entirely
  owed. Next action: deploy the assembly, then author content (this needs BENCH/Fable per
  the model ladder, not FOUNDRY solo).
- `LIGHTFALL_CHASM_AUTHORING_1` — NOT touched this window; claimed/started
  2026-09-07T04:39, immediately before this window began, no work logged since. Spec is
  in `forsaken_crags.md` §3, site+name owner-ratified. Next action: take the bridge,
  author the landmark at tile 9023 per that spec.
- `SETTLEMENT_VERBS_WAVE_1` — NOT touched this window; claimed/started 2026-09-07T01:04
  by the prior wave. The claim-fee `FloatMenuOptionProvider` is live-verified correct
  (a real fee computed, the insufficient-silver gate fires with the right message). Blocked
  on a bridge-tooling gap, not this item's own code: `jawa/inventory_transfer` refuses to
  move ANY item into ANY pawn's inventory on this modset (tested 2 items, 2 colonists) —
  check whether that got filed as its own item before re-chasing it here.
- `SETTLEMENT_VISIT_LOOP_1` — NOT touched this window; claimed/started 2026-09-07T00:53
  by the prior wave. Build is complete and reviewed (7 files, correctly extends the
  existing 297-def `Inhabited` engine rather than colliding with it), 0 errors, 0
  warnings, selftests green. Only the live quicktest is owed. Next action: run it via
  bridge.
- `WORLDMAP_DESERT_BAND_REPAIR_1` — NOT touched this window; claimed/started
  2026-09-07T04:39, same moment as `LIGHTFALL_CHASM_AUTHORING_1`, no work logged since.
  Same class of work as this window's four biome-placement passes (repaint the Desert
  def's climate-outlier tiles on the frozen CSV, then re-freeze) — the established
  `ashkarr_*.py` pattern (see "The one thing to carry forward") applies directly; worth
  picking up early next wave since the method is now proven four times over.

## Traps learned

- **`ParentName` silently fails to resolve against a vanilla def with no `Name=`
  attribute on its own XML tag** — confirmed via `ilprobe` against
  `Verse.XmlInheritance.TryRegister`/`GetBestParentFor`: a `ParentName` only matches
  another def registered under a `Name=` attribute, never a bare `defName`, and there is
  no fallback. Hit twice this session (`IceSheet`, then `Lake`/`Ocean` independently by a
  subagent) — every new from-scratch `BiomeDef` this session restates the vanilla shape
  directly rather than inheriting it. Worth checking before writing `ParentName=` against
  ANY vanilla def whose own tag you have not read.
- **A fresh general-purpose subagent asked to do a purely-offline def-dump task can
  wrongly conclude it needs live bridge access and stop short** — the mutators-census
  subagent claimed the full ~336-entry `TileMutatorDef` list "requires live bridge
  access." It doesn't; `DefDump/captures/<latest>/defs/<DefType>.json` has it, same as
  every other def type. Caught by checking the actual deliverable file, not trusting the
  subagent's own completion summary (`grade-the-answer-not-the-exit-code`).
- **A subagent session can hit a false-positive content-safety trip on ordinary fictional
  game content** — a sonnet subagent computing tile placements for "the Contagion" (a
  fictional in-game bio-hazard biome) was terminated mid-task by a `[bio]` classifier
  refusal ("Sonnet 5 can't help with this"), with no way to resume that session. Picked
  the task up directly instead of relaunching a fresh subagent on the same
  disease/sterilization-themed content, to avoid risking the same trip twice.
- **The shared working tree can sweep a session's staged changes into an unrelated
  concurrent commit** — `bb437a16` (a BENCH/Fable commit) picked up two of my staged
  world-tile edits alongside its own `the_sump.md` work. Data was verified correct after
  the fact, but the lesson is to commit IMMEDIATELY after each edit rather than batching,
  to shrink the window another seat's commit can catch your staged files in.

## Closed since the last handoff (25)

- `ARMOURY_GEN_HANDEDIT_DESYNC_1` — f95eacfc
- `LOAD_CONFIG_ERROR_SWEEP_1` — 7f781d1e
- `ARMOURY_ABSORBED_KOTORCORE_DUPES_1` — a24cda4d
- `DROID_RETIREMENT_ORDER_ASSERT_1` — 0f430178
- `DOCTRINE_LOADAFTER_STALE_1` — bf99382b
- `ARMOURY_SWMODS_MODNAME_GAP_1` — 62fbc541
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

## Filed and still open (13) — the next seat's queue

- `ARMOURY_LOADAFTER_STALE_1` — Armoury declares 3 loadAfter packageIds against roughly 40 mods its patches actually target
- `PATCHMODS_LOADAFTER_SWEEP_1` — StarWarsPatches and UtinniPatches have the same undeclared-loadAfter gap; sweep every mod of ours that patches somebody else
- `PATCH_LEDGER_MINUS_ONE_OSCILLATES_1` — 87 patch_ledger entries record an original of -1, and any op emitted onto one oscillates in and out on alternate runs
- `ARMOURY_SUBSTRING_RUNG_TRAP_1` — gen_armoury_patch's 'repeater'/'heavy'/'cannon' substring rung can retune any third-party projectile a turret drags in
- `FUNGALFOREST_RAID_MERGE_1` — Dissolve BMT_FungalForest (an underground def on 425 surface tiles) into its neighbors per the measured cluster table (the Rot; Wasteland at South Cra
- `FUNGAL_SOIL_TRADE_1` — Jawas dig fungal soil from the Rot and haul it to the moisture farms by ship — early money; digging sends distress through the fungal whole and brings
- `MOISTURE_FARM_TEMPLATES_1` — Content injection: several highly plausible moisture-farm templates (homestead, vaporator field, cistern head, compound, ruin) — needed many times ove
- `WORLD_RIVER_COLORS_1` — Color the worldmap's rivers by segment (red headwaters → brackish green/brown jungle → toxic brown/blue termini) and the propane lake slate cyan — Riv
- `SAND_SWIMMERS_MOD_1` — Sand fishing: impassable Deep Sand pools you fish like water, with sand-swimmer analogs (never fish-shaped) — the sand swimmers mod
- `OASIS_LANDMARK_PLACEMENT_1` — Hand-place and hand-name the Oasis landmarks on Weeping Stones tiles with per-site mutator loadouts (uplink/haven/stockpile/dead ring); seep-oasis sit
- `OASIS_MUTATOR_PATCH_1` — Whitelist ZBiome_DesertOasis into vanilla TileMutatorDef Oasis; strip donor snow weathers; re-point forageability; alien-flora swap in additionalWildP
- `KOTORCORE_ADAPTIVESTORAGE_PARENTNAME_1` — Absorbed_Kotorcore_AdaptiveStorageFramework_HiddenSmugglingCompartmentPanels.xml: guy762_SecretFloorPanel_BASE ParentName=AdaptiveStorageBase resolves
- `PAWNFLAVOR_GEN_BEHIND_1` — PawnFlavorPhase2 patches are far behind gen_pawn_flavor_phase2_apply.py, plus two small drifts

## Commits

```
83d0cfe0 rimflow: UNUSED_MUTATORS_WORLD_ASSIGNMENT_1 note — Part 3 census correction landed
9faf0e43 UNUSED_MUTATORS_WORLD_ASSIGNMENT_1: complete the offline census's Part 3
882478f1 rimflow: HORRORS_RAIDING_FACTION_1 note — dissolve dependency cleared, storyteller research still blocks
f3533d85 rimflow: LIQUID_BIOMES_MAP_1 closed (three seas painted; propane lake remains)
182c6984 LIQUID_BIOMES_MAP_1: give the boiling ocean and the two brine seas their own biomes (1,135 tiles)
f9043a52 rimflow: HORRORWASTES_BIOME_DISSOLVE_1 closed, NIGHTSIDE_ICE_DEF_1 paint half confirmed done
bb437a16 the_sump.md: biome sheet ratified — the trap that remembers; R-H9 reconciled (Pyrelands make the tar, the Sump collects it, cold seals it); moat trade + Junker stations; the tar beast joins the Patient family; sump-mice, wick-gardens, booby-trap-weighted dig lottery; SUMP_MECHANICS_1 filed; next = the Pyrelands, ocean-bottom deferred by ruling
a4f4493b rimflow: LIQUID_BIOMES_MAP_1 claimed/started/noted by FOUNDRY (offline half)
b25b9839 LIQUID_BIOMES_MAP_1 (offline half): reconcile the three seas + propane lake to real defs
c0f0b602 CONTAGION_BIOME_PLACEMENT_1: paint the widened Contagion onto the frozen world (170 tiles)
527d7763 the_fever_wood.md: crown revision ratified — giant trees tamed the swamp, wood-road byways, thornbug nectar-for-safety canton (Wookiees/Ewoks), the two-front Feralisk/Ant war and the stand-back doctrine, seep-oils, the deep tentacled thing BUILT with plot-reserved emergence (aquatic sarlacc register); Ants from the They/Them mod pending recognizability check, never an existing faction
0a5f43ca Rimflow ledger: claim, start, and note UNUSED_MUTATORS_WORLD_ASSIGNMENT_1 step 1 completion
23cadd0d UNUSED_MUTATORS_WORLD_ASSIGNMENT_1: Step 1 offline census complete
7e8a390c the_fever_wood.md: biome sheet ratified — the held breath; water from below; the causeway vs the water; the Tenant (one aquifer, one creature, never seen whole; BENCH-designed on delegation, owner veto open); FEVER_WOOD_MECHANICS_1 filed; status table rows for Miasma + Fever Wood
7b8a0b37 rimflow: NIGHTSIDE_ICE_DEF_1 closed (def half; paint half owed)
064d8c99 NIGHTSIDE_ICE_DEF_1: author RUT_NightsideIce (def half only, paint deferred)
73393c46 the_miasma.md: biome sheet ratified — the lifeboat at the drain; breath-tide and the moving salt line; the Working (gene machine stays the Slime's); fever-forged; rainbow flora that never lies; the attar replaces the cut medicine; Wildsteam worship-pilgrimage; MIASMA_MECHANICS_1 filed
ed6d2b8d rimflow: block HORRORWASTES_BIOME_DISSOLVE_1 on its own younger prerequisite NIGHTSIDE_ICE_DEF_1
eb4c22d1 rimflow: block HORRORS_RAIDING_FACTION_1 pending HORRORWASTES_BIOME_DISSOLVE_1's owner-reviewed render
693d24e9 rimflow: EDIBLE_GENEPACK_NATIVE_1 closed (research half)
77c041a4 EDIBLE_GENEPACK_NATIVE_1: decompile GenepacksInjection.dll, verify the edible-genepack mechanism, spec it for native reimplementation
3678700d rimflow: supersede the stale FOUNDRY_REBOOT_HANDOFF_20260906/B/C queue items
6f123b17 rimflow: KOTORWEAPONS_ABSORPTION_CONTENT_NITS_1 closed
08ecf392 KotOR absorption pool: fix 6 of 9 donor content nits, generator-side so a regen never undoes them
ad219169 the_rust_cathedral.md: biome sheet ratified — assembly of ruled canon + this sitting's layer (naming settled, the hum-mood system, coolant canals + kept eels, living bolts drifting in its thoughts, wall ladder, kyber-mind GM); lore partitioned; RUST_CATHEDRAL_MECHANICS_1 filed; next = Miasmic Mangrove
1ee4001d rimflow: PAWNFLAVOR_MEGAFAUNA_GEN_DESYNC_1 closed, SARLACC_NATIVE_HABITAT_1 blocked pending owner review, PAWNFLAVOR_GEN_BEHIND_1 filed
76b485ae gen_pawn_flavor_phase2_apply.py: retired-donor exclusion + --out, mirroring gen_armour_patch.py/gen_megafauna_yield.py
d5a290b8 file LIQUID_TYPES_MOD_1 — data-driven liquid varieties (viscosity/damage/pH/color/opacity, tilemap+worldmap); consumers already ruled across six biomes; the indexing into other mods is the named hard part
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-07T06:09:11Z

Uncommitted (say for each whether it is yours or another seat's):

```
M infrastructure/state/codebase_health_last.json
 M infrastructure/state/queue/BENCH.md
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

