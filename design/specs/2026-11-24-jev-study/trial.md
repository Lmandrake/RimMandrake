# The one trial: a peek at what a live run is doing

This page belongs to `study.md` beside it. It is a plan. Nothing here is built. The pass line below was written
on 2026-11-24, before any run of the trial.

## Why this trial and no other

- The owner asked on 2026-11-24 for a peek at what each live run spends its time on. Nothing gives it today.
- The answer is in the text that the model would read (the last events of the run). The two judgments that
  failed in `study.md` did not have that property.
- A wrong answer costs little: one wrong word on a status page, with the raw last line beside it.
- The trial is also a fair test of Jev against plain code. If a rule on tool names does as well, we ship the rule
  and stop asking where Jev could help with our build-time text.

The Designer's expectation, written before the run: the plain rule ties Jev on the activity word `[guess ~55%]`,
and Jev wins on "is this run stuck" only if hindsight labels are clean `[guess ~40%]`.

## What it replaces

Today, to learn what a live run is doing, the Conductor (Fable) or the owner reads the run's notes or the tail of
its transcript. A Sonnet reader of the same tail would cost about 10,000 weighted tokens a look `[guess ~50%]`.
The peek would cost about 30 weighted tokens a look with Jev `[guess ~60%]`, and nothing with the rule.

## The three contenders

Each contender reads the same window: the last 15 events of one run's transcript. An event is the tool name, the
first 200 characters of the command or the text, and the seconds since the event before it.

1. **The rule.** Code only: tool names and command words (`Read` is reading; `./publish` is landing;
   `waitalive.py` is waiting; the same failed command three times is a loop).
2. **Jev.** One call for each window, with two questions:
   - a Choice, "what is this run doing now?", over the eight words below;
   - a Noul, "is this run repeating an act that keeps failing?".
3. **Jev's answers with a fitted threshold.** The Noul's threshold is fitted on half of the windows and scored
   on the other half.

The eight words: reads to understand · edits or builds · runs offline tests · drives a live game · waits for a
job or a game · repairs a refusal of form · repeats a failed act · writes records.

## The labelled set

- **80 windows** from at least 20 different finished runs of the last 7 days. A seeded script picks the runs and
  the moment in each run. No window is picked by hand.
- **The activity label.** Two fresh Opus readers label each window, each alone. Each reader sees 60 events (a
  wider view than the contenders get). Only windows where the two readers agree are scored. Report how many
  windows were lost to disagreement.
- **The stuck label, by hindsight and by code.** A window is "stuck" when the next 20 minutes of the same
  transcript hold no new commit, no new note, no new file write and no test that passed. Otherwise it is "moving".
  No reader's opinion goes into this label.
- No transcript text leaves the machine except the window sent to Jev. The windows hold our own commands and
  file names. A script removes any line that matches a key pattern before the call.

## The pass line

Jev passes only if **all three** hold, on windows that no threshold was fitted on:

1. Jev's activity word agrees with the label on **85% or more** of the windows.
2. That figure is **10 points or more above the rule's** on the same windows.
3. For "stuck", with the fitted threshold: Jev catches **70% or more** of the stuck windows and flags **5% or
   fewer** of the moving windows.

The rule passes on its own if its activity word agrees with the label on 85% or more.

If fewer than 50 windows survive the readers' disagreement, or fewer than 10 windows are "stuck", the trial is
`COULD NOT DECIDE`. That is not a pass and not a fail; widen the sample once and run again.

## What we do on each result

| result | act |
|---|---|
| Jev passes | Build the peek as one column on the pipeline page: the word, with the raw last line beside it. Pin the model version. The peek is a display only. It never feeds a stop, a void or an alarm. Write its boundary page first. |
| Jev fails and the rule passes | Build the same column from the rule. Record Jev as measured unfit for our build-time text. Remove the uncalibrated shadow caller (`src/RimMandrake/Utils/modcheck/jev_triage.py`, `jev_questions.py`, `selftest_jev.py`), which has waited for a calibration since 2026-10-01. |
| Both fail | Build nothing. The peek stays a hand act. Record both figures, so that nobody asks a third time without a new model or a new input. |

## The cost of the trial

- Jev: 80 calls of about 1,500 tokens ≈ 1,300 weighted tokens `[guess ~70%]`.
- The two Opus readers: about 200,000 weighted tokens in total `[guess ~50%]`.
- The sampling script and the rule: one short Sonnet or Opus run.

## What the trial does not show

A pass shows that Jev can name an activity from a window of our transcripts. It does not show that Jev can judge
our tickets, findings or failed checks: `study.md` measured two of those, and both failed.
