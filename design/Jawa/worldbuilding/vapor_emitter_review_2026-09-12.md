# Vapor/Smoke/Gas Emitter Review — Ash'karr (offline legs, parts 1-3)

Filed against `VAPOR_EMITTER_PLACEMENT_1`. **Scope: parts 1-3 only** (inventory,
per-type rule proposals, frozen-map audit). **Part 4 (bridge fix-up) is NOT in this
file** — the bridge was held by another seat while this was written; nothing live
was touched.

## Instruments used

- **Def inventory**: the frozen `official` dump, `OFFICIAL-2026-08-29`
  (`infrastructure/state/dumps/REGISTRY.jsonl`), capture
  `2026-08-29T13-30-02Z`, **584 mods**, `modlist_sha 1742630eb6253187`, at
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon
  Studios\DefDump\captures\2026-08-29T13-30-02Z`. All counts below tagged
  **MEASURED** come from parsing that capture's `defs/*.json` directly (not
  `rimsage`, so the exact fingerprint is known and stated here) or from decoding
  the save against its `TileMutatorDef.json`/`BiomeDef.json` shortHash tables.
- **Frozen-map audit**: `CANONICAL_ASHKARR_2026-09-09.rws` (live copy at
  `...\RimWorld by Ludeon Studios\Saves\`, 26.3 MB, last written 2026-09-10
  23:57). Parsed whole with `xml.etree.ElementTree` (0.55 s — small enough to
  read directly, not a "large artifact" in the deflate-grid sense) plus manual
  decode of the world layer's `tileMutatorDefsDeflate`/`tileMutatorTilesDeflate`
  arrays (raw-DEFLATE, `SurfaceLayer.SerializeMutators`/`DeserializeMutators` in
  `Verse`/`RimWorld` source, confirmed via `rimsage` C# read — parallel
  `ushort[]` shortHash + `int[]` tile-index arrays, little-endian).
- ⚠️ **Mod-set caveat**: the save's own `<meta><modIds>` lists **573** mods;
  the official dump was captured at 584. Every one of the 28,126 decoded
  mutator-hash instances resolved cleanly against the official dump's 336
  `TileMutatorDef` shortHashes (0 unresolved), and a biome-hash spot check
  (tiles 0-5) matched `world/ASHKARR_WORLDMAP_tiles.csv` exactly — strong
  evidence the tables are compatible, but not a proven byte-identical mod set.
  Treated as **MEASURED with this caveat noted**, not blind.
- World tile count: **21,872** (matches `ASHKARR_WORLDMAP_tiles.csv`'s 21,872
  data rows exactly, tile-ID-for-tile-ID, confirmed by biome spot check).

## Part 1 — Inventory

**Two mechanism tiers exist, and they matter for the rules in Part 2:**

- **Tier A — colony-map genstep scatterers.** `SteamGeyser` (Core) and
  `GeothermalVent` "sulfur spout" (Odyssey) are placed by `GenStepDef`s
  (`GenStep_ScatterGeysers`, `GenStep_GeothermalVents`) that run **when a
  colony map is generated on a world tile**, not at worldgen. Their count is
  `countPer10kCellsRange` (0.7-1) × `BiomeDef.geyserCountFactor` ×
  `TileMutatorDef.geyserCountFactor` **for `GenStep_ScatterGeysers` only** —
  confirmed in `GenStep_ScatterGeysers.cs`. `GenStep_GeothermalVents` does
  **not** read `geyserCountFactor` at all (confirmed in
  `GenStep_GeothermalVents.cs`): it fires on **every map, unconditionally,
  whenever Odyssey is active** — no biome or mutator gate exists in the
  engine. There is currently no colony map in the save (`<maps>` has 0
  children), so no Tier-A census is possible from this save; that is a Part-4
  question against a live/quicktest map, not this one.
- **Tier B — world-tile `TileMutatorDef`s.** These ARE baked into the
  worldmap/save today and are what Part 3 audits. A tile's mutator list gates
  which Tier-A things generate on it later, and for some vent families
  (Ancient*Vent, VEE geysers) the mutator itself carries the whole family.

| defName | defType | source mod | family | mechanism |
|---|---|---|---|---|
| `SteamGeyser` | ThingDef | Core | steam | `GenStep_ScatterGeysers`, scaled by `geyserCountFactor` |
| `SteamGeysers_Increased` | TileMutatorDef | Odyssey | steam (lever) | `geyserCountFactor=2`; blacklists `Grasslands, GlacialPlain, AB_MechanoidIntrusion, ZBiome_Sandbar_NoBeach, ZBiome_Iceberg_NoBeach, ZBiome_DesertOasis` |
| `VEE_SteamGeysers_Decreased` | TileMutatorDef | Vanilla Landmarks Expanded | steam (lever) | `geyserCountFactor=0` — the "kill it" mutator; **0 tiles use it anywhere on Ash'karr** |
| `GeothermalVent` ("sulfur spout") | ThingDef | Odyssey | steam/sulfur gas | `GenStep_GeothermalVents`, unconditional on any map when Odyssey active — **not gated by `geyserCountFactor`, biome, or mutator at all** |
| `AncientSmokeVent` / `AncientToxVent` / `AncientHeatVent` | ThingDef + matching TileMutatorDef + LandmarkDef | Odyssey | smoke / toxic gas / heat | landmark category `AncientVent`; placed only where that landmark/mutator is assigned |
| `AB_AncientFreezingVent` / `AB_AncientGreyPallVent` / `AB_AncientBloodRainVent` / `AB_AncientDeathPallVent` | ThingDef + TileMutatorDef | Alpha Biomes | cold-gas / grey pall gas / blood-rain gas / death-pall gas | same `AncientVent`-category mechanic, reskinned gas effects |
| `AB_MagmaVent` (ThingDef) / `AB_MagmaVents` (TileMutatorDef) | — | Alpha Biomes | magma/steam | `biomeWhitelist=[AB_PyroclasticConflagration, BiomeGRimphire]`, `chanceOnNonLandmarkTile=0.5` |
| `VEE_RotstinkVent` / `VEE_ToxicVent` / `VEE_SmokeVent` / `VEE_DeadlifeVent` (+ matching TileMutatorDefs) | ThingDef+TMD | Vanilla Landmarks Expanded | rotstink gas / toxic gas / smoke / necrotic ("deadlife") gas | standalone mutators, flat 2.5% chance per non-landmark tile, blacklist only `SeaIce, IceSheet, GlacialPlain` — **not mountain/volcanism-keyed at all** |
| `VEE_SulfurVent` | ThingDef | Vanilla Landmarks Expanded | sulfur gas | building only found via its Blueprint/Frame; no distinct TileMutatorDef found under this exact name in the dump — associated mutator not separately confirmed, flag UNMEASURED |
| `VEE_Volcano` | LandmarkDef + TileMutatorDef | Vanilla Landmarks Expanded | volcanic (steam-adjacent) | landmark category `Mountain` |
| `VEE_VolcanicSandDesert(Flora)` / `VEE_VolcanicRichSoil` / `VEE_UndergroundGasDeposits` | TileMutatorDef | Vanilla Landmarks Expanded | volcanic terrain / underground gas (not an active emitter building) | present in the dump, **0 tiles use any of them on this map** |
| `VHGE_GasGeyser` ("gas geyser") | ThingDef | Vanilla Helixien Gas Expanded | helixien gas | no matching `TileMutatorDef`/`GenStepDef` found by name search — placement mechanism **UNMEASURED**, not fabricated; ties to `hydrology_and_fire_ecology.md`'s "helixien gas pockets on volcanic and deep-desert tiles" design intent, which is a design note, not a confirmed engine hook |
| `IronScruff_PrimordialGeysers` (BiomeDef) | BiomeDef | Primordial Geysers | steam (biome-level lever) | `geyserCountFactor=3`, no new emitter ThingDef — reuses vanilla `SteamGeyser` |
| `RUT_GasVent` | — | (ours, Utinni) | cold gas (propane) | **RULED v1** in `design/Jawa/proposals/propane_gas_deep_design.md` §3 (self-igniting puffs, no depletion until pumped) — **not yet built as a ThingDef**; NOT FOUND in the dump. A design commitment, not an inventory item yet. |
| `VFEPD_GeothermalVent` / `VFEPD_Geyser` / `VFEPD_SmallVent` / `VFEPD_TinyVent` / `VFEPD_SmokeSpewer` / `SmokeSpewer` (Royalty) / generic `Vent`/`WallVent`/etc. | ThingDef | VFE Props and Decor, Royalty, WallStuff, Replace Stuff | decor/building HVAC | **excluded from this inventory** — player-placed furniture, not natural worldgen emitters |

**Count**: **17 emitter-family defName groups MEASURED** as present and
worldgen-relevant against the official dump (counting `VHGE_GasGeyser`'s
mechanism as the one genuine gap, and `RUT_GasVent` as designed-not-built).
Decor/HVAC ThingDefs and one-off quest props (`VQE_Genetron_ThermalVent`) are
inventoried above but excluded from the placement-rule count as non-worldgen.

## Part 2 — Placement rule per type

### Steam — RULED (owner, verbatim, restated only)

> Steam geysers are NOT uniformly distributed. Frequency **radially decays away
> from mountain ranges / overt vulcanism** and reaches **zero before the
> terminator** — the deep nightside and the seam never see them.

Applies to: `SteamGeyser` (the `geyserCountFactor` lever), and by extension
`GeothermalVent` **once** it is given a gate (see finding below — today it has
none). Levers that exist to build this with: `BiomeDef.geyserCountFactor`
(currently `1` on all 10 Ash'karr biomes — the rule is not implemented at the
biome level at all yet) and per-tile `SteamGeysers_Increased` /
`VEE_SteamGeysers_Decreased` mutator assignment (currently used inconsistently
— see Part 3).

### Everything else — PROPOSED (owner rules)

- **PROPOSED — Ancient*Vent family** (`AncientSmokeVent`/`ToxVent`/`HeatVent`
  + the four AB reskins): leave keyed to the `AncientVent` landmark category
  and whatever dungeon biomes carry it (`PoisonForest`, `AB_MechanoidIntrusion`
  "Rust Cathedral" dominate the current map — see Part 3). These are lore
  props on dead-machine/ruin sites, not a climate phenomenon; **no
  mountain/terminator rule should apply to them** — propose a separate rule:
  *allowed only on tiles that already carry an ancient-ruin landmark, banned
  nowhere else that the landmark itself doesn't already exclude.*
- **PROPOSED — `AB_MagmaVents`/`AB_MagmaVent`**: keep the existing engine
  `biomeWhitelist` (`AB_PyroclasticConflagration`, `BiomeGRimphire`) as the
  rule — magma vents belong strictly to volcanic-crater biomes, never a
  general "near mountains" radius. Part 3 found 5/10 current instances sitting
  on biomes **outside** that whitelist (see below) — a cleanup candidate for
  Part 4, not a rule change.
- **PROPOSED — VEE geyser family** (`RotstinkVent`/`ToxicVent`/`SmokeVent`/
  `DeadlifeVent`): these are NOT volcanism-keyed in the engine (flat 2.5%
  chance, only ice biomes excluded) and the review found them clustering by
  **biome type**, not mountains — Rotstink in tropical swamp (`Fever Wood`),
  Toxic in the Rust Cathedral ruin biome, Deadlife split between ruin and
  nightside. Propose ratifying that pattern explicitly: *keyed to biome
  family (swamp → Rotstink, dead-machine ruin → Toxic/Deadlife), not to
  mountain distance; no terminator ban, since none of these are steam.*
- **PROPOSED — `VHGE_GasGeyser` (helixien)**: no confirmed engine placement
  hook (see Part 1 gap). Propose treating `hydrology_and_fire_ecology.md`
  §3B(5)'s stated intent ("volcanic and deep-desert tiles") as the working
  rule until the actual mechanism is found — **flag for a live/source
  follow-up before building anything on it**, since the placement instrument
  itself is UNMEASURED, not just the map audit.
- **PROPOSED — cold-gas family (`RUT_GasVent`, nightside)**: per the item's
  own coupling note, keep this OUT of the steam/terminator ban entirely —
  propose the inverse gate: *allowed only past the propane-lake cold
  threshold (arc ≳ 132, per `the_propane_lakes.md`'s own MEASURED arc range),
  banned dayside.* `RUT_GasVent` is ruled-but-unbuilt, so this is a rule for
  whoever builds it, not an audit finding.
- **PROPOSED — Weeping Stones hot oasis vent-feed** (the review's one
  required decision, per the item's coupling note): `SteamGeysers_Increased`
  is **hard-blacklisted from `ZBiome_DesertOasis`** in the engine (Part 1),
  so the oasis cannot literally carry that mutator. Two live options, ranked:
  1. **(preferred)** Set `ZBiome_DesertOasis`'s own `BiomeDef.geyserCountFactor`
     directly above 1 — this is independent of the blacklisted mutator and
     needs no new def, just a biome field.
  2. A bespoke Ash'karr `TileMutatorDef` (e.g. `RUT_VentFedOasis`) carrying
     its own `geyserCountFactor`/category, if the biome-level lever proves
     too blunt (it would apply to every oasis tile equally, no fine control).
  Either way, this feeds the oasis's water narratively as vent/relic-condenser
  fed per the ruling — it does not require literal `SteamGeyser` buildings to
  exist on every oasis tile.
- **Boundary note, not a rule**: The Contagion's rain-receiving highs
  (`CONTAGION_BIOME_PLACEMENT_1`) are a different family from volcanic steam
  highs — nothing in this review's inventory or proposals touches Contagion
  placement, and none of the emitter types above should be read as
  overlapping it.

## Part 3 — Audit of the frozen map

All counts below are **MEASURED** (world-tile `TileMutatorDef` level, per the
instrument note above). **Colony-map-level `SteamGeyser`/`GeothermalVent`
census is not possible from this save — it holds 0 local maps** (`<maps>` has
zero children); that check is **UNMEASURED**, deferred to whatever live map
Part 4 or a later quicktest builds.

**28,126 total mutator instances across 21,872 tiles**, 0 unresolved hashes.

| type | tiles (MEASURED) | arc range (min–max) | headline finding |
|---|---|---|---|
| `SteamGeysers_Increased` | 54 | 27.6–127.1 | 🔴 **RULE VIOLATION**: 21/54 (39%) sit AT OR PAST arc 90 (the terminator, `ASHKARR_WORLD_DEFINITION.md` line 53), several deep into nightside (up to 127.1) — e.g. tile 12702 (`AB_MycoticJungle`, Capwood, arc 127.1), tile 17410 (arc 123.3), tile 7261 (arc 120.3). Directly contradicts "zero before the terminator." |
| `VEE_SteamGeysers_Decreased` | **0** | — | The engine's only "kill geysers here" mutator is used on **zero tiles anywhere on Ash'karr** — there is currently no active suppression mechanism past the terminator at all. |
| `AncientHeatVent` | 180 | 0.8–117.3 | 92% (164/180) on `AB_MechanoidIntrusion` "Rust Cathedral" — landmark-concentrated as expected; a residual tail past arc 90 exists but this family isn't steam-ruled (see Part 2). |
| `AncientSmokeVent` | 34 | 47.0–110.0 | Dominated by `PoisonForest` (32/34); bimodal arc (dayside cluster + ~90 cluster), consistent with landmark placement, not a violation of anything ruled. |
| `AncientToxVent` | 24 | 11.0–100.9 | `PoisonForest` 18/24; same pattern. |
| `AB_AncientFreezingVent`/`GreyPallVent`/`BloodRainVent`/`DeathPallVent` | 61/42/43/33 | ~5–111 each | All four dominated by `PoisonForest` and `AB_MechanoidIntrusion`; internally consistent ancient-ruin placement, arc range spans both dayside and terminator-adjacent tiles (expected — ruins aren't climate-gated). |
| `AB_MagmaVents` | 10 | 18.7–99.4 | ⚠️ **Whitelist mismatch**: engine restricts this mutator to biomes `AB_PyroclasticConflagration`/`BiomeGRimphire`, but only 5/10 current tiles carry those biomes — the other 5 sit on `AB_RockyCrags` (3) and `ZBiome_Badlands` (2), biomes NOT on the whitelist. Reads as an orphaned mutator surviving a biome repaint, not a fresh placement — a Part-4 cleanup candidate. |
| `VEE_RotstinkVents` | 16 | 40.6–55.8 | 100% (16/16) in `Fever Wood` region, swamp biomes — matches the proposed swamp-keyed rule already. |
| `VEE_ToxicVents` | 91 | 5.5–47.0 | 92% (84/91) on `AB_MechanoidIntrusion` — dayside-only here, no terminator issue. |
| `VEE_SmokeVents` | 5 | 27.5–43.7 | Small sample, `Dune Sea`/`Scald Spine`/volcanic-adjacent biomes. |
| `VEE_DeadlifeVents` | 10 | 2.3–133.0 | Bimodal: 6 on Rust Cathedral (dayside ruin), 2 on nightside `RUT_BlueDesert`/Cinderdark (arc 133) — the nightside pair is a plausible existing example of a correctly cold-appropriate placement, not a violation (this family isn't steam-ruled). |
| `VEE_Volcano` | 1 | 16.6 | Single instance, dayside, on `AB_MechanoidIntrusion` — too small a sample to judge. |
| `VEE_VolcanicSandDesert(Flora)`, `VEE_VolcanicRichSoil`, `VEE_UndergroundGasDeposits` | 0 each | — | Present in the mod, unused anywhere on Ash'karr. |
| `Mountain` (context, not an emitter) | 1,039 | 15.6–176.0 | Mountains exist across the FULL arc range including deep nightside (up to 176) — consistent with the doctrine that ranges are everywhere; it is geyser DENSITY near them, not their existence, that must decay. |

**Bottom line for Part 4**: the steam rule is **not implemented at all** at the
`BiomeDef.geyserCountFactor` level (uniform `1` everywhere on Ash'karr), and
the one per-tile lever that exists (`SteamGeysers_Increased`) was placed
without any terminator awareness — over a third of its instances already
violate the ruling as written. `VEE_SteamGeysers_Decreased` is available and
unused, and would be the natural tool to zero out the nightside/seam per the
ruling. `AB_MagmaVents` has 5 tiles orphaned outside its own whitelist.
Neither of these is touched here — that fix-up is explicitly Part 4's job on
the live bridge.
