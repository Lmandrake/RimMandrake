## spec
DESIGN DECISION 2026-11-18 (on RIMMANDRAKE_DECIDE_GUARDS_OWED_BY_LANDED_OLD_FIXES): rimflow's guard rule stays (a fix that died closes only with a class guard), and what counts as a death changes. One stop of one shared timer was read as the death of every fix whose promise names that timer: 45 `live broken` readings between 02:00Z and 06:00Z on 2026-11-07, 7 items in the single 17:33Z sweep on 2026-11-01 [measured over the 69 items' deadman events]. Each of those fixes then owed its own class guard for an outage it did not cause.
- `deadman_check.shared_hosts(rows)` (pure): rows are a pass's broken rows (`{"item", "line", "why"}`, before the `MAX_PER_PASS` cut). Two or more items broken on the same subject (`unit=`/`hook=`/`role=`) with the same reason, digits aside, are one outage; each maps to the subject's fixed host `item_id(line)`. The host never maps to itself.
- `sweep` writes that host on each such `live broken` reading as `sharedWith` (the `live` verb's schema takes it), and files the host broken too when no row already does (the existing `spawn` road).
- `model._apply_live`: a `broken` whose `sharedWith` names another item the ledger holds counts in `live_repeats` and reopens the item, but is not a death. `sharedWith` naming the item itself, an unknown item, or anything that is not an item id excuses nothing.
- No old event is rewritten. The 59 old fixes this decision closes were closed by the Conductor's authority, each with its outage named.

## refs
file: src/RimMandrake/Utils/deadman_check.py
file: src/RimMandrake/rimflow/model.py

## criteria
- The acceptance test passes 25 of 25; selftest_deadman*.py and the model's selftests stay green; replaying the real ledger gives every item the same `deaths` before and after (no real event carries `sharedWith` yet).
- Operational: closes with `--live "unit=rm-deadman.timer max_age=2h"`.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/shared_outage_one_death_accept.py` (25 checks; on 3e560d2656, watched: 15 red, 10 green). Covers, for the model: an outage alone, a shared outage, the host's death, `kept` after a shared outage, a later own outage, `sharedWith` naming itself, an unknown item, empty, None, a number, a list; for the deadman: two items, the host's own row, one item with the host, one item alone, no rows, a different reason, reasons differing only in digits, different units, kept rows and rows with no line, a hook, a role.
