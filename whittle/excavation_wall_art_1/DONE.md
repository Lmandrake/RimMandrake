# Done claim

- true: **A1 (L1):** Every dug depth D1..D4 draws its own wall-face height (RM_WallFaceMath.NorthByDrop strictly rising; SelfTest WallFaces_every_depth_differs), liquid covers the f | evidence: `whittle/excavation_wall_art_1/evidence/selftest_wallfaces_spikes.log` `whittle/excavation_wall_art_1/evidence/wall_faces_proof_live.json` `whittle/excavation_wall_art_1/evidence/wall_faces_proof_live.log` `whittle/excavation_wall_art_1/evidence/broaden_e1_pit_changed_under_fixed_camera.png`
- true: **A2 (L1):** RM_Spikes, RM_Ladder and RM_LadderRaised ship bespoke PNGs (no magenta) and no FlowWorks def points at Things/Building/Security/TrapSpikeArmed. | evidence: `whittle/excavation_wall_art_1/evidence/a2_texture_census.txt` `whittle/excavation_wall_art_1/evidence/playerlog_texture_scan.txt` `whittle/excavation_wall_art_1/evidence/live_crop_D4_LADDER.png` `whittle/excavation_wall_art_1/evidence/live_crop_D4_SPIKES.png`
- true: **A3 (L3):** In a frame, D1..D4 read as visibly different depths and a superdeep cell reads as a hole, not a building (pit_depth_ladder_legible, pit_reads_as_hole, never_rea | evidence: `whittle/excavation_wall_art_1/evidence/live_row_ordinary_zoom.png` `whittle/excavation_wall_art_1/evidence/live_contact_sheet_D1_D4_water_spikes_ladder.png` `whittle/excavation_wall_art_1/evidence/live_crop_D4.png` `whittle/excavation_wall_art_1/evidence/broaden_e2_staircases.png` `whittle/excavation_wall_art_1/evidence/broaden_e5_row_after_save_reload.png`
- true: **A4 (L3):** In a frame, some amount of spike shows at the bottom of a spiked D=4 cell (spikes_read_distinct). | evidence: `whittle/excavation_wall_art_1/evidence/live_crop_D4_SPIKES.png` `whittle/excavation_wall_art_1/evidence/broaden_e3_spikes_single_cell_and_trenches.png` `whittle/excavation_wall_art_1/evidence/broaden_e4_spike_fade_half_metre.png`
- unseen: **A5 (L4):** The owner reviews the wall faces, spikes and ladder in game and keeps them. | evidence: `whittle/excavation_wall_art_1/evidence/live_contact_sheet_D1_D4_water_spikes_ladder.png` (staged for him; the look is his, see BLOCKED.md)

## How the evidence was made (2026-11-12, Archmagi, FlowWorks tier: 12 mods, all five DLC)

- FlowWorks DLL redeployed from main (it had drifted), then the fixed ladder sprites deployed; game restarted after each.
- `src/RimMandrake/FlowWorks/northstar/wall_art_scene.py` (new, committed) on a fresh quicktest map. It lays out a row of 3x3
  pits: D1, D2, D3 and D4 dry; D4 with 1 m of water; D4 spiked through the player's Architect "pit spikes" button; D4
  with a wooden ladder built through the Architect button on the north wall plus a second, raised one on the south wall;
  a D3 where spikes are tried and refused ("needs a sheer drop of 2 m"); and a 3x3 given the player's own "Dig to 4 m"
  order, which colonists with shovels partly dug. Ordinary clutter (rock chunks, logs) was left where it fell. Shots are
  at an ordinary zoom and at the closest zoom, in daylight. The map is saved as `EWA_WALL_ART_REVIEW_20261112.rws`.
- `wall_faces_proof.py` live: the loaded DLL draws north faces of 0.12 / 0.23 / 0.35 / 0.50 of a cell for D1..D4, and a
  5-deep pit with 1 m of water draws the 3-deep face (the water covers the foot of the wall). SelfTest
  `WallFaces_every_depth_differs` and 10 other wall-face and spike cases pass.
- The A2 census reads the DEPLOYED mod folder: 13 PNGs identical to the repo, 0 key-magenta pixels at any alpha,
  0 TrapSpikeArmed in deployed or repo FlowWorks defs. The resolved live defs inherit only BuildingBase. Player.log
  shows no texture errors.

## Fixed this round

- **Magenta in the raised ladder.** `RM_LadderRaised_east.png` and `_west.png` each carried one pure-magenta
  (225,0,225) pixel at alpha 17: Lanczos ringing in v5's side-view un-premultiply. `rail_pale.scrub_key_fringe` now
  recolours such fringe pixels from their neighbourhood, so a rebuild cannot bring it back. Every other pixel is
  byte-identical, so the owner-approved pale wood is unchanged; `selftest_fw_offline_art` pins that, plus a can-fail
  showing v5's raw output still carries the pixel. Installed through the art ledger (`c39192a556`, published
  `e406c3fda2`). The old PNG was owner-protected. The change is one invisible pixel per facing, so it is logged
  `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` and goes in his digest.
- **Owner-review staging showed spikes no player can build.** `owner_review_stage.py` put RM_Spikes in a 1.5 m pit and
  on the pit centre via `build_batch`, which bypasses the placeworker. It now uses a 2 m pit and skips the wall-less
  centre.

## What I'm least sure about

- **The spiked 3x3 shows a ring of stakes around a bare centre.** The centre square has no wall over it, and the
  shipped rule ("at the foot of a sheer drop of 2 m or more") refuses it. A4 holds, since stakes show in the spiked
  cells, but whether a ring reads right is a taste call for the owner's look.
- **D1 is subtle at ordinary zoom.** It reads as a lighter floor with a hairline face and an outline. It is clearly
  different from D2, but it is the weakest step of the ladder.
- **The raised ladder on the south wall is small** at ordinary zoom: a short ladder lying on the near lip. It is
  legible at the closest zoom.

## What I did not test

- Night, snow or roofed light. Section-boundary seams. Removing a spiked cell's wall afterwards. Every ladder
  rotation in this scene (owner_review_stage's ladder row covers all four walls; it ran at the start of this round,
  before the ladder pixel fix). The steel ladder (`RM_LadderSteel*`, outside this item) carries the same
  key-magenta fringe pixels (3 to 5 per side facing); it is filed, not fixed here.
- A5 is the owner's own look and cannot be made true by an agent.
