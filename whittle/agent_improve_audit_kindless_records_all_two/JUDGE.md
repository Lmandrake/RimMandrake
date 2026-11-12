# Judge: AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO

Judged 2026-11-11 by a fresh judge (CLAUDE_ARCHMAGI_OFFLINE1 clone, HEAD dc397d440e). I did not read DONE.md, BROADEN.md or the earlier JUDGE.md.
What I read: STATEMENT.md, NOTES.md, every evidence/*.out, the net diff 7b44484903^..HEAD of agent_improve.py, lessons.py and design §4.3, the
selftest_agent_improve_steps kindless checks, and `rimflow show`. What I ran myself: the five selftests (GREEN 5/5) and
`measure_kindless.py` with no argument (exit 0). Sections 1-3 of its output match evidence/measure_kindless.out line for line.

## Line 1: a change applied below L2 records source kinds, or design 4.3 records and explains the decision to leave it uncheckable; doc and code agree. TRUE

- Route (b) is taken. §4.3 has a dated paragraph (2026-11-11, naming the item) that says in bold that an L0/L1 change whose
  cited pieces name no item is applied with `source_kinds: []` and stays uncheckable by design. It gives the reason: a
  guessed kind would make a held-out sample that is not held out, and refusing the change would be a new gate that pulls
  down the ramp's acceptance rate. It also names the two other sources it tried and how each failed: the seat touched 8
  and 41 items within an hour, and the commits that added the lessons name no item.
- The builder also did part of (a). `piece()` now carries `task_kind`, taken from the lesson's `item:` footer when it
  has one, else from the first item named anywhere in the whole text. Relentless alarms take the item from `item` or
  `clones/<item>`. `lessons.py add --item` writes the footer, falling back to RIMFLOW_ITEM and then WC_ITEM.
  `verdict_record` cites each piece's task_kind, and `source_kinds()` reads it.
- Doc and code agree. I checked every source the paragraph names against `collect()`. Reject, learned, ops-alarm and
  owner pieces put their own item first in the text, so the first item named is their own. A lesson footer saying
  `item: NONE` gives no kind, matching `kind_of_text("NONE")`. The selftests show L0 (`foo_v4`) and L1 (`foo_v5`) both
  apply a kindless change and record `source_kinds == []`, which is what the doc says.
- The tests do bite. evidence/selftests_old_code.out shows the new checks failing on the pre-change code (66ab8395fd):
  2 in selftest_agent_improve, 4 in _steps, and lessons crashing. All of them pass on HEAD (my run).

## Line 2: the share of kindless change records is measured from changes/, with a sanity probe, and stated on the item and in 4.3. TRUE

- My run: `KINDLESS 2 of 2 records` (rimworld-modding_v1, using-rimflow_v1). The sanity probe, the same reader on a
  copy with `['REPAIR']`, reads `kinded=True`, so the reader can see a non-empty list.
- The figure is stated on the item. `rimflow show` has the note of 2026-11-12T04:41:56Z: "2 of 2 change records on file
  have source_kinds [] ... Sanity probe ...". It is also stated in §4.3 ("Measured 2026-11-11: 2 of 2 ...").
- Every other figure in §4.3 matches the evidence. 159 (7%) and 582 (24%) of 2396 lessons name a kind; the
  corroboration rates are 27% and 49% within ±3 h (attribution_audit.out); the inbox has 8 of 110 lessons naming an
  item, 2 by first line and 1 by footer.

## Staging / flattery check

- Nothing looks staged. The population really is 2 records, and the doc says so plainly ("2 of 2 is no rate"). The
  evidence works against the builder's own fallback: the attribution sample of 8 is mostly "no", and the doc calls the
  whole-text reading "a proxy, not provenance".
- Section 4 of the measurement (ordinary use, old vs new code) comes from the builder's own run; I skipped it as briefed
  (no argument). It shows no change in what is signalled, so it does not flatter either.
- One weak spot that does not falsify either line. For a reject, learned or owner piece whose own id has no intent word,
  `kind_of_text` keeps scanning and takes a later item from the text. §4.3's "Otherwise it is the first item named
  anywhere" covers this, but only lessons get the "never second-guessed" guard.
- Practical effect: §4.3 itself predicts that most skill changes stay unmeasured until lessons carry `item:`. That is
  exactly the decision line 1 allows, written down.

would show: yes
