# Titan passage on the dark side: can a giant live there? (calls, 2026-11-05)

Item: `NIGHTSIDE_TITAN_JUDGE_GIANTS_IN_THE_DARK`. Delegated design (ledger 2026-10-23: *"per-biome giant is a roster-hole
fill (new creature) at the biome's sitting; judge-checked"*). Owner, 2026-10-21, on the titan passage: *"Every biome
should have something like this."* and *"A few exceptions such as rust cathedral and dark side biomes. Only if giants can
exist there."* The done-condition (ledger note 2026-10-29) is a recorded call per biome: a giant can live there (a roster
row is filed) or no titan passage is built.

The item names `RM_NightsideIce` and `RUT_NightsideIce`. Those were renamed `RM_SleepingIce` and `RUT_SleepingIce` in
80e0635c30 (`design/RimMandrake/biome_name_provenance_audit_2026-10-28.md`); the calls below use the live names.

A passage giant is T2 or bigger: adult body size 8 or more (`RM_TitanicTierDef`). It must also match the map's water-ness:
a sea giant on a sea map, a land giant on land (`RM_TitanicKernel.TitanEventEligible`).

| biome | call | how it is enforced |
|---|---|---|
| `RM_SleepingIce` | **no giant can live there; no passage** | `RM_TitanPassageExtension none=true` (patch below) |
| `RUT_SleepingIce` | **no giant can live there; no passage** | the same |
| `RM_TheChill` | **a giant can live there**; a roster row is filed | `CHILL_TITAN_POPULATE_WAX_GIANT_TOO_SMALL` |
| `RUT_Umbra` | **a giant can live there**; a roster row is filed | `UMBRA_TITAN_POPULATE_BURNS_TO_WALK` |

A naive judge (a fresh Opus that did not draft this) checked the first draft. It kept both Sleeping Ice calls. It overturned
the Chill's "no", and kept Umbra's "yes" on different grounds: the sheet's *"so it gets big"* line is about the liquid lake,
not the Umbra's land. Both sections below are written to its findings.

The patch is `src/RimMandrake/HugeThings/Patches/RM_TitanPassage_DarkSide.xml`. The proof is
`src/RimMandrake/Utils/selftest_titan_passage_dark_side.py`.

## What the rosters hold today (measured from `src/`, 2026-11-05)

| biome | roster (`wildAnimals`, plus patch-added rows) | largest adult body size |
|---|---|---|
| `RM_SleepingIce` | `RM_Zhissa` 0.65, plus patch-added `RSW_CaveLemming` 1.0, `RSW_Wampa` 6, `RSW_Tauntaun` 1.0 | 6 (wampa), below T2 |
| `RUT_SleepingIce` | `RSW_CaveLemming` 1.0 | 1.0 |
| `RUT_Umbra` | `RUT_BurnerAscendant` 1.3 | 1.3 |
| `RM_TheChill` | ten floor animals, `RM_Hesuun` 3.5 the largest; the rest under 0.3 | 3.5 |

None of them homes a giant, so the passage already skips all four. The question this sheet answers is whether that is
correct, or whether the biome has a hole that a new giant should fill.

## The Sleeping Ice (`RM_SleepingIce`, `RUT_SleepingIce`): no

The sheet `design/Jawa/worldbuilding/biomes/sleeping_ice.md` rules this out in so many words:

- §6, a hard ban: *"No warm-blooded, fast, pursuing, fleeing or flocking fauna on the surface; the tunnelers move only
  within the ice and surface only to feed or in a thaw pulse."*
- The wanted/barred list bars *"anything that walks, runs, flies, flocks, herds or flees on the surface"*, and
  §4c: *"anything warm here is a visitor, a machine, or dying"*.
- The incident table already has its own version of the vanilla migration: *"animal migration passing → the one-move
  animal commits, once, ever"*.
- There is no food. Plant density is 0 and the sheet bans photosynthesis, soil and farming.

A walking giant crossing the map breaks the first ban whether it lives there or passes through, so a passers list is out
as well. The biome's apex is already designed: the dhorrumak (`RM_Dhorrumak`, roster draft §1.5, item
`DHORRUMAK_BUILD_BIGGEST_LAST`), an ice wyrm that breaks up through the ice when the colony has run warm for too long, and
*"never on the wild roster"*. Its breach is how this biome delivers a giant. A titan passage would be a second, contradictory
one. The Utinni twin is built to the same sheet (`RUT_SleepingIce` *"overrides every list"*), so the call is the same.

## The Chill (`RM_TheChill`): yes, a giant can live there

`RM_TheChill` is the propane lake itself, a sea biome (`isWaterBiome`, `BiomeWorker_Ocean`). Only a sea giant could pass,
on its floor map. (`RUT_Umbra.xml` says it directly: *"The lake is NOT this biome: it is RM_TheChill"*.)

- The propane sheet (§3) is about this liquid: *"Propane-in-liquid gives the nightside's butane/pentane biochemistry a
  medium — so it gets big."* The sheet expects big life here, not an absence of it.
- The 2026-10-02 sitting has already given the floor a giant: `RM_Hesuun`, *"the floor's giant (Q4b), a slow file"*
  (`CHILL_WAX_PROCESSION_GIANT_1`, in the def). It is a wagon-sized wax colony at body size 3.5. That is a giant by the
  floor's measure, but it is T0 by the passage's measure, which starts at 8.
- The V-wake (owner 2026-09-02, built as `RM_Vaunoom`) was proposed as *"the lake's one giant"* at about body size 4
  (`terminal_seas_cast_proposal_2026-09-25.md`). It is now built at 1.1 and has been moved off the floor roster to wait for
  a shore home.

So the lake holds giants, but none of them is passage-sized. That is a roster question for the Chill's sitting, which is
why this sheet files `CHILL_TITAN_POPULATE_WAX_GIANT_TOO_SMALL`. The sitting has two choices. It can grow a sea giant the
sitting already ruled (the hesuun file, or the V-wake back at its proposed scale) to an adult body size of 8 or more, if its
identity bears that. Or it can invent a NEW propane-native sea giant, body size 8 or more, homed on the floor roster. The
Chill's thin food web (animal density 0.08) is that sitting's to weigh. This sheet does not shrink the call to "no" for it.

## The Umbra (`RUT_Umbra`): yes, a giant can live there

`RUT_Umbra` is the land biome of the propane country: black ice under the planet's strongest aurora, with propane falling
as rain and pooling. The sheet is `design/Jawa/worldbuilding/biomes/the_propane_lakes.md`.

- The sheet's §3 *"so it gets big"* line is about the liquid lake, which is the Chill, not this biome. The Umbra's own case
  is the land beside it. §3 puts the Ammonia Flats, *"692 tiles of this def"*, under their own solvent:
  *"the nightside's chemical oasis: ammonia-based life, efficient where the Blue Desert starved."* §4 puts a big herd
  animal there, the Frostbound Behemoth, *"what the polar solvent builds when it has a medium"* (an Alpha Animals
  donor at body size 3.0, not on this roster).
- It has a food base. Its crystal flora *"regrow overnight"* from the fuel snow (plant density 0.75), and it has the
  densest animal roster of the four (animal density 0.5).
- §4 says how such a body moves: *"fluid movement is impossible without burning. Always in flame when moving."* A giant
  here would be slow and burn as it goes. That fits the hard bans: it is not an icy dayside analog (ban 1), and a walking
  fire is exactly the "hot source" ignition the lake needs (ban 4). A passage that ends with the propane pools burning is
  the biome's own story.
- Nothing on the sheet bans large surface fauna, the way the Sleeping Ice bans it.

The roster homes no giant today; its apex is the Burner ascendant at 1.3. The owner's rule for a hole is that *a NEW
creature fills it*, so this sheet invents nothing and lends nothing. It files `UMBRA_TITAN_POPULATE_BURNS_TO_WALK` for
Umbra's roster sitting: invent a native land giant, adult body size 8 or more, under the propane sheet's §4 and §6. It
gets an invented `RM_` name (Q11a), and it is homed on `RUT_Umbra`'s roster, which makes it the passage pool.
