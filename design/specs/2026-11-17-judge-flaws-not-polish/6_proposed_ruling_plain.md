# Proposed ruling: the judge refuses flaws, not polish

**Status: ADOPTED by the owner by question card, 2026-11-17, answered about 5:17 PM PST** ("Adopt the four rules
(Recommended)"; OWNER.jsonl tsn 1794964642498221334, on `RIMMANDRAKE_RETHINK_JUDGE_STRICTNESS_BARS_LOOSE_PROOFS_ORNATE`).
**The build is still owed:** the rules bind once the judge and Designer prompts are edited and the judge is
recalibrated, not before. Until then the judge runs as it stands. Standing ruling: `design/RimMandrake/standing_rulings.md`
§The judge refuses flaws, not polish. Build tickets: filed under the parent item (`rimflow show` it).
Wording settled with the owner in conversation, 2026-11-17 about 5:00 to 5:20 PM PST. Sources: the Fable independent
review (`5_fable_independent_review.md`), GPT's two rounds (`3_…`, `4_…`), the owner's words (`1_…`).

## The four rules

### 1. The judge may refuse for only three reasons

1. **A promise is not kept.** The bar says orange and the evidence shows it is not orange.
2. **Nobody would notice if a promise were broken.** There is no test for it, or the test cannot fail. The judge must
   describe the broken mod that would get through.
   - The fire-immunity test where the beast never touches fire.
   - The wind test with one wind direction, which passes a mod whose fire always spreads east.
3. **The test or the paperwork is itself wrong.** A test that would fail a correct mod, or a file that says something
   false.
   - A test counting a creature that was deleted, so it can only read zero.

Every refusal quotes the promise it rests on. Anything else is advice and does not block: "prove it more thoroughly",
"test more cases", "it could be better", polish, tuning.

*Dial:* who must confirm a refusal. Today only late findings get a second reader. One step up: every refusal.
*Turn it up* when refusals keep being overturned; *turn it down* when play finds flaws the judge passed.

### 2. One full inspection, then one check of the repairs

On the first look the judge hunts for everything. On the second it checks only whether the listed problems were fixed,
by reading the fix itself, never by whether a form was filed. It may raise something new on the second look only when a
repair itself broke something, and it must quote the changed passage. After that it stops; anything left goes to the
owner as a short list, not to another judge.

*Dial:* the number of looks, starting at 2.
*Watch:* looks used per mod, and new demands on material that had not changed (should read 0).

### 3. A refusal may not create new requirements

A refusal binds only "close this hole". The numbers, day counts, wind bearings and methods the judge suggests are one
way to close it, never a bar; the builder may close it another way. A number binds only if the owner said it. The mod
itself is never changed to hit a test's number: if a test seems to need that, it is a question for the owner.

(The 2026-11-12 ruling stands: every refusal still carries an attainable path to pass. That path is a suggestion.)

*Watch:* any refusal citing a number that is not in the owner's words; any change to the mod that cites a test.

### 4. Only the owner's promises must be proven; the Designer's extra warnings are tips

The Designer may add "it must not read as…" lines under a bar. Unless the line is the owner's own words or the plain
opposite of the promise, it is a tip that helps the judge think of broken mods. It is never a separate thing that needs
its own test.

*Dial:* how many such tips the Designer may write per promise, starting at 1.
*Watch:* the share of refusals that rest on a line the owner did not say.

## Two bugs fixed whatever is decided

- A finding the judge itself rated polish can block today (`src/RimMandrake/rimflow/bar_rule.py`).
- A problem the judge found repaired stays refused when a claim form is missing
  (`src/RimMandrake/rimflow/coverage_judge.py`). This caused the three wasted refusals at Pyrelands look 8.

## How it is built

1. The four rules go into the judge's and Designer's instructions as prompt text, in the plain wording above.
2. The two bug fixes land as their own small commits, each with a test that fails first.
3. The look limit changes from 3 refusals to 2 looks.
4. The changed judge is recalibrated before its refusals bind. Three cases from the Pyrelands record are added to the
   calibration: look 8 must close, the beast-never-touches-fire test must be refused, "test the giant against every
   roster kind" must not block.
5. Four counts are printed when a mod's coverage stage closes: looks used; refusals and how many were overturned; new
   demands on unchanged material; refusals citing a number or line the owner did not say. After the played session, a
   fifth: flaws found in play that the judge passed.

**Not built now:** GPT's five new record fields, the hash-based ratchet alarm, the 18-case calibration set, and
corrections without a fresh exam. Each waits until a real miss asks for it.

**Rollback:** the rules are prompt text and one value. Revert the one commit; the two bug fixes stay.

## Pyrelands, under these rules

- It stays covered; it is not reopened and the rules are not applied backwards.
- The pending restamp and the one-entry look are done, with no fresh search.
- The landed wind and burned-share tests stay. "Most of the map" and "wind off must flood" are marked as examples.
- Its wind and burned-share tests have never been run live. They run at the next played session; that is the first real
  evidence about them.

## Known weaknesses

- Nothing here has been run against a judge. How a judge behaves under these rules is a guess until the calibration
  and the first mod.
- A keen judge can describe "a broken mod that would get through" for almost anything. Rule 2 and the second-reader
  dial are what hold that in check, not the wording of rule 1.
- With one full inspection, what the first look misses reaches play unless a repair check or the played session
  catches it.
