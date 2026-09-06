# LANTERN_DEEPS_INJECTION_1 — the crystal caverns as an injected underground layer

Owner ruling 2026-09-06 (`the_lantern_deeps.md`): `BMT_CrystalCaverns` is NOT a worldmap
biome; it is an injected cave-map layer beneath any nightside map with biome temperature
≤ −40 °C, with two entrance types.

## spec
1. **Quicktest first** (rimworld-debug-testing): confirm what `BMT_CrystalCaverns`
   generates when reached — the mod defines it `isCavern true` (enclosed, stable
   overhead mountain roof, `Calm` weather, incidents disabled) and ships NO entrance def
   in XML; find the transition mechanism in its DLL / Odyssey's layer system. Report
   MEASURED.
2. **Entrances as map-transition features** (caverns sitting: same category as
   DeepRim/Z-Levels shafts): (a) **natural emergence** — lanternstone breaking the
   surface, lit from below; (b) **old mineshaft inside a ruined mining facility** —
   well-provisioned high-tech ruin (Rakatan kyber mine or later expedition), corpses in
   excellent gear. Scene-composition skill applies to both.
3. **Injection rule**: host biome temp ≤ −40 °C only (Blue Desert, ice sheet, propane
   margins); density and kyber richness per host; persistent layers (no regeneration).
4. **Roster**: evict the crystal-studded animals; keep non-crystal cave fauna for the
   sitting; the crystal-life cast (Lantern, Creep, Cleavers, Chorus, Shard-minds,
   mindstone) is authored content — art + C# scoped separately.
5. **Kyber**: the lightsaber mod's `KOTOR_*Crystal` formations + `guy762_focuscrystal_BiomeCrystal`
   as the mineables; crafting-only (Force v2).
6. Darkness mechanic + collapse hazard wired per the caverns sitting.

## verify
A quicktest reaches a Deep through each entrance type; the cave map is enclosed and
dark; kyber formations spawn; the same Deep persists across two visits.
