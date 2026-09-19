# BENCH_REBOOT_HANDOFF_202609072200 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609072318`. Everything below is committed and pushed.
**Game and bridge state is the last section — read it before touching the game.**

## 🔑 The one thing to carry forward

**THE SAVEGAME IS THE WORLD. The CSV is a RECORD exported from it, never a rival.**

Ash'karr had two divergent lineages for two weeks and nobody noticed. `world/ASHKARR_WORLDMAP_*.csv`
was seeded by `ashkarr_paint.py`, hand-edited for weeks, and repeatedly *imported into*
the game — while the game itself was being edited independently by the bridge, the debug
menu, and the owner's own hand. Measured against `WORLDMAP_V1_original_e.rws`, the last
state he inspected and approved:

| field | tiles differing |
|---|---:|
| biome | 5,411 |
| **hilliness** | **7,275** — a third of the planet, both directions |
| elevation | 787 |
| **road edges** | the links CSV shared only **77** of the save's **1,399** |

⛔ **And the verification that was supposed to catch this could not fail.** The 2026-09-07
redo imported the CSV wholesale, flattening the planet (`Impassable` 355→56, `Mountainous`
2,428→1,495 — nobody asked for that), then validated live against the same CSV and reported
*"21,872/21,872, 0 mismatches"*. **A 100% match against the artifact you just imported only
proves the import worked. It says nothing about whether the import was WANTED.** Any future
live-vs-CSV validate must state which direction it is evidence for. I made the same mistake
early in this session and told the owner "the biomes check off" on that basis.

## What the owner should see

1. **The globe, after this restart.** It carries two things he has not seen: the propane
   lake's new texture (it was invisible — see below) and `RUT_ComplexStructures`.
2. **`ashkarr_place_complex_structures.py` has NOT been run** — it refuses until its def is
   live, and the def only loads at startup. **This is the first action after the load.**
3. The Forsaken Crags tooltip still shows donor Alpha Biomes text. He raised it; it is
   `BIOME_LABEL_CAMPAIGN_NAMES_1` plus descriptions, unstarted.

## What landed (commits `361dddfd` … `9f9a2e77`)

- **Canon rebased from the save.** `ashkarr_rebase_from_save.py` (new) exports tiles+links
  from a savegame into the canonical CSVs. Old lineage deprecated under
  `world/DEPRECATED_painted_lineage/` with the full account.
- **The intended biomes finally landed on the REAL planet** — three seas, the Blue Desert /
  nightside mosaic (dissolving the cavern biome off the surface), the widened Contagion.
  All replayed cleanly on the corrected base. `HorrorWastes`/`BMT_CrystalCaverns`/
  `IceSheet`/`Ocean` are now 0. **The design was never wrong — its savegame half was
  deferred and owner-gated, and every original commit says so.**
- **The propane lake exists**, 57 tiles, centroid 0.41 of a tile width off the antipode
  ("suspiciously precisely"), outline reaching 3.3× further one way than another ("not
  perfectly circular"). ⚠️ **It is a LIQUID body, not a water body** — owner's correction.
  Terrain carries the generic `Water` tag but NOT `Ocean`/`dbh_ocean`, so nothing treats it
  as drinkable.
- **Roads: no modern road past −10 °C** (owner's rule). It diagnosed an existing defect —
  every one of the 216 sub-−10 °C edges was `StoneRoad`, the DAY road, which is incoherent
  at −78 °C. Now `AncientAsphaltHighway`; 5 straddling edges cut, which is the break.
- **Deep Desert Tribes dispersed** — min separation 9.34→15.94°, linearity 2.64→**1.02**.
  Pure maximin only reached 2.27; spending 2° of separation on roundness did it.
- **Rust Cathedral**: 8 → 137 of 236 tiles carrying a landmark, zero mutator losses.
- **`RUT_ComplexStructures`** — new LandmarkDef + procedurally-drawn icon, placed only where
  a tile already carries ≥6 mutators (261 tiles, top 1.2%).
- **`verify_frozen.py` was failing OPEN** — it reported ✅ CURRENT on a marker with no hash
  at all (`if k in d` skipped absent keys). Fixed; an absent stamp now reads UNSTAMPED.

## What is half-done, and where it stops

- 🔴 **Place the 261 complex-structures landmarks.** `python.exe src/RimMandrake/Utils/ashkarr_place_complex_structures.py --apply`. Blocked only on the restart.
- 🔴 **The biome sheets' stats are stale and now finally valid to redo.** All 34 were
  re-derived mid-session, but against the pre-replay planet, so those numbers are already
  superseded. Re-run against the world as it now stands. `Transient/biome_sheet_rederive.py`
  is a starting point but its subject-detection is weak — 31 of 34 came back UNIDENTIFIED.
- **The owner's meander ruling is unapplied**: *"Only ancient asphalt roads should be
  straight. Meander the rest."* 1,134 living edges; `world/_roads/compose.py` has the
  `STRAIGHT_W` machinery, measured band 0.55–0.70.
- **`world/ASHKARR_WORLDMAP_settlements.csv` is stale** — 121 rows against the world's 96,
  deprecated lineage. A name-matched sync churned 66 rows and was **reverted, not shipped**.
  Rebuilding it from the save while preserving its hand-written `why` column is its own job.
- **A clean landmark baseline against `base_e` is owed** — I overwrote it mid-session and
  then briefly mis-diagnosed a +294 landmark delta by comparing across two different worlds.
- **GravTide flavour gap**: diving works on all four seas (gate is `isWaterBiome`; the seabed
  generator keys on depth+temperature only), but its vents/seeps/drowned-structure layer is
  hardcoded to literal `BiomeDefOf.Ocean`. Needs a Harmony patch, not XML.

## Traps learned

1. 🔴 **Driving the bridge does NOT refresh the bridge lock — only ledger events do.** I held
   it four hours, emitted nothing after the initial claim, and FOUNDRY correctly took it as
   stale at 233 minutes. **Emit a `rimflow` note periodically while holding it.**
2. 🔴 **A peer swapped ModsConfig to 6 mods for a quicktest without backing up the live list.**
   The newest backup was 2 days old and 596 mods. **Recover from the SAVE instead** — every
   `.rws` records `<modIds>` in load order. `modsconfig_from_save.py` (new) does it.
3. ⚠️ **`get_defs` returns only the TYPE NAME for list fields** (`["TerrainThreshold"]`), so a
   field-by-field def diff silently reports complex fields as identical. Read the XML.
4. ⚠️ **`HillinessLabel` is cached on the Tile with no reset anywhere in the engine** — a
   hilliness change is invisible in the tooltip until the world reloads.
5. ⚠️ **A biome painted with the same `texture` as its neighbour is invisible.** `BiomeDef`
   has no colour or material override; `texture` is the only lever.
6. ⚠️ **`TileMutatorDef` has NO visual fields.** Only `LandmarkDef` draws on the world map.
   A dense place with no landmarks reads as barren.
7. ⚠️ Setting a water/liquid biome means setting **hilliness Flat too** — every other liquid
   body on the planet is 100% Flat; I left mountains standing in the lake.
8. ⚠️ **Painting a biome can bury a settlement.** The lake swallowed The Cracking Station;
   `world_lint`'s settlements-on-water check caught it.

## Game / bridge / tree state at wrap

- **Bridge: HELD by BENCH.** Release it if the next window is not continuing this work.
- **Game: LOADING** — relaunched via Steam at ~22:00 on the **restored 599-mod list**, which
  was rebuilt from `WORLDMAP_V10`'s own header after a peer left a 6-mod list in place.
  Expect ~15 minutes.
- **Load `WORLDMAP_V10_cathedral_landmarks_2026-09-07.rws`** — that is the current world.
  V6–V9 are superseded steps of the same evening; V1_original_* are the pre-rebase archive
  and are byte-untouched.
- Tree is clean and pushed through `9f9a2e77`.
