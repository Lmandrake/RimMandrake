# BELT Messy Conduit live pass 2 — 2026-10-02

Progress log (appended per step).

## Step 0 — start
- 15:0x step 1 DONE: game PID 38720 killed; deploy --apply 15 files VERIFIED; tier messyconduit applied (9 mods); Steam launch, bridge up; Player.log shows "[MessyConduit] targets: PowerConduit, WaterproofConduit; invisible=True".

## Step 2 — live validation
- step 2: validation --live --fresh-map 19/19 live PASS, 6 UNBUILT, 2 UNCOVERED, 268 ticks -> northstar/validation_result_20261002T150004.json
- record: modcheck record MessyConduit -> REFUSED at b21ff367ace3 (honest: 6 UNBUILT + 2 UNCOVERED)
- scene extended (live2.py extend): X node at 155,153 (N arm -> 2nd lamp, S arm into a 3x3 Granite block -> stub_rock); census: 8 cord edges, junction 2, stub_rock 1, stub_wall 1, terminal 4, 0 fallbacks, 0 unwalkable; clock +15000 ticks for light
- Saves folder backed up: 54 top-level files -> D:\Luke\dev\_rmscratch\saves_backup_20261002_messyconduit (+ saves_manifest_before_20261002_mc.txt)

## Step 3a — save/load (validation.py --save-load, new mode)
- M4 FAIL (real MOD defect): after load the graph exists (8 edges, same nodes) but 0 pieces/0 strands/0 decals -> NO cords drawn on any loaded save. Log seq 36: "Could not regenerate layer SectionLayer_RM_MessyCords: NRE at MapDrawer.MapMeshDirty". Cause (RimSage MapDrawer): RegenerateEverythingNow creates Section objects inside the regen loop, so Rebuild dirtying later sections hits null slots; pieces were assigned AFTER the dirty loop so the throw lost them. Fix: publish pieces before dirtying + DirtySection skips not-yet-created sections. Also: the save carries <li Class="RimMandrake.MessyConduit.RM_MapComponent_CordGraph" /> (M9 risk) -> measure.
- DLL rebuilt (0 err) + deployed. Tier flowworks applied (note: modset_builder overwrote untracked deployed/config/ModsConfig.before-tier-flowworks.xml with the messyconduit list; .kept-20261002 copy untouched). Launched.

## Step 3b — mod removal (validation.py --removal-check, new mode)
- M9 FAIL (real MOD defect) on save MC_LIVE2_20261002, flowworks tier, load 4 s: 2 red errors: "Could not find class RimMandrake.MessyConduit.RM_MapComponent_CordGraph while resolving node li" + "SaveableFromNode exception: Can't load abstract class Verse.MapComponent". No other errors. Fix: Harmony prefix/finalizer on Map.ExposeComponents removes the component while SAVING (FillComponents re-add dropped). Built 0 errors.
- relaunched on messyconduit tier with both fixes deployed

## Step 3c — re-prove: --live, extend, --save-load MC_LIVE2B_20261002
- re-prove: --live 19/19 PASS (validation_result_20261002T150809.json); extend same census (geometryHash d957f9fa758583d6, identical to the first map)
- M4 PASS: save MC_LIVE2B_20261002.rws (new file only, nothing else changed), load 2 s, geometryHash d957f9fa758583d6 == before, 8 edge hashes, decals/ends/strands identical; M9a PASS: 0 mentions of RimMandrake.MessyConduit in the save; no error in log

## Step 4 — screenshots
- screenshots taken (paused, ~1 PM): rl2_wide, rl2_left, rl2_right (root 11), rl2_off (master off); crops -> Transient/messy_conduit_live_20261002/real_art_01..05
- in-place save MC_LIVE2C_inplace_20261002: running component kept (builds 2 before/after, hash same, layerVerts 15508); 0 occurrences of RimMandrake.MessyConduit in it

## Step 5 — removal re-check + end state
- M9 PASS on MC_LIVE2B_20261002 (flowworks tier, load 3 s, 0 errors naming the mod, 0 Player.log lines, conduit present)
- Saves folder vs manifest: 54 original files unchanged; 3 new MC_LIVE2* saves only
- comment-only rebuild (DLL bytes unchanged, srchash updated) deployed; selftest 102/102
- docs: validation.py docstring + LEARNED, walk parentheticals M4/M9 + step 3, design 8.13, README
- END: game UP on flowworks tier (MC_LIVE2B save loaded, mod absent); modcheck status = REFUSED recorded at 93fd84eddacc (run 150809); a re-record now says STALE (only doc/comment edits + identical DLL since) -- next live run re-records. Nothing committed (brief forbids git).
