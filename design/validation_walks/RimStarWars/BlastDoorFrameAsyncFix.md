# BlastDoorFrameAsyncFix — validation walk
subject: src/RimStarWars/BlastDoorFrameAsyncFix  (packageId: mandrake.rsw.blastdoorframeasyncfix)
deps: Lumi.doorsexpanded (Doors Expanded Star Wars edition) — required, this mod loadAfters it
list: minimal+Lumi.doorsexpanded
status-hint: replaces 3 blank east split-frame textures (+ their _eastm masks) for Doors Expanded SW edition's blast doors, so the inner frame stops vanishing behind the leaves when the door faces east/west.

## must be true
- Ships exactly 6 loose PNGs under Textures/Things/Building/Door/Blast/, no Defs, no Patches, no code.
- Declares `loadAfter Lumi.doorsexpanded` so its loose files win the same-path resolution against the donor's own blank ones (loose beats loose only by load order; both are loose, no AssetBundle involved).
- SWDoorBlastDoor_FrameAsync_east.png, SWDoorBlastBDoor_FrameAsync_east.png and SWDoorBlastDDoor_FrameAsync_east.png each carry non-zero alpha (the donor's originals at the same path are 933x933, 100% transparent).
- Each of the three ships its own `_eastm` colour mask at the same stem, so Graphic_Multi's `shaderType CutoutComplex` doesn't fall back to the north mask.
- Game load produces no Config error for mandrake.rsw.blastdoorframeasyncfix, and Doors Expanded SW edition's own defs PH_DoorBlastCDoor / PH_DoorThickBlastBDoor / PH_DoorBlastDDoor still resolve with the texPaths this mod's files are addressed to.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.blastdoorframeasyncfix" and no XML error naming any file under src/RimStarWars/BlastDoorFrameAsyncFix   # load-time
2. [D] asset check: script (PIL, same pattern as Source/verify_frameasync_east.py) opens the deployed .../BlastDoorFrameAsyncFix/Textures/Things/Building/Door/Blast/SWDoorBlastDoor_FrameAsync_east.png, SWDoorBlastBDoor_FrameAsync_east.png and SWDoorBlastDDoor_FrameAsync_east.png; each is 933x933 with max alpha > 0
3. [D] asset check: same script confirms the three `_eastm` masks (SWDoorBlastDoor_FrameAsync_eastm.png, SWDoorBlastBDoor_FrameAsync_eastm.png, SWDoorBlastDDoor_FrameAsync_eastm.png) exist at 933x933 — no missing-underscore/missing-suffix fallback to the north mask
4. [B] jawa/get_def {defType: "ThingDef", defName: "PH_DoorBlastCDoor"} (and PH_DoorThickBlastBDoor, PH_DoorBlastDDoor) resolves — confirms Doors Expanded SW edition is present and these defs' texPath still points at Things/Building/Door/Blast/SWDoorBlastDoor_FrameAsync (etc.), the path this mod's files fill
X. [S] (human pass) build one of each door facing east/west, close it, and confirm the inner frame reads as present with the leaves shut — not just alpha > 0 in isolation
