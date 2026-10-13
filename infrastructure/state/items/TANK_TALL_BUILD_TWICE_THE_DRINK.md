## spec
Owner 2026-10-13: "Make tall tanks too that double the storage."
Capacity lives in C# (`Building_LiquidTank.Capacity` = footprint area x 20 x 2 if `RM_LiquidTankExtension.tall`), not in defs.

## done
- `RM_LiquidTankTall` (2x2, tall=true => 160; RM_LiquidTank is 80). Cost 285 steel + 5 components (1.9x / 1.7x), WorkToBuild 5800 (1.8x), HP 320, skill 5: a second drum roughly doubles material with a small frame saving. Same VCHE_PipeNetworks category, same thingClass so every workgiver/bill keyed on Building_LiquidTank covers it (no defName checks in non-selftest C#). The tank-capacity Mod Setting scales all tanks, so it already covers it.
- Art: PLACEHOLDER derivative (short-tank drum stacked twice, 512x768, drawSize (2,3), drawOffset z+0.5) via `art_source/TankTall/mk_tall.py` + artledger install. OWED: a real painted tall tank.

## owed
- The cargo tank `RM_UniversalCargoTank` is ALREADY tall (160). An extra-tall 320 version needs `RM_LiquidTankExtension` to carry a capacity factor (C#: extension, RM_Volume.TankCapacity, Mod Settings label, selftests). Owner picked it by card; waits on the pit-pocket-grid builder's uncommitted FlowWorks C#.
