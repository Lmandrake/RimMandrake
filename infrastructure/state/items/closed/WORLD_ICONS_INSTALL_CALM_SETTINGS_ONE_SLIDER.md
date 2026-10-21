# WORLD_ICONS_INSTALL_CALM_SETTINGS_ONE_SLIDER

Mutator World Icons (Snobi.MutatorWorldIcons, workshop 3551904193) clutters the globe. Measured offline 2026-10-20.

## Measured (save ASHKARR_DEV_START_2026-10-20_PARITY, SurfaceLayer)
- 27,913 mutator entries on 14,483 tiles (158 distinct defs) after the prune.
- The mod draws ONLY three worker classes: AnimalHabitat 343 (`AnimalHabitat`), WildPlants 1,457 (`RSW_WildTattooinePlants` 1,403, `WildPlants` 30, `WildTropicalPlants` 18, `RSW_WildGalacticPlants` 6), MineralRich 614 (`MineralRich`). So at most ~2,414 icons; the big cosmetic defs (VEE_MoreSolarPower 4,362, VEE_LessSolarPower 3,900, Caves, Dunes...) draw nothing.
- Hidden-per-def: NOT possible. Settings are only: `iconSizeModifier` (float, default 1.15, UI 0.2-5), `visibilityLerpRate` (float, default 3, UI 0.1-5), `isEnabled` (bool, default true), `visibilityZoomThreshold` (WorldCameraZoomRange enum, default Close = 1; icons draw when CurrentZoom <= threshold; VeryClose=0, Close=1, Far=2, VeryFar=3). Icon pixel size = lerp(0.2,1,altitude/100) * iconSizeModifier. (Read from the DLL IL; no source shipped.) `RSW_WildTattooinePlants` alone is 58% of icons: only a per-def hide would cull it, which needs a patch of our own (not built).

## Staged file
`/home/mandrake/rm/foundry/deployed/config/Mod_3551904193_MutatorWorldIconsMod.CALM-world-map-2026-10-20.xml`: size 0.7, lerp 3, enabled, threshold VeryClose (icons only at the nearest zoom). File format and name pattern follow the other `Mod_<workshopId>_<ModClass>.xml` files (SettingsBlock / ModSettings Class="MutatorWorldIcons.MutatorWorldIconsModSettings"); the class name and enum text are inferred from the DLL, so the screenshot check proves them.

## Install (live agent, game CLOSED, Windows paths)
1. Copy the staged file to `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3551904193_MutatorWorldIconsMod.xml` (drop the `.CALM-world-map-2026-10-20` part; no live file exists today).
2. Launch, open the globe at Close and Far zoom: expect no mutator icons; at VeryClose small ones. If icons look as before, the file was not read: open Mod Settings > Mutator World Icons and compare values; the game rewrites the file on close, so read it back and fix the Class= name from what it writes.
3. If still too busy at VeryClose, lower size to 0.5 or set isEnabled False (the world toolbar also has "Toggle Animal and Plant Icons").

NEXT: with the game up, copy the staged file per Install, screenshot the globe at Close, Far and VeryClose (system_screenshot.py), and attach the three images.
