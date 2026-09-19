## the symptom
Owner, 2026-09-07, reading the world map: **"I see 'Cypre Jungle' — I thought we
were renaming all of this?"**

## the answer, and why it is not a naming-scheme failure
`design/NAMING_SCHEME_PLAN.md` governs **our own defNames** (`RUT_`/`RSW_`/`RM_`).
It never covered **donor LABELS**, and it should not: renaming a donor's defName
breaks every reference to it — patches, mutator whitelists, our own tiles CSV.
🔑 **The player never sees a defName. The player sees `<label>`.** So the fix is a
label/description patch, which is cheap, reversible, and has simply never been done.

## MEASURED 2026-09-07 — the scale
**30 distinct biomes are painted on the planet. Only 4 are ours.** The other 26
display a donor label. Every one of them has a biome sheet that already names it:

| tiles | donor def (what the game shows today) | campaign name (its sheet) |
|---:|---|---|
| 2291 | `AB_MycoticJungle` | **the Rot** |
| 1797 | `AB_PropaneLakes` | **the Propane Lakes** |
| 1336 | `BiomeGRimond` | **the Blue Desert** |
| 1233 | `AB_RockyCrags` | **the Forsaken Crags** |
| 979 | `ZBiome_Badlands` | **the Cracked Lands** |
| 542 | `PoisonForest` | **the poison forest** |
| 236 | `ZBiome_DesertOasis` | (Weeping Stones oases) |
| 236 | `AB_MechanoidIntrusion` | **the Rust Cathedral** |
| 226 | `ZBiome_Grasslands` | **the Pyrelands** |
| 191 | `BiomeCypreJungle` | **the Greentide** ← the one he spotted |
| 173 | `AB_OcularForest` | **the Contagion** |
| 172 | `AB_FeraliskInfestedJungle` | **the Webwork** |
| 96 | `AB_GelatinousSuperorganism` | **the Slime** |
| 92 | `AB_MiasmicMangrove` | **the Miasma** |
| 62 | `AB_TarPits` | **the Sump** |
| 60 | `COMIGO_GreaterSwamp_Tropical` | **the Fever Wood** |
| 31 | `AB_PyroclasticConflagration` | **the Forge** |

⚠️ Some defs are claimed by MORE THAN ONE sheet (`Desert` and `ExtremeDesert`
each carry several — the dune sea and deep desert share `ExtremeDesert`, ruled
[R22]). **A def has ONE label**, so where two sheets share a def the label must be
the shared, higher-level name, not either sheet's. Do not force a per-sheet name
onto a shared def.
⚠️ `SeaIce` (262 tiles) is claimed by no sheet — decide before labelling.

## the work
A single `PatchOperationReplace` file in `UtinniPatches` over
`/Defs/BiomeDef[defName="X"]/label` (and `/description`), guarded with
`MayRequire` on each donor's packageId so the patch is inert when a donor is off.
⛔ **Do not rename any defName.** ⛔ Do not touch the tiles CSV.

## why it is worth doing early
It is the cheapest large win available: no map change, no def change, no restart
risk beyond the ordinary, and the entire planet begins reading as Ash'karr instead
of as a stack of other people's mods. It also makes every later art and review
pass legible, because the labels on screen will match the sheets being reviewed.

## verification (cheap, per the standing rule)
`jawa/get_defs` on each patched biome returns the campaign label; one screenshot
of the world map with the tooltip open.
