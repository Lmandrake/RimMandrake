# The far hanger drew over a colonist's head on east-west bridges: fixed, proven live (2026-11-27)

Item: RIMMANDRAKE_DRAW_SCRAPPER_JETTIES_HEAVY_BRIDGE_IN_HIS_PICKED_MANNER (judge question (a), verdict_heavy_bridge_Scrapper_B_ingame.md).

## Result

On an east-west span the ropes, hangers, backstays, rails and netting NORTH of the deck print at `AltitudeLayer.PawnRope` (21),
under `Pawn` (23); every other rope stays at `PawnUnused` (24), over him (`RM_SuspensionMath.RopeOverPawns`, `RM_DeckArt.RopeY`,
landed in 486dcad2f6). A colonist on the deck now draws in front of the far ropes and hangers and behind the near ones; a
north-south span is unchanged.

- Live, SteveDesktop lane, fresh quicktest, `live_deck_art_picks.py --heavy-scrapper --origin 100,135 --draw-order --rope-sides`
  (job J20261127T150946Z-24bd14, FlowWorks build 486dcad2f6, script 786e875fe3): ROPESIDES PASS on ew2, ew4 and ns4.
  Captures and readings: `fix_live_J20261127T150946Z-24bd14/`. Before and after on ew4 with the hat:
  `ew4_mid_hat_base_left_fix_right.png` (left: the base build, the far hanger over the crown; right: behind it).
- The same verdict on the base build's live readings (`base_live_J20261127T132644Z-f03cad/readings.json`, every rope at
  8.7805): FAIL on ew2 and ew4, "no rope lies behind him".
- Offline: the C# case `Suspension_far_rope_of_an_east_west_run_draws_behind_pawns` is red on the base's behaviour (every rope
  over) and green on the fix (T_BRIDGES 78/78; red seen recorded with `T_BRIDGES_far_rope_over_pawns.patch`).

## What decides what covers a pawn (measured, job J20261127T132644Z-f03cad on the base build)

- Every section sub-mesh has its bounds set to the section rect at y 0 (`MapDrawLayer.RefreshSubMeshBounds`; read
  boundsY centre 0, min -0.5, max 0.5 on every draw). So the renderer orders each sub-mesh as one draw at y 0, before
  every pawn. A print's height, or a material or section layer of its own, never moves that order.
- The cable (`Custom/Cutout`), the deck strip, the railing, the shadows (`Custom/Transparent`) and the colonist's nodes are
  all render queue 2900 (terrain reads 2328 to 2340, the lighting overlay 3100).
- The cable material's queue set to 2901, so drawn after the colonist (`jawa/material_queue`): 41 pixels changed, all
  blended edges. So a rope covers a colonist only by the depth test of its own vertices against his drawn nodes.
- The colonist's drawn nodes lie at y 8.38 to 8.48 over five jobs (`jawa/pawn_render_nodes`); PawnRope is 7.6829 and
  PawnUnused 8.7805.
- At the default zoom (root 24) a humanlike pawn draws as one cached atlas quad at his body height (8.38 to 8.45 read); the
  same heights decide.

## The first try, the same morning

`tried_far_rope_at_pawnrope.patch` is the change that landed. Its first live look (ArchSmall, a fresh quicktest map) showed
no change (`ew4_mid_bare_crop3x_after.png`, `ew4_mid_hat_crop3x_after.png`), and the deployed DLL matched the build by hash.
The measurements above show the code was right, so that look most likely ran the old assembly: RimWorld loads a mod
assembly only at game start, and a file hash does not show a restart [guess ~75%; that session's log is gone]. The lane's
deploy phase reloads the game when the mod drifts.

Ruled out then: the pit-depth draw patch (moves z only) and the under-liquid redraw (open liquid only).

## Owed

A fresh art judge (a run that did not make the fix) looks at `fix_live_J20261127T150946Z-24bd14/` (each span's colonist
bare and in a hat, and each end) for judge question (a).
