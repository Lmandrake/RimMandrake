# Second Windows workstation: would it pay? (study, 2026-10-24)

Written by a BENCH research helper, 2026-10-24 evening. Every number is cited to a file or command; where nothing
measured it, it says UNMEASURED. Nothing here touched the game, bridge, ModsConfig or deploy.

## 1. Owner's question (verbatim)

"You had previously given the suggestion that another Windows machine might help us advance by speeding up testing.
In the background, I'd like you to document the typical testing workflows we use and give details on FlowWorks and
Pyrelands and Gimme Slack testing. send that to GPT and ask the question "If we had another similarly capable machine
to Archmagi workstation, how would that have impacted our progress vs. the token cost required?" If it simply doubles
are progress but doubles token spend, that's only weakly useful. But if we could become more efficient per token in
terms of bugs closed, deployment progress, etc. that would be worth it. The computer exists and is powered off, the
question is "what would it take to bring it online and participating, would it be worth it, and how would we
accomodate the additional token burn given we already deplete 1.5 Claude Max accounts per week (at $200 level)?" then
file that report in the project and summarize it in bullets for me here."

## 2. The testing workflows we use today

Archmagi (this machine): Intel Core Ultra 5 245K, 14 cores / 14 threads, 63 GB RAM, RTX 5080, C: 2.2 TB free, D: 1.9 TB
free (powershell Get-CimInstance, 2026-10-24). One Windows RimWorld install (Steam, `C:\Program Files (x86)\Steam\...`),
1,270 workshop folders under `steamapps/workshop/content/294100`, the repo's own mods copied into `RimWorld\Mods`
(about 1.5 GB). Agents run in WSL2 seat clones (`~/rm/bench`, `~/rm/foundry`), scratch in `D:\ClaudeWork\rimmandrake`.

| Layer | What | Cost per run (cited) | Needs the game? |
|---|---|---|---|
| Offline selftests | `Utils/run_selftests.py --only <tests>`; full sweep nightly 03:00 (`rm-selftests-nightly.timer`, CLAUDE.md l.321) | seconds to minutes per test; FlowWorks stock C# SelfTest 8-9 min on 2026-10-24, not the "80 s" claimed (live_20261024/LOG.md l.9) | no |
| C# build and SelfTest | `Utils/winbuild.py` -> `dotnet.exe`, staged on D: | build ~1 min; SelfTest see above | no (Windows CPU only) |
| Deploy | `Utils/deploy_custom_mods.py` plan then `--apply` into the Steam Mods folder | full plan ~117 s after today's fix; before it, 158-448 s per plan (perf_audit_20261024/VERDICT.md; the 117 s figure is the task brief's, not re-timed here) | no, but a companion DLL can only be written with the game down |
| Cold load | `modlist_swap.py` swaps ModsConfig; relaunch | minimal 13-mod tier 22 s, tiers 22-90 s, full owner list about 15 min (brief) / about 25 min (skill rimworld-load-round); GAME_DRIFT, 14-24 DOWN transitions per day | is the game |
| Live driving | the RimBridgeServer (GABP) plus our JawaBench companion DLL; ONE driver at a time, held through `infrastructure/state/BRIDGE` (`rimflow bridge take/release`) | see section 4 | yes |
| modcheck | `Utils/modcheck` `run <Mod>`: static chain, then live rows on the smallest tier that loads the mod; REWRITES the live ModsConfig.xml (CLAUDE.md l.130); reports to `Transient/modcheck/<Mod>_<stamp>.json` | FlowWorks 2026-10-24: 345 PASS / 6 FAIL / 265 UNMEASURED before the rerun; 93 rows UNMEASURED only for "no live result at the current mod hash" (ledger FLOWWORKS_LIVE_ROWS_REMEASURE_STALE_HASH) | yes |
| North-star / validation_v2 / proof_hose / proof_all | scripted live proofs, one JSON result each; fresh map or a registered saved site (`test_site_saves.py`) | a proof_all run is 105-119 rows; see section 3 | yes |
| Companion test profile | time-boxed profile that arms the test tools; expires (renewed 18:00Z -> 23:00Z today) | minutes, but a stale one refuses the run | yes |
| Owner review | saves plus `human_review.py` sheets; owner looks, rulings come back as decisions JSON | owner time, not machine time | saves need the game |

Skills that govern it: rimworld-load-round (spend a cold load only when confident, batch by ambiguity),
live-debugging-proof-harness (classify MOD vs SITE vs HARNESS), rimworld-debug-testing (throwaway quicktest colonies,
no cold load), rimbridge (drive tools; "success" that did not move the game).

## 3. Per-mod testing detail

### FlowWorks (BENCH owns all of it, plus Gimme Some Slack; flowworks_lane.json)
- Offline: 29 `selftest_*.py` files in `src/RimMandrake/FlowWorks`, plus 107
  `.py` files in `FlowWorks/northstar/` (39 `selftest_*`, 52 `*_live`/`*_proof` drivers, and fakes: `fakegame.py`, `thirst_fake.py`,
  `sprinkler_fake.py`, `water_scenes_mock.py` run a mock game). C# `Source/` with a `dotnet` SelfTest
  (`selftest_flowworks_stock.py`) and an oracle comparison.
- Live: `validation.py` (1,463 lines, rivers/ponds/pits rows; `rivers_switch_flips` calls the SelfTest from inside the
  live runner, which stalled the runner for 8-9 min on 2026-10-24 while the game sat idle at tick 1:
  an offline cost charged to the live clock), `validation_v2.py` (63 core rows, `--live --fresh-map`),
  `validation_hose.py` / `proof_hose.py` (30 hose rows), and the single-topic live drivers in `northstar/`
  (`climb_proof`, `drawbridge_proof`, `deep_lake_proof`, `trench_*_live`, `raid_*_live`, `pit_rescue_live`,
  `thirst_live`, `sprinkler_live`, ...). Owner review sheets: `owner_review_stage.py`, `human_review.py`.
- Today (2026-10-24): modcheck run4 (rerun plus stale-hash v2/hose rows) is in flight; BENCH_RUN_1 ran 00:09-18:10Z
  across sections 2-7 (a 526-minute single hold), then a chain of 1-49 minute holds each starting with
  "FlowWorks redeploy" (ledger bridge events).
- Result mix: UNMEASURED is the dominant non-pass state: 265 of 616 modcheck rows. It is a live-time deficit, not a
  defect count.

### Pyrelands (fire biome; RM_Pyrelands plus 36 .cs files, `src/RimMandrake/Pyrelands`)
- Offline: `selftest_pyrelands_site.py` (1,402 lines), `selftest_pyrelands_fruit_clear.py`, code-review marks (all 36
  `.cs` files CLEAN, PYRELANDS_SHIP_READINESS_1).
- Live: `validation.py` (2,565 lines, run through modcheck on the smallest tier that loads the mod, which is the
  `pyrelands` tier), `preflight_pyrelands.py` gates A (session), B (site, after each fixture reload), C (post), run
  under Windows python.exe with the bridge held; `northstar_site.py` builds a player settlement on tile 3 so the map
  survives a save; `tick_rate_probe.py`. Review save `RM_pyre_review_20261015_r2`, owner approved every station
  2026-10-16.
- State: PYRELANDS_GREEN_MINIMAL_1 still "not green" at triage 2026-10-13 (burrowers_dive FAIL once, 6 UNMEASURED, a
  30 C control never run); PYRELANDS_GREEN_FULL_1 "needs a fresh full-list mapgen, no short check"; the 2026-10-04
  mechanics-first modcheck record is in foundry `Transient/modcheck/PyrelandsMechanics_20261007T204247Z.json`.
  PYRELANDS_TITAN_POPULATE_FIRE_NO_FOOTFALL is open. Typical cost: one cold load on a small tier plus site fixture
  reloads; a live-only half exists for grass census (r5: 58,052 things examined, 0 Bush) that takes one run.

### Gimme Some Slack (GSS, cords/wires; owned by BENCH since 2026-10-23)
- Offline: `proof_all.py --offline-gate` in WSL (seconds): validation O1-O8 incl. the C# SelfTest against a Python
  oracle plus mutation probe, `northstar_matrix/selftest.py`, `selftest_human_review.py`.
- Live: `proof_all.py --live` is "the ONE live proof" after the owner's densification (2026-10-05): loads the clean
  saved site `calm`, runs 105-119 rows; result files show 105/105 PASS (2026-10-11 twice) and 118 PASS + 1 UNMEASURED
  (2026-10-16 19:25). Also `validation_aerial.py`, `validation_style.py`, `live_probes/`, matrix runs, review sheets.
- Known limits are written down (`KNOWN_LIMITS.md`), so GSS rows are among the cleanest in the project: its live
  cost is steady, not exploratory.

## 4. Where the time goes (measured)

All from `infrastructure/state/ledger/events/*.jsonl` (bridge and game events), scripts re-runnable.

- Bridge held, hours per calendar day (sum of take->release spans, spans >24 h dropped): 10-19 14.7, 10-20 9.0,
  10-21 11.2, 10-22 22.2, 10-23 20.5, 10-24 17.2 (mean 12.4 h on the 30 active days since 09-24; 362 spans, median
  span 26 min, mean 62 min). Over 10-22..10-24 BENCH held 56.3 h, FOUNDRY 3.6 h, OWNER 0.1 h. So in the last three
  days the one live seat was occupied about 19 h/day, nearly all by one owner of the lane (BENCH owns FlowWorks and
  GSS by ruling, so "mutual waiting" was designed away by serialising on BENCH).
- Caveat that matters: "held" is not "busy". UNMEASURED: the fraction of held time the game was actually being driven
  (versus an agent reading, editing or waiting with the bridge still taken). The only direct sample: 2026-10-24 run
  "BENCH bridge run 1" held 177+33+59+121 min, and the 8:10Z hold stretched 526 min; the stall at 12:03 (LOG.md l.8)
  shows the game idle at tick 1 for ~8 min while the harness ran an offline SelfTest.
- Gaps between consecutive holds since 10-22: median 0.63 min, 33 of 50 gaps are <= 2 min. The bridge is handed over
  almost back to back: demand exceeds supply, there is no idle slack to harvest by scheduling better.
- Game process (game UP/DOWN stamps): UP 16-23 h/day on 10-18..10-24 (8.8 h on 10-17), with 7-24 DOWN transitions per
  day, 127 DOWN gaps since 10-17, median 4.5 min, mean 22 min, total 47 h of downtime in 8 days (restarts, deploy
  windows, cold loads). That downtime is where a second box could overlap work.
- Queue shape (ledger, 10-17..10-24): 1,040 items filed (BENCH 376, FOUNDRY 341, OWNER 323); by `needs`: offline 517,
  bridge 136, game-up 27, deploy 31, owner 91, unset 238. Live-or-deploy-bound items are about 19% of filed items
  but they are the ones that queue behind one resource. Closes in the week: BENCH 154, FOUNDRY 123, OWNER 37 (314).
  `verify` events: BENCH 232, FOUNDRY 151.
- Deploy: 158-448 s per plan before the perf fix; now ~117 s. Redundant second `tree()` pass and per-invocation
  `_def_guard` identified as the cost (perf_audit VERDICT.md top actions 1-2).
- Waiting on the bridge by non-holders: only 4 ledger notes in the week mention it in words. The cost of waiting is
  UNMEASURED, because an agent that sees the bridge held switches to offline work (the rule in the BRIDGE header)
  and the delay shows up as items parked "needs bridge", not as a wait stamp.
- This machine is also memory-bound for agents: memwatch cgroup counters show `claude-seats.slice` capped at about
  24 GB with `oom_kill` 5, and `rm-harness.slice` capped at 12 GB with `oom_kill` 3 (latest sample in
  `~/.local/state/rm-memwatch/samples.jsonl`). One box carries game, dotnet builds, hashing and the agents together.

Reading: the live game is a serial resource that is held most of the day by one seat; offline agent work (517 of 1,040 filed items are `needs offline`, about 50%; the remaining 238 unset and 91 owner-bound are not live-blocked by definition either, but are not proven offline-only) is not blocked by it; the queue of live/deploy-bound items and the 265 UNMEASURED rows is the visible
backlog that more live seats would drain.

## 5. Token side (measured from transcripts)

Source: `~/.claude/projects/-home-mandrake-rm-bench/**.jsonl` and `...-rm-foundry/**.jsonl`, `message.usage`, de-duplicated
by (message id, request id), days 2026-10-17..2026-10-24 (8 days). Subagent transcripts included (they are most of it).

| Slice | messages | output tokens | cache-write tokens | cache-read tokens |
|---|---|---|---|---|
| bench main | 3,290 | 2.07 M | 8.2 M | 818 M |
| bench subagents | 38,658 | 11.12 M | 139.2 M | 5,705 M |
| foundry main | 3,097 | 2.14 M | 9.3 M | 669 M |
| foundry subagents | 40,096 | 10.01 M | 156.5 M | 6,717 M |
| total | 85,141 | 25.3 M | 313 M | 13.9 B |

- Model mix by message: bench main is Opus 5.5 (3,279 of 3,290); foundry main is Sonnet 5.5 (3,083 of 3,097);
  subagents are mostly Opus 5.5 (32,397 of 38,658 in bench, 29,782 of 40,096 in foundry), Sonnet 5.5 the rest.
- Subagents are about 85% of output tokens and of messages. The spend is helper fan-out, not the two seat windows.
- Cache reads dominate by volume (13.9 B) as expected: the cost is how many calls re-send a growing context.
- Closed items in the same window: 314 (ledger `close`). So per closed item: about 80 K output tokens, 1.0 M cache-write,
  44 M cache-read tokens, 270 model calls (all division by 314; an item's cost is not attributable, since many
  calls are not item work: owner chat, sheets, art, consults). UNMEASURED: tokens per LIVE-run, tokens per item by
  `needs` class. The transcripts do not carry the item id; getting it needs the `Claude-Session` trailer matched to
  ledger events (a one-day job).
- Owner's figure, taken as given: about 1.5 Max ($200) accounts depleted per week. We do not convert tokens to dollars
  here; we have no plan-limit formula, only the observation that the limit binds.

## 6. What a second Windows box takes

What Archmagi depends on (measured by grep/ls): 46 files under `src/RimMandrake/Utils` hard-code
`C:\Program Files (x86)\Steam\...` or its `/mnt/c` form (for example `modcheck/patch_targets.py:39-41`); the bridge
lock `infrastructure/state/BRIDGE` and the rimflow bridge verbs are one global lock with no machine field; the
canonical test saves, companion DLL deploy, the test profile, ModsConfig, `deployed/config/*` swap files, the E:
telemetry inbox, the mirror `D:\Luke\dev\RimMandrake` and the systemd user timers (nightly selftests, mirror, pulse,
telemetry, scratch reaper) all live here.

Steps for a box B (effort in agent-days is an estimate, not a measurement):
1. Windows base: Steam login, RimWorld plus Royalty, Ideology, Biotech, Anomaly, Odyssey (DLC are assumed by ruling,
   so the second PC must own or share them; Steam family sharing blocks simultaneous play of a shared title under one
   library: LICENSING RISK, resolve before spending anything else), Harmony, the 1,270 workshop subscriptions (Steam
   downloads them; size UNMEASURED, du timed out at 90 s), the same Unity/Windows version. 0.5 day, mostly download.
2. WSL2 plus the toolchain: Ubuntu, python3, dotnet.exe SDK, git, the two seat clones, `~/.claude` skills and logins
   (Claude login is per account; the GenAI path comes from the environment, never a literal), SSH key to GitHub,
   tmux, Tailscale node for Remote Control (CLAUDE.md remote-access notes in Machinist). 0.5-1 day.
3. Storage root `D:\ClaudeWork\rimmandrake` (exists as a convention on B), `D:\Luke\dev\RimMandrake` mirror, E: telemetry
   inbox path or an override. 0.25 day.
4. Make the repo machine-aware. Today the path to the game is a constant in about 46 files; replace with one
   resolver (env var or `machine.json`). The bridge lock must become per machine: `BRIDGE.<machine>` plus a
   `--machine` flag on `rimflow bridge`. `deployed/config/` ModsConfig swap files, `companion_profile.json`, canonical
   saves and test-site saves are per machine or synced explicitly. 2-4 days of focused work plus selftests.
5. Ledger concurrency: the ledger is sharded per seat and merged by git, so two boxes need distinct seat names
   (e.g. BENCH-B) with their own shard and `./publish`; two writers to one shard from two machines would conflict.
   Ledger commits are local-only until published, so the `BRIDGE` mirror file can lag across machines. 1 day.
6. Divergence control: both machines must run the same mod hash. `deploy_custom_mods.py --apply` on each, plus a
   check that a result file records `machine` and mod hash (modcheck already keys "live result at the current mod
   hash"; add the machine). Save compat: test-site saves are git-tracked or copied by hash. 1 day.
7. The first useful job, a script-driven live sweep with no LLM in the loop (section 7 asks about it): needs a
   queue of rows, a runner that takes the per-machine bridge, and a result collector. The runners exist
   (`proof_all.py`, `validation_v2.py`, `proof_hose.py`, modcheck); the missing parts are the scheduler and result push.
Rough total 6-9 working days, most of it item 4 (a code change that reaches every seat), plus the licensing check.
Risks: path constant misses (a hidden `C:\` assumption silently deploys to the wrong machine); two bridges answering
on the same port number if both boxes are ever reached from one network name; a partial deploy on B making the
same row PASS on one machine and FAIL on the other (a harness-vs-mod misclassification); the owner's attention for
review saves does not double.

## 7. The question to GPT

Asked with `gpt_consult.py` (model per the script default), this study plus the supporting files attached:
the perf audit verdict, the agent policy, the live log, and the bridge/ledger miner script output. The question was the
owner's, verbatim, followed by four explicit sub-questions (a)-(d); the full prompt is reproduced under "GPT's answer".

### The prompt as sent

Attached: this study, perf_audit VERDICT.md, Agent_Policy.md, live_20261024/LOG.md. (Note: the sent copy of the study said "80% of filed items are offline-only"; GPT corrected that, see below, and the study now says 517 of 1,040 = about 50%.)

> OWNER'S QUESTION, verbatim: "If we had another similarly capable machine to Archmagi workstation, how would that have impacted our progress vs. the token cost required?" The owner adds: if it simply doubles our progress but doubles token spend, that is only weakly useful; but if we could become more efficient per token in terms of bugs closed, deployment progress, etc., that would be worth it. The computer exists and is powered off. The question is: what would it take to bring it online and participating, would it be worth it, and how would we accommodate the additional token burn given we already deplete 1.5 Claude Max accounts per week (at the $200 level)?
> 
> The attached study (second_workstation_study_2026-10-24.md) documents our testing workflows (offline selftests, C# SelfTest, deploy, cold loads, a single serialized live bridge, modcheck, scripted live proofs), the FlowWorks / Pyrelands / Gimme Some Slack testing detail, measured bottlenecks from our ledger (bridge held ~19 h/day by one seat over the last 3 days; game down 47 h over 8 days across 127 restarts; 80% of filed items are offline-only; 19% need bridge/game/deploy) and measured token use from agent transcripts (25 M output / 313 M cache-write / 13.9 B cache-read tokens over 8 days, 85% of it in subagents, 314 items closed). Please use those measured facts, and say where you are going beyond them.
> 
> Answer explicitly, in this order:
> (a) Would a second machine raise OUTPUT PER TOKEN (bugs closed, items verified live, deploys) or only output per DAY? Give a reasoned estimate and say what it depends on.
> (b) Which work would move to it (e.g. a dedicated live-test runner that only drives the game, batched rows, nightly live sweeps) so parallelism removes waiting rather than adding agents? Be specific about what would NOT benefit.
> (c) What it takes to bring it online: steps, effort, risks (Steam licensing and DLC on a second PC, save and mod-list divergence, two bridges, ledger concurrency, path constants hard-coded in ~46 tool files).
> (d) How to fund the extra token burn: e.g. tiering models down for live drivers, script-driven live sweeps with no LLM in the loop, fewer verify ceremonies, cheaper tiers per our model ladder (Agent_Policy.md attached). And what experiment would decide it (a 1-week trial with measured bugs-closed-per-token before and after): define the metric, the baseline, the stop/go thresholds.
> Finish with a one-paragraph verdict: worth it, not worth it, or conditional on what.

## GPT's answer

Raw, unedited (gpt_consult.py, default model, 2026-10-24):

**(a) A second machine could improve output per token, but only if it changes how testing runs. Simply adding another autonomous agent seat would mainly increase output per day—and could reduce efficiency through extra coordination, repeated verification, and larger contexts.**

The promising configuration is **a dedicated, script-driven test machine fed by the existing agents**.

Your measurements support that direction:

- BENCH held the bridge about **19 hours/day** over the last three days.
- **127 restart/down gaps consumed 47 hours across eight days.** A second game instance could continue testing during some of those interruptions.
- FlowWorks had **265 UNMEASURED rows**, including **93 lacking evidence at the current mod hash**. That is a verification backlog, not 265 bugs.
- Meanwhile, **85% of output tokens came from subagents**. Adding hardware does not require adding that same pattern of model calls.

Two qualifications limit the forecast. Bridge ownership is not measured game utilization; the eight-minute offline SelfTest inside a live hold demonstrates recoverable waste. Also, the ledger explicitly labels **517/1,040 items offline: about 50%**. About 19% are bridge/game/deploy-bound; the remainder are owner/unset. “About 80% not explicitly live-bound” is supported; “80% proven offline-only” is not.

My **planning estimates, beyond the measurements**, are:

| Configuration | Expected effect |
|---|---|
| Second machine, same agent-heavy workflow | More output/day; little reason to expect better output/token |
| Second machine as a scripted runner | Plausible **0–10% improvement in fleet-wide accepted items/token** from less recovery, repeated setup, and stale evidence |
| Scripted runner plus better batching, delegation, and verification discipline | **10–25% improvement is a reasonable trial target**, not an established forecast |

The hardware’s direct efficiency gain could be zero—or negative during setup. The larger opportunity combines automation and workflow changes, many of which should also benefit Archmagi alone.

For illustration, **20% more accepted work with 5% more token cost improves efficiency by 14%**: `1.20 / 1.05 = 1.143`. Doubling both produces no improvement.

Whether that happens depends on the number of ready-to-run jobs, actual game activity during bridge holds, how often evidence becomes stale before use, and whether failures require expensive exploratory diagnosis.

**(b) Move repeatable game execution to it; keep reasoning demand roughly constant.**

Initially, Archmagi should remain the interactive development and owner-review machine. Machine B should consume a queue of immutable test jobs:

`revision + deployed hashes + mod-list profile + fixture hash + suite/rows + timeout`

Existing agents submit jobs and receive results. A Windows process runs the tests without an LLM watching or polling.

| Work | Assignment and purpose |
|---|---|
| **Gimme Some Slack** | First commissioning workload: existing `proof_all.py --live`, clean `calm` fixture, known 105–119-row coverage. Its stable history makes infrastructure faults easier to distinguish. |
| **FlowWorks** | Batch `validation_v2`, hose proofs, and selected topic drivers by compatible mod-list tier and fixture. Prioritize release-blocking missing evidence, including stale-hash rows. Run the 8–9-minute stock SelfTest **before acquiring the bridge**. |
| **Pyrelands** | Reserve separate blocks for minimal-tier validation and fresh full-list map generation. Preserve preflight A/B/C and required fixture reloads. A short successful check must not substitute for the outstanding full-list proof. |
| **Nightly sweeps** | Run approved suites against a frozen deployed revision. Publish structured results and failure artifacts; request model attention only for exceptions. |
| **Deploy/load overlap** | B continues its frozen test batch while A restarts or deploys. B accepts its next revision between batches, rather than chasing every commit. |

Batch by **mod-list tier first**, then compatible fixtures. Do not skip required clean-site reloads merely to reduce loading.

The runner should produce JSON evidence, logs, relevant screenshots, and a single completion notification. It should stop on profile expiry, hash mismatch, indeterminate bridge writes, or failed preflight—not improvise recovery indefinitely.

Work that would **not automatically benefit** includes:

- Ordinary offline fixes and searches already progressing while the bridge is held.
- Design decisions, complex C# diagnosis, art judgment, and owner review.
- A single proof whose steps depend on one evolving game state.
- Repeating already-valid evidence without a changed dependency.
- Deploy hashing inefficiencies that should be fixed directly.

Moving builds or offline tests might relieve the measured memory pressure and OOMs, but their contribution to lost progress is unmeasured. That is a secondary benefit to instrument, not the main justification.

**(c) Bring it online in stages, with machine identity enforced before parallel operation.**

1. **Resolve simultaneous game access first.** Budget conservatively for a second Steam account with independently usable RimWorld and Royalty, Ideology, Biotech, Anomaly, and Odyssey. Steam Families requires another available copy for simultaneous play of the same game; DLC follows the selected copy, and mismatched DLC can affect saves. Confirm existing entitlements before buying anything. [Steam Families FAQ](https://help.steampowered.com/en/faqs/view/054C-3167-DD7F-49D4)

2. **Provision Windows and the execution environment.** Install the game, required Workshop content, matching game branch/version, Python, .NET SDK, Git, remote access, and WSL2 where the existing wrappers require it. Match the supported tool versions. A dedicated runner does not initially need two additional Claude seats or another paid account.

3. **Introduce one machine configuration resolver.** Audit the approximately **46 tool files** with hard-coded Steam paths. Centralize game, Workshop, repository, staging, saves/config, telemetry, and bridge locations. Matching today’s drive layout reduces migration work, but does not replace this audit. Every destructive/deploy operation should display and validate its target machine and resolved directory.

4. **Separate both bridges and their authority.** Give each machine a distinct endpoint and identity. The same port number on different hosts is fine; ambiguous host routing is the risk. Require explicit machine selection and verify the responding machine/session before writes. Use a machine-local authoritative lock or coordinator; a git-published `BRIDGE.<machine>` file alone can be stale and is insufficient for exclusion.

5. **Separate mutable game state.** Keep ModsConfig, swap backups, companion profiles, deployed manifests, output directories, and working saves per machine. Copy canonical fixtures by hash into disposable working saves. Prevent Steam Cloud or file synchronization from silently merging test state. Pin or detect Workshop changes before accepting results.

6. **Make ledger publication safe.** Give B a distinct seat/shard, such as `BENCH-B`. Never let two machines write the same shard. Publish results through an idempotent collector with unique job IDs; keep item ownership and closure authority explicit.

7. **Commission with equivalence checks.** Run the same frozen GSS job on A and B. Confirm game/DLC versions, ordered mod list, deployed content hashes, companion version, fixture identity, and result agreement. Then try a controlled restart and interrupted job to verify recovery and duplicate suppression.

The study’s **6–9 working-day estimate for a supported implementation is reasonable as a planning allowance**, not a measurement or guarantee. A narrow first sweep can arrive earlier by supporting only its required execution paths; completing that sweep does not mean all 46 tools support two machines.

The principal risks are wrong-machine writes, partial deployments, save/mod-list divergence, stale lock mirrors, and infrastructure failures being misclassified as mod defects. Preserve the MOD/SITE/HARNESS distinction. Owner attention remains a separate bottleneck.

**(d) Fund it first by redirecting existing usage, then consider a capped paid increment.**

The measured token burden is:

- **25.3 million output tokens**
- **313 million cache-write tokens**
- **13.9 billion cache-read tokens**
- **314 ledger closes across eight days**

That is approximately **80,600 output tokens, 997,000 cache-write tokens, and 44.3 million cache-read tokens per close**. These are fleet averages, not attributable bug costs.

The first funding measures should be:

- **No LLM during routine sweeps.** Scripts wait for the game, execute approved sequences, collect evidence, and notify once. Passing runs need no conversational supervision.
- **Apply the supplied model ladder to helper work.** Haiku for rechecked mechanical inventories/extraction; Sonnet for bounded implementation with a real compiler/test/validator catching errors; Opus for design, complex code, uncaught conclusions, and instrument-truth judgments. Resolve aliases through the existing dispatcher.
- **Respect the live-write restriction.** Agent_Policy.md explicitly forbids cheaper models for live bridge writes. Moving those writes to Sonnet/Haiku would require an explicit policy change. Existing approved deterministic proof scripts offer savings without introducing a cheaper model making live decisions.
- **Reduce redundant verification.** Adopt the audit’s one plan, one apply, accepted deploy verification; remove routine ad-hoc PNG hashing/XML censuses. Reuse valid suite evidence when dependencies are unchanged. Keep meaningful correctness gates.
- **Reduce helper context and repeated calls.** Give bounded tasks the needed files and evidence, return compact results, and avoid duplicate “reliability” agents. Cache reads dominate volume, but they are not priced identically to output or cache writes.

As an illustration—not a dollar forecast—cutting helper output by 10% would save about **8.5% of fleet output tokens**, assuming the measured 85% share persists. Track cache categories and quality as well.

For the trial, target **no increase in total weekly fleet usage**: fund B’s exception handling from these savings. Allow at most a separately measured **5% operational token-cost increment**, offset elsewhere. Extra hardware does not enlarge the same account’s allowance; Claude and Claude Code share plan limits. [Claude Code plan limits](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan)

If savings prove insufficient but efficiency passes the trial, use a small, explicitly capped usage-credit/API budget rather than immediately adding a full agent seat. Current usage credits support spending limits and charge at standard API rates beyond included usage. [Claude usage credits](https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans)

**“1.5 Max accounts depleted per week” is a capacity observation, not a $300/week bill.** It does not establish an API-equivalent token budget or how much another subscription would supply.

For the **one-week experiment**, use these definitions and thresholds:

| Measure | Definition and baseline |
|---|---|
| **Primary efficiency** | Accepted, deduplicated bug fixes per fixed token-cost unit. Report accepted non-bug items separately. Audit historical closes: **314 closes is not necessarily 314 bugs**. |
| **Token-cost unit** | Weight uncached input, cache writes, cache reads, and output by model using a frozen reference rate card. Include orchestration, helpers, retries, triage, and coordination on both machines. Also publish the raw token categories. |
| **Live progress** | Previously missing required rows resolved with valid evidence at the intended revision/profile/fixture. Separate PASS, confirmed defect, and unresolved. Repeated passes do not become new progress. |
| **Deployment progress** | Accepted release revisions reaching a predefined verified milestone. Copying the same build to B or repeatedly redeploying it is not another completed deployment. |
| **Quality** | Reopens, rejected closures, false passes, invalid results, and owner correction time. |
| **Resource use** | Actual game-driving time, lock-held idle time, queue delay, cold-load time, retries, and exception-triage tokens. |

The historical baseline is **39.25 closes/day**, approximately **275 per seven days**, with the token totals above scaled to the same duration. It lacks bug classification and live-run attribution; do not invent those baselines.

Before starting the seven operating days, add item/job IDs to usage attribution and run the new batching/verification discipline on **A alone** for a short baseline. Otherwise the comparison credits B for improvements A could deliver. Within the trial, use predefined comparable A-only and dual-machine blocks where practical, keeping model policy and task mix consistent. Report offline and live-bound results separately.

My proposed decision rules—**chosen thresholds, not measured facts**—are:

- **Go:** at least **15% better accepted bugs/token-cost unit**, at least **25% more useful live evidence/day**, no observed quality deterioration, and operating usage within the agreed cap.
- **Extend once:** 5–15% efficiency improvement with credible live gains, or too few comparable bug closures to decide. Do not extrapolate from a single successful batch.
- **Stop expansion:** under 5% efficiency improvement without a compelling release milestone benefit; token cost rises as fast as output; or sustained triage/invalid-result overhead consumes the gains.
- **Pause affected automation immediately:** wrong-machine writes or false acceptance caused by state divergence.

Record setup tokens and human effort separately, then include them in payback. A good operating week does not erase 6–9 days of setup. I would also require a credible path to recovering setup cost within roughly **eight weeks**.

**Verdict: conditionally worth it as a dedicated automated live-test runner.** The measured live backlog, bridge occupancy, restart downtime, and memory pressure justify a controlled trial, but do not establish a token-efficiency gain. Keep the existing reasoning capacity, move repeatable game execution to scripts, fund exception handling by reducing helper and verification waste, and expand only if accepted bugs per token improve materially. If the second box needs another continuously reasoning agent and proportionate token spend, it offers throughput rather than the efficiency the owner wants.

## Our read

Where GPT is right against the measured facts:
- Hardware alone buys output per day, not output per token. Our token bill is 85% subagent fan-out and 13.9 B cache-read
  tokens; a second box does not shrink either. It only helps per token if live work stops costing LLM tokens while the
  game runs (script-driven sweeps) and if less is re-done (stale hashes, repeated setups, recovery after restarts).
- Its correction of my "80% offline" figure is right: 517 of 1,040 filed items are `needs offline`; 19% are bridge, game-up
  or deploy-bound. I fixed the study. The claim "the bridge is the serial bottleneck" rests on the 19-h/day holds and
  the 265 UNMEASURED rows, not on item shares.
- "Held is not busy" is the key unknown, and it is ours to measure first: one cheap measurement (game CPU or tick rate
  against hold spans, or bridge call timestamps in the journal) tells how much of 19 h/day is actual driving. If most of
  it is idle holds, a second box is the wrong fix and a runner on Archmagi is enough.
- The 6-9 working-day setup, the licensing gate (a second copy plus DLC for simultaneous play), the per-machine bridge
  lock that cannot be a git-mirrored file alone, and a distinct ledger shard (`BENCH-B`) match what the repo needs.
- "No LLM in routine sweeps" is the real lever, and it needs no second machine to start.

Where GPT is wrong or has too little to go on:
- Its 0-10% and 10-25% efficiency figures are its own planning numbers. We have no measured tokens-per-live-row. Treat
  them as hypotheses the trial must test, not forecasts.
- "314 closes" mixes bugs with housekeeping (queue items such as sheets, ledger notes, art). The bug-fix share is
  UNMEASURED, so a bugs-per-token baseline does not exist yet; GPT is right that one must be built first.
- Agent_Policy.md forbids cheaper tiers for "live bridge writes" because that clause protects the hand-authored world and
  frozen saves (the rule says "the world is frozen and hand-authored"). Test drivers run on throwaway quicktest maps or
  registered clean sites, which that clause was not written for; but it is the owner's ruling, so any tier-down of a live
  driver is a policy change to put to him, not an agent decision. Deterministic scripts avoid the question.
- It frames token funding as "redirect existing usage". For us the weekly limit is already binding (1.5 Max accounts by the
  owner's figure), so a trial with a "no increase" cap is the right guard. Its suggestion of a capped usage-credit budget
  is workable only if the owner opts into pay-as-you-go; extra hardware does not enlarge the plan limit.
- It did not weigh that Archmagi is itself memory-constrained (claude-seats.slice 24 GB cap with 5 OOM kills,
  rm-harness.slice 3 OOM kills). Moving the game to B could improve agent reliability on A, a gain GPT calls secondary
  and unmeasured. Agreed: instrument it, do not bank it.
- Neither GPT nor the study measured owner attention, which caps review saves and sheets whatever the machines do.

## Recommendation

Do not buy time on setup before three cheap offline-to-A steps that every outcome needs:
1. Measure held vs driving (one afternoon, no new hardware): game tick or CPU against bridge-hold spans for the last 7 days,
   and join item ids to token usage via the `Claude-Session` commit trailer (also a one-day job). This produces the
   missing baseline (tokens per live-bound close, per bug fix).
2. Build the no-LLM live sweep on Archmagi first: one queued runner for `proof_all.py --live` (GSS, clean `calm` site),
   then `validation_v2.py` / `proof_hose.py` stale-hash rows, run between agent shifts with a single notification. Move
   the 8-9 minute stock SelfTest out of the bridge hold (the live runner calls it from `rivers_switch_flips`, wasting
   about 8 minutes of game time per run).
3. Check Steam entitlements for a second simultaneous copy of RimWorld plus all five expansions before touching the box.

The decision experiment (one week, after steps 1-3; setup tokens and effort counted separately and paid back within about
eight weeks, as GPT proposed):
- Week A (control, Archmagi only, runner and batching discipline already in): record accepted bug fixes (real bug classes,
  not housekeeping), live rows resolved at the current mod hash, deploys reaching verified, and a weighted token-cost
  unit with raw token categories, each per closed item via the id-join.
- Week B: machine B runs the sweep queue (GSS proof_all first, FlowWorks v2/hose stale-hash rows, Pyrelands minimal-tier
  blocks, then nightly), under its own seat shard and its own bridge lock, with no extra reasoning seat.
- Go if: accepted bug fixes per token-cost unit rise by at least 15%, useful live evidence per day by at least 25%, reopens
  and false passes do not rise, and weekly token use stays within the agreed cap (no growth, at most 5% offset).
  Extend one week if 5-15% or too few bug closes to decide. Stop expansion below 5% or if triage overhead eats the gain.
- Funding: tokens saved by scripted sweeps (no polling agents), single plan/apply deploys, retiring ad-hoc verify
  scripts, and the model ladder for bounded helpers; a live-driver tier-down only with the owner's say-so. If the
  experiment passes but the cap is tight, ask the owner whether he will fund a capped usage-credit budget.
- Owner decisions needed: (1) buy or share a second entitlement; (2) whether to open the "no cheaper tier for live writes"
  clause for scripted test drivers on throwaway maps; (3) go for the 6-9 day tooling work (resolver for ~46 files with the
  hard-coded Steam path, per-machine bridge) only after step 1 shows the bridge is busy, not merely held.

Evidence for this study is reproducible from the ledger (`event` in bridge/game/file/close), the transcripts named in
section 5, and the files cited inline. Scripts used were throwaway and lived in the seat scratch directory.
