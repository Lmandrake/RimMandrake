# Messy Conduit polish pass — 2026-10-02 (FOUNDRY)

Fixing live pass 2 visual defects. Appended per fix.

## Status
- (1) T junction arms alignment: pending
- (2) X junction tape lump draw order: pending
- (3) wall grommet / rock stub hidden: pending
- (4) lamp plug offset: pending
- (5) dead end vs live end: pending

## Log
- start: baseline selftest 102/102. Read: real art geometry measured (Tape = T with arms W/E/S, junction point 0.152 canvas above centre; Tin = 4-arm cross centred; StubWall plate centred, cord from -X; StubRock hole centre +0.11; Plug head face +0.46). Causes found in code: junction decal angle = random +-0.6 rad (not from arms) and cords end at node centre; stub decals rotated +90deg (placeholder-era orientation, real art cord is along +X); plug angle = cord travel angle, centred on tip outside the device; LimpTail curl only ~0.1 cell. Draw order: MapDrawLayer.RefreshSubMeshBounds gives every submesh the same bounds (CellRect.ToBounds, decompiled 1.6), so transparent submeshes tie on sort distance and y alone does not order them -> use explicit renderQueue; stub face decals also lifted to BuildingOnTop altitude.
- RED: SelfTest gains ArtFitChecks (independent art geometry constants measured from the PNGs): junction art point on the node + an arm along every arriving cord + cord ends at the arm tip arriving along it; plug head inside the machine footprint, axis-aligned; stub decal along Into with plate/hole on the face; dead end tip >=0.22 cell off the conduit line and curled >=50deg; live end straight out of the conduit end. Result 116/137 (21 new FAILs across all scenes) -- red as intended.
- GREEN (core): selftest 137/137 (102 old + 35 new), --probe 7/7. Core changes: CordBuilder.PoseJunction (tin cross for 4 arm directions, taped T turned so its missing arm faces the empty side, art junction point on the node), AttachEnd/CordLayer.Approach (cords end at the arm tip / plug point / stub face / conduit end, arriving along the art's axis), one plug per end turned INTO the machine and pushed 0.05 past the edge, stub decals along Into (plate/hole on the face line), LimpTail 0.7-cell curl falling 0.30 cell sideways (walkability-guarded), junction knot jitter removed (it misaligned neighbouring T arms). Offline render with the real art checked by eye (scratch).
- Verse side: CordMaterials sets explicit render queues (shadow = strand-1, end pieces strand+1, face pieces + hanging tail strand+2); face pieces at BuildingOnTop altitude; live-end glow drawn each frame (MoteGlow, works paused); probe gains "artfit" (Core.CordAudit on live pieces + queues + wall/rock material). Core audit moved to Core/CordAudit.cs (shared by SelfTest and probe; csproj lines added both). Selftest 137/137. winbuild MessyConduit: 0 errors.
- 15:53 game PID 40156 killed; deploy --apply 2 files VERIFIED (DLL+srchash)
- 15:58 relaunched (Steam) on messyconduit tier; loaded MC_LIVE2B_20261002. LIVE artfit: faults 0 (junctions 2/0, plug ends 8/0, stubs 2/0, dead ends 9/0 off-line 0.27-0.38, live 1/0 arrival 0deg), glowDraws 2. Measured queues: Transparent shader = 2900 and the WALL and GRANITE materials are Custom/Cutout at queue 2900 too -> the old stubs tied with the wall on queue AND sort distance (why they hid); now face pieces 2902, end pieces 2901, shadow 2899.
- 15:59 screenshots on MC_LIVE2B (paused, ~noon, root 11 = 54 px/cell, crops 3x LANCZOS): real_art_06_wide / _T_junction_and_lamp_plug / _X_junction / _wall_and_rock_stubs / _dead_vs_live_end. By eye: X tin cross over the cords with all 4 cords entering its arms; T arms W/E/N each with its cords; lamp plug head into the lamp's east side; wall grommet plate on the wall face (hanging tail visible); rock hole on the rock face; live end straight + glow, dead end curled + dull fray.
- 16:00 validation --live --fresh-map: 19/19 PASS, 6 UNBUILT, 2 UNCOVERED (northstar/validation_result_20261002T160022.json); live2 extend + artfit on the fresh map: faults 0 (same counts)
- 16:00 --save-load MC_POLISH_20261002: 3/3 PASS (geometryHash c28208f0d5e60028 before == after, 8 edges, new file only, 0 mentions of our types in the save)
- 16:06 tier flowworks + relaunch; --removal-check MC_POLISH_20261002: M9 PASS (load 4 s, 0 errors naming the mod, conduit present). OPEN QUESTION before closing: queue 2901/2902 pieces could draw OVER pawns/items standing on them if RimWorld's cutout shaders do not write depth (the old stub-under-wall result suggests ties are order-based). Measuring live with a pawn + items on the pieces.
- 16:11 occlusion check (messyconduit tier, MC_POLISH loaded, 2 colonists + steel/component spawned ON the X tin, T tape, lamp plug, live end, wall stub): pawns and items draw OVER the raised-queue pieces -> no regression (real_art_06_pawn_and_items_over_pieces.png, dusk light). Restoring flowworks tier.
- END 16:16: game UP on flowworks tier (main menu, MessyConduit absent). README polish section + design §8.13 updated (old "known defects" replaced). Nothing committed (brief forbids git).

## Status
- (1) T junction: FIXED (pose from cords + cords to arm tips), live artfit 0 faults, screenshot real_art_06_T_junction_and_lamp_plug.png
- (2) X junction draw order: FIXED (render queue 2901 over strand 2900), real_art_06_X_junction.png
- (3) wall grommet / rock stub: FIXED (queue 2902 + BuildingOnTop altitude + art turned along the cord), real_art_06_wall_and_rock_stubs.png
- (4) lamp plug: FIXED (one plug per end, head into the footprint), same T screenshot
- (5) dead vs live: FIXED within 1a (0.7-cell curl, dull fray; live straight + per-frame glow); no whip (phase 1b)
