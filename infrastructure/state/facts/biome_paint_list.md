# Biome paint list — source of truth for the ONE terminal repaint

**What this is.** A registry of every BiomeDef we own (`RM_*`, `RUT_*`, `RSW_*`), kept as
biomes finish, so the terminal painting pass (owner ruling 2026-09-20, see
`infrastructure/state/items/BIOME_PAINT_ONCE_AT_THE_END_1.md`) has a single source of
truth to paint from instead of re-deriving one under time pressure.

🔴 **A biome carrying 0 tiles below is the EXPECTED mid-migration state, not a defect.**
The planet is painted **once**, after every biome is its own mod (owner, 2026-09-20,
verbatim: *"Don't worry about worldmap painting. Once we have all the biomes in mods we
will do the painting once and for all."*). Nothing in this file gates, defers or escalates
any biome's build work on its tile count.

**Provenance of every number below:**
- **defs / build-state columns** — MEASURED live against the def dump, `mods=618/a48bc71544df1a7e captured=2026-09-20T20:14:27Z`, via `measure` (`~/.claude/skills/measuring-large-artifacts/bin/measure`), cross-checked by reading the mod XML on disk under `src/`. XML-derived facts are dated 2026-09-20 (today).
- **tile counts** — read from `world/ASHKARR_WORLDMAP_tiles.csv`, a RECORD exported from the savegame on **2026-09-12**. ⛔ Every tile count in this file is labelled "as of the 2026-09-12 export" and is NEVER a claim about the live planet right now — a live bridge edit after that date is invisible to this file, exactly as it was invisible to the CSV that produced `PYRELANDS_WRONG_BIOME_DEF_1`.
- **campaign region / target mod columns** — from the per-biome sheets in `design/Jawa/worldbuilding/biomes/` and the DRAFT proposal `design/RimMandrake/biome_mod_architecture.md` (owner-blocked, not yet ruled). Every name marked **PROPOSED** is that doc's invention, not an owner-ruled name — do not treat it as decided.

## Table

| defName | label | owning mod (folder / packageId) | active in ModsConfig (2026-09-20) | build state | campaign region(s), 2026-09-12 export | tiles, 2026-09-12 export | paint verdict |
|---|---|---|---|---|---|---|---|
| `RUT_Jawa_BackgroundWater` | mineral water | `UtinniPatches` / `mandrake.rut.patches` | yes | Deliberately minimal (44 lines): `implemented=false`, `isBackgroundBiome=true`, no terrain/plants/fauna/weather. Exists only so `WorldDrawLayer_Terrain.cs` has a background texture for TerrainMask landmarks — see its own header comment. | none — no tile can ever carry it by design | 0, by design | NO PAINT |
| `RUT_AridShrubland` | the arid shrubland | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (182 lines); weather is shared via `mandrake.rm.weathersuite`, not authored per-biome | Damp, Thornbelt, Grey Sea, Ashfall Range, Combs | 628 | PAINT |
| `RUT_BlueDesert` | the Blue Desert | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants present (140 lines); **no `wildAnimals` block found** — fauna not yet authored (tracks the open item `BLUE_DESERT_LIFE_AUTHORING_1` named in the DRAFT architecture doc) | Deadstone, Sootreach, Cinderdark, Ammonia Flats, The Verge | 1029 | PAINT |
| `RUT_Contagion` | the Contagion | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (150 lines) | Dew Horn, Cratercrown, Ashfall Range, Dune Sea | 179 | PAINT |
| `RUT_CrackedLands` | the Cracked Lands | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (162 lines); FROZEN 2026-09-21 with one header comment (`FLOODEDCANYON_RM_MOD_BUILD_1`) — content lives in `mandrake.rm.floodedcanyon` from here on, this def stays byte-for-byte otherwise | Dew Horn, Cracklands, Damp, Dune Sea, Salt | 970 | NO PAINT — content merges into `RM_FloodedCanyon` (Q4 ruled 2026-09-21, verbatim "YES, same place"); frozen, carries the live world until Phase B, deleted then |
| `RUT_Desert` | the Desert | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (305 lines) | Long Sand, Thornbelt, Dry Marches, Combs, Sinkground | 2390 | PAINT |
| `RUT_ExtremeDesert` | the Extreme Desert | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (208 lines) | Dune Sea, Glare, Kiln, Anvil, Long Sand | 3969 | PAINT |
| `RUT_FeverWood` | the Fever Wood | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (232 lines) | Fever Wood | 43 | PAINT |
| `RUT_ForsakenCrags` | the Forsaken Crags | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (141 lines) | Gray Crags, Rimewall, Twilight Crags, Sunreach, Nightspill | 1135 | PAINT |
| `RUT_Greentide` | the Greentide (campaign twin) | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present, 287 lines — the richer of its twin pair | Dune Sea, Cratercrown, Dew Belt, Anvil, Hollow Verge | 235 | NO PAINT — content is slated to merge into `RM_Greentide` (DRAFT §4a); the twin decision itself IS owner-ruled, via closed item `GREENTIDE_STANDALONE_MOD_1` (confirmed at `infrastructure/state/items/closed/GREENTIDE_STANDALONE_MOD_1.md`) |
| `RUT_GreySea` | the Grey Sea | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + fauna present, no plants (104 lines) — sea biome, impassable by design | Grey Sea | 472 | PAINT |
| `RUT_Miasma` | the Miasma | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (254 lines) | Dune Sea, Fever Wood, Dew Horn, Salt Gate, Grey Sea | 93 | PAINT |
| `RUT_NightsideIce` | the Nightside Ice | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + fauna present, no plants by design (173 lines) — DRAFT doc: "thin (no plants by design) but it is a Lantern Deeps host surface" | Deadstone, Sunreach, Gray Crags, Nightspill, Sootreach | 1506 | PAINT |
| `RUT_PoisonForest` | the Poison Forest | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (145 lines) | Dew Belt, Grinding Floor, Twilight Sea, Slough, Sunreach | 546 | PAINT |
| `RUT_PropaneLake` | the Propane Lake | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + fauna present, no plants (158 lines) | Umbra, Ammonia Flats | 57 | PAINT |
| `RUT_RustCathedral` | the Rust Cathedral | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (113 lines) | Rust Cathedral | 236 | PAINT |
| `RUT_Scarlands` | the Scarlands | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (180 lines); ⚠️ its `workerClass` is vanilla `RimWorld.BiomeWorker_Scarlands` (label collision with a vanilla 1.6 biome) — inert either way, no worldgen on this world | Scorch | 90 | PAINT |
| `RUT_Slime` | the Slime (campaign twin) | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present, 106 lines — thinner than its twin | Slough, Glass Reach, Nightspill, Chalk Marches | 96 | NO PAINT — **RULED 2026-09-21 (owner, verbatim: "RM_GelatinousSlime survives"):** content merges into `RM_GelatinousSlime` per the DRAFT doc's §4b proposal; `RUT_Slime` is frozen, carries the live world until Phase B, deleted then |
| `RUT_Sump` | the Sump | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (140 lines) | Nightspill, Glass Reach, Damp, Scour, Twilight Crags | 41 | PAINT |
| `RUT_TheForge` | the Forge | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (176 lines) | Dune Sea, Anvil | 44 | PAINT |
| `RUT_TheRot` | the Rot | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (215 lines) | Nightspill, Frostcaps, Sporefields, Sootreach, Hanging Wood | 2204 | PAINT |
| `RUT_TheScald` | the Scald | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + fauna present, no plants (178 lines) — sea biome | Scald | 312 | PAINT |
| `RUT_TwilightSea` | the Twilight Sea | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + fauna present, no plants (132 lines) — sea biome | Twilight Sea | 607 | PAINT |
| `RUT_FuelSnows` | the Fuel Snows | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (renamed 2026-09-21 from `RUT_Umbra`, content unchanged, `UMBRA_IS_A_REGION_NOT_A_BIOME_1` — "Umbra" now names the region, not this biome) | Deadstone, Umbra, Ammonia Flats, Fuelmere, Lantern Deeps | 0 — RE-MEASURED 2026-09-21 live against the canonical save's own tile array (`worldmap.py`, not the CSV): 0 tiles carry this defName's shortHash. All 2,531 live tiles are still tagged `RUT_Umbra` (see that row) | PAINT — the forward-authored def; target for the terminal repaint |
| `RUT_Umbra` | Umbra (compat duplicate) | `UtinniPatches` / `mandrake.rut.patches` | yes — RESTORED 2026-09-21 | full duplicate of `RUT_FuelSnows`'s content, kept alive only so this defName resolves | Deadstone, Umbra, Ammonia Flats, Fuelmere, Lantern Deeps | 2531 — RE-MEASURED 2026-09-21 (`worldmap.py` decode of `CANONICAL_ASHKARR_START_2026-09-12.rws`'s live `tileBiome` array against a pre-deletion def-dump capture, shortHash 15270): **CONFIRMED, not stale** — the 2026-09-12 export's 2531 figure still holds because nothing has repainted these tiles since. `UMBRA_IS_A_REGION_NOT_A_BIOME_1`'s rename had deleted this defName outright and left these 2531 tiles unresolvable; restored as a compat duplicate pending the terminal repaint. | NO PAINT (temporary) — retire once the terminal repaint moves these 2531 tiles onto `RUT_FuelSnows`; verify with the same live decode before deleting |
| `RUT_Wasteland` | the Wasteland | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + fauna present, no plants (162 lines) | Sunreach, Ashen Wastes, Scour, Salt, Blight | 1853 | PAINT |
| `RUT_Webwork` | the Webwork | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (160 lines) | Dune Sea, Cratercrown, Hollow Verge, Dew Belt, Anvil | 161 | PAINT |
| `RUT_WeepingStones` | the Weeping Stones | `UtinniPatches` / `mandrake.rut.patches` | yes | terrain + plants + fauna present (191 lines) | Dew Belt, Dew Horn, Dune Sea, Cratercrown, Anvil | 223 | PAINT |
| `RUT_LanternDeeps` | lantern deeps | `src/RimUtinni/LanternDeeps` / `mandrake.rut.lanterndeeps` | yes | terrain + plants + fauna present (178 lines), own pocket-map generator; the FROZEN sheet `the_lantern_deeps.md` states it explicitly: "Not a worldmap biome (owner: 'that was a mistake') — an injected underground layer beneath any nightside map" | none by design — no surface tile carries this def; it is injected under nightside maps below −40 °C | 0, by design | NO PAINT |
| `RM_FE_Pyrelands` | the Pyrelands | `src/RimMandrake/Pyrelands` / `mandrake.rm.pyrelands` | yes | terrain + plants + fauna present, 322 lines — the richest def in the whole registry | Pyrelands (per the region column) | 0 under this defName in the 2026-09-12 export — that day the 63 "Pyrelands"-region tiles were recorded under the **donor** `ZBiome_Grasslands`, not this def. A committed comment from a LIVE bridge read on 2026-09-19 asserts the reverse. Which def the tiles carry **right now** is UNMEASURED by this pass — deliberately, per `BIOME_PAINT_ONCE_AT_THE_END_1`: the terminal paint pass reads the live world once and settles it, this file does not. | PAINT — this is the only Ash'karr-owned def for the Pyrelands; `ZBiome_Grasslands` is a *More Vanilla Biomes* donor def, not ours, and is out of scope for this registry |
| `RM_Greentide` | the Greentide | `src/RimMandrake/Greentide` / `mandrake.rm.greentide` | yes | terrain + plants + fauna present, but only 123 lines — a thinner placeholder body than its twin `RUT_Greentide`; the DRAFT plan (§4a) merges the twin's richer content in before the terminal paint | Dune Sea, Cratercrown, Dew Belt, Anvil, Hollow Verge (from its twin's 2026-09-12 tiles) | 0 under this defName in the 2026-09-12 export — all 235 tiles that day were recorded under the twin `RUT_Greentide` | PAINT — ruled survivor of the twin pair, closed item `GREENTIDE_STANDALONE_MOD_1` |
| `RM_FloodedCanyon` | flooded canyon | `src/RimMandrake/FloodedCanyon` / `mandrake.rm.floodedcanyon` | **NOT active** in the campaign's full modlist — a def carrying 0 tiles by design is the expected mid-migration state (`BIOME_PAINT_ONCE_AT_THE_END_1`), not a defect | terrain + plants + fauna present, own generic vanilla-Core body plus 3 ported disease entries (`FLOODEDCANYON_RM_MOD_BUILD_1`); the Star Wars fauna/flora, the campaign weather ban and the "soil only from the flood" terrain override ride `src/RimUtinni/UtinniPatches/Patches/WildAnimals_CrackedLands.xml` as PatchOperationReplace/Add onto this def, not this def's own body — RM_'s generic roster stays intact for a non-campaign world | Cracked Lands | 0 — mod not enabled in the full campaign modlist yet; carries 0 tiles by design until Phase B | PAINT — ruled survivor of the twin pair (Q4, 2026-09-21, "same place"); RUT_CrackedLands merges in and is frozen |
| `RM_GelatinousSlime` | the gelatinous slime | `src/RimMandrake/GelatinousSlime` / `mandrake.rm.gelatinousslime` | **ACTIVE — CORRECTED 2026-09-21.** Confirmed present in `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (620 active mods, parsed via `xml.etree.ElementTree`, not grep). The "NOT active" claim below was true against the 2026-09-20T20:14:27Z capture (618 mods) but is stale as of `SLIME_GENE_ARCHIVE_BUILD_1`'s close (`f8304235e`), whose own prose recorded the mod as live during its quicktest and the doctrinal full list as having been missing it before recapture. | terrain + plants + fauna present, 198 lines, richest of the Slime twin pair; as of today also ships the full 33-target A/B-list gene/kit system (`SLIME_GENE_ARCHIVE_BUILD_1`, live-verified) | Slime (proposed pairing, per its twin's tiles) | 0 under this defName in the 2026-09-12 export (mod was inactive then) — tile count is UNMEASURED now that the mod is active; not remeasured here per `BIOME_PAINT_ONCE_AT_THE_END_1` | **UNDECIDED** — twin pair with `RUT_Slime`; no closed item found ruling which survives, only the DRAFT doc's proposal (§4b). The mod being active removes the previous blocker on that decision. |

Donor def out of scope, noted for context only: `ZBiome_Grasslands` (*More Vanilla
Biomes*) is not `RM_*`/`RUT_*`/`RSW_*` and is not ours — it does not get a row, but it
carried 222 Pyrelands-region tiles in the 2026-09-12 export (see the `RM_FE_Pyrelands`
row above).

No `RSW_*` BiomeDefs were found in the 618-mod def dump or in a source search of `src/`
as of 2026-09-20 — Star Wars content is fauna/flora patched onto RimMandrake/Utinni
biome defs, not its own biome tier (matches `biome_mod_architecture.md` §1: "only Star
Wars creatures become patches").

## Counts

- **PAINT: 25** — all 23 standalone RUT_ regions not otherwise flagged, plus `RUT_FuelSnows`
  (renamed 2026-09-21 from `RUT_Umbra`, forward target for the terminal repaint), and the
  two ruled/uncontested survivors `RM_FE_Pyrelands` and `RM_Greentide`.
- **NO PAINT: 4** — `RUT_Jawa_BackgroundWater` and `RUT_LanternDeeps` (both never carry a
  tile by design), `RUT_Greentide` (its content is owed to `RM_Greentide`, ruled), and
  `RUT_Umbra` (restored 2026-09-21 as a temporary compat duplicate of `RUT_FuelSnows` — see
  its row; carries the live 2,531 tiles until the terminal repaint moves them, then retires).
- **UNDECIDED: 4** — `RUT_CrackedLands` / `RM_FloodedCanyon` (one open twin question),
  `RUT_Slime` / `RM_GelatinousSlime` (one open twin question).
- **Total rows: 33** owned BiomeDefs (25 + 4 + 4).

## Needs an owner decision

1. **Cracked Lands vs Flooded Canyon** (`RUT_CrackedLands` vs `RM_FloodedCanyon`) — are
   these the same place? `biome_mod_architecture.md` §4d / §7 Q4 asks this directly; until
   answered, neither def's paint verdict can be finalized, and `mandrake.rm.floodedcanyon`
   is also not in the active mod list.
2. **Slime twin** (`RUT_Slime` vs `RM_GelatinousSlime`) — the DRAFT doc proposes
   `RM_GelatinousSlime` as the survivor (richer article, existing gene/kit system, now also
   the full A/B-list built 2026-09-21) but, unlike Greentide, no closed item was found
   actually ruling it. Needs an explicit owner call. **CORRECTED 2026-09-21:
   `mandrake.rm.gelatinousslime` is already active** (confirmed in
   `ModsConfig.FULL.LATEST.xml`) — the mod-activation blocker no longer applies, only the
   ruling itself is outstanding.
3. **Whole architecture doc is DRAFT.** `design/RimMandrake/biome_mod_architecture.md` is
   marked "DRAFT for owner review; builds nothing" with its own §7 list of open questions
   (naming, the Scarlands worker collision, the Pyrelands rename, flora ownership, etc.).
   Every "target RimMandrake mod" name in this file's build-state notes that traces to
   that doc is PROPOSED, not decided — the current, real owning mod for 26 of these 32
   defs is still the single `mandrake.rut.patches` (UtinniPatches) mod, not a per-biome
   RimMandrake mod. That is the expected mid-migration state, not a defect.

## Unmeasured

- Whether `RM_FloodedCanyon`'s mod **folder** exists in the live Steam Mods directory (only
  its absence from `ModsConfig.xml` was checked here). `RM_GelatinousSlime`'s is confirmed
  active as of 2026-09-21 — see its row above — so this no longer applies to it.
- The **live**, right-now BiomeDef under the Pyrelands tiles (deliberately not measured by
  this pass — see the `RM_FE_Pyrelands` row and `BIOME_PAINT_ONCE_AT_THE_END_1`).
- Full completeness (hediffs, game conditions, mod-settings gating) per biome beyond
  terrain/plants/fauna presence — this pass checked structural presence of those three
  blocks only, via `grep` on each biome's own small source XML file (not a large-artifact
  scan; the def dump and disk source agree on which files exist).
