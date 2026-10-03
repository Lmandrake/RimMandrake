# CHILL_NATIVE_COLD_TOLERANCE_1 work notes (2026-10-03)
Item has no prose; spec = design/Jawa/worldbuilding/biomes/the_propane_lake_floor_sitting_agenda_2026-10-02.md Q5 (a) + 2.1.
Choices:
- Mod folder: src/RimMandrake/TerminalBiomes only. No C#.
- Set ComfyTemperatureMin -100 -> -150 on the 10 RM_ cast ThingDefs (RM_TheChillFauna.xml x4, RM_TheChillFloorLife.xml x6). Floor stays -110.
- ComfyTemperatureMax (-30) untouched: the item concerns the cold side only.
- Frozen campaign twin RUT_PropaneLakeFauna.xml (2 defs at -100) NOT touched: outside the item's named mod; frozen until repaint.
- validation.py created for TerminalBiomes (static def-level check only; no live Suite run).
