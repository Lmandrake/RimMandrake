# BENCH_REBOOT_HANDOFF_202609072318 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609070000`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

🔑 **The worldmap is DONE and the three seas exist in game for the first time.**
`WORLDMAP_V4_oasis_rivers_2026-09-07.rws` is the current world: all 21,872 tiles
match the authored CSV with **0 mismatches**, rivers are exactly the authored 584
entries / 308 tiles, and `RUT_TheScald` (312) · `RUT_GreySea` (381) ·
`RUT_TwilightSea` (442) are live biomes rather than vanilla Ocean/Lake.
`BMT_FungalForest` is extinct.

⭐ **And the method that made today work: measure the owner's observation before
believing OR dismissing it.** Every one of his sightings today resolved to a
different cause than it looked like — the oases "following the roads" was the road
router doing its job (3.5× correlation, by design); the "huge amount of oasis" was
unchanged from the CSV; the huge labels were a real 1.63× arithmetic defect; the
broken rivers were 25 genuinely orphaned links. Three of four were not what they
appeared. **Never rule on a sighting without measuring it.**

## What the owner should see

1. 🔴 **The map, after this restart.** It carries three fixes he has not yet seen:
   all six of our biomes now `allowRoads: true` (133 authored road links were
   invisible), the feature-label multiplier 2.2→1.35, and the oasis line broken up.
   **He should look at the globe and rule on whether the labels are now right** —
   they may still be too big because our regions are genuinely enormous, and the
   answer to that is a cap, not a smaller multiplier (`WORLD_FEATURE_LABELS_OVERSIZED_1`).
2. ⭐ **`BIOME_LABEL_CAMPAIGN_NAMES_1` — the cheapest big win available.** 26 of the
   30 painted biomes show DONOR labels: the map says "Cypre Jungle", "Mycotic
   Jungle", "GRimond" where his sheets say the Greentide, the Rot, the Blue Desert.
   One patch file, no defName renames, no map change. He spotted this himself.
3. **`ZBiome_Grasslands` is double-claimed** — it is both "stormy savanna" (now 236
   tiles, the oasis fill) and the def `the_pyrelands.md` claims. He ruled "use it
   anyway, fix the claim later". That fix is owed at the relabelling pass.
4. **`ZBiome_DesertOasis` (204 tiles) has no biome sheet** — it is on the undefined
   list, which is why 200+ oases read as noise.
5. `SETTLEMENT_REJIGGER_ROUND2_1` is released to `needs: bridge` and awaits its own pass.

## What is half-done, and where it stops

- **Nothing is mid-edit. Everything is committed and pushed.** The game is
  RELOADING as he asked; the next window should confirm it reached the menu.
- **`PROJECT_MATURITY_DASHBOARD_1`** — designed in full (two spines, function ×
  content axes, rimflow-owned, Artifact render) but **not built**. Next action:
  write the capability registry schema. ⛔ **Read its anti-friction constraint
  first — the owner explicitly forbade hooks and per-check-in verification.**
- **`MOD_VALIDATION_PLAN_AUTHORING_1`** — filed, nothing authored yet. Next action:
  write one acceptance line per mod for all 76. Offline, no game needed.
- **`WORLD_LINT_WATER_HARDCODE_1`** and **`WORLD_FEATURE_LABELS_OVERSIZED_1`** — the
  label fix IS BUILT AND DEPLOYED (this restart picks it up); the lint fix is
  **not** written yet. One line, `b.isWaterBiome`.
- **`staleMarineMutators 0 → 99`** is filed UNPROVEN. A theory was tested and
  failed; do not repeat it (see Traps).

## Traps learned

1. 🔴 **`world_links_import` with `clearFirst: true` reports `clearedFirst: true`
   and does NOT clear orphans.** It only clears tiles named in the CSV, so links on
   tiles absent from the CSV survive. 25 orphan river links across 39 tiles were
   invisible to it. **Fix: find the extras by diffing a live per-tile sweep against
   the CSV, then `world_links_clear` those tiles by name.** This is what the owner
   saw as "broken rivers".
2. ⚠️ **`riverEntries` staying identical across two imports proves idempotency, NOT
   correctness.** I used that stability to argue the extra links were benign. They
   were orphan stubs on his map. **Stable ≠ right.**
3. ⛔ **Neighbour-majority fills must exclude WATER biomes.** My first oasis pass
   would have painted `RUT_TheScald` and `RUT_TwilightSea` onto dry land.
4. ⚠️ **`build.py` needs `--gm`**, or it drops the GM tool pair and the guard
   reports a long LOSES list. `--allow-tool-removal` is the WRONG answer there.
5. ⚠️ **zsh `nomatch` aborts a whole compound command.** `ls a/*Foo* b/*foo*` with
   one glob unmatched printed nothing and I briefly reported a deployed mod as
   NOT DEPLOYED. Quote globs or test them separately.
6. ⚠️ **`jawa/get_defs` wants `Type/defName` per entry and one entry per call** —
   a comma-joined string is treated as a single malformed id.
7. ⚠️ **Editing `world/ASHKARR_WORLDMAP_tiles.csv` needs `verify_frozen.py
   --restamp`** or every later tool prints a STALE FREEZE STAMP warning.

## Closed since the last handoff (2)

- `NIGHTSIDE_BLUE_DESERT_1` — 4d8f4d7999a3a1c98bebb3f17f85720c57ba6d92
- `CRACKED_LANDS_ENRICHMENT_1` — dd8c7c71d9fd3bfb8c2d39eedd8a102eabf9eb06

## Filed and still open (89) — the next seat's queue

- `GIZKA_TRIBBLE_ADAPTATION_1` — Examine the subscribed (not installed) Tribble module; design the Gizka ship-pest event — cute first, real problem after; check Absorbed_KotorCore for
- `GEONOSIAN_BRAINWORM_MORPH_1` — Research Space Worms mod + Geonosian brain worm canon (Brain Invaders arc), author our own RSW_ brain worms — cold-vulnerable, host-puppeting
- `HORRORS_RAIDING_FACTION_1` — Horrors become a RAIDING faction (no settlements, nightside-gated encounters) + nests/sinkholes/crysalises injected as nightside dungeon content — the
- `OCULAR_OVERDRIVE_SITE_1` — Ocular Forest stays as a named site (the Overdrive, 3 Ashfall Range tiles) + custom dungeon, woven into the plot — Rust Cathedral enmity (45.5° apart,
- `WATER_KINDS_TAXONOMY_1` — Owner: many kinds of water by content + the transmutations between them — inventory every sheet's water, write the taxonomy as data, map onto the live
- `MUTATION_MODIFIERS_SURVEY_1` — Survey every mutation-type system in the stack (Biotech genes, mutagen part-hediffs, SlurryHigh, transformation hediffs) to build Contagion-touched — 
- `BIOME_FREEZE_FABLE_REVIEW_1` — Full-scale Fable review of ALL biomes together before the freeze — temps, physics, weather, precipitation, dust/sand/ash, fuel/wood/animal/meat/growth
- `MECHANOID_BIOME_PRESENCE_REVIEW_1` — Review which biomes contain mechanoids and ancient dangers — not all should; the two magnetic poles (Rust Cathedral, the antistellar war lab) by rulin
- `ANCIENT_WAR_LAB_1` — The war lab beneath the propane lake over the Impact Site — submerged dungeon, lab fauna + mechanoid guardians, and the crater ending as a permanent m
- `TERRAMANUFACTURE_CANON_1` — Propagate the terramanufacture ancient history (dynamo at the substellar pole, Cathedral as remnant, unplanned war lab, mutual learning) into the worl
- `LANTERN_DEEPS_INJECTION_1` — The crystal caverns as an injected underground layer beneath ≤ −40 °C nightside maps — quicktest the cave-map generation, two entrance features (emerg
- `CRYSTAL_MODS_INGEST_1` — Find the orange glowing crystal's source mod; inventory every crystal harvest in the stack; assess ingesting it so all crystals live in the Lantern De
- `MECHANOID_ORIGIN_CANON_1` — The mindstone droid-mind race; mechanoids + Rust Cathedral as a non-artificial AI and the Deeps' crystal minds as their wild cousins; the production f
- `KYBER_TRADE_PLOT_1` — Selling kyber: Empire heat rises per sale, Hutt interest rises, alleged Jedi from the Moisture Farmers, the donate-and-smuggle plot (no helping the Re
- `DROID_ORACLE_VOICE_DESIGN_1` — Design (dormant): four droid Oracle consumers with prescribed fallbacks, claude -p transport
- `DROIDWORKS_LIVE_LOOP_PROOF_1` — Minimal-list quicktest proof of the five-state loop on GNK + a KotOR kind; close the 8 open live checkboxes
- `DROIDWORKS_FULL_LIST_COEXIST_1` — Enable Droidworks in the full mod list beside the donors; cold load, texPath census, Harmony idempotency
- `DROIDWORKS_FORMAT_TIERS_1` — Format tiers blank/mindless/programmable/sapient with needs by tier (ruling 4), work gating, format recipes
- `DROIDWORKS_MODULE_ABSORB_1` — Absorb KotOR's six-slot droid module apparel as RSW_DW_Module_* (loot-only, no recipes)
- `DROIDWORKS_HEADS_BRAINS_SPIKES_1` — Brain trio (import-only), per-family heads with CompHeadIdentity, the mindstone head, per-faction data spikes
- `DROIDWORKS_FINE_PARTS_1` — Fine parts per family (limbs, sensors, motivators, cells) with quality, drop tables and stat/personality effects
- `DROIDWORKS_SHOP_BENCHES_1` — Repair bench, reassembly harness (head-gated), rebuild-from-corpse, overclock as a bench job
- `DROIDWORKS_BOLT_PAYOFF_1` — Restraining bolt consequences: mood aura, rebellion on removal past resentment threshold, shear on damage, un-bolt-each-other
- `DROIDWORKS_ION_SHIELD_BODYSIZE_1` — Ion breaks shields (EMP side-damage) and scales by body size — merge with ION_STUN_IGNORES_BODY_SIZE_1
- `DROIDWORKS_DETONATION_REVIEW_1` — Detonation grid (energyDensity x charge) built and SAVED for the owner to walk; deny-module on JDS battle kinds
- `DROIDWORKS_PRIMITIVE_TIER_1` — Primitive family: Jawa-fabricable frames/parts/modules at grossly inferior stats, the G2 repair droid (new art), the Junker suicide droid
- `DROIDWORKS_WIPE_SEVERITY_1` — Memory wipe: 7-day severe relearning debuff, service-record reset, permanent accreting hardware quirks
- `DROIDWORKS_RESEARCH_ROWS_1` — Seven Droidworks research rows in The Unbolting; cut the Depot droid-brain rows; brains never researchable
- `DROID_FACTION_LOADOUTS_1` — Droids in every faction's hands: Empire attack droids, Homestead utility droids, Hutt heavies, Junker suicide droids, traders' protocol droids, Trade 
- `DROID_FDE_KINDS_REPOINT_1` — Repoint the 4 Jawa_Droid_* FDE kinds and FDE droid backstories onto Droidworks races (fix the generator)
- `DROID_FDE_GOODWILL_CAP_1` — Free Droid Enclaves goodwill cap via GoodwillSituationDef (spec: restraining_bolt_technical.md)
- `DROID_PROTOCOL_TRADE_ADVANTAGE_1` — Protocol droid in the trade party shifts prices both ways; none on your side is a penalty
- `DROID_REPAIR_FOR_PROFIT_EVENTS_1` — Recurring event: friendlies bring droids for paid repair/upgrade; inferior/superior parts choices; offload problem droids
- `DROID_HUTT_CAPTIVES_1` — Droids held in Hutt torture chambers as a rescue-or-purchase source at Hutt sites
- `DROID_DISTRESS_CALL_REPOINT_1` — Re-point the BTD Droid Distress Call quest's 5 KotOR kinds to Droidworks kinds; reframe as the crashed-droid rescue
- `DROID_RETIRE_KOTORDROIDS_1` — Retire guy762.kotordroids (wave R1) after modules, heads, loadouts, FDE repoint and Distress Call are closed; cold load
- `DROID_RETIRE_ABF_SYNCORE_1` — Retire ABF + SynCore (wave R2); DroidDonor_ABFGate fires; remove DroidsAreMachines ABF half; cold load
- `DROID_RETIRE_DEPOT_ASIMOV_1` — Retire Droid Depot + Asimov + MSEDroidFix (wave R3); repoint the Empire KX kind; retire NoDroidManufacture; cold load
- `DROIDWORKS_CHASSIS_PERSONALITY_1` — Per-family starting-trait weights and the protocol-droid pedantry social modifier
- `DROIDWORKS_SERVICE_RECORD_DRIFT_1` — CompServiceRecord: time-since-wipe accretes chassis-weighted idiosyncrasies; wipe resets
- `DROIDWORKS_MODULE_PERSONALITY_1` — Installed modules carry attitudes: CompModulePersonality trait-hediffs while worn
- `DROIDWORKS_WILD_DROIDS_1` — Wild crashed droids: factionless erratic hostiles, capture -> Wild spike -> reprogram-as-recruit with resistance
- `ALPHA_FAMILY_SOURCE_REVIEW_1` — Study the whole Alpha family from its public source (github.com/juanosarg/AlphaBiomes + AlphaAnimals): catalog the C# mechanics, replicate the ones wo
- `FUNGALFOREST_RAID_MERGE_1` — Dissolve BMT_FungalForest (an underground def on 425 surface tiles) into its neighbors per the measured cluster table (the Rot; Wasteland at South Cra
- `FUNGAL_SOIL_TRADE_1` — Jawas dig fungal soil from the Rot and haul it to the moisture farms by ship — early money; digging sends distress through the fungal whole and brings
- `MOISTURE_FARM_TEMPLATES_1` — Content injection: several highly plausible moisture-farm templates (homestead, vaporator field, cistern head, compound, ruin) — needed many times ove
- `WORLD_RIVER_COLORS_1` — Color the worldmap's rivers by segment (red headwaters → brackish green/brown jungle → toxic brown/blue termini) and the propane lake slate cyan — Riv
- `SETTLEMENT_REJIGGER_ROUND2_1` — Round-2 rejigger: re-shift every settlement to fit the pre-frozen biomes — right AFTER BIOME_FREEZE_FABLE_REVIEW_1, BEFORE the animal/plant assignment
- `FISH_BY_BIOME_1` — Fish in every biome where relevant — inventory the stack's fish defs and each biome's fishTypes; rule per water kind (milk, propane, red water, brine)
- `SAND_SWIMMERS_MOD_1` — Sand fishing: impassable Deep Sand pools you fish like water, with sand-swimmer analogs (never fish-shaped) — the sand swimmers mod
- `VAPOR_EMITTER_PLACEMENT_1` — Worldmap review: ALL vapor/smoke/gas emitters — inventory every vent/geyser/smoker type, rule placement per type; steam geysers radially decay from mo
- `MOD_NAMING_CONSOLIDATION_AUDIT_1` — Full review of mod naming/organization: RimMandrake vs RimMaster, consolidation candidates, an ASCII map of how mods relate
- `OASIS_LANDMARK_PLACEMENT_1` — Hand-place and hand-name the Oasis landmarks on Weeping Stones tiles with per-site mutator loadouts (uplink/haven/stockpile/dead ring); seep-oasis sit
- `OASIS_MUTATOR_PATCH_1` — Whitelist ZBiome_DesertOasis into vanilla TileMutatorDef Oasis; strip donor snow weathers; re-point forageability; alien-flora swap in additionalWildP
- `WEEPING_STONES_ROSTER_1` — Weeping Stones flora+fauna roster to the sheet: reconcile the 29 cast, dewback move from LavaField (RULED), sorts-of-animals frame, blade-flora — runs
- `CANON_LORE_PROPAGATION_1` — Wednesday 2026-09-09 after 4pm (token reset): full propagation of canon back into the lore docs, AND re-think the three-layers-of-canon design with th
- `EXPLOSIVE_PLANT_GROWTH_1` — World mechanic: water-soaked plants grow VISIBLY on screen; design the terminal moment (what happens at the top), then custom mod actions so players e
- `FLOOD_WITNESS_EVENT_1` — Plot event: the player witnesses a Cracked Lands flood (chimes, wall of water, explosive growth) at least once — organized as part of the plot, since 
- `GREENTIDE_MECHANICS_1` — The Greentide C# kit: wet-bulb condition+gear, dry-air blower, scald damage+steam devils, Roil/Breaklight weathers, churnmud+causeways, three-feller t
- `WEBWORK_MECHANICS_1` — Webwork C# kit: web-sense felt-marks + pack convergence, concealed-burst ambush, Shokk-bound hediff, light-moat via existing UV-sensitivity mechanism 
- `SHOKKWEAVE_SOLE_SOURCE_1` — Shokkweave economy: rename hyperweave game-wide, strip it from EVERY trader stock table (prove against live trader generation), add the three Webwork 
- `ANCIENT_RUINS_MOD_AUDIT_1` — Deep audit of the ancient-ruins mod (the mall-maps one — identify exact packageId from the live list first): anything redeemable? full ThingDef invent
- `SCARLANDS_MECHANICS_1` — Scarlands C# kit: mynock ship-infestation (board/breed/eat conduit+flooring+lighting/hunt-out), Scarlands mark hediff, plated-grazer scaria onset, Sen
- `STAGED_LORE_DESCRIPTIONS_1` — Engine feasibility: scenario-driven staged descriptions - biome/terrain/def texts that change as lore reveal gates open; Scarlands P/GM ladder is the 
- `LIQUID_TYPES_MOD_1` — Author a liquid-types mod: boiling/frigid/normal water, propane, slime, ooze, tar, acid, poison, mineralized, coolant + more - per-liquid viscosity, d
- `RUST_CATHEDRAL_MECHANICS_1` — Rust Cathedral C# kit: hum-mood system (attitude value, layered tones, bolt-dance display, droid commentary, hysteresis wiring), deep-drill response e
- `MIASMA_MECHANICS_1` — Miasma C# kit: surge/salt-line system (fresh-brine map axis, storm-driven movement, stranding pools), fever-forged boon tables, miasma weather, warden
- `FEVER_WOOD_MECHANICS_1` — Fever Wood C# kit: the Tenant as map-spanning aquifer entity (pool-strike logic, evidence events, never-resolved rule), marsh building-refusal terrain
- `SUMP_MECHANICS_1` — Sump C# kit: poured tar moat + command ignition (smoke wall), dig-lottery tables with era booby traps weighted first, tar beast set-pieces (wake cause
- `PYRELANDS_MECHANICS_1` — Pyrelands C# kit: migrating burn-line presence + burn intelligence, fire-hawk twig-carrying, furnace-beast thermal circuit (heat aura, bed-down igniti
- `FORGE_MECHANICS_1` — Forge C# kit: boiling-rain weather (scald, flash cycle, flash-interval growth), beldon herds + tibanna harvest, vapor-column flight layer, foundry tow
- `TIBANNA_EMBARGO_PLOT_1` — Campaign clock: the Empire's tibanna monopoly at the Forge - metered blaster gas, dwindling resistance ammunition, and the resolution that must come; 
- `SCALD_MECHANICS_1` — Scald C# kit: steam-catch industry, margin fishing + bath recreation, bubble-sailor and bottom-walker set-pieces, geyser fields, boiling-lift integrat
- `ASHKARR_RIVER_LEDGER_1` — Author the lore river ledger: every river named, source-course-fate, built on R1's Scald outflow -- R18 step 1, unblocks the assignment pass
- `SCALD_RIVER_REPAINT_1` — Redirect the Scald's rivers outward on the painted worldmap to match R1 -- R18 step 2, blocked on ASHKARR_RIVER_LEDGER_1, verify tile-by-tile
- `BLIZZARISK_DONOR_CUT_1` — Cherry Picker cut of the Blizzarisk donor def -- R20, owner: donor creature not our canon, remove it from the game
- `GEOTHERMAL_DENSITY_FIELD_1` — Geothermal vent/geyser density field: high at dayside mountain ranges, decaying with distance, zero at the terminator -- R12, stop geysers spawning on
- `POISON_FOREST_REPASS_1` — poison_forest.md second pass: MEASURED block, weather table, R13's chemical venting, struck phrasing removed
- `DONOR_DEFNAME_RECONCILE_1` — Reconcile ten shipping names that differ from their def labels (listed in _freeze_matrix.csv)
- `LANES_DOCTRINE_PARAGRAPH_1` — One paragraph in the grammar README naming the lanes motif: boughways, causeways, root-roads, pillar navigation, oasis strings
- `RAKATAN_LEGACY_INDEX_1` — Rakatan engineered-legacy GM index: quickgrass, scaria, smart metal, the Webwork question, the Scald's makers
- `ARMOURY_PATCH_INNER_MISS_1` — Jawa Armoury Rebalance: 3 FindMod blocks report failure though all 3 mods are ACTIVE -- an inner xpath is missing (patch failures 8 vs baseline 5)
- `UNDERWATER_BIOME_SUPPORT_1` — Underwater biome support: land on the three seas -- looks like ocean, playable seafloor beneath (owner 2026-09-07, later modification)
- `WORLD_LINT_WATER_HARDCODE_1` — world_lint hard-codes Ocean/SeaIce as the only water biomes -- reports all 1135 custom-sea tiles as landBiomeSubmerged
- `PROJECT_MATURITY_DASHBOARD_1` — Project maturity dashboard: two spines (systems function x content, and the GOAL_SHEET content inventory), rimflow-owned, rendered as an Artifact -- t
- `WORLD_FEATURE_LABELS_OVERSIZED_1` — World feature labels render HUGE and overlap the globe -- our maxDrawSizeInTiles multiplier is 1.63x vanilla's
- `MOD_VALIDATION_PLAN_AUTHORING_1` — Author a per-mod automated validation walk for all 76 mods -- a scripted string of checks exercising most of each mod's behaviour, written NOW while c
- `MOD_HUMAN_EXPLORATION_PASS_1` — Human-executable exploration pass: per mod, a scripted in-game walkthrough the owner runs to confirm it looks and feels right -- runs AFTER the art/no
- `BIOME_LABEL_CAMPAIGN_NAMES_1` — Relabel the 26 donor biomes to their campaign names -- the planet currently shows 'Cypre Jungle', 'Mycotic Jungle', 'GRimond' instead of the Greentide

## Commits

```
f9717f5a Oasis line broken up: 32 of 51 road-hugging oasis tiles replaced by their dry neighbours
3e063c2f Note on OASIS_LANDMARK_PLACEMENT_1: roads follow oases by design, measured 3.5x
78697ca1 BIOME_LABEL_CAMPAIGN_NAMES_1: 26 of 30 painted biomes show donor labels, not campaign names
864ac9a5 All our biomes allow roads (owner ruling); world-feature label multiplier 2.2 -> 1.35
6733b891 Retrospective filed as TWO items per owner ruling: automated walk + human exploration
ac8ae245 WORLD_FEATURE_LABELS_OVERSIZED_1: filed -- our label multiplier is 1.63x vanilla
234da798 PROJECT_MATURITY_DASHBOARD_1 filed; cold-load figure corrected to ~15 min on 599 mods
77752af7 Worldmap redo COMPLETE: 21872/21872 tiles, 0 mismatches, the three seas are on the planet
ea547771 WORLD_LINT_WATER_HARDCODE_1: filed -- lint hard-codes Ocean/SeaIce, flags all 1135 custom-sea tiles
ccbe3809 RUST_CATHEDRAL_MECHANICS_1: owner rules the roaches out of the hum mechanics
dfa58f0e RUST_CATHEDRAL_MECHANICS_1: enhanced with the roach reskin (owner 2026-09-07)
931dde5a Decision strings for the GravTide + three-seas load, written before launch
8e4bce2b Sea biomes drafted for GravTide: terrainsByFertility, weather, wander ban; Scald description to R1
b110e188 Worldmap redo: session outcome -- merge complete, rivers laid, new colony, R36 diff passed
ed79d53a UNDERWATER_BIOME_SUPPORT_1: the mechanism exists -- GravTide, subscribed but inactive
20477dce UNDERWATER_BIOME_SUPPORT_1: filed -- land on the three seas, seafloor beneath
9897eb63 Worldmap: FungalForest merged into 5 neighbours (425 tiles); all 16 rivers reordered mouth-first
7d5bc53c Rulings R37-R39: Scald sources at the shore; riverDist is noise not a direction; tile 16869 ruling
58fe2807 FOUNDRY reboot handoff 202609072130
dd0ed072 Worldmap redo run sheet: ordered, gated, with the decision string for the riverDist proof
e7672cc2 BIOME_FREEZE: owner rulings R35-R36 -- R01 drains the Spine's outer flank; the frozen-world safety bar
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
72ce6a2d FOUNDRY_REBOOT_HANDOFF_202609070656: owner-requested reboot, four biome placements painted this wave
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
05d21125 FOUNDRY_REBOOT_HANDOFF_202609070526: owner-requested reboot, two hung agents recovered
ebe38fbe rimflow: bridge release after killing hung LIGHTFALL/WORLDMAP world-editing agent
f4e7b6d3 NINEFOLD_LAUNCH_POSTFIX_FALSE_FIRE_1 + RIVER_STEAM_ANIMATION_1: live-session findings from an interrupted verify agent
cae9fb68 rimflow: recover from a hung bridge-verify agent, block RIVER_STEAM_ANIMATION_1 + STICK_FOOD_INGEST_1
e421a75e the_scarlands.md: biome sheet ratified — the Rakatan last stand with PARTITIONED lore (§P player-facing / §GM reveal ladder, leak ban), Glowers, plated grazers, the mynock comes home with ship infestation, rainbow pools, reclaimable droids, the curse as mechanics; SCARLANDS_MECHANICS_1 + STAGED_LORE_DESCRIPTIONS_1 filed; Scarlands verified vanilla Odyssey
6bca1783 file ANCIENT_RUINS_MOD_AUDIT_1 — the mall-maps mod: identify, grade for redeemables, ThingDef triage, and study its generation tech; Scarlands biome itself verified vanilla Odyssey, not a mod
330951bd rimflow: claim/start WORLDMAP_DESERT_BAND_REPAIR_1, LIGHTFALL_CHASM_AUTHORING_1
8a2cad43 rimflow: close NINEFOLD_HOOK_DOWNS_NOT_JUST_DEATHS_1
0a8e1b58 Ninefold: split the down hook's melee/ranged credit into Ishko too
d83bca5b the_webwork.md: biome sheet ratified, two rounds — the drunk river, a biome-sized creature of shade, the Wyyyschokk canon (mouth-loom, Shokk-bound, the three wars, droid-hatred unexplained), the light-moat, Shokkweave as sole hyperweave; WEBWORK_MECHANICS_1 and SHOKKWEAVE_SOLE_SOURCE_1 filed
38de8a10 Close MOISTURE_VAPORATOR_WALL_CLIP_1: verified drawOffset fix by independent measurement
3b19bf5b rimflow: start NINEFOLD_LAUNCH_POSTFIX_FALSE_FIRE_1
f491c303 rimflow: start MOISTURE_VAPORATOR_WALL_CLIP_1, NINEFOLD_HOOK_DOWNS_NOT_JUST_DEATHS_1; reclaim NINEFOLD_LAUNCH_POSTFIX_FALSE_FIRE_1
14590c59 rimflow: claim/start RIVER_STEAM_ANIMATION_1, MOISTURE_VAPORATOR_WALL_CLIP_1, STICK_FOOD_INGEST_1
eaa7d02e rimflow: close DROID_KOTORDROIDS_PORT_WAVE1_1
04e05aa5 Fix Droidworks recipe skillRequirements XML shape — all 4 recipes were silently discarded at load
618e700e rimflow: close KOTORCORE_ABSORPTION_MISSING_TEXTURES_1, file KOTORCORE_ADAPTIVESTORAGE_PARENTNAME_1
e5a344af File KOTORCORE_ADAPTIVESTORAGE_PARENTNAME_1: dangling ParentName found while closing the texture item
b5974870 KOTORCORE_ABSORPTION_MISSING_TEXTURES_1: supply the 13 (16 measured) missing textures
b28e8481 rimflow: close STRUCTUREINJ_RUT_TEMPLATE_DEFECTS_1
8ab4d5a6 StructureInjectionsRUT: fix toll_gap's invalid Rot4=4, wire glass_sea live
ee2c5248 rimflow: claim/start DROID_KOTORDROIDS_PORT_WAVE1_1, KOTORCORE_ABSORPTION_MISSING_TEXTURES_1, STRUCTUREINJ_RUT_TEMPLATE_DEFECTS_1
3e095082 STARWARS_DONOR_SUNSET_1: re-verify waves 1-3, block on doorsexpanded owner call
30ec13f2 rimflow: close FORSAKEN_CRAGS_PREDATORS_BUILD_1
620be27e Livestock: wire RSW_Cindermare/RSW_Skarnix into AB_RockyCrags wild spawns
1b083990 rimflow: close GL_EMITTER_OBJECT_GAP_1
431e0c1e gl_emit: carry AllowedRiverTypes through worldTileReq; selftest covers all 44 landforms
a6a44980 planet_portrait.py: stylistic two-hemisphere render of Ash'karr from the tiles CSV — naturalistic palette, sun terminator, night emissives and the reconnection aurora; output goes to Transient
473f1cb6 rimflow: close BUILD_PY_TOOLNAME_SCAN_FALSE_LOSS_1
3a8978bf build.py: replace byte-scan tool census with exact DLL metadata read
86f19843 rimflow: drop KOTORWEAPONS_ABSORPTION_DANGLING_REFS_1 (false positive), claim/start GL_EMITTER_OBJECT_GAP_1 + BUILD_PY_TOOLNAME_SCAN_FALSE_LOSS_1
7c4407da rimflow: WEAPONS_DONOR_RETIREMENT_1 blocked, verify step 2 done
40dbc7f9 FOUNDRY_REBOOT_HANDOFF_202609070239: write and check
3c186e88 Reconcile 3 queue items against today's actual Ninefold/Codex work
a42e5a62 the_greentide.md: biome sheet ratified, four rounds — water is the only argument; STEAM/Roil/Breaklight; NO truce; the dying river and its graves; wet-bulb survival, blowers and domes; three fellers, Shatterers, Lungers; the Greatboles you mine and must paint; GREENTIDE_MECHANICS_1 filed
4de79033 rimflow ledger sync: this session's claims/starts/blocks/drops/closes/file
814d4223 Merge graphics-pipeline fixes: harvest-on-timeout, per-worker CODEX_HOME, chroma-key retirement
9ea7e950 codex_image.py: a timeout is not a failed image; per-worker CODEX_HOME; retire the chroma-key generation path
64e09460 Mark 6 files CLEAN after adversarial review + fixes
572413c0 Adversarial review (fresh-context agents): fix 4 real findings
e2d042e2 COLONY_VISIBILITY_BUILD_1: note the csproj fix, live sweep still owed
ad6fef13 SETTLEMENT_VISIT_LOOP_1: debug actions confirmed live-callable; compose proof still blocked on same-tile GetOrGenerateMap no-op + no picker tool
6e6ce2d9 TheftHauler + Visibility: fix silently-excluded debug-action files (real bug)
50e9677f Bank CODEX's second-graphics-pipeline proposal, unvalidated -- do not act on it yet
5c1f7df9 biome status table: weeping_stones + cracked-lands enrichment rows added beside the done sheets; next = Cypre Jungle; _openers_prep marked as decayed on list membership (README table is the authority)
504093ef close CRACKED_LANDS_ENRICHMENT_1 at dd8c7c71
dd8c7c71 the_cracked_lands.md: enrichment backfilled and ratified — time-sorted bestiary (the Sealed/Spenders/Patient, no-truce inversion), water chimes with the owner's tooltip, discovery surveys, crack-wax, NEVER-the-bottom ban; explosive visible growth ruled WORLD-WIDE (EXPLOSIVE_PLANT_GROWTH_1) with a plotted witnessed flood (FLOOD_WITNESS_EVENT_1); grammar README gains the enrichment step
4df56038 SETTLEMENT_VISIT_LOOP_1: log the start_debug_game_ready OOM crash
36d7e0b6 file CANON_LORE_PROPAGATION_1 — Wednesday 2026-09-09 post-reset: canon→lore propagation sweep + the three-layers-of-canon rethink sitting; claim CRACKED_LANDS_ENRICHMENT_1
95cf8525 Weeping Stones rulings landed: truce cheap-for-v1, dewback move RULED, droids never take potable water (propagated to faction_roster_v2 water doctrine); four items filed (landmarks, mutator patch, roster, cracked-lands enrichment backfill)
56f07f2d weeping_stones.md: enrichment pass — bestiary (7 natives + 29-cast reconciliation, dewback mis-cast found), weather+sound (fog at wind-hour, singing vanes), items/structures ladder, 11 faction faces of the water; owner's pass owed
4af94dfb TheftHauler + Visibility: test harness debug actions for the batched live-verification pass (Droidworks not on the live mod list, no other way to reach either mechanism)
bc1ccdb4 Inhabited: add the revisit half of the test harness (casing proof)
7e08f3af Inhabited: build the missing settlement producer (test harness)
09552b98 weeping_stones.md: biome sheet written with the owner — dew+relic engine, biome+landmarks architecture, the truce, the comb convergence, the recapture ladder, seep oases; VAPOR_EMITTER_PLACEMENT_1 filed
89ef5813 File MOD_NAMING_CONSOLIDATION_AUDIT_1 for BENCH: owner asked for a full mod-naming/consolidation review with an ASCII relationship map.
ae21392d COLONY_VISIBILITY_BUILD_1: re-verified clean/deployed, block on live batch
22c43313 NINEFOLD_ENGINE_M0_1: state ledger + hooks CLEAN, block on voice redline
87331ff7 Ninefold: gate Ta'Baa launch credit on CanLaunch, not TryLaunch entry
b0fdd21a FOUNDRY_REBOOT_HANDOFF_202609070028: write and check, owner asked to prepare for reboot
d99aba4a rimflow ledger sync + rebuilt Graffiti/SacredGraffiti assemblies (already deployed)
c5e44c24 Graffiti: fix the absorbed vandal spree never placing a mark (placementMask=Any is backwards); add graffiti test tier
f89eac71 rimflow: close RIMMANDRAKE_PITS_BUILD_1 and MODSET_BUILDER_RESTORE_STALE_1 at abc1e7cd; spawn PITCELL_PRISONER_BED_BRIDGE_GAP_1
abc1e7cd Pits: fix dead Oiled ignite (Flammability 0), root-cause the prisoner-intake gap; modset_builder --restore no longer uses a stale mod-count snapshot
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running; BRIDGE NOT PROBED — no port found in the environment or in Player.log, so LOADING here is a DEFAULT, not a reading.)
- recorded  : LOADING
- Bridge: FREE    since 2026-09-07T23:16:28Z

Uncommitted (say for each whether it is yours or another seat's):

```
M infrastructure/state/codebase_health_last.json
 M infrastructure/state/items/IKEE_MYNOCK_ART_REGEN_1.md
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
 M src/RimStarWars/BeastLairs/About/About.xml
 M src/RimStarWars/BeastLairs/Defs/ThingDefs_Buildings/RSW_BeastLairs_Buildings.xml
 M world/ASHKARR_WORLDMAP_tiles.csv.frozen.json
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

