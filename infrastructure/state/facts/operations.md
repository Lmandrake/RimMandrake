> HISTORY: retired era, see design/RimMandrake/retired_eras_index_2026-11-18.md. This file's mentions of Relentless, Artisan, Whittle, FOUNDRY, RimPulse or rimflow v3 are history (that machinery no longer runs); the rest is as current as its own status says.

# Operational facts salvaged from the superseded POLICY.md and seat files (2026-08-27)

Write one line for each fact. When a fact is superseded, replace its line. Never append a correction under a line.
This file is unbudgeted, like everything in `facts/`.

- **RimSort never blocks a config write.** RimSort writes only on a Save that the owner announces. `ModsConfig.xml`, load
  order and user rules are writable game-up or game-down. After you edit, write one sentence: "RimSort is open, hit
  Refresh". Then move on.
- **Nothing outside the repo is precious** (owner, 2026-08-15): maps, saves, colonies, deployed mod folders, live game
  state. Destroy them freely. Do not ask. Do not infer that play has started: the trigger is an explicit announcement.
- **Runtime data lives under the data root, never `D:\Luke\dev`** (owner, 2026-10-19: *"dev is my special
  directory for Lodestar-managed projects, not a temp dir for your stuff"*).
  - `src/RimMandrake/Utils/rmpaths.py` resolves the data root. The sources are `RM_DATA_ROOT`, else Lodestar
    `agent_storage.py rimmandrake`. On archmagi the data root is `D:\ClaudeWork\rimmandrake`.
  - The folders are `artpipe` `artstore` `scratch` `build` `obs` `dashboard`.
  - Code calls `rm_path(...)`. `selftest_rmpaths.py` refuses a hard-wired `Luke/dev/_<dir>`.
  - Units get the data root from `~/.config/systemd/user/<unit>.service.d/rm-data-root.conf`. Windows tasks get the data
    root from the user env var.
- **`observed/` is the ONE capture root**, at the repo root. The former second root under `infrastructure/state/` merged
  in 2026-08-23. A second root manufactured a false "evidence missing" verdict three times. `rimflow verify` still accepts
  the old prefix in pre-merge ledger events.
- **Unattended mod-list experiments** (owner, 2026-08-21) are permitted only with all three of these steps:
  - Take a snapshot to `infrastructure/state/modlists/`, named for the test.
  - Sweep every installed workshop mod for dependents before you disable a mod.
  - Announce loudly where he reads on waking. Name the snapshot and the restore.
- **Mode `afk`** suppresses every `needs: owner` item in `rimflow next`. Its sources: `--mode`, else `$RIMFLOW_MODE`
  (`_ctx` in `cli.py`).
- **WSL cannot reach the bridge socket.** RimBridge binds Windows loopback and WSL2 is NAT-mode. So `127.0.0.1:5174` has
  *no route* from WSL. A refused connect is no reading at all. Drive the bridge under `python.exe`.
  - The instrument is `rimbridge_client.resolve_endpoint()` + a real `session/hello`. The instrument scrapes host, port
    AND per-launch token from `Player.log`. An empty token means "too early to say", never "down".
- **Queue views render on write** (owner, 2026-08-27). Every `rimflow` mutation rewrites `queue/BENCH.md`/`FOUNDRY.md` in
  the same command (`cli.py _emit`).
  - Since 2026-10-02 those views are gitignored, so a PULL does not refresh them. Read them with `rimflow queue <SEAT>`
    (renders, then prints).
  - The 60 s `queue_publisher.sh` loop is retired with its whole staleness apparatus. `render.py --overwrite-queues`
    remains the manual form.
- **`strings -a -el` on an assembly is not a census.** It found 16 of 115 companion tool names. `strings` proves that a
  name is PRESENT, never that a name is absent.
- **The trap file is cited exactly one way**: `as per the trap file`. Do not use a numeric index or a line anchor.
  `check_refs.py` validates the shape. Line anchors break on any edit above them.
- **Bridge-item offering**: rimflow offers a `needs: bridge` item to any window while the lock is free or the lock is that
  window's own (`priority.py`, corrected 2026-08-26 under `BRIDGE_GATE_HARDCODES_CHECK_1`).
- **Nothing is SELF-REPORTED** (board post-mortem, 2026-08-27).
  - Read liveness from `ps`, activity from the ledger, the game from the process list, the bridge from
    `rimbridge_client`, and durability from `git`.
  - Where no instrument exists, the answer is UNMEASURED, never a guess.
  - Do not bring back anything that a window must "remember to update".
- **Windows Terminal ignores OSC 10** (measured 2026-08-13). Per-window colour comes only from the WT profiles
  (`install_wt_seat_profiles.py --apply`), never from escape sequences.
- **Seat/window launch**: the WT profile exports `AGENT_SEAT` and launches `claude_bounded.sh --name 'AGENT <WINDOW>'`.
  - `claude_bounded.sh` exists because four unbounded seats in one cgroup produced whole-VM OOM kills twice in one day
    (2026-08-14). Each window gets its own `systemd-run --user --scope` with MemoryMax.
  - `--name` is the only route to an addressable session name. sessionTitle hooks never reach that name.
- **Seat OOM deaths are enforced against, not exhorted.**
  - `claude_bounded.sh` caps tool commands at 6G inside the seat (delegated scope, 'seat' sub-cgroup). It also moves TMPDIR
    to `~/.seat-tmp/<SEAT>`.
  - `.claude/hooks/block_tmpfs_clone.py` refuses repo copies into /tmp, /dev/shm, /run.
  - `run_selftests.py` runs tests in `rm-harness.slice` (12G) outside seats.
  - After any Claude Code upgrade, check that `claude --debug` shows a tool cgroup path under the seat scope.
  - If these guards misbehave, the fallback is to mask `tmp.mount` (SEAT_MEMORY_STANDARD_FALLBACK_1). See
    `design/RimMandrake/memory_clones_drives_2026-10-08.md` §9.
- **Role launch floor (measured on the retired Producer role).** Every run wrote the same 107,656 tokens of opening context as 1-hour cache writes
  (weight 2). So any such launch costs about 215k weighted before the run reads anything. Size a more frequent role
  cadence's cap from this floor, not from turn count. A lean launch for short runs is the lever.
- **The live `ops_watch` timer, like every Operations clock, runs from the one Operations deploy, `/home/mandrake/rm/dispatch`**
  (`src/RimMandrake/Utils/systemd/ops_clocks.json`), not a seat clone.
  - A collector change is live only after that tree has the published commit. Check
    `git -C /home/mandrake/rm/dispatch log -1` before you call a change live.
  - `rm-ops-watch.timer` is disabled. `rm-metronome.timer`'s beat writes
    `/mnt/d/ClaudeWork/rimmandrake/ops_watch/status.json`. So a close promise about ops_watch readings names
    `unit=rm-metronome.timer`.
- **Wrap-up debts are in-process game state** (DebugSettings, the loaded game's difficulty, ModSettings statics that
  `jawa/mod_settings_field` never writes to disk, scenes on disposable maps). So a debt owed before the game's last launch
  is void. `wrapup.void_debt` reads `Player-prev.log` mtime (Unity rotates at launch, keeps mtime). A wrap-up alarm
  relapse is usually void debts resolved by hand.
- **Steve lane.**
  - Two consecutive canary REDs 'no live colonist' with a ~1 s load phase mean that the long-lived game session's colony
    died, and that jobs keep reusing the session. Run `rw_game.sh down`, then `testq.py resume`
    (`infrastructure/stevedesktop/RUNBOOK.md`: the runner starts a new quicktest).
  - The Steve fault monitor STUCK state is sticky until a new boot. STUCK alarms only when its pause expires. So the lane
    sits idle up to 6 h with jobs queued. When Steve reads PAUSED, check the `steve.state` reason and the `rm-steve-fault`
    journal.

## Context and cache economics (measured by Utils/sim/ctx_strategy_sim.py)
- **Prompt-cache economics of long seat sessions.**
  - Under the 1-hour cache TTL, gaps up to 60 min are 99.6-100% cache-warm. Gaps over 1 h are full re-writes (7.5% of
    spend). A 5-min TTL would cost 1.69x on the same calls (33% of round-opening calls follow a gap over 5 min).
  - A handoff near 350k context costs ~164k input-token-equivalents per round at a 251k mean. A fixed handoff at ~125k,
    or a stateless restart every round, simulates ~36% cheaper.
  - The biggest lever is the wake cost. An interactive wake shares only 27k of its 77k prefix with the previous session's
    cache. So every restart writes ~50k fresh (a fully cached wake with handoff at 75k saves 35% vs 200k
    auto-compaction).
  - Clearing tool results in place does not pay: tool results are only 17% of context growth.

## Throughput facts (census 2026-10-26, recheck before relying)
- **On 2026-10-26, with one live game, that game was the bottleneck.** Several games run now (`CLAUDE.md` §There are
  several live games). Measured then:
  - 343 BUILT items (median age 16.4 d).
  - Verify backlog 521 (median 17.2 d).
  - The bridge held 10.9 h/day.
  - 98.8% of closes since 10-19 carry no verify level.
  - 123 doing-rows with median age 23.8 d and 0 live leases.
  - Net +567 items in 7 days (1,531 filed less 922 done is 609, before drops/supersedes; use 567 for the growth of the
    list).

  BUILT 343 (the waiting items), 496 (the BUILT items of the friction count, 470 of which owe a bridge level) and the
  verify backlog 521 are three different sets: name the population.
- **Selftest time is concentrated and repeated.**
  - The total is 72.1 agent-hours of selftests in 22 days. The flowworks_stock selftest alone took 18.7 h (26%) at 38 PASS
    to 1 FAIL. 33% of executions were repeats.
  - The skip-when-unchanged hit rate is not measurable from run tails (they truncate the skip summary). So do not call the
    repeats 'unchanged-input' before you measure.
- **Owner ceremony is a large share of owner traffic (census 2026-10-26).**
  - 40% of owner messages drive the machine (card pulls 7.4/d, go-ahead 6.4/d, restart 5.1/d, handoff 4.6/d, wake 4.1/d).
  - 5 card classes are 69-89% rule-predictable (~47 min/wk).
  - Of 21 owner defect reports since 10-12, 12 were findable by an instrument we own.
  - The art judge sends 74% to REGEN (802 of 1,086 decisions of the judge in use on 2026-10-26; one asset was regenerated 40 times).
  - Evidence: `D:\ClaudeWork\rimmandrake\csuite\evidence.md` Q7, Q8, Q16.
- **Open Codex review findings (reviewed at cd905b46d6).**
  `modset_builder.py`: tasklist failure treated as stopped (~L1073); concurrent apply backup race; non-atomic restore
  (~L1304/1352).
  `modlist_swap.py`: capture ignores reorder; folder deps not transitive; DLC deps dropped; merge order of deps. Check
  each before you rely on the file.
- **Seats stop quickly after the owner speaks:** median autonomous run 1.8 min per owner message, 64% under 5 min, only 7%
  over an hour. 40% of his ~78 messages/day drive the machine (keep going, status pulls, orchestration).
  Evidence: `D:\ClaudeWork\rimmandrake\orch_record\friction_census.md` sections 1, 4b.
- **Live-test waste is selection, not capacity.**
  - One run spent 66% of chain-minutes on re-running known work (offline-in-live 32%, PASS->PASS known-good 32%,
    stale-only 2%). Another run spent 64%.
  - 58% of 6,492 re-executed rows across 95 historic runs were PASS->PASS.
  - A bridge day held 449 min, but call time was only 31% of held.
  - Until modcheck metrics exist, measure with
    `D:\ClaudeWork\rimmandrake\test_orch\{waste,history_waste,bridge_util}.py`.
- **A repair item that holds chains must have a cause that closes itself or an owner.**
  - A stale companion item sat 2 days and held 59 FlowWorks chains. So the fixed lane read EXHAUSTED ("nothing to test").
  - When the filler says exhausted, group `gaps.settled()`'s held chains by repair item before you believe the filler.

## Supervisor designs need an executor
- **Build and 48 h-prove an unattended executor before any supervisor (auditor, COO, producer, board, inspector) gets authority.**
  - Every supervisor design fails on the same missing piece. Nothing wakes a sleeping seat, leases a command, sees the
    command acked or retries, and records the outcome.
  - Watchers without an executor make the owner the dispatcher. Examples: a TPS drop recorded unseen, a reaper dry-run for
    8 d, a warn-only close gate, unapplied rulings, ~31 go/wake messages a day.
  - Also: 'closed' is not 'accepted'. Acceptance needs PASS on named scenarios on an identified build by a non-maker.

## Simulation findings
- **The weekly budget decides TestPilot, not reload tactics.**
  - In the round-2 sim, reload and full-batch parameters (2-min drain, 2 items/30 min, 12k startup, 17-30 min full load)
    moved accepted/day by +0.43 (noise) at +25% reloads and +22% game minutes.
  - The designs are in `src/RimMandrake/Utils/sim/testpilot_sim.py` and `loop_sim.py`. TestPilot-plus is variant TP+:
    two Test Pilots and a critic with a two-round cap. Ralph C+sub is two Ralph builder loops with bounded subagents. The
    v2/v3 world is the calibrated model of the fleet as it ran under rimflow v2 and v3.
  - At a 1.0G weekly budget TestPilot-plus loses 16.7/day, and Ralph C+sub beats it on sound production in 98% of members.
  - Measure critic false rejects and budget first. Design reload tactics last.
- **TestPilot is limited by the blind critic, not the pilots.**
  - In `testpilot_sim` (240 members, two TestPilots) the pilots idle 56-62%. Every pilot parameter (reload, full-load, test
    minutes, crash, invalid) moves accepted/day by <0.3. The critic's false-reject rate (`crit_fr`, `crit_fr_big`) and
    sensitivity move accepted/day by 3-6.
  - Measure the critic's false-reject rate before you invest in pilot speed. All TP params are ASSUMED.
- **Replay trial tasks are a total order under sibling containment** (300/300 pairs, width 1).
  - Each later base holds every earlier real fix. So replay tasks that run side by side leak answers.
  - Across-task parallel trials need a constructed snapshot workload.
  - Evidence `D:\ClaudeWork\rimmandrake\parallel_add_on\evidence\trial25_sibling_relation.json`.
- **The process simulator models the owner only as a ticket source and card answerer, so it understates his steering.**
  - In the calibration week he was active 72% of minutes (85 msgs/day, helper launches ~3x higher when present).
  - The simulated v2 lead (49 closes/day) is largely his live steering. An autonomous-only v2 is about 25 closes/day
    (ESTIMATE, range 13-38).
  - Any architecture comparison must model owner presence explicitly or use an unattended day.
  - Source: `D:\ClaudeWork\rimmandrake\testpilot\v2_owner_augmentation.md`.
- **A single Ralph loop is capacity-bound, not more efficient.**
  - On the calibrated v2/v3 world, sound work per token ties v2 (52% of members higher), while throughput is a third and
    backlog grows ~100/week.
  - Its owner-message saving rests on one unmeasured assumption (Spearman +0.99 on the status-ping multiplier). Measure
    the assumption with a one-week AB_test slice before you believe any nudge claim.
