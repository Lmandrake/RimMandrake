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
⛔ Not yet startable: the game was DOWN then LOADING (owner broadcast,
2026-09-11) as this item was unblocked, and the bridge is held by BENCH
(`WORLDMAP_FINAL_REVIEW_1`, live and non-stale — do not force-take a peer's
active bridge claim for this). Wait for the game to reach UP and the bridge
to free before starting the live legs. Do not deploy a new mod into the Mods
folder while the game is mid-load — RimWorld is reading that folder right now.
