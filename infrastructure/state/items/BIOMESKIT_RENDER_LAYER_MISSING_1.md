# BiomesKit's removed WorldLayer — CLOSED, mechanism identified, non-issue

## spec
Original concern: "BiomesKit's 1.6 DLL dropped `BiomesKitWorldLayer` entirely —
worldmap decoration icons' current source unknown."

Filed 2026-09-09 (caused by `WORLDMAP_BIOME_ICONS_REGEN_1`, now closed on an
unrelated premise). A prior FOUNDRY pass confirmed `BiomesKitWorldLayer` is
missing from every loaded assembly (Map Mode Framework's own reflection scan
agreed) but then took a live screenshot showing gray rock/ice-chunk decoration
icons genuinely rendering on the worldmap right now — contradicting the
"nothing draws them" theory — and left the item open with the mechanism
unidentified.

## verify — decompiled, not string-scanned
Used `ilspycmd` (real IL decompile; `strings` misses .NET UTF-16 constants and
was not used) on the actually-loaded 1.6 assemblies.

**BiomesKit (Continued)** (`zal.biomeskit`, workshop `3333951497`, modVersion
1.0.3, active): decompiled both `.../1.5/Assemblies/BiomesKit.dll` (10 types)
and `.../1.6/Assemblies/BiomesKit.dll` (8 types, the loaded one). Confirmed
**absent from 1.6**, present in 1.5: `BiomesKit.BiomesKitWorldLayer`
(`: WorldLayer`, draws per-biome hill/mountain/forest overlay art keyed off a
`BiomesKit.BiomesKitControls` `ModExtension`), the `WorldLayer_Hills.Regenerate`
Harmony prefix that only ever fired when `Odeum.WMBP` was installed (never true
on this campaign), and `WorldGenStepConstructor` (a C# static-ctor registration
of a `WorldGenStepDef`). The mod's own changelog: 1.0.1 ported to 1.6, 1.0.2
"removed WMBP code", 1.0.3 "now added correctly to WorldGenSteps" — but that fix
only restored the **unrelated** biome-assignment `WorldGenStepDef`
(`BiomesKitWorldGenStep` → `LateBiomeWorker`) via
`.../1.6/Defs/WorldGenerator.xml`. The rendering class was never brought back,
in any form, anywhere in the mod.

**Zero biomes on this mod list were ever affected by that removal.** Grepped
`BiomesKitControls` (BiomesKit's own modExtension class name) across the entire
Steam workshop content folder (all ~580 subscribed mods), the deployed
`RimWorld/Mods` folder, and this repo's own mods — no hits anywhere, and
BiomesKit ships no biome-compat patches of its own (`1.6/Patches/` has only an
unrelated `PlanetLayerDef.xml`). So `BiomesKitWorldLayer` drew nothing on this
campaign even back in 1.5 — dead code both before and after the 1.6 port.

## the actual live mechanism, identified
Decompiled **ReGrowthCore** (`ReGrowth.BOTR.Core`, "ReGrowth 2", workshop
`2260097569`, `.../1.6/Assemblies/ReGrowthCore.dll`) — the source of the
`[ReGrowthCore]`-tagged log line
(`<color=#FFA500FF>[Map Mode Framework]</color> BiomesKitWorldLayer
[ReGrowthCore] not found. Render patch not applied.` in
`Transient/Player_log_C1_run1_automatons_discarded_2026-09-08.log:1396` and
the `_run2` log) that misled the earlier pass. It ships its **own**,
independent, near-1:1 reimplementation:

- **`ReGrowthCore.WorldDrawLayer_Beautification`** (`: WorldDrawLayer`) — reads
  a modExtension named `ReGrowthCore.BiomesKitControl` (singular "Control", a
  *different* type in a *different* namespace from BiomesKit's own
  `BiomesKitControls`) off `BiomeDef.PrimaryBiome`, and draws the same
  `"WorldMaterials/BiomesKit/<biome>/Hills/…"` and `.../Forest/…` overlay
  textures BiomesKit's old layer used to draw. When no biome carries that
  extension, it falls back to generic `"WorldMaterials/BiomesKit/Default/Hills/
  {SmallHills,LargeHills,Mountains,Impassable}"` icons, gated on
  `ReGrowthMod.DefaultWMBPTextureFallback`.
- **`ReGrowthCore.Patch_WorldDrawLayer_Hills_Regenerate`** — a Harmony prefix on
  vanilla `WorldDrawLayer_Hills.Regenerate` that skips vanilla's own hill icons
  entirely whenever `WorldDrawLayer_Beautification` is present and active, so
  ReGrowth's art fully replaces vanilla's rather than layering under it.
- Both are gated on `ReGrowthMod.WorldBeautificationIsActive &&
  ReGrowthMod.worldBeautificationToggle` — `worldBeautificationToggle` defaults
  `true`, and `WorldBeautificationIsActive` reads a
  `ModSettingsFramework`-managed patch-operation state keyed
  `"RG_WorldMapBeautificationProject"`.

**The art is really there**: `.../2260097569/Textures/WorldMaterials/BiomesKit/`
ships per-biome folders (`Desert`, `Tundra`, `TemperateForest`, `IceSheet`, …)
plus `Default/Hills/{SmallHills,LargeHills,Mountains,Impassable}.png` — the
generic gray rock/ice-chunk PNGs, matching exactly what the prior pass
screenshotted live at tile 22 (`RUT_BlueDesert`/Cinderdark — a custom RimUtinni
biome that carries no `BiomesKitControl` extension, so it draws the Default
fallback icons).

The `[Map Mode Framework]` log line is a **separate, cosmetic loose end**:
Map Mode Framework carries a hardcoded per-mod compat table of world-layer
class names to hook for its own map-mode toggle UI, and its entry for
ReGrowthCore still says `BiomesKitWorldLayer` — a stale name; ReGrowthCore's
real class has been `WorldDrawLayer_Beautification` for some time. That only
means Map Mode Framework can't add its own toggle affordance for this layer —
it does not stop the layer from rendering. Not chased further; harmless to this
item and not worth its own fix unless the owner wants Map Mode Framework's
toggle to cover it.

## criteria
- [x] Confirmed via real decompile that `BiomesKitWorldLayer` is absent from
      the shipped, active 1.6 `BiomesKit.dll` (1.0.3).
- [x] Confirmed nothing in BiomesKit itself replaced it, and that its removal
      changed nothing observable on this mod list (no biome ever used its
      modExtension).
- [x] Identified the actual live source of worldmap decoration icons:
      `ReGrowthCore.WorldDrawLayer_Beautification`, an independent, already-
      active reimplementation of the same feature, shipping its own art and
      its own vanilla-hill-suppressing Harmony patch, on by default.
- [x] Visual confirmation already exists from the prior pass:
      `Transient/biomeskit_icons_live_2026-09-09.png` (tile 22,
      RUT_BlueDesert/Cinderdark) — now explained as ReGrowthCore's Default
      fallback icons, not BiomesKit's.

## notes
No fix needed or filed. Worldmap decoration icons are alive and well, owned by
ReGrowthCore (`ReGrowth.BOTR.Core`), not BiomesKit — BiomesKit's own removed
layer was already fully redundant/inert for every biome in this campaign. If
BiomesKit is ever dropped from the mod list entirely, nothing changes visually.
If ReGrowthCore is ever dropped, that's when the icons would actually
disappear — worth remembering if `ReGrowthCore` comes up for a cut later.
