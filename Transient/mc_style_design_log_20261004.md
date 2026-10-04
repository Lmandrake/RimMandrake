# MessyConduit style-per-build design log 2026-10-04

- 14:28 start; skeleton
- 14:28 read MessyConduitMod.cs + CordMaterials.cs: global static style, per-net variant seed exists
- 14:28 read AerialMaterials, anchor+hose defs, CompHoseReel
- 14:29 RimSage: Designator_Build stuff float menu + styleDef field; PowerConduit replaceTags Conduit
- 14:29 RimSage: style picker tied to ideo (classicMode+styleOverridden only); designatorDropdown works for ThingDefs; CompStyleable not auto-added
- 14:30 RimSage: blueprint+frame defs always carry CompStyleable; Frame passes StyleDef to the built thing; Thing.Graphic honours StyleDef.graphicData
- 14:31 confirmed no saved MapComponents (mod-less load doctrine); conduit targets = all isPowerConduit except HiddenConduit
- 14:31 read northstar_human_review + debug_process 6a-6c (removal = extended concern)
- 14:32 evidence gathered; writing design doc
- 14:33 doc written; publishing
