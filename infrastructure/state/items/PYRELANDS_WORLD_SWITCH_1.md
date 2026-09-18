## spec
Deploy `RM_FE_Pyrelands` (built and closed by `PYRELANDS_SELF_CONTAINED_BIOME_1`,
2026-09-09 — self-contained biome, own everything, no donor dependency) to the
live Mods folder, prove it out on a quicktest, then switch Ash'karr's Pyrelands
worldmap tiles from the donor `ZBiome_Grasslands` to `RM_FE_Pyrelands` before the
world freeze. Unblocks the zylle donor retirement (owner ruled 2026-09-09).

## verify
Offline readiness already proven (`PYRELANDS_SELF_CONTAINED_BIOME_1`'s close: 12
XML files, 0 `validate_patch.py` errors in static mode). Remaining, live-only:
1. Deploy the mod (`deploy_custom_mods.py --apply`), confirm it loads with 0
   Config errors for its own defs (`validate_patch.py --live`).
2. Quicktest the biome: scorch-fruit spoilage, ash-fall/cinderfall weather,
   fast EmberGrass regrowth — read back, not assumed.
3. `jawa/world_tile_set` the Pyrelands tiles to `RM_FE_Pyrelands`, `jawa/world_commit`,
   confirm the read-back and a world-map screenshot.

## criteria
- RM_FE_Pyrelands live with 0 Config errors.
- Quicktest confirms the three named mechanics actually run.
- Ash'karr's Pyrelands tiles read back as `RM_FE_Pyrelands`, not `ZBiome_Grasslands`.

## Owner ruling, 2026-09-11
Asked directly: run the live quicktest now. Answered yes, then went AFK
("full auto, don't stop").

## Watch out
- Do not deploy a new mod into the Mods folder while the game is mid-load —
  RimWorld is reading that folder right now.
- ⚠️ The mod is already deployed; RM_FE_Pyrelands rides UtinniPatches/Pyrelands
  in the live 634 list. What has never happened is a clean FULL-LIST load with
  it: the 2026-09-17 23:31Z attempt died pre-menu on unrelated whole-file def
  discards (see BENCH note on this item) and RimWorld reset the live ModsConfig
  to Core+DLCs — restored from `ModsConfig.FULL.LATEST.xml`, fixes at
  `01eca070e`, relaunch 00:13Z 09-18. Verify the load survived before spending
  bridge time.
- Known cosmetic-or-worse config error to triage on arrival:
  `RM_FE_Ground_Sand/Gravel/Soil: burnedDef is flammable`.
