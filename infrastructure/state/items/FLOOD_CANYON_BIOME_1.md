# FLOOD_CANYON_BIOME_1 — flooded-canyons biome as a standalone RimMandrake mod

Owner, 2026-09-12 (verbatim on the filing event): the flood-witness work
restructures into its own standalone biome mod — canyons that get periodically
flooded, flooding as one of its events, the chime warning mechanic included.
RimMandrake tier: not Star Wars specific, playable on any planet.

## spec
- Biome mod per the tier grammar (`design/NAMING_SCHEME_PLAN.md`): packageId
  `mandrake.rm.<name>`, RM_ prefixes, namespace `RimMandrake.<Mod>`. No
  RSW_/RUT_ token, no Star Wars string inside.
- Core content: a canyon biome whose floor floods on a cycle — warning chimes
  (the Cracked Lands chime mechanic, generalized), then the wall of water,
  then soak-driven explosive plant growth where applicable.
- Design inputs already written (campaign register — generalize, don't copy
  lore): `design/Jawa/worldbuilding/biomes/the_cracked_lands.md` §10b (flood
  weeks canon), `design/Jawa/worldbuilding/flood_witness_event_design.md` (the ruled campaign design: chime tells,
  injury-ceiling lethality, invitation route),
  `design/Jawa/worldbuilding/explosive_plant_growth_design.md` (growth mechanic; terminal
  moment awaits owner cards on EXPLOSIVE_PLANT_GROWTH_1).
- MOD_OPTIONS_RETROFIT_1 doctrine applies from day one: per-feature Mod
  Settings (flood cycle on/off + period, chime lead time, growth coupling,
  canyon biome insertion vs feature-only in other biomes).
- The CAMPAIGN plot beat (guaranteed first witnessing per the ruled
  invitation design in `flood_witness_event_design.md`) stays in the Utinni layer and consumes this
  mod as a dependency — it is NOT part of this mod.
- Coordinate with GREENTIDE_STANDALONE_MOD_1 / SHIP_VERMIN_MOD_1 on where
  shared RM_ mechanics assemblies live.

## verify
Mod folder with About.xml + packageId `mandrake.rm.*`; deploys via
deploy_custom_mods.py; no Star Wars token; flood cycle + chimes provable on a
quicktest map in the canyon biome; features toggleable per settings.

## criteria
A player with only this mod gets flooded canyons with chime warnings on any
world; the Utinni campaign rides it for the witness beat.
