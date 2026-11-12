A ThingDef with ParentName="Wall" inherits graphicData.linkType CornerFiller (vanilla Wall, raw def), so its texPath is drawn as a LINKED ATLAS whatever graphicClass says; a single 128 px block picture (RM_SpunstoneHull, TheForge) renders sliced into fragments. Odyssey's GravshipHull does the same (Graphic_Single + GravshipHull_Atlas). Give every Wall child an atlas in the 4x4 link layout, or set linkType None.
item: BIOME_SHIP_CONTRIBUTIONS_1
home: skills/rimworld-modding/references/project-engine-facts.md
