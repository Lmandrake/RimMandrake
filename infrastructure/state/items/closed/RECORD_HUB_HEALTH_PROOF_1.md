# RECORD_HUB_HEALTH_PROOF_1 — record the codebase-health hub proof on DASHBOARD_HUB_ARTIFACT_1

Filed for BENCH (item owner) by FOUNDRY, caused by `DASHBOARD_HUB_ARTIFACT_1`.
`HUB_TAB_PUBLISHER_MIGRATION_1` (FOUNDRY) says explicitly "Record the proof on
DASHBOARD_HUB_ARTIFACT_1" — the write is blocked at the hook because that item
belongs to BENCH, so the proof is handed over here instead of being lost.

## spec
Append the following as a new dated section on
`infrastructure/state/items/DASHBOARD_HUB_ARTIFACT_1.md` (verbatim content
below; BENCH may retitle/reformat, but land the facts):

---

## Two-seat no-clobber proof — codebase-health publisher, 2026-09-11 (FOUNDRY)
`HUB_TAB_PUBLISHER_MIGRATION_1`'s codebase-health leg is done: republished
ONLY `data/health.json` (Version 6) against the live hub URL, passing no
other file in `files`.

Fingerprint evidence: `infrastructure/dashboards/hub/data/health.json` now
carries `source.sha256_12: db8a05d6a520` for `Transient/codebase_health.json`
(489768 bytes, HEAD `feec8c4fa`), `generatedAt: 2026-09-11T18:33:00Z`.
`python3 infrastructure/dashboards/hub/hub_check.py` reports
`health GREEN 7.0 h source ok` — the recorded fingerprint matches the file on
disk.

No-clobber: re-fetched the live artifact (`Artifact action:"read"`) both
before and after this publish — `art`, `maturity`, `worldmap` and the
`sheets` links section are byte-identical across the two reads; only
`data/health.json` changed. In the same `hub_check.py` run, `art` independently
reports STALE (that lamp belongs to the art publisher, unrelated to this
change) — further evidence this republish touched nothing outside its own
tab.

This, together with BENCH's original build/publish, satisfies the "two
different seats republish without clobbering" verify line on
`DASHBOARD_HUB_ARTIFACT_1`.

Publisher migration is 1/3 done: the codebase-health hook
(`src/RimMandrake/Utils/codebase_health_publish.py`) now regenerates
`infrastructure/dashboards/hub/data/health.json` automatically as part of
its own `build()` (calling `make_tab_data.py health`) — no more manual step.
`artpipe` and `maturity` publishers still need the same treatment; see
`HUB_TAB_PUBLISHER_MIGRATION_1`.

---

## verify
`infrastructure/state/items/DASHBOARD_HUB_ARTIFACT_1.md` contains the section
above (or BENCH's equivalent capturing the same facts: version 6, the
health.json fingerprint, and the no-clobber confirmation).

## criteria
Proof lands in the item BENCH owns; this item closes once it does.
