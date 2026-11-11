# Scope reconciliation

The original finding FE_cs_selftests_2.4 records a vacuous rejection of the retired counter-only callback. Its explanation says the guard must catch that callback after RiverSwitchFlipChecks.Src collapses whitespace. The assertion message says “the callback is no longer only a counter”.

History supplies the behavior. Commit 1e681b935e used `private static void OnSpansChanged(Map map) => SpansChangedCount++;`. Commit 5f54729885 added the block callback, per-map signatures, Changed, NetBumps and RM_LiquidNet.Bump(map), together with these production-math and wiring checks. The current callback retains those operations. RM_PipeSpanNetMath.Changed admits the first observed set and changed sets, and refuses repeated equal signatures. The net revision must follow a real span-set change.

The 2026-10-29 ledger note says “fails when the callback body gains a statement”. That agent-drafted done-condition reverses the original guard and the shipped phase-5 contract. The attached owner quote asks for assessment of ancient items and routing of owner-needed work. It supplies no instruction to reject the working callback or remove net invalidation. The frozen statement and current worker instruction explicitly require rejection of the retired callback and acceptance of the working callback.

The repair therefore rejects the retired counter-only body through the same whitespace collapse used by Src, keeps acceptance of the working callback, and preserves the production net-bump, listener registration and join-order checks. This file records the reconciliation for the parent’s ledger note. The worker performs no ledger mutation. The evidence is an offline test-instrument repair. Live pipe-span acceptance remains outside this item.

The raw item, including the complete triage text and owner quote, is saved in item.txt. The relevant source history is saved in history.txt.
