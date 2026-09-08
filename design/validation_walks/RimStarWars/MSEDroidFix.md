# MSEDroidFix — validation walk
subject: src/RimStarWars/MSEDroidFix  (packageId `mandrake.rsw.msedroidfix`, from About/About.xml)
deps: Neronix17.OuterRim.DroidDepot (Outer Rim - Droid Depot) — sole modDependency; no loadAfter declared (deliberate, see About.xml: loose files always beat the donor's AssetBundle regardless of load order)
list: minimal+OuterRim Droid Depot
status-hint: no Defs, no Patches, no Assemblies — a single loose PNG (`Textures/OuterRim/Droid/MSE_north.png`) dropped at the texPath the donor mod's own PawnKindDef already asks for, to fill the missing 4th `Graphic_Multi` direction (About/About.xml)

## must be true
- The mod ships exactly one content file, `Textures/OuterRim/Droid/MSE_north.png`, and no Defs/Patches/Assemblies at all — "no defs are patched, no code runs" (About.xml, verbatim).
- `MSE_north.png` is 256×256 (matches the donor's own `MSE_south`/`MSE_east` canvas), with its inked bounding box at (97, 80, 159, 178) and a 3px black keyline — copied pixel-for-pixel from the donor's `MSE_south` silhouette per About.xml's own claim, so registration cannot drift from the other three directions.
- Outer Rim - Droid Depot's own `PawnKindDef OuterRim_MSEDroid` (`1.6/Defs/ThingDefs_Automatons/Animal/Droid_MSEDroid.xml`, quoted in About.xml) declares `texPath OuterRim/Droid/MSE` and `graphicClass Graphic_Multi` — so `Graphic_Multi`'s own direction-resolution logic must find `OuterRim/Droid/MSE_north` at load, given loose files win over the donor's AssetBundle regardless of load order.
- Before this mod exists, walking an MSE droid north (away from camera) shows its `MSE_south` (front) texture as a silent fallback — Graphic_Multi degrades quietly, no "Failed to find any textures at" error, because 2 of 4 directions (south, east) were present. After this mod, the same walk shows `MSE_north` (rear) instead.

## the walk
1. [L] Player.log after load contains no `Config error in mandrake.rsw.msedroidfix` and no "Failed to find any textures at" error naming `OuterRim/Droid/MSE`.
2. [D] `MSE_north.png` on disk is 256×256 RGBA with alpha bounding box `(97, 80, 159, 178)` — measured directly with PIL 2026-09-08 (`Image.open(...).getchannel("A").getbbox()` → `(97, 80, 159, 178)`, `im.size` → `(256, 256)`, file size 1051 bytes), matching About.xml's own claim exactly.
3. [D] def read-back: `PawnKindDef`/`ThingDef` `OuterRim_MSEDroid` (from Outer Rim - Droid Depot, once that mod is active) → `texPath == "OuterRim/Droid/MSE"`, `graphicClass == "Graphic_Multi"` — confirms this mod's file path assumption against the donor's LIVE def, not just the doc's quote of it.
4. [B] `jawa/texture_audit` on `OuterRim_MSEDroid` (or on `OuterRim/Droid/MSE`) → expect all four directions (`MSE_north`, `MSE_south`, `MSE_east`, and the mirrored west) resolve to a texture, with `MSE_north` specifically resolving to THIS mod's loose file rather than a fallback.
5. [B] `jawa/spawn_pawn` an `OuterRim_MSEDroid` pawn on a quicktest map with Outer Rim - Droid Depot active → `jawa/set_pawn_rotation` (or the pawn's facing) set to North → `jawa/pawn_atlas` (or an equivalent render/atlas read) confirms the resolved graphic path is `OuterRim/Droid/MSE_north`, not a silent south fallback.
6. [S] (human pass) look at an MSE-6 droid walking away from camera in play and confirm it shows a rear panel, not its own front.
