# HOSE_ORDERS_MEND_WAITING_FOREVER

FlowWorks: dropped-hose gizmo orders stall with auto-resume off; menu/driver mismatches

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C7b-F2** CONFIRMED MEDIUM — With 'auto-resume dropped hose' OFF, the reel's own Move/Retract gizmo orders on a dropped hose never run. HoseOrderRules.MayResume (Hose/HoseCarry.cs:270-271) refuses Dropped unless forced/auto; OrderMove/OrderRetract (CompHoseReel.cs:386,395) set pending but leave carry Dropped; WorkGiver_HoseOrders.cs:53 says 'waiting for a new order' forever. Non-default setting (default true, RM_HoseSettings.cs:58).
- **C7b-F3** CONFIRMED LOW — Float-menu move of a reachable loose end is blocked when the REEL is unreachable. Jobs/FloatMenuOptionProvider_Hose.cs:61 Blocked() requires CanReach(reel) before EndBlocked; WorkGiver_HoseOrders' laid branch checks the end instead.
- **C7b-F4** PLAUSIBLE LOW — Hose order validates the destination with Touch, the driver walks OnCell. WorkGiver_HoseOrders.cs:78 Touch vs JobDriver_CarryHoseEnd.cs:123 OnCell for standable cells; a pit-lip cell reachable by touch only would pick up then drop. Live: destination on a sealed pit floor next to the surface.
- **C7b-F5** PLAUSIBLE LOW — A failed forced job submission leaves the new pending order queued for any colonist. FloatMenuOptionProvider_Hose.cs:94 ignores GiveForced's bool. Offline: inject TryTakeOrderedJob=false, check pending restored.
- **C7b-F6** CONFIRMED LOW — Interrupting a wind removes whole trailing cells (winds in more than was wound). HoseCarry.cs:124 ShortenBy deletes cells until length <= target.
- **C7b-F8** CONFIRMED LOW — Coupling to a tank/pipe/machine takes the plain 30-tick set-down, not the 90-tick coupling. Jobs/JobDriver_CarryHoseEnd.cs:130-131 counts only reel relays as couplings.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
