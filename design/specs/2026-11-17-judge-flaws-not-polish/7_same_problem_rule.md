# When is a second-look finding the same problem as a first-look one?

Item `RIMMANDRAKE_DESIGN_JUDGE_SAME_PROBLEM_MATCH_FOUR_ROUNDS_LOST`, 2026-11-18. Serves rule 2 of the owner's ruling
(`6_proposed_ruling_plain.md`: one full inspection, then one check of the repairs) and his trial of 2026-11-17: on the
second look a reader-confirmed new problem that quotes a passage a repair CHANGED still blocks; a new problem on
unchanged material is advisory and goes to his short list. The build is `RIMMANDRAKE_WRITE_JUDGE_FOUR_RULES_TWO_LOOK_LIMIT`.

## Why four rounds failed

Every round tried to decide, from the judge's own words, whether a second-look gap was an old gap still open: matching
`what`, `observed`, `where`, a `since: g1`, evidence lists. Each matcher had a hole a reviewer reproduced: a reworded
open gap matched nothing and was signed as repaired; a new finding wearing an old id stopped judging; evidence in another
order failed to match. A text matcher over a model's prose will always have such holes. **The fix is to stop matching.**

## The rule

1. **Identity is the row, never the wording.** A first-look gap's identity is the checklist row ids it names (an id-less
   gap is the `rest` row). The program carries them from the prior verdict. Nothing the judge writes on the second
   look decides identity: its `new_since` tag, a `since` gap number, its wording, its evidence and their order are
   ignored for it.
2. **A prior gap is repaired only when the judge's own rows say so.** Claimed or not claimed (the claim form only
   decides what the judge is shown): repaired when every one of its row ids has a row written this look with at least
   one part and every part ok, and no finding this look names any of those ids. Anything else, including a row not
   written, a contradictory row, or a malformed answer: **open. Unsure = open.**
3. **An open prior gap blocks as itself.** Its first-look record (promise, `would_pass`, `smallest_fix`) is the
   refusal. Second-look findings that name its ids are attached to it as `second_look` notes for the Designer and the
   owner; they are never a separate refusal and never a new requirement (rule 3). This is why a reworded or split or
   merged report cannot sign anything off or add anything: it can only keep its row open.
4. **A finding on rows no prior gap names is new.** It blocks only if all three hold: (a) its `since` names an entry key
   that changed since the prior verdict and a passage the program finds verbatim (whitespace collapsed) in that entry's
   current text as the program rendered it to the judge (a removed entry is quoted by its key); (b) the judge gave it
   `severity` `problem`; (c) the second reader confirms it serious. Otherwise it is advisory and marked for his short
   list. With no entry hashes on the prior verdict, nothing can be shown to have changed: every new finding is advisory.
5. **The verdict word is never trusted over the rows.** The look is `not_covered` exactly when an open prior gap or a
   blocking new finding remains; `covered` with an open gap is `not_covered`; `not_covered` with only advisory findings
   is covered (stored and shown).
6. **Counting looks is not changed by this rule.** Every well-formed `not_covered` is a refusal; the second stops
   judging; a malformed round is not a look; a release grants one look and its refusal stops again.

These rules apply to every look whose prior verdict on file is `not_covered`, delta or full re-judge alike.

## The input regions, and what each does

| region | outcome |
|---|---|
| reworded still-open gap, same rows | rows named: prior gap open, blocks as its first-look record |
| reworded gap citing other rows (scene instead of tree) | prior gap's rows not all ok, or not written: open. The new-row finding is new: advisory unless rule 4 |
| new finding reusing an old gap number or row | names the prior rows: keeps that gap open (unsure = open), no extra refusal, no new demand |
| split (one gap reported as two) / merged (two as one) | each prior gap whose rows are named stays open; nothing new is added |
| moved passage | identity is row ids, not file positions: unchanged. A new finding quoting the moved text qualifies for rule 4 (it changed) |
| evidence in another order | evidence is not used for identity: no effect |
| contradictory: row all ok and a finding on it | the finding wins: open |
| contradictory: `covered` word with a failing row, or with gaps | `not_covered` (rows and gaps outrank the word) |
| id-less prior gap | closes only by a `rest` row written this look, all parts ok; the prompt asks for that row |
| prior verdict without hashes | no changed entry can be shown: every new finding advisory; prior gaps follow rule 2 |
| quote rendered differently (key order, spacing) | checked against the exact text the prompt showed, whitespace collapsed; not found = advisory |
| stale release record | see below |

**A defect found while designing this, built in the same ticket:** a second reader's charge (ref
`rm-coverage-judge-<n>-reader`) is counted by `rounds()` as a legacy judge round [measured: Graffiti and LeaningScrub
each read one phantom round; LeaningScrub's stop reads "4 judge runs" from 3 real rounds]. The fix folds those charges
into their judge's spend and never makes them a round. A release written before the fix stores `rounds_at` counted
with the phantoms, so it is resolved against that old list to the set of judges before it; a new release also stores
`judges_at`. When the two disagree, the earlier boundary wins (an old release never grants an extra look). In-repo
today one release exists (Contagion, no phantoms) [measured].

## Test files the build must touch

- `design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_four_rules_two_looks.py`: kept as is (wrong 0).
- `design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_same_problem_identity.py`: new, one case per table row
  above plus the phantom reader round and the legacy release; watched failing on base.
- `src/RimMandrake/rimflow/selftest_coverage_refusal_record.py`: its repair fixtures expect an `unfixed` report to
  enter refusal validation; under rule 3 an open prior gap is not re-validated. Fixtures change, its observation-storage
  and bounded re-ask assertions stay.
- `selftest_judge_card_answers.py`: "a confirmed late gap blocks" becomes "a confirmed new gap blocks only with a
  verified changed-passage quote"; unchanged-material late gaps advisory.
- `selftest_judge_calibration.py`: the unchanged-late fixture expects a refusal; it becomes advisory.
- `selftest_coverage_judge_loop.py`, `selftest_designer_park.py`: the limit, expressed as `CJ.NOT_COVERED_LIMIT`.
- `selftest_coverage_delta.py`, `selftest_coverage_judge.py`: run; changed only where a fixture relied on tag matching.

## Not built

Routing the short list to the owner (stored in `advisory_gaps`, `short_list: true`; who reads it is the counts ticket's
and a later one's). Any semantic matcher. A judge-assigned identity field.
