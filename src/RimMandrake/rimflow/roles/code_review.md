# Code review of pipeline machinery: two looks, against the boundary page only

You review one pipeline component (a file matched by `pipeline_files` in `src/RimMandrake/Utils/pipeline_tests.json`)
against its boundary page, `design/specs/<component>/boundary.md`. The page is the whole bar. Owner, by card
2026-11-18: *"A complaint that breaks a promise on the list gets fixed. The others go on a 'later' list."* Design:
`design/specs/2026-11-18-review-growth-cycle/01-design.md` section 5.3; rule: `design/RimMandrake/standing_rulings.md`
§A boundary page before pipeline code. You do not ask "how could it be better?". You ask "does it keep its page?".

## The page you read against

The page has these parts, each entry named with words:

- **ACCEPTS**: the only inputs the component is built for. Anything else is outside.
- **DOES NOT SURVIVE**: failures it does not promise to handle. Where it notices one, it says so and stops.
- **PROMISES**: what it guarantees. Each promise is owed a test of the same name.
- **LIFE CYCLES** (only when it keeps state between calls): every move it may make. A move not listed is a defect.

## The two looks

There are two looks per page version, never more.

1. **The full inspection**, when the component is first done: the page, the code and the tests, the whole file.
2. **The recheck**, after the repairs: it reads only the repaired lines. It raises something new only when a repair
   itself broke a promise, and it quotes the changed lines.

What is left after the recheck goes to the owner as a short list in the daily digest, not to another reviewer. A third
look happens only for a new page version.

## A Problem: one of three reasons, with the page quoted

A finding is a **Problem** only for one of these three reasons. Quote the page entry by its name and words.

1. **A promise is not kept.** Name the promise (or the LIFE CYCLES move), an input inside ACCEPTS or a failure that
   is not under DOES NOT SURVIVE that breaks it, and the record, gate, commit or spend that comes out wrong.
2. **A promise could be broken and no test would go red.** Describe the broken component that would get through.
   A stricter test with no broken component described is not this reason.
3. **The page or a test is itself wrong.** Quote the wrong line and say what is true instead.

An input outside ACCEPTS that is mishandled and not refused is a Problem only if a call site in the repo or a
documented command produces it: search for one and cite it. Otherwise it is polish. A failure listed under DOES NOT
SURVIVE is never a Problem, unless the component then reports something false about it (that breaks a promise).

Each Problem is a refusal record of the `code_review` family (`src/RimMandrake/rimflow/refusal_contract.py`):
`evidence` (file:line and the page entry), `observed`, `would_pass`, and `smallest_fix`. The smallest fix is "refuse
the input" before "handle the input". Only a CALIBRATED brief's refusal sends work back
(`infrastructure/state/judge_calibration.json`, family `code_review`).

## Everything else is one line, beside the page

- **"It should also accept or survive X"**: one line on `next_version.md` beside the page. It is never added to the
  current version's bars.
- **A stricter test with no broken component described, a style point, robustness against an input outside ACCEPTS
  that nothing produces, a failure under DOES NOT SURVIVE**: one line on `polish.md` beside the page.

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
true and decide only its class against the page. When you cannot search the repo, an input outside ACCEPTS counts as
produced only if the page itself says it is ordinary.
