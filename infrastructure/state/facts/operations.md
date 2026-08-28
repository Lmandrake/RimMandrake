# Operational facts salvaged from the superseded POLICY.md and seat files (2026-08-27)

One line each; replace a line when superseded, never append a correction under it.
Unbudgeted, like everything in `facts/`.

- **RimSort never blocks a config write.** It writes only on a Save the owner
  announces; `ModsConfig.xml`, load order and user rules are writable game-up or
  game-down. After editing, one sentence — "RimSort is open, hit Refresh" — and move on.
- **Nothing outside the repo is precious** (owner, 2026-08-15): maps, saves,
  colonies, deployed mod folders, live game state — destroy freely, do not ask. Do
  not infer that play has started; the trigger is an explicit announcement.
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
  rewrites `queue/*.md` in the same command (`cli.py _emit`), so a view is never
  staler than the ledger. The 60 s `queue_publisher.sh` loop is retired with its
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
