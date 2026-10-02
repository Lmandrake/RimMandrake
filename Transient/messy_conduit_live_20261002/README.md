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

## Live pass 2: real art (2026-10-02 15:09)

Same scene as above, now with the 8 real artpipe textures (4 placeholders kept: EndFrayed_Live, SparkGlow, PowerStrip,
ConduitTransparent), plus an **X node** at 155,153 (north arm to a second lamp, south arm into a 3x3 granite block,
giving a rock stub). The shots come from the scene AFTER a save and reload (`MC_LIVE2B_20261002.rws`, keeper,
in the game's Saves folder), so they also show that cords draw after a load. Paused, about 1 PM. Crops 02-04 are
cut from the full frames and upscaled (LANCZOS, 3x or 4x) so you can see detail. No pixels were edited.

| file | what it shows | visual defects |
|---|---|---|
| `real_art_01_wide.png` | the whole scene: battery, X node with lamp and rock run, gap, doorway, room with T node, lamp and east-wall run, far dead run | overall it reads well: loose dark rubber cords with real loops and heaps. The granite block reads as a grey slab, not a rock outcrop (a 3x3 natural `Granite` block spawned on cleared soil, which is a staging artefact) |
| `real_art_02_junctions_X_and_T.png` | left: the X node (tape lump). right: the T node in the room (tin box) | **X:** the tape lump is a faint brown disc drawn UNDER the cords and almost invisible. **T:** the tin's stub arms do NOT line up with the cords: one short capped arm points east and one points south into empty floor while the cords join at other angles (the flagged "arms reach the canvas edge" problem). **Plug:** the room lamp's cord ends at the conduit cell east of the lamp, so the plug lies one cell away from the lamp instead of reaching it |
| `real_art_03_wall_grommet_and_rock_hole.png` | left: the cord into the east wall. right: the cord into the granite block | the wall grommet is drawn under the wall sprite, so only an orange sliver shows and the cord seems to stop at the wall face. The rock stub is mostly hidden by the rock edge and shows as a small grey lump. Both are an altitude (draw order) issue, not texture defects |
| `real_art_04_break_live_vs_dead.png` | the break: west (battery side) end LIVE, east end DEAD | the live fray is bright orange and the dead fray is dull: this reads well. The dead end is straight, not limp, at this zoom. No sparks show because sparks are flecks thrown on ticks and the shot is paused |
| `real_art_05_master_off.png` | the same view with the master switch off: vanilla conduit (cross at the X node, T in the room, run into the rock and the wall) | none. Vanilla art came back with no restart |

No seams, z-fighting or floating cords were seen at this zoom. The strand texture tiles cleanly.
Saves: `MC_LIVE2_20261002.rws` (made BEFORE the fixes: it holds the component entry, so keep it as an M9 regression
fixture); `MC_LIVE2B_20261002.rws` (the keeper scene); `MC_LIVE2C_inplace_20261002.rws` (save without reload, used to
check the running component survives a save). Saves folder backup: `D:\Luke\dev\_rmscratch\saves_backup_20261002_messyconduit`.

## Polish pass: the art fits the cords (2026-10-02, ~16:00)

Same keeper scene (`MC_LIVE2B_20261002.rws`), reloaded after the fix; one paused frame at about noon,
`real_art_06_wide.png` (zoom root 11, 54 px per cell); the other 06 files are crops of that frame upscaled 3x
(LANCZOS). No pixels edited. State proof: probe `artfit` = 0 faults (2 junctions, 8 plug ends, 2 stubs, 9 dead
ends, 1 live end), the same on a fresh validation map; `validation.py --live` 19/19, `--save-load MC_POLISH_20261002`
3/3, `--removal-check MC_POLISH_20261002` PASS.

| file | what it shows | still imperfect |
|---|---|---|
| `real_art_06_T_junction_and_lamp_plug.png` | the room's T: the taped T is turned so its arms point west, east and north, and each bundle of cords runs into an arm. Top: the lamp's plug now sits on the lamp's east side, head pointing into it | the lamp shows its no-power bolt (the room is on the dead side of the break, as designed); the plug head tucks under the lamp sprite |
| `real_art_06_X_junction.png` | the X: the tin cross now draws over the cords, its four arms on the four cords | none seen |
| `real_art_06_wall_and_rock_stubs.png` | left: the grommet plate on the east wall's face with the hanging tail below it. Right: the hole on the rock face with the cord going in | the rock-side conduit ends inside the rock, so a wall-style tail hangs down the rock face as a thin dark line |
| `real_art_06_dead_vs_live_end.png` | the break: west (live) end straight out of the conduit end with a glow at the tip; east (dead) end curled over with a dull fray | the dead curl (0.27-0.38 cell sideways) is clear at this zoom but subtle zoomed out; no whip on the live end (phase 1b) |
| `real_art_06_pawn_and_items_over_pieces.png` | a check, not a review shot: colonists and item stacks spawned ON the tin, the T, the plug, the live end and next to the stub all draw over the pieces | taken at dusk on `MC_POLISH_20261002` |
| `real_art_06_wide.png` | the whole scene after the fix | the granite block is still a staging slab, not an outcrop |

What changed: junction art posed from the arriving cords (tin cross for 4 directions, taped T with its gap where
no cord comes); cords end at the arm tips, the plug point and the stub faces, arriving along the art; plugs point
into the machine; stubs turned along the cord; explicit render queues (every section submesh shares one bounds box,
so altitude alone never ordered them; walls and the Transparent shader are both queue 2900, measured); face pieces
at `BuildingOnTop`; dead ends curl 0.7 cell; live ends straight with a per-frame glow.

Art the pipeline could still improve (not queued): a real `EndFrayed_Live` (bright copper strands; the procedural one
reads fine with the glow), and a rock-face tail variant if the hanging tail on rock bothers you.
