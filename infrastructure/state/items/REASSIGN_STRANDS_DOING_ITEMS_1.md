## spec
🔴 **THE OWNER ORDERED THIS FIXED — 2026-08-21 12:54, shown the bug in a report:
*"Capture that reassign bug and pass it to BUILD to fix! That's horrible!"*** It is not a
nice-to-have and it is not DECIDE's opinion of the tooling.

⚠️ **It is unrowed, so `rimflow` will sort it LAST behind ~11 waiting items.** That is not a
judgement about its importance — rimflow's only priority lever is the V1 milestone row, and a
tooling fix has no honest V1 row. **Take it early anyway; the owner said so.**

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

## 🔎 blast radius — MEASURED, and it is good news

Replayed all of `infrastructure/state/ledger/events.jsonl`, 2026-08-21:

- **38 `reassign` events in the ledger's whole history.**
- **Exactly ONE was on a `doing` item — mine, today.** Every other one fired on `proposed`
  (34) or `ready` (3), where `reassign`'s failure to touch `state` is harmless.
- **Nothing is stranded right now.** All 8 currently-`doing` items are owned by the seat that
  started them.

⇒ **This is a latent defect caught before it bit anyone, not a live outage.** Fix it properly
rather than urgently — but do fix it, because the next person to reassign mid-flight has no
way to notice.

## 🔴 the pattern this is the THIRD instance of, in ONE day

| when | item | how work became invisible |
|---|---|---|
| 07:32 | `COMMIT_GUARD_BLOCKS_SPECS_1` (done) | the ownership guard refused the filing seat its own spec prose |
| 09:59 | `FILED_WORK_NEVER_OFFERED_1` (done) | 15 of BUILD's 21 items sat in `proposed`, which `next` never offers |
| 12:50 | **this item** | `reassign` leaves `doing`, which `next` never offers |

🔑 **The root cause is structural, and all three were patched at the symptom.**
`rimflow next` is the **only** discovery channel a seat has — agents cannot message each
other (owner, 2026-08-19) — and it filters hard on `state == "ready"` **and** `owner == seat`.
⇒ **Any transition that parks an item outside that intersection makes it permanently
undiscoverable, silently, with no report to anyone.** There will be a fourth instance.

⭐ **So the fix worth building is the invariant, not the fourth patch:** something that
enumerates every OPEN item (`proposed` · `ready` · `doing` · `blocked`) and asserts each one is
reachable by *some* seat through a route that seat is actually told to run — and names the
unreachable ones. `rimflow sweep` or `admin` is the natural home. **Ship that alongside
whichever of (a)/(b) below you choose**, or this recurs.

⚠️ And note the one shape the invariant must NOT flag: the nine items parked `doing` by the
10:54 work stop are *deliberately* unoffered. Unreachable-by-design and unreachable-by-accident
have to be distinguishable, or the check gets muted.
