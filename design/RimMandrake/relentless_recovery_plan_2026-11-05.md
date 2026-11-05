# Relentless recovery plan, 2026-11-05: second read of the GPT review, and a ranked plan

Inputs: the failure catalog `design/RimMandrake/relentless_failure_catalog_2026-11-05.md` (classes a-p, lessons q1-q7,
roots 1-8) and the raw GPT answers `design/RimMandrake/relentless_failure_review_gpt_2026-11-05.gpt_read.md`
(consults A, B and C, gpt-6.1-sol at high effort, files inlined). GPT's answer is guidance, never authority. Every
verdict below was checked against the source at HEAD 46c7af61ac. Where I name a line, I read it.

The owner's ask (2026-11-05, filed with each item as `--owner-said`): document the strange error conditions, send them
to GPT for a skeptical review, and make Operations and the Conductor much better at recovering after a major event and
at arbitrating the semi-defective items such an event leaves behind.

## 1. My verdicts on GPT's claims

### Consult A: structure, Judges, gates, contracts

| # | GPT claim | Verdict | Grounds in the code |
|---|---|---|---|
| A1 | A `--defect` label decides FAIL without proving that the instrument worked or that the target caused the failure. | AGREE | `relentless_wall.read_as` l.528-529 returns FAIL on any non-empty `defects`. Nothing checks that the defect locates the candidate. Class d is this. |
| A2 | Structured WEAK with GAP:OTHER and non-empty `unreached` becomes PASS. | AGREE, BLOCKER | l.530 tests only `("PASS","FAIL",UNMEASURED)` before `unreached`. WEAK falls through to `acted_weak`, and GAP:OTHER narrows to PASS (l.546-551). A Judge that could not reach the evidence can therefore close an item. It is a one-line fix. |
| A3 | `check_backlog_max` and the degraded pause come before any per-item relevance check. | AGREE | `lease` l.4821-4845 returns on the backlog before it looks at any item. `content_paused` l.3655-3662 counts a queued system item even when that item cannot launch for another reason (a game hold, or pending help). |
| A4 | `live_reading` folds a reader exception into "DOES NOT HOLD". | AGREE, minor | `relentless_reach.py` l.141-145 sets `holds=False`, and `why` carries the exception text, so the Marker can read it. The state is still two-valued, and the Marker is told never to call it unreached (l.162-164). |
| A5 | `unhold()` clears `blind`, and any offbox entry bypasses the reach checks. | AGREE on unhold, UNSURE on offbox | `blind_back` sets `st["blind"]=None` at l.1224, so my catalog was wrong to say that an unhold keeps the blindness (now corrected). I did not re-read whether offbox matching is too broad. |
| A6 | A machine ticket's source failure is not an enforceable acceptance boundary. | AGREE | `testq/ingest.py` l.216-219 files a title only. Already filed as TESTQ_REPAIR_FIX_TICKETS_NAME_THEIR_PASS. |
| A7 | Quarantine corrects by prose and never recomputes a ticket's support. | AGREE | l.380-404 writes notes ("drop this item if no sighting outside...") and does nothing else. This is catalog class i. |
| A-root | Missed root: conclusions outlive the evidence that authorized them. | AGREE | It joins A5, A7, catalog class e (stale showings) and class p (answered holds): a decision stays in force after the reading or question behind it changed. I adopt it as root 9. |
| A-catalog | Cause routing is not absent, the Judge prompt does ask about an easier contract, and the Steve gate is not wholly retroactive. | AGREE | My wording was too broad. The routes exist (`relentless.py` l.355-382, `relentless_game.py` l.1056-1071), but they are keyed on the verdict word and the Judge's own tags, not on a validated cause. The Judge does read for easier contracts (`relentless_wall.py` l.26-28), but it has no authoritative source contract to compare against. |
| A-Q3 | Classify each obligation as PRODUCT, MEASUREMENT, ENVIRONMENT or UNKNOWN. Only a validated PRODUCT defect may go back to a builder or count a strike. | AGREE | This is the answer to the owner's "throwing things back to fix without fixing the measurement". UNKNOWN must never route to a builder. |
| A-Q4 | Scope every gate by a cause key and its affected dependencies. A timer may buy one probe, never a reopening. | AGREE in principle | Cost is high; see step 8. |
| A-Q7 | The filer owns the ticket contract. A Judge refuses a proposed pass unless it detects the original fault fixture and catches a re-injected fault (a negative control). | AGREE | This matches the hand-written SITE_QUIET spec (4100c595ae). It folds into TESTQ_REPAIR_FIX_TICKETS_NAME_THEIR_PASS and step 5. |

### Consult B: recovery, ownership, alarms, cheapest first

| # | GPT claim | Verdict | Grounds in the code |
|---|---|---|---|
| B1 | Unusable health rules produce `healthy`. | AGREE, BLOCKER | `ops_health.verdict` l.270-274 sets `b={}` when `probs` is non-empty, so `spent=[]` gives `state="healthy"` and `content_paused` False. A broken instrument reads as green (root 1). |
| B2 | Every open system item counts toward the pause, not just repairs of the spent SLIs. | AGREE | `system_items` l.244-253 classifies on the id's words. Nothing ties an item to `infra_share` or `nightly_reds`. |
| B3 | An OPEN alarm whose ticket was closed, with the reading unchanged, never reopens. | AGREE | `ops_watch.py` l.3646-3657 returns when there is nothing fresh and nothing worse, before it checks whether the item is open. Closing the ticket silences an unfixed fault. |
| B4 | A corrupt alarm state returns before any alarm is processed. | UNSURE | GPT points at l.3564-3573. I did not re-read it. It is folded into step 3's tests. |
| B5 | Quarantine retracts by prose. | AGREE | Same as A7. |
| B6 | Machine repair tickets go to FOUNDRY for FlowWorks. | AGREE | `ingest.py` l.217 hard-codes "FOUNDRY". FOUNDRY is retired (standing ruling), so these tickets land on a seat that builds nothing. |
| B7 | Churn uses a recent trigger with lifetime counts. | UNSURE | `churn_blind` l.2052-2063 does as described, but I did not check whether the caller already windows the rows. Left as a note on CHURN_WATCH_BUILD_NAMES_EVERY_BOUNCER. |
| B8 | The health verdict carries no rules or collector revision. | AGREE, with evidence | `health.json` at 04:52Z lists SELFTEST_SOURCE_POLISH_STALE_SEVENTY_SUITES in `system_items`. `ops_watch_rules.json` lists it in `health.not_system`, it is absent from `system_rank`, and `is_system` l.231 would refuse it. The verdict therefore ran on rules other than HEAD's, and nothing in it says which. |
| B-catalog | The phantom spend did not cause this pause: `returned_tokens_pct` is not spent. | AGREE | At 04:52Z only `infra_share` and `nightly_reds` were spent; `returned_tokens_pct` showed 21 bad h and was not spent. I corrected the catalog. |
| B-catalog | 155 system items does not prove a permanent pause. | AGREE | 155 is the classifier's list. The pause counts only queued items that are not on a clock wait and not refused. I corrected the catalog and did not count how many qualify. |
| B-Q2 | Recovery runs per incident: QUARANTINE, RECONCILE, VERIFY, RAMP, NORMAL, with a STALLED exit. Each sighting is classed drop, merge, park or keep. | AGREE, with one change | Too heavy to build first. The cheap core is sighting-level validity (step 6) plus the incident record. A "park" must carry a wake condition, and the STALLED age alarm keeps a park from becoming the next silent hold. |
| B-Q5 | Operations owns measurement validity, source recovery, circuits and alarm delivery. The Conductor owns arbitration and the owner's decisions. Neither marks its own repair accepted. | AGREE | This fits roles/operations.md and roles/conductor.md. The gap is in applying it, not in the role split. |
| B-Q6 | Order: health validity, then alarm reopen, then retry barriers, then accounting, then quarantine, then templates, then scoped pause, then recovery mode. | MOSTLY AGREE | I put A2 first because it is a one-line fix to a false close. |
| B-pause | Scope the pause with a global fallback. A fresh owner ruling raises priority but must not certify a broken measurement path. | AGREE | See section 3. |

### Consult C: answered owner holds

| # | GPT claim | Verdict | Grounds in the code |
|---|---|---|---|
| C1 | A hold must name a question key, and an answer must cite that key. A title or timestamp match is not enough. | AGREE | The hold dict at l.764-770 is `{why, kind, delivered, at}`, with prose only. |
| C2 | Do not release by calling `unhold()` blindly: it re-queues, grants spend grace and sets `needs_back`. | AGREE | Seen at l.1229-1233. Release should go through one path that records which answer it consumed. |
| C3 | An answer that lands during `stopping` must survive until the worker reaches `held`. Reconcile on every tick, not just when an answer arrives. | AGREE | `unhold` accepts only "held" (l.1174-1177). |
| C4 | A legacy prose-only hold raises a migration alarm and is never guess-matched. | AGREE | It is the cheap first slice. |
| C5 | A Conductor-written decision cannot discharge an owner-only hold. | DISAGREE | The standing ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM (2026-10-30) makes a Conductor ruling recorded `--per-ruling` an answer. A builder's word still is not one. |
| C6 | `hold_is_his` classifies a hold but does not enforce who may lift it. | AGREE, minor | This is noted, not a step. |

## 2. Ranked plan (value per cost)

Each step lists what it changes, how it is proven, and which ruling it touches. "Filed" gives the rimflow item id; all
are `--for BENCH`, needs offline, with ids that the health classifier reads as system work (subject word `CHECKER`, `OPS_`,
`RELENTLESS` or `TESTQ`), so Relentless places them ahead of content.

1. **A walled Judge that could not reach its evidence can no longer close an item.** Filed CHECKER_WEAK_FIX_UNREACHED_READ_AS_PASS.
   - Changes: `relentless_wall.read_as` l.530 tests `unreached` before `acted_weak` for every verdict word, WEAK included.
   - Proof: a selftest table of every word (PASS, FAIL, WEAK GAP:DIFF, WEAK GAP:OTHER, untagged WEAK, UNMEASURED) against
     a non-empty `unreached`. Each must give UNMEASURED, and no case may give PASS. Also a replay over attempts.jsonl
     counting past closes that this rule would have refused. The result goes on the item, and it is not zero until a
     probe shows the instrument can see.
   - Ruling: keeps the owner's "Narrow it now" WEAK ruling (2026-11-03) intact; this step only adds unreached precedence.
2. **Broken health rules read UNMEASURED, not healthy, and every verdict names its inputs.** Filed OPS_HEALTH_FIX_BROKEN_RULES_READ_HEALTHY.
   - Changes: `ops_health.verdict` publishes `state: unmeasured` when `probs` is non-empty. The verdict stamps the rules
     sha256, the collector's git sha and the ledger watermark. Relentless reads `unmeasured` as "assessment broken": it
     places the measurement repair first and does not count it as healthy.
   - Proof: three selftests (unusable rules, missing ledger, pinned-input replay that must be byte-identical). Then
     explain the SELFTEST_SOURCE_POLISH mismatch (B8) from the new stamp.
   - Ruling: touches health_order ("I want it to ask the system for its health assessment"). It honours that ruling
     more strictly, so it does not need him.
3. **Closing an alarm's ticket cannot silence an unfixed fault.** Filed OPS_ALARM_FIX_CLOSED_TICKET_SILENCES_FAULT.
   - Changes: in `ops_watch.run_alarms`, an OPEN alarm whose item is closed while its reading is still crossed reopens,
     before the "nothing new" return at l.3656. Also check B4 (corrupt state returns early) and give it one fixed
     incident.
   - Proof: a selftest of file the alarm, close the item, keep the reading, expect a reopen. Then a corrupt-state test.
   - Ruling: none.
4. **An answered question releases the holds waiting on it.** Filed RELENTLESS_HOLD_BUILD_RELEASE_ON_ANSWER (class p).
   - Changes: an `owner_call` hold records a `question_id`. The card, ruling or `--per-ruling` answer cites it. Each tick
     reconciles matched answers into a recorded release (resume, or re-plan with the ruling attached) under Store.lock,
     fenced on `hold_id`.
   - Legacy prose holds: listed by an alarm as "unmatchable, needs the Conductor", never guess-matched.
   - Proof: consult C's tests, minus C5. A Conductor ruling counts as an answer.
   - Order: build after RELENTLESS_HOLD_BUILD_A_VERB_FOR_CONDUCTOR, which supplies the hold path.
   - Ruling: CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM decides who may answer. It does not need him.
5. **The Judge names the cause before anything goes back to a builder.** Filed CHECKER_VERDICT_BUILD_CAUSE_BEFORE_RETURN.
   - Changes: verdict files carry `cause: product|measurement|environment|unknown` for each defect. `fail()` refuses a
     return or a strike unless the cause is product, the defect cites the candidate's diff or behaviour, and the
     instrument passed its control.
   - Other classes: measurement goes to reach or contract repair on the same sha; environment goes to an Operations
     incident keyed on the dependency; unknown waits for diagnosis and never goes to a builder.
   - `relentless_game`: `not_measuring` and `blocked_here` stop routing to `_back` as game_unmeasured.
   - `live_reading`: keeps three states (holds, does not hold, could not read).
   - Proof: replay of the class-d sightings in the catalog (each must route away from the builder), plus an ENOSPC
     `--defect` fixture that must open an environment incident.
   - Ruling: touches BLIND_JUDGE_BUILD_FIXES_OWN_EYES (the owner's design for blind Judges). It extends that design and
     does not reverse it.
6. **Quarantine withdraws what an event filed.** Filed TESTQ_QUARANTINE_BUILD_WITHDRAW_UNSUPPORTED.
   - Changes: each auto-filed repair ticket records the sightings it rests on, with their attempt ids. A fault window
     marks those sightings invalid. The ticket's support is then recomputed: with no valid sighting it is dropped (the
     evidence is kept, plus a reopen signature); with mixed sightings it is kept.
   - Also changes `ingest.py` l.217: "FOUNDRY" becomes BENCH, because FOUNDRY is retired.
   - Proof: two-sighting fixtures (one invalid keeps the ticket, both invalid drops it), and the property that late fault
     discovery reaches the same end state as early discovery.
   - Ruling: "FOUNDRY is retired" (standing ruling), which this step carries out.
7. **Post-event recovery mode, designed before it is built.** Filed OPS_RECOVERY_DESIGN_POST_EVENT_MODE.
   - Changes: a design of the incident record, plus consult B's state machine (QUARANTINE, RECONCILE, VERIFY, RAMP, with
     a STALLED exit and an age alarm). It covers the entry signals for a host fault wave, an account or 429 wave and a
     harness burst, and per-sighting drop, merge, park or keep. Re-baselining keeps raw history and adds a versioned
     correction view. Steps 2, 3, 5 and 6 are its parts.
   - Proof: a design doc with a replay of the 2026-11-04 Steve and 429 events through it on paper, then the usual design
     review.
   - Ruling: none until it proposes changing the pause.
8. **Scoped content pause.** NEEDS OWNER, not filed (section 3).
9. **Unhold keeps the blindness history and needs a passing probe of the failed dependency before a paid re-check (A5).**
   Not filed. This is small, but it changes what the Conductor's unhold means, so it should be decided together with
   RELENTLESS_HOLD_BUILD_A_VERB_FOR_CONDUCTOR.
10. **Window churn counts to the event (B7).** Not filed. To be verified and noted on CHURN_WATCH_BUILD_NAMES_EVERY_BOUNCER.

## 3. Should "content paused while degraded" become scoped?

The rule now is: if any SLI budget is spent, and any system item is queued (and not clock-waiting or refused), then every
content item waits. Two measured problems follow. The spent SLIs (`infra_share`, `nightly_reds`) are not tied to the
items that would heal them. One red nightly class can stop every mod item, including ones he ruled on that day.

**Recommendation: scope it, with a global fallback.**
- Pause globally only when a shared integrity resource is impaired: the account circuit is open, storage is below
  headroom, the health assessment is unmeasured (step 2), or the store itself is suspect.
- Otherwise pause only the content whose lane depends on the spent SLI's scope. Reserve at least the places that the
  queued system items can actually use, and let the rest run content.
- Let content that carries a fresh owner ruling (filed or ruled within 48 h) take a reserved content place even while
  degraded. Such content still goes through the same checks: the ruling raises priority and does not certify a
  measurement path.
- Add an alarm: "runnable content paused > 6 h". It goes to the Conductor and names the system items that hold it.

**NEEDS OWNER.** This changes his 2026-11-03 ruling ("Please work any machine fixing item right now... max priority";
"System work immediately but existing non system work continues"). The second half of that ruling already says
non-system work continues, which supports scoping, but the code reads the first half as "pause all content". The
Conductor may rule this under CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM. Because it reverses the visible behaviour of a
recent owner priority, I recommend he hears it in plain words first:

"While the system is unhealthy, new mod work stops completely. Should mod work you ruled on recently, and mod work that
doesn't use the broken part, keep going in the free places?"

## 4. What this read changed in the catalog

- Headline: 155 is the classifier's list, not the runnable set, so the claim of a permanent pause is weakened.
- Class a: an unhold still clears the blindness (l.1224).
- Class c: the phantom spend did not cause the current pause.
- Added class p (an answered owner_call hold is never released) and root 9 (conclusions outlive their evidence).
