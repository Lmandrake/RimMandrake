# SHOKK_RSW_MOD_1 — the Wyyyschokk as its own RimStarWars-tier mod

Owner, 2026-09-11 card sitting (on the webwork bound-bait card), verbatim:
"The Shokk feels like it's becoming its own MandrakeStarWars level mod, with
the rest of the mechanics in this biome party of the Utinni scenario."

## spec
- Extract the Shokk from the webwork kit into an RSW-tier mod (packageId
  `mandrake.rsw.*` per `design/NAMING_SCHEME_PLAN.md`): the Wyyyschokk
  species (canon Star Wars fauna), `ShokkBound` (re-token RSW_ from the
  spec's provisional RUT_), the spit damage def, the sun-scald cripple
  hediff behavior (RULED: cripple ~×0.3 and crawl for shade, never downed),
  and the emergent-Shokk spawn hook (RULED: creep-web harvest on border maps
  yields, with a small chance of spawning an emergent Shokk).
- The rest of the webwork kit — biome wiring, web-sense MapComponent's biome
  gating, creep-web terrain, sole-source boundary — stays RUT_/Utinni per
  the same ruling. The generic behavior classes (JobGivers/MapComponents at
  RM_) live in the ruled separate creature-behaviors assembly.
- Sun-keyed mechanics carry the 2026-09-11 canon note: no night on
  Ash'karr's dayside; lamps never substitute for the sun; on a generic
  planet the same InSunlight primitive simply also turns off at night —
  no special-casing needed.
- Full ruled detail: `design/Jawa/worldbuilding/biomes/kits/
  webwork_kit_spec.md` "Owner rulings" section.

## verify
RSW mod loads standalone with the species + defs; webwork biome content
still references them across the mod boundary; no RUT_ token inside the RSW
mod.

## criteria
The Shokk is usable by any Star Wars scenario; the Utinni webwork biome is a
consumer, not the owner.
