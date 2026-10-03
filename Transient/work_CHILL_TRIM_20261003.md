# CHILL_FLOOR_CAST_TRIM_1 work notes (2026-10-03)
Ruling: sitting 2026-10-02 Q1 (a) - move hoolen, vaunoom, AA_AuroraSylph, AA_Skyeel off the floor roster; they wait for a surface home.
Choices:
- Edit only src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TheChill.xml (wildAnimals rows removed, comment notes where they went).
- ThingDefs/PawnKinds of RM_Hoolen/RM_Vaunoom stay (surface home owed); no other biome lists them (measured per agenda).
- RUT_PropaneLake twin and BiomeCastEvictions patch (src/RimUtinni) NOT touched: frozen, outside the item's mod.
- RUT_Zhiil comment pairing with vaunoom left; zhiil body is CHILL_ZHIIL_FLOOR_BODY_1.
- validation.py: added roster_trim check (parses wildAnimals as XML nodes).
