# Biome Transitions against the Baroque Biomes: judgment, 2026-11-01

Item `BIOME_TRANSITIONS_JUDGE_VS_BAROQUE`. Owner, C06, 2026-10-10: *"Also need to look at transitions. With our baroque
biomes they may no longer make sense and actually need to go."*

**Verdict: GO.** `m00nl1ght.geologicallandforms.biometransitions` stays off every list, the shipped one included, and
nothing replaces it. Decided under the delegation policy; his C06 ruling asked for this look and an experiment.
Evidence: `design/RimMandrake/biome_transitions_judgment_2026-11-01.evidence.json`.

## What it does

It is XML only: one Geological Landforms graph ending in a biome grid, and one display mutator (`GL_BiomeTransitions`)
derived at display time and never stored on a tile. It fires on any tile with a differently-biomed neighbour and hands
part of the map to that neighbour's biome. It has been off `ModsConfig.FULL.LATEST.xml` since the 2026-10-19 world
remake (wave 2); until today that rested on "no dependence of ours", with the C06 experiment still owed.

## The experiment

One scratch quicktest world, four sites of our biomes, the same tiles generated under two lists that differ by this one
mod and nothing else (`src/RimMandrake/Utils/biome_transitions_ab.py`). Map 200x200, no tick run.

| site | with the mod | without it | reading |
|---|---|---|---|
| Rot, all neighbours Rot (control) | 16,001 plants | 16,054 | the arms are comparable; no border, no effect |
| Cauldron beside Rot | 13,303 plants, **6,047 of them (45%) the Rot's** | 11,238, none foreign | the neighbour's flora takes the map |
| Rot beside Blue Desert | **9,773 plants** | 16,386 | 40% of the Rot's cover goes, and none returns as Blue Desert flora |
| Rot beside Blue Desert, carrying Odyssey's `MixedBiome` | 11,165 | **1 plant: a dead map** | see below |

An earlier full-list reading agrees: 78% foreign plants on a tile ringed by other biomes (2026-09-17,
`design/validation_walks/RimMandrake/Pyrelands.md`).

## Why it goes

- **A Baroque Biome's promise is its map.** Flora, fauna and hazards are authored per biome, and mechanics are promised
  inside our biomes only (owner, 2026-10-15). A map that is 45% another biome breaks that promise for both.
- **It is not rare.** On today's paint 8,443 of 21,872 tiles (39%) touch a different biome, and small biomes are nearly
  all border: every tile of Webwork, The Sump and Fever Wood, and 94% of Pyrelands. That is a size for the question,
  not a claim about the final planet, which is painted once at the end. A small biome's identity would rest on luck.
- **Our biomes do not blend gracefully.** Ours are deliberately unlike each other, so a blend puts a second biome
  on the map rather than softening an edge, and against a sparse neighbour it simply strips cover.
- **It adds work to every biome.** Pyrelands needed interior-tile censuses and a plant allowlist; every biome would owe
  the same.

**What we lose:** soft edges on border maps. A map is its tile's biome and stops there, as in the vanilla game without
Odyssey. **Nothing replaces it.** If an authored edge is ever wanted, it belongs to a biome's own map-maker
(`design/RimMandrake/biome_map_makers_design_2026-10-10.md`), not to a general blender.

## The bug it was hiding, now fixed

The mod replaced Odyssey's mixed-biome handling. With it gone, `MixedBiome` runs its own worker, whose whitelist holds
vanilla biomes only. On a tile of ours it logs *"No neighbour tile found for mixed biome tile"*, leaves a null secondary
biome, and `GenStep_Plants` and `GenStep_Animals` both throw: a map with no plants or animals. The start save
`ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws` carries `MixedBiome` on **326 tiles**, rolled by landmarks. Whitelisting
our biomes would bring the bleed back, so `src/RimMandrake/TerminalBiomes/Patches/RM_MixedBiome_Inert.xml` drops the
worker and the mutator does nothing. Same tile: 1 plant becomes **16,074**, with no GenStep error, and the other three
sites match the arm without the mod. Our own landmark defs no longer roll it.

**Still owed:** the 326 tiles keep a false "mixed biome" line in the tile pane until the paint pass strips it (noted on
`BIOME_PAINT_ONCE_AT_THE_END_1`).

## Limits

- Measured on a 22/23-mod list, at generation, not on the 321-mod full list; the 326 tiles were counted, not each generated.
- Two border pairs, one seed each. The direction is not in doubt; the percentages are not general constants.
- Geological Landforms itself was present in both arms and is **not** judged here: it remains C06's open question. At
  load it warns that `mandrake.rm.lanterndeeps` adds a destructive patch against it.
