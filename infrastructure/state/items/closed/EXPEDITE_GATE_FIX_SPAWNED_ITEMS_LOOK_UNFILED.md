# EXPEDITE_GATE_FIX_SPAWNED_ITEMS_LOOK_UNFILED

## Spec
relentless.py ledger_has (line ~2557) tests e.get("id") == item; a `spawn` event stores the item under "name", so `expedite set` and `enrol` refuse every spawned item as "never been filed". Seen 2026-11-04T03:2xZ on STEVEN_LINK_ENFORCE_TWENTY_ENDS_AT_RESET (spawned, published a9f81c19f9).

## Verify
A selftest: a ledger holding only a spawn event for X makes ledger_has(X) true; `expedite set` on a spawned item succeeds.
