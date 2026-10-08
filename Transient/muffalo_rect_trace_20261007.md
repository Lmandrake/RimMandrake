# Muffalo dirt-rectangle trace, 2026-10-07 (source read only)

Screenshot (`Transient/desk_muffalo_crop.png`, 2026-10-06 20:50): a hard-edged, ~1.2-cell-wide ground-coloured rectangle, semi-transparent (body ghost visible), narrower than the creature (both flanks stick out), top edge flat.

## Verdict: already traced and fixed (ledger item PIT_LIP_OCCLUDES_OUTSIDE_1, fix a100d8e2e, 2026-10-06 23:13, after the screenshot)

## H1 (top, near certain): RM_PitLipOcclusion cover quad
- `src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitLipOcclusion.cs:105` draws at `AltitudeLayer.Pawn + 0.9*AltInc`, `:197` `Graphics.DrawMesh`, material = the terrain's own DrawMatSingle cloned into a render queue after pawns (`RM_FaceMaterial.cs:113`), alpha 0.85 (`RimMandrakeFlowWorksMod.cs:177`). That is exactly "dirt-coloured, over the body, ghost visible, flat hard edges".
- The sprite width used (`HalfExtent`, :56) came from `sqrt(bodySize)*1.2` (~1.86 for muffalo) while the real graphic is 3 cells; the cover stopped short of the flanks (file comment :50-55 says the same).
- Second cause per BENCH ledger note: a D4 pawn is sunk 4 rows south by PIT_DEPTH_DRAW_OFFSET, drawn outside the opening, with the cover over it.
- Fix a100d8e2e: sink clamped so drawn centre stays north of the near lip; HalfExtent uses body graphic drawSize. BENCH re-shot the repro save live (`Transient/flowworks_art_muffalo/muffalo_after_fix.png`): no rectangle. Ledger event `implemented` (needs bridge, L2, A1) is filed; owner look still pending.
- Deployed DLL (`Assemblies/RimMandrakeFlowWorks.dll`, 2026-10-07 03:14, repo and Mods copy same size) postdates the fix.

## H2: stale build when the screenshot was taken
The shot predates the fix and a re-check at 22:23 still showed the bug. If a rectangle appears again on the current DLL, first confirm the running game loaded the 03:14 DLL.

## H3 (low): wall-face / excavation section layers
`RM_ExcavationWalls.cs:57` draws at TerrainScatter altitude, below pawns, so cannot cover a pawn. No pawn-altitude or graphic-alpha candidate found in FlowWorks Defs.

## Falsifiable test (one bridge call)
Load `RM_pitlip_muffalo_bug_20261006` (Muffalo24734 at 172,135) and screenshot it with `RimMandrakeFlowWorksSettings.pitLipOcclusionEnabled=false`. Rectangle gone with it off, present with it on, confirms H1. On the current DLL expect none either way.

## Not determined
No live check from here (offline only). I did not verify that the screenshot's rectangle is the muffalo from that repro save, nor that the deployed DLL contains a100d8e2e (inferred from timestamps and commit order, not from a hash).
