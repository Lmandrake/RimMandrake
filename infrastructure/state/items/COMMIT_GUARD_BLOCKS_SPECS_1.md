## spec
🔴 **Found the hard way, 2026-08-21: DECIDE can no longer commit any item she specs.**

`.claude/hooks/queue_lint.py:305-332` refuses a commit whose pathspec contains
`infrastructure/state/items/<ID>.md` for any `<ID>` the ledger says another seat owns. That
guard is right about its purpose and wrong about this case:

- `DECIDE.md` — *"Turn a v1 bullet into an item BUILD can execute without asking you
  anything… `spec:` `verify:` `criteria:`… Writing `verify:` is your work, not BUILD's."*
- `rimflow file --for BUILD …` itself answers
  *"items/<ID>.md still needs ## spec and ## verify and ## criteria before it can reach
  `ready`."*
- ⇒ the prose MUST be written by the filer, MUST live in `items/<ID>.md`, and **cannot be
  committed by the filer.** The item sits `proposed` forever or the file rots untracked.

**It is new.** Three BUILD items filed earlier the same session committed cleanly; the
guard tightened in `cf787f3` / `70607b8` between those commits and this one.

**The workaround used, so nobody thinks it was sanctioned:** `rimflow reassign` to DECIDE,
commit, reassign back. It works only because DECIDE is the one seat that may reassign — ⛔
**no other seat can file a specced item at all right now.**

**THE FIX — permit the filer to write prose while the item is still untouched by its
owner.** The narrow condition, which keeps every case the guard exists for:

> allow if the item's state is `proposed` **and** the committing seat is the seat that
> filed it **and** the owner has never claimed or started it.

⛔ Do not widen it to "any `proposed` item" — a seat could then rewrite a spec filed for it
by someone else, which is the thing the guard is for.

⚠️ Add the case to `.claude/hooks/selftest_queue_lint.py`; it has cases for DENY on
another seat's item and none for ALLOW on your own filing.

## verify
`selftest_queue_lint.py` gains a passing ALLOW case: seat DECIDE, item owned by BUILD,
state `proposed`, filed by DECIDE ⇒ permitted. The existing DENY cases still pass —
especially "another seat's item when it IS in the pathspec" for an item in `doing`.

## criteria
`rimflow file --for BUILD …` followed by writing `items/<ID>.md` and committing it
succeeds, with no reassign.

## notes
Raised to the owner in DECIDE's reply, 2026-08-21, because it silently disables the seat's
output rather than failing loudly at the point of authorship.
