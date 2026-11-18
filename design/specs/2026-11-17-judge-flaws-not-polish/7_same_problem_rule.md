# When is a second-look finding the same problem as a first-look one?

Item `RIMMANDRAKE_DESIGN_JUDGE_SAME_PROBLEM_MATCH_FOUR_ROUNDS_LOST`, 2026-11-18. **Settled** after one Codex critique
(`7b_codex_critique_same_problem_rule.md`, FIX_FIRST on the first draft; its four findings are folded in below). Serves
rule 2 of the owner's ruling (`6_proposed_ruling_plain.md`: one full inspection, then one check of the repairs) and his
trial of 2026-11-17: on the second look a reader-confirmed new problem that quotes a passage a repair CHANGED still
blocks; a new problem on unchanged material is advisory and goes to his short list. Built in
`RIMMANDRAKE_WRITE_JUDGE_FOUR_RULES_TWO_LOOK_LIMIT`; its acceptance cases are `tickets/case_same_problem_identity.py`.

## Why four rounds failed

Every round tried to decide, from the judge's own words, whether a second-look gap was an old gap still open: matching
`what`, `observed`, `where`, a `since: g1`, evidence lists. Each matcher had a hole a reviewer reproduced: a reworded
open gap matched nothing and was signed as repaired; a new finding wearing an old id stopped judging; evidence in another
order failed to match. A text matcher over a model's prose always has such holes. **The fix is to stop matching: the
program asks about each old gap by its own number, and the judge answers in that slot.**

## The rule

1. **Each first-look gap is a numbered slot the program owns.** The repair check lists every prior gap (`g1`..`gN`,
   numbered by the program when the refusal was written) and the judge must answer `repairs`: one row per slot,
   `{gap, repaired: true|false, evidence}`, read from the fix itself, never from a claim form.
2. **A slot closes only when every sign agrees.** `gN` is repaired when its slot says `repaired: true`, every row the
   judge wrote this look on gN's ids is all ok, and no finding this look names gN (its number in `since`, or tagged
   `unfixed` on gN's ids). Anything else (slot missing, false, a failing row, a finding calling it open): **open.
   Unsure = open.** An answer in the old form, with no `repairs` key at all (replays, old fixtures), is read by its
   rows as the 2026-11-17 fix reads it: closed when every id has a row this look, all ok, and no finding names the ids.
3. **An open slot blocks as itself.** Its first-look record (promise, `would_pass`, `smallest_fix`) is the refusal; a
   second-look finding that names it is attached as a `second_look` note, never a separate refusal and never a new
   requirement (rule 3). A reworded, split or merged report can only keep its slot open.
4. **Every other finding is new.** A finding naming no slot but tagged `unfixed` (it says "still open" and points at
   nothing) is an unplaced repair report: it blocks, so the look cannot sign. Any other new finding (including a
   failing checklist part on a row no slot owns) blocks only when all three hold: (a) `since` is an entry key, a
   newline, then a passage of at least 12 characters that is present in exactly one of the entry's renderings before
   and after (whitespace collapsed; the rendering is the text the program shows a delta judge: `json.dumps(entry,
   ensure_ascii=False)`, a sheet section's text), so the passage itself changed, not just its entry; (b) the judge rates
   it `severity` `problem`; (c) the second reader confirms it serious. Otherwise it is advisory, `short_list: true`.
   To make (a) checkable every verdict stores `entry_text`, the rendering of each entry; a prior verdict without it
   (every verdict written before this build) can verify nothing, so its repair check's new findings are all advisory.
5. **The verdict is derived, never taken from the word.** `not_covered` exactly when an open slot, an unplaced report
   or a blocking new finding remains; otherwise covered, with the advisory findings stored and shown.
6. **A failed attempt keeps the baseline.** A look that errs, times out or ends malformed writes its record with
   `baseline`: the last usable verdict, which the next look reads as its prior. (Today `prior_verdict` returns nothing
   after a failed attempt and the retry loses every slot and hash.)
7. **Counting looks is unchanged by this rule.** Every well-formed `not_covered` is a refusal; the second stops
   judging; a malformed round is not a look; a release grants one look and its refusal stops again.

These apply to every look whose prior verdict (rule 6) is `not_covered`, delta or full re-judge alike.

## The input regions, and what each does

| region | outcome |
|---|---|
| reworded still-open gap, same rows | slot false (or the report names it): open, blocks as its first-look record |
| the same open defect reported under other rows, slot's rows all ok | slot false, or the report names gN: open. A judge that answers `true` and reports it unnamed contradicts itself in two places; no program catches that |
| a different new problem on a repaired slot's row (Codex finding 1) | slot true, rows ok, finding tagged new: the slot closes; the finding is new (rule 4) |
| a new finding reusing an old gap number | names gN: gN stays open (the judge said it is gN) |
| `unfixed` finding naming no slot | unplaced: blocks, unsigned |
| split / merged | each slot named stays open, as itself; nothing new is added |
| a finding naming a slot's rows and new rows | attached to the slot (keeps it open); its new rows are shown in the note |
| moved passage | slots are numbers, not positions: unchanged. A new finding quoting the moved text passes (a) |
| unchanged passage inside a changed entry (Codex finding 3) | present in both renderings: fails (a), advisory |
| quote rendered differently (key order, spacing) | checked against the program's own rendering, whitespace collapsed; not found = advisory |
| evidence in another order | evidence is not used for identity: no effect |
| slot `true` with a failing row on its ids | open |
| advisory findings plus failing parts on rows no slot owns | the parts are new findings without a quote: advisory; covered |
| `covered` word with an open slot | `not_covered` |
| id-less prior gap | closes by its slot alone; in the old form it cannot close (no rows) |
| failed attempt, then a retry (Codex finding 4) | the retry reads `baseline`: same slots, same hashes and texts |
| prior verdict without `entry_text` | every new finding advisory; slots follow rule 2 |
| stale release record | below |

**Phantom judge rounds, a defect found while designing this, fixed in the same build:** a second reader's charge (ref
`rm-coverage-judge-<n>-reader`) is counted by `rounds()` as a legacy judge round [measured 2026-11-18: Graffiti and
LeaningScrub each read one; LeaningScrub's stop reads "4 judge runs" from 3 real rounds]. The fix folds those charges
into their judge's spend and never makes them a round. A release written before the fix stores `rounds_at` counted
with the phantoms, so it is resolved against that old list to the set of real judges before it (phantoms dropped, never
promoted); a new release stores `judges_at`, the judge ids before it. An old release never grants an extra look.

## Test files the build touches

- `tickets/case_same_problem_identity.py` (new, the rows above plus the phantom round and both release forms) and
  `tickets/case_four_rules_two_looks.py` (unchanged): both must read wrong 0.
- `tickets/case_carried_gap_closes_on_ok_rows.py` (the landed fix, old-form answers): must stay green, unedited.
- `selftest_coverage_refusal_record.py`: its later-look fixtures re-report `unfixed` gaps to test record validation;
  under rule 3 an open slot is not re-validated, so those fixtures move to fresh first looks, every assertion kept.
- `selftest_judge_card_answers.py`: "a confirmed late gap blocks" becomes the two halves of rule 4 (changed passage
  blocks when confirmed; unchanged material never).
- `selftest_judge_calibration.py`: its unchanged-material late fixture expects a refusal; it becomes advisory.
- `selftest_coverage_judge_loop.py`, `selftest_designer_park.py`: the limit as `CJ.NOT_COVERED_LIMIT`, never a literal.
- `selftest_coverage_delta.py`, `selftest_coverage_judge.py`: changed only where a fixture relied on tag matching or on
  a claimed gap closing because the judge did not re-report it.

## Not built

Routing the short list to the owner (stored, `short_list: true`; the counts ticket counts it). Any semantic matcher.
Catching a judge that contradicts itself in two places at once.
