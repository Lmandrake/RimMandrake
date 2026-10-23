# JOINT_GATE_HARDEN_TRUST_THE_DRAWN_BOX

FlowWorks joint gate, audit F9 (`Transient/pile_2026-10-22/hose_audit.md` §5(a)): "for every reel/port, the drawn collar's
box must overlap the nozzle/port sprite box (state read + zoomed crop per joint); red blocks the showing". Owner card
2026-10-23 (HOSE_LOOK_DECIDE_OVERGROUND_OR_UNDERPIPE): keep over-ground, add a joint check. **Fallback that is part of the
decision:** if this gate cannot go green on both walkthrough maps in one sitting, the under-pipe option (§5(b)) is to be
reconsidered and put back to the owner.

## criteria
- A1 L0: SelfTest `joints:` CollarBoxes rows (drawn collar covers the tip/flange every look x facing; can-fail: 0.2 short,
  0.4 beside) and selftest_joint_check.py (gate(), crops, camera restore, scenarios_map save refusal) green.
- A2 L2: live on both walkthrough maps (C and R), `joint_check.py --all-maps --crops Transient/joint_gate/<stamp>` prints
  JOINT CHECK: PASS with a crop for every joint, and the crops are read by a second agent before anything is shown.
- A3 L2: `scenarios_map.py --save` refuses while the gate is red (live read of the refusal line) and saves when green.

## built
- RM_MapComponent_Hoses records each coupling AS DRAWN (reel_end, port_end, relay_end, feed_nozzle); HoseJointProbe adds
  `collar_box` rows (HoseJoints.CollarBoxGap: target to the coupling's opaque box) and "no collar drawn" FAILs.
- joint_check.py: `through_wall` rows (census wallCross), crossings by probe lift, `--crops DIR` (camera on each joint at
  rootSize 8, marked crop, index.json, full frames removed, camera restored), `gate()` library call.
- scenarios_map.py `--save` (map C and --river) runs the gate on every loaded map first; `--allow-red-joints WHY` overrides
  for a save not meant for the owner.
