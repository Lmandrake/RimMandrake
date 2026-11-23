# HOSE_CROSSING_FIX_FLAT_AS_A_PANCAKE

FlowWorks hose, audit F8 / defect D11 (`Transient/pile_2026-10-22/hose_audit.md` §3): map R hoses 382378 x 382379
"cross flat, one painted over the other with no lift or shadow".

## criteria
- A1 L0: SelfTest `joints:` CrossSpans rows green; selftest_joint_check.py crossing rows (lifted passes, flat FAILs, an
  older probe without `crossings` still FAILs).
- A2 L2: on the walkthrough, joint_check.py --all-maps reports every crossing `lifts over` and a zoomed crop of the map R
  crossing shows the upper hose's crossing shadow on the lower one (judged by a second agent).

## built
- `RM_MapComponent_Hoses.DrawCrossShadow`: the upper hose (B18 band) casts a deeper, wider, further-offset shadow onto the
  lower one over the overlap (HoseOverDraw.CrossSpans vs every lower-ranked drawn strand, +-0.25 cell); spans recorded.
- HoseProbe `joints` answer carries `crossings` ({upper, lower, at, lifted}); joint_check.crossing_joints judges by it.
