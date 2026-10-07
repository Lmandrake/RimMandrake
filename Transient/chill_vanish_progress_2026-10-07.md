# Chill vanish + FeverWood + ElderWeapon — progress 2026-10-07

- started
- 00:56 Chill vanish cause: vanilla LeaveIfWrongSeason (comfy -150..-30) walks them off a temperate map; fix = RM_WildLeaveNotice message (CreatureBehaviors), selftest green, DLL built
- 01:03 FeverWood: RUT_RootCauseway->RM_RootCauseway, RUT_ToxinSealant->RM_ToxinSealedFloor (per Greentide alias table)
- 01:04 ElderUnknownWeapon: its art is present+deployed; the 'Collection cannot init' came from RM_TetherChain borrowing that single PNG as Graphic_StackCount -> Graphic_Single
- 01:13 System.String error: workshop 3506645273 'Invisible Conduit Continued' (glitchgoblin.invisibleconduitcont) About.xml has <author><li>zzz</li></author>; third-party; fires once per load pass (Prepatcher reload = 2)
- 01:17 deployed compose biomes: XML live on next load; CreatureBehaviors.dll (and another agent's Stillsand.dll) locked by running game -> re-run 'deploy_custom_mods.py --compose biomes --apply' with the game closed
