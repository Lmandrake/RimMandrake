# Editing the planet offline in a savegame

## 10. ⭐ PROVEN: editing the planet offline in a savegame

**2026-08-15, end to end, verified by the engine.** `src/RimMandrake/Utils/worldmap.py`.

```python
from worldmap import WorldGrid
g = WorldGrid(save_path)                       # decodes the SurfaceLayer
targets = [i for i, n in enumerate(g.biome_names()) if n == "BorealForest"]
g.set_biome(targets, "ExtremeDesert")
g.set_scalar("tileRainfall", targets, 40)
g.write(out_path)
```

Then `rimworld/load_game_ready` and read it back with `jawa/world_stats`:

```
before   BorealForest 1193   ExtremeDesert  -
after    BorealForest    -   ExtremeDesert 1193
```

**The engine reported the change.** Not the tool's own success flag — the running game's
biome histogram. That is the whole verification loop, and it costs one call.

### What the tool does

Decodes eight parallel arrays off `savegame/game/world/grid/layers` →
`<li Class="SurfaceLayer">`: `tileBiome`, `tileElevation`, `tileTemperature`,
`tileRainfall`, `tileFeature`, `tilePollution` (2 bytes each) and `tileHilliness`,
`tileSwampiness` (1 byte each). Round-trip with no edit is **byte-identical** —
`--selftest` asserts it.

### 🔴 Traps this tool exists to avoid

* **Find the SURFACE layer, not the first match.** The two `OrbitLayer`s carry the
  **same element names**. A naive `find("tileBiomeDeflate")` can land on an orbit stub
  and edit 488 tiles while reporting success.
* **The shortHash table must come from a dump of the SAME mod set.** A hash decoded
  against a different set resolves to a *different biome* rather than failing.
  `WorldGrid.unresolved()` returns hashes with no def — **non-empty means stop.**
* **Splice high offset → low**, or every edit after the first lands in the wrong place.
* 🔴 **CORRECTED 2026-08-16: roads and rivers are NOT graphs — they are arrays, and
  they are editable.** Each is three parallel per-entry arrays in the SurfaceLayer:
  `tile{Road,River}OriginsDeflate` (4 bytes, tile index) · `…AdjacencyDeflate`
  (1 byte, neighbour slot) · `…DefDeflate` (2 bytes, shortHash). Plus
  `tileRiverDistancesDeflate` at 1 byte per TILE. Dropping an entry ends the road or
  river at that tile, which is what a coast does anyway; nothing dangles because
  nothing is added. `src/RimMandrake/Utils/clean_ashkarr_hydrology.py` does it.
  ⚠️ A repaint that moves the sea WILL strand them — 41 of 607 road tiles and 38 of
  237 river tiles ended up under new ocean on Ash'karr, and 95 rivers ran across a
  frozen nightside that has no liquid water.
* Tile mutators are a separate pair and are still untouched by `worldmap.py`.

### ⚠️ What a biome edit does NOT do

* **It does not regenerate an existing local map.** The colony map was generated from the
  old tile and stays exactly as it was. Biome edits affect tiles not yet visited, world
  rendering, and anything computed from tile data — not ground already made.
* **It edits one field.** A forest turned desert keeps its old rivers, hilliness and
  elevation unless you set those too — which is why `set_scalar` exists.
* Anything standing on a tile stays there. **Mask against `worldObjects` before
  repainting**, or a settlement ends up in the sea.

### 🔑 The wrong-parameter trap bit again, here

`rimworld/load_game_ready` takes **`saveName`**, not `fileName`. Passing `fileName`
silently dropped it and the call tried to load a *different, non-existent* save. Read the
schema off `list_tools` before every unfamiliar call — this is the third time in one
session that an invented parameter name cost a round trip.

---

## 11. ⭐ What can be moved offline — all four answered, 2026-08-15

Verified by the strongest available test: RimWorld **loaded the edited save and re-saved
it itself**, and every edit survived that round-trip.

```
settlement 0   tile 3671 -> 1898   ✅ persisted, name and faction intact
landmark       tile 2516 -> 15     ✅ persisted
landmark 3142  VEE_MeteorCrater -> Oasis   ✅ persisted
```

### 1. Settlements — ✅ TRIVIAL

```xml
<li Class="Settlement">
  <def>Settlement</def>
  <tile>95988,0</tile>   ← change this, nothing else
  <ID>0</ID><faction>Faction_0</faction><nameInt>…</nameInt>
</li>
```
`WorldObjects.move_settlement(id, new_tile)`. **ID, faction and name are untouched**, so
nothing that references the object breaks. This is why moving things *inside* one save is
safe while transplanting a world *between* saves is not.
⚠️ Mask the destination against ocean and against other settlements' tiles first.

### 2. Landmarks — ✅ EASY, two operations

Stored as a parallel keys/values dict, keys `"tile,layer"`:
```xml
<keys><li>2516,0</li>…</keys>
<values><li><def>HotSprings</def><name>Green Seal Hot Springs</name></li>…</values>
```
`move_landmark(old_tile, new_tile)` edits the key; `retype_landmark(tile, defName)` edits
the def. **113 LandmarkDefs are available** (same list the debug menu offers).
⚠️ Runtime `AddLandmark()` also rolls `LandmarkDef.mutatorChances`. Editing the XML does
**not** — the landmark changes and its terrain features do not follow. Set the mutators
too if you want them.

### 3. Geological landforms — ⚠️ TWO SEPARATE SYSTEMS, do not confuse them

* **Vanilla tile mutators** — `tileMutatorTilesDeflate` (4 bytes/entry, tile index) paired
  with `tileMutatorDefsDeflate` (2 bytes, `TileMutatorDef` shortHash). Planet-wide;
  6,648 entries on a 3,787-tile world, so tiles carry several each. This is where
  rivers/caves/coasts/landmark features live in 1.6.
* **`GeologicalLandforms.LandformData`** — the MOD's own store, a `tileData` dict of
  tile → `{topology, topologyDirection, landforms[], biomeVariants}`, plus a
  `biomeTransitionsDeflate` blob. 🔑 **It is populated LAZILY, per tile visited** — one
  entry on this save. So there is nothing planet-wide to edit, and writing an entry for an
  unvisited tile pre-empts a decision the mod would otherwise make at map generation.

⇒ Edit vanilla mutators for planet-wide work; leave `LandformData` alone unless you are
deliberately pinning one tile's local map.

### 4. Faction territories — ✅ FREE, because they are NOT STORED

`FactionTerritories.GameComponent_FactionTerritories` holds only scan bookkeeping —
`nextMapIncursionTickByKey`, `processedMapEntryKeys`, tick counters. **There is no
per-tile territory array and no territory blob anywhere in the save.**

⇒ **Territory is derived from settlement positions at draw time.** Move the settlements
and the territory moves with them, for free. Nothing to edit, nothing to keep in sync.
That makes settlement placement the single highest-leverage edit available: it moves the
political map as well as the object.

---

## 13. 🔑 The scalar encodings — and how to calibrate one without guessing

Every per-tile array is little-endian **unsigned**; the physical value comes out of a
bias/scale. Read one raw and it looks like nonsense — *"ocean elevation 7842"* — which is
how a whole afternoon gets spent on float16 theories that were never right.

| array | decode | status |
|---|---|---|
| `tileTemperature` | **`(raw - 3000) / 10`** → °C | ✅ **VERIFIED against the engine** |
| `tileRainfall` | **`raw`** → mm/year, no transform | ✅ land spans 233–2584 |
| `tileElevation` | **`raw - 8192`** → metres | ⚠️ strongly supported, not proven |
| `tilePollution` | `raw / 65535` → 0..1 | ⚠️ hypothesis |
| `tileHilliness` | `raw` → enum 0..5 | |
| `tileSwampiness` | `raw` → 0..1 | ⚠️ scale unconfirmed |
| `tileFeature` | index into `world/features`, `0xFFFF` = none | |

`worldmap.py` exposes `get(array, tile)` / `set(array, tiles, value)` in **physical
units** and **refuses to write** any array whose encoding is unconfirmed.

### ⭐ THE TECHNIQUE — ask the engine for its own number

You do not need a new tool, a DLL deploy, or a screenshot to calibrate a decode. **The
game will print its own values through a debug Output**, and the bridge returns them in
`effects.logs`:

```python
r = rb.call("rimworld/execute_debug_action", {"path": "Outputs\\Temperature Data"})
[l["message"] for l in r["effects"]["logs"]]      # -> "Tile avg: 6.7°C"
```

Then match against the raw bytes for that tile:
```
colony tile 1318, raw 3067  ->  (3067 - 3000) / 10 = 6.70   ← the engine said 6.7
```
One call, one exact answer. **Get the tile id from `game/info/startingTile` in the save**
— that is the colony's tile, and it is the one tile you can always name.

**Generalises to:** before inventing an encoding, look for a debug Output that already
prints the value. `Outputs` has **261 entries** in game — `Temperature Data`, `Biomes`,
`Terrains`, `World Gen Steps`. Sanity-check the result across biomes afterwards
(Tundra −1.1 °C, BorealForest 0.4, TemperateForest 6.1 — if those don't order correctly,
the decode is still wrong).

### ⚠️ Why a repaint looks fake — the flood-fill trap

Setting 1,193 contiguous tiles to one biome **with identical scalars** renders as an
obvious paint-bucket blob. Real worldgen varies rainfall, elevation and temperature tile
by tile, and the world-map art keys off that variation.

Worse, editing biome ALONE leaves the old climate behind: those tiles became
`ExtremeDesert` while keeping boreal temperatures, i.e. **a freezing desert at 52°N**.

⇒ **A believable biome conversion sets the climate too** — temperature, rainfall, and
ideally a little per-tile jitter — not just `tileBiome`.

---

## ⛔ Deleting a faction from a save DOES NOT WORK — measured 2026-08-16

36 unwanted factions were removed from `allFactions`, every relation entry naming them
dropped, owner references repointed, faction-keyed dictionaries pruned key-and-value
together, and the last singletons (`parentFaction`, `bountyFaction`) redirected — down
to **one** residual reference in a 21,872-tile save. It still loaded broken:

```
Could not do PostLoadInit on RimWorld.FactionManager: NullReferenceException
Could not resolve reference to Faction_16 … VanillaTradingExpanded.TradingManager
                                            /banksByFaction/keys
Error while generating pawn. Rethrowing. NullReferenceException
```

🔑 **Why it cannot be finished by sweeping:** every mod may keep its own faction-keyed
dictionary (Vanilla Trading Expanded's `banksByFaction`, a raid-cooldown mod's
`factionDataDict`), and pawn relations, memories and starting-pawn lists reach further
than the faction list does. A general regex sweep cannot know them all, and the ones it
misses are exactly the ones that NRE.

⇒ **A faction is removed at the Configure Factions page during worldgen, or not at all.**
Converting what a faction OWNS is safe and effective; deleting the faction is not.
📌 Work on a COPY and read `Player.log` — `load_game_ready` returned `success: true` on
the broken save. **The load succeeding is not the save being sound.**

## ⭐ SWAPPING a faction's def WORKS — and it is the way in for a faction worldgen refuses

Measured 2026-08-17, after three worlds generated without `Pirate`.

**The problem:** `Pirate` is `permanentEnemy`, and the planet editor does not offer permanent
enemies in its configurable list. No amount of patching put it there — and the patch that
tried made things worse (below). Meanwhile the world had generated **two** `Jawa_Junkers`.

**The fix:** convert one into the other, in the save.
`src/RimMandrake/Utils/swap_faction_def.py --from Jawa_Junkers --to Pirate --nth 2
--name "Blackstar Company" --hostile --apply`

🔑 **Only the `<def>` string changes.** Every loadID, every settlement's `<faction>` pointer,
every relation entry and every world pawn still points at the same `Faction_N`, so the
reference graph is untouched. That is why this succeeds where DELETING a faction fails
completely: deletion has to chase every reference and still NREs; a swap touches one string.
✅ Verified end to end: the engine reported 12 factions with settlements including
**Blackstar Company**, after a load.

⚠️ **Pass `--hostile` when swapping into a `permanentEnemy`.** The def's traits (pawn kinds,
xenotypes, permanentEnemy) apply from the next load, but the STORED goodwill does not
re-derive — without it you get a permanently-hostile faction sitting at neutral.
📌 Do the swap on the SOURCE before re-running a paint pipeline, so settlement placement
assigns to the new faction properly.

## 🔴 `Pirate` IS `PirateBandBase` — never patch a def that is also a parent

Vanilla's pirate def carries `Name="PirateBandBase"`, so it is simultaneously a concrete
faction and the template every other pirate faction inherits, **ours included**
(`Jawa_Junkers` has `ParentName="PirateBandBase"`).

Adding `startingCountAtWorldCreation 2` to it to make Blackstar generate **did not work and
produced a second Junkers**, because the child inherited the field. The hazard had already
been written down in this skill an hour earlier and was walked into anyway.

⇒ **Before patching any vanilla def, grep for `ParentName="<its Name>"`.** If anything
inherits from it, patch the children's own fields or find another route entirely.
