# FISH_BY_BIOME_1 — think about FISH in every biome where relevant

Owner, 2026-09-06: *"need to think about FISH in every biome where relevant! Good lord..."*

## spec
- Odyssey's fishing is live in the stack (donor biome defs carry `fishTypes` blocks —
  Alpha Biomes assigns e.g. `VCEF_DuskySprat`/`VCEF_ForsakenAnglerfish` to the crags,
  `VCEF_Jellyfungus` to the Rot; vanilla `IceSheet` carries salmon/cod/frostfish). Inventory
  every fish def in the stack (MEASURED from the dump) and every biome's current
  `fishTypes`.
- Per biome with water (the four liquid biomes, the Cracked Lands' 27 open-water tiles,
  the Slime's slime-rain floods, the Rot's milk ponds, the propane sea's exotics, the
  Contagion's red pools): what lives in it, what a fisher catches, what the fliers dip for
  — all under the recognizability rule (no salmon; analogs and aliens) and each sheet's
  water chemistry (`WATER_KINDS_TAXONOMY_1`: fishing in milk, propane, red water, brine
  are different acts).
- Output as DATA: biome × water kind × fish defs × rare catches, fed into the freeze
  review's per-biome table.
- Ties: `SAND_SWIMMERS_MOD_1` (sand fishing), the fliers (`the_cracked_lands.md` §4).

## verify
Every water-bearing biome has a ruled fish list or an explicit "no fish, because…"; the
dump resolves each def.

## 2026-09-09 progress (BENCH, assignment pass)
- Per-biome fish RULINGS are data now: every roster in
  `design/Jawa/worldbuilding/biomes/rosters/*.json` carries a `fish` field (mostly
  ruled no-fish with the chemistry cited).
- Candidates for the ruled-yes waters: `rosters/_fish_candidates.json` (`f18fb5de`) —
  87 fish ThingDefs MEASURED in the live dump; binding is `BiomeDef.fishTypes`
  (fresh/salt Common/Uncommon buckets) — fish placement is BIOME work, no def edits;
  the campaign water-kinds chemistry has no engine hook, it is flavor over the
  fresh/salt axis. Weeping Stones and Cracked Lands have confident donors; greentide
  already assigned (RSW_Mee/Faa/Laa); twilight sub-roof shoal = the one new-def gap,
  non-blocking (diving mods unbuilt).
- ⚠️ RECONCILE BEFORE CLOSING: another window is concurrently authoring sand-fishing
  content (`src/RimUtinni/UtinniPatches/Patches/SandFishing_CrackedLands.xml`,
  `src/RimStarWars/SWBestiary/.../RSW_SandStalker.xml`, `ManyWaters/Defs/` — untracked
  in their tree as of this note). Their custom-def approach and this census's donor
  candidates for the Cracked Lands must merge into ONE fishTypes ruling per water.
