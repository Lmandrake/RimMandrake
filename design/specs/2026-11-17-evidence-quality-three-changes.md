# Three changes to how the pipeline records evidence

**Filed** 2026-11-17, ~12:10 PM PST, by the Conductor; revised to 0.2.0 ~1:40 PM PST and to 0.3.0 ~2:50 PM PST after two independent blind reviews, from the owner's conversation of the same
morning (the e2e.com evaluation and his reply to it). Design Version of this spec: **0.3.0** (0.1.0 pre-review; 0.2.0 after the first blind review; 0.3.0 after a second, independent one).

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

## Blind review, 2026-11-17 — what it changed (Design Version 0.2.0)

A blind Opus review (fresh agent, given the code and not this writer's confidence) found nine
defects. Every load-bearing claim below was re-checked against the code by the Conductor before it
was accepted. **It killed Part B, rerouted change one, and found that Part A's named change site was
the wrong function.** The order of work is now: change two → change one → Part A → (Part B not in
this version).

**Accepted, verified, and now binding on this spec:**

1. 🔴 **Change one as written wrote to a store nothing reads.** `model._apply` keeps exactly four
   fields on a finding — `{"from", "type", "severity", "at"}` (`model.py:2763`). `--ruled-out`,
   `--red-at` and `discriminated` would land in the shard and be **dropped at every replay**, and
   the renderer this spec named (`modledger.py:1239` `findings_block`) belongs to a *different*
   ledger, fed by `modledger append --kind finding.open`. [measured — read both call sites]
2. 🔴 **Change one reinvents an existing, stricter, and already-verifiable checker.**
   `relentless_explain.validate()` already **requires** ruled-out causes as `theory :: why_not`
   pairs through `_pairs()` (`relentless_explain.py:59-70`): both sides present, minimum length, no
   unfilled placeholder, empty list refused. The proposed grammar was weaker (one colon, no minimum,
   `malformed: true` instead of a refusal) with a different separator. **And the "no checker can
   verify it" premise was wrong**: `cmd_spawn` already refuses a cause that resolves to nothing —
   *"a cause that resolves to nothing is not one"* (`cli.py:3211`) — and `modledger.check_entry`
   already requires evidence as a typed reference (`path:…#row`, `run:<id>`, `test:<id>`) and
   refuses pasted logs (`modledger.py:320-330`). Requiring one typed reference in the observation
   half makes the field machine-checkable for ~zero tokens.
   **Where the review was wrong, and the correction:** it recommended extending `relentless_explain`.
   That module is only reachable from `relentless.py`, which the owner **retired 2026-11-13** with
   *"nothing to resume"* (`design/RimMandrake/retired_loops_2026-11-13.md`), and nothing in `cli.py`
   imports it [measured — no non-selftest importer outside the three `relentless_*` files]. So its
   **grammar and its `_pairs` validator are lifted** into the live path rather than extended in
   place; a retired module is not a home for new work.
3. 🔴 **Part B's central mitigation is decorative.** `testpilot_route.brief()` prints
   `"Routed by the Test Pilot rule: %s" % verdict["why"]` (`testpilot_route.py:170`), and `judge()`
   builds that `why` from the predicate itself (`:124`). Change the predicate and the brief hands
   the agent the sentence *"3 non-informative runs in a row."* The proposed acceptance test — grep
   the brief builders for the field name — **would have passed while the information leaked**,
   because the leak is the derived prose, not the identifier. A test calibrated to the mitigation's
   wording instead of its claim is exactly the "passing grader on a wrong theory" this spec was
   written about. [measured]
4. 🔴 **Part A and Part B contradicted each other.** Part A excluded pipeline faults from the streak
   *and* filed findings for them; Part B counted a new finding as yield. So every novel pipeline
   fault would reset the non-informative counter, holding the Test Pilot off precisely the mods
   breaking most. Both could not stand.
5. 🔴 **`unknown → pipeline` misclassified the worst real defect class.** For a RimWorld mod, *"the
   game fails to load"* is the most severe genuine mod defect (a malformed def, a bad `MayRequire`, a
   static-constructor exception). The table's first row booked it against the harness. The fix is to
   split that signature on **whether the declared mod list was active at the failure** —
   `build_match.judge_row` already carries that discriminator (`build_match.py:433-448`) — and a load
   failure with the mod active is `mod`, full stop.
6. 🔴 **Part A named the wrong function.** Visit consumption is not `retriable()`; it is
   `launch_counted` (`maturation_dispatch.py:1673-1704`, one book entry per visit), the two `per`
   gates (`:1438` blind, `:1541` in-game), and the `if mine and not retry` terminals (`:1428`,
   `:1535`). None were listed. Also unlisted: `AUT.releasable`, `reserve_refused`, and
   `maturation_autonomy.TRANSIENT/NEVER_TRANSIENT` — a **second** fault vocabulary that already
   overlaps this one, whose `NEVER_TRANSIENT` exists because that overlap bit once already
   (`RIMMANDRAKE_UNSTICK_DISPATCH_CLONE_PUBLISH_LINT_REFUSES_HEAD`). Two classifiers will reproduce it;
   Part A extends the existing vocabulary rather than adding a rival.
7. 🔴 **This spec overstated its own motivating defect.** *"All of them spend the visit and land as a
   non-pass on the mod"* is half wrong. The mod's verdict is derived separately by `read_ingame_exit`
   (`maturation.py:2639`); a game that never loaded writes no rows, so it reads `no_exit_block` →
   `visit_unfinished` → *"nothing launches: the Conductor reads it"* (`maturation_dispatch.py:1526`).
   That is a **park, not a false non-pass**. The real harm is the spent automatic launch plus a hand
   step — smaller than claimed. [measured] A spec that overstates its motivation gets built to the
   wrong size, so: **try `testpilot_route.NOT_A_TEST` first** (`testpilot_route.py:42`), which already
   exists for *"runs that are not tests of the item"*, and measure whether one tuple entry closes most
   of the complaint before building a classifier.
8. **The repeat-detector had no comparison defined**, and all three obvious ones break (verbatim
   `why` carries unit ids and never matches; `kind` has 7 buckets so three unrelated faults stop a
   mod). Resolved by reuse, found independently before the review landed: **`findings_fold.row_key()`
   / `signature()`** (`src/RimMandrake/Utils/findings_fold.py:107-115`) is a tested exact-signature
   comparator stripping only job ids, timestamps and durations, with its doctrine written down —
   *"A duplicate row is cheap; a wrong merge loses a bug."* `findings_fold_rules.json`'s
   `machine_health_patterns` is already Part A's idea in production, routing a machine fault to
   Operations instead of the mod. **Measured 2026-11-17: no file under `src/RimMandrake/rimflow/` or
   `Utils/modcheck/` reads either.** Both are reused, not reinvented. The counter's home and reset
   rule must be stated before Part A is built (the visit books are keyed `version#visit` and released
   wholesale by `clear`, so a counter living there resets with them).
9. **The "obvious answer" on refusing a why-less UNMEASURED fixes the wrong layer.** UNMEASURED is
   mostly **derived, not written**: `status.step4_live` returns it for a *missing* record
   (`status.py:619-628`), `read_ingame_exit` derives `absent`/`no_exit_block`, `maturation_convergence`
   returns it for "no measured round". A refusal inside `record_run` reaches none of those. **Before
   building that refusal, measure what share of the 659 historical UNMEASURED rows were explicitly
   written rather than derived.** Unmeasured today; stated as the prerequisite rather than guessed.
   Related: `verdict_for` being untouched means Part A could create two instruments that disagree
   about one mod, against `status.py:674`'s own standing rule — *"A summary must never be able to
   disagree with the detail it summarises."*

**Also accepted:** both changes' new fields need a `model._apply` change plus the strict-write and
tolerant-read paths (`model.py:964`, `:3077`); change two's vocabulary should live beside
`modledger`'s existing closed sets (`modledger.py:350`) and relate to its `verified|withdrawn`
statuses rather than forming a sixth parallel vocabulary; novelty-by-finding-name is free to game
because `modledger._finding_name_ok` requires a freshly minted name per finding (`:240-250`); and
`bar_rule.split` routes tuning/variant gaps to advisory so a correctly-behaving mod could read
non-informative and burn a sitting. Concurrency is unaddressed: several helpers share one tree and
one index, and both the per-cause counter and "novel against existing findings" are
read-modify-write on shared state — so the derivation runs once, after the fact, by a single reader.

**One live demonstration, fixed in the same session** (*the pipeline fixes its own defects*, owner
2026-11-15): `selftest_maturation_dispatch.py`'s in-game block was red 12-of-12 on this machine
because it asked the real `companion_current()`, which reads the deployed JawaBench DLL under the
Windows game folder — absent anywhere but the game host. A filed item claimed **one** failing check;
twelve were measured. That is this spec's Part A in miniature: a reading of the test machine,
reported as a verdict on the pipeline. Fixed by a `companion` stand-in beside the existing `bridge`
one, plus a new check that hands it a STALE reading and watches the launch refuse, so the stand-in
cannot become a bypass. `selftest_mod_owner_hold.py`'s fsync-order spy had the same disease: it
probed `/proc/self/fd`, which exists only on Linux, so every fd read False on a Mac and the check
reported FAIL having measured nothing. Both green, published `165b38afa4a1`.

---

## Second blind review (independent GPT, no knowledge of the first) — Design Version 0.3.0

A second reviewer, given the proposal, the live process doc, ten open tickets and the code — and
deliberately **not** shown the first review — found nine things. Three overturn decisions this spec
had already made, and two of those correct **this writer**, not the spec's critics. Verified against
the code before acceptance.

1. 🔴 **The typed-reference premise is WRONG, and the precedent I cited does not do what I said.**
   `cmd_spawn` does **not** verify a run exists: `known = (args.from_ in w.items or args.from_ in
   w.findings or model.RUN_RE.match(args.from_ or ""))` — `RUN_RE` is a **regex on the shape of the
   name** (`model.py:435`), so any syntactically valid `FOO/run-3@full-578` passes however fictional
   (`cli.py:3211`). [measured] 0.2.0 claimed this as the proof that a reference "either resolves or
   it does not." It does not. So change one must **implement** resolution rather than cite it, and
   until it does, `discriminated: true` is a label asserting something unchecked.
2. 🔴 **`discriminated` is the wrong NAME, and the name is the defect.** What the field can honestly
   record is that the reporter *wrote down an alternative* — not that the alternative was excluded,
   not that the cause was isolated, not that the red assertion concerned that cause. Renamed
   **`alternatives_recorded`**, with reference resolution tracked as its own separate field. A field
   called `discriminated` would make the next reader *less* careful than no field at all, which is
   the opposite of the point. Same for `--red-at`: it is the reporter's assertion until something
   links it to the recorded failure.
3. 🔴 **Part A conflates two different questions**, and this is the deepest finding in either
   review: *"Classify whether a MEASUREMENT WAS VALID separately from WHICH COMPONENT caused the
   failure."* A missing test file may be a builder's omitted deliverable; a wrong mod list may be an
   undeclared dependency; leftover state may be a real persistence defect in the mod. Part A's
   signature table answers "who is at fault" using evidence that can only answer "was anything
   observed." The rebuild: a run carries **`observed: yes|no`** (did this run measure the mod at
   all) and, separately and only on positive evidence, **`owner: mod|pipeline|unknown`**. `unknown`
   keeps the existing escalation rather than suppressing it. No signature may assign ownership
   without causal evidence.
4. 🔴 **My asymmetry argument was also wrong.** 0.1.0 said a misclassified mod fault "costs a false
   green." It does not: `verdict_for` is untouched, so excluding a run from a streak **delays
   diagnosis and escalation** — it does not turn anything green (`status.py:415-450`). The real cost
   is slower escalation on the mods breaking worst. The honest framing, now in the spec.
5. 🔴 **Part A is a POLICY change presented as a records change.** The live process gives each blind
   and in-game visit **one** automatic run and sends every ended visit to the Conductor (PROCESS §5,
   Dispatch). Letting a pipeline-classified run not consume its visit authorises **additional
   automatic attempts** — exactly the automation the owner bounded on 2026-11-14 (*"As long as we
   don't have automated loops rejecting/cycling things, we can't get into too much trouble."*). It
   needs his word, not a spec's assertion that nothing policy-level changed. Also: removing runs from
   the streak changes the population the `.21`-at-N=3 calibration was measured on, so **Part A
   inherits the same calibration caveat** this spec only wrote down for Part B.
6. **The repeat-detector's reuse was a half-answer.** `findings_fold.signature()` hashes the tuple it
   is given; it does not discover semantic equivalence, and its tuple (mod, chain, row, normalised
   text) can split one shared infrastructure cause across several checks or merge different causes
   that share a symptom. Needed instead: a structured incident identity (affected component, stable
   failure code, the evidence for the cause), counting **distinct attempts** rather than repeated
   ingestion of one run, with scope, reset-after-repair and cross-version rules stated. And
   `classify(evidence) -> (kind, why)` is the wrong shape: a pure function cannot count repeats, file
   findings or raise alarms. Classification separates from the orchestration that acts on it.
7. **Concurrency is a threat to the evidence, not just a race.** Several agents share one working
   tree **and one git index**: a red-then-green comparison can be invalidated between its two runs,
   one agent can stage another's files, and a patch reversal can undo another's work. Two existing
   tickets already record this class of loss (`RIMMANDRAKE_UNFENCE_LIVE_HOLDER_WHEN_RIVAL_NEVER_STARTED`,
   `RIMMANDRAKE_HOLD_TICK_LAUNCHES_ON_STALE_CLONE_GHOST_STEWARD`). Mod leases do not serialise edits
   to shared pipeline code. Repairs need an isolated index, and evidence must bind to the tested commit.
8. **Neither change one nor change two names an operational CONSUMER, so neither yet saves work.**
   A recorded rejection cannot spare the next investigator unless the next investigator is *handed*
   it: change two specifies no candidate identity, retrieval step, expiry or reconsideration
   trigger. And the consumer probably already exists — `testpilot_route`'s surprise/explain-away
   machinery already remembers explained observations, retires recurring ones and revives real bugs
   (`testpilot_route.py:1-50`). **Extend that instead of building a parallel rejection archive.**
   Corollary accepted: *"Hiding a continuation metric is different from hiding diagnostic context"* —
   this spec's "no agent is told these fields" was too broad. Reporters must be told how to fill them.
9. **The UNMEASURED migration manufactures causes from missing evidence.** The 659 rows need
   distinguishing as never attempted / incomplete attempt / missing record / unknown provenance —
   absence is not evidence of an infrastructure failure. Strict requirements for *new* attempts,
   tolerant historical reads, append-only corrections carrying the classifier version. Also
   [measured by the reviewer, worth repeating]: **the quoted 195 + 134 + 659 accounts for 988 of
   1363 rows — 375 are unexplained**, and no revised quality percentage should be published until
   they are identified.

**Order, from this review:** corrected **Part A first** (it alone changes an expensive decision —
whether to spend another attempt and when to escalate); change one small, honestly labelled, with a
consumer; **change two NOT as a separate subsystem.** Before any of it, the cheapest interventions
that use machinery already present: wire `RC.submit`
(`RIMMANDRAKE_COUNT_ADVANCE_REFUSALS_SO_A_LOOP_RINGS` — refusals are checked today and never
counted), and note that **`TESTPILOT_WANTED` already routes a defect straight to a sitting with no
three-failure wait** (`testpilot_route.py:125`) [measured]. Then the trust-the-evidence tickets:
stale-clone decisions, live-holder fencing, blind-judge write permission, build-identity capture, the
red coverage selftest, and Stage 3's missing "behaviour built" signal — *"preventing unbuilt behaviour
from reaching live testing saves more than annotating the resulting failure."*

**Where the two reviews agree** (independently, which is the strongest signal in the pair): the
"game never reached a loaded map" signature is wrong; the new fields do not survive `model._apply`;
Part A's named change sites are insufficient and must include `decide_ingame`'s terminals and
`testpilot_route.judge`; the repeat-detector needs a defined identity and lifetime; the UNMEASURED
refusal targets a derived value; and `_pairs` rejecting an empty list must be adapted for an optional
flag. **Where they differ:** the first called Part B gameable and deferred it (kept); the second
reached Part A's ownership model, the policy-change framing, and the missing consumer, which the
first did not. Neither has been implemented; both now gate the build.

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

**Revised at 0.2.0** (review findings 1 and 2). Two optional fields on `rimflow finding`, and one
derived line in the record:

- `--ruled-out "<theory> :: <why_not>"`, repeatable. The grammar and validator are **lifted from
  `relentless_explain._pairs`** (`relentless_explain.py:59-70`): the `::` separator, both sides
  present, each at least 4 characters, no unfilled `<placeholder>`. Not a new vocabulary — the same
  one, moved out of a retired module into the live path.
- The `why_not` half must carry **one typed evidence reference** in `modledger.check_entry`'s
  existing grammar (`path:…#row`, `run:<id>`, `test:<id>`; `modledger.py:320-330`). 🔴 **Resolution
  must be IMPLEMENTED here, not inherited.** 0.2.0 cited `cmd_spawn` as precedent; measured
  2026-11-17, `cmd_spawn` only regex-matches the SHAPE of a run name (`model.RUN_RE`, `model.py:435`)
  and never checks the run exists, so any well-formed fictional id passes (`cli.py:3211`). Until this
  tool resolves the reference itself, the field records a citation, not a check.
- `--red-at "<which assertion went red, and where>"`. When the finding came from a failing test,
  this is *which* check failed, not that one did.

**Neither flag is required. Nothing is refused for lacking them.** But a `--ruled-out` that IS
passed must parse and its reference must resolve — a malformed one is refused, not stored with a
`malformed: true` flag as 0.1.0 proposed. A field that records its own brokenness is a rigour signal
that lies.

The record grows **`alternatives_recorded: true|false`** — renamed at 0.3.0 from `discriminated`,
which asserted something nothing verifies. Reference resolution is a separate field, so a reader can
tell "an alternative was written down" from "its evidence resolves".

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
  is a false statement with a permanent address, and it will read as rigour. **Partly closed at
  0.2.0**: the typed reference must resolve, so an invented `run:<id>` or a `path:` that is not
  there is refused. What remains unverifiable is whether a resolving reference actually *supports*
  the claim — a real run id can be cited beside a theory it says nothing about. That residue is
  honesty-dependent and is documented as such; it is strictly smaller than 0.1.0's, which could not
  check anything at all.
- **Optional fields get skipped.** Likely, at first. Accepted: the field's value is in the records
  that *do* carry it, and in the daily digest being able to say what share of findings discriminated.
  No enforcement is proposed in this version.
- **It cannot catch the case it most wants to.** A reporter that never considered cause X will not
  list X as ruled out. The field records the search that happened, not the one that should have.

### Acceptance test

`src/RimMandrake/rimflow/selftest_finding_discriminated.py` — fails on the base commit (the flags do
not exist; argparse exits 2), passes after. Cases: a finding with two valid `--ruled-out` flags
records both and `discriminated: true`; a finding with none records `discriminated: false` and is
**not** refused (exit 0); a `--ruled-out` missing `::` exits 2; one whose `why_not` carries no typed
reference exits 2; one citing a `run:<id>` that resolves to nothing exits 2; an unfilled
`<placeholder>` exits 2; `--red-at` is recorded verbatim; **the fields survive a ledger replay**
(write, re-read through `model.load()`, assert they are still there — the check 0.1.0 lacked, which
is why it would have shipped a store nothing reads). Expected: 8 of 8 pass.

### Where it goes

`src/RimMandrake/rimflow/cli.py` (`cmd_finding`, the parser), `src/RimMandrake/rimflow/model.py` —
the `finding` verb's `opt` tuple (line 517) **and `_apply`'s finding branch (line 2763), which keeps
only four fields today**, plus the strict-write and tolerant-read paths (`:964`, `:3077`). The
grammar and validator are lifted from `relentless_explain.py:59-70` (retired module; see review
finding 2). Renderer: whichever ledger actually stores it — `modledger.findings_block` (`:1239`)
reads `finding.open` entries, a different store from `rimflow finding`, so the renderer follows the
chosen store rather than being assumed.

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

Same files as change one, including `model._apply` (review finding 1). **Open at 0.2.0, to settle
before building:** whether the disposition lives on `rimflow finding` or beside `modledger`'s
existing closed sets for `finding.open` (`modledger.py:350`), which already carry `class` and
`how_checked` and already have `verified|withdrawn` statuses (`:1050`). If it goes in `modledger`,
`rejected` must relate to those two rather than forming a sixth parallel vocabulary. Plus the daily
digest (`delegated_digest.py`) gaining a dispositions-by-count line — token-blind by construction,
so counts are all it may show.

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

### Part B: informativeness — NOT BUILT IN THIS VERSION (0.2.0)

🔴 **Withdrawn from this version by the blind review, and the Conductor agrees.** His four-way
reading is right and is kept below verbatim as the design to return to. What was wrong was this
spec's way of measuring it: uncalibrated by its own admission, contradicting Part A (review finding
4), gameable by construction because `modledger._finding_name_ok` mints a fresh name per finding,
its central mitigation printing itself into the brief (finding 3), and its "same insight" comparator
undefined. The review's verdict, which this writer accepts: *"measuring it with undefined novelty
against an uncalibrated threshold that gates continuation is the worst version of being right."*

It returns when three things exist, in this order: Part A has landed (so a pipeline fault is already
out of the yield numerator); the novelty comparator is `findings_fold.signature()` rather than
something new; and there are enough runs under the new predicate to calibrate it the way the
non-pass streak was calibrated (858 items, 2664 runs, 2026-10-31). Until then the Test Pilot keeps
routing on consecutive non-pass runs, which is calibrated.

The design to return to, unchanged:

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
