# The far hanger draws over a colonist's head on east-west bridges: one fix tried, no visible effect (2026-11-27)

Item: RIMMANDRAKE_DRAW_SCRAPPER_JETTIES_HEAVY_BRIDGE_IN_HIS_PICKED_MANNER (judge question (a), verdict_heavy_bridge_Scrapper_B_ingame.md).

Tried (`tried_far_rope_at_pawnrope.patch`, not landed): `RM_SuspensionMath.RopeOverPawns(sideZ, sg)` puts every rope, hanger,
backstay, rail and netting run north of an east-west deck at `AltitudeLayer.PawnRope` (21) and the others at `PawnUnused` (24),
in PrintEnd, PrintTimberRail and PrintNetting (`RopeY`). The C# case `Suspension_far_rope_of_an_east_west_run_draws_behind_pawns`
was red on the parent and green on the change; the deck-art, rope, timber and jetty selftests stayed green.

Live, ArchSmall, fresh quicktest, `live_deck_art_picks.py --heavy-scrapper --origin 100,135`, the deployed DLL byte-equal to
the build (md5 e95abf4b…, srchash names RM_DeckArt.cs 0727d3b8…): the far hanger still draws over the hair (bare) and over the
hat crown (hat) on ew4 (`ew4_mid_bare_crop3x_after.png`, `ew4_mid_hat_crop3x_after.png`). So the altitude of a run inside
the section-layer cable mesh does not decide whether it covers a pawn.

Ruled out: an old DLL (hash matched); `RM_Patch_PitDepthDrawOffset` (moves the drawn z only, never y); the
`Printer_Plane.PrintPlane` split in RM_SubmergeDraw (acts only in an open liquid split; this pit is dry).

Not measured (no bridge read exists): the drawn y of each pawn render node, and the render queue or sort of the
section-layer cable submesh against the pawn's materials. Next: a Test Pilot sitting reads both, then fixes the order.
