# EXCAVATION_WALL_ART_1: judge verdict (blind, 2026-11-12)

I read STATEMENT.md, NOTES.md and the item spec. I did not read DONE.md or BROADEN.md. I looked at every evidence image (the contact sheet, the four D4 crops, the ordinary-zoom row, and broaden e1 to e4) and read the census, Player.log scan, selftest log and live proof json. I ran `run_selftests.py --only selftest_fw_offline_art` myself: PASS, GREEN. I grepped the deployed FlowWorks XML for TrapSpikeArmed (no file) and listed the deployed Canals textures (RM_Spikes, RM_Ladder*, RM_LadderRaised* present).

## Per line

- **A1 true.** selftest_wallfaces_spikes.log line 158 has `ok WallFaces_every_depth_differs` (11 cases, exit 0). wall_faces_proof_live.json gives north heights for D1..D4 of 0.12, 0.23, 0.35 and 0.50, strictly rising. In the WET case (a 5-deep pit with water) the drop is 3, so the liquid covers the foot. The frames agree: the face band of "D4 + 1 m water" is thinner than the band of dry D4. The statement text is cut off at "covers the f", so I judged only the part that is visible.
- **A2 true.** a2_texture_census.txt: all 13 PNGs are bespoke, have 0 key-magenta pixels, and the deployed files match the repo. The deployed XML has 0 TrapSpikeArmed, and my own grep agrees. The Player.log scan has no texture errors, with a sanity probe of 27. The live frames have 0 magenta.
- **A3 true.** In the contact sheet and the ordinary-zoom row, the north face band grows and the floor darkens from D1 to D4. The staircases in e2 show four distinct steps in all three directions. D4 reads as a dark hole. Staging: in the main row the D3 cell is half covered by rock chunks, so e2 is the clean D3 look. D1 vs D2 is subtle at ordinary zoom. The heavy black cell outlines lean slightly toward a "box" look, but they do not make it read as a building.
- **A4 true.** The D4_SPIKES crop, e3 (a single cell, an N-S trench and an E-W trench) and e4 all show dense, pale spikes on the floor.
- **A5 cannot tell.** This is the owner's own look, and no evidence of it exists or can exist yet. A record of his keep or redo would settle it.

## Flags
- The first "E4 spiked D4 under 0.5 m" frame (inside broaden_e1, panel 5) shows water drawn over only the west two-thirds of the pit, while the east column stays dry. The separate e4 file is a re-shot frame with full cover, and the evidence gives no cause. This may be a stale water-mesh render, and the re-shot frame is the flattering one. It belongs to water rendering, not this art. Watch for it at the owner's sitting.
- In the 3x3 spiked pit the centre cell is bare. The spike rule refuses a cell with no wall over it, so the field has a hole in the middle. That is a mechanic, not art, but the owner will see it.
- The shots carry clutter: forbidden logs and chunks with red X marks next to the pits.

would show: yes
