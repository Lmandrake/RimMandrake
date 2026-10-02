# BlastDoorFrameAsyncFix — validation walk
subject: src/RimStarWars/StarWarsPatches  (packageId: mandrake.rsw.patches)
feature: blast-door-frame-async-fix
absorbed: BlastDoorFrameAsyncFix (dying id rsw.blastdoorframeasyncfix) folded into StarWarsPatches at Source/BlastDoorFrameAsyncFix + its Textures/.../Blast/SWDoorBlastBDoor_FrameAsync art in Sprint wave A (commit 7e6eda0bd) — no longer ships alone.
deps: Lumi.doorsexpanded (Doors Expanded Star Wars edition) — required, this mod loadAfters it
list: minimal+Lumi.doorsexpanded
status-hint: replaces 3 blank east split-frame textures (+ their _eastm masks) for Doors Expanded SW edition's blast doors, so the inner frame stops vanishing behind the leaves when the door faces east/west.

## must be true
- Ships exactly 6 loose PNGs under Textures/Things/Building/Door/Blast/, no Defs, no Patches, no code.
- Declares `loadAfter Lumi.doorsexpanded` so its loose files win the same-path resolution against the donor's own blank ones (loose beats loose only by load order; both are loose, no AssetBundle involved).
- SWDoorBlastDoor_FrameAsync_east.png, SWDoorBlastBDoor_FrameAsync_east.png and SWDoorBlastDDoor_FrameAsync_east.png each carry non-zero alpha (the donor's originals at the same path are transparent). CORRECTED (VALIDATION_SCRIPT_BACKFILL_1, measured with PIL against all 6 shipped files): the canvas is 936x936, not 933x933 as this line previously claimed.
- Each of the three ships its own `_eastm` colour mask at the same stem, so Graphic_Multi's `shaderType CutoutComplex` doesn't fall back to the north mask.
- Game load produces no Config error for mandrake.rsw.patches, and Doors Expanded SW edition's own defs PH_DoorBlastCDoor / PH_DoorThickBlastBDoor / PH_DoorBlastDDoor still resolve with the texPaths this mod's files are addressed to.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.patches" and no XML error naming any file under src/RimStarWars/BlastDoorFrameAsyncFix   # load-time
2. [D] asset check: script (PIL, same pattern as Source/verify_frameasync_east.py) opens the deployed .../BlastDoorFrameAsyncFix/Textures/Things/Building/Door/Blast/SWDoorBlastDoor_FrameAsync_east.png, SWDoorBlastBDoor_FrameAsync_east.png and SWDoorBlastDDoor_FrameAsync_east.png; each is 936x936 with max alpha > 0
3. [D] asset check: same script confirms the three `_eastm` masks (SWDoorBlastDoor_FrameAsync_eastm.png, SWDoorBlastBDoor_FrameAsync_eastm.png, SWDoorBlastDDoor_FrameAsync_eastm.png) exist at 936x936 — no missing-underscore/missing-suffix fallback to the north mask
4. [B] jawa/get_def {defType: "ThingDef", defName: "PH_DoorBlastCDoor"} (and PH_DoorThickBlastBDoor, PH_DoorBlastDDoor) resolves — confirms Doors Expanded SW edition is present and these defs' texPath still points at Things/Building/Door/Blast/SWDoorBlastDoor_FrameAsync (etc.), the path this mod's files fill
X. [S] (human pass) build one of each door facing east/west, close it, and confirm the inner frame reads as present with the leaves shut — not just alpha > 0 in isolation

## north star
state: DRAFT
validated-hash:

Seeded 2026-10-01 by an agent (NORTH_STAR_WALK_AUTHORING_1) from this walk's
`## must be true` and the mod's shipped sprites, defs and settings, on the owner's
ruling that day: *"You are mostly seeding the field right now with reasonable
initial guesses for refinement later through debugging needs or live feedback."*
Every line is an agent guess for him to accept, edit or cut; `(guess)` marks the
least certain. `### the experience` is his to dictate.

### the experience  (OWNER'S WORDS)
(not yet dictated)

### must show

**Blast doors facing east and west**
- [ ] `blastdoor_frame_visible_east` — the three Doors Expanded blast doors, built in
      an east-west wall, show their inner frame around the leaves, open and closed.
- [ ] `blastdoor_frame_tinted` — the frame takes the door's stuff colour like the
      north frame does. (guess)

### cannot show

- [ ] `blastdoor_never_frameless_sideways` — the inner frame vanishing behind the
      leaves on an east- or west-facing blast door.
