# GSS hose graphics fix 2026-10-05 (FOUNDRY helper)

## Root causes (measured)
2. RECTANGLES = vanilla WALL SUN SHADOWS drawn over the hose. Hose drew at AltitudeLayer.Conduits (5) with Custom/Transparent
   (queue 2900+3, ZWrite Off). Vanilla Custom/Sun shadow: queue Transparent+170 (3170), ZTest LEqual, ZWrite Off, quads at
   AltitudeLayer.Shadows (13); Edge shadow 2950. Read from resources.assets via UnityPy. Items/pawns escape it because
   Custom/Cutout ZWrites above the Shadows layer.
1. REEL JOIN: hose lay started at HoseReelRect.Mouth (under the pump) and the planner turned it straight to the target (or ran it
   back east UNDER the reel), so it never passed through the outlet coupling; coupling stub stopped short of the nozzle.
3. JOINER: each half's cloth wrap sat behind the coupling's narrow body -> wrap | bare hose + thin body | claws | ... gap.

## Changes (Source/Core/DrawOrder.cs, Source/Hose/HoseMath.cs, Source/Hose/RM_MapComponent_Hoses.cs, SelfTest/ReviewRound6Checks.cs)
- Hose band moved to LayerHose = Shadows (+0.004); every opaque hose piece gets a Cutout depth pre-pass (HoseMaterials.Depth,
  RM_MapComponent_Hoses.Solid) so sun/edge shadows fail the depth test on it; lighting/fog still cover it.
- Nozzled 2x2 reel: lay leaves dead straight west through the outlet (HoseLay.Outlet, Lay/LayAlong startOutward,
  OutletStraight 1.6, plan lead = straight + 2 bend radii, turn eased over 2 bend radii); own footprint blocked for its lay so
  a target behind the reel is reached round it; strand trimmed to start inside the coupling's wrap; coupling seated 0.07 into
  the nozzle; coupling drawn only when the hose really uses the outlet. Fallback to the old lay if no clear outlet.
- Joiner: wraps run up to the interlocked claws (JoinerWrapIn 0.09); WrapK 1.4 -> 1.3 (B22 floor, O6 still PASS).
- Selftest 680/680; validation O6 PASS.

## Screenshots verified (C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\)
- gss_fix6_reel__cell_rect.png / gss_fix6_run__cell_rect.png: st21 final, no shadow rectangles, hose through coupling.
- gss_fix3_reel__cell_rect.png: joiner (wrap-claws-wrap, no gap). Final build places no joiner at st21 (route changed).
- gss_scan5_st*__cell_rect.png: stations 11,12,16,17,22,29,30-33.

## Still open (for the owner)
- Relay reel fed by another hose (st29, reel 192,174): its west nozzle takes the FEEDING hose (round 7), so its own hose still
  starts under the drum (no outlet coupling). Needs a ruling on which fitting the outgoing hose uses.
- Boxed-in reel (st16 middle reel, reels stacked with no gap): no clear outlet route -> old under-the-drum start, no coupling.
- Drum shows no wound hose while deployed: Reel_Deployed art by design (B26 swap); not changed.
