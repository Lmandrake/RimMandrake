## Problem
`incident.step` auto-acks an unacked incident when `item_acted(events, items, inc["told_at"])` finds a seat action on a named item. `since` is always `told_at`, so after a revisit clears the ack, the next step finds the same old event and re-acks at once, with a fresh `recover_by` and a plan that is only that event.

Seen 2026-11-03 21:15:27Z (`told.jsonl`): disk-20261101160557 got plan "drop on OPS_SCRATCH_DIRT_MEASURE_AT_END_RVNI" (that drop was 2026-11-01 17:49Z, a planted-test item), and testing-20261101162433 got "start on OPS_NIGHTLY_RED_DIAGNOSE_LNTM" (that start was 2026-11-01 21:05Z, and the item has since closed). Both read as a live owner and a live plan; neither is.

Related: both alarms still name an item that is dropped or closed, so the news keeps attaching to them.

## Fix
In `step`, read item actions since the latest of told_at, the last revisit and the last ack clearing, not since told_at. Add a case to `selftest_incident.py`: a revisit with only old events stays unacked and is rung. Coordinate with `INCIDENT_REVISIT_TAME_SAME_NEWS_HOURLY`, which changes the same path.

## Done when
A revisited incident with no new item event stays unacked until a reader acks it. Close with `--live "once: pure step logic, pinned by selftest_incident.py"`.
