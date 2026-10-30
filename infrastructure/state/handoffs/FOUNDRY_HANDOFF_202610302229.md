# FOUNDRY_HANDOFF_202610302229 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610300444`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Every arena safety layer so far was found leaky by an INDEPENDENT tester after our own selftests and 2 GPT rounds passed (retired trees readable, public-repo git fetch, tester spend unmetered, planted AGENTS.md and ProgramData config steering the judge). Treat 'selftest green + GPT clean' as nothing: day-1 readiness needs independent tests per layer. (filed: lessons)

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- The stopping rule decides a true 1.5x only 28-40% of runs within 25-40 tasks/arm; the Conductor added a hard-cap pick clause and took the power question to you (thresholds unchanged).
- Same-user token risk ACCEPTED for the trial (Conductor, owner authority).
- A live arm needs a login token in its sandbox env; one small logged-in claude -p test is authorised.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- Run run_selftests.py --only with the selftest file stem or full path, not a bare short name (it rejects 'arena_testpilot'). (see: builder reports, lessons)
- ledger shards modified by --per-ruling/--owner-said land in OWNER.jsonl, not FOUNDRY.jsonl; commit both or publish aborts on pull. (filed: lessons)

## Commits

```
e356769f81 arena_tasks: vet hidden checks at base via the judge route, sibling-fix-in-base report, criteria never from the later ledger, remap verified by patch-id (PARTIAL)
557d2e86c7 ledger: FOUNDRY idle-down notes on arena sandbox items (A partial, B/C/gates not started)
2405375327 arena item A (ARENA_TESTER_SPEND_ENFORCE_METERED_HOME): tester/critic spend captured before root delete; meter blocks unmetered testers
c9086ced24 handoff: BENCH Conductor before account switch to system (arena day-1 gates with FOUNDRY)
1ea663cdd8 conversations: catch-up 1 record(s)
02f5410152 ledger: FOUNDRY note ARENA_JUDGE_PROGRAMDATA_CONFIG_STEERS (idle-down)
80dd01a245 arena GPT judge: refuse the call while codex's SYSTEM config layer is non-empty (PARTIAL, idle-down)
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
... 279 more: git log --oneline a4c494b150..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   other agents / earlier sittings (Transient scratch, not mine)
?? .claude.json   other agents / earlier sittings (Transient scratch, not mine)
?? "D:\\ClaudeWork\\rimmandrake\\foundry_arena\\gpt_review.md"   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S1_20261017T084726.txt   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S1_20261017T084802.txt   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S1_20261017T092155.txt   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S1_20261017T110253.txt   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S1_p00.png   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S1_p03.png   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S1_p10.png   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S1_p14.png   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S2_20261017T084824.txt   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S2_20261017T092355.txt   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S2_20261017T110404.txt   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S2_p00.png   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S2_p10.png   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S2_p30.png   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S2_p60.png   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S3A_p20.png   other agents / earlier sittings (Transient scratch, not mine)
?? Transient/fw_scenes/live/S3B_p06.png   other agents / earlier sittings (Transient scratch, not mine)
... 121 more uncommitted paths (by top-level dir: Transient 116, conversations 5): git status --short
```

