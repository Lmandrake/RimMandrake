# Archmagi for Artisan only: how many loops, and what it takes (design, 2026-11-07)

Status: design and measurement only. Nothing on the machine was changed: no unit stopped, no game launched or closed, no Steam
action, no `.wslconfig` edit. Item `RIMMASTER_WEIGH_ARCHMAGI_TWO_GAMES_ARTISAN_ONLY_HOW_MANY`. Companion to
`design/RimMandrake/two_rimworld_instances_2026-11-07.md` (the SteveDesktop trial and the rung ladder), which this does not repeat.

Owner's words, Sat 2026-11-07 ~4:35 PM PST: *"I'd also like you to consider what it would take to reconfigure Archmagi to a two
Rimworld setup like SteveDesktop's currently doing plus one Conductor on Archmagi. We're configured for a whole pipeline right now.
If we reconfigure to only Artisan, how many could Archmagi handle with proper configuration? With their own Steam games of course"*

## The answer

- **Two games plus one Conductor fits on Archmagi, but not as the machine is set today.** Commit free is 7.2 GB and a second game
  needs 4 to 7.5 GB, so B today would run Windows to the edge. Two changes make room: apply the WSL cap that is already written but
  not live (28 GB in `.wslconfig` since 2026-11-05; the VM still runs at 35 GB), and let WSL give back its page cache. After that
  the estimate leaves about 10 GB of commit headroom with two small-list games and his usual desktop apps open (ESTIMATE; peaks unmeasured).
- **Loops on Archmagi's two games: 2 while he sits on game A, 4 when he does not.** A loop is on the game 46% of the time it is
  not already waiting for one (38% of pass time, with 18% waiting, MEASURED over 31 passes), so one game carries about 2 loops at
  most. Add SteveDesktop's two games and the fleet's games carry about 8.
- **Every loop's agent already runs on Archmagi**, including the loops whose game is on SteveDesktop. Agents are cheap in RAM
  (0.3 to 0.5 GB each, MEASURED). The ceiling if games were not the limit is about 8 to 10 by this machine, but the real ceiling
  is lower: today 4 loops raised 8 items that need him, and 3 of the 4 hit their 20M-token limit. **Past 4 to 5 loops, his
  attention and the token budget bind before Archmagi does.**
- **"The whole pipeline" costs almost no RAM, apart from the loops themselves.** Every pipeline service other than the loop units
  holds under 50 MB resident (MEASURED); a loop unit is 2.65 GB with its page cache, its `claude` 354 MB. Relentless is already stopped. Turning the pipeline off frees disk and token budget, not memory. The memory is in WSL's page cache (29 GB), his
  desktop apps (about 16 GB) and the game (7.4 GB).
- **Steam: one account can run two Steam-connected games on one machine** (MEASURED on SteveDesktop today, two games up now on 5174
  and 5175). Archmagi needs `steam_appid.txt` (the tested route) for its direct-launched B, since its bridge is a Workshop item.
  Whether he wants each game on its *own* licence is his question below, not a technical need.

## Measured on Archmagi, 2026-11-07 16:37 to 16:50 PST

All read-only, by `powershell.exe` and `/proc`.

| what | value | mark |
|---|---|---|
| CPU | Core Ultra 5 245K, 14 cores, 14 logical (6 P plus 8 E), 4.2 GHz | MEASURED |
| CPU busy | 76 to 91% Windows total at two reads; a 5 s sample: vmmemwsl 196%, dllhost 187%, pythonw 81%, RimWorld 63% (100% = one core) | MEASURED |
| WSL load | load average 12.3 / 8.2 / 5.0 | MEASURED |
| RAM | 63.3 GB total, 4.7 GB free | MEASURED |
| Commit | limit 90.9 GB, 7.2 GB free | MEASURED |
| WSL VM | `vmmemWSL` 35.2 GB private, 25.5 GB working set | MEASURED |
| inside WSL | `free -g`: 35 total, 10 used, 29 buff/cache, 24 available; swap 16, 2 used | MEASURED |
| `.wslconfig` | `memory=28GB`, `swap=16GB`, `autoMemoryReclaim=gradual`, file dated 2026-11-05 | MEASURED |
| WSL uptime | 5 days 13 h, so the 28 GB cap is **not live**: the VM still has the earlier 35 GB | MEASURED |
| Seats slice | `claude-seats.slice` 9.6 GB current | MEASURED |
| Game | 1 RimWorld, pid 42388, 7.37 GB private, 1.22 GB working set, started 14:53, parent `steam.exe`, args `-disable-compute-shaders` | MEASURED |
| Its list | 16 active mods incl. Core and all five expansions (parsed `activeMods`) | MEASURED |
| `steam_appid.txt` | absent from `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\` | MEASURED |
| Workshop | 1269 items; local `Mods` 104 folders | MEASURED |
| GPU | RTX 5080, 5.6 of 16.3 GB VRAM used, 9% busy | MEASURED |
| `/proc/meminfo` | MemAvailable 24.9, Cached 23.1, file pages 24.7, AnonPages 1.9, Shmem 1.3, SReclaimable 2.1 GB; `min_free_kbytes` 1 GB | MEASURED |
| Disk | C: 2140 GB free, D: 1667 GB free, WSL ext4 649 GB free | MEASURED |
| Desktop apps | Plaud 5.1 GB, Chrome 4.8, svchost 3.2, ChatGPT 2.0, Spotify 1.3, Steam 1.2, Typora 1.0, Dropbox 0.7, others; nonpaged pool 2.2 | MEASURED |

Resident cost of the pipeline, by unit (`MemoryCurrent`, MEASURED): `rm-ralph-flowworks` 2.65 GB (peak 3.75 GB; this counts its
page cache, its `claude` process is 354 MB RSS), `rm-artpiped` 12 MB, `machinist-chromeextbridge` 10 MB, the two
`rm-account-handover` units 8 MB each, `hestia` 7 MB, `rm-sheet-dessicated-corpses` 3 MB, everything else 1 MB or less. Relentless,
the Dispatcher and ops_watch have no process running (MEASURED, `pgrep`); 37 user timers exist. Pool: 3 clones, 13.5 GB, all three
are detached helpers (MEASURED, `scratch_clone.py pool`). `claude` processes: 100 to 494 MB RSS each (MEASURED).

Loops, from each `events.log` (weighted tokens = input + output + cache writes + cache reads / 10, as `tally.py` counts):

| loop | game on | passes | weighted tokens | pass-hours | per pass-hour |
|---|---|---|---|---|---|
| pyrelands | Archmagi | 10 | 23.2M | 12.8 | 1.8M |
| gss | SteveDesktop | 10 | 23.0M | 10.4 | 2.2M |
| graffiti | SteveDesktop | 8 | 21.8M | 7.9 | 2.8M |
| flowworks | SteveDesktop | 1 | 9.1M | 0.9 | 10.2M (one pass, first passes run heavy) |
| all | | 29 | 77.0M | 32.0 | 2.4M |

Pass time split from the `<title>` lines of `D:\ClaudeWork\rimmandrake\conductor\ARTISAN_NOW.md`, 31 distinct passes, 1936 minutes
(MEASURED): game 38%, thinking 27%, waiting for a game 18%, building 13%, writing code 3%. The page at 16:37 PST: 4 loops, 2 paused
for review at their token limit, 1 waiting for a game, 1 working; 8h 07m waited for a game today across all loops; 8 items need
him; about 71.7M tokens today.

## 1. The binding constraints, ranked

### First, RAM

Commit is the hard limit: a process that cannot commit fails, while a short physical shortfall only pages. Today (MEASURED): commit
limit 90.9 GB, 7.2 GB free. The private figures (WSL 35.2, game 7.4, desktop about 16) are commit charges, not resident memory: the
game's working set is 1.2 GB and WSL's 25.5 GB. Both budgets matter; the one below is commit.

What each thing costs:

- **A small-list game: 4 to 7.5 GB private.** MEASURED: B on SteveDesktop 3.9 to 4.4 GB on 27 mods; Archmagi's game 7.37 GB on 16
  mods after 1 h 45 min up. A game grows while it runs; the larger figure is the one to budget.
- **A full-list game: about 30 GB** (`design/RimMandrake/mod_audit/OWNER_CARDS.md`, line 253). There is no room for two of those on
  this machine, ever, and one leaves no room for a second game.
- **A loop's agent: 0.3 to 0.5 GB** for `claude`, plus its python tools. Its unit peaked at 3.75 GB, but that includes page cache.
  ESTIMATE 1 to 1.5 GB real per loop, inside WSL.
- **A build:** `winbuild.py` runs `dotnet` on Windows. Its peak is UNMEASURED; budget 1 to 2 GB transient (ESTIMATE).
- **The Conductor seat:** one `claude`, 0.3 to 0.5 GB, plus its helpers when it starts them.

WSL holds 35 GB, of which about 25 GB is file cache that Linux would drop under pressure (`/proc/meminfo`: 23.1 GB Cached, 1.9 GB
anonymous). `autoMemoryReclaim=gradual` is set, but the VM still holds 25.5 GB working set. WSL's `gradual` reclaim is documented to
wait for the guest's CPU to be idle (GPT's point, below), and the guest's load average is 12: busy loops may be what keeps the cache
held. That is a likely cause, UNMEASURED. One snapshot cannot say how much would come back.

So a second game on Archmagi today would land on 7.2 GB of commit, and a 7 GB game would leave nothing. **Today: no.**

With the config this doc recommends (WSL cap applied and lowered, reclaim working, his desktop apps as they are):

| budget | GB |
|---|---|
| Windows, his apps, nonpaged pool | 16 (MEASURED today) |
| WSL cap | 20 (ESTIMATE of need: 4 to 5 loops at 1.5, Conductor 1, base and cache 8; anonymous use today is under 4) |
| Game A, the Conductor's | 7.5 |
| Game B, the loops' | 7.5 |
| One build | 2 |
| **Total** | **53 of 63.3**, about 10 GB headroom |

This is a commit estimate with peaks (game saves, builds, cold loads) UNMEASURED; it says a trial is worth running, not that the
headroom is proven. A third small-list game fits only with WSL at 16 GB and his desktop apps lighter: possible, not planned.

Applying any WSL change needs `wsl --shutdown`, which kills every seat and loop on the machine. That is a maintenance moment, and
the `.wslconfig` comment says the cap exists to make the per-seat cgroup budget close (`MemoryMax=10G` per seat, slice 24G). Lowering
it below 24 GB means lowering the slice too, and leaving measured kernel and non-seat headroom under the cap. A shutdown does not
close the Windows games, and enabled timers start again when WSL returns, `testq` included: recheck them after.

### Second, Steam and "their own Steam games"

What is MEASURED: on SteveDesktop one Steam account runs two games from one folder at once, both connected to Steam, both seeing the
same 64 Workshop items, with no Steam dialog (`two_rimworld_instances_2026-11-07.md`, Trial result). It is production there now:
the Artisan page reads "SteveDesktop: 2 games up, ports 5175 and 5174". SteveDesktop runs on a different Steam account from
Archmagi's, which the owner called "a totally valid 2nd license" (`stevedesktop_bringup_plan_2026-10-24.md`, line 11).

What "one account normally allows one running copy" means in practice: Steam's Play button refuses a second launch of a game that
is already running. A directly started `RimWorldWin64.exe` does not go through the Play button. With `steam_appid.txt`
it connects to the running Steam client, which checks that the signed-in account owns the game. SteveDesktop showed
Steam tracking the second process without complaint.

Archmagi differs in three ways, all MEASURED: it launches through `steam://rungameid/294100`; its folder has no `steam_appid.txt`;
the bridge is only a Workshop item there. So B on Archmagi without that file is expected (UNMEASURED) either to be handed back to Steam or to start with no Workshop mods and no
bridge, and looks healthy on screen.

The routes, cheapest first:

1. **Second instance, same folder, Steam connection kept** (rung one). `-savedatafolder`, own log, own port and token, plus
   `steam_appid.txt` in the folder. Minutes. This is what SteveDesktop does. The file sits in A's folder too, but for a
   Steam-launched A the restart check already passes, so it is redundant there; it names the app and proves no ownership. A
   `SteamAppId` environment variable instead is untested and not Valve's documented route for the restart check.
2. **A second game folder** (rung three). Own `Mods`, so deploys never collide; about 2.5 GB. Copies Steam's install, which is the
   one licence-wording question in the ladder.
3. **A second Windows user** with a second Steam client. Hours, every tool's paths change, WSL interop does not reach that session,
   and it needs either the same account signed in twice (UNMEASURED, likely to fight) or a second account.
4. **A second Steam account** that owns RimWorld and all five DLCs. Same machine means route 3's second Windows user as well, because
   one Windows user runs one Steam client.

**A plain question for him:** "With their own Steam games of course" can mean either of two things. (a) Each game connected to Steam
with its Workshop mods, under your one account, as SteveDesktop does now: route 1 gives that, and no extra purchase. (b) Each game
on its own licence, a separate purchase: that is route 4 and needs a second Windows user. Steam's Subscriber Agreement does not
mention running two copies at once in words, and Ludeon's terms say personal use; whether (a) is what you want under your licence is
your call, not ours.

### Third, the shared `Mods` folder and companion-DLL deploys

Both games in one folder load one `Mods`. The companion DLL (`JawaBench`) is loaded by both, so replacing it needs both games down:
one loop's companion deploy stops the other loop's game, and on Archmagi that is his sitting's game. A non-DLL deploy into a mod the
other game is loading is UNMEASURED. Rule: the writable mods of game A's and game B's lists stay disjoint, and no companion deploy
while two games are up; a needed one waits for a moment when the sitting is not live. If that bites weekly, rung three is the cure.

### Fourth, his live looks

The Conductor sitting needs a game for him, with the advanced-zoom mod in the list (owner rule, 2026-11-03). That makes game A his:
the Steam-launched one, on the default data folder, never touched by a loop. Two risks on Archmagi that SteveDesktop does not have,
because he sits at this machine:

- **B takes the foreground on launch** (MEASURED on SteveDesktop). The standing rule is never to focus or fullscreen the game. A
  launch that does not take focus is UNMEASURED: try `Start-Process -WindowStyle Minimized`, and, for loops that need no picture,
  `-batchmode -nographics` (UNMEASURED with our tools; bridge screenshots will not work).
- **The desktop tools hit whichever window is on top** (`system_click.py`, `system_screenshot.py`). B's loop must use bridge
  screenshots only, never desktop clicks. Both games share the title "RimWorld by Ludeon Studios".

A sitting on the full list (about 30 GB) cannot run beside any B with today's desktop footprint. A sitting means a tier list, or B goes down for it.

### Fifth, CPU and GPU

Probably not binding at two games; UNMEASURED with two up here. The game used 63% of one core in the sample and averaged 1.5 cores over its life (9146 CPU-seconds in
1 h 44 min, MEASURED). Windows reads 76 to 91% busy now, but most of that is WSL (196%) and two Windows processes this design does not
explain (dllhost 187%, pythonw 81%; what they are is UNMEASURED). The 245K's 8 E-cores are slower than its P-cores, so a third game
may tick slower than the second; UNMEASURED. VRAM: 5.6 of 16.3 GB with one game; a small-list game adds 1 to 2 GB (MEASURED on
SteveDesktop). SteveDesktop's two games cost each other 10 to 15% of top speed on small lists.

### Sixth, tokens and his attention (the real ceiling)

2.4M weighted tokens per pass-hour on average across today's loops, 1.8 to 2.8M for loops past their first pass (MEASURED). At the
20M limit a loop runs about 7 to 11 pass-hours before it stops for his word, and 3 of 4 did today. Each loop also raised about 2
items that need him (8 for 4). Doubling the games removes the 18% of pass time spent waiting; it does not change tokens per pass or
the questions per loop. The account's own hourly or weekly limit is UNMEASURED here.

## 2. How many loops Archmagi could carry

| setup | games on Archmagi | loops | range | why |
|---|---|---|---|---|
| Today, as configured | 1 | 1 game loop here (agents for all 4) | 1 to 2 | commit free 7.2 GB leaves no room for B |
| **Two games plus one Conductor, as he asks** | 2 (A his, B the loops') | **2** while he sits, **4** when he does not | 2 to 4 | B carries about 2 loops; A carries 2 more only when he is not using it. Loops on SteveDesktop's two games are extra, about 4 |
| Artisan-only, proper configuration | 3 small-list (A sometimes his) | 5 | 4 to 6 | RAM allows a third only with WSL at 16 GB and lighter desktop apps; each game about 2 loops |
| Ceiling if games were not the limit | | 8 to 10 agents here | | CPU and RAM for agents allow it; tokens (about 20 to 25M weighted per hour) and his attention (about 2 questions per loop) do not |

Why about 2 loops per game: a loop is on the game 38% of its pass time and waiting 18%, so the game is 46% of its working time
(38/82). One game is saturated at about 2.2 loops in theory, and the queue gets long before that. This is a bound, not a forecast:
cold starts, deploys and long holds are bursty. Today 4 loops on 3 games waited 8 h in total.

**Recommendation: two games on Archmagi, one loop on B first, then 4 loops fleet-wide (2 per machine), 6 at most**, and raise only if the "needs
you" count stays under 2 per loop. Beyond that the machine is not the limit; he is.

## 3. What reconfiguring takes

### What stops or moves

Each service's absence and what it costs. Nothing frees meaningful RAM; the reason to stop these is tokens, disk and fewer things
touching the one `Mods` folder or the one game.

| service | state now | stop? | what its absence costs |
|---|---|---|---|
| Relentless | stopped, owner PAUSE | stays stopped | nothing more; the pool clones it held are already back |
| Dispatcher, ops_watch | no process (MEASURED) | already quiet | `rm-deadman` rechecks their stamps: retire or mark those promises, or it alarms on its own design (UNMEASURED whether it does already) |
| `testq-tick`, `testq-sweep`, `testq-steward-watch` | timers | **must pause or become instance-aware** | testq is a no-model test queue that drives a game; beside B it is the third driver. Its absence: no overnight no-model sweeps |
| `rm-selftests-nightly` (03:00) | timer | keep | a CPU and RAM burst at night; no game |
| `rm-arteval-autojudge`, `rm-artpipe-idle-fill`, `rm-artpiped` | daemon and timers | keep if art matters this week | they spend Codex and Opus tokens, 12 MB RAM; absence stops art regeneration |
| `rm-deploy-update` | timer | keep | fast-forwards the pulse-deploy checkout; not a game deploy, but check it never writes `Mods` (UNMEASURED) |
| `rm-ops-reds`, `rm-codebase-health`, `rm-objstore`, `rm-streams-collect`, `rm-telemetry-*`, `rm-mirror` | timers | keep | tiny; their absence loses health readings |
| `rm-memwatch`, `rm-order7`, `rm-scratch-pressure`, `rm-scratch-reap` | timers | **keep** | these guard the very memory this plan spends |
| Pool clones | 3, 13.5 GB | no change | disk is not the limit (649 GB free in WSL) |
| Steam-launch sites in our tools (4 files) | | no change | they start A only, which is what he wants |

### Archmagi's tooling gaps against SteveDesktop

| thing | SteveDesktop | Archmagi |
|---|---|---|
| `game_instance.py` instance `b` | in use | the code is in the repo; without `RM_INSTANCES_ROOT` it uses `<data root>/instances` (`game_instance.py` line 111), so the `b` folder is `D:\ClaudeWork\rimmandrake\instances\b` |
| Ports and token | 5174 A, 5175 B, token file | same scheme; A stays 5174 by default |
| Lock key | `stevedesktop.b` | `archmagi.b` is already a valid key (`rimflow/model.py` line 1230 accepts any `BRIDGE_HOSTS` machine plus one letter); also the remote-take lock path bug `RIMMASTER_FIX_REMOTE_TAKE_HOLDS_LOCK_NOBODY_READS` |
| Steam connection for B | `steam_appid.txt` already present | add the same file (one line, `294100`); `SteamAppId` alone is untested |
| `-disable-compute-shaders` | not used | must be passed by hand to B; it is A's Steam launch option |
| Window | B seeded 1280x720 in its `Prefs.xml` | same, plus a launch that does not take focus (UNMEASURED); registry key export before, import after with no game running |
| Bridge mod | local copy in `Mods` | Workshop only, so B's Steam connection is what gives it a bridge at all |
| Driver | loops drive by `ralph/steve.sh` over ssh | a local wrapper is needed: `ralph/steve.sh`'s `on()` without the ssh, with `game_instance.py env b`. No such wrapper exists for Archmagi |
| Gate | `AHEAD = {"b": []}` per copy | the same per-instance gate; the Pyrelands gate's stale unit names (`two_rimworld_instances` Part 2) must be fixed first |
| Single-game assumptions | old tools still pick the first game | the same 25-file list applies; the `taskkill /IM` and `Select -First 1` sites are the ones that could close **his** game here |

### Order of steps

1. Decide (a) or (b) in the Steam question. Everything below assumes (a).
2. Make every loop sharing Archmagi carry the instance-aware tools (`OLD_TOOLS_BESIDE_B_STILL_TAKE_IT`); pause the `testq` timers.
3. At a maintenance moment with nothing live, apply the WSL cap (`wsl --shutdown`). Lower it to about 20 GB only together with the
   `claude-seats.slice` limit. Measure reclaim afterwards: if WSL's working set still climbs to the cap with cache, consider
   `autoMemoryReclaim=dropCache` (UNMEASURED on this build).
4. Build the local B wrapper (the `archmagi.b` lock key already parses); selftest it offline.
5. Run the rung-one trial below.
6. Put one loop on B; add the second after a day without a wrong-game event.

### The canonical world saves

`infrastructure/state/CANONICAL_SAVE.md` names the precious saves; they live in A's default data folder (`...\LocalLow\Ludeon
Studios\RimWorld by Ludeon Studios\Saves`). B runs on its own `-savedatafolder` and does not read that folder, which is the main
protection. That is path selection, not access control: any same-user agent or mod can still reach it. The risks that remain: a tool run with `RM_GAME_INSTANCE` unset aiming at A's data folder from B's loop; a stray
`taskkill /IM RimWorldWin64.exe` closing A mid-save; and a deploy restarting A. Rules: B's loop always runs with `RM_GAME_INSTANCE=b`
and its gate refuses `taskkill /IM`; before the trial, copy the canonical saves to a dated backup folder and record their hashes,
and check them after; no loop ever loads a canonical save. Whether RimWorld syncs Saves by Steam Cloud on this account is UNMEASURED;
check before B runs.

## 4. Trial plan for rung one on Archmagi (not run)

**When.** He is away from the desk, nothing live on game A that he is looking at, no loop on Archmagi's game (pyrelands paused at its
limit counts), `testq` timers paused, `rimflow bridge who --host archmagi` free or ours. About 30 minutes. One driver.

**Before.** Apply the WSL cap first or confirm commit free is at least 12 GB; **if commit free is under 12 GB, do not start B.** Back
up A's `Saves` folder to `D:\ClaudeWork\rimmandrake\backups\`. `reg export` the Unity key. md5 A's `ModsConfig.xml` and `Prefs.xml`.
Read free RAM, commit, VRAM, A's private memory.

**Steps.**

1. `rimflow bridge take --host archmagi --for "second game trial on Archmagi"`.
2. A is up through Steam as usual. Record its pid, its TPS alone over 2 minutes from `JawaBench\tps`, its memory.
3. Create `D:\ClaudeWork\rimmandrake\instances\b`. Create `<i>\Config`, then copy `infrastructure/stevedesktop/Prefs.template.xml` to `<i>\Config\Prefs.xml`
   with `screenWidth` 1280, `screenHeight` 720, fullscreen False, run in background. Copy
   `infrastructure/state/modlists/ModsConfig.MINIMAL.xml` to `<i>\Config\ModsConfig.xml`, checked to resolve here.
4. From a PowerShell with no leftover `GABP_` variables:
   ```powershell
   $i = 'D:\ClaudeWork\rimmandrake\instances\b'
   # steam_appid.txt (one line, 294100) placed in the game folder first, as on SteveDesktop; record that it was added
   $env:GABP_SERVER_PORT = '5175'; $env:GABP_TOKEN = [guid]::NewGuid().Guid
   [IO.File]::WriteAllText("$i\bridge_token.txt", $env:GABP_TOKEN)
   $b = Start-Process -PassThru -WindowStyle Minimized -FilePath 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe' `
     -WorkingDirectory 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld' `
     -ArgumentList '-disable-compute-shaders', "-savedatafolder=$i", '-logfile', "$i\Player.log", '-screen-fullscreen', '0'
   ```
   Record `$b.Id` and check its command line holds `-savedatafolder=` before anything acts on it. Watch for a Steam dialog or a
   relaunch through Steam: without a working `steam_appid.txt`, `RestartAppIfNecessary` may hand the start back to Steam, which then
   refuses because A runs. `SteamAppId` alone is untested; do not substitute it.
5. Wait for `[RimBridge] GABP server connected to GABS on port 5175` in `<i>\Player.log`; read its Steamworks lines; count
   `rimworld/list_mods` entries with `source` = `SteamWorkshop` (on Archmagi the bridge itself being up already shows Steam worked).
6. `rimworld/start_debug_game_ready` on B. Check A on 5174 with its own token. Spawn a marker on B; confirm A does not have it.
7. Throughout, a 10 s commit-free and available-RAM log to the trial folder (startup and save peaks are what matter). Two minutes with both up: both TPS, both private memories, commit free, VRAM, CPU, `Get-NetTCPConnection -State Listen -LocalPort
   5174,5175`. Record whether B took the foreground (`system_screenshot.py` once, under `python.exe`).
8. Stop B by pid (`taskkill /PID`, `/F` after 90 s). Confirm A alive, bridge answering, `JawaBench\tps` growing. md5 A's files and the canonical saves.
   `reg import` the key only when no game runs; if A must stay up, leave the import for A's next down.

**Pass** (the same as SteveDesktop's): two games at once; each on its own port and token; each its own map, shown by the marker;
clean logs (no Steamworks warning, no bridge failure, no new error from the other game); A's files unchanged. **Plus two checks
Archmagi needs:** commit free stays above 4 GB throughout, and B did not take the foreground (if it did, the trial passes for loops
but not for running beside a sitting).

**A partial pass still answers.** B up with no Workshop mods: first check whether B relaunched through Steam or its `steam_appid.txt`
was not read; only then call it `STEAM_REFUSES_SECOND_INIT` for Archmagi.
Commit under 4 GB: RAM, not Steam, is the answer; stop B.

**Back-out.** Stop B by pid; the instance folder keeps everything B wrote; nothing in the game folder, Steam or A's data changed
except `steam_appid.txt`, which stays only if he agrees; it is redundant for a Steam-launched A. Release the bridge.

## GPT critique, and what was done with it

Asked with `gpt_consult.py` on this doc and the SteveDesktop design (job `consult-20261107-164318-1168705-0db44e`, 86 s). Folded in:

- **Memory model.** Private bytes are commit, not residency; the old "63.3 = 35.2 + 7.4 + ..." sum mixed them. The budget is now
  stated as commit, with working sets beside it, and called an estimate with peaks unmeasured.
- **WSL reclaim.** "Windows cannot take that memory back" was wrong as written: WSL returns pages and `gradual` reclaim waits for an
  idle guest CPU. `/proc/meminfo` was read (about 25 GB reclaimable file cache, 1.9 GB anonymous) and the busy guest named as the
  likely, unmeasured, cause.
- **`wsl --shutdown`** does not close Windows games, and timers come back with WSL; noted, with `testq` to recheck.
- **"Under 50 MB"** excluded the loop units; corrected.
- **`SteamAppId` is untested and not the documented route.** The trial now uses `steam_appid.txt`, the route SteveDesktop proved,
  and a missing Workshop is first checked as a relaunch through Steam before it is called a refusal.
- **Loops per game.** 38% of pass time is 46% of non-waiting time, so the bound is about 2.2 loops, not 2.6; the "3 during a sitting"
  figure had no allocation and is now 2.
- **Saves.** A data folder is path selection, not access control; the trial now backs up and hashes the canonical saves, and Steam
  Cloud is an open check.
- **Trial.** Create `Config`; take B's pid from `-PassThru` and check its command line; log commit every 10 s rather than one
  two-minute window; start with one loop on B.

Rejected:

- **"The design supports an experiment, not its claimed capacity."** Half kept: the capacity figures stay, because he asked for a
  number, but every one is now marked as an estimate whose test is the trial. Refusing to give a number would not answer him.
- **"`steam_appid.txt` is harmless remains broader than tested."** Kept as GPT's own point 6 states it: the file changes nothing for
  a Steam-launched game. The doc still asks his agreement before leaving it in place.
- **"CPU not binding is unproven."** Accepted as unproven, not as wrong: one game uses 1.5 cores of 14, and the doc now says
  UNMEASURED for two. The unexplained `dllhost` and `pythonw` load is left as a separate question, not this design's.
