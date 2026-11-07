# Operational facts salvaged from the superseded POLICY.md and seat files (2026-08-27)

One line each; replace a line when superseded, never append a correction under it.
Unbudgeted, like everything in `facts/`.

- **RimSort never blocks a config write.** It writes only on a Save the owner
  announces; `ModsConfig.xml`, load order and user rules are writable game-up or
  game-down. After editing, one sentence — "RimSort is open, hit Refresh" — and move on.
- **Nothing outside the repo is precious** (owner, 2026-08-15): maps, saves,
  colonies, deployed mod folders, live game state — destroy freely, do not ask. Do
  not infer that play has started; the trigger is an explicit announcement.
- **Runtime data lives under the data root, never `D:\Luke\dev`** (owner, 2026-10-19: *"dev is my special
  directory for Lodestar-managed projects, not a temp dir for your stuff"*). `src/RimMandrake/Utils/rmpaths.py`
  resolves it (`RM_DATA_ROOT`, else Lodestar `agent_storage.py rimmandrake`; archmagi `D:\ClaudeWork\rimmandrake`):
  `artpipe` `artstore` `scratch` `build` `obs` `dashboard`. Code calls `rm_path(...)`; `selftest_rmpaths.py` refuses
  a hard-wired `Luke/dev/_<dir>`. Units get it from `~/.config/systemd/user/<unit>.service.d/rm-data-root.conf`,
  Windows tasks from the user env var.
- **`observed/` is the ONE capture root**, at the repo root. The former second root
  under `infrastructure/state/` merged in 2026-08-23; a second root manufactured a
  false "evidence missing" verdict three times. `rimflow verify` still accepts the
  old prefix in pre-merge ledger events.
- **Unattended mod-list experiments** (owner, 2026-08-21): permitted only with all
  three — snapshot to `infrastructure/state/modlists/` named for the test · sweep
  every installed workshop mod for dependents before disabling · announce loudly
  where he reads on waking, naming the snapshot and the restore.
- **`infrastructure/state/MODE`** holds `belt` or `afk` only; `afk` suppresses every
  `needs: owner` item. Precedence in rimflow: `--mode` > `$RIMFLOW_MODE` > the file
  (`cli.py:255`). `bench` is refused — bench is per-window, delivered by
  `.claude/hooks/bench_mode.py`. `interactive`/`autonomous` are dead words.
- **WSL cannot reach the bridge socket**: RimBridge binds Windows loopback and WSL2
  is NAT-mode, so `127.0.0.1:5174` has *no route* from WSL — a refused connect is no
  reading at all. Drive it under `python.exe`; the instrument is
  `rimbridge_client.resolve_endpoint()` + a real `session/hello` (scrapes host, port
  AND per-launch token from `Player.log`; empty token = "too early to say", never
  "down").
- **Queue views render on write** (owner, 2026-08-27): every `rimflow` mutation
  rewrites `queue/BENCH.md`/`FOUNDRY.md` in the same command (`cli.py _emit`). Since
  2026-10-02 those views are gitignored, so a PULL does not refresh them: read with
  `rimflow queue <SEAT>` (renders, then prints). The 60 s `queue_publisher.sh` loop is retired with its
  whole staleness apparatus; `render.py --overwrite-queues` remains the manual form.
- **`strings -a -el` on an assembly is not a census** — it found 16 of 115 companion
  tool names; it proves a name PRESENT, never absent.
- **The trap file is cited exactly one way**: `as per the trap file` — no numeric
  index, no line anchor (`check_refs.py` validates the shape and line anchors break
  on any edit above them).
- **Bridge-item offering**: a `needs: bridge` item is offered to any window while
  the lock is free or its own (`priority.py`, corrected 2026-08-26 under
  `BRIDGE_GATE_HARDCODES_CHECK_1`).
- **Nothing is SELF-REPORTED** (board post-mortem, 2026-08-27): liveness from `ps`,
  activity from the ledger, the game from the process list, the bridge from
  `rimbridge_client`, durability from `git`; where no instrument exists the answer
  is UNMEASURED, never a guess, and nothing a window must "remember to update" may
  be reintroduced.
- **Windows Terminal ignores OSC 10** (measured 2026-08-13): per-window colour comes
  only from the WT profiles (`install_wt_seat_profiles.py --apply`), never from
  escape sequences.
- **Seat/window launch**: the WT profile exports `AGENT_SEAT` and launches
  `claude_bounded.sh --name 'AGENT <WINDOW>'`; `claude_bounded.sh` exists because
  four unbounded seats in one cgroup produced whole-VM OOM kills twice in one day
  (2026-08-14) — each window gets its own `systemd-run --user --scope` with
  MemoryMax. `--name` is the only route to an addressable session name;
  sessionTitle hooks never reach it.
- **Seat OOM deaths are enforced against, not exhorted.** `claude_bounded.sh` caps tool commands at 6G inside the seat (delegated scope, 'seat' sub-cgroup) and moves TMPDIR to `~/.seat-tmp/<SEAT>`; `.claude/hooks/block_tmpfs_clone.py` refuses repo copies into /tmp, /dev/shm, /run; `run_selftests.py` runs tests in `rm-harness.slice` (12G) outside seats. After any Claude Code upgrade check `claude --debug` shows a tool cgroup path under the seat scope. Fallback if these misbehave: mask `tmp.mount` (SEAT_MEMORY_STANDARD_FALLBACK_1); see `design/RimMandrake/memory_clones_drives_2026-10-08.md` §9.
- **Producer launch floor.** Every Producer run writes the same 107,656 tokens of opening context as 1-hour cache writes (weight 2), so any Producer launch costs about 215k weighted before it reads anything. Size a more frequent role cadence's cap from this floor, not from turn count; a lean launch for short runs is the lever.
- **The live `ops_watch` timer, like every Operations clock, runs from the one Operations deploy, `/home/mandrake/rm/dispatch`** (`src/RimMandrake/Utils/systemd/ops_clocks.json`), not a seat clone: a collector change is live only once that tree has the published commit. Check `git -C /home/mandrake/rm/dispatch log -1` before calling it live. `rm-ops-watch.timer` is disabled; `rm-metronome.timer`'s beat writes `/mnt/d/ClaudeWork/rimmandrake/ops_watch/status.json`, so a close promise about ops_watch readings names `unit=rm-metronome.timer`.
- **A stale 0-byte `.git/logs/refs/remotes/origin/HEAD.lock` froze the pulse deploy checkout** (`/mnt/d/ClaudeWork/rimmandrake/pulse-deploy`) for 15 h: `rm-pulse-update` failed every run, every rm-* unit kept running old code, and nothing alarmed. Check that checkout's HEAD when landed code seems not live. Owed: an ops_watch flag when pulse-update fails N times in a row, and `pulse_update` clearing a lock older than its own max run time when no git process holds the repo.
- **Wrap-up debts are in-process game state** (DebugSettings, the loaded game's difficulty, ModSettings statics that `jawa/mod_settings_field` never writes to disk, scenes on disposable maps): a debt owed before the game's last launch is void. `wrapup.void_debt` reads `Player-prev.log` mtime (Unity rotates at launch, keeps mtime); a wrap-up alarm relapse is usually void debts resolved by hand.
- **Steve lane.** Two consecutive canary REDs 'no live colonist' with a ~1 s load phase mean the long-lived game session's colony died and jobs keep reusing it: `rw_game.sh down/init/up --wait`, then `testq.py resume`. The Steve fault monitor STUCK state is sticky until a new boot and only alarms when its pause expires, so the lane sits idle up to 6 h with jobs queued: check `steve.state` reason and the `rm-steve-fault` journal when Steve reads PAUSED.
- **Loop units run on Archmagi, not where their game runs.** The SteveDesktop Artisan loop's unit `rm-ralph-gss-steve` and its agent run on Archmagi; only the game and its tools run on SteveDesktop through `ralph/steve.sh`, so `systemctl --user is-active rm-ralph-gss-steve` over ssh on SteveDesktop answers inactive while the loop runs (the same ssh listed 0 units: sanity-check an empty answer). The loop gate's AHEAD lists name `rm-ralph-graffiti`, `rm-ralph-gss`, `rm-ralph-gss2` while the running units are `rm-ralph-graffiti3` and `rm-ralph-gss-steve`, so the Pyrelands gate does not see Graffiti; the gate lives only in untracked per-loop copies under `rm/scratch/BENCH/ralph_*/ralph/`.
