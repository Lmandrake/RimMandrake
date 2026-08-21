## spec
**Measured 2026-08-21 on `DROID_KINDS_NEED_A_RACE_1`.**

`rimflow reassign` sets `item.owner` and nothing else — `model.py:653`, a bare
`item.owner = ev["to"]` with no `to(...)` call. So reassigning an item that is **`doing`**
leaves it `doing` **under the new owner**, and `priority.rank()` filters `state != "ready"`
(`priority.py:82` and `:115`). ⇒ **The receiving seat is never offered the item and cannot
discover it** short of running `rimflow show` on an ID nobody told them — and agents do not
message each other, so nobody will.

I worked around it by re-running `claim --seat BUILD`, which routes through
`to("ready" if _complete(item) else "proposed")` at `model.py:619`. ⛔ **That workaround is
worse than the bug** — it writes a `claim` event under a seat that did not act, so the
ledger now records BUILD claiming something DECIDE claimed for it. Do not adopt it.

**Pick one real fix:**
- **(a)** `reassign` re-runs `claim`'s completeness test and sets `ready`/`proposed`
  accordingly, or
- **(b)** `reassign` refuses on a `doing` item and names the supported route in the refusal.

⛔ **Do NOT make `next` surface `doing` items generally.** The 2026-08-21 10:54 work stop
parked nine items as `doing` precisely because `next` does not re-offer them; that behaviour
is load-bearing and must not be traded away to fix this.

## verify
`python3 src/RimMandrake/rimflow/selftest_model.py` passes with a new case: an item taken to
`doing`, then `reassign`ed to another seat, is afterwards either `ready` for that seat
(fix a) or the `reassign` raised `TransitionError` (fix b). Under fix (a),
`priority.next_item(w, <new seat>)` returns the item.

## criteria
Offline only; no game needed. After the fix, `rimflow reassign` on a `doing` item leaves the
receiving seat able to find it with `rimflow next` alone.

## notes
Filed by DECIDE, 2026-08-21, from a live hit rather than a code read. Scope is the tool, not
the ruling that exposed it — `DROID_KINDS_NEED_A_RACE_1` is correctly `ready` for BUILD now
and is not blocked on this.
