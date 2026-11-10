# Harness repair requested

2026-11-10: read-only parse of live ModsConfig.xml finds:
`brrainz.harmony, ludeon.rimworld, ludeon.rimworld.royalty, ludeon.rimworld.ideology, ludeon.rimworld.biotech, ludeon.rimworld.anomaly, ludeon.rimworld.odyssey, brrainz.rimbridgeserver, ray1203.simplecamerasetting, mandrake.rm.gimmesomeslack, mandrake.rm.patches`.

FlowWorks is absent, game DOWN, bridge FREE. User forbids this worker touching ModsConfig.xml. Observer repair needed to place the harness on a FlowWorks-capable list; do not change implementation or proofs. Worker continues offline.

## Preflight harness failures (second request)

`preflight_bridge.py --tier quicktest --modset flowworks` now passes list membership/order. `whittle/evidence/preflight-ready.log` reports O09 missing this clone's ignored companion artifact; O12 flags pre-existing test-only FakeEngine/Oracle and FlowWorks Replay/{ReplayTick,Compat,Trace}. Shipping C# build succeeds zero warnings/errors. These files are unchanged by this worker. Required preflight isn't GREEN, so worker has not launched. Please repair harness provenance/false positives without weakening bars; worker continues scoped proof authoring. First text-only broaden inherited armed Whittle hook and wrote STALLED; observer diagnosed this, retry with WHITTLE=0 succeeded. Both raw answers retained.

## Preflight dependency baseline

FlowWorks deployed via inspected plan; `deploy-apply.log` VERIFIED in sync. Normal deep preflight passed O09/O12 and required checks so far but O10 dependency_fp FAIL: changed `0Harmony.dll` vs recorded baseline (`whittle/evidence/preflight-after.log`). Not comparable to the old run, not a prison implementation finding. Worker released bridge on this preflight error and has not launched; observer please resolve baseline provenance through the supported process (do not suppress the check). Other deep checks may still be running.

Preflight completed NO-GO O10,O13: O14 passes; O13 only GimmeSomeSlack DLL + .srchash differ in deployment. FlowWorks is in sync. This is a test-list dependency drift, not worker implementation. Full log `whittle/evidence/preflight-after.log` and JSON preserved. Worker has released bridge, asks observer to settle that harness dependency along with Harmony baseline.

Bridge release harness warning: CLI released ledger to FREE but says host driver lock belongs to BENCH pid 1755864 (this Codex runner's live parent), not the short-lived release process; it explicitly says another take will refuse while parent lives. Worker did not force a hold. Inspect `whittle/evidence/bridge-release-warning.txt` if needed. This is an ownership-identity mismatch in the runner/CLI release, not an active game driver (game remains down).

Driver release resolved by worker using documented RM_DRIVER_PID override from driver_lock.owner_pid(): actual live Codex parent is 1755864 (`ps` read), so `RM_DRIVER_PID=1755864 ... bridge release` releases its OWN hold without force. Subsequent who: driver lock FREE, bridge FREE. `bridge-release-warning.txt` now contains the successful retry; earlier warning is in the runner transcript. Future takes/releases will name this same actual parent.
