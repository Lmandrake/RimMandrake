# Ramp + raised-ladder art — 2026-10-15 (BENCH art helper)
Owner by card 2026-10-15: "The pit ramp ships with a placeholder arrow, and the ladder has no 'raised' art. What do we do for release? → Make both today"

## Status — done offline (no deploy, no bridge)
- [x] existing-art check: ramp had none (artpipe `find PitRamp` 0 hits). **The raised ladder already existed**:
      artpipe `fwart_RM_LadderRaised` (2026-10-07), installed in 909240a2b5 at
      `Textures/Things/Building/FlowWorks/Canals/RM_LadderRaised.png`, wired through `RM_CompProperties_Ladder.raisedGraphicData`
      and drawn by `RM_Building_Ladder.Graphic` (mesh dirtied on toggle). Not regenerated. The card's premise was stale.
- [x] ramp art, Graphic_Multi, 4 facings, 256 px (drawSize 1), installed via `art.py install --owner-said <card words>`:
      `Textures/Things/Building/FlowWorks/Excavation/RM_PitRamp_{north,east,south,west}.png`
- [x] def wired: texPath + Graphic_Multi + ignoreThingDrawColor (stuff tint would darken painted art); "(Placeholder art.)" and
      the XML placeholder comment removed; selftest `Ramp_wiring_pinned_at_call_sites` re-pinned to the real art.
- [x] texPath binds: validate_patch OK (0 errors); four facing files present.
- [x] contact sheet `Transient/ramp_ladder_art_2026-10-15/sheet.png` (64 px/cell in a pit, + 2x row) — looked at.
- [ ] OWED: owner look on the FlowWorks walkthrough map — station 27 (pit ramp), station 34 (ladder art lowered/raised; ladder def 33).
- [ ] OWED (C#, not touched to avoid rebuilding others' uncommitted FlowWorks work into the DLL): stale comment
      `Source/Superdeep/RM_PitRamp.cs:18` "ART: PLACEHOLDER" — fix at the next FlowWorks C# rebuild.

## How the ramp was made
Camera: design/RimMandrake/building_camera_perspective_2026-10-14.md. A ramp is floor-level (FloorEmplacement), so the read is
carried by light: the high (uphill) end is brightest, the low end darker in the pit; north shows lit step risers (stairs climbing
away), south shows dark drops (stairs descending away), east/west a side wedge of earth at the south edge.
- `art_source/PitRamp/guide.py` — grey blockouts (image 1 of each edit).
- `codex_image.py edit --model gpt-6.1-sol` (gpt-5.5 default refused on this account): north_b from guide_north + RM_WallFace_North
  (earth) + a first timber attempt; south_b from guide_south + north_b as sibling; east_c = north_b rotated 90° then relit by edit
  (guide_east attempt read as a crate and was rejected). West = east mirrored.
- `art_source/PitRamp/finalize.py` — premultiplied BOX to 256, alpha<32 zeroed, east inset 12 px (wedge touched the canvas edge).
- `art_source/PitRamp/sheet.py` — the contact sheet.
