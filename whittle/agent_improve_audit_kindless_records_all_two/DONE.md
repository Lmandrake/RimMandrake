<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

- true: **A change applied below L2 either records source kinds, or the decision to let it stay uncheckable is written in | evidence: `whittle/agent_improve_audit_kindless_records_all_two/evidence/selftests_new_code.out` `whittle/agent_improve_audit_kindless_records_all_two/evidence/selftests_old_code.out` `whittle/agent_improve_audit_kindless_records_all_two/evidence/ordinary_use_lesson.out` `whittle/agent_improve_audit_kindless_records_all_two/evidence/attribution_audit.out`
- true: **The share of change records with no source kinds is measured from `infrastructure/state/agent_improve/changes/` and | evidence: `whittle/agent_improve_audit_kindless_records_all_two/evidence/measure_kindless.out` `whittle/agent_improve_audit_kindless_records_all_two/evidence/measure_kindless.py`

Every evidence file was re-run 2026-11-11 21:19-21:24 PST at HEAD 2452d42756 (after the last pull); the figures are
unchanged. `measure_kindless.py` is unchanged since it was committed (only re-run). The item's 04:41Z note described an
older probe; a correcting note (2026-11-12T05:18:29Z) now states the apply_change probe.

## How each is true
Bullet 1 is true both ways: (a) and (b), and they agree.
(a) `apply_change` at L0 and L1 now records the kind a lesson names past its 200-character first line, and a
lesson's `item:` footer kind over an item its text names. The footer is written by `lessons.py add` from `--item`,
else `RIMFLOW_ITEM`/`WC_ITEM`. A Relentless row, ops alarm and owner note's own item decides its kind (never a later id in the text). The steps selftests "L0/L1 records the kind
a lesson names past its first line" and "a lesson's item: line is its kind" pass on the new code and fail on 66ab8395fd.
(b) The 2026-11-11 paragraph in §4.3 of `design/RimMandrake/daily_agent_improvement_2026-11-02.md` says a change at L0
or L1 whose cited pieces still name no item applies and stays uncheckable by design, and why: no sound source
remains, since seat-at-time and the adding commit were measured and both fail; refusing would be a new gate; and it
would drag down the ramp's acceptance rate. The code agrees: the selftest "L0 applies a change from a lesson naming no
item, recorded kindless" and "L1 applies it too, recorded kindless" pass. The cadence still shows such a record `unmeasured` (selftest_agent_improve_cadence,
unchanged and green), and only the L2 gate refuses one.
Bullet 2: 2 of 2 records have `source_kinds == []`. The sanity probe: the production apply_change, run in a temp repo on a real footered lesson, writes
`['AUDIT']` and the same reader counts it kinded (0 of 1), so the reader can see a non-empty list. The share is stated on the item (`rimflow note`, ledger shard CLAUDE_ARCHMAGI_OFFLINE1) and in §4.3.

## What I'm least sure about
- The whole-text fallback is a proxy. Its first-named item is corroborated by the seat's own ledger for only 49% (27%
  for the old first-line rule), so a non-empty kind from prose can be wrong, and a wrong kind would let a source-kind
  item into the "held-out" sample. Only the `item:` footer is sound. The doc says so with the numbers.
- 2 records is the whole population, so the share is 100% of a tiny sample. In the live inbox (20:59 PST) only 8 of 114
  lessons name an item in their text; 5 already carry an `item:` footer from Whittle rounds that pulled this code. Most skill changes stay unmeasured until lessons carry footers. Most of today's lessons
  come from Whittle loops, which now stamp one.

## What I did not test
- A real agent-improvement pass applying a change (`run --apply`) on live data: none was due, and the live state under
  D:\ClaudeWork\rimmandrake\agent_improve\ is off limits. Apply is shown only in temp-repo selftests.
- Lessons filed on SteveDesktop clones until they pull this code (their lessons today have no footer).
- A launcher that exports a stale `RIMFLOW_ITEM`: none exists today (checked by reading, not run).
- `code_review_status.py mark-clean` was not run on the changed files; they stay DIRTY until a review.
