# SCALD_SAAL_ONE_NAME_1 work notes (2026-10-03)
Ruling (owner, typed "Saal"): creature and catch both named saal; "noohm" retires.
Choice: LABEL and TEXT only. defName RM_Noohm (race ThingDef + PawnKindDef) stays: it is shipped content, referenced from C# (DivingInteraction) and 8 XML files, and the name RM_Saal is already the catch ThingDef (same ThingDef namespace, a rename would collide). Texture folder RM_Noohm also stays (texPath binds by path).
Folders touched: src/RimMandrake/TerminalBiomes/Defs, src/RimMandrake/Utils/scald_showcase.py, src/RimMandrake/DivingInteraction/validation.py, design/Jawa/worldbuilding/biomes (agenda).
