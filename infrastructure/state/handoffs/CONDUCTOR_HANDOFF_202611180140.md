# CONDUCTOR_HANDOFF_202611180140 — READ FIRST on wake

Follows `CONDUCTOR_HANDOFF_202611110123`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**"Could not look", "failed", "zero" and "empty set" are four different answers — and it is now a GLOBAL
rule, not advice** (owner, 2026-11-17; `~/dev/Lodestar/claude/global/36-distinguish-nothing-from-zero.md`,
rendered into `~/.claude/CLAUDE.md`, Lodestar `3b9feb4c`). Nine instances were measured in Dispatch in one
day and **four of them reported success**. All nine are fixed with 14 red-on-base tests (Dispatch `9d2599f`,
`05b278a`). The four variants, as a checklist against any tool you write or trust:
(1) the code COMPUTES the "could not look" case and then drops it from the exit expression;
(2) two causes share one code (an auth check returned "signed out" for "unreadable");
(3) a failure is stored AS CONTENT (a dead judge scored a model 0/10, and `overall or 0` then ranked it worst);
(4) output is written BEFORE the failure check (a banner on stdout, then exit 4 — a non-empty file with no
answer in it, which survives an is-non-empty check and is worse than an empty one).
🔴 **And the one that bit me personally:** `cmd > log 2>&1; echo "exit=$?"` reports the **last command's**
status, not the tool's. That single shell habit hid four consecutive consult failures and I reported one of
them to the owner as if it had run. Capture it immediately (`cmd > log 2>&1; rc=$?`) and prefer a tool that
prints its own verdict line. Full checklist: `infrastructure/state/lessons/20261117T225720Z-UNSEATED-all-nine-silent-failure-instances-found.md`. (filed: lessons)

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. 🔴 **The soak he started at 01:29:32Z DIED 28 SECONDS LATER and is NOT running** (measured
   2026-11-18T01:30Z, three ways: no `prime95.exe` in `tasklist`, `SOAK INTERRUPTED … steps=0` as the log's
   last line, no STOP file). Its positive control passed first (`inject_fatal_seen=1 inject_died_seen=1
   heat_seen=1 load_seen=1 load=100 ok=1`), so the instrument is not blind — it just exited. **The same thing
   happened on the first attempt six hours earlier** (`SOAK END steps=0 passes_started=1 reason=`, empty
   reason) and a retry 22 s later ran 32 steps fine. He was told; the restart is his or the next session's.
   I could not read `schtasks /query` (Access denied: the task runs as SYSTEM, my SSH session is not elevated).
2. **The +0.100 V BIOS raise DID take effect and cut the fault rate ~20x, but did NOT cure it** — and this
   corrects two earlier claims in our own files (`45e7142d14`). Uptime-MATCHED (his question: isn't this just
   because we're barely using it?): **34.6% of cycles bad before (575/1661) vs 1.8% after (2/113)**, both
   restricted to boots under 5.2 h. P(≤2 bad | the old rate) = **2.6e-18**, so the improvement is real.
   BUT the 95% upper bound on the true post-raise rate is **5.5%**, so a cure is NOT established; only the
   72 h window to **2026-11-20T15:33Z** settles it. A superseded note said "the raise is not visible in
   vcore" — it compared a mean to a single sample; what actually changed is the vcore SPREAD (1.004–1.332 V
   → 1.016–1.037 V) and package temp (42.8 → 36.1 °C mean).
3. **Do not buy the i9-10900K yet.** An independent hardware review (filed:
   `infrastructure/state/evidence/STEVE_CPU_SWAP_SECOND_OPINION_2026-11-17.md`) puts a swap at only
   **40–60%** likely to fix it, splits cause CPU 45% / board-VRM 30% / RAM 10% / PSU 5% / other 10%, and says
   plainly *"I would not spend a nonreturnable $400 yet."* Its line worth keeping: *"No free software test
   cleanly separates marginal CPU silicon from marginal VRM delivery. Controlled substitution does."*
   My own earlier CPU-mechanism argument was judged the weakest part of my analysis and I accept that.
4. **Spec `design/specs/2026-11-17-evidence-quality-three-changes.md` is at 0.3.0 and NOTHING in it is built.**
   Two independent blind reviews (the second never saw the first) corrected the writer twice. **Part B is
   withdrawn.** Part A is a **POLICY change** presented as a records change — it authorises extra automatic
   attempts past the one-per-visit rule he bounded 2026-11-14 — so it needs **his word** before anyone builds it.
5. **375 of 1363 live-proof rows are unaccounted for** (195 PASS + 134 FAIL + 659 UNMEASURED = 988). No
   revised quality percentage should be published until they are identified.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `REMOTE_WORK_QUEUE` — **the owner's standing order for the next session**: work the tickets in
  `infrastructure/state/remote_work.md` by the rules captured there (one ticket, one commit, branch
  `remote/<id lower>` off current `origin/main`, never push `main`, test-first with the case watched failing
  on base, no ledger writes, no game, no `C:\`, no `modcheck run`). He says it is safe to do from this
  terminal. Order: tickets 1, 2, then **8 and 9 before 3–7**; NEXT: read `remote_work.md`, then
  `cli.py show RIMMANDRAKE_UNBLOCK_PUBLISH_UNTRACKED_FILE_EQUALS_ORIGIN_COPY`, and build ticket 1.
- `STEVE_SOAK_NOT_RUNNING` — started 01:29:32Z, dead by 01:30:00Z with `steps=0`, no STOP file, positive
  control passed; the 6-hours-earlier attempt failed identically and worked on an immediate retry; NEXT: ask
  him to re-trigger the `SteveDiag CPU Soak` task (a SYSTEM task I cannot start unelevated), then confirm
  `prime95.exe` is in `tasklist` and the log is growing past `steps=0`.
- `STEVE_SOAK_SILENT_EXIT` — a soak that logs `steps=0` with an **empty reason** and stops is the same
  silent-failure class fixed everywhere else today; unfiled, no item yet; NEXT: file a ticket against
  `src/RimMandrake/Utils/steve_cpu_retest/steve_cpu_soak.ps1` to exit non-zero with a named cause (and note
  `c62f5f5d2a` changed its defaults to 72 h / resume-after-reboot AFTER my reading, so re-read it first).
- `RIMMANDRAKE_AUDIT_SILENT_FAILURES_IN_THIS_REPO` — Dispatch is done (9 fixed), **RimMandrake is NOT
  audited** for the same four variants; a subagent on it hung for an hour, found "one strong instance", never
  reported it, and was killed (work lost); NEXT: audit `modcheck/status.py` (`verdict_for`, `step4_live` —
  they decide GREEN) and `deadman_check.py` / `fault_monitor.py` (they ring his phone) by hand, in a narrow
  pass, not via a broad subagent.
- `EVIDENCE_QUALITY_SPEC_0.3.0` — reviewed twice, nothing built, Part B withdrawn, Part A blocked on his word
  because it changes policy; NEXT: put Part A's policy question to him (may a pipeline-classified run not
  consume its visit?) before writing any code, then build change two first (self-contained, closed sets).
- `CHEAPEST_PIPELINE_WINS_UNBUILT` — two interventions that use machinery already present and were never
  built: `RC.submit` wiring (`RIMMANDRAKE_COUNT_ADVANCE_REFUSALS_SO_A_LOOP_RINGS`: refusals are checked today
  and never counted) and the fact that **`TESTPILOT_WANTED` already routes a defect straight to a sitting with
  no three-failure wait** (`testpilot_route.py:125`, measured); NEXT: build the `RC.submit` ticket, it has its
  acceptance test written.
- `RIMMANDRAKE_DECIDE_COVERAGE_LOOK_BEFORE_EXAM_SIX_EXAMS_RETAKEN` — he answered **"DECISION: yes"** on
  2026-11-16 with a NEXT to build the stage-order change, and **no successor item was ever filed**; NEXT: file
  the build ticket with its acceptance test and name his decision event as the authority.
- `RIMMANDRAKE_DRAIN_ITEMS_WAITING_ON_A_JUDGE_THAT_RETIRED` — 46 items blocked on Relentless's retired judge
  that nothing will ever lift; acceptance test already named
  (`rimflow/acceptance/judge_blocked_drained_accept.py`, wants PASS 0 waiting); NEXT: run the drain and close it.
- `STEVE_NVME_46000_EVENTS` — ~46,000 `bad block` events on the Samsung 970 since 2026-10-30, SMART counters
  empty, Health=Healthy, still unexamined; the hardware review says "46,000 events are NOT necessarily 46,000
  distinct bad blocks" and that I had not earned calling it unrelated; NEXT: back up first, then read the real
  NVMe error log by serial (not SMART summary) with a tool that supports the drive.
- `TWO_PARKED_TO_THE_RESET` — `RIMMANDRAKE_EXPLORE_OPERATIONS_OPTIONS_AFTER_WEDNESDAY_RESET` (his words: *"Bring
  it back up then and we'll explore the options together"*) and `RIMMANDRAKE_REASK_FABLE_FROM_START_WHEN_MOD_IS_FREE`;
  Wednesday is the **token reset day**, not a deadline; NEXT: raise both with him after the 2026-11-18 reset,
  his call to open.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- `gpt_consult.py` cannot run on this Mac at all and failed at exit 0 three ways; the working route is the `codex-consult` container (filed: `lessons/20261117T212809Z-UNSEATED-gpt-consult-py-cannot-run-work.md`).
- The silent-failure class is systemic, not a one-off: 15 found across Dispatch, 8 HIGH, with the four-variant checklist (filed: `lessons/20261117T225720Z-UNSEATED-all-nine-silent-failure-instances-found.md`).
- `findings_fold.py` already holds a same-failure comparator AND a pipeline-fault classifier that no `rimflow`/`modcheck` file reads (filed: `lessons/20261117T195942Z-UNSEATED-pipeline-already-has-same-failure-comparator.md`).
- e2e.com's replay cache is route-keyed, so it cannot apply to a re-rolling RimWorld map; import its three rules, not the framework (filed: `lessons/20261117T190600Z-UNSEATED-e2e-com-agentic-test-framework-evaluated.md`).
- `selftest_maturation_dispatch.py` read FAIL 12-of-12 off the game host (it asked the real `companion_current()`, which reads a Windows-only deployed DLL) and `selftest_mod_owner_hold.py` probed `/proc/self/fd`, which exists only on Linux: both reported FAIL having measured nothing (see: commit `165b38afa4a1`, which fixes both and adds a STALE-reading check so the stand-in cannot become a bypass).
- A filed item claimed **one** failing check in that selftest; twelve were measured, and the soak's record implied it was running 28 s after it died — believe the run, not the ticket (filed: `lessons/20261118T014146Z-UNSEATED-believe-measured-run-not-ticket-s.md`). (filed: lessons)
- `git stash` hit an index lock mid-run, left a dangling entry while the edits stayed live, and `stash pop` then refused; diff the stash against the working tree before dropping it, and prefer file copies for red-on-base checks in a shared tree (see: `design/RimMandrake/GIT_WORKFLOW.md`).
- `--sandbox read-only` gives the Codex model **no filesystem tool**, so a `-v …:/work:ro` packet is unreadable to it and it returns a polite refusal; inline the documents into the prompt (filed: the gpt_consult lesson above).

## Commits

```
c8d73d052d remote_work.md: add the judge ruling's two bug-fix tickets
903b277178 judge ruling by card 2026-11-17 on record; four build tickets with failing cases, recalibration owed
c3beaf61a7 remote_work.md: seven offline tickets offered to a remote builder, with its rules
c62f5f5d2a steve_cpu_soak: 72 h default, resumes after reboot, waits out jobs, keeps going past a FAIL, CONTROL at every start; soak_read.py reader
82bd1de950 seat_dirt: land 2 safe path(s) left in the seat clone (conversation records, filed item prose)
9ae57150a3 switching plan: steven keeps 25% overnight, no plan line Wednesday daytime (owner 2026-11-17)
832ca36f68 ledger: Graffiti re-pin item parked to Wednesday afternoon
050d36895a ledger: Graffiti soak fix approved by card, re-pin parked until the Wednesday resets
343177ae1c ledger: owner's judge ruling by card, soak re-run filed, incident acks
b5bb677d48 switching plan: system leaves at 1% (owner 2026-11-17); steven's 35% line made live in the week plan
23c9adaead seat_dirt: land 1 safe path(s) left in the seat clone (conversation records, filed item prose)
55f545f724 design: proposed plain-wording ruling for the judge (four rules, not adopted)
751c76a877 ledger: DISPATCHER notes (1)
45e7142d14 Steve fault: the +0.100 V raise DID take, and cut severity ~10x without curing it
d7b68a0c50 ledger: DISPATCHER notes (1)
571ed05788 ledger: DISPATCHER notes (1)
6fac175548 ledger: RUNNER ingest of 0 testq job(s)
15d60a3770 seat_dirt: land 1 safe path(s) left in the seat clone (conversation records, filed item prose)
3a340bc9da design: Fable independent review of the judge-strictness rulings (not adopted)
d48ce838b8 ledger: ops_watch alarm(s) note:STEVE_INCIDENT_UNCLAIMED:steve.incident_unclaimed_min
... 6312 more: git log --oneline cc117a6db0..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Working tree clean.

