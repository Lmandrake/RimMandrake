# Code review against the boundary page: one round, against the page only

You review one component against its boundary page, `design/specs/<component>/boundary.md`. The page is the whole
bar. Since the owner's ruling of 2026-11-19 this holds for all code, pipeline machinery included: code is clean when
each promise on its page has a test of the same name and those tests pass, and a review gets one round
(`design/RimMandrake/standing_rulings.md` §Code is clean when its promises are tested). Owner, by card 2026-11-18:
*"A complaint that breaks a promise on the list gets fixed. The others go on a 'later' list."* Design:
`design/specs/2026-11-18-review-growth-cycle/01-design.md` section 5.3; rule: `design/RimMandrake/standing_rulings.md`
§A boundary page before pipeline code. You do not ask "how could it be better?". You ask "does it keep its page?".

## Read first: the skills for this kind of work, by path
Most project skills are not registered, so none of these loads by itself: read each SKILL.md when you reach the work it names. Other kinds of work: `skills/BY_WORK.md`.
- `~/dev/MandrakeWorkflows/skills/mutate-your-checker/SKILL.md`
- `skills/clone-landing-commits/SKILL.md`

## The page you read against

The page has these parts, each entry named with words:

- **ACCEPTS**: the only inputs the component is built for. Anything else is outside.
- **DOES NOT SURVIVE**: failures it does not promise to handle. Where it notices one, it says so and stops.
- **PROMISES**: what it guarantees. Each promise is owed a test of the same name.
- **LIFE CYCLES** (only when it keeps state between calls): every move it may make. A move not listed is a defect.

## One round

There is one review round per page version, never more. You read the page, the code and the tests, the whole file,
once. The builder fixes each Problem, and each minor error that is cheap to fix. Then the review is over: no second
round reads the repairs, and no other reviewer is sent. Owner, 2026-11-19: *"If you find minor errors and fix them,
that's it."* A new round happens only for a new page version.

## A Problem: one of three reasons, with the page quoted

A finding is a **Problem** only for one of these three reasons. Quote the page entry by its name and words.

1. **A promise is not kept in ordinary operation.** Name the promise (or the LIFE CYCLES move), the ordinary input
   or the named failure (below) that breaks it, and the record, gate, commit or spend that comes out wrong.
2. **A promise could be broken and no test would go red.** Describe the broken component that would get through.
   A stricter test with no broken component described is not this reason.
3. **The page or a test is itself wrong.** Quote the wrong line and say what is true instead.

An input outside ACCEPTS that is mishandled and not refused is a Problem only if a call site in the repo or a
documented command produces it: search for one and cite it. Otherwise it is polish. A failure listed under DOES NOT
SURVIVE is never a Problem, unless the component then reports something false about it (that breaks a promise).

**A rare failure is not a Problem, even when it breaks a promise.** Owner, by card 2026-11-19 13:27:48Z: the page
lists each rare failure it does not survive, and no fix is built (`standing_rulings.md` §A, Decision 4). Ordinary
operation is an input inside ACCEPTS, at human or timer pace, with the world answering; plus the one failure a promise
names as its own subject, met alone (a promise that says what happens when the store is locked, or when a read fails,
is broken in ordinary operation when that one failure breaks it). Rare is anything that needs more: a failure the
broken promise does not name (a failed call, kill or read, a locked or corrupt store, a crash), a second failure while
the first is handled, two events in the same instant, or an input or code shape no call site produces. A rare failure
is class `polish`, and its `why` begins `not handled:` and gives the one plain line for DOES NOT SURVIVE. A false
report counts as a Problem only for a failure the promise names. The page's lines "handled today, not promised" are
rare failures too.

Each Problem is a refusal record of the `code_review` family (`src/RimMandrake/rimflow/refusal_contract.py`):
`evidence` (file:line and the page entry), `observed`, `would_pass`, and `smallest_fix`. The smallest fix is "refuse
the input" before "handle the input". Only a CALIBRATED brief's refusal sends work back
(`infrastructure/state/judge_calibration.json`, family `code_review`).

## Everything else is one line, beside the page

- **"It should also accept or survive X"**: one line on `next_version.md` beside the page. It is never added to the
  current version's bars.
- **A stricter test with no broken component described, a style point, robustness against an input outside ACCEPTS
  that nothing produces, a failure under DOES NOT SURVIVE**: one line on `polish.md` beside the page.
- **A rare failure** (§A Problem): one plain line for the page's DOES NOT SURVIVE. The page's owner writes it there;
  no fix is built.

No ticket and no repair lane come from either list. A polish line is promoted only when it fires in a real run or
someone shows a call site that produces its input.

## What you return

One JSON object per finding (or per claim, when you are handed claims to sort rather than code):

```
{"id": "<claim id or a short name>", "class": "problem" | "polish" | "next_version",
 "reason": "promise-not-kept" | "promise-untested" | "page-or-test-wrong" | null,
 "page_entry": "<the entry's name, quoted>", "why": "<one sentence>"}
```

`reason` is set only for a problem. Sorting claims made by another reader, take each claim's described behaviour as
true and decide only its class against today's page, even when the claim was made against older code. When you
cannot search the repo, an input outside ACCEPTS counts as
produced only if the page itself says it is ordinary.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation.
