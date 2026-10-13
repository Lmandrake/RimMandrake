# tank_loop_rebuild (BUILT, ready for short live check)

Changed (src/RimMandrake/FlowWorks): Source/RM_NorthstarProofs.cs (+ProofTank: set tank mode/contents; DLL + .srchash rebuilt),
Source/SelfTest/TransferChecks.cs (allowlist ProofTank like the probe's filltank), northstar/extensions.py,
northstar/selftest_extensions.py, validation.py (bottleLoopEnabled leaves EXTENSION_TOGGLES_OWED: it now has real components).

Design (bottleLoopEnabled OFF for the whole tank chain so the terrain giver cannot win):
- tank_loop_on (toggle tankLoopEnabled): Store tank pre-filled 100 fresh water + RM_BottleEmpty -> units must FALL within 3000 ticks.
- tank_loop_pour_in: Fill-mode empty tank + RM_Bottle_FreshWater -> units must RISE within 3000 ticks.
- tank_loop_off: same two scenes with tankLoopEnabled OFF -> Store stays 100, Fill stays empty (3000 ticks each).
- toggle_bottle_loop: 4x4 WaterShallow pond + RM_BottleEmpty. ON: empty gone and RM_Bottle_FreshWater present within 3000; OFF: still 1 empty, 0 filled after 2000.
- Deviation: the probe `filltank:` verb is unreachable from the extension harness (no HoseProbe channel), so ProofTank does prefill AND mode in one static_call.
- toggle_bottle_dirty stays owed.

Selftests: selftest_extensions PASS (stateful fake covers moves/never-moves/ProofTank refused/ignores-setting); run_selftests 350/419, the 1 FAIL (stock Transfer_caller_coverage) was my ProofTank, fixed by the allowlist, stock selftest now 0 FAIL.
code_review_status: RM_NorthstarProofs.cs DIRTY (one method added; no full-file review done).

Live: python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live --chains toggle_tank_loop,toggle_bottle_loop
