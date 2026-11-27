# BOUNDARY: the dead-man sweep files one ticket per fault, Design Version 0.1.0

Code: `src/RimMandrake/Utils/deadman_check.py`, the part that turns one pass's broken promises into filings:
`cause_key`, `cause_id`, `arm_id`, `host_id`, `hosts_of` (with `shared_hosts`, which it calls) and the filing loop of `sweep`. Item:
`RIMMANDRAKE_KEY_AUTO_FILERS_ONE_FAULT_ONE_TICKET` (owner by card 2026-11-19, "One fault, one ticket"), written
2026-11-19. The census of every program that files tickets on its own, and why this is the one changed:
`census.md` beside this page. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_deadman_check.py`. Each test except `a-lone-fault-keeps-its-own-ticket` (a must-stay-green
guard) was seen red on the code before this item. Seven planted faults in the code each turn at least one test red.

Why: on 2026-11-08 one moved settings path made 23 hooks read "hook X is not wired in <settings>", and the sweep filed 23
LIVE_RESTORE_* tickets in 30 minutes. One timer stopped under 45 fixes reopened 45 items
(RIMMANDRAKE_CHARGE_SHARED_OUTAGE_ONCE_FORTY_FIVE_DEATHS).

## ACCEPTS (the only inputs the filing is built for)

- **one-pass-of-rows.** The rows of one sweep pass: `{"item", "line", "why"}`, where `line` is a `live_line` promise
  (`unit=` / `hook=` / `role=` subject) or None (an arm), and `why` is the checker's reason, or None when the promise is kept.
- **the-ledger-items.** `items`, the ledger's replayed items. They are read for state (retired or not), `live_broken` and
  `live_repeats`.

## DOES NOT SURVIVE (not promised)

- **two-faults-that-read-alike.** Two independent faults whose reasons are the same once each subject's own name and
  every digit are masked are filed as one cause ticket. The merge is bounded: the ticket names every member. When the
  group falls to one member, that member files its own ticket and the cause ticket is put back.
- **a-reason-that-names-another-subject.** Only the row's own subject name is masked. A reason that names a different
  unit (or a path with a changing name) makes a different key, so that one fault can still file two tickets.
- **a-same-subject-host-off-the-baseline.** A same-subject host (`shared_hosts`) that is not itself a baseline promise
  and was filed before this item has no marker, so it is not put back when its outage ends.
- **phone-pushes.** `phone()` still pushes once per phone-worthy broken row, not once per cause. Its route is off
  (Todoist retired, 2026-11-19).

## PROMISES (each one is owed a test of the same name)

- **one-cause-files-one-ticket.** Two or more promises with different subjects that break in one pass for one reason
  (same `cause_key`) file one ticket, `LIVE_RESTORE_CAUSE_<8 hex>`. Its reading names every member's item.
- **a-repeat-reopens-the-same-ticket.** The same cause in a later pass, with its members in any order, reopens that same
  id. It does not spawn. While the ticket is still broken, the cause files nothing more.
- **two-causes-stay-two-tickets.** Different reasons make different keys and different tickets. A hook and a timer with
  the same words are two kinds, so they make two tickets.
- **a-lone-fault-keeps-its-own-ticket.** A promise broken for a reason that no other promise in the pass shares files
  under its own id (`item_id` or its ledger item), as before this item.
- **members-file-no-ticket-of-their-own.** A member of a shared outage spawns, reopens and raises nothing of its own.
  This covers one subject under many fixes, and one cause across subjects. Only the host is filed.
- **the-cause-ticket-is-put-back-when-the-cause-clears.** A broken host (its reading starts `shared outage of `) that
  holds no member this pass is read `kept`. When one member is left broken, that member files its own ticket in the
  same pass.
- **a-retired-cause-ticket-gets-a-successor.** A dropped or superseded cause ticket is never reopened. The key's next
  generation id is filed, and is that cause's ticket from then on.
- **no-filing-lands-on-a-retired-item.** No reading of a pass is filed onto a dropped or superseded item, by any road:
  an arm, a baseline line, a ledger promise, a cause host or a same-subject host. An arm whose fixed id
  `LIVE_RESTORE_<ARM>` is retired files the arm's next generation id (`arm_id`), spawned once, and that id is the arm's
  ticket from then on. A same-subject host whose fixed id is retired gives way to its next generation (`host_id`) the
  same way (`LIVE_RESTORE_RM_OPS_WATCH`, dropped while 30 swept promises named its timer, 2026-11-27). Why: the ledger
  refuses a write onto a retired item, the refusal made `rm-deadman.service` exit 1, and TIMER_FAILED rang for a sweep
  that worked (`LIVE_RESTORE_UNITS` and `LIVE_RESTORE_OPS_WATCH`, 2026-11-25 and 2026-11-26; OPS_TIMER_REPAIR_PRXC_XKGA).
- **cause-ids-are-item-names.** A cause id passes `model.mint_problems`, so `rimflow spawn` takes it.
