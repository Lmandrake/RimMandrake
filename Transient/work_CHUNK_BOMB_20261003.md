# CHUNK_BOMB 2026-10-03 (GELATINOUSSLIME_TITAN_CHUNK_BOMB_1)
## Searched first
- RM_TitanoslimeChunk ALREADY EXISTS (Defs/ThingDefs_Items/SlimeSealBreach.xml, butcher product of RM_Titanoslime, Usable seal-breach comps). Reused as THE bomb item, not duplicated.
- NOT existing: any throw verb, burst, timed shrink (DeteriorationRate 6 does not tick in an inventory), terrain-for-a-while. artpipe find chunk/titanoslime: only titanoslime body art; no chunk art -> keeps tinted vanilla Meat_Big placeholder, no art queued.
## Choices (numbers [INVENTED])
- Route: grenade shape (cheapest honest): chunk gets equipmentType Primary + CompEquippable + a Verb_LaunchProjectile "throw titanoslime chunk" (copied from vanilla Weapon_GrenadeFrag), projectile RM_Proj_TitanoslimeChunk (class Projectile_SlimeChunk). Seal-breach comps kept. stackLimit 5 -> 1 (each chunk has its own clock).
- Burst (Impact): radius 3.9. Every non-resistant flesh pawn in radius: Slimification set to severity 0.55 (stage 2 "half absorbed": holds off slime, only dry ground/antidote undo; no armour check). Cells: natural unfloored terrain becomes RM_Slime_Mud for 1 day, then reverts (MapComponent_ChunkBurst, Scribed). Smear filth + green mote splash; letter-less message naming who was drenched.
- Shelf: CompChunkShelf stores birth tick; MapComponent_ChunkShelf sweeps map items + spawned pawns' inventories every 250 ticks, chunk past shelf days is destroyed (smear if on the ground, message). Applies to the seal use too (same item).
- Settings: chunkBomb (bool, default on; off = thrown chunk lands inert, still shrinks), chunkShelfDays (float 0.5..5, default 1.5).
- Ban 7 exception recorded as the owner's (card 2026-10-02 14:44 PDT); body never arms itself.
## Not done
- Live criteria (throw drenches a pawn; unused chunk shrinks) need bridge: OPEN. Not deployed. Unverified in engine: verb consumes the item as vanilla grenades do (def shape copied from Core).

## Results
- winbuild: succeeded 0 warnings; selftest_slime_suite exit 0 (66 components, 30 faults incl. chunk_bomb_defs); validate_patch OK (2 warnings, both unresolved vanilla parents without --defs). Mock FIELDS extended.
