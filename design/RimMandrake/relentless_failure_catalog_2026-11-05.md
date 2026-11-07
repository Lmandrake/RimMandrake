# Relentless failure catalog, 2026-11-05

Lessons cited below by timestamp with `relentless` in their slug were folded into `skills/relentless/references/traps.md` on 2026-11-07; their full text is in git history.

Owner, 2026-11-05 ~05:00Z: "Please document all of these strange error conditions we're having: stale items, judges
unable to judge throwing things back to "fix" without fixing the measurement, all of these edge cases. [...] How can we
make this system much more robust, sane, and self-recovering after a major event?"

One entry per failure class. Fields: **Saw** (the symptom as he or we saw it), **Mechanism** (file:line at
origin/main 045724125c unless a sha is named), **Cost** (measured, with its source), **Found by**, **Fix** (sha) and
**Kind** (CLASS fix: the whole class can no longer happen; PATCH: this instance or one route). Line numbers are for
`src/RimMandrake/rimflow/relentless.py` unless another file is named.

Companion docs: GPT's review `relentless_failure_review_gpt_2026-11-05.gpt_read.md`, plan
`relentless_recovery_plan_2026-11-05.md`.

## Headline finding (measured while writing this)

`D:\ClaudeWork\rimmandrake\ops_watch\health.json` at 2026-11-05T04:37Z: `state: degraded`, spent SLIs `infra_share`
(24.5 h bad of 24) and `nightly_reds` (47.75 h bad of 24), and **155 `system_items`**. `content_paused()`
(l.3647-3663) is true while any one of those that is queued, not clock-waiting and not refused stays unplaced. Correction
after the GPT read (2026-11-05): 155 is the classifier's list (`ops_health.system_items`), not the runnable set, so it
does not by itself prove a permanent pause; how many qualify was not counted. The pause ends only when that set drains
or both SLIs heal. One red nightly class stops every mod item
on the board, owner-ruled ones included, and nothing measures how long that has lasted (class f).

## a. A blind Judge re-checks on a clock, forever

- **Saw:** JAM_CLASS spent 10.9M on a small fix; 142 items had check_count >= 3; 26 had more than half of their spend in
  checks (`D:\ClaudeWork\rimmandrake\conductor\churn_diagnosis_2026-11-05.md`).
- **Mechanism:** an UNMEASURED verdict (the Judge's box could not reach the evidence) re-checked the same sha after an
  1800 s clock. Two in a row held the item, but `unhold()` (l.1169-1215; `blind_back` at l.1206) reset `st["blind"]`, so
  every unhold, by the Conductor (07:02Z, 03:01Z) or the owner (12:57Z), bought a new paid round. The Conductor's first
  guess ("the counter resets inside the loop") was measured false from attempts.jsonl.
- **Cost:** OPS_ERROR_BUDGET 4.36M over 8 checks, plus about 0.15-0.5M per blind check across the 26 items.
- **Found by:** the owner, who asked why JAM cost 10.9M. The churn SLI was red, but it does not name items.
- **Fix:** BLIND_JUDGE_BUILD_FIXES_OWN_EYES 2614683a4e, f967adc735, 7cc9d2921b, 320ee24883. The first blind check ends
  checking, the Judge proposes its own reach repair (`relentless_reachfix.py`), the supervisor probes and applies it,
  and the same sha is checked once more. Correction after the GPT read: `unhold()` still sets `st["blind"] = None` in
  its `blind_back` branch (l.1221-1225), so a manual unhold still buys one paid re-check; reachfix (l.455-464) only removes
  the clock. `reach_hold` (l.662)
  landed 4eabac097b.
- **Kind:** CLASS for clock re-checks. The repair still depends on the Judge naming its blindness correctly (see d).

## b. A walled Judge cannot reach its evidence

- **Saw:** checks UNMEASURED on evidence that plainly exists: `D:\ClaudeWork` series, seat-tmp, other clones, and
  Windows `dotnet.exe` builds.
- **Mechanism:** the Marker wall (`relentless_wall.py`, `relentless_rules.json` walls.marker) hid whole trees
  (`tree_exclude` drops `infrastructure/state/items/`; `tree_from_parent` shows the ledger as the parent's snapshot), and
  ClaudeWork inside the box was a tmpfs, so Windows dotnet received a `\\wsl.localhost` UNC path and refused it. Lessons:
  `20261104T060514Z-...-walled-check-that-cannot-reach-its.md`, `20261103T222919Z-...-wall-s-deny-list-every-launcher.md`
  (a new TMPDIR under a denied root killed every checker at start, 11312ebfc6).
- **Cost:** STEVE_DISK_MEASURE_ONLY_FORTY_GIGS_LEFT was done at gen 1 and looped to later gens. On 11-03, 29 of 29 checks
  died at launch within seconds.
- **Found by:** builders and the owner reading returned items. There was no alarm for "unreached evidence by class".
- **Fix:** d37c847f5e and e7f40a92bd (the wall hides only the diary; seat-tmp and clones read through by name; the
  Windows build stage is bound read-write). d776e3f8e0 added offbox adapters (git at {sha}, gh for
  MandrakeWorkflows-dev, /proc cwds). Open: CHECKER_REACH_FIX_{CLONES,SEAT_TMP,STORE}_STILL_DARK and
  CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK.
- **Kind:** PATCH, path by path. The wall is a deny list that a launcher's environment can contradict. Nothing proves
  the box can reach a contract's evidence *before* a paid check.

## c. Phantom spend: zero-usage runs were charged the full reserve

- **Saw:** JAM_CLASS 10,913,625 tokens. The real spend was about 1.31M.
- **Mechanism:** an API 429 (weekly limit) run returns a result with every usage field 0 and duration_api_ms 0.
  `relentless_usage.py:129 if tok:` read a measured 0 as unmeasurable and returned `estimated`, and `charge()`
  (l.551-556) then charged `run_reserve` 1.2M.
- **Cost:** 48 runs on 2026-11-04 (25 work, 23 check) charged 57.6M of phantom spend across 6 items (5 of them over
  8.4M). The phantom spend also inflated the `returned_tokens_pct` health SLI (66.2% at 04:37Z). Correction after the GPT read:
  that SLI is not spent (21 bad h at 04:52Z); the pause comes from `infra_share` and `nightly_reds`, so the phantom spend
  did not cause this pause.
- **Found by:** the owner (the JAM cost question).
- **Fix:** b902ac4ec9 (RELENTLESS_SPEND_FIX_ZERO_USAGE_RESERVE): a measured all-zero result is charged 0.
- **Kind:** PATCH. The class is "an account outage is read as work". Account loss also kept *launching*: 8 consecutive
  rate-limited check runs on JAM, 35 min apart. The account breaker did not stop the launches, and the past spend was
  not re-baselined (the 57.6M is still on the books).

## d. Judges return work as "fix it" when the measurement is the problem

- **Saw:** proof_weak and blind_fail loops. Items came back to a builder with "the proof has holes" when the hole was
  the Judge's reach, the harness, or the game load.
- **Mechanism:**
  - `relentless_wall.read_as` (relentless_wall.py:521-543) has only four outcomes: FAIL, WEAK, UNMEASURED and PASS.
    There is no ENVIRONMENT outcome. The old prose format is "biased to FAIL": a defect named anywhere makes it FAIL,
    even under UNMEASURED (l.535-537).
  - WEAK routes to `fail(..., "proof_weak")` (l.4243-4248) and from there to a proof-only builder. After
    `same_failure_limit` it becomes a `proof_weak` hold, written needs=owner (lesson
    `20261103T194227Z-...-owner-pile-relentless-holds.md`: 43 of 61 needs=owner items were Relentless holds, 37 of them
    proof_weak).
  - The live lane does separate harness INFRA (relentless_game.py:1056-1061, never a strike). But `game_unmeasured`
    ("the proof ran and measured nothing", l.1075-1085) goes `_back` to the worker. The queue triage
    (`D:\ClaudeWork\rimmandrake\conductor\triage_20261105\result_batch_00.md`) shows that this route carries
    environment failures: GRAFFITI_NORTHSTAR_GREEN_FULL_1 (gen 18, 9 returns, 6.5M: "a game already loaded", then
    Graffiti not in the load), GENERATOR_MODS_PROVE_INERT (save.missing_mods every time), ATMOSBASE (proof save stale on
    the current load), ART_OVERRIDE_FAMILY_SCRIPT_1 (10.9M, the same UNMEASURED 8 times: Scarlands has no readable
    packageId).
  - The attribution consult failed with "no room in N s" (a capacity wait) and was recorded as an unattributed
    validation end, which held 7 items (RELENTLESS_ATTRIB_FIX_CONSULT_NO_ROOM_HOLDS, fixed 4da5d60ad1).
  - The contract is frozen after gen 1 (lessons `20261104T040225Z`, `20261103T022128Z`): a typo in `--proof` (a wrong
    selftest stem) dooms every finish, and no builder may repair it.
  - Measurement traps that read as product results: a negated grep goes green on an unreadable file
    (`20261104T022556Z`), and `proof_gate` does not tokenize a trailing '.' (`20261103T074928Z`).
- **Cost:** the triage lists 8 CHURNING items at 1.9M-10.9M each. `churn_items` was 35 and `returned_tokens_pct` 66% at
  04:37Z. The 11-04 churn alarm put 71% of spend on returned attempts (lesson `20261104T224055Z`).
- **Found by:** the owner ("judges unable to judge throwing things back to fix").
- **Fix:** 4da5d60ad1 (no-room consults wait instead of holding). The structured `--defect/--unreached` verdict exists
  (lesson `20261104T062142Z`). There is no product/measurement/environment split.
- **Kind:** PATCHES. The class (return routing chosen by a word, not by a cause) is open.

## e. Stale owner showings

- **Saw:** an old item, DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS, was staged for his look while his newer rulings sat unbuilt
  on its successor, DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED (filed 11-03 21:14Z with his words: "the drawbridges appear
  very broken").
- **Mechanism:** staging chose by item status. Nothing checked whether a newer item carried a fresher owner ruling on
  the same subject or mod. Lesson `skills/rimworld-live-review/references/traps.md`.
- **Cost:** one owner look spent on superseded work (his time is the scarcest resource here).
- **Found by:** the owner.
- **Fix:** policy 4a3bd2b12a (OWNER_REVIEW_BUILD_SHOWS_READY_BEFORE_ASKED, design section 8.1). No mechanical "newest
  ruling wins" gate.
- **Kind:** PATCH (policy text and a lesson).

## f. A global content pause froze every mod item for a day or more

- **Saw:** RUNNING NOW read "health degraded: content paused while system items wait". Every content item stopped,
  owner-ruled ones included.
- **Mechanism:** `ops_health.verdict` (src/RimMandrake/Utils/ops_health.py:274) sets `degraded` if ANY SLI's 24 h-in-48 h
  budget is spent. `content_paused` (l.3647-3663) is true while any system item (the health verdict's
  `system_items`, 155 at 04:37Z) waits. `lease()` (l.4841-4845) then `return`s at the first content item, so the whole
  line stops, not just that item. Only `expedite`, the priority `first` list and `plan` items pass.
- **Cost:** nightly_reds was 47.75 h bad at 04:37Z. The pause had been in force since the budget was spent (the brief
  says 28 h or more). Content throughput was 0 for that time. The cause was red selftests, not any mod.
- **Found by:** the owner.
- **Fix:** partial. 0cd6407291 (a system item on a clock-wait no longer holds content back) and the concept-refused
  exemption (l.3651-3653). The gate is still global.
- **Kind:** PATCH. The gate's scope (all content) does not match its cause's scope (one SLI, a tooling class).

## g. Gates block the very system work that would clear them

- **Saw:** the first-touch Designer gate held system items. One system item waiting on a 342 min timer stalled all
  content, with 2 of 8 places live.
- **Mechanism:** `first_touch_hold` (l.1777) applied to system-class items. The clock-wait counted as "a system item
  waits for a place" in `content_paused`.
- **Cost:** hours of 2/8 utilisation (0cd6407291 message).
- **Found by:** the Conductor reading the board.
- **Fix:** 162541a866 (system items exempt from first-touch) and 0cd6407291.
- **Kind:** PATCH, gate by gate. No gate declares the scope it blocks.

## h. The engine ran old code

- **Saw:** a landed fix did not take effect. The books clone read books_stale.
- **Mechanism:** the books clone could not level because of dirt, and the fix that exempted that dirt was itself
  unpulled (lesson ac8bef705e, `skills/relentless/references/traps.md`). Also, a tick
  imports relentless.py *then* merges origin/main, so a supervisor change takes effect one tick late (lesson
  `20261103T224213Z`). rm-mirror and rm-codebase-health ran from the retired foundry clone (lesson `20261104T032656Z`).
- **Cost:** fixes measured as landed but not running, for hours.
- **Found by:** the Conductor, after the owner asked why a fix had no effect.
- **Fix:** ac8bef705e (a lesson only).
- **Kind:** PATCH. There is no "running code sha == origin sha" reading and alarm per service.

## i. One machine fault poured N tickets in

- **Saw:** 18 HARNESS_REPAIR_CAUSE_* tickets, one per testq job, near-duplicates, several inside SteveDesktop's
  hardware fault windows.
- **Mechanism:** `src/RimMandrake/Utils/testq/ingest.py:197-222 repair()` files one item per normalised cause base, so
  differently-worded symptoms of one fault become different bases. The Steve fault gate (`fault_monitor`, 162ddf91df)
  is *retroactive*: a fault window is known only after later results, so ingest files first, then (l.381-401) notes
  "drop this item if no sighting outside a fault window". Nothing drops it.
- **Cost:** 18 tickets of triage (045724125c). Each would have spent a builder run if admitted.
- **Found by:** the Conductor's queue sweep after the owner asked (615a045471, "sweep the queue for trash after a major
  system event").
- **Fix:** 045724125c (a class item, Steve-fault supersedes, two closes as fixed). This was hand triage.
- **Kind:** PATCH. The class (one source fault becomes N tickets) is open.

## j. An item that cannot succeed here kept spending

- **Saw:** STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO (probable hardware, RAM test owed: only hands can do it) kept being
  claimed and checked, 38 events.
- **Mechanism:** no "achievable here" predicate. The ladder (strikes, proof_weak, unmeasured) eventually holds it, but
  only after paid rounds. SOORRAK_INSTANT_JOB_LOOP_1 is the same shape: the flyer gate refuses its A1 forever because
  the criterion text says "flight" (triage batch_02).
- **Cost:** 1.07M over 3 checks (churn census).
- **Found by:** the owner, who asked to HOLD it.
- **Fix:** held by hand, editing state under Store.lock (no verb, see m).
- **Kind:** PATCH.

## k. The board misleads

- **Saw:** all three CHECKING rows went red. Two were checks that had finished with success (NO PROCESS: the unit had
  exited and the verdict was written, waiting up to a tick for collection). One was a fresh check reading an old beat
  (SILENT 5.5 h from the build run's last_beat). Held and blocked items were invisible.
- **Mechanism:** the board reads process liveness and beat age, not the verdict file. `activity()` (lesson
  `20261104T223742Z`) takes the max mtime over a whole projects dir, so another session masks a silent worker.
- **Cost:** owner alarm and attention. One false red trains people to ignore red.
- **Found by:** the owner.
- **Fix:** d8ecb3baf6 (held and blocked boxes). RUNNING_BOARD_FIX_FINISHED_JUDGES_CRY_WOLF is open.
- **Kind:** PATCH.

## l. Throughput: the check lane starved the builders

- **Saw:** 4 of 8 places used.
- **Mechanism:** check starts were capped per tick (3), while `lease()` refused all builders when
  `candidate > check_backlog_max` (l.4821-4825). Two throttles on one queue, set apart, make a deadlock-shaped stall.
- **Cost:** about half the capacity for hours (8f5be116c1 message).
- **Found by:** the Conductor.
- **Fix:** 8f5be116c1 (5 check launches a tick).
- **Kind:** PATCH (a constant).

## m. Missing levers and replayed messages

- **Saw:** the Conductor could only unhold. Holding meant editing state by hand under Store.lock, twice on 11-05. The
  wake replayed owner messages that had already been answered, so a fresh Conductor re-answered settled questions.
- **Mechanism:** relentless.py has `unhold` (l.1169) and no `hold` verb. `seat_restart.py wake` filtered by the wrong
  timestamp.
- **Fix:** SEAT_WAKE_FIX_ANSWERED_MESSAGES_REPLAYED e9efb41a65. RELENTLESS_HOLD_BUILD_A_VERB_FOR_CONDUCTOR is open.
- **Kind:** PATCH. Hand edits under a lock are themselves a reliability risk.

## n. Queue triage after the event, and its own gaps

- **Saw:** `D:\ClaudeWork\rimmandrake\conductor\triage_20261105\result_batch_0{0,1,2}.md`. Batch 00 has 8 CHURNING, 1
  CANNOT SUCCEED and the rest KEEP. Batch 01 is almost all PENDING (not judged). Batch 02 has 2 CANNOT SUCCEED, 1 DONE and
  about 25 PENDING.
- **Finding:** the post-event triage was hand-run by helpers, and most rows came back PENDING, so the triage itself did
  not finish. The CHURNING rows are mostly class d (environment or proof bugs returned as work). The fields a machine
  would need (returns, last end class, spend, live INFRA count) are already in the store. No tool computes the verdict
  from them.

## o. Machine-filed tickets with no definition of done (Conductor addendum)

- **Saw:** the owner asked what HARNESS_REPAIR_CAUSE_* for "colonists downed or killed" builds and how it passes. The
  answer was: nothing is defined.
- **Mechanism:** `testq/ingest.py:217-219` spawns with `--title` only: no spec, no repro, no pass condition, and
  `--for FOUNDRY` for FlowWorks, a seat retired 2026-11-02. A builder must invent its own pass, and the cheapest
  invented pass silences the check (removing the harness's colonist-harm test "fixes" it).
- **Fix:** hand-written spec for SITE_QUIET_FIX_COLONISTS_HURT_DOWNED_DEAD (4100c595ae: classify MOD, SITE or
  ENVIRONMENT first; forbidden fixes; a negative control). TESTQ_REPAIR_FIX_TICKETS_NAME_THEIR_PASS is filed.
- **Kind:** PATCH for one item. The class (an auto-filer with no contract template, and a Judge that accepts a contract
  easier than the failure it names) is open.

## p. An owner_call hold whose question he already answered is never released (Conductor addendum)

- **Saw:** ICON_OUTLINE_REPAINT_1 was held by Relentless at 2026-11-03T13:17Z as `owner_call` ("regenerating our own
  non-donor art overturns his 10-19 ruling"). He answered by card at 20:11Z the same day ("Fix any live art that needs
  fixing, who cares if some art goes unused"); an audit re-routed the item to offline at 2026-11-05T00:23Z. The
  Relentless hold stood until the Conductor unheld it by hand at ~05:10Z: about 33 h lost.
- **Mechanism:** the snag path (relentless.py:764-770) writes `hold = {why, kind: owner_call, delivered, at}`: a prose
  reason, not the question it waits on; `hold_is_his` (relentless.py:5012-5015) then makes it a hold only he can lift. Nothing links a card answer,
  a ledger ruling or a `needs` change back to the holds that wait on it, so release needs a person to notice
  (`unhold` in relentless.py ~1169 is manual only).
- **Cost:** 33 h on one item; every owner_call hold is exposed the same way, and his answered questions look
  unanswered on the board.
- **Found by:** the Conductor, by hand.
- **Fix:** none yet. A hold should name what releases it (card id, ruling id, or a needs value), and an answer event
  should release every hold keyed to it.
- **Kind:** CLASS (cross-cutting root 8, missing levers; and root 7, the owner as the alarm).

## q. Further classes from the last 7 days of lessons

- **q1. A recurring fix is applied as a patch:** `remote.origin.pushurl=read-only-consult` was inherited by item clones
  from help clones three times (lessons `20261104T092038Z`, `20261104T234013Z`, `20261105T005329Z`). Each was fixed in
  that clone. `help_checkout` still sets it and reuse never clears it.
- **q2. A repair item with no owner holds chains:** FC103899 (a stale companion) sat 2 days holding 59 FlowWorks
  chains (lesson `20261104T000538Z`).
- **q3. A jam closed on the wrong cause:** OPS_RELENTLESS_UNSTICK_XARX was closed on a checkout fetch while the real jam
  ran about 11 h (lesson `20261103T033821Z`).
- **q4. Resource exhaustion read as a slow proof:** /tmp is an 18G tmpfs, filled by tree copies. Checkers "gave no
  verdict" (lessons `20261103T010743Z`, `20261104T051221Z`, `20261105T024235Z`). checker_lost is a launch failure until
  the .err says otherwise (`20261103T222536Z`).
- **q5. Shared fixed /tmp names cross-contaminate:** POOL_STRANDS read another worker's selftest output
  (`20261104T020031Z`).
- **q6. A new alarm kind is unrouted until the nightly run** (`20261103T215031Z`, `20261104T031455Z`), so the nightly
  goes red and feeds class f.
- **q7. The needs=owner pile is mostly machine holds** (43 of 61, `20261103T194227Z`), so his queue is noise, and he
  "discovers first" because the real asks are buried.

## Cross-cutting roots

1. **The system acts on a reading it cannot trust.** Classes a, c, d, k, q4. A 0 usage reading became a 1.2M
   charge. An unreachable file became a WEAK proof. A dead unit became NO PROCESS. "No verdict" became a failure. No
   reading carries "can this instrument see?", so a consumer cannot tell blind from bad. This is the largest root.
2. **One bad source multiplies into N tickets or N retries.** Classes i, c (8 launches on one exhausted account), a,
   o. Inflow is never deduplicated by *source event*, only by text, and is quarantined (if ever) after admission.
3. **A global gate where a scoped one was needed.** Classes f, g, l. A health SLI about selftests paused mod content.
   One timer paused everything. A check backlog paused all builders. A gate does not declare which items its cause
   can affect.
4. **A fix that needs itself to land.** Classes h and q1. The levelling exemption could not arrive because of the dirt
   it exempted. The supervisor runs pre-merge code. Repair routes run in the same machinery they repair.
5. **Routing by verdict word, not by cause.** Classes d and j. Product, measurement and environment failures all
   come back through FAIL, WEAK and UNMEASURED words, and the default route for "I am not sure" is a builder.
6. **A contract easier than its failure.** Class o, the frozen-contract half of d, and the triage's GRAFFITI_V1 (the
   proof calls methods with the wrong arity). Nothing checks that a pass condition would have failed on the original
   failure (a negative control).
7. **The owner is the alarm of last resort.** In a, c, d, e, f, j and k the owner saw it first. The alarms that
   existed (churn_items, returned_tokens_pct) were aggregate. They did not name items, did not distinguish phantom
   spend, and did not page anyone as a *new* event.
8. **Levers are missing, so state is edited by hand.** Class m. Hand edits under Store.lock leave no causal record
   and are how new inconsistent states get made.
9. **A conclusion outlives the evidence that authorized it** (added after the GPT read, consult A). Classes e, i, p and
   the unhold reset in a. A showing, a repair ticket or a hold stays in force after the reading or question behind it
   changed: nothing links the decision to its evidence, so nothing recomputes it. Plan:
   `design/RimMandrake/relentless_recovery_plan_2026-11-05.md`.
