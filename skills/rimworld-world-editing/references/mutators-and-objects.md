# Mutators, landmarks and world objects: the instruments and how they lie

Everything here was measured on the live Ash'karr planet on **2026-08-25/26**, writing ~1,900
mutators, 28 landmarks and 3 settlements across four seas and a mining province. Every entry
is a mistake that was actually made, by me or by an agent I was supervising.

---

## 1. 🔴 `world_mutators_audit`'s `mutatorHistogram` IS NOT A CENSUS

It **omits defs**. Measured: it reported **0** for `RiverDelta`, `AB_GeothermalHotspots` and
`VEE_SmokeVents` while a direct `world_mutators_get` on the same tiles showed all three
present on **9, 3 and 5** tiles.

✅ **Use the audit for `offenderCount` and nothing else.** Every count you report must come
from a direct per-tile read. I nearly filed three false failures against a correct pass.

## 2. 🔴 The audit's `marineChecked` scope is `['Coast']` BY DEFAULT. Widening it invents offenders.

Three separate agents widened it on a guess in one session:

| widened to | result |
|---|---|
| `VEE_SaltPlains` | flagged **313** unrelated pre-existing placements planet-wide and **auto-removed 50** before anyone noticed |
| `VEE_RisingWaters, Archipelago, Iceberg` | `offenderCount: 33`, mixing 15 unrelated pre-existing tiles with its own |
| *(default)* | **11**, every one real and every one written that session |

⛔ **Run it at default scope and treat a non-zero count as real.**
⛔ **NEVER bulk auto-remove what an audit flags.** If a check flags something you did not
write, stop and report it. The 50 removed above had to be identified and restored one by one.

## 3. 🔴 `World.CoastDirectionAt` recognises `Ocean` AND NOTHING ELSE

A tile whose every water neighbour is **`SeaIce`** — or **`Lake`** — is **not coastal** to the
engine. Any coastline-gated def placed there is illegal: it lands, reports `success: true`,
and then misbehaves.

Coastline-gated defs seen so far: `Coast` · `VEE_RisingWaters` · `Archipelago` ·
`CoastalIsland` · `CoastalAtoll` · `Bay` · `VEE_GravelBeach` · `VEE_MarineSanctuary` ·
`VEE_LoneIsland` · `VEE_BasaltCape` · `Peninsula`.

Measured: 11 `Coast` markers written onto a sea-ice shore of the Grey Sea, all illegal, all
removed. Check the neighbours' BIOMES, not just `waterCovered`.

## 4. 🔴 Prefer the MUTATOR form. A LandmarkDef's `IsValidTile` can be unsatisfiable.

`VEE_DryRiver` exists as both. The **landmark** returned `isValidTile: false` on **every tile
probed** — rings 1–3 out from a dying creek, across `ZBiome_Badlands`, `AridShrubland`,
`Desert`, `Wasteland` and `ZBiome_Grasslands`, with and without an adjacent river. The
**mutator** form was already live and legal on 39 tiles with a clean audit, and took 12 more
without complaint.

⚠️ The 23 dry-river *landmarks* already on the planet must therefore have been force-placed by
an earlier pass. **A def existing as a landmark is not evidence you can place one.**

### And `AddLandmark` does not enforce validity anyway
`world_landmarks_set action=add` reports `added: N` **including tiles whose `isValidTile` is
false**. Worse, validity is evaluated **per tile as the batch proceeds**, so a batch of 16
coastal landmarks spaced two tiles apart has each one invalidate its neighbours — and the same
batch returns a *different* validity pattern on a second run.

✅ **Place one at a time, read `isValidTile`, and REMOVE it again if false.** That is the only
pattern that kept the map legal. 28 of 30 attempts survived at 3.2° spacing.
⚠️ `isValidTile` also returns false when a landmark is ALREADY on the tile — so a validity
reading taken after your own add is contaminated and worthless.

## 5. Settlements: `world_objects_add`, and the fault that is invisible until too late

`world_objects_set` only MODIFIES (`ids`, `tile`, `faction`, `name`). Creation is a different
tool and it is easy to conclude the bridge cannot do it:

```
jawa/tile_settleable   tiles="6645"                 -> settleable true/false + reason
jawa/world_objects_add def=Settlement tile=6645 faction=<FactionDef> name="Bitterleaf"
jawa/world_commit                                    <- FastTileFinder caches settlement tiles
jawa/world_objects_validate                          <- read it back
```

🔴 **`faction` is required and a null-faction Settlement is DESTROYED on load**, with only a
warning. The bridge says so itself: *"This is the one fault that is invisible until it is too
late."* `world_objects_validate` reports `nullFactionSettlements`, `badTileCount`,
`settlementsOnWater`, `settlementsOnImpassable`, `stackedTiles` — all five must be 0.

✅ Always run `tile_settleable` FIRST. It is cheap and it answers with a reason.

## 6. Category conflicts, and the verification that cannot see them

A more specific mutator silently displaces the general one in its category. That is the system
working — but **a pass that verifies each def against its OWN intent reports a clean 100%
while destroying other people's work.** Measured twice in one session:

- a coastal pass wiped **26 `CoastalIsland`** and **2 `Oasis`** tiles canon protects, and
  reported every def landed;
- a second pass wiped **12 `CoastalIsland` + 4 `Archipelago`**, and reported 100%.

✅ **Harvest the whole planet's mutators before and after, and diff the LOSSES:**

```python
lost = Counter(d for t in before for d in before[t] - after.get(t, set()))
```

Every loss then needs a sentence: *intended* (`RiverDelta` displacing `River` at a mouth) or
*collateral* (an island paved over by a tidal flat). ⚠️ Collateral is not automatically wrong,
but it is a decision someone must make — and **a specific instruction from the owner outranks
a generic one.** The islands were restored and the tidal flats relocated to shore with no
coastal rival, so both passes kept their intent.

Known displacing pairs: `RiverDelta`/`Headwater`/`RiverConfluence` → `River` ·
`Fish_Increased` ↔ `Fish_Decreased` · any `category=coastal` def → any other ·
`SunnyMutator` ↔ `WindyMutator` (category Weather) · `VEE_DryRiver` → `VEE_FloodPlains`.

## 7. A gate you cannot read is UNMEASURED, not permission

The live roster truncates long biome lists with `...`. ⛔ Do not read that as allowed.
Two ways to settle it, in order of strength:

1. **Where the def ALREADY lives on this planet** — `VEE_DryRiver`'s real biome set was read
   off its 39 live tiles, not off the note.
2. **The def's own XML**, if a source copy exists. ⚠️ A live "probe" is the WEAKEST evidence
   of all: `Tile.AddMutator` never validates biome, so a write **cannot fail** on a gate that
   is never checked. An agent correctly refused `FoggyMutator` on `Ocean` on exactly this
   reasoning after its probe appeared to succeed.

---

# Measured 2026-08-26, authoring ~11,000 mutators and 150 landmarks on Ash'karr

Every entry below is a mistake that was made and caught in one session.

## 🔴 `world_landmarks_set`'s `isValidTile` is evaluated AFTER the add. It is not a gate.

```
world_landmarks_set {action:add, def:sw_Sarlacc, tiles:"6", checkValid:true}
  -> added: 1
     validity: [{tile: 6, isValidTile: FALSE}]
     tiles:    [{landmark: "sw_Sarlacc", landmarkName: "White Sarlacci Burrow", ...}]
```

The landmark **is on the tile** and named. `isValidTile` reports false because a landmark now
occupies it — the flag describes the state *after* your own write. ⛔ It never blocks the add,
and it is worthless as a pre-check.

✅ **The only honest success signal is `added >= 1` AND the read-back row showing your def in
`landmark`.** Everything else lies in one direction or the other.

## 🔴 The LANDMARK and the MUTATOR often have DIFFERENT defNames

`AncientRuins` is a TileMutatorDef. The LandmarkDef is `Ruins`. Nine placements failed with
*"No LandmarkDef 'AncientRuins'"* on the assumption that one name served both.

⚠️ Others that differ or exist on only one side: `sw_Sarlacc` is a LandmarkDef with **no**
mutator (its mutator is `sw_SarlaccLair`); `VEE_CactusFields` is landmark-only. **Check
which def type you actually hold before writing.**

## 🔴 A landmark's `mutatorChances` rolls BYPASS any category guard you apply to your own writes

`AddLandmark` also rolls the def's `mutatorChances` and `comboLandmarkMutators` onto the tile.
Those adds go through `Tile.AddMutator` like any other, so they displace same-category
mutators — and your careful guard never saw them.

Measured: 7 displacements from one landmark pass. Six were correct specialisations
(`Cavern` / `VEE_SerpentineCanyons` / `VEE_Cenotes` replacing a generic `Mountain`). **One was
a real defect** — a `VEE_DryRiver` landmark on a LIVE river tile displaced its `River`.

✅ **Diff whole-planet LOSSES after any landmark pass, not just your intended gains.**

## 🔴 A remove does NOT restore what an add displaced

```
before: ['Cliffs', 'VEE_MoreSolarPower']
add VEE_JaggedRocks   -> Cliffs displaced (both category Mountain)
remove VEE_JaggedRocks
after : ['VEE_MoreSolarPower']            <- Cliffs is GONE
```

⇒ **Any add/remove probe on a categorised mutator is destructive.** Read the tile first and
put back what you displaced. This bit during an experiment, on a tile nobody meant to edit.

## ⚠️ `overrideCategories` is a SECOND displacement path your guard probably misses

`AddMutator` removes on `categories` overlap **and separately** on
`mutator.overrideCategories` matching the existing def's `categories`. A collision guard built
on `categories` alone will miss it — measured once, `VEE_SerpentineCanyons` took out a `Caves`.

## 🔴 The 45 `GL_*` defs cannot be written, and that is CORRECT

Geological Landforms (and its sibling **Biome Transitions**, same author, same `GL_` prefix,
different mod) register `TileMutatorDef`s that are **computed at display time and never enter
`Tile.mutatorsNullable`**.

Control, six genuinely empty tiles across six biome/hilliness combinations:

```
tile   biome            hilliness    def                 added  LANDED
10140  ExtremeDesert    Flat         GL_DesertPlateau      1     NO
10140  ExtremeDesert    Flat         VEE_PebbleDunes       1     YES
297    AB_RockyCrags    Mountainous  GL_Caldera            1     NO
297    AB_RockyCrags    Mountainous  Cavern                1     YES
```

No category conflict was possible, nothing was logged, and `Tile.AddMutator` has no early
return — so the mod's worker removes it again. Proof they are live regardless:
`Player.log` reports `Loaded 49 landforms`, and the in-game pane for a tile bordering two
biomes lists `biome transitions` that `world_mutators_get` does **not** return.

⛔ **So a "never used" count over `GL_*` defs is measuring the wrong thing.** They are assigned
at MAP generation from tile requirements (`<workshop>/2773943594/1.6/Landforms-v1/*.xml`:
Topology, Commonness, hilliness / elevation / temperature ranges). ⇒ **The lever is hilliness
and elevation, not mutators**, and no landform ever shows on the world-tile pane, before or
after a reload.

## 🔴 Every canyon and chasm def needs Mountainous, and they are ALL category `Mountain`

```
VEE_SerpentineCanyons · Chasm · Cavern · Hollow · Cliffs   minHilliness = Mountainous
VEE_RockRidge · VEE_JaggedRocks · VEE_StoneForest · Crevasse   maxHilliness = Flat
```

⇒ There is **no canyon vocabulary at LargeHills or SmallHills** — the two families gate at
opposite ends. To carve a canyon system you must raise the whole structure to Mountainous
first. And because they share the `Mountain` category, **a tile holds exactly one of them**;
build variety by walking different defs along the ridge, not by stacking.

## 🔴 `elevation <= 0` IS water, and a sub-zero tile generates NO ROCK

```csharp
SurfaceTile.WaterCovered => elevation <= 0f;
GenStep_RocksFromGrid.Generate: if (map.TileInfo.WaterCovered) { return; }
```

That return takes rock, rock roofs and `GenStep_ScatterLumpsMineable` with it;
`GenStep_RockChunks` bails the same way. And it cannot even persist —
`SurfaceLayer.cs:98` stores `WaterCovered ? elevation : Mathf.Max(elevation, 1f)`, so a land
tile's elevation is clamped to at least **1 m** on save.

🔑 **A chasm floor is not the world tile's elevation.**
`TileMutatorWorker_Chasm.GeneratePostElevationFertility` writes `MapGenerator.Elevation` —
the MAP grid — raising cells above `ChasmThreshold 0.5`. The chasm is the *gap between raised
rock*: depth comes from raising walls. Taking a tile sub-zero makes a canyon **shallower and
drowned**, not deeper.

## ⚠️ `FeatureDef` is a WORLDGEN classifier. Nothing reads it at draw time.

`FeatureWorker.cs:33` uses `def.nameMaker` once, when the region is created.
`WorldFeatures.cs` draws from `name`, `drawCenter`, `drawAngle`, `maxDrawSizeInTiles` — never
`def`. ⇒ Retyping named regions onto `Sea` / `MountainRange` / `Desert` changes **nothing**
visible or mechanical. Do not spend a pass on it.

⚠️ And `maxDrawSizeInTiles` cannot differentiate labels downward: `EffectiveDrawSizeCurve`
starts at `(10 -> 15)` and `SimpleCurve` clamps below its first point, so **anything under 10
draws identically to 10**. Differentiation only goes up, and up collides on a globe carrying
70+ named regions. The flat default of 10.0 is usually correct.

## ⚠️ Mutators persist as shortHash BYTE ARRAYS. `grep` on a save cannot see them.

`<tileMutatorDefsDeflate>` / `<tileMutatorTilesDeflate>` — base64 + raw DEFLATE, 2-byte
little-endian shortHashes. Landmarks DO store as defName text, which makes the contrast
maximally misleading: grepping a save finds `sw_Sarlacc` and returns **0** for
`VEE_MoreSolarPower` on 4,362 tiles.

✅ To verify a mutator pass in a save, decode the array and count shortHashes:

```python
raw = zlib.decompress(base64.b64decode(re.sub(rb'\s+', b'', m.group(1))), -15)
counts = collections.Counter(struct.unpack('<%dH' % (len(raw)//2), raw))
```

⚠️ Compare against TOTALS, not against how many you added — the pre-existing count is in
there too. That mistake produced a false "SOMETHING DID NOT PERSIST" verdict on a pass that
was perfect.
