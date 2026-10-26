# Orchestration designs: GPT's skeptical review, checked against our numbers (2026-10-26)

You asked (about 14:00): "May I see the design for the dynamic optimizer, allocation of subagents, the game testing,
all of that? Is that whole new one orchestrator plus engine with a light human interactor design already built? Has it
been thoroughly scanned by gpt and compared to our many past designs and how they failed?"

**Short answer.**
- **Designs:** there are three, all listed in (a).
- **What is running:** the allocator, the token meter and the SteveDesktop steward.
- **What is not built:** the one-window-plus-engine design. It waits on your seven cards, D1-D7.
- **GPT's review:** it read all three designs alongside a catalogue of 18 past schemes and how each one failed, in two rounds: first a skeptical round, then improvements.
- **Fact-check:** we checked every number GPT used. None was wrong (0 CONTRADICTED). Two of its numbers come from this morning and have drifted by one since. Four of its claims cannot be checked yet.
- **Result:** we accept 8 of GPT's 10 improvements, and add two of our own: logging in the spawn-limit hook, and fixes to the design docs. Of the other two, the wider test feed is already filed (`TESTQ_MODS_WIRE_BEYOND_FLOWWORKS`), and testing in batches is declined for now. Each is filed as an item and none is built. Five of your seven cards change.

---

## (a) What exists

**The three designs** (all in `D:\Luke\dev\RimMandrake\design\RimMandrake\`):

| design | what it decides | state |
|---|---|---|
| `work_allocation_framework_2026-10-26.md` | the six work streams, their measures, the allocator rules R1-R8, the SteveDesktop steward | partly built |
| `operating_modes_2026-10-26.md` | the three dials (tokens, review queues, where you are), plus the CRUNCH and GAME_DOWN overrides | built |
| `single_primary_design_2026-10-26.md` | retire FOUNDRY; BENCH becomes your one window; a no-AI engine runs the queue with headless workers | **not built**; waits on D1-D7 |

**What is running now** (checked 14:01-14:10):

| piece | state | evidence |
|---|---|---|
| token meter | live | 15 readings since 12:47. Some accounts are carried forward from an older reading. |
| allocator plus the spawn-limit hook | live | Its current mode: "CRUISE+OWNER PAYDOWN BENCH N=4, FOUNDRY 1". The spend rate still comes from a message count, because the meter has only 5 readings over 1 h. |
| SteveDesktop steward and heartbeat watcher | live | state RUNNING. It has made 17 state changes. Its AI wake has never fired. |
| RimPulse streams panel | live | 174 rows |
| Archmagi batch backfill | built, off | 0 jobs |
| engine tick, workers, triage, phone push, phone answers | **not built** | 9 build items are filed and held behind your cards |

**The review files:**
- The brief GPT read: `D:\ClaudeWork\rimmandrake\design_review_20261026\brief.md`
- GPT's answers: `gpt_r1.md` (skeptical) and `gpt_r2.md` (improvements), in the same folder.

---

## (b) GPT's top skeptical findings, and our verdict

| # | GPT says | our verdict | evidence |
|---|---|---|---|
| 1 | **The slot split is wrong for the new design.** FOUNDRY's 25% share would go to the engine, and BENCH's unused share would sit idle. | **Agree** | `slot_rules.json` gives FOUNDRY 0.25 of the total. The live split is BENCH 4, FOUNDRY 1. |
| 2 | **"Published" does not mean "accepted."** A sha on main plus a ledger move does not prove the work is right. | **Partly.** The ledger already records verify levels and an acceptance field. What is missing is a gate that refuses a close without them. | Today 77 of 541 new items cite closed work (14.2% rework). 391 of today's 513 closes were never started. 164 were closed within 5 min. |
| 3 | **Leases do not fence effects.** A worker whose lease has lapsed can still publish, close or touch the bridge. | **Partly.** We accept a cheap attempt token in the ledger. Bridge workers stay off until the bridge also checks the token. | `lease.py` line 31 says "TWO CLONES ARE NOT COORDINATED". There are 19 contested claims on record and 166 lapsed leases open now. |
| 4 | **The budget control cannot see what is spending.** The daily ceiling counts only finished results, so workers still running are invisible to it. | **Agree** | The design sums completed results only. The rate comes from a message count, and the meter has too few readings for a slope. |
| 5 | **Automation can make the debt grow faster.** BURN and fresh workers would outrun review, verification and your answers. | **Partly.** It is real history, but today's flow is better. | Over 10-23..26, 1,163 items were filed and 625 closed. Today, 541 were filed and 513 closed. On 10-22, 125 were filed and 30 closed, at 99.5 M tokens per close. Today 521 built items wait for verification. |

**Other GPT findings, checked:**

- **R3 wording.** The allocator's rule R3 says "grew 3 days running" (line 218). The worked example fires it on "not falling" (line 235).
  **Agree:** this is a doc error.
- **Tick home.** The design runs the tick in `~/rm/foundry`, then archives that clone at step 4 (S lines 114 and 245).
  **Agree:** this is a doc gap.
- **Over-engineered.** 50-70 h of builds, plus 9 more engine items, aimed at a problem that showed up as 166 idle minutes.
  **Partly.** The allocator, steward and streams panel are already built. The hourly triage pass can shrink to "run on an event". The engine itself is small.
- **Scratch clones collide when their work is merged.**
  **Agree.** On 09-26, helpers collided on one shared `.csproj`. There are 4 lessons about publish refusals. We accept one worker per mod at a time.
- **Batching cards can bring back stale asks.**
  **Agree.** There were 5 "I've already ruled" messages between 10-05 and 10-24. Today, 49 items wait on you, 32 of them for over 3 days; the oldest has waited 45 days.
- **Keep the old window running beside the engine as a comparison.**
  **Disagree.** It costs tokens. It also recreates the two-clone double-lease problem. We compare against the last 7 days of the ledger instead.
- **Test work in batches ("cohorts") during the pilot.**
  **Disagree for the pilot.** We measure tokens per accepted item instead, and look again on day 14.
- **Delete SWEEP.**
  **No change.** There is no evidence either way.

---

## (c) Accepted improvements (filed for BENCH, none built)

- Every threshold below is our proposal. GPT's own numbers were marked "assumed".
- The baseline is the last 7 days of the ledger, leaving out bulk closes and closes that were never started.

| item | size | what | confirms it worked | window | kill if |
|---|---|---|---|---|---|
| `ENGINE_SLOTS_WIRE_TOTAL_MINUS_DESK` | S | engine slots = the total minus what BENCH is running; replaces the 25% share | engine idle with work ready under 10 min a day | the 48 h pilot | idle over 60 min a day on 2 days |
| `ENGINE_CLOSE_ENFORCE_ACCEPTANCE_EVIDENCE` | M | a worker can only mark an item built; a close needs evidence of the verify level the item owes | rework rate of engine closes at or below 14.2% | 7 days | above 17.8% at day 14, or the built-not-verified pile grows over 10% |
| `LEDGER_LEASE_HARDEN_ATTEMPT_TOKEN` | M | each attempt gets a token; the ledger refuses a close or move from a stale token | 0 contested claims on engine items (19 on record); the drill shows a refusal | 14 days | any stale effect is accepted |
| `ENGINE_BUDGET_ENFORCE_RESERVE_AT_LAUNCH` | S | each worker reserves its budget when it starts; the ceiling counts finished plus running work | (finished + reserved) / ceiling stays at or below 1 | 72 h | above 1.1 |
| `ENGINE_ADMISSION_ENFORCE_PAYDOWN` | S | under PAYDOWN the tick starts only verify, fix and close work, never new filing | the built-not-verified pile (521) stops growing; net flow at or below 0 | 7 days | the pile grows over 10% |
| `ENGINE_WORKERS_ENFORCE_ONE_PER_MOD` | S | one worker per mod or `.csproj` at a time | publish or rebase failures at or below 5 per 100 workers | the pilot plus 7 days | over 15 per 100, or slots blocked idle over 60 min a day |
| `OWNER_CARDS_HARDEN_DECISION_RECEIPTS` | M | every card carries a decision id, a revision and an addressee; each answer gets an enactment receipt | 0 "already ruled" messages (5 between 10-05 and 10-24) | 14 days | any re-ask of a decision that has a receipt |
| `ENGINE_TRIAGE_REWIRE_ON_SHARED_FAILURE` | S-M | tell shared failures (permissions, publish, bridge) apart from bad work; run triage on that event instead of every hour | the drill restores service within 30 min at p90 | the fault drill | above 120 min |
| `SLOT_HOOK_MEASURE_REFUSALS_AND_PEAK` | S | the spawn-limit hook logs each refusal and the peak number running (today it logs nothing) | peak at or below N in at least 99% of 15-min windows | 7 days | it ignores one of your overrides |
| `SINGLE_PRIMARY_DOC_FIX_TICK_HOME` | S | doc fixes: give the tick a home that survives step 4; fix R3's worked example | - | - | - |

---

## (d) Fact-check of GPT's claims

- **CONFIRMED** means our measurement or doc text says the same thing.
- **CONTRADICTED** means we measured a different value.
- **UNMEASURED** means we cannot check it yet.

| GPT claim | verdict | measured |
|---|---|---|
| FOUNDRY gets 25% of slots | CONFIRMED | `slot_rules.json` FOUNDRY_share 0.25; live split 4 + 1 |
| 76 of 495 new items are rework | CONFIRMED (morning) | now 77 of 541, 14.2% |
| 167 lapsed leases | CONFIRMED (morning) | now 166 |
| 165 bulk closes | CONFIRMED | same in the morning metrics |
| leases do not coordinate clones | CONFIRMED | `lease.py` line 31 |
| daily ceiling sums finished results only | CONFIRMED | single_primary §2 |
| breaker items go to BENCH; triage stops in ALMOST_OUT or DARK | CONFIRMED | single_primary §2 |
| R3 says "3 days running" but the example says "not falling" | CONFIRMED | work_allocation lines 218 and 235 |
| the tick lives in a clone that step 4 archives | CONFIRMED | single_primary lines 114 and 245 |
| 50-70 h of builds; 22-30 h for the first slice | CONFIRMED | work_allocation line 352 |
| 9 engine build items | CONFIRMED | single_primary §9 lists 9 |
| 166 idle minutes; 104 of 104 jobs FlowWorks; 1 of 129 harnessed mods selectable | CONFIRMED | work_allocation §1 |
| meter has 15 readings, some carried forward | CONFIRMED | `account_usage` series |
| a cold start costs 47,546 tokens (about $0.38); a cached one about $0.0096 | CONFIRMED | two probes; reuse across clones not tested |
| two windows with auto-wake would match the engine | UNMEASURED | never run |
| the spawn hook holds N | UNMEASURED | the hook writes no log (item above) |
| one-item workers waste context | UNMEASURED | no data yet; tokens per accepted item will show it |
| D2 answer-latency measure | UNMEASURED | it reads 0 resolved, which we suspect is wrong |

**CONTRADICTED: 0.** The two morning numbers (76 of 495, 167) are drift over the day, not errors.

---

## (e) Changes to your cards D1-D7

- **D1 The shape.** Same shape, with the attempt-token fence and one worker per mod added. Retiring FOUNDRY becomes its own later card, asked only after the pilot.
- **D2 May a program start sessions.** Our recommendation changes from "yes" to **"pilot only"**. It becomes a standing yes once the pilot passes the metrics in (c).
- **D3 FlowWorks and GSS to the engine.** Now conditional: only after the acceptance gate and one-worker-per-mod have run clean for 48 h, and offline items only. BENCH keeps the live work.
- **D4 Push channel.** ntfy is still recommended. Note that a push alone does not stop re-asks; the decision receipts do.
- **D5 Push budget.** Unchanged.
- **D6 Interactive allowance.** When you come back to BENCH, running engine workers finish their item rather than being killed. Any allowance above the total expires on its own.
- **D7 The pilot.** The fault drill adds two cases: a stale attempt, and a budget reservation. The baseline leaves out bulk and never-started closes. Retiring FOUNDRY also needs the phone answer loop working and a clean 7-day rework watch.

---

## (f) Glossary

| term | meaning |
|---|---|
| BENCH / FOUNDRY | the two agent windows today. BENCH talks with you; FOUNDRY works the queue. |
| engine | the planned no-AI timer that starts headless workers. It is not built. |
| worker | a headless Claude session that does one item and exits |
| allocator | a no-AI program that sets N, the number of helpers allowed at once, every 15 min |
| N | the number of helpers allowed to run at once |
| lease | a 45-minute claim on an item, so two agents do not do the same one |
| attempt token | a number stamped on each try at an item, so a late, stale try is refused |
| verify level L0-L4 | how strongly an item is checked; L4 means you look at it |
| V0 | built items still waiting to be verified (521 now) |
| rework | a new item that cites closed work, meaning the close did not hold |
| PAYDOWN | a queue setting: verify and close before filing new work |
| CRUISE / BURN / ALMOST_OUT / DARK / SWEEP | token modes, set by how fast the weekly allowance is being used |
| steward | the no-AI watcher on SteveDesktop that owns brakes, pauses and empty queues |
| testq | the batch test lane on SteveDesktop |
| p90 | 9 in 10 cases are at or below this value |
| kill criterion | the measured result that makes us undo a change |
