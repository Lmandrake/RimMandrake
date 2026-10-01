# STILLSAND_SUN_FROM_LATITUDE_1 — the Stillsand's fixed sun, its heat, its glare and its mirage

From `STILLSAND_BEDAZZLE_SITTING_1` (closed 2026-09-30). Design source:
`design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md` §2.7 and §4 #3, #4,
with the turn-4 rulings in `stillsand_bedazzle_cast_2026-09-30.md` §0. **Blocked on
`SOLAR_HEAT_EXPOSURE_1`** (in flight: heat-kind extension, directional shade grid, dash), and it
reuses `RM_PinnedSunExtension` / `RM_MapComponent_PinnedSun` (built for the Long Shade).

Owner rulings, typed in volley turn 2: *"The biome takes its sun angle from its latitude ok the
planet not a region description."* · *"Overheating here should be trivial and difficult to
avoid."* Turn 4, by card: the cover that counts follows the sun angle. CLAUDE.md law: one kind of
heat planet-wide (sun exposure feeds vanilla heat, never a new hediff).

## spec

1. **Pin the sky from the tile.** Add `RM_PinnedSunExtension` to `RM_Stillsand` with elevation
   from the map tile's arc to the substellar point (`RM_MapComponent_ShadeGrid.ResolveSun`). No
   region override: "the Dune Sea" never forces a sun by name. This ends the day-night cycle,
   which fixes dune_sea §6's first ban (broken as shipped). Palette: bleached-white sky, black
   shadow, no penumbra.
2. **Lift the clamp** for this biome to about 85° (`RM_PinnedSunExtension.maxElevationDegrees`
   defaults to 30, and the shade grid clamps at 60): near the substellar point shadows shrink to
   almost nothing.
3. **Cover follows the sun angle (ruled).** The heat kind is resolved from elevation: above about
   55° the `overhead` rules apply (roofs and parasols count, lee shadows are short); below it,
   `lowSun` (only a lee or rock counts). This is which cover counts, never a new kind of heat.
   Built as an elevation threshold on the existing heat-kind extension, so any biome can use it.
4. **Irradiance by angle:** the heat offset scales with sin(elevation). First values: 55 °C at the
   substellar point, about 35 °C in the far ring (today 35 flat). The owner-watched sitting tunes them.
5. **Sand glare (heat):** exposure on open natural sand cannot drop below 0.35, even in cast
   shade. Constructed floors do not glare, so a paved lee ("shade yard") is the one outdoor space
   where shade fully works.
6. **Glare-blind, race-gated (slate IN).** Owner, typed: *"the sun protection for the eyes is great
   for races that need it, but the Jawa won't need it, but the slaves might"*. Unprotected
   humanlike eyes in full glare slowly take a sight debuff (a hediff on vanilla `Sight`).
   **Immunity is a gene, never a defName list:** a new `RM_GlareAdapted` GeneDef (RM tier) grants
   it, and an RSW patch adds it to the Jawa xenotype (`RSW_RimMandrakeJawa`). Every other race
   or xenotype, slaves included, is affected unless it wears eye protection. Animals are out of
   scope.
7. **Sun goggles.** `RM_SunGoggles`, an eyes-layer apparel that cancels glare-blind. Made from
   `RM_Biosilica` (exists today) at a crafting spot, and from sun glass once
   `STILLSAND_GLASS_LENS_CHAIN_1` lands. Existing goggle headgear in the Armoury (Bothan, light-scan,
   pao hat) also cancels it by a patch-added tag, so nobody has to re-buy what they wear.
8. **The mirage (slate IN).** On a tile with sun elevation above a threshold, a GameCondition
   paints a shimmering false-water band on the far map edge and lowers long-range accuracy in full
   sun. A heat-struck pawn can break into a `MentalStateDef` "chasing the water": it walks toward
   the mirage until rescued or it collapses. It always leaves the pawn on the map, with a letter.
9. **One bearing for everything.** Pin the dunes engine's wind to the same tile-to-substellar
   bearing (`DuneFieldExtension.lockBearingToSubstellar`, small C#), so dune crests, lees, shadows
   and the wind all point one way and *"a wind that has never once changed its mind"* holds.
10. **Cooling draught:** a drink of still water gives a hediff of ComfyTemperatureMax +8 °C for
    about 6 h (XML on the still's output).
11. **Mod Settings:** a toggle each for the pinned sky, kind-from-elevation, glare floor,
    glare-blind, the mirage and the wind lock; the heat offsets and glare floor as sliders.

## criteria

- On Stillsand quicktest maps at two latitudes: no night ever falls; shadow length differs by
  latitude; above the threshold a roof protects, below it only a lee does (SelfTest + state read).
- A Jawa colonist never gets glare-blind; a non-Jawa slave in full glare does, and goggles clear it.
- A pawn in the open is in heatstroke territory within an in-game hour at the far ring.
- The mirage's mental state ends with the pawn still on the map and a letter.
- Solar panels on a pinned Stillsand map run at full output (sky glow constant).
