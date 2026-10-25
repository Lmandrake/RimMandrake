# SteveDesktop: second test machine, bring-up plan (2026-10-24)

**Status:** plan only. Nothing is installed. Two items carry it:
- `STEVEDESKTOP_TRIAL_MEASURE_TOKEN_FREE_FIRST`: Wednesday 2026-10-28 after 16:00, after the accounts refresh. It runs on Archmagi only.
- `STEVEDESKTOP_BRINGUP_BUILD_SECOND_BENCH`: Friday 2026-10-30, once the owner can power the machine on.

The measured basis is `design/RimMandrake/second_workstation_study_2026-10-24.md` (bridge held about 19 h/day, held is not the same as busy, 127 restarts in 8 days, about 85% of tokens spent in subagents). GPT's enhancement pass is appended at the end of this file.

## Owner's facts and words, 2026-10-24

> The other windows desktop (we will call it SteveDesktop from now on) already has Steam and Rimworld using a different account, so a totally valid 2nd license already present. It is not as powerful as this machine but still strong and more than capable of running Rimworld plus some monitoring and control. It does not yet have WSL or any environmental configuration such as RimMandrake uses, but that's easy to install. … Both machines are on the same home internet network. We have root login on both.

> Do the tests and upgrade our testing such that it could be mostly token free.

Things this plan does not assume: whether that account owns all five DLCs (it must, per the every-DLC rule; check first), the SteveDesktop specs, and its Windows edition (UNMEASURED).

## Guiding principle: the second machine is a token-free runner, not a second agent farm

The study's conclusion was that hardware alone buys output per day, not output per token. So SteveDesktop's job is to **drive the game from scripts and write results as data**. Claude reads summaries, never transcripts of polling. LLM sessions on SteveDesktop are the exception: setup and debugging only.

## Phase 0: before power-on (Wednesday, on Archmagi, no SteveDesktop needed)

These steps are owned by the Wednesday item.
1. **Measure held vs busy.** Instrument bridge holds (from first to last bridge call per hold, and the game's tick advance per hold), and join token usage to item ids. Output: the share of the bridge hold that is real driving, and tokens per accepted fix.
2. **Build the no-LLM live sweep on Archmagi.** One script reads a run list (modcheck tiers, `validation_v2 --live --fresh-map`, `proof_hose --live`, Pyrelands tier blocks, GSS proof). It takes the bridge, launches the tier, runs the rows, writes a JSON plus a one-page summary, stamps the game down and releases the bridge. It has no Claude in the loop. A failure is a row, not a conversation. It prechecks the companion profile, which lapsed silently on 2026-10-24.
3. **Measure the token cost of a live run with and without the sweep.** The pass bar comes from the study: accepted bug fixes per token +15%, useful live evidence per day +25%, no rise in reopens or false passes.
4. **List deterministic, non-LLM jobs** that could run non-stop on a second box:
   - git health: fsck, stale-branch and untracked-bloat scans, committed files over 50 MB;
   - the full selftest sweep on every push rather than nightly;
   - deploy-plan drift (repo vs game) reports;
   - the def-guard, citation and live-proof lints;
   - stale-item and decay sweeps on the ledger;
   - code_review_status DIRTY census;
   - telemetry and RimPulse reports and visualisations;
   - disk and memory watch;
   - handoff `--check`.

   For each, record its current cost on Archmagi (CPU, memory, its share of the 5+3 OOM kills) and whether moving it frees Archmagi.
5. **Decide the Lodestar relationship.** Should SteveDesktop be a 4th Lodestar node (hourly sweep, board, registry) or a plain runner that Lodestar does not know about? Criteria: does it own any project (no), does it need the board (only to report runs), and what cross-machine sync cost would a node add? Write the decision as one line for the owner.

## Phase 1: power-on and communication (Friday)

1. Log in as the admin user. Name the host `SteveDesktop`. Give it a fixed LAN IP (a DHCP reservation on the router). Record the IP in Machinist.
2. Enable OpenSSH Server on Windows. Add Archmagi's `~/.ssh/id_ed25519.pub` to the admin `authorized_keys`. Test `ssh SteveDesktop` from Archmagi WSL.
3. Install WSL2 Ubuntu, then sshd inside WSL or a forwarded port. Install git, python3 and the gh CLI. Generate an SSH key and register it on GitHub as a read+push deploy key, or as the same account if the owner prefers.
4. Windows prerequisites: the .NET SDK (for winbuild and SelfTest), the Python for Windows that the tools call as `python.exe`, and the codex CLI only if GPT consults will run there.
5. Install the Claude Code CLI and log in (an interactive login, owner's hands). Do **not** turn on Remote Control there unless it is needed (see the RC skill's `/login` incident rule).
6. Firewall: allow LAN-only traffic for SSH and the bridge port.

## Phase 2: install the harness

1. Clone RimMandrake to `/home/<user>/rm/runner` (ext4). It is a third seat clone, **RUNNER**. It never edits src/ and never commits code, only results and ledger shard events.
2. Make the hard-coded Steam path configurable: about 46 tool files name `C:\Program Files (x86)\Steam\...` (MEASURED in the study). Use one config or env var, read through the agent-storage helper pattern. This is real tooling work and has its own item.
3. Set the agent storage root per machine (`agent_storage.py`) on SteveDesktop's own disk.
4. Install the RimBridge server and the JawaBench companion DLL into that game's Mods folder, and copy the companion profile.
5. Deploy: run `deploy_custom_mods.py --apply` locally on SteveDesktop from its own clone at a pinned origin/main sha. Never deploy across the LAN.
6. ModsConfig: SteveDesktop keeps its own and loads the tier the run list names. The canonical world saves stay on Archmagi only.
7. A RUNNER seat in the ledger: its own shard `infrastructure/state/ledger/events/RUNNER.jsonl`, which needs a rimflow seat registration.

## Phase 3: control, ticketing, results across two machines

- **The bridge becomes per machine.** `infrastructure/state/BRIDGE` is today one lock for one game. Use either `BRIDGE.<host>`, or a host field so that two games can be driven at once. It needs a rimflow change and selftests.
- **Control:** Archmagi BENCH queues a run list (a file in the repo, or a ledger event `run-request`). The RUNNER on SteveDesktop polls git, runs it, and publishes results plus a ledger event `run-result`. There is no LLM in that loop. SSH is the fallback channel for start, stop and status.
- **Ticket philosophy:** RUNNER never files design or fix items. It writes run results, and a failed row becomes one finding against the item it proves. Humans and BENCH triage. Live proof becomes data any seat can read.
- **Results:** they are JSON under a results dir in the repo, small and committed, keyed by mod-hash fingerprint, so a stale result is detectable (cf. the 93 FlowWorks rows with no result at the current hash). Big artifacts (captures, logs) stay on SteveDesktop's storage root, with paths in the JSON. Phone images go through RimPulse as today.
- **Failure modes to design out:**
  - Two machines on different origin/main shas: every result carries its sha.
  - A results commit racing a BENCH commit: union-merge shards, and results files are append-only.
  - SteveDesktop sleeping or rebooting: a watchdog, and a lease that expires.
  - Divergent mod lists: the run list names the tier.
  - DLC missing on the second account: preflight refuses.

## Open questions for the owner (Friday)

- Does SteveDesktop's Steam account own all five DLCs?
- RUNNER as a Lodestar node or not (Wednesday's answer).
- May scripted drivers on scratch maps use cheaper models or no model? (`Agent_Policy.md` live-write clause.)

## GPT enhancement pass (2026-10-24, via gpt_consult.py; raw reply below)

**Our read:** accepted almost entirely. The adopted changes:
- Commission one workload (the GSS `proof_all.py --live`) before porting everything.
- A machine-local lock instead of git for exclusion.
- Immutable jobs pinned to a sha, plus an outbox for publication.
- Record the actual deployed state, not just the requested sha.
- Prove the interactive Windows session (locked screen, reboot).
- Outcome classes, with an expected-row manifest.
- Windows SSH first; WSL only where a workload needs it.
- The bridge bound to loopback.
- One RUNNER results branch, with BENCH importing.
- Dependency-triggered jobs instead of non-stop housekeeping.
- A timeboxed Wednesday.

GPT's Lodestar answer (a plain worker reported through BENCH, promoted only on need) is its recommendation; Wednesday decides. Where this conflicts with the phases above, **this section wins.**

The direction is sound. Wednesday should decide whether scripted testing pays on Archmagi; the second-machine benefit needs a separate comparison.

For (1), replace the ordering bullets with:

- **Gate provisioning first:** verify SteveDesktop’s game/DLC entitlements, specs, disk capacity and supported Windows/toolchain versions. Confirm simultaneous play before substantial setup.
- **Commission one workload:** build the Archmagi wrapper around GSS `proof_all.py --live` first. Run offline gates before taking the bridge. Add FlowWorks and Pyrelands only after completion, timeout and recovery work.
- **Establish isolation before parallel operation:** configure machine identity, local bridge exclusion, deployment paths and scratch-save boundaries before allowing either machine to target SteveDesktop.
- **Transfer test fixtures explicitly:** distribute hashed, read-only source fixtures such as GSS `calm`; create disposable local copies. “Canonical world stays on Archmagi” must not exclude required test fixtures.
- **Commission by equivalence:** run the same frozen job on both machines; compare behavioral assertions within declared tolerances. Then test interrupted execution, duplicate delivery, reboot and failed publication before unattended operation.

For (2), replace or extend the failure-mode bullets with:

- **Git is transport, not exclusion:** use a machine-local authoritative lock covering deploy, ModsConfig changes and live driving. Git publishes status only. Lease expiry must fence or terminate the old driver before another starts.
- **Jobs are immutable:** require `job_id`, target machine, source SHA, suite/version, rows, dependency manifest, fixture hash and timeouts. Execute from a pinned checkout; never pull into an active run.
- **Publication survives failure:** write results atomically to a durable outbox; retry publication without rerunning the game. Use unique job/attempt paths and deduplicate ingestion. Append-only files and union merges do not establish exactly-once execution.
- **Verify actual deployed state:** record game/DLC versions, ordered mod list, Workshop content hashes, custom DLL hashes, companion and harness versions. Detect updates or partial deploys; a requested SHA and tier name alone are insufficient.
- **Prove the Windows session works:** launch the game in the intended interactive user session; test locked screen, remote disconnect and reboot recovery. SSH availability does not establish interactive-game availability. Windows services occupy a separate desktop context. [Microsoft documentation](https://learn.microsoft.com/en-us/windows/desktop/services/interactive-services)
- **Fail closed:** validate machine/game-session identity and scratch-site identity before writes. Check profile authorization and expiry at relevant boundaries; copying a profile is not commissioning it. Treat ambiguous writes as interrupted, never blindly retry them.
- **Separate outcomes:** report `PASS / MOD_FAIL / SITE_FAIL / HARNESS_FAIL / BLOCKED / INTERRUPTED`. Require an expected-row manifest so crashes, skipped rows and empty output cannot become passes.
- **Preserve evidence:** include artifact hashes, retention deadlines and a tested SSH retrieval command. A SteveDesktop-local pathname alone is not usable evidence elsewhere. Prevent Cloud synchronization from replacing scratch saves or ModsConfig.

For (3), simplify setup with these replacements:

- **Use one SSH endpoint:** prefer Windows SSH plus a local runner launcher; add WSL only where the selected workload requires it. Omit WSL sshd, `gh`, Claude/Codex logins, Remote Control and mirrored agent environments initially.
- **Keep the bridge local:** bind it to loopback and use SSH for administration. Open a LAN bridge port only if a demonstrated workflow requires direct access.
- **Port the commissioning path first:** centralize configuration for GSS and its dependencies; reject unsupported paths explicitly. Track the remaining 46-file portability audit separately.
- **Install only required Workshop dependencies:** commission minimal tiers first; download the full owner list when scheduling its actual acceptance test.
- **Use one RUNNER result branch and one publisher:** keep BENCH’s work checkout separate. BENCH imports validated summaries and writes ledger findings; defer RUNNER ledger registration until direct ledger writes provide measurable value.
- **Run jobs on relevant changes:** replace “non-stop” housekeeping and “full selftests on every push” with dependency-triggered, coalesced jobs plus a periodic sweep. Prioritize expiring or missing required evidence.
- **Resolve policy narrowly:** confirm whether unattended deterministic scripts are authorized on disposable sites. Remove cheaper-model deployment from this bring-up decision.

For (4), replace Wednesday’s measurement plan with:

- **Timebox Wednesday:** instrument and trial one existing suite; defer historical transcript reconstruction and the broad housekeeping inventory. Record incomplete measurements as inconclusive.
- **Measure prospective states:** timestamp offline gates, deploy, load, fixture setup, command execution, intentional tick waits, idle holds, recovery and publication. First-to-last calls, CPU and tick advance alone cannot distinguish these. Historical occupancy remains unknown without suitable logs.
- **Correct the bottleneck inference:** short gaps between holds show continuous ownership, not proven excess demand. Measure ready-job queue age and owner-requested bridge delays.
- **Compare like with like:** use frozen revisions, fixtures and row sets; alternate existing and scripted execution order, separating cold and warm runs. Start with GSS equivalence, then one bounded stale-evidence batch. Keep model policy unchanged.
- **Count total token cost:** use frozen model/category weights and publish raw usage. Include preparation, helpers, supervision, retries, triage and acceptance. Attach job IDs prospectively; retain unattributed fleet overhead rather than forcing session-to-item attribution.
- **Separate outcomes:** commissioning reruns measure reliability; progress means previously missing required evidence accepted at the intended revision. Deduplicate rows and findings. Report accepted bug fixes separately.
- **Wednesday decision:** advance only if scripting materially reduces total tokens for equivalent accepted results, detects an injected failure, and stays inside a preset setup budget. Keep the **+15% efficiency / +25% useful evidence/day** targets for the longer trial; Wednesday cannot establish bug-fix efficiency or unchanged reopen rates.
- **Measure hardware separately:** compare scripted Archmagi-only blocks against comparable dual-machine blocks. Record ready backlog, completion time, exception tokens and evidence invalidated before use. Measure cgroup limits, peak memory and OOM deltas; historical kill counters alone do not prove offloading will help.
- **Include payback:** charge implementation and commissioning tokens separately, then estimate recovery within eight weeks from measured weekly savings. Track human setup/triage time alongside tokens.

For (5), replace the Lodestar decision with:

- **Decision: RUNNER is initially a plain execution worker, reported through BENCH.** Give it a machine identity and heartbeat without an autonomous hourly reasoning sweep.
- **Promote only when necessary:** require either a real project/ownership responsibility or demonstrated need for native board scheduling that BENCH reporting cannot satisfy; also require measured maintenance/token savings exceeding integration costs.
- **Keep one authority:** node status must not create a second queue, competing item ownership, duplicate findings or another continuously reasoning seat. Native reporting alone does not justify promotion.