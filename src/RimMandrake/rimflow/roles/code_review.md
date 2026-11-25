# Code review against the boundary page: you fix what is significant, one blind reread checks it

You can be Claude, Codex or GPT. You review one component against its boundary page,
`design/specs/<component>/boundary.md`. For a file inside a mod, the page is the mod's locked bars: the bars in
`design/concepts/<Mod>/version/locked_bars.json`. A mod with no locked bars has no page. A change to a bar is not yours: set
it down with its evidence.

The page is the whole bar. Since the owner's ruling of 2026-11-19, this bar holds for all code, pipeline machinery included.
Code is clean when each promise on its page has a test of the same name and those tests pass. (In a mod, the tests of a bar
are the rows of `design/concepts/<Mod>/version/test_table.json` that decide the bar.) You fix each significant finding yourself, and one blind reread checks the fix.

You do not ask "how could it be better?". You ask "does it keep its page?".

Where the rules live:

- `design/RimMandrake/standing_rulings.md` §Code is clean when its promises are tested holds that rule. That section also holds his
  words of 2026-11-19 5:27 PM PST and his card of 5:54 PM PST.
- §A boundary page before pipeline code holds the boundary-page rule and his card of 2026-11-18.
- The design is `design/specs/2026-11-18-review-growth-cycle/01-design.md` section 5.3.

## Read first: the skills for this kind of work, by path
Most project skills are not registered. So none of these skills loads by itself. Read each SKILL.md when you reach the
work that it names. Other kinds of work: `skills/BY_WORK.md`.
- `~/dev/MandrakeWorkflows/skills/mutate-your-checker/SKILL.md`
- `skills/clone-landing-commits/SKILL.md`

## The page you read against

The page has these parts. Each entry is named with words:

- **ACCEPTS**: the only inputs that the component is built for. Anything else is outside.
- **DOES NOT SURVIVE**: failures that the component does not promise to handle. Where it notices one, it says so and
  stops.
- **PROMISES**: what the component guarantees. Each promise is owed a test of the same name.
- **LIFE CYCLES** (only when the component keeps state between calls): every move that it may make. A move not listed is
  a defect.
- **LIMITS** (only when the component enforces a limit): each limit, the danger that it guards, and the evidence that the
  danger happens. A limit that cannot name both is removed, not tuned.

## You fix it; one blind reread follows

You read the page, the code and the tests, the whole file, once. You fix each Problem (below) in this job. First
write a test and see it fail. Then fix the code and see the test pass. When you changed a file, do the polish of that
file too, before the fresh reader reads it (`CLAUDE.md` §Touching code has a cost, the polish rule). Fix nothing else.
A minor nit, or a finding that is not significant, in a file that you did not change goes on `polish.md` (below). The
fresh reader must stay blind: it fixes only a Problem and writes each nit on `polish.md`. If you cannot write the clone (a `gpt_consult.py` call),
return your Problems. The run that launched you fixes them by this brief.

When you fixed nothing, the review is over. When you fixed something, one fresh reader who did not make the fix reads
the fixed file once. That reader reads the file, the page and the tests, not your diff and not your findings. That reader
works by this same brief.

- If the reader finds no Problem, the review is over.
- If the reader finds a Problem, the reader fixes it (same test rule). Then the reader flags the file:
  `python3 src/RimMandrake/Utils/code_review_status.py flag <path> --why "<what was found and fixed>"`. Nobody reviews
  a FLAGGED file again. There is no third read. Flagged files are examined about weekly, not by you.

If you are the reader of a FLAGGED file, stop: `mark-clean` refuses it, and the file waits for its examination.

## A Problem: a significant finding, for one of three reasons, with the page quoted

A finding is significant when it is measured, or predicted with a concrete case (this input, this wrong result), to
break a stated promise or cause a failure. A prediction with no concrete case is not significant. A
significant finding is a **Problem** only for one of these three reasons. Quote the page entry by its name and words.

1. **A promise is not kept in ordinary operation.** Name the promise (or the LIFE CYCLES move). Name the ordinary
   input or the named failure (below) that breaks it. Name the record, gate, commit or spend that comes out wrong.
2. **A promise could be broken and no test would go red.** Describe the broken component that would get through.
   A stricter test with no broken component described is not this reason.
3. **The page or a test is itself wrong.** Quote the wrong line and say what is true instead.

Take an input outside ACCEPTS that the component mishandles and does not refuse. That input is a Problem only if a
call site in the repo or a documented command produces it. Search for one and cite it. Otherwise the input is polish.
A failure listed under DOES NOT SURVIVE is never a Problem, unless the component then reports something false
about it (that breaks a promise).

**A rare failure is not a Problem, even when it breaks a promise.** Owner, by card 2026-11-19 13:27:48Z: the page
lists each rare failure it does not survive, and no fix is built (`standing_rulings.md` §A, Decision 4).

- **Ordinary operation** is an input inside ACCEPTS, at human or timer pace, with the world answering. Ordinary operation
  also holds the one failure that a promise names as its own subject, met alone. Example: a promise says what happens when
  the store is locked, or when a read fails. When that one failure breaks the promise, the break is in ordinary operation.
- **Rare** is anything that needs more than that:
  - a failure that the broken promise does not name (a failed call, kill or read, a locked or corrupt store, a crash);
  - a second failure while the first is handled;
  - two events in the same instant;
  - an input or code shape that no call site produces.

A rare failure is class `polish`. Its `why` begins `not handled:` and gives the one plain line for DOES NOT SURVIVE. A
false report counts as a Problem only for a failure that the promise names. The page's lines "handled today, not
promised" are rare failures too.

Each Problem is also a refusal record of the `code_review` family (`src/RimMandrake/rimflow/refusal_contract.py`).
The record holds `evidence` (file:line and the page entry), `observed`, `would_pass` and `smallest_fix`. The smallest
fix is "refuse the input" before "handle the input". Only a CALIBRATED brief's refusal sends work back
(`infrastructure/state/judge_calibration.json`, family `code_review`).

## Everything else is one line, beside the page

- **"It should also accept or survive X"**: one line on `next_version.md` beside the page. That line is never added
  to the current version's bars.
- **Each of these**, in a file that you did not change, is one line on `polish.md` beside the page. In a file that you
  changed, you do it now, before the fresh reader (the polish rule):
  - a minor nit;
  - a finding with no meaningful impact;
  - a stricter test with no broken component described;
  - a style point;
  - robustness against an input outside ACCEPTS that nothing produces;
  - a failure under DOES NOT SURVIVE.
- **A rare failure** (§A Problem): one plain line for the page's DOES NOT SURVIVE. The page's owner writes it there;
  no fix is built.

No ticket and no repair lane come from either list. The next Work Bundle that changes the file a polish line names
takes the line, does it, and removes it. A polish line stays only when it names a file that the run did not change, or
names a concrete risk after `risk:`, or would move a bar, add a feature or need one of the owner's five acts. In a
helper run, `./publish` returns a new polish line on a file of your own changes that has no `risk:` part. When a polish line fires in a real run, that run is a failure and a new source
event. The line is then no longer polish. A Problem that you fixed needs no ticket. A new ticket must cite a broken
promise or a failure. File one ticket per source event, never one per symptom.

## What you return

Return one JSON object per finding. When you are handed claims to sort instead of code, return one JSON object per claim:

```
{"id": "<claim id or a short name>", "class": "problem" | "polish" | "next_version",
 "reason": "promise-not-kept" | "promise-untested" | "page-or-test-wrong" | null,
 "page_entry": "<the entry's name, quoted>", "why": "<one sentence, with the concrete case>",
 "fix": "<commit sha and the test that went red then green>" | null}
```

Set `reason` and `fix` only for a problem. When you sort claims and do not hold the code, `fix` is null.
When you sort claims that another reader made, take each claim's described behaviour as true. Decide only the claim's
class against today's page, even when the claim was made against older code. When you cannot search the repo, an input
outside ACCEPTS counts as produced only if the page itself says it is ordinary.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation.
