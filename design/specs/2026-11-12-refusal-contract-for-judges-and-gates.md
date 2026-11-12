# Refusal contract for judges and gates (spec, nothing built)

Item `RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS`. Owner ruling 2026-11-12 14:50 PST, verbatim in the item's
filing event (`infrastructure/state/ledger/events/OWNER.jsonl`, the `file` event of that id). In short: no judge or gate
may refuse forever. A refusal is as detailed as the evidence it rejects. It names attainable fixes and a path to passing,
and it assesses the acceptance criteria. Flawed criteria go at once to a neutral fixer (not the judge, not the builder),
then the item is rejudged. "Nothing could ever pass" calls for swift action. No ceremony loops.
Related rulings the same day (Conductor log, 22:47Z): "One gate, and it refuses" (the evidence gate becomes the one proof
gate, and its flip waits on this spec). Mechanism work is done at stage 4, with his condition: *"Piecemeal revalidation
of specific touched line items is crucial, or converting all steps to very rapid validation passes."*

## 0. What the history says (measured 2026-11-12; scripts and counts in `D:\ClaudeWork\rimmandrake\refusal_contract\PROGRESS.md`)

| Source | Measured |
|---|---|
| Relentless store, `items/*/attempts.jsonl`, 2026-11-01..07 | 813 refusal ends: proof_weak 281, blind_fail 228, unmeasured 123, game_fail 94, close_refused 42, game_unmeasured 18, game_refused 18, proof_unrunnable 9 |
| Marker verdicts (journal acts) | 642 PASS, 627 refusals (weak 278, blind_fail 226, unmeasured 123): **refusal rate 49.4%** |
| Same class refused again at the **same sha** (no new code) | 56 of 813 (7%), of which **52 were UNMEASURED**: the judge could not measure, and said so again on the same evidence |
| Later refusal of the same class with near-identical text (word overlap >= 0.7) | 27 of 212 same-class pairs (game_fail 18) |
| Refusal detail as stored | cut at 600 characters; **687 of 813 hit the cut**. The stored refusal is shorter than the evidence by construction |
| Items by number of refusals, and share later done | 1: 246 (79% done), 2: 134 (63%), 3: 38 (61%), 4: 29 (59%), 5: 11 (36%), 6+: 2 (0%) |
| Ledger holds "N returns and the proof still reads weak" | 83 items, 101 events |
| Marker run cost (`spend-*.json`) | 2,116 check runs, median 173k tokens, p90 320k, 504M tokens in all (work runs 1,323M) |
| Evidence gate in shadow (`evidence_gate.py report`) | whole log: would refuse 78 of 190 judged closes, **73 of the 78 for "no marker"**. The Marker has been stopped since 2026-11-06, so that clause cannot pass for any new close. Since 2026-11-07: 18 closes, 7 rejects, each for no record / no run / no marker |
| Concept floor gate (journal `concept_refused`) | 2,599 refusals on 31 items. The top three were refused 140, 139 and 137 times, each time with the same sentence ("names a mod with no Designer pass on record"). Mechanical, so no tokens, but it refused forever |
| Designer coverage judge, ExplosiveKnockback, 2026-11-12 | **9 refusals (not_covered) in 3 hours** (gaps 19, 14, 11, 6, 9, 7, 6, 4, 4), about 720k tokens per judge run. 15 of the 50 distinct gap ids first appeared after round 1. The whole loop came to about 90M tokens against a 4M cap (Conductor log 11:18Z). The judge's text was detailed and named fixes, so detail alone did not stop the loop |
| Art pipeline `regen_rounds.json` | 92 of 212 defs reached round 3, the cap that escalates; `criteria_ledger.jsonl` has 48 owner-vs-pipeline misses, 29 still OPEN |
| Binding repair proposals (builder proposes, judge rules) | 52 proposals sit unruled in the store |
| Refusals that the judge itself called a criterion fault | UNMEASURED: no judge has ever been asked |
| Token cost of builder reruns caused by refusals | UNMEASURED per refusal; work spend is 1,323M tokens in all |

Every existing loop limit counts the **builder's** tries: Relentless `same_failure_limit` 2 and `unchanged_returns_limit` 9,
Test Pilot after 3 non-pass runs, art regen at 3 rounds then escalate. None of them ever asks whether the criterion can
be met. That is the hole this spec closes.

## 1. The refusal record

A refusal is a JSON record. One record per refused clause; a verdict holds a list of them, plus a `passed` list naming
every clause it accepted. Required fields:

| field | content |
|---|---|
| `clause` | id of the acceptance line refused (exam clause, coverage checklist id, scene cell, art criterion id), plus `criterion_hash` (hash of that clause's text) |
| `evidence` | the evidence line(s) it answers: file path plus line, record id, or crop file name. It must resolve, and it must be one of the inputs the judge was given |
| `observed` | what the evidence shows, quoting at least one token from it |
| `would_pass` | the observable result that would pass this clause, stated concretely enough that a script or a fresh judge could check it |
| `smallest_fix` | the smallest change that reaches `would_pass`: files, defs, scenes or cells named, plus `attainable: yes/no` and its cost class (edit / rerun / new instrument / owner) |
| `criterion_verdict` | `sound`, `flawed` or `unattainable`, plus `criterion_why` (at least one sentence, required whatever the verdict) |
| `new_since` | for any refusal after the first on this item: `unfixed:<prior clause>`, `changed:<input>`, `regression:<clause>`, or `late` (see §3) |

**"As detailed as the evidence"** is checked by coverage, not by length. Every evidence line the judge was given appears in
either `passed` or a refusal's `evidence`. One record per clause means the refusal is exactly as granular as the evidence.
Length is not a test, because padding is easy.

**Mechanical check** (`refusal_contract.py check <verdict.json>`), applied before any refusal has a consequence:
- every required field is present and non-empty, and the enums are valid;
- `evidence` resolves to a given input, and `clause` exists in the criterion set at `criterion_hash`;
- `would_pass` and `smallest_fix` are not on a short ban list of empty phrases ("does not pass", "insufficient",
  "needs more work", "weak", "not convincing" with nothing else), and `would_pass` is not the clause text restated;
- every given evidence line is accounted for (coverage);
- the full record is stored whole (no 600-character cut; the store keeps a pointer).

A verdict that fails the check is **refused itself**. It does not count against the item, the builder is not sent back, and
the judge is re-run once with the check's error list. A second malformed verdict from the same brief marks the brief
FAILED in calibration (§5) and raises the alarm in §3.

## 2. The criteria-repair route

**Trigger.** Any of these sends a clause to repair at once, with no waiting for a human:
- a refusal says `flawed` or `unattainable`;
- the mechanical triggers in §3 fire (the third refusal of a clause, a family refusal rate, a dead producer);
- calibration fails (§5).

The judge's own `sound` never blocks a mechanical trigger. A judge rating its own criteria is the weakest witness.

**Who the neutral fixer is.** A fresh Opus agent (`rm-builder` type with a fixed brief, `roles/criteria_fixer.md`). It is
neither the judge nor the builder of this item, and it has never run on this item before. It is given:
- the clause and its history (criterion text and hashes);
- the owner's words or spec line the clause serves;
- the refusal records;
- the evidence;
- the calibration cases (§5).

It is **not** given the builder's arguments, the item's stakes or priority, or any wording that frames passing as the goal.
Its task reads: "make this clause measure what the source line asks, so that the known-bad case fails and the known-good
case passes". Success is judged by calibration, not by whether the item passes. That removes the pass = success bias.
Opus, because judging whether a criterion is sound takes judgment. Never Haiku. When the clause sits next to an owner bar,
add a GPT second read through `chatgpt-consult`.

**What it may change.**
- **Tighten** a clause: add a control, sharpen a threshold toward stricter, name an object.
- **Clarify** ambiguous wording without changing what passes.
- **Replace** an unmeasurable or unattainable check with one that measures the same property and can be run. Example:
  "newest Marker verdict PASS" while the Marker is stopped, replaced per the owner's D4 card by the mechanical evidence
  the gate can read.
- **Correct a wrong fixture**: an expectation sentence that misdescribes a reference cell, a stale scene, or a wrong
  defName read from the def.

**What it may not change.**
- It may not loosen an owner bar: remove, merge or relax a hash-bound `## north star` line or anything tagged L4
  (`delegation_policy.md` §2 line 1: "Loosening a bar ... stays his"). That goes to him as a card, with the clause, the
  evidence that nothing could pass, and options.
- It may not loosen an agent-written criterion quietly. Removal or relaxation is classed `loosen`. It is allowed only
  when the fixer shows that no owner bar or spec line asks for the property, and a second reader (GPT) agrees.
  Otherwise it becomes a card.

**Mechanical guard** (`refusal_contract.py diffguard old new`):
- classifies each change as tighten / clarify / replace / fixture / loosen, by finding:
  - removed clauses and removed controls;
  - numeric thresholds that moved in the permissive direction;
  - touched north-star hashes;
- refuses any loosen that does not carry the card or second-read reference;
- refuses any repair after which the known-bad calibration case passes.

**Recording.** The repair is a commit to the criterion file (exam, checklist, brief or scene contract) plus one event:
`rimflow note <ITEM> --why "criteria repair <clause>: <class>; refusal <ref>; calibration good=PASS bad=FAIL"`.
Art criteria also append to `infrastructure/state/art_eval/criteria_ledger.jsonl`. An owner-bar card answer is recorded
with `--by-card`.

**Automatic rejudge.** Once the guard is green, the item is rejudged on the same evidence. If the repaired clause needs
evidence that does not exist yet, only that clause goes to the builder (§4). The rejudge uses **the same judge brief in a
fresh instance**, not the instance that refused and not a different brief:
- Same brief, because calibration (§5) certifies the brief, and swapping briefs would re-open everything.
- Fresh instance, because the refusing instance is anchored on its own reading of the old clause.
- The fresh judge does not see the old refusal, which would anchor it the same way.
- If it refuses the repaired clause again, that counts toward §3's limits. A repair is new information, so it earns
  exactly one more look, not a fresh counter.

## 3. Loop limits

| Rule | Number | Tied to |
|---|---|---|
| A clause refused with **no new evidence** (same `clause`, `criterion_hash`, evidence hash and sha) is not judged again. The cached verdict is returned, at no token cost | 2nd refusal is never spent | 56 of 813 store refusals (7%) repeated on the same sha, 52 of them UNMEASURED |
| A first refusal must be complete: every gap the judge can see. A later refusal may cite only an `unfixed`, `changed` or `regression` gap. A `late` gap (on material already judged and unchanged) is allowed, but it does not reset any counter and it is logged as a judge miss in calibration | — | ExplosiveKnockback: 15 of 50 gap ids first appeared after round 1 |
| The **3rd refusal of the same clause** on one item (with new evidence each time) sends the clause to the neutral fixer, whatever the judge's `criterion_verdict` | 3 | owner's `same_failure_limit` 2; the done rate flattens from 63% (2 refusals) to 61% (3) |
| The **4th refusal on one item** (any clauses) raises the alarm, and no further judge run starts on it until the fixer or the Conductor answers | 4 | done rate 59% at 4 refusals, 36% at 5, 0% at 6+ (n = 13 at 5+); EK would have stopped at round 4 of 9 |
| A **family** (one judge brief, or one gate clause across items) refusing more than **70% of its last 20 verdicts**, or 100% of its last 8 across at least 3 items, raises the alarm | 70% / 20; 100% / 8 | [guess ~70%], set above the Marker's measured 49.4%; the shadow gate's "no marker" clause (73 of 78 rejects) and the concept gate (31 items, same sentence) would both have tripped |
| A clause whose **producer has not run in 14 days** (the program that writes the evidence it reads: Marker, testq, modcheck) is unattainable by construction. The gate does not refuse on it; it holds the item as "criterion under repair" and alarms | 14 days | card draft rule 6 (no run in 14 days means deleted or put on a clock); the Marker stopped 2026-11-06 |
| **Judging spend per item:** at most 4 judge runs, or 4x the brief's measured p90 run cost, whichever comes first. After that no new judge run starts, the running one is never killed, and the alarm fires | 4 runs; Marker about 1.3M tokens, coverage judge about 3M | Marker p90 320k; coverage judge about 720k a run; EK spent 5.7M on its 8 measured judge runs (the first is unmeasured) and about 90M in all |
| A fixer may repair the same clause at most twice. A third failure on that clause goes to the owner by card | 2 | [guess] |

**The alarm.** It has one fixed id, `REFUSAL_NOTHING_COULD_EVER_PASS`, routed to the Conductor through
`alarm_routes.json`, with one row per item or family and repeat trips updating the row. It is never a new queue item per
trip. "Swift action" means the alarm itself launches the neutral fixer for the clause it names. The Conductor reads the
result and does not have to start it. While a clause is under repair the item is neither failed nor passed, and no builder
run is spent on it.

## 4. Piecemeal revalidation

- Each acceptance line (exam clause, testq line, scene cell, art criterion) declares its `inputs`: source files or globs,
  defs, scene id, cell id, art files.
- A PASS is stored under the key (line id, criterion hash, inputs hash, game build plus mod-list hash for live lines).
- An objection, whether from a judge refusal or from his look, names line ids (the refusal record's `clause`). The rerun set
  is the objected lines plus every line whose inputs hash changed after the fix. Every other PASS stands, because its key is
  unchanged.
- At the look stage, an objection to one matrix cell re-stages that cell and any cells that share the touched fitting or
  art. The pre-look judges re-judge only those crops.

A whole-suite rerun is needed only when:
- the brief or criterion set changed as a whole;
- the game build or the mod list changed (live lines);
- a line declares no inputs. Such a line always reruns, and gets a ticket to declare them.

A C# change rebuilds the DLL, so lines depend on source files, not on the DLL. A change to a shared core file correctly
reruns every line that reads that file. This is the testq skip-when-unchanged cache, which today answers 0 of 1,583
(inventory §4): fixing that cache is the mechanism, not a new layer.

## 5. Judge calibration

- Every judge brief and every gate clause set has a calibration record, `infrastructure/state/judge_calibration.json`,
  keyed by brief hash. It holds at least one known-good case and at least one known-bad case.
- Known-good cases are owner passes, for example the EK knockback grid ("It looks AWESOME") or incendiary Station 6
  ("Full pass").
- Known-bad cases are owner-caught misses (the "Missed by the judge" table in `scene_look_judge_brief.md`, the art
  `criteria_ledger.jsonl`) or a planted break (`mutate-your-checker`).
- Existing calibration sets count: `evidence_gate_corpus.json` (false and valid closes), the art regression set, and the
  2026-11-12 scene-judge calibration (n=1).
- Status is UNTESTED, CALIBRATED or FAILED. Any edit to a brief resets it to UNTESTED.
- **Only a CALIBRATED brief's refusal has a consequence.** An UNTESTED one may pass or report. Its refusal is stored and
  shown, but the item is not sent back.
- When calibration fails:
  - Refusing the known-good case means the brief goes to the neutral fixer, like a flawed clause. The brief is a
    criterion.
  - Passing the known-bad case means the judge is blind, so its passes are not evidence either. The brief is FAILED, the
    item waits on the fixer, and the alarm fires.
- Re-calibration costs one judge run per case: about 350k tokens for the Marker, about 1.4M for the coverage judge.

## 6. Where it lands, and build tickets (one agent each; listed here, not filed)

Freeze note: the Marker and the rest of `relentless.py` stay untouched under the 2026-11-06 freeze. This contract lives in
rimflow, the Designer, the art pipeline and the judge briefs, and joins Relentless only when the Marker is revived. Its
numbers are constants in `refusal_contract.py`, never keys in `relentless_rules.json`.

1. **T1, stops the live burn first: the Designer coverage loop.** `src/RimMandrake/rimflow/designer_stage.py` and
   `coverage_judge.py`:
   - a 3rd `not_covered` on one concept stops judge launches and raises the alarm;
   - the coverage brief demands a complete first gap list and tags later gaps `unfixed`/`changed`/`late`;
   - judge spend per concept counts toward the cap.
   Selftest replays the nine EK verdicts.
2. **T2: `src/RimMandrake/rimflow/refusal_contract.py`.** Record schema, `check`, the repeat-key cache, per-clause and
   per-item counters, family rate, and the one alarm row in `alarm_routes.json`. Selftest with good, malformed and repeat
   fixtures.
3. **T3: evidence gate, before the flip.** `evidence_gate.py`:
   - reasons become refusal records;
   - the producer-liveness check;
   - the "no marker" clause replaced per the owner's D4 card, as a recorded criteria repair;
   - `corpus check` becomes its calibration.
   Then `EVIDENCE_GATE_FLIP_ENFORCE_AFTER_NOV9` may flip.
4. **T4: judge outputs.** `design/RimMandrake/scene_look_judge_brief.md`, `design/RimMandrake/art_judge_brief.md` and
   the coverage prompt emit refusal records, and their launchers call `refusal_contract.py check`.
5. **T5: neutral fixer.**
   - `src/RimMandrake/rimflow/roles/criteria_fixer.md`;
   - `refusal_contract.py repair` (launch, fixed brief, Opus);
   - `refusal_contract.py diffguard`;
   - the recording path;
   - the automatic fresh-instance rejudge.
6. **T6: calibration registry.** `infrastructure/state/judge_calibration.json`, `refusal_contract.py calibrate`, seeded
   from the existing corpora. An UNTESTED brief's refusals become advisory.
7. **T7: piecemeal revalidation.** Fix the testq skip-when-unchanged cache key (line, criterion hash, inputs hash, build),
   and let lines declare `inputs`.
8. **T8: art pipeline.** `src/RimMandrake/Utils/art_eval/round_series.py`: at the round-3 cap, route to the fixer when a
   criterion is suspect (the 29 OPEN criteria-ledger rows), and send to the owner only for owner bars.
9. **T9: store fixes and the concept gate.** Remove the 600-character cut on stored refusal detail (keep a pointer to the
   whole record), and apply the repeat-key cache to `concept_refused` so the same sentence is not re-issued 140 times.
10. **T10: docs.** Add one line each to CLAUDE.md, `delegation_policy.md` §4, the `rimworld-art-evaluation` and
    `rimworld-live-review` skills, and the `standing_rulings.md` entry for this ruling, and propagate it to every file
    that describes a judge's loop.

## 7. Where I disagree, or see holes

- **A fixer that quietly weakens criteria.** This is the main risk the ruling creates. Safeguards:
  - `diffguard` classifies every change;
  - any loosening goes to a card (owner bar) or a second reader (agent criterion);
  - the known-bad case must still fail after a repair.
  A fixer that cannot meet these does not get a lighter rule. It goes to the owner.
- **"Immediately rejudged" needs one qualifier.** A rejudge with no new evidence is useful only when the repair changed what
  the evidence is judged against. When the repaired clause needs new evidence, it goes to the builder first, for that
  clause only. Otherwise the immediate rejudge is itself a ceremony.
- **Sometimes nothing passes because the work is wrong, not the test.** A fixer that finds the criterion sound turns
  "nothing could ever pass" into a redesign-or-drop decision for the Conductor, under the same alarm. It is still swift,
  but it does not change the criterion.
- **Detail alone did not save us.** The EK coverage judge was detailed and named fixes, and it still ran 9 rounds. The
  limits that matter are the complete-first rule and the clause counters, not the length of the text.
- **The spend cap sits against `TOKEN_LIMITS_TAME_BARK_NO_BITE`** ("Nothing gets killed or stopped"). The cap here never
  kills a run; it only declines to start the next judge run. I read his newer ruling ("judges destroy my account
  uselessly") as covering that, but the Conductor should confirm the reading on the item.
- **The freeze.** This is judging machinery. It is built outside Relentless; Relentless only receives one call site when
  the Marker resumes.
- **The judge's own `criterion_verdict` will mostly read `sound`.** That is UNMEASURED, since no judge has been asked. So
  every trigger that matters is mechanical, and the self-assessment is an extra signal, never the gate.
