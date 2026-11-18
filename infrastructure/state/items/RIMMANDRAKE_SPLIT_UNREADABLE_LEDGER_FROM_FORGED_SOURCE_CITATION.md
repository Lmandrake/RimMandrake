## spec

Found by the builder of `RIMMANDRAKE_CHECK_SCOPE_SOURCE_EVENT_EXISTS_FAKE_ID_OPENS` (landed 895f0834c356) while
fixing the sibling check, and **left alone correctly** — it is a different function, and widening that ticket would
have broken its minimal-diff rule. Filed here instead, with a reproduction.

`designer_stage.py` `source_errors` (line ~347):

```python
elif s.startswith("OWNER:") and owner_ev is not None and s[6:] not in owner_ev:
    errs.append("%s: %s finds no event in OWNER.jsonl" % (where, s))
```

The `is not None` guard was meant to mean "only judge a citation when we actually have a reading". But production
passes `CT.owner_events(...)` (`concept_tree.py:564`), which returns a plain `{}` when the shard could not be read
— **not** `None`. So `{}` passes the guard, every tsn is "not in" it, and **every real OWNER citation is reported
as `finds no event in OWNER.jsonl`**: a true event of his, called a forgery, in the same words a genuine forgery
gets.

**Reproduced by a direct probe (Conductor, 2026-11-17), not inferred:**

| `owner_ev` | what `source_errors` says |
|---|---|
| `{}` — an UNREADABLE shard, as production supplies it | `w: OWNER:1794793804486811354 finds no event in OWNER.jsonl` |
| `None` — never read at all | `[]` (no error) |
| a real reading without that tsn — a genuine forgery | `w: OWNER:999999 finds no event in OWNER.jsonl` |

Rows 1 and 3 are byte-identical in meaning to any reader, and row 2 is the opposite behaviour for an almost
identical cause. That is the owner's 2026-11-17 rule broken twice over: *"could not look"* collapsed into
*"failed"* (row 1), and two causes sharing one code (rows 1 and 3) — and it is the **false-forgery** direction,
which is worse than the permissive one, because it accuses his own record.

**The fix.** The same shape the sibling check landed with: key the unreadable case on **falsiness**, not on
`is None`, and give it its own message — the citation stays unjudged, is NOT called forged, and the text says
UNMEASURED and why. Keep four answers apart: the event is present; the event is absent from a ledger that **was**
read (a real forgery, keep today's message); the ledger could not be read (UNMEASURED, judge nothing); and no
citation was given at all (the existing "no source" error).

🔴 Do not make this permissive in the other direction either: an unreadable ledger must not let a forged citation
through as if verified. `source_errors` is a *reporting* function, so the right answer here is to report UNMEASURED
and let the caller refuse — check what each of the three call sites (lines ~476, ~485, ~893) does with the returned
errors before choosing, and say in the commit message which callers now see UNMEASURED and what they do with it.

Note for whoever takes it: the landed sibling fix in `inventory_errors` is the worked example to copy, including
its comment explaining why falsiness and not `is None`. Its evidence is
`Transient/scope_source_acceptance.txt`.

## refs

file: src/RimMandrake/rimflow/designer_stage.py
file: src/RimMandrake/rimflow/concept_tree.py
file: src/RimMandrake/rimflow/selftest_designer_stage.py

## verify

python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_stage selftest_designer_repin selftest_designer_stage_land

## criteria

- A1: with `owner_ev == {}` (an unreadable shard), a real OWNER citation is NOT reported as `finds no event`; the
  message says UNMEASURED and names the unreadable ledger.
- A2: with a real reading that lacks the tsn, the forgery is still reported exactly as today.
- A3: `owner_ev is None` and `owner_ev == {}` behave the same way (both "could not look"), rather than opposite ways
  as they do now.
- A4: an unreadable ledger never lets a citation through as verified: the caller refuses or holds, and the commit
  message says which of the three call sites does what.

## acceptance

Acceptance test: four cases in `selftest_designer_stage.py` beside the ones the sibling ticket added, calling
`source_errors` directly with `{}`, `None`, a real reading lacking the tsn, and a real reading holding it —
asserting the UNMEASURED message contains "UNMEASURED" and does NOT contain "finds no event", and that the forgery
case still does. Watched FAILING on the base commit; the base reading to quote is the probe table in this spec
(`{}` → `finds no event`, `None` → `[]`), reproducible with:
`python3 -c "import sys; sys.path.insert(0,'src/RimMandrake/rimflow'); import designer_stage as DS; print(DS.source_errors('OWNER:1794793804486811354','w','.',{}))"`
