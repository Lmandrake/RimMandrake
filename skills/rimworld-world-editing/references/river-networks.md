# Rivers: editing a whole drainage network over the bridge

Everything here was measured on the live Ash'karr planet on **2026-08-25**, editing
21,872 tiles through `jawa/world_*` while the game sat at `programState: Playing`.
⚠️ It is about the WORLD, not the map screen — the `world_*` tools reach
`Find.WorldGrid` whatever screen you are on, so none of §0's screen rules apply here.

---

## 1. The three bridge facts that cost the most time

### 🔴 Every `world_*_get` caps at 100 rows. Pass `limit`.

```python
rb.call("jawa/world_links_get", {"range": "0-1999"})              # -> count 100
rb.call("jawa/world_links_get", {"range": "0-1999", "limit": 2000})  # -> count 2000
```

⛔ `max` and `count` are **silently ignored** — they return 100 and report
`requested: 2000`, which reads like a partial success rather than a capped one. The same
cap and the same fix apply to `world_mutators_get`, `world_objects_get` and
`world_landmarks_get`. A whole-planet harvest without `limit` gives you 100 tiles per
call and a plausible-looking answer.

### 🔴 `AddMutator` resolves CATEGORY conflicts, so a read-back "miss" is usually correct

Adding a *more specific* mutator silently removes the general one in its category:

| you add | it displaces |
|---|---|
| `Headwater` · `RiverConfluence` · `RiverDelta` | `River` |
| `CaveLakes` | `Caves` |

Measured: 149 `River` adds reported success, 136 landed, and **73 river tiles read as
"missing the River mutator"** — of which 70 carried `Headwater`/`RiverConfluence`/
`RiverDelta` instead. That is the category system working, not a failure. ✅ **Verify by
asking "does this tile carry ANY mutator from the family", never "does it carry the exact
def I wrote".**

### 🔴 The setter does NOT enforce a mutator's gates. The roster's `note` does.

`jawa/world_mutators_set` will happily write a def whose own generator would refuse the
tile, and the def then misbehaves rather than erroring. **The gate is in the live roster's
`note` field** and must be checked before writing:

```
needs no river · landlocked (0 coast sides) · requires coastline (1-6 coast sides)
max/min hilliness <X> · needs avg temp A-BC · biome-locked: <list, often TRUNCATED with ...>
```

### 🔴 VERIFY WHAT YOU DISPLACED, NOT ONLY WHAT YOU INTENDED

**Measured 2026-08-26, and it is the failure mode a per-def verification cannot see.** A pass
that checks each def against its OWN intent reports a clean 100% while silently destroying
other people's work in the same category. On the Twilight Sea a coastal pass reported every
def landed and had, in the same breath, wiped **26 `CoastalIsland` mutators** (21 overwritten
by `VEE_RisingWaters`) and **2 `Oasis` tiles** the canon explicitly protects — none of which
appeared in its own report, because it never asked.

✅ **Diff the WHOLE planet's mutator set before and after, and look at the LOSSES.**

```python
lost = Counter(d for t in before for d in before[t] - after.get(t, set()))
```

Every loss then needs a sentence: *intended* (`RiverDelta` displacing `River` at a mouth,
`VEE_DryRiver` replacing `VEE_FloodPlains`) or *collateral* (an island paved over by a tidal
flat). ⚠️ Collateral is not automatically wrong — the category system is working — but it is a
decision someone must actually make, and a specific instruction from the owner outranks a
generic one. The islands were restored and `VEE_RisingWaters` relocated to flat shore with no
coastal rival, keeping both.

⚠️ **A truncated biome list is UNMEASURED, not permission.** Where the note ends in `...`
you cannot prove a biome is excluded — treat it as unknown and verify by read-back.

**Pairs that mean the same thing on opposite sides of a gate** — reach for the sibling
rather than deleting the flavour:

| gated "needs no river" / coastal | the equivalent where water still flows / inland |
|---|---|
| `ToxicLake` | **`VEE_ContaminatedRiver`** |
| `VEE_SulfuricLake` | **`VEE_SulfuricRiver`** |
| `Oasis` (a spring) | **`CaveLakes`** (ungated) |
| `VEE_RelictDelta` (needs a coastline) | **`VEE_DryRiver`** (landlocked) |

---

## 2. Laying and cutting links

```
world_links_set   kind=river  path="a,b,c"  def=Creek|River|LargeRiver|HugeRiver
world_links_clear kind=river  tiles="a" to=b        <- ONE segment, both directions
world_links_clear kind=river  tiles="a"             <- EVERY link on a, including a
                                                       junction's other branches
```

🔑 **Rivers are laid MOUTH FIRST.** `WorldGrid.OverlayRiver` sets
`riverDist = max(riverDist, previous + 1)`, so upstream-first writes wrong distances and
`max()` means a too-high value can never be corrected downward.

⚠️ **Determine the mouth by `riverDist`, not elevation.** On a floodplain half a chain
sits at 1 m and elevation is noise; measured on 16 runs, 14 agreed and the 2 that
disagreed differed by 1 m and 3 m. Elevation is the tiebreak, never the primary.

⛔ Overlay silently refuses a LOWER-priority def over a higher one. To downgrade, clear
first.

---

## 3. The five diagnostics worth running on any river network

Each is a plain graph question over `potentialRivers`, and each found real damage.

| defect | test | what it means |
|---|---|---|
| **hump** | a degree-2 tile strictly higher than BOTH its river neighbours | water flows uphill; reads on the map as a river cresting a hill |
| **no outlet** | a system whose lowest tile touches no water and no other system | water pools with nowhere to go |
| **cross-system adjacency** | two river tiles adjacent, in different components | two networks touching and not joined — almost always wrong |
| **same-system adjacency** | adjacent, unlinked, same component | usually FINE — a delta is supposed to braid |
| **downhill dead end** | degree-1, lower than its neighbour, no water adjacent | legal on Ash'karr: creeks may die in playas |

📌 On Ash'karr after repair: 164 adjacent-unlinked pairs, of which **exactly one** was
cross-system (two mouths entering the Grey Sea side by side, benign). The other 163 were
braiding. **Do not "fix" braiding.**

---

## 4. Meandering a straight river — three mistakes, all made

Rivers are laid straight by any painter. Bending them is a shortest-path problem with a
curve penalty, and it goes wrong in three specific ways:

1. ⛔ **Do not MAXIMISE sinuosity.** A first pass took a 4-step run to 57 steps and
   sinuosity 13.7 — a scribble crossing half a hemisphere. **Aim at ~1.35 with a hard
   ceiling of 1.75**; real meandering rivers sit at 1.3–1.5.
2. ⛔ **An amplitude expressed as a FRACTION of run length cannot bend a short run.**
   0.20 of a 4-step run is 0.8 of one tile width, so the straight path stays cheapest and
   every 5-tile creek survives untouched. **Floor the bulge in TILE WIDTHS.**
3. 🔴 **Elevation must be a HARD constraint, not a soft cost.** Costing a climb at
   `max(0, dElev)/400` made 516 m of ridge cost 1.29 against a larger curve penalty, and
   Dijkstra routed a creek over a 1128 m ridge. Measured: **21 humps before the pass, 36
   after — 22 of them created, 828 m of uphill water.**

⚠️ **Dehumping needs ITERATION**: dropping a peak promotes its neighbour to peak. Four
passes took 22 humps / 828 m down to 5 / 99 m.

---

## 5. The corridor: learn the band, do not invent it

The vegetation beside a river is the most visible thing about it. ✅ **Measure the rule
off the corridors the edit did NOT touch**, then apply it only to tiles whose
distance-to-river actually moved.

Ash'karr's own measured band, from 21,377 unchanged tiles:

```
d0 BiomeCypreJungle 62%   d1 AB_FeraliskInfestedJungle 37%
d2 ZBiome_DesertOasis/AridShrubland   d3 Grasslands/Badlands   d4+ Desert
```

…and it **widens with river size** — Creek 70/49/39/31% lush by distance, LargeRiver
91/84/71/63%.

🔑 **Learn an ACCEPTABLE SET per distance, not one biome per ring.** Take the biomes
covering ~85% of real tiles at that distance and leave anything already inside its set
alone. That single rule cut a churny 276-tile plan to a faithful 139, and the tiles left
alone are where the corridor's natural irregularity lives.

🔴 **Owner, 2026-08-25:** *"occasional violations of the rules I just gave you make it look
more natural anyway... not hard and fast math."* ⇒ Do NOT modulate with RNG — a seed is a
knob that could roll a second planet, which is out of scope in every version. **Modulate
with the TERRAIN instead**: ground below the channel holds moisture and the green reaches
further; bluffs and steep hillside pinch it off. Every exception then has a reason a
reader can see, and the result is deterministic.

⚠️ **Do not apply a hilliness penalty on the channel itself** — a river in a valley is
green regardless of the surrounding hills, and the penalty silently suppressed every d0
tile under hilliness 3.

📌 **Regional vernacular beats the planet-wide rule.** Dune Sea runs `BiomeCypreJungle` on
65 of 99 river tiles, and neighbouring Anvil runs jungle at **+61.6 °C mean** — so "too hot
for jungle" was wrong on this planet. Measure the region before deciding a corridor is
anomalous.

---

## 6. Enriching a corridor without it reading as generated

Measured before: the channel carried 2.07 mutators/tile but the banks were nearly bare —
d1 39% empty, d2 46%, d3 57%, against 70% for open desert. A river corridor on a desert
world should be the most interesting ground on the planet.

✅ **Key every placement to the tile's ROLE in the network**, which is a cheap graph
property: `mouth` (touches standing water) · `headwater` (degree 1, above its neighbour) ·
`terminus` (degree 1, below) · `confluence` (degree ≥3) · `gorge` (hilly) · `lowland`.

Mutators with **no gate at all**, so usable anywhere: `RiverIsland` · `CaveLakes` ·
`Caves` · `AnimalHabitat` · `AnimalLife_Increased` · `Fish_Increased` · `Mountain` ·
`VEE_DeepOreRich`.

⚠️ **Leave gaps on purpose.** Placing on every eligible tile reads as generated; roughly
half is enough. Choose by a hash of the tile id rather than RNG, so the gaps are stable
and there is no seed.

---

## 7. Where the numbers live

`design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md` is authoritative for counts and
coordinates; `infrastructure/state/canon.yml` settles disputes. The working scripts for
all of the above are `world/_rivers/` — `meander.py`, `dehump.py`, `corridor.py`,
`corridor_plan.py`, `mutator_plan.py`, `enrich.py`, `probe.py` — each with its own
measured provenance in the docstring.

⭐ **`probe.py <lat>,<lon>` answers "what is at this coordinate"** in one line: tile id,
biome, elevation, river def and degree, system size and every neighbour's state. The owner
gives coordinates; that is the tool that turns one into a tile.
