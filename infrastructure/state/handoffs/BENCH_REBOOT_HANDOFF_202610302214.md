# BENCH_REBOOT_HANDOFF_202610302214 — READ FIRST on wake

Follows `BENCH_HANDOFF_202610301448`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**Independent testing finds a real defect in almost every build, and fixes breed new small defects.** Today: 9 TestPilot rounds, and every arena day-1 gate (analysis, feed, judge isolation, sandbox) failed or went partial on its first independent test. The biggest: the replay pool was a stale 4-task report (fixed to 241), an unsandboxed builder could read the answer anywhere on disk, and a SANDBOXED builder could still `git fetch` the fix from the PUBLIC GitHub repo. Never tell Mandrake a day-1 gate is ready until a different agent has tested it. Subagents cannot reach Artifact tools (filed: lessons).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Trial is NOT at day 1.** FOUNDRY was told to idle down for the account switch. Remaining day-1 gates (FOUNDRY): sandbox fixes (harness runs arm code, egress allowlist to model API only, /var/log, env allowlist, 4 mutants) + tester-spend metering (ARENA_TESTER_SPEND_ENFORCE_METERED_HOME), ARENA_JUDGE_PROGRAMDATA_CONFIG_STEERS, pool vet (ARENA_TASKS_VET_CHECK_FAILS_AT_BASE etc.), then freeze.
- **Delegated calls he can veto** (all logged): hard-cap rule = simplest arm not credibly worse than control wins at day 3 (ARENA_ANALYSIS_RETHINK_POWER_BELOW_TARGET); same-user risk accepted for the trial; build-only tasks excluded from the pool; egress allowlist instead of making the repo private.
- **RimMandrake repo is PUBLIC on GitHub** while his global rule says repos are private; his call, not a trial blocker.
- **Owner rulings this session (verbatim, recorded):** strip owner-presence triggers ("I really, really need you to strip \"when I come back to the machine\" as an event for anything changing."); owner hold "45 minutes after my last interaction, or I deliberately release it"; Conductor authority (CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM); FOUNDRY questions route through the Conductor.
- **Mineral sheet still waits on his labels:** `D:\ClaudeWork\rimmandrake\mineral_matrix_2026-10-30\mineral_matrix_2026-10-30.xlsx`.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `TESTPILOT_FIX_ABORT_WRONG_SCENARIO` — done-verified (indep7 pass recorded this wrap); NEXT: nothing — leave closed.
- `TESTPILOT_FIX_CRASH_WINDOWS_IN_LEDGER_WRITES` — done; independently checked (testpilot_fixes/check, verify3) and live-checked where owed; NEXT: nothing — leave closed.
- `TESTPILOT_FIX_DRAIN_CHECKS_EVERY_SEALED` — done; independently checked (testpilot_fixes/check, verify3) and live-checked where owed; NEXT: nothing — leave closed.
- `TESTPILOT_FIX_FAILED_SAMEFP_REBUILD_RELOAD` — done; independently checked (testpilot_fixes/check, verify3) and live-checked where owed; NEXT: nothing — leave closed.
- `TESTPILOT_FIX_PERIODIC_CANARY_IN_PROOF` — done; independently checked (testpilot_fixes/check, verify3) and live-checked where owed; NEXT: nothing — leave closed.
- `TESTPILOT_FIX_RESOLVE_AFTER_CRASHED_PASS` — done; independently checked (testpilot_fixes/check, verify3) and live-checked where owed; NEXT: nothing — leave closed.
- `TESTPILOT_HARDEN_SELFTEST_MUTANTS_ROUND2` — done-verified (indep7 pass recorded this wrap); NEXT: nothing — leave closed.
- `ARENA day-1 gates` — FOUNDRY's, idling for the account switch; NEXT: on wake, read FOUNDRY's IDLE reply / seat log, then send an independent rm-builder tester for each gate it reports built (sandbox egress+harness+env+journal, tester-spend, PROGRAMDATA config, pool vet), and only then tell Mandrake day 1 is ready.
- `ARENA_CRITIC_MEASURE_PLANTED_DEFECTS_FIRST` — critic vs tester verified undecided (p=0.39); judge rates + sim re-run done by FOUNDRY and verified; NEXT: mark it implemented with --per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM citing 67926b5d29, 0d655e5d72, 2a708574c6, 13cef0c090.
- `FOUNDRY trial-only directive` — section at top of infrastructure/agents/FOUNDRY.md plus dispatcher_schedule.json seat_focus; NEXT: delete both on the day day 1 starts.
- `MINERAL_SHEET_REBUILD_FROM_PAINTED_MAP` — xlsx with him; NEXT: when he says done, read his edits from the xlsx and enact them.
- `FOUNDRY watch timer` — was a session cron (deleted at wrap); NEXT: on wake, recreate it (CronCreate every 15 min running the watch; script copy needed — the old one lived in this session's scratchpad), or build it into the Dispatcher.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Subagents cannot reach Artifact/ArtifactData; board writes stay top-level (filed: lessons).
- `--per-ruling`/`--owner-said` write OWNER.jsonl, which helpers forgot to commit and which blocked ./publish (see: .claude/agents/rm-builder.md).
- rimflow close recorded pre-rebase shas; close now refuses unpublished shas (see: CLOSE_SHAS_AUDIT_NAME_NO_COMMIT).
- Git tests against fake http servers popped Windows Git Credential Manager (filed: lessons).
- A helper refused an owner ruling relayed by the Conductor; agent defs now say briefs carry owner authority (see: .claude/agents/rm-*.md).
- An isolated Codex home is still steered by C:\ProgramData\OpenAI\Codex\config.toml (filed: lessons).

## Closed since the last handoff (2)

- `CRITIC_CALIB_REMEASURE_TIERB_AS_UNLABELLED` — 3c7429f5eafa
- `BRIDGE_FIX_RECHECK_LIVENESS_UNDER_LOCK` — edeef00b69

## Filed and still open (47) — the next seat's queue

- `TESTPILOT_FIX_ABORT_WRONG_SCENARIO` — Pilot.abort marks invalid the first scenario with no evidence, not the in-flight/decided one
- `TESTPILOT_HARDEN_SELFTEST_MUTANTS_ROUND2` — testpilot selftest: 18 of 31 independent mutants survive (M5 crash/quarantine, L10 live-fail park, L9a carry guards, S3 hot-apply mod set)
- `TRIO_ABSDIFF_VET_PARKED` — Trio parked TRIO_ABSDIFF after 4 rounds: look at trio/failed branch, then retry, split or drop
- `CRITIC_MUTANTS_DELETE_EQUIVALENT_M30` — mutant m30 is equivalent: zip(a[2:],b[2:]) sits only in the assert MESSAGE of selftest_reader_invariant._assert_same_world; assert a[1:]==b[1:] still 
- `CRITIC_CALIB_FIX_SMALL_N_INTERVAL` — arena_critic_mutants boot(): percentile cluster bootstrap is anti-conservative at 8 labelled originals and collapses to zero width at 0/n false reject
- `TESTPILOT_FIX_CHECKOUT_REFUSAL_LOOPS` — testpilot: a PilotRefused mid-act (e.g. _at_rev checkout failure in reload) bypasses the abort requeue budget: candidate stays queued forever, every p
- `TESTPILOT_FIX_QUARANTINE_SPARES_SIBLING` — testpilot M5/L10: quarantine/park sets item_parked but the item's other open candidate (a repair queued before) is still reloaded, tested and resolved
- `TESTPILOT_HARDEN_SELFTEST_MUTANTS_ROUND3` — testpilot selftest: 13 of 21 new independent mutants survive (n15 epoch check likely equivalent; 12 real gaps): abort attribution n1-n5 (in_flight ign
- `TESTPILOT_FIX_STALE_YIELD_KNOBS` — owner-presence remnants after the strip (no behaviour): testpilot_reload_rule.json still carries yield_bound_steps/yield_bound_s; design/RimMandrake/t
- `RIMFLOW_FIX_PER_RULING_UNCHECKED` — rimflow file --per-ruling accepts an id that names no item or event and stamps the event seat=OWNER (live: TESTPILOT_FIX_STALE_YIELD_KNOBS filed 2026-
- `OWNER_STAMP_FIX_UNWRITABLE_FAILS_OPEN` — A bare ./bridge whose OWNER_LAST_ACT.json stamp cannot be written only warns; an older readable stamp then lets a seat take his hold before 45 min (GP
- `HOST_OWNER_HOLD_ENFORCE_ACROSS_CLONES` — An OWNER hold on a non-Archmagi host (bridge take --host stevedesktop --seat OWNER) taken in the OTHER clone is invisible here until pushed: there is 
- `TESTPILOT_HARDEN_SELFTEST_MUTANTS_ROUND4` — testpilot selftest: 20 of 30 indep7 mutants survive (g10 g27 likely equivalent; test gaps, no behaviour defect) + presence remnants in fixture. D:\Cla
- `TESTPILOT_FIX_RELOAD_FOR_COUNTED_REBUILD` — TestPilot spends an R2 reload on a rebuild whose every scenario is already counted at its fingerprint
- `TESTPILOT_FIX_RESOLVE_AFTER_CRASHED_PASS` — TestPilot leaves a candidate testing forever if the pilot dies after its last PASS is saved but before _resolve: the next pilot goes idle
- `TESTPILOT_FIX_CRASH_WINDOWS_IN_LEDGER_WRITES` — TestPilot crash windows: wake clears in_flight before recording the interruption (crash record and requeue charge lost); reload not reconciled if the 
- `TESTPILOT_FIX_PERIODIC_CANARY_IN_PROOF` — TestPilot never runs the script canary inside a long scenario (design L8: before, after and periodically inside); _poll only checks ownership
- `TESTPILOT_FIX_DRAIN_CHECKS_EVERY_SEALED` — TestPilot R3 drain checks only the oldest sealed repair: a newer cheap repair past its 900 s max acceptance delay waits behind an older expensive one
- `TESTPILOT_FIX_FAILED_SAMEFP_REBUILD_RELOAD` — TestPilot still spends an R2 reload on a same-fingerprint rebuild of a FAILED parent: runs nothing, resolves fail (eb295521da covers only the all-pass
- `CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` — Ruling: Conductor instructions carry the owner's authority for every seat and helper
- `TESTPILOT_FIX_WAKE_RECONCILE_SKIPS_CARRY` — testpilot wake _reconcile resolves a same-fp rebuild with no carry decision/records (L9a bypass)
- `TESTPILOT_SELFTEST_HARDEN_DEDUP_ORDERING` — selftest_arena_testpilot: kill surviving mutants M06 M07 (interrupt dedup window) and M18 (most-overdue order)
- `TESTPILOT_SELFTEST_HARDEN_RECONCILE_CARRY` — testpilot selftest gaps on wake reconcile carry (low priority, no defect): surviving mutants N01 (reconcile resolves before carry: a carry decision is
- `TESTPILOT_FIX_MID_CANARY_COUNT_IN_EVIDENCE` — TestPilot evidence row does not record how many mid-proof canaries ran (only the first red); a green in-proof check is auditable only from trio.jsonl 
- `DISPATCHER_ENFORCE_SEAT_FOCUS_TRIAL_PREP` — Schedule seat_focus filters next/ring to in-focus items (FOUNDRY trial prep)
- `ARENA_SPEND_ROW_HARDEN_MISSING_GPT_FIELD` — arena_analysis.task_tokens: a spend row missing gpt_ite/gpt_ite_est is read as 0 (row.get(k,0.0)) and can decide; spend_census always emits all 3 fiel
- `ARENA_WINNER_ENFORCE_MEASURED_DQ_CHECKS` — arena_analysis: DECIDE_FOR_X fires while X's own publish or scope disqualification check is UNMEASURED (only listed in dq_unmeasured). Probes f/g: win
- `ARENA_CONTROL_HARDEN_ABSENT_NOT_NO_DIFF` — arena_analysis: with control v3 absent (or disqualified) the rule can never decide or test futility, yet --final reports HARD_CAP_NO_DIFFERENCE (probe
- `ARENA_ANALYSIS_WIDEN_JUDGE_GATE_ORDER_TESTS` — selftest_arena_analysis misses two mutants: last-judge-counts -> first-judge-counts (last.setdefault) and gate-after-judge accepted in dq_publish (dro
- `ARENA_GPTJUDGE_HARDEN_ISOLATED_CODEX_HOME` — GPT judge (codex.exe, unconfined Windows) shares C:\Users\Mandrake\.codex sessions+history with the v3/v3c arms' own gpt_consult calls and actively ru
- `PRESCREEN_SHA_HARDEN_CLOSES_NEVER_LANDED` — Auditor rule: close sha is not the landed commit (repeat x5). Add pre-screen HARD flags: sha_not_on_origin (sha exists but no origin/main branch conta
- `FINDINGS_FOLD_VET_NOTES_BEAT_THE_REVIEW` — The 61 RUNNER findings_fold notes of 2026-10-29T20:4xZ (retire/reopen) were written live by 4c0b13067d, before three blind reviews found 25 P1s incl. 
- `ARENA_TASKS_VET_CHECK_FAILS_AT_BASE` — arena census: run each hidden fix_test at base and fix; drop checks that do not discriminate
- `ARENA_RESOLVER_VERIFY_REMAP_BY_PATCH_ID` — arena Resolver: confirm a triple remap by patch-id (10k duplicate triples in old history)
- `ARENA_POOL_HARDEN_SIBLING_FIX_IN_BASE` — arena pool: a task's base can hold another pool task's fix and test; planner must not pair them
- `ARENA_TASKS_FIX_CRITERIA_FROM_LATER_LEDGER` — arena census: criteria fallback reads the final ledger manifest, not the one at close (latent, 0 tasks)
- `ARENA_SANDBOX_HARDEN_RETIRED_TREES_VISIBLE` — arena sandbox masks miss retired-trees (holds every replay fix, pinned) and ClaudeWork notes
- `ARENA_TESTER_SPEND_ENFORCE_METERED_HOME` — Arena tester spend is unmetered (HOME in deleted tempdir, RM_ARM stripped) yet analysis DECIDEs
- `ARENA_GPTJUDGE_HOME_FIX_AGENTS_MD_STEERS` — GPT judge home: a planted AGENTS.md steers the judge; verify_home passes and the tripwire is silent
- `ARENA_JUDGE_OWNPATH_TEST_PREFIX_SIBLING` — judge_env own-path sibling-prefix mutant survives; calib drops GPT vote tools record
- `ARENA_SANDBOX_HARDEN_GITHUB_PUBLIC_FETCH` — arm sandbox: github.com/Lmandrake/RimMandrake is PUBLIC; inside arm_sandbox.wrap 'git fetch https://github.com/Lmandrake/RimMandrake.git main' (no cre
- `ARENA_SANDBOX_HARDEN_JOURNAL_SYSLOG_READABLE` — arm sandbox: /var/log is not masked; inside the sandbox /var/log/syslog and the systemd journal (1.16M lines via journalctl -D /var/log/journal) are r
- `ARENA_SANDBOX_HARDEN_ENV_PASSED_WHOLESALE` — arm sandbox: sandbox_env passes the launcher env wholesale minus a deny list (ralph_a passes dict(os.environ)): AGENT_SEAT=BENCH, CLAUDE_CODE_MESSAGIN
- `ARENA_SANDBOX_HARDEN_FOUR_MUTANTS_SURVIVE` — selftest_arm_sandbox misses 4 of 10 BENCH mutants: --disable-userns dropped; WIN_FS branch of check_mounts dropped; the .credentials.json opt-in widen
- `ARENA_JUDGE_PROGRAMDATA_CONFIG_STEERS` — GPT judge: a %ProgramData%\OpenAI\Codex config.toml steers a fully guarded judge to a VALID vote (day-1 gate)
- `ARENA_JUDGE_MODELS_CACHE_MIDCOHORT_PLANT` — GPT judge: a models_cache.json planted mid-cohort steers the judge and passes every allow-list check (not day-1)
- `PLAYER_ROLE_DESIGN_EMPTY_CHAIR_AT_TABLE` — Innovation (agent/L, proposed): a Player role that plays the shipped savegame as a player and files what a player meets, not what a mechanism does

## Commits

```
b6c6ea03b0 conversations: catch-up 7 record(s)
81dbd97392 ledger: DISPATCHER notes (1)
a4a7c0e426 innovator run 2026-10-30: propose PLAYER_ROLE_DESIGN_EMPTY_CHAIR_AT_TABLE (agent/L); findings proposal -> accepted (superseded by fold)
99f57bd4ee verify ARENA_GPTJUDGE_HOME_FIX_AGENTS_MD_STEERS + ARENA_JUDGE_OWNPATH_TEST_PREFIX_SIBLING (BENCH independent): A2 pass; file ARENA_JUDGE_PROGRAMDATA_CONFIG_STEERS (day-1) + ARENA_JUDGE_MODELS_CACHE_MIDCOHORT_PLANT; arena_judge.py clean; lesson
b516f3774c ledger: DISPATCHER notes (2)
2117326365 ledger: judge home allow-list + own-path fix implemented
07f8f2fdb1 lesson: locked-down codex is still steered by instruction files (cwd AGENTS.md, home skills, models_cache templates)
1e41c7f1c7 arena GPT judge: allow-listed Codex home + cwd guard; separator-aware own-path test; calib keeps vote tools
5ca6ee89dd ledger: FOUNDRY claims and notes (arena sandbox gates)
bebb2df5fc verify ARENA_SANDBOX_HARDEN_RETIRED_TREES_VISIBLE (BENCH independent): fail; public GitHub fetch inside arm_sandbox gets the fix -> file 4 FOUNDRY items (github fetch, /var/log journal, env wholesale, 4 surviving mutants); lesson
dc3d0e495d arm_sandbox: blind GPT review r1+r2 fixes; file ARENA_SANDBOX_HARDEN_HARNESS_RUNS_ARM_CODE
a00247537a arena: arm_sandbox.py - one fail-closed bubblewrap choke point for every arm builder/tester launch
fd989ab300 verify ARENA_GPTJUDGE_HARDEN_ISOLATED_CODEX_HOME (BENCH independent): partial; planted AGENTS.md steers GPT judge -> file 2 FOUNDRY items; mark gpt_consult clean; lesson
78fad88c48 ledger: real shas on analysis items; hard-cap figures labelled 2-arm; tester-spend gate filed
9403f6cad0 arena verify (BENCH independent): part A pass, part B partial; file ARENA_TESTER_SPEND_ENFORCE_METERED_HOME for FOUNDRY; mark arena_analysis/arena_spend/spend_census clean; 2 lessons
3108d48c81 ledger: GPT judge isolation implemented; five reviewer items claimed
62d8f964f2 arena judge: isolated locked-down Codex home for the GPT judge + transcript tripwire
8d05198961 arena census review: mark arena_tasks + selftest clean; file 5 FOUNDRY follow-ups; census notes + Conductor build-only decision
be4a3aa1d7 arena census: exclude build-only tasks (Conductor decision); review fixes to Resolver, labels, rework order, pins
f90f7c404b ledger: close LIVEPLAN_FOOTPRINT_HARDEN_EMPTY_ELEMENTS
... 170 more: git log --oneline 51f380af20..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-10-30T18:01:27Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M deployed/config/ModsConfig.before-tier-visibility.xml   generated by modlist_swap during arena lane runs; disposable
```

