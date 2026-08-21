## spec
✅ **Done in this item; recorded so the reasoning survives.**

REP fixed `FILED_WORK_NEVER_OFFERED_1` by adding `_claimable()` to `cli.py` — an empty
answer now says *"claim one"* instead of *"nothing"*. That was right and it left the worse
half open: **`_claimable` fires only when NOTHING is claimed**, so a seat holding any
`ready` item never learns that finished specs are waiting.

**Measured 2026-08-21, after REP's fix landed:**

| seat | offered | spec-complete but MASKED behind them |
|---|---|---|
| BUILD | 2 | **15** |
| CHECK | 31 | **15** |
| DECIDE | 0 | 1 |

⇒ **30 finished specs unreachable fleet-wide.**

🔴 **And for BUILD it was permanent, not slow.** Its top `ready` item was `B-V2` — *"Park any
v2 idea in V2_DREAMS.md yourself"* — a **standing right with no completion condition.** BUILD
could never finish it, so its queue could never empty, so `_claimable` could never fire. The
fifteen were not delayed; they were unreachable.

**Two changes, both shipped:**
1. `cli.py` — after printing the claimed item, `next` now names the claimables in one line:
   `⚠️ 15 spec-complete items ALSO waiting for BUILD to claim: … `rimflow claim <ID>``
   ⛔ Deliberately does **not** touch `priority.rank()`. `ready` still means claimed, the
   claim is still an explicit act, and the rendered NEXT section still shows only claimed
   work.
2. `B-V2` and `C-V2` **dropped**. ⚠️ Their doctrine was moved into `design/V2_DREAMS.md`'s
   header FIRST — because their own `verify` said *"read the header of V2_DREAMS.md; it says
   the same thing"* and **it did not**. Dropping them without that would have deleted a
   standing right.

🔑 **The general lesson, and it is worth more than the fix:** a queue item with no completion
condition is not a reminder, it is a **permanent occupation of the top of a board**. Doctrine
goes in a doc; a queue holds work that can end.

## verify
- `rimflow next --seat BUILD` names the masked claimables ✅ (15, as of 2026-08-21)
- `selftest_cli.py` 24/24 ✅
- `render.py` unchanged in behaviour ✅
- `V2_DREAMS.md`'s header now carries the append-yourself right ✅

## criteria
No spec-complete item is unreachable because another item cannot be finished.
