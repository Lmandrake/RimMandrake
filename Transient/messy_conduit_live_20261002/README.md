# Messy Conduit phase 1a — live screenshots (2026-10-02)

Fresh dev quicktest map, `messyconduit` tier (Core + 5 DLCs + Harmony + RimBridge + the mod), the scene built by
`src/RimMandrake/MessyConduit/validation.py --live` (cells x150..181, z150..160). Clock jumped to ~1 PM for light.
Placeholder art (procedural, `export_textures.py`). Not a pass bar; the state checks are in `northstar/validation_result_*.json`.

| file | what it shows |
|---|---|
| `mc_01_wide.png` | whole scene: battery (yellow, left) -> loopy cords out through the doorway into a 9x7 steel room; the gap at x157 (one conduit destroyed); the junction, the lamp's cord, the run into the east wall; top right, a far 3-cell run on its own dead net (two dangling ends) |
| `mc_02_break_live_end.png` | the break: the battery-side end is LIVE (straight, bright copper fray, spark flecks); the far side is DEAD (limp curl, dull fray); no cord bridges the gap |
| `mc_03_room_junction_lamp_wallterminal.png` | inside the room: tape lump at the junction, plug into the standing lamp, a cord into a grommet in the east wall where the conduit ends inside the wall (live wall terminal; its hanging tail is hard to see on dark steel — known defect) |
| `mc_04_master_off_vanilla.png` | same scene with the master switch off: vanilla conduit art and hookup wires are back, no cords (taken on a roofed-ruin map before the roof was cleared, hence the shadows) |
| `offline_csharp_*.png` | the C# core's laid geometry on the Python oracle's scenes (SelfTest dump), red = fallback (none) |
| `textures_contact_sheet.png` | the 12 placeholder textures |
