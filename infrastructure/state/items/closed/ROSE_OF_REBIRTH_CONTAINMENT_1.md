## spec
Owner, live 2026-09-10, watching the colony map: "There are also 'Rose of
Rebirth' all over the map... We want to control that plant tightly."
476 `RotR_RoseOfRebirth` counted on the live Ash'karr colony map
(`jawa/list_things`, group=Plant, same session).

## finding: the mechanism cannot self-spread — decompiled `RomanceOnTheRim.dll`
`RotR_RoseOfRebirth`'s own ThingDef already ruled out the two ordinary
spread routes (`wildClusterWeight=0`, empty `sowTags`). This session went
further and decompiled the mod's actual C# (`ilprobe` against
`RomanceOnTheRim.dll`, 448 types):
- **`RoseOfRebirth`** (the plant's own class): `TickLong`, `TryResurrect`,
  `TryResurrectAsShambler` — matches its flavor text exactly (resurrect a
  lover, or the corpse becomes a shambler). **No self-reproduction logic
  anywhere in this class.**
- **`CompPlantableByWidowed`** (the seed item's usable-comp, the only way
  a rose gets planted): `CanBeUsedBy` requires
  `LovePartnerRelationUtility.ExistingLovePartners(pawn, true).Any(...)`,
  erroring `"RotR_MustBeWidowed"` otherwise — this is a **player-initiated,
  per-seed, one-at-a-time job** (`Job.count = 1`), gated on a specific
  pawn's relationship history. Nothing here is a background/automatic
  trigger.
- Searched the whole assembly for any grief/mourning/funeral/incident
  class that might auto-grant the seed on a partner's death: **none
  exists.** The only class with "Seed" in its name is the ordinary
  `JobDriver_PlantSowWithSeed`.

**476 planting actions, one at a time, each requiring a widowed colonist
and a physical seed item, is not reachable through this mod's own
mechanics on a campaign this young** — confirmed via the bridge this
session: `ticksGame` 109173, ≈1.8 days in.

## finding: already correctly excluded from the biome roster — this is a placement artifact, not a live bug
`design/Jawa/worldbuilding/biomes/rosters/arid_shrubland.json`'s
`flora_purged` list ALREADY contains `RotR_RoseOfRebirth`, reason:
"Earth-nameable (rose)" — the same pattern-match bucket as
`ZBiome_Plant_WildRose`. It is correctly absent from the live
`BiomeFlora_Ashkarr.xml` `AridShrubland` `wildPlants` list too (confirmed
during `BOOM_FAMILY_CUT_1`, same session — AridShrubland's actual roster
is 10 named plants, this is not one of them). **The design process already
got this right**; the plant was never wired into any spawn-on-map-
generation path.

⇒ **The 476 live instances did not arise from gameplay or from a wiring
bug — they are a one-time PLACEMENT**, almost certainly from an earlier
map-authoring or decoration pass (the mod tracks it in
`design/Jawa/mods/plant_pool.csv` as a valid candidate plant with real
metadata, texPath included — so a bulk-decoration tool call reading that
pool without respecting `flora_purged` is the likeliest route, though the
exact historical call was not pinned down: no script under
`design/Jawa/mods/*.py` or `design/Jawa/worldbuilding/**/*.py` that reads
`plant_pool.csv` does a bulk map-scatter — they all generate the proper
biome-roster XML, which correctly excludes it. The scatter more likely
came from an interactive bridge session, not a checked-in generator).

## what "control tightly" actually means, given this
Going forward, nothing needs containing — the mechanism cannot add more
roses without a player manually planting seeds near a widowed pawn, which
takes real seed items and real relationship state, not a runaway loop.
**The existing 476 are a static cleanup, not an active problem**, and
squarely inside "we'll repair savegames later" (the owner's own words,
same session, about the rainbow-plant cleanup generally).

## NOT done
Did not remove the 476 existing instances — deferred per the owner's
explicit "repair savegames later." Did not identify the exact historical
tool call that placed them — no committed script reads `plant_pool.csv`
and scatters to a live map, so the placement was very likely an
interactive session action, not a repeatable bug in checked-in tooling;
chasing it further would be searching session history rather than code.

## verify
`RomanceOnTheRim.dll` decompiled, `RoseOfRebirth`/`CompPlantableByWidowed`
read in full — no auto-trigger found (done). `arid_shrubland.json`'s
`flora_purged` and the live `BiomeFlora_Ashkarr.xml` both confirmed to
already exclude this plant (done, cross-referenced against
`BOOM_FAMILY_CUT_1`'s own-session AridShrubland roster read). `ticksGame`
109173 read via bridge, ruling out organic accumulation on a campaign this
young (done).
