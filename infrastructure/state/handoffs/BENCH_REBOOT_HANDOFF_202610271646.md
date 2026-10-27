# BENCH_REBOOT_HANDOFF_202610271646 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610270854`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**Wednesday wave 1 is ready to switch on, and the steps are written down**: `design/RimMandrake/rimflow_v3_golive_wave1.md` (07ea49e615) lists every command with its proof, pre-flight, rollback and the 48 h kill criterion. Do it after the weekly reset, in that order. The code passed six independent review rounds today (Q→X); every role except Operations is token-blind by the owner's ruling and that is enforced three ways: the launch message (only Operations gets token info), `digest_blind.md` built from an ALLOW-list, and `blind_view.py` over the queue and notes (63 hand-written leaks caught). Token-talk drift is measured by ops_watch (`tokentalk.*`, baseline BENCH ~2.6%, FOUNDRY ~1-3%).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Owner rulings today, all on the ledger as OWNER notes on `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE`: token duties split by kind (Dispatcher enforces caps and picks the account; Operations alone analyses burn; Producer drafts the cut list; Conductor brings it to him; everyone else token-blind); Arbiter weighs ALL evidence; Conductor sets the goals that drive the Producer, information flows up through the Conductor; GPT ≈ Opus, route by runway; max two helpers at once.
- Explainer set he approved: `design/RimMandrake/rimflow_v3_explainer_{code,flows,starts}.png`, `rimflow_v3_flows.svg` (2e3bc65bab). He asked for ASCII drafts before any further image spend.
- Account choice holds work and alarms instead of switching by itself (switching is machine-wide and can drop Remote Control); auto-switch only after that is shown safe.
- Arbiter starts ADVISORY Friday; the tiered design (`design/RimMandrake/rimflow_v3_arbiter_tiers_2026-10-27.md`) currently sends ~92% of claims to AI because no recorded evidence counts yet (review AB2 made shared-clone runs non-evidence). Simulator insight he asked about: on today's budget an all-AI Arbiter buys "less, later".
- Operations' daily cap raised 200k→300k so one alarm run fits after the scheduled runs (7ad8f9a548, delegated call).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `RIMFLOW_V3_BUILD_DISPATCHER_FIRST` — built, six review rounds, timer dry-run, runbook written; NEXT: after Wednesday's reset run `design/RimMandrake/rimflow_v3_golive_wave1.md` step by step (FOUNDRY clone pull + doorbell hook, timer --apply for wakes only, enable Conductor + Operations) and start the 48 h proof.
- `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE` — all six AI role files written (Conductor, Operations live Wed; Producer, Arbiter Fri; Auditor, Innovator Sun), all disabled; NEXT: get one GPT review round on producer.md, arbiter.md, auditor.md, innovator.md before Friday's enable.
- `EVIDENCE_TOOLS_WIRE_ISOLATED_CHECKOUT` — no live run counts as Arbiter evidence until tools run in an isolated checkout; direction noted on the item (b555b4dcad); NEXT: build the Dispatcher's per-claim isolated selftest run (independent seat, no AI) and measure checkout time and disk.
- `ARBITER_REDESIGN_RISK_TIERED_VERDICTS` — design + code fixed through reviews Y/Z/AA/AB (45eef6b97e), still DIRTY; NEXT: one more independent review (GPT if Codex runway ≥1) of close_evidence.py and arbiter_tiers.py at HEAD, then mark clean.
- `EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES` — untouched today (v3 focus by owner's order); NEXT: find why one pulse slice costs 161 ms live vs 2.6 ms offline.
- `ROAST_STICK_FIX_DISABLED_COOK_STAT_ERRORS` — untouched today; NEXT: suppress the FoodPoisonChance read for the roast-on-a-stick bill.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A word-denylist check passed a "token-free" digest that still said "93 % of the week used"; use an allow-list of fields (filed: lessons 20261027T144647Z).
- A first pre-screen hard-flagged 749 of 815 closes on a signal true 92% of the time; weight signals by rarity (see: AUDITOR_BUILD_PRESCREEN_CLOSES_NO_AI, 3f5773481c).
- Seat clones are shared by concurrent agents, so a test pass in one is not evidence for its sha; only isolated checkouts count (see: EVIDENCE_TOOLS_WIRE_ISOLATED_CHECKOUT).
- `run_selftests.py --only` takes file PATHS, not test names (filed: lessons 20261027T164656Z).

## Closed since the last handoff (20)

- `STEVE_LANE_UNSTICK_PAUSED_UNOWNED_A686` — 6087591e79
- `DISPATCHER_HARDEN_OWNER_RETURN_AFTER_RING` — 5c49a263a511
- `DOORBELL_HARDEN_SPARE_OWNER_TYPING` — 6357be7eac57
- `DISPATCHER_BUILD_OUTSIDE_DEADMAN_HEARTBEAT` — ed8954506864
- `DISPATCHER_BUILD_ROLE_LAUNCH_FROM_SCHEDULE` — 2b6857eafa43
- `DISPATCHER_RECOVERY_PROVE_BG_SURVIVES` — 2b6857eafa43
- `ROLE_CAPS_TUNE_ABOVE_RUN_FLOOR` — fab2c69088
- `ROLE_LAUNCH_DECIDE_SEAT_AND_GATES` — fab2c69088
- `OPS_WATCH_BUILD_TOKEN_TALK_DRIFT` — 2aa3d505dcc6
- `DISPATCHER_BUILD_PICK_ACCOUNT_FIRST` — b475fd5969
- `SLOT_ALLOCATOR_FIX_SITTING_ACROSS_SWITCH` — e3ae063457
- `DISPATCHER_BUILD_WEEKDAY_AND_EVENT_TRIGGERS` — 28fbc818e2f1
- `PRODUCER_FIX_SLOT_AFTER_BAND_SKIP` — 28fbc818e2f1
- `ROLE_VET_MODEL_TIERS_PER_POLICY` — 28fbc818e2f1
- `DISPATCHER_FIX_LENT_HOLD_ALARM` — 28fbc818e2f1
- `OPS_ALARM_ITEMS_PRUNE_FROM_BENCH_QUEUE` — 7f0b0a6abb
- `RIMFLOW_AUDITOR_RETHINK_DAILY_CAP` — c913fefb75
- `AUDITOR_BUILD_PRESCREEN_CLOSES_NO_AI` — b40e79af6b
- `CLOSE_EVIDENCE_BUILD_GATES_CAN_DECIDE` — e8196aa714d6
- `ARBITER_GATES_HARDEN_SIX_FAKES_PASSED` — c1acbe9cf52f

## Filed and still open (18) — the next seat's queue

- `SIM_TWIN_BUILD_BOTTLE_GETS_A_PULSE` — Digital twin: feed ops_watch's live KPI series into rimflow_v3_sim weekly — recalibrate on v3's real numbers, publish predicted-vs-actual per role, fl
- `QUOTA_ENFORCE_UNUSED_AT_RESET_WASTE` — Quota unused at reset counts as waste like running dry: in the Operations success test/forecast and in the slot allocator
- `OPERATIONS_MONITOR_ACCOUNTS_OFF_SHARED_TABLE` — Operations-only ledger item: the token-aware role's launch, finish and economy-pass notes land here, never on the shared V3 roles item that token-blin
- `ROLE_AFTER_SLOTS_UNIFY_WEEKDAY_KEYS` — role_launch after_slots keys drop the weekday (DATE HH:MM) while due keys keep it (DATE Wed 09:00): an after_role on a weekday-slot role never runs (r
- `SLOT_SITTING_FIX_UNMEASURED_START` — slot_allocator sitting_step: a sitting that starts UNMEASURED still under-counts its drop (review U F9 part 2, unchanged by 4ce07578be)
- `ACCOUNT_PICK_HARDEN_UNRESOLVED_CURRENT` — account_pick.py:113: an unresolved machine account (current None) still keeps with hold=False; hold it like a stale lent reading (review V, N1 LOW res
- `ARBITER_REDESIGN_RISK_TIERED_VERDICTS` — Arbiter by risk tier: deterministic gates decide the clear cases (selftests, validators, builds, north-star checks), the pre-screen ranks the rest, AI
- `PRODUCER_CAPS_DECIDE_EVENT_ROOM` — Producer daily cap leaves no room for event runs after a large 09:00 run; decide the caps before the Producer goes live (review V, V6 scenario 2; D:\C
- `HELPER_WAITS_FIX_CACHE_COLD_REWRITES` — Helper foreground waits longer than the prompt-cache lifetime rewrite the whole cached context; keep each wait under that lifetime (the measured share
- `PRESCREEN_SHA_FIX_BLIND_TO_FOUNDRY` — audit_prescreen.git_files looks only in the bench clone: 58 of 816 closes (7d) flagged sha_unresolvable whose commit is in the foundry clone; its evid
- `CLOSE_SHAS_AUDIT_NAME_NO_COMMIT` — 17 closes in 7 days (BENCH, e.g. 2727a45c4a, 8ab4647364, bac56b6b50) cite a sha present in neither the bench nor the foundry clone (all refs): find wh
- `BLIND_VIEW_FIX_DIGIT_IDS_UNMASKED` — blind_view prints digit-bearing ids whole since 4a357cb3df (withheld() only catches \d+K); withhold any id with a 2+ digit part other than a trailing 
- `CODE_REVIEW_WIRE_REVIEWER_SEAT` — code_review_status records carry only the recording seat, never the reviewer, so no review can be shown non-maker; arbiter tier 1 flags 129 of 194 ran
- `AUDITOR_BUILD_AUDITS_FILE` — D:\ClaudeWork\rimmandrake\auditor\audits.jsonl does not exist; arbiter_tiers now exits 2 without it (was silently read as nothing failed). Auditor mus
- `PRESCREEN_EPOCH_FIX_DST_HOUR` — audit_prescreen._epoch is one hour off under DST (local mktime on a UTC string); arbiter_tiers uses calendar.timegm, the prescreen still does not
- `CLOSE_EVIDENCE_WIRE_RUNNER_SEAT` — close_evidence records carry seat None (all 8 in the 7-day window), so arbiter G6_independent is UNMEASURED and no run can pass tier 0; record RIMFLOW
- `EVIDENCE_KEY_HARDEN_AGENTS_CANNOT_READ` — close_evidence v3 mac key (~/.config/rimmandrake/close_evidence.key) is readable by the same Unix user every agent runs as: an agent can still mint a 
- `EVIDENCE_TOOLS_WIRE_ISOLATED_CHECKOUT` — Make run_selftests, winbuild and validate_patch record from an isolated checkout (close_evidence.py isolated). Since 45eef6b97e6d (review AB2), runs i

## Commits

```
75c9504df8 conversations: catch-up 5 record(s)
b555b4dcad ledger: direction note on EVIDENCE_TOOLS_WIRE_ISOLATED_CHECKOUT
ca3287ff03 ledger: review AB fixes note (45eef6b97e6d), file EVIDENCE_TOOLS_WIRE_ISOLATED_CHECKOUT
45eef6b97e Close evidence v4 + arbiter: fix review AB's ten findings
634ae07afc ledger: RUNNER ingest of 1 testq job(s)
d1b861c9a7 ledger: RUNNER ingest of 1 testq job(s)
277a6528f0 ledger: close ARBITER_GATES_HARDEN_SIX_FAKES_PASSED (c1acbe9cf52f), file EVIDENCE_KEY_HARDEN_AGENTS_CANNOT_READ
c1acbe9cf5 Arbiter gates: refuse all six forged claims (review AA)
e021e189f9 ledger: file ARBITER_GATES_HARDEN_SIX_FAKES_PASSED (review AA)
2686174adb ledger: RUNNER ingest of 1 testq job(s)
23bd92b4f2 ledger: review Z fixes + WHO note (73a85b59c8)
07ea49e615 Add RimFlow v3 wave 1 go-live runbook
73a85b59c8 close_evidence v2: review Z fixes (F1-F10) and WHO ran it (seat, session, agent per line)
44155dc383 ledger: correct review-Y fix sha to 9f184eda9d
c373ed0ea5 ledger: review Y fixes note (80f6dd80fb), five findings filed
9f184eda9d Arbiter tiers: review Y fixes (14 findings) and G6 wired to close_evidence
8c76e85dbd ledger: RUNNER ingest of 1 testq job(s)
32ca578faa ledger: close CLOSE_EVIDENCE_BUILD_GATES_CAN_DECIDE at e8196aa714d6
e8196aa714 Close evidence per sha: selftests, winbuild, validate_patch and modcheck append one JSONL line per run
e1a45c6850 ledger: file CLOSE_EVIDENCE_BUILD_GATES_CAN_DECIDE
... 94 more: git log --oneline 2ae77062d9..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-27T08:03:06Z

Working tree clean apart from untracked `Transient/`.

