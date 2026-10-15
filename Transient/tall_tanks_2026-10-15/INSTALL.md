# TANK_TALL_BUILD_TWICE_THE_DRINK — install of 16 tank looks (2026-10-15, BENCH)

- [x] 1. Staged images: src/RimMandrake/FlowWorks/art_source/TankTall/v3/<Look>/<Tank>.png (16; 512x512 / 512x768 / 512x512 / 512x1024, real alpha)
- [x] 2. Wiring already in C# (PipeLook registers PipeStyles.TankDefs once <Tank>_Scrapper style def loads) — no C# change, no build
- [x] 3. art ledger install (owner's words) via art_source/TankTall/v3/install_looks.py; old Things/Building/FlowWorks tank PNGs retired through the ledger; `art guard worktree` 0 unledgered
- [x] 4. RM_LiquidTankStyles.xml shipped to Defs/LiquidTypes/ThingDefs/; base texPaths -> Scrapper look; placeholder (stacked drums) comment removed; stale art comments + Scrapper-only description wording fixed
- [x] 5. texPath bind: 20/20 (4 base + 16 styles) resolve to a PNG; Graphic_Single, non-rotatable (one facing)
- [x] 6. FlowWorks SelfTest 325/325 (TankStyles_four_looks_per_tank now reads the shipped file)
- [x] 7. installed.png checked: all 16 present, standing on their footprints, consistent per tank across looks
- [x] 8. Reviewed in full; mark-clean after commit
- [x] 9. Item noted; live look owed (FlowWorks walkthrough map station)

Not touched (other agents' C#): RimMandrakeFlowWorksMod.cs:1275 settings label and Building_LiquidTank.cs:21 doc still say "patched-together scavenger tank".
