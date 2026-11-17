# Three changes to how the pipeline records evidence

**Filed** 2026-11-17, ~12:10 PM PST, by the Conductor, from the owner's conversation of the same
morning (the e2e.com evaluation and his reply to it). Design Version of this spec: **0.1.0**.

**What this is.** Three narrow changes to what the Maturation Pipeline *records* about its own runs.
None of them changes a bar, a stage, a model, or a budget. Each exists because the pipeline currently
writes down a verdict that reads stronger than the evidence under it, and a human later pays for the
difference.

**The frame, in his words (2026-11-17).** On the first: *"Requiring a second Bridge sitting is
gratuitous. But if the reporter can do a little more work to include a proof that the filed bug is
caused precisely by the issue suspected and NOT by several others, that's vital information they have
the context to perform."* And: *"This is valuable wisdom, NOT a blocker to cause problems, and should
never be a significant %token spend."* On the second: *"these are pipeline issues to resolve (valid
pipeline findings), but they should in no way be construed to be measurements of a mod or the final
game's state nor of the current agent's function. And sometimes they are. The current pipeline will
say 'Sorry, you failed one of your allotted walk-throughs' because the game failed to start or some
other nonsense."* And: *"Unmeasured should be refused unless it specifies WHY. Literally bounced,
maybe even by a hook. Agents not capturing their context and insights when they report has been a
bane on this project."* On the third: *"A non-informative PASS result is comforting but
uninformative: you wouldn't authorize another one. A non-informative FAIL is even worse: you
certainly shouldn't authorize another of those either. An informative FAIL that has made progress,
real discoveries, findings have why's attached... that's valuable, and I certainly would authorize
another of those... But if it's producing the SAME insights and somehow returning for a repeat
pass... again that's non-informative overall, and I wouldn't authorize it anymore."*

**What he rejected, and why it is not here.** A budget or FAIL quota (*"the pipeline is so new right
now it's hard to realistically predict them. We keep having to up token allowances, and those are
right decisions"*). A deletion rule for unverified evidence — the Conductor had over-read e2e, which
deletes a *replay cache entry*, a performance artifact, and keeps every trace, report and screenshot.
Nothing in this spec deletes evidence. A promotion gate requiring a live reproduction before a defect
counts — `CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP` took 314 non-pass runs and a Test Pilot sitting to find
a spawn path that skipped `PostProcessSpawnedPawns`; a gate like that would have made it
unreportable.

---

## Change one: a finding names what else it ruled out

### What is wrong now

`rimflow finding` requires `--from --name --type --severity` (`model.py:517`) and records exactly
those (`cli.py:3185`). Nothing on the record says *why the reporter believes this cause rather than
another one it could see*. The reporter holds that context at the moment it files and holds it nowhere
else: the next reader rebuilds it, or doesn't and acts on a guess.

Red-on-base/green-on-fix, which this project already does, proves a test **discriminates**. It does
not prove the red came from the claimed defect. A test that errors in setup, times out, or trips an
unrelated earlier assertion is red-on-base and green-on-fix and says nothing — a passing grader on a
wrong theory.

### The change

Two optional fields on `rimflow finding`, and one derived line in the record:

- `--ruled-out "<cause>: <the observation that excludes it>"`, repeatable. Free text, one cause per
  flag. No vocabulary, no schema beyond the colon.
- `--red-at "<the assertion or symptom that went red, and where>"`. When the finding came from a test
  that failed, this is *which* check failed, not that one did.

**Neither is required. Nothing is refused for lacking them.** The record grows a field
`discriminated: true|false` — true when at least one `--ruled-out` is present — and the rendered
finding shows the ruled-out list under the finding's own line.

### Why this is not the blocker he refused

The reporter writes one to three short lines from context it already has. It is not asked to run
anything new, take the bridge, or reproduce anything. A finding with no `--ruled-out` files exactly as
it does today. The only consequence of an empty list is that the record says so, where a later reader
can see it — which is the whole point: today the absence of discrimination is invisible and reads like
confidence.

### Token cost

One to three sentences per finding, written from context already in the agent's head, at filing.
`[measured]` on the mechanism (the flags are plain argparse strings; no model call is added anywhere
in `cli.py`). `[guess ~90%]` that the prose costs under 100 output tokens per finding.

### Risks and costs, stated

- **A fabricated ruling-out is worse than none.** "I ruled out X" with no real observation behind it
  is a false statement with a permanent address, and it will read as rigour. Mitigation: the flag's
  own help text demands the *observation*, and the grammar (`cause: observation`) makes an empty
  assertion visibly empty. No checker can verify it; this is an honesty-dependent field and is
  documented as one.
- **Optional fields get skipped.** Likely, at first. Accepted: the field's value is in the records
  that *do* carry it, and in the daily digest being able to say what share of findings discriminated.
  No enforcement is proposed in this version.
- **It cannot catch the case it most wants to.** A reporter that never considered cause X will not
  list X as ruled out. The field records the search that happened, not the one that should have.

### Acceptance test

`src/RimMandrake/rimflow/selftest_finding_discriminated.py` — fails on the base commit (the flags do
not exist; argparse exits 2), passes after. Cases: a finding with two `--ruled-out` flags records both
and `discriminated: true`; a finding with none records `discriminated: false` and is **not** refused
(exit 0); a `--ruled-out` without a colon is still accepted verbatim (no schema enforcement) but the
record marks it `malformed: true` so a reader can see it; `--red-at` is recorded verbatim; the
renderer shows the list. Expected: 6 of 6 pass.

### Where it goes

`src/RimMandrake/rimflow/cli.py` (`cmd_finding`, the parser), `src/RimMandrake/rimflow/model.py`
(the `finding` verb's `opt` tuple, line 517), the finding renderer in `modledger.py`
(`findings_block`, line 1239).

---

## Change two: the rejection bucket, and a named reason

### What is wrong now

A candidate defect becomes a ticket or becomes nothing. There is no record that says *we looked, and
it was seed data* — so the same candidate is re-found, re-investigated and re-dropped, and the cost of
the second look is identical to the first.

e2e's bug bash reports in four tiers: confirmed bugs → **production risks it cannot verify locally**
→ **rejected findings, by reason** → warnings. The reasons are a closed set: explorer limit, local
environment, intended design, seed data.

**The tier that matters most here is the unverifiable one.** On a web app most defects reproduce from a
route; here most need a bridge sitting, so a great deal of real work lands in "cannot verify locally."
Making that a first-class, respectable outcome — rather than an absence — is what keeps change one
from becoming a silencer.

### The change

`rimflow finding --disposition <d>` with a closed set of five:

| disposition | means |
|---|---|
| `confirmed` | a test fails on the reported defect |
| `unverifiable_here` | real, and this seat cannot prove it (needs the bridge, needs his eyes, needs a machine this one is not) |
| `rejected` | looked at, and it is not a defect — with `--because` naming which |
| `warning` | real, outside the current version's scope |
| *(absent)* | the default; records nothing new, behaves as today |

`--because` takes a closed set when `--disposition rejected`: `harness_limit`, `environment`,
`intended_design`, `seed_data`, `stale_dump`, `other` — and `other` requires `--because-why "<text>"`.
A `rejected` with no `--because` is **refused** (exit 2), naming the five values. That refusal is safe
because it only fires on a flag the caller chose to pass.

### Risks and costs, stated

- **`unverifiable_here` becomes a dumping ground.** The honest failure mode: an agent that does not
  want to work a finding marks it unverifiable. Mitigation: the disposition requires naming *what*
  would verify it (`--needs-to-verify "<bridge sitting on X>"`), which is a testable claim a later
  reader can check. Not enforced beyond being required for that one disposition.
- **A closed set will be wrong.** Five reasons will not cover the sixth case. `other` plus a required
  why is the escape hatch, and the set is in one constant, meant to grow.
- **Rejecting is now cheaper to record than to think about.** A real cost. Accepted because the
  alternative — no record at all — is what we have, and it is worse.

### Acceptance test

`src/RimMandrake/rimflow/selftest_finding_disposition.py` — fails on base, passes after. Cases: each
of the five dispositions records; `rejected` without `--because` exits 2 and the message names all six
reasons; `--because other` without `--because-why` exits 2; `unverifiable_here` without
`--needs-to-verify` exits 2; an absent `--disposition` files exactly as today (byte-compare the event
against the pre-change shape, minus new keys); an unknown disposition exits 2. Expected: 9 of 9 pass.

### Where it goes

Same three files as change one, plus the daily digest (`delegated_digest.py`) gaining a
dispositions-by-count line — it is token-blind by construction and counts are all it may show.

---

## Change three: a run's verdict is separate from a run's *informativeness*, and a pipeline fault is neither

This is the change with the most value and the most risk, so it is split in two parts. **Part A is the
one he described as the bane of the project. Part B is the one he agreed was worth building.**

### Part A: a pipeline fault is not a measurement of the mod

#### What is wrong now

His words: *"The current pipeline will say 'Sorry, you failed one of your allotted walk-throughs'
because the game failed to start or some other nonsense."* That is exactly what the code does. A visit
is consumed by anything that started: `retriable()`
(`maturation_dispatch.py:1276`) returns False for a run that *started* and then failed for any reason
other than being killed — `"one that started, or failed any other way, is [the visit's automatic
run]"`. The transient set (`maturation_autonomy.py:60`) is narrow and launch-time only:
`index.lock|is not on origin/main|ingest.lock stayed busy|publish stopped|another ingest/publish
holds|systemd-run did not answer`. A game that fails to load, a missing test file, a wrong mod list, a
model outage mid-run, an uncleaned previous run — all of these started, so all of them spend the
visit and land as a non-pass on the mod.

Three separate things are being conflated into one verdict: **the mod's state**, **the pipeline's
health**, and **this agent's performance**. He named all three.

#### The change

A new module, `src/RimMandrake/rimflow/run_fault.py`, with one function and one closed vocabulary:

```
classify(evidence) -> (kind, why)
  kind: "mod"       the run measured the mod. Counts as a visit. Counts in the streak.
        "pipeline"  the pipeline broke. Does NOT count as a visit, does NOT count in the
                    streak, and FILES A PIPELINE FINDING.
        "unknown"   cannot tell -> treated as "pipeline" and alarmed, never as "mod".
```

Pipeline faults, measured from what has actually happened in this project:

| signature | why it is not the mod |
|---|---|
| the game never reached a loaded map | nothing about the mod was observed |
| a named test file or chain does not exist | the harness is wrong, not the mod |
| the active mod list is not the list the check declared | `build_match.py` already knows this; its verdict is "does not count" |
| the model was unavailable or the provider failed | e2e's own carve-out: *"these say nothing about the app"* |
| a previous run left state this one tripped on | the uncleaned run is the fault |
| the bridge was unreachable or held | no observation was made |
| a known silent-failure engine call was the only evidence | `skills/rimbridge/references/silent-failures.md`: 30+ calls that report success and change nothing |

**`unknown` resolving to `pipeline` is deliberate and is the one place this change is deliberately
unsafe in the generous direction.** A misclassified pipeline fault costs a wasted re-run. A
misclassified mod fault costs a false green on a mod, which is the failure that cost 25-of-65. Given
the choice, the pipeline eats the re-run.

Every `pipeline` classification **files a finding** (`type: pipeline`, the new `--disposition
confirmed` where a test proves it) — which is how "these are valid pipeline findings" (his words)
becomes true rather than aspirational. Per *the pipeline fixes its own defects* (owner, 2026-11-15),
the run that classified it fixes it in the same run where the fix is known.

#### Risks and costs

- **An infinite re-run loop.** If a pipeline fault never consumes a visit and the fault recurs, the
  mod never advances and nothing stops. Mitigation: a pipeline fault consumes nothing *on the mod*
  but increments a per-cause counter; the **third occurrence of the same cause** stops the mod with
  `maturation.pipeline_fault_repeats` and goes to the Conductor. This is a repeat-detector, not a
  budget — it counts identical causes, not spend.
- **Classification is a new place to be wrong.** Accepted, with `unknown → pipeline` as the fail-safe
  direction and every classification recorded with its evidence so a human can audit the call.
- **It will reclassify history as pipeline faults.** Likely a large share of the 659 UNMEASURED. That
  is the point, and it will make the pipeline's measured quality look *worse* before it looks better.
  Say so when it lands.

#### Acceptance test

`src/RimMandrake/rimflow/selftest_run_fault.py` — fails on base (module absent), passes after. One
case per signature in the table above (7), plus: `unknown` evidence classifies `pipeline` and sets
`alarmed: true`; a genuine mod failure (a bar's check ran and returned FAIL on a loaded map with the
declared list) classifies `mod`; a pipeline classification emits a finding event; the third identical
cause returns a stop. Expected: 11 of 11 pass. Run with `--mutants`.

### Part B: informativeness, recorded beside the verdict

#### What is wrong now

The Test Pilot route keys on consecutive non-pass runs — `testpilot_route.py:12`, measured 2026-10-31
over 858 items and 2664 runs: `N=0 .75, 1 .52, 2 .42, 3 .21, 4 .11, 5 or more about .05`. It counts
failures. It does not count whether a failure *taught anything*. An agent failing three times while
producing three new facts is working; one failing three times producing nothing is stuck. Today they
look identical.

His four-way reading, which is the design:

| | informative | non-informative |
|---|---|---|
| **PASS** | the valuable case | *"comforting but uninformative: you wouldn't authorize another one"* |
| **FAIL** | *"real discoveries, findings have why's attached... I certainly would authorize another"* | *"even worse... you certainly shouldn't authorize another of those either"* |

And the fifth case, his: *"if it's producing the SAME insights and somehow returning for a repeat
pass... again that's non-informative overall."*

#### The change

Each run record gains one derived field, computed by a program from what the run already wrote — **no
model, no self-assessment, nothing the agent declares about itself**:

```
informative: true|false
yield: {new_findings, new_whys, repeated_findings, first_time_causes}
```

`informative` is true when the run produced at least one of: a finding not already on the mod, a `why`
on an existing finding that had none, a newly-ruled-out cause (change one), or a first-time cause
classification (part A). It is false when every finding it produced already existed with the same
content — his repeat case.

**This changes one routing predicate and nothing else.** `testpilot_route.py` currently routes on
three consecutive non-pass runs; it will route on **three consecutive non-informative runs**, pass or
fail. A mod producing new facts keeps going past three fails. A mod cycling the same insight goes to a
sitting at three, whatever its verdicts say.

#### Risks and costs

- **Gaming.** An agent that learns `informative` gates its continuation can produce novel-looking
  findings to keep going. This is the serious risk. Three mitigations: the field is **derived, never
  declared**; novelty is measured against the mod's existing findings, so a reworded duplicate does not
  count; and the agent is **not told** the field exists in its brief — consistent with *no launched
  agent is told its spend* (owner, 2026-11-16), for the same reason.
- **Novelty is not value.** A run can produce ten new true-but-useless findings and read as
  informative. Accepted for this version: the measurement is novelty, and the spec says so rather than
  claiming to measure worth.
- **The .21-at-N=3 calibration does not transfer.** It was measured on *non-pass* streaks, not
  *non-informative* streaks. The new predicate is therefore **uncalibrated at landing**, and must be
  recorded as such and re-measured once there are runs under it. It is not a stronger number, it is a
  differently-shaped one.

#### Acceptance test

`src/RimMandrake/rimflow/selftest_run_informative.py` — fails on base, passes after. Cases: a run with
a new finding is informative; a run whose only findings duplicate existing ones is not; a run adding a
`why` to a why-less finding is; a reworded duplicate is not; a PASS with no new facts is
non-informative (his "comforting" case); three consecutive non-informative runs route to a Test Pilot
while three non-pass-but-informative runs do not; the field is absent from every brief
(`grep` the brief builders for the field name, expect zero hits). Expected: 8 of 8 pass.

#### Where it goes

`src/RimMandrake/rimflow/run_informative.py` (new, the derivation),
`src/RimMandrake/rimflow/testpilot_route.py` (the predicate, keeping the old one readable beside it),
the run record writer in `maturation.py`.

---

## What this does NOT touch

No bar. No stage. No model tier. No budget, cap or allowance — his 2026-11-17 ruling stands that the
pipeline is too new to predict them, and nothing here sets one. No agent is told any of these fields.
Nothing deletes evidence. `modcheck`'s `verdict_for()` (`status.py:415`) and its REFUSED/RED/GREEN
ladder are unchanged; part A adds a classification *beside* a verdict, it does not add a verdict value.

## Open question for him, with the obvious answer taken (Evidence-for-Ask, 2026-11-15)

Whether `UNMEASURED` should be **refused by a hook** when it carries no why — he said *"Literally
bounced, maybe even by a hook."* The obvious answer is yes, and it is taken: part A's classification
is what supplies the why, so an UNMEASURED with no classification is refusable once part A lands.
Evidence against doing it as a *hook* specifically: a hook fires before the shell and refuses a
compound command whole, so a hook here would refuse writes that are legitimately mid-sequence. It is
therefore built as a refusal **inside the recorder** (`maturation.py`'s run-record writer and
`modcheck`'s `record_run`), which cannot be bypassed by splitting a command and gives a better
message. Logged `--per-ruling RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME`.
