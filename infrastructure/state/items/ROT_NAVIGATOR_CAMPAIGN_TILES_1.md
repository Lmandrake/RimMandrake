## spec
Split from `ROT_NAVIGATOR_LOG_SITES_1` (the free-tier log, sites and landing ping shipped there). Campaign half only:
1. **Owner/BENCH names the tiles**: the Ash'karr Rot tile whose hwelgrue carries the drive core, and up to four
   tiles for the log's salvage sites (entries 2/4/6/8, used in order; fewer tiles = the rest fall back to the
   vanilla tile finder).
2. FOUNDRY then adds one `UtinniPatches` patch: `RM_SwallowedCoreExtension.campaignTile` on `ThingDef RM_Hwelgrue`
   and `campaignSiteTiles` on `RimMandrake.TheRot.RM_NavigatorLogDef RM_NavigatorLog`
   (`src/RimMandrake/TheRot/Defs/Misc/RM_NavigatorLog.xml`).

## criteria
- On the campaign save, `RM_SwallowedCoreProof.ProofClaim` names a carrier only on the authored tile.
- `RM_NavigatorLogProof.ProofPings 8` reveals a site whose world object sits on the first authored site tile.
