# WASTELAND_EXCRETOR_BEZOAR_1 — excretor herd creature + metal-salt bezoar, built

## what

Resolves `COMMISSION_LEDGER_CLEANUP_1` ledger slug
`wasteland:excretor-herd-creature-metal-salt-bezoar-product-def` —
wasteland.md §4: "The excretors. Creatures that metabolize contamination
concentrate it — and shed what they can't use as dense pellets, metal-salt
bezoars, plated casts. A kept herd is a slow refinery."

## built

- `RSW_Excretor` (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Excretor.xml`)
  — reskin of the already-ported `RSW_FeralNerf` body/art (zero new PNGs,
  not double-booked: `RSW_FeralNerf` itself is not wired into any RUT_
  biome's wildAnimals). `CompProperties_Shearable` retargeted from wool to
  the new bezoar resource — the roster's "mechanic exists in donors"
  reading resolved to a plain vanilla comp, no donor C# dependency at all.
- `RUT_MetalSaltBezoar` (`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_WastelandItems.xml`)
  — the harvested resource, `ResourceBase` shape.
- Wired into `RUT_Wasteland.xml` wildAnimals at 0.15.

## art

Zero new art needed — full asset reuse of `RSW_FeralNerf`'s texPath. The
bezoar item ships with a placeholder texPath (own-namespace pending error,
same class as `RUT_CrackWax`/`RUT_DarkCrust`).
