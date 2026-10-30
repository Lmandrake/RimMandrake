# FOUNDRY_HANDOFF_202610300444 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610261818`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The ARENA architecture-trial build (steps 1-8 of 16, design/RimMandrake/testpilot_merged_2026-10-29.md 6.3) is built but every module has an UNRESOLVABLE same-OS-user residual (arm agents run as uid 1000: token, judge dir, hooks, hidden checks can all be read or bypassed by a deliberately malicious arm). Each module's docstring says so plainly; only a separate OS user / root-owned signer / server-side GitHub rulesets closes it. Do not let a green selftest be read as 'unforgeable'. (filed: lessons)

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Owner decision: same-user token risk for the arena trial (accept, or give the harness its own OS user / per-arm credentials + GitHub rulesets).
- Owner decision: raw GPT tokens vs Claude ITE conversion for total_ite_mixed (ARENA_METER_BUILD_SPEND_BY_CLONE_PATH).
- Owner/Conductor: SEAT_MEMORY_DECIDE_KEEP_SHARED_STORE (store trial verdict GOOD, 769 GB saved).
- Owner: bottom cast tune-or-bless, thrixweave numbers, 7 escalated facing sets (older, still owed).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `ARENA_SWITCH_BUILD_ONE_ARM_LIVE_ONLY` — fix round 2 published 3c2d4aa8b972; NEXT: run the blind GPT review round 2, then record implemented/verify and release the claim
- `ARENA_RALPHA_BUILD_TESTER_PASS_EACH_BUILD` — fix round 1 published 5fcc20138ec3; NEXT: add "ralph_a_loop.py" to ENTRYPOINTS in arena_eventlog.py, then blind GPT review, then record implemented/verify
- `ARENA_TRIO_BUILD_CRITIC_ROUND_CAP_PARKS` — unclaimed, lease released; NEXT: claim it and spawn an Opus rm-builder with the item spec (steps 9-16 are ticketed ARENA_*)
- `ARENA_CONTROL_BUILD_V3_TESTER_AFTER_CLOSE` — unclaimed, lease released; NEXT: claim it, spawn an Opus rm-builder
- `ARENA_RALPHC_BUILD_BUILDERS_WAIT_ON_TESTERS` — not claimed; NEXT: claim it after ralph_a closes (Sonnet)
- `ARENA_METER_BUILD_SPEND_BY_CLONE_PATH` — built, A1 L2 live probe owed; NEXT: run a real 1-pass job in a fresh arm clone under /home/mandrake/rm/arena/<arm> once the arena root exists
- `ARENA_GATE_FIX_EVENTLOG_SELFTEST_CANT_PASS` — filed; NEXT: close it (arena_eventlog now accepts the gate runner, 85ecec3e5a) after confirming a gate run over an eventlog change passes
- `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL`, `GSS_SWITCHES_PROVE_LAST_FOUR_STANDING`, `FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS` (A2 needs a fresh full sweep), `CONTAGION_BURN_OFF_FIX_PAWN_WONT_WALK`, `GSS_FALLEN_WIRE_FIX_SHOCK_HOTSPOT`, `FLOWWORKS_PUMP_FIX_POURS_BACK_STILL_THREE` — filed/open; NEXT: take them from rimflow next after the arena build
- Code review: all arena_*.py files and the touched gate/judge/replay/meter/switch files are DIRTY; NEXT: run code_review_status.py review before any mark-clean

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- Never start a private systemd --user/dbus from a seat Bash: it wedges the seat's cgroup (EBUSY clone3); recover by writing -memory to .../claude-code-bash/cgroup.subtree_control with the Write tool. (filed: lessons 20261030T034001Z)
- A targeted modcheck run does not run the site chain; the chain must retile itself. (filed: lessons)
- gpt_consult medium effort + 'do not run code' finishes; high effort timed out at 500 s. (see: foundry_arena/*_gpt_review*.md)
- Targeted blind-review loops do not converge on same-uid threats: stop at two GPT rounds and document the residual. (filed: lessons)

## Commits

```
3c2d4aa8b9 ARENA_SWITCH_BUILD_ONE_ARM_LIVE_ONLY: fix round 2 (production unit set, scoped restore, fail-closed evidence)
9196224243 ledger: FOUNDRY wrap-up, leases released
923ce748af ledger: BENCH ralph_c build note for tester, two filed follow-ups
92862d28f6 ARENA_RALPHC_BUILD_BUILDERS_WAIT_ON_TESTERS: ralph_c, two area-split builder loops on one board, runner back-pressure
328872c707 ledger: RUNNER ingest of 1 testq job(s)
5fcc20138e ARENA_RALPHA_BUILD_TESTER_PASS_EACH_BUILD: fix round 1 (quick-skip safety, blind tester cwd/env, group kill, anchored log)
d54f3b2ba4 ledger: RUNNER ingest of 1 testq job(s)
1feefe2a19 ARENA_SWITCH_BUILD_ONE_ARM_LIVE_ONLY: fix round 1 (hooksPath chain, alarm reader, trial units, wider unpushed check, switch lock)
8cef33b76a ledger: RUNNER ingest of 1 testq job(s)
33b78a86eb ledger: BENCH takes TESTPILOT, RALPHC, CRITIC_MEASURE to speed up the arena build
6d88a872d6 ledger: RUNNER ingest of 1 testq job(s)
78cf62ab64 ledger: RUNNER ingest of 1 testq job(s)
8028abb0d2 ledger: RUNNER ingest of 1 testq job(s)
cb913b4bc0 ARENA_RALPHA_BUILD_TESTER_PASS_EACH_BUILD: ralph_a loop with a blind tester pass per build
d830245dbe ledger: RUNNER ingest of 1 testq job(s)
ca21d07ca9 ARENA_SWITCH_BUILD_ONE_ARM_LIVE_ONLY: selftest expects arena.py in ENTRYPOINTS now
5e6cfcbf73 ARENA_EVENTLOG_BUILD_AGENTS_MAY_NOT_WRITE: let arena.py sign switch events
d32f81666d ARENA_SWITCH_BUILD_ONE_ARM_LIVE_ONLY: arena switch, who, units and pre-push hooks
3f75c00315 ledger: RUNNER ingest of 1 testq job(s)
f0647ce059 ledger: ARENA_REPLAY done; lessons (private systemd wedges seat bash; leak scan trusts arm marker)
... 1748 more: git log --oneline 4e62b5885d..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? "D:\\ClaudeWork\\rimmandrake\\foundry_arena\\gpt_review.md"   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S1_20261017T084726.txt   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S1_20261017T084802.txt   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S1_20261017T092155.txt   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S1_20261017T110253.txt   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S1_p00.png   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S1_p03.png   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S1_p10.png   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S1_p14.png   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S2_20261017T084824.txt   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S2_20261017T092355.txt   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S2_20261017T110404.txt   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S2_p00.png   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S2_p10.png   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S2_p30.png   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S2_p60.png   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S3A_p20.png   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S3B_p06.png   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
?? Transient/fw_scenes/live/S3B_p16.png   FOUNDRY (leftover of earlier sessions or agent scratch; not committed on purpose)
... 118 more uncommitted paths (by top-level dir: Transient 115, conversations 3): git status --short
```

