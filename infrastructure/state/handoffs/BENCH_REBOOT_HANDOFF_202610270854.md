# BENCH_REBOOT_HANDOFF_202610270854 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610270528`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**RimFlow v3 goes live in three waves after the Wednesday token reset** (owner by card): Wed Dispatcher + Conductor + Operations, Fri Producer + Arbiter, Sun Auditor + Innovator. Before then everything AI stays off and the measuring arm (ops_watch, no AI) runs. Tokens are the binding constraint: first ops_watch reading put runway at system 0.81, lukas 0.25, Codex 0.64 (below 1 = runs out before reset), so the seat throttled to zero new helpers overnight. Owner rulings this session that change how work is done: reviews go to GPT (`gpt_consult.py`), non-v3 helpers capped at 2, north-star regression checks AND new bars delegated to the Arbiter (loosening stays his), Dispatcher measures / Operations analyses (replaces RimPulse).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Roles review page (published, v2): https://claude.ai/artifact/AfjyADpEtbhPB12nfsNGbV — coverage 76 concerns, 0 orphans after adjudicating his six proposals (agreed 1, in part 2, pushed back 3: carry-out = auto-opened enact item checked by a program, canon contradictions = Dispatcher check + Conductor fix, spare capacity = Producer orders / Arbiter stops / Innovator explores, weekly success test = he decides on a program's numbers). Five more GPT re-homing proposals listed for him.
- FlowWorks-between-sittings home changes the schedule's "BENCH never woken" rule (headless bench-lane builder while he is away) — his to confirm.
- Process simulator findings: `design/RimMandrake/rimflow_v3_sim_findings_2026-10-27.md` — Dispatcher cuts FOUNDRY stalls 100-230 min/day; Arbiter on today's token budget LOWERS sound output 8-11/day (quality gain only with headroom); Auditor at ~4 audits/week vs ~200 escapes does nothing measurable as designed; cut helper caps first when throttling. These bear on the Friday/Sunday waves.
- Dispatcher recovery passes --dangerously-skip-permissions (matches the seat launcher); recovery stays OFF until proven live.
- Leftovers: 66 deleted (43 saves, 22 ModsConfig backups, 1 14.3 GB clone), archive D:\ClaudeWork\backups\leftovers\2026-10-26 (in his digest).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `RIMFLOW_V3_BUILD_DISPATCHER_FIRST` — built f0b736505a, independently reviewed + 13 fixes b183e72775 (GPT 16/19 real), timer installed dry-run, FOUNDRY recover_dead off 80f16a3f04; NEXT: on Wednesday after the reset install the doorbell hook in the FOUNDRY seat settings and switch the timer to --apply for wakes only, starting the 48 h proof.
- `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE` — responsibilities register + orphan homes 9a03300d23, Operations layers 1-2 live (ops_watch, allocator disk brake), Operations role written/disabled; NEXT: write the Conductor role's instructions (quick + session mode) and get a clean GPT round on slot_allocator.py and csuite_codex_limits.py before Wednesday's wave.
- `EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES` — sliced pulse 990e5e7de6 deployed; live r12 0.62-1.18 ms/tick, max 129-308 ms (bar 0.2/20); NEXT: find why one pulse slice costs 161 ms live vs 2.6 ms offline before optimising further.
- `ROAST_STICK_FIX_DISABLED_COOK_STAT_ERRORS` — CookSpeed error gone live r12, FoodPoisonChance disabled-stat error remains; NEXT: suppress the FoodPoisonChance read for the roast-on-a-stick bill.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Offline CoreCLR timing predicted 2.6 ms for a slice that cost 161 ms live (filed: lessons 20261027T085507Z).
- Escape counts fall when less ships, so fewer escapes is not better quality (filed: lessons 20261027T085337Z).
- `rimflow note --owner-said` refuses text ending in a question; quote only his instruction sentences (see: using-rimflow).
- `rimflow close` run before the commit lands records the wrong sha (see: using-rimflow).

## Closed since the last handoff (4)

- `ARTLEDGER_BAN_FIX_PH_FROM_LIVE_FILE` — 1ad131f6a4
- `ART_GUARD_FIX_ALLOWS_LIVE_OF_BANNED` — 1ad131f6a4
- `LEFTOVERS_BUILD_ARCHIVE_THEN_DELETE` — a89d56de9e
- `RIMFLOW_SIM_BUILD_FACTORY_IN_A_BOTTLE` — c93c543ec8

## Filed and still open (12) — the next seat's queue

- `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE` — Build every v3 role's instructions, schedule, token cap and off switch, GPT-reviewed, ready for the three-wave go-live after the Wed reset (Wed: Dispa
- `DISPATCHER_RECOVERY_PROVE_BG_SURVIVES` — Prove recovery via claude_bounded.sh --bg --remote-control survives the oneshot unit, before recover_dead under --apply
- `DOORBELL_HARDEN_SPARE_OWNER_TYPING` — Doorbell ring can wake a window the owner is typing in (asyncRewake has no focus check)
- `DISPATCHER_HARDEN_OWNER_RETURN_AFTER_RING` — Owner presence checked only at ring time; next may hand out game work after he returns
- `V3_ROLES_DESIGN_INTERIM_HOLDER_PER_DUTY` — v3 activation table: duty, interim holder, cadence, independent checker, handover version
- `RULINGS_BUILD_STATE_RECONCILER_NEWEST_WINS` — Ruling-vs-state reconciler in the Dispatcher measuring arm: holds each enact item open until state matches
- `DISPATCHER_BUILD_OUTSIDE_DEADMAN_HEARTBEAT` — External dead-man heartbeat for dispatcher.py and ops_watch
- `CANON_BUILD_SWEEP_WHEN_CANON_MOVES` — check_canon.py sweep when canon.yml moves, on commit, and nightly
- `FOCUS_ENFORCE_HEADLESS_LAUNCH_ALLOWLIST` — Headless launch allowlist plus foreground-change probe for unattended tools
- `EXACT_SOURCE_PICK_VERIFY_DISABLED_FIRST` — Exact path: a dry dug cell picks the first unsealed cardinal source; if that body is disabled (or its fluid unclaimable) an enabled source on another 
- `RIMFLOW_ARBITER_MEASURE_FALSE_REJECTS` — Before v3.3: measure Arbiter false-reject rate and per-verdict token cost, and define what 'batches daily' saves; sim says under today's quotas the Ar
- `RIMFLOW_AUDITOR_RETHINK_DAILY_CAP` — v3 Auditor: 4/day cap plus throttle pause leaves it ~4 audits/week vs ~200 escapes; lift the cap or drop the role (finding 8, design/RimMandrake/rimfl

## Commits

```
5ceafc6b41 conversations: catch-up 2 record(s)
751694f9b6 ledger: BENCH sync (sha note)
84e61e6664 ledger: BENCH sync (sim item close, 2 follow-up items)
fdd6b05c0c rimflow v3 sim: isolate/auditor_cap experiments, end stocks, findings doc after GPT round 3, lesson
916d7992e7 ledger: RUNNER ingest of 1 testq job(s)
c93c543ec8 rimflow v3 sim: factory in a bottle (DES of the RimFlow process), params with provenance, selftest
12b311b3e3 ledger: RUNNER ingest of 1 testq job(s)
f2de7fba6f ledger: RUNNER ingest of 1 testq job(s)
15d485b421 ledger: RUNNER ingest of 1 testq job(s)
d77f5153da ledger: RUNNER ingest of 1 testq job(s)
c47ad028ba ledger: r12 bridge release; NEXT notes on excavation and roast stick
caa9a9e475 BENCH r12 live: Excavation re-measure 1.05-1.18 ms/tick (bar missed), roast FoodPoisonChance error remains; FlowWorks DLL rebuilt from 45d3bb0f89; lessons filed
121d7fbaec ledger sync: ops watch live, alarms filed, NEXT on V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE
f931dff539 ledger: ops_watch alarm(s) OPS_RUNWAY_RESCUE_E2BB
4ad91f2263 pulse deploy: sparse checkout holds Utils/sim (ops_watch's Codex reader was ModuleNotFound under the timer)
00655b16ad ledger: ops_watch alarm(s) OPS_RUNWAY_RESCUE_77F2, OPS_RUNWAY_RESCUE_C01D
150ed8028e ledger sync + code review: ops_watch.py CLEAN (GPT round J); allocator findings filed
fc5e99d6b2 slot_allocator: refuse a mode-only override that names a seat (GPT round O #1)
f84c4fc085 slot_allocator/csuite: GPT round N fixes (unmeasured count holds PAYDOWN; override seat names validated and upper-cased; csuite finite-number check on both windows)
b33931c5c7 ledger: RUNNER ingest of 1 testq job(s)
... 39 more: git log --oneline 1c18b080b8..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-27T08:03:06Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M infrastructure/state/ledger/events/OWNER.jsonl   BENCH (committed after the skeleton, 0245e6157d)
```

