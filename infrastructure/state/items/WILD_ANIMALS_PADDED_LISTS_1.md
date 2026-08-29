## Spec
Every one of the 81 biomes with a wildAnimals list holds EXACTLY 1024 records in the
2026-08-29T05-18-06Z capture (defs/BiomeDef.json, post-patch reflection read) — including
biomes our BiomeCast patch REPLACED with ~29-record lists. An unidentified C# pass pads
every biome's wildAnimals to the full animal-kind roster at load:
- existing records keep their weights (all 791 cast records survive at exact weights)
- race.wildBiomes weights are materialized INTO wildAnimals (dumper's declared-null
  count is 0 — nothing arrives "via race.wildBiomes" anymore)
- entity kinds are EXCLUDED: our 10 cast records for Noctol/Chimera/Sightstealer/
  Fingerspike/Toughspike/Devourer/Gorehulk/Bulbfreak/Dreadmeld in
  AB_GelatinousSuperorganism + AB_OcularForest are dropped — they can never wild-spawn
- everything else is padded in at commonality 0

Consequences to rule on:
1. Cast biomes are NOT exclusive: Desert carries 145 non-cast animals at >0 (e.g.
   Megasloth 0.31, Toxalope 0.4) — owner brief said "creatures unique to a biome as far
   as possible".
2. The 10 entity entries need another delivery mechanism or an explicit cut.
3. biome_animal_conflicts.py's b-side (race.wildBiomes) may now be permanently empty —
   its 0 could be a blind-spot zero.

## verify
Identify the padder (C# harmony patch or ResolveReferences pass in the 582-mod stack);
name the assembly. Then re-read Desert wildAnimals in a fresh capture with the padder
identified and its behavior understood.

## criteria
- [ ] The padding assembly is NAMED with the method that does it.
- [ ] Owner ruled on exclusivity (145 extras in Desert) and on the 10 entity entries.
- [ ] biome_animal_conflicts.py either proven still valid or fixed.
