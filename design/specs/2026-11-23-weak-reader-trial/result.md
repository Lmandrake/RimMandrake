# Result of the pilot: does the rewritten rule text make a weaker reader act more correctly?

Item `RIMMANDRAKE_TRIAL_WEAK_READER_ACTS_ON_OLD_AND_NEW_RULE_TEXT`. Run 2026-11-23, 10:12 to 10:35 AM PST. 40 cases, 680 reader calls, 0
failed calls. The prediction was published (`92a9c306a7`) before the first reader ran, and its bars did not move.

## In four sentences
- **Plain style alone changed nothing that this pilot can see.** Sonnet already reads the old sentences right (98%), so
  there is no room above. The question "does style help" is NOT answered for harder conditions. [measured]
- **Giving an undefined term its meaning helped Sonnet: 64% → 92%, and it missed my own bar (30 points) by 2.** Read it
  as promising, not shown. [measured]
- **Correcting a false line is by far the largest effect: 10% → 70%, for Sonnet and for Opus alike.** [measured]
- **Your premise about Opus holds for style and terms** (old text: Opus 100% and 90%), **and not for false lines**: Opus
  obeys a false line as faithfully as Sonnet does (10%). [measured]

## The scores (all [measured]; 10 cases for each kind; 5 Sonnet and 2 Opus readers for each arm of each case)

"Correct" = the reader says that the text tells it, and the act is right. NOT TOLD = the reader says "the text does not
tell me". No call failed and no answer was unreadable, in any cell.

| kind | reader | text | correct | wrong | not told | failed |
|---|---|---|---|---|---|---|
| STYLE | Sonnet | old | 49 of 50 (98%) | 1 | 0 | 0 |
| | Sonnet | new | 50 of 50 (100%) | 0 | 0 | 0 |
| | Opus | old / new | 20 of 20 / 20 of 20 | 0 / 0 | 0 / 0 | 0 / 0 |
| BINDING | Sonnet | old | 32 of 50 (64%) | 0 | 18 | 0 |
| | Sonnet | new | 46 of 50 (92%) | 0 | 4 | 0 |
| | Opus | old / new | 18 of 20 (90%) / 20 of 20 | 0 / 0 | 2 / 0 | 0 / 0 |
| CORRECTION | Sonnet | old | 5 of 50 (10%) | 45 | 0 | 0 |
| | Sonnet | new | 35 of 50 (70%) | 1 | 14 | 0 |
| | Opus | old / new | 2 of 20 (10%) / 14 of 20 (70%) | 16 / 2 | 2 / 4 | 0 / 0 |
| CONTROL (same bytes in both arms) | Sonnet | old | 48 of 50 (96%) | 1 | 1 | 0 |
| | Sonnet | new | 49 of 50 (98%) | 1 | 0 | 0 |
| | Opus | old / new | 20 of 20 / 20 of 20 | 0 / 0 | 0 / 0 | 0 / 0 |

Difference new − old, Sonnet, by case (n = 10 cases), with a 95% bootstrap interval: STYLE +2 [0, +6]. BINDING +28 [+6, +56].
CORRECTION +60 [+30, +90]. CONTROL +2 [0, +6].

## Can the instrument see? All four checks fixed in advance passed [measured]

| check | bar | reading |
|---|---|---|
| grader scores planted answers as planted | ≥ 95% | 200 of 200 alone, 200 of 200 mixed with the real answers |
| known positive (CORRECTION) | ≥ +30 | +60 |
| known zero (CONTROL) | inside ±15 | +2 |
| readers with no text act worse than readers of the new text | ≥ 20 points | 40% against 93% (act right, TOLD mark ignored) |

## What it shows, by the table in `prediction.md`
- **STYLE:** two rows apply: "inside ±10" and "Sonnet old ≥ 90%: no room". If there is a style effect on one section in
  front of the reader, it is at most about 6 points. That agrees with the earlier 0 of 5.
- **BINDING:** +28 misses the bar (30) and the interval is above 0. No row of my table covers that gap. I do not round it up.
  - All of it comes from 4 of 10 cases: "lane", "a metric joins", "settings/snapshot debts", "on one alarm". In the other 6, the rest of
    the section already gave the meaning.
  - The old text never made Sonnet act WRONG on a term (0 of 50). It made Sonnet say "not told" (18 of 50). When the
    TOLD mark is ignored, Sonnet's act was right more often, and the difference shrinks to +14 [0, +36].
  - So the cost of an undefined term, here, is a stop or a hunt through other files, not an error.
- **The weak reader does show what Opus hides,** on terms: +28 for Sonnet, +10 [0, +30] for Opus. Opus read three of the
  four terms from context; only "lane" stopped it.
- **CORRECTION new is not 100%.** In three cases the correction deleted the false line, or left only a pointer, and the
  section then told the reader nothing: "build his daily digest" (0 of 5; readers still build it by hand), the `Jawa/` tier (0 of 5; the
  pointer goes to a file that a reader here cannot open), `broadcast.py` (0 of 5; the line says who may, not when). A deletion
  stops no one who would do the wrong thing by common sense.
- One false line did not mislead anyone (the 45-minute bridge line: 5 of 5 on both texts).

## What it cannot show
- What an agent with tools does, or whether a reader of a whole file finds the line. Both could favour the plain text.
- Anything about a human reader. `clear-findings` already says that this is unmeasured.
- Style by itself at section level: of 36 random changed sections, only 3 changed in style only. So the kind is the
  kind of the sentence that the case turns on, and the rest of the section travels with it.
- The plants were easy (the case author wrote them). A hand read of 20 random grades and of every told-but-wrong answer found the grader too
  strict on 2 CONTROL answers (one in each arm: the act was right, "60 minutes" unsaid) and perhaps 2 "a metric joins" answers (already
  NOT TOLD, so only the +14 moves). I left the grades as they fell.
- I wrote the source-of-truth lines after I had seen many new lines; that can favour the new text in BINDING and
  CORRECTION. The STYLE keys come from the old text; that can favour the old.

## The full trial
- Prediction said 95 cases for each kind. The measured spread for BINDING is 42 points, so 10 points needs about 138 cases.
  Only 21 of the 76 resolved terms turn an act, by my hand count [measured; a judgment each], so that trial cannot exist.
- Cost per case, with no Opus readers: about 37,000 weighted tokens (`weighted_v2`: situation and key 13k, 13 Sonnet readers 17.6k, grading
  ≈6k) [measured, grading share guess ~70%]. The full trial as first sized (285 cases) is ≈10.5M [guess ~80%].
- **Not worth it.** STYLE has no room; CORRECTION is already decided; BINDING has no 138 cases.
- Worth it, if you want BINDING settled: the 9 act-bearing terms not yet used, at 5 readers: ≈0.33M weighted tokens [guess ~80%]. With 19 cases the
  trial can see about 27 points, so it can confirm an effect of the size seen, no smaller one.
- This pilot spent 2.51M weighted tokens, all instrument calls: readers 1.18M (Sonnet 0.71M, Opus 0.47M), Opus
  situations, key checks, classifier and grader 1.33M. [measured]

## What I would do with it
Rank rule-file work by this order: (1) find false lines and correct them; state the right act, do not only delete;
(2) gloss a term only where the rest of the section does not already give its meaning; (3) do not spend on style alone
for the sake of agents. Style may still be worth it for you as a reader; this trial says nothing about that.
