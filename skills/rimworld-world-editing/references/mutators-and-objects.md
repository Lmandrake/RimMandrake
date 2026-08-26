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
