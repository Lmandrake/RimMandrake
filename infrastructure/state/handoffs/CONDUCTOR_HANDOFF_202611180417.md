# CONDUCTOR_HANDOFF_202611180417 — READ FIRST on wake

Follows `CONDUCTOR_HANDOFF_202611180140`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
🔴 **THE PIPELINE DOOR IS RED ON `origin/main` ON THIS MACHINE, AND IT UNDOES YOUR COMMIT.** A judge-only change
to `bar_rule.py` was refused twice tonight by door tests it cannot possibly reach, and each refusal ran
`git reset --soft` on the commit I had just made. Four door tests are red on base here:
`selftest_dispatch_two_games` (6 FAIL darwin, **5 FAIL in a Linux container too** — a real defect, not a platform
artifact), `selftest_maturation_dispatch` (CRASH, uncaught OSError), `selftest_designer_stage` (2 FAIL on a
hard-wired `/home/mandrake/rm/bench` path that does not exist here), and `selftest_seat_restart(+_death)` until I
fixed those two.
**The method that works, and the only one you should use:** stash exactly your own paths, re-run the same command,
and compare the FAIL lines. Then land with `RM_PUBLISH_SKIP_PIPELINE_CHECKS="<why>"` naming a pinned evidence file,
after running by hand every door test that actually reads a file you changed (`publish.pipeline_selection` +
`door_inputs` tell you which — it selected 47 for a four-file judge change, of which 10 genuinely read my files and
all 10 were green). ⛔ **Never relax a door test you have not diagnosed.** Evidence:
`Transient/judge_tickets_door_state.txt`; ticket `RIMMANDRAKE_REPAIR_TWO_GAMES_DOOR_TEST_BLOCKS_EVERY_PUBLISH`
(its criterion A4 is the door learning to say "already red before your change"). (filed: lessons)

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. 🔴 **The soak is RUNNING and nothing is owed to you — the last handoff's "it died, please restart it" was
   wrong.** Measured 2026-11-17 19:31 PST through the only route that works from this Mac: run
   `S20261118T012929Z`, 72 h to 2026-11-21T01:29:29Z, resumed after the 01:39:36Z reboot (which is exactly what
   `c62f5f5d2a` was built for), at pass 8, **0 fails**, one `prime95.exe` live, CONTROL passing twice, vcore
   1.001–1.028 V (inside the post-raise band). Evidence `Transient/steve_soak_live_20261117.txt`.
   **Why two sessions got this wrong:** `soak_read.py` cannot reach SteveDesktop from the Desktop at all — the bare
   host `stevedesktop` resolves only in Archmagi's ssh config and the tailnet IP times out, because this machine's
   only tailnet route is inside the Colima container. It honestly answered `UNREACHABLE … nothing is known`, exit 3,
   and a reader turned two of those into a claim about the CPU. Ticket:
   `RIMMANDRAKE_ROUTE_SOAK_READ_VIA_TAILNET_DESKTOP_SEES_NOTHING`. The working route, for any Steve question:
   `docker exec tailscale-gmail tailscale ssh stevedesktop-wsl "<cmd>"`, reading `C:\…` as `/mnt/c/…`.
2. **The NVMe hunt is closed on measurement and the pointer was wrong twice.** There is **no Samsung 970 in the
   machine** — `Get-Disk` by serial reads a `KINGSTON SNV3S1000G` (1 TB, Healthy) and a WDC SATA, so the
   replacement the ledger ordered is fitted. And the 30328 `disk` events are **one repeated message**, `The device,
   \Device\Harddisk1\DR1, has a bad block`, not 30328 distinct blocks — exactly what the independent hardware review
   warned. **0 in the last 7 days against 3473 other System events** (the probe that makes the zero readable). This
   removes the SSD from the CPU-fault candidates on evidence, which that review said I had not earned. Closed at
   b7608ac8f754.
3. **`OPS_WRAPUP_SKIP_CLONES_OF_LIVE_FLEET_RUN` landed NARROWER than its own sentence, deliberately — your call if
   you disagree.** The ticket asked that a clone owned by a live *fleet* not stand as debris; measured, Greentide's
   fleet held its lock 09:03:50–09:23:00Z while the row was filed 09:39:11Z, so that bar would have suppressed a
   **true** positive and blinded `wrapup.debris_standing` for ~8 h across 23 mods. What landed is the per-mod phase
   gap. The fleet-wide version was not built; the stray-draft defect itself is `designer_cleanse`'s and wants its
   own ticket.
4. **Recalibration is owed before the judge's refusals mean anything.** `bar_rule.py` and `coverage_judge.py` are
   both in `refusal_contract.brief_hash`, so the coverage judge's brief is **UNTESTED** and its refusals stay
   advisory until `RIMMANDRAKE_RECALIBRATE_JUDGE_THEN_RESTAMP_PYRELANDS_ONCE` runs. Your 2026-11-17 card's four
   rules bind once the judge prompt is edited and recalibrated — that has not happened yet.
5. **A pointer that said you had decided something had not been decided by you.** The last handoff said you
   "answered **DECISION: yes**" on the coverage-judge-before-exam order; the ledger event (tsn
   1794793804486811354) is a **delegated evidence-for-ask** decision an agent took under your standing ruling and
   reported in a digest. The successor build ticket is now filed
   (`RIMMANDRAKE_REORDER_COVERAGE_BEFORE_EXAM_SIX_RETAKES_PAID`) and its spec says so in the first paragraph, so
   nobody later mistakes it for your word. It also flags that `maturation_autonomy.exam_gate` makes the judge skip
   on a not-passed exam — unmeasured counter-evidence that the builder must read before reordering.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `FIVE_LIVE_SUBAGENTS_AT_WRAP` — five agents were RUNNING when this was last updated (20:36 PST), each in a clone
  that must NOT be deleted; NEXT: for each clone below, run `git -C <clone> log --oneline -1` and if a commit is
  there, review it, run its verify command yourself, land it with `./publish`, record a level-tagged pass and close
  the item, then delete the clone (an empty clone whose agent is gone means the work is lost: re-launch it rather
  than believing a summary).
  - `RIMMANDRAKE_COUNT_ADVANCE_REFUSALS_SO_A_LOOP_RINGS` — `~/ClaudeWork/scratch/rm-rc-submit`, branch
    `remote/rimmandrake_count_advance_refusals_so_a_loop_rings`. 🔴 Its plan's own `--submit` test PASSES on base
    (the flag is ignored), so check the case it wrote really fails on base before believing the fix.
  - `RIMMANDRAKE_DRAIN_ITEMS_WAITING_ON_A_JUDGE_THAT_RETIRED` — `~/ClaudeWork/scratch/rm-drain`, branch
    `remote/rimmandrake_drain_items_waiting_on_a_judge_that_retired`. This one DOES write ledger events, in its own
    clone only. Accept a PARTIAL drain honestly reported.
  - `RIMMANDRAKE_TRACE_REPIN_FROM_FIRST_PIN_B_CHANGE_SKIPPED` — `~/ClaudeWork/scratch/rm-ticket-5`.
  - `RIMMANDRAKE_CHECK_SCOPE_SOURCE_EVENT_EXISTS_FAKE_ID_OPENS` — `~/ClaudeWork/scratch/rm-ticket-6`.
    ⚠️ Tickets 5 and 6 edit the SAME file (`designer_stage.py`), briefed about each other; land them one after the
    other and re-run the second's case after the first lands.
  - `RIMMANDRAKE_RESTART_GAME_AFTER_MAPDATA_TIMEOUT_THREE_JOBS_BURNED` — `~/ClaudeWork/scratch/rm-ticket-7`
    (`infrastructure/stevedesktop/worker.py`). Its second half was split out as
    `RIMMANDRAKE_SHORTEN_BRAKE_PASS_STEWARD_MISSED_ITS_BEAT`.
  🔴 **Measured, and worth distrusting:** at 20:36 PST the two oldest (rc-submit, drain) had been running ~95 min
  and had written **nothing at all** — no commit, no dirty file, no file in the clone touched since 19:14. That is
  not proof they are dead, but a RimMandrake subagent has hung for an hour on this kind of work before and lost
  everything it found. Check the clone itself, not the agent's word.
- `RIMMANDRAKE_DRAIN_ITEMS_WAITING_ON_A_JUDGE_THAT_RETIRED` — **43** open items (not the spec's 45/46) are blocked
  with kind `judge` on a retired Relentless judge; the acceptance test
  `src/RimMandrake/rimflow/acceptance/judge_blocked_drained_accept.py` reads `FAIL 43 open items wait on the retired
  judge`, exit 1, and wants `PASS 0`. An agent is working it (above); NEXT: when it reports, re-run that acceptance
  test in the main tree and accept a PARTIAL drain honestly reported — `SEKKULAATH_RISING_DESIGN_CRATER_EVENT` is a
  `judge_needed` block whose judge also retired and may genuinely need the owner.
- `RIMMANDRAKE_COUNT_ADVANCE_REFUSALS_SO_A_LOOP_RINGS` — the last handoff claimed this "has its acceptance test
  written"; **it does not**, and its item says so: the plan's own `--submit` test PASSES on base because the flag is
  ignored, so it is not an oracle. An agent is building the real case (above); NEXT: when it reports, check the case
  it wrote actually fails on base before believing the fix.
- `RIMMANDRAKE_REORDER_COVERAGE_BEFORE_EXAM_SIX_RETAKES_PAID` — filed tonight with four criteria and an acceptance
  test, the successor nobody had filed; unclaimed. NEXT: before writing code, read `maturation_autonomy.exam_gate`
  (line 369, wired 638) and decide whether the coverage judge's reading leans on an exam-passed tree — if it does,
  the reorder needs the owner, not a builder.
- `RIMMANDRAKE_REPAIR_TWO_GAMES_DOOR_TEST_BLOCKS_EVERY_PUBLISH` — filed tonight; `selftest_dispatch_two_games` is
  red on main (6 FAIL darwin, 5 FAIL on Linux), it is a door test, and the five core failures are his own
  2026-11-16 promise ("I don't want to hear any 'waiting for game'"). NEXT: settle whether the test or the two-game
  dispatch code is wrong — do NOT relax the test — and quote the evidence either way.
- `RIMMANDRAKE_SPLIT_RED_FROM_UNMEASURED_STATUS_ENTRY_LIES` — filed tonight, the RimMandrake half of the
  silent-failure audit: `modcheck.verdict_for` records `RED` for a real FAIL, for a suite that measured NOTHING,
  and for a gate that SKIPPED a chain, so 71 status entries cannot tell a defect from an unrun suite. NEXT: build
  it, and note criterion A4 — no input that reads non-GREEN today may read GREEN after.
- `RIMMANDRAKE_AUDIT_SILENT_FAILURES_IN_THIS_REPO` — **partly done**: `modcheck/status.py` audited (one real
  instance, filed above), and `deadman_check.py` + `fault_monitor.py` were read and are **clean** — that is `[]`,
  not `unknown`, and the detail is in the filed item so nobody re-reads them. The rest of the repo is unaudited;
  NEXT: audit the next narrow slice by hand (a broad subagent on this hung for an hour and lost its work last
  time), and file each instance as its own ticket.
- `RIMMANDRAKE_NAME_SOAK_SILENT_EXIT_INTERRUPTED_LOOKS_IDLE` — filed tonight with four criteria: the soak exits 0
  after `SOAK INTERRUPTED … steps=0`, so a soak dead in 28 s reads the same as one that never ran. NEXT: build it,
  re-reading the script first (`c62f5f5d2a` changed its defaults to 72 h / resume-after-reboot after the reading
  the ticket quotes).
- `RIMMANDRAKE_SPLIT_ONLY_NAMES_LONG_LIST_CRASHES` and `RIMMANDRAKE_LIST_WALK_SUITE_IN_HARNESS_MUTANTS_SURVIVED` —
  both filed tonight with reproductions: `run_selftests.py --only` with a long comma list dies `OSError 63`
  (`is_file()` on the whole string raises, and a raise is not "not a file"), and `plant_faults.py` consults 13 of
  29 suites so "survived every offline suite" is a claim about its hand list. NEXT: take either; both are small and
  self-contained.
- `TWO_PARKED_TO_THE_RESET` — `RIMMANDRAKE_EXPLORE_OPERATIONS_OPTIONS_AFTER_WEDNESDAY_RESET` (his words: *"Bring it
  back up then and we'll explore the options together"*) and
  `RIMMANDRAKE_REASK_FABLE_FROM_START_WHEN_MOD_IS_FREE`; Wednesday is the token reset day, not a deadline. NEXT:
  raise both with him after the 2026-11-18 reset — his call to open, not yours.
- `EVIDENCE_QUALITY_SPEC_0.3.0` — carried from the last handoff, untouched tonight: reviewed twice, nothing built,
  Part B withdrawn, Part A blocked because it changes POLICY (extra automatic attempts past the one-per-visit rule
  he bounded 2026-11-14). NEXT: put Part A's policy question to him before any code, then build change two first.
- `EK_FAULT_HARNESS_SCOPE` — `selftest_explosiveknockback_walk_raid.py` already kills both frame mutants but is not
  in `plant_faults.py`'s `SUITES`, so the ticket I closed tonight rested partly on a blind instrument (the work
  still stands: the judge genuinely had no offline oracle, and now has one with four unreadable-kind cases). NEXT:
  fold it into `RIMMANDRAKE_LIST_WALK_SUITE_IN_HARNESS_MUTANTS_SURVIVED` rather than filing again.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- A pipe ate the exit code I was about to report: `test | tail` said 0 while the drain acceptance test under it was FAILING with 43 blocked items (filed: `lessons/20261118T032319Z-UNSEATED-pipe-eats-exit-code-you-are.md`).
- The Desktop cannot ssh to SteveDesktop at all, so every Steve reading taken here is UNREACHABLE while the machine is up and the soak runs; the route is the Colima tailscale container (filed: `lessons/20261118T033258Z-UNSEATED-desktop-cannot-ssh-stevedesktop-at-all.md`).
- A handoff pointer's claim about the ledger is a claim, and two were wrong tonight (a missing acceptance test called written, a delegated decision called his) (filed: `lessons/20261118T032326Z-UNSEATED-handoff-pointer-s-claim-about-ledger.md`).
- `seat_restart._proc_stat` read only `/proc`, so on darwin it answered None and the code spelled that "pid gone before the kill" and FAILED the restart; `kill_pid` raised AttributeError, reading as CRASH (filed: `lessons/20261118T041633Z-UNSEATED-linux-only-reading-must-say-unmeasured.md`).
- The pipeline door is red on `origin/main` here and undoes your commit; prove innocence by stashing your own paths, then skip by name with pinned evidence (filed: `lessons/20261118T041633Z-UNSEATED-pipeline-door-red-origin-main-this.md`).
- `plant_faults.py`'s "survived every offline suite" is a claim about its 13-entry hand list, not the repo's 29 suites (filed: `lessons/20261118T032335Z-UNSEATED-mutation-harness-s-survived-every-offline.md`).
- A ticket's quoted base reading decays: the Graffiti ticket said 6 missed, 5 were, because two commits closed the sixth first (filed: `lessons/20261118T032335Z-UNSEATED-ticket-s-quoted-base-reading-decays.md`).
- `git reset --keep` refuses on an untracked file identical to the incoming blob but silently OVERWRITES an ignored one, and must never call an unhashable path identical (filed: `lessons/20261118T032341Z-UNSEATED-git-reset-keep-refuses-any-untracked.md`).
- The 46,000 NVMe "bad block" events were one repeated message on a drive that is no longer in the machine: verify by serial before spending a session on a symptom (filed: `lessons/20261118T033537Z-UNSEATED-46-000-nvme-bad-block-events.md`).
- A ticket's literal sentence can be the wrong bar; land narrower and say so on the item rather than implementing words against their own evidence (filed: `lessons/20261118T041641Z-UNSEATED-ticket-s-literal-sentence-can-be.md`).
- `modcheck.verdict_for` collapses "measured nothing", "gate skipped" and a real FAIL into one `RED`, while the machinery around it already keeps them apart (filed: `lessons/20261118T032924Z-UNSEATED-rimmandrake-silent-failure-audit-s-first.md`).
- `rimflow` refuses every verb without a seat: `RIMFLOW_SEAT=CONDUCTOR` is needed on each call in this window, `./game` included (see: the refusal names the three ways to set it).

## Commits

```
a2a8db9627 lessons: the door is red on main, a Linux-only reading must say UNMEASURED, and a ticket's literal sentence can be the wrong bar
cf45e88c1d ledger: the three reviewed branches closed, with their live promise and narrowing
cf4a8a4d02 wrapup: a clone a live cleanse run owns by flock is in flight, not debris
dbd5c89339 judge: a polish gap blocks on no look, and a repaired carried gap closes unclaimed
55722bc0f9 seat_restart: three Linux-only readings that reported verdicts on a Mac
17e23d67fe ledger: DISPATCHER notes (1)
412a1bcf64 ledger: DISPATCHER notes (1)
efc2cbceb0 seat_dirt: land 2 safe path(s) left in the seat clone (conversation records, filed item prose)
69db482f5a designer cleanse: TerminalBiomes converge round 1 (0 open)
4a0e04f971 seat_dirt: land 1 safe path(s) left in the seat clone (conversation records, filed item prose)
8ce22925c0 designer cleanse: Webwork converge round 1 (0 open)
b8be6bbab9 NVMe bad-block hunt closed on measurement, not argument
0ac68645a2 designer cleanse: Miasma converge round 1 (0 open)
7838ea8891 ledger: DISPATCHER notes (1)
b7608ac8f7 Steve NVMe: no Samsung in the machine, and the bad-block flood closed 2026-11-01
c5e8b50a03 ledger: DISPATCHER notes (2)
e5ac416c64 Steve soak IS running: the Desktop just cannot see it
0fea81942d ledger: DISPATCHER notes (1)
30a6e84b73 ledger: DISPATCHER notes (3)
8c548cb768 designer cleanse: LeaningScrub converge round 1 (0 open)
... 33 more: git log --oneline 7457b7695c..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Working tree clean.

