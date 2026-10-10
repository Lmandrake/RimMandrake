# The RimMandrake live-game bridge — architecture, control and intention

*Written 2026-10-10 by FOUNDRY (offline pass, no bridge taken) on the owner's order:
"document the ENTIRE bridge system and intention... all of it. Debugging, control,
everything." This is the **architecture / control / intention** half. A sibling document
covers debugging, observability and testing. Both are written to be handed to an external
reviewer (GPT) whose job is to **predict problems now** instead of discovering them one
live session at a time.*

## 0. How to read this document

- **Every factual claim carries a label.**
  - **MEASURED**: read from source, a file on disk or a command run on 2026-10-10, with a
    citation (`file:line` or the command).
  - **DOC**: what a repo document or skill asserts, quoted as an assertion. It has not been
    re-checked against code here. Docs in this repo rot (`CLAUDE.md` § "Doc rot and stale
    gates").
  - **UNVERIFIED**: believed, but no source was read that settles it.
- Paths are repo-relative to the seat clone `/home/mandrake/rm/foundry` (the Windows
  read-only mirror is `D:\Luke\dev\RimMandrake`), unless they are absolute Windows paths.
- **Counts rot.** Every count here is stamped with how it was taken. Re-measure it; never
  quote it.
- §7 (the predicted-problems table) is the reason this document exists. §1–§6 are there
  so that table can be checked.

### Glossary

| term | meaning |
|---|---|
| **the bridge** | the whole system: the RimBridgeServer mod inside RimWorld, the JawaBench companion DLL, the Python client, and the lease/state tooling around them |
| **RimBridgeServer (RBS)** | third-party RimWorld mod by Andreas Pardeike (`brrainz.rimbridgeserver`). It opens a TCP server inside the game process |
| **GABP** | the wire protocol RBS speaks (`gabp/1`) |
| **GABS** | Pardeike's optional launcher/broker for RBS. **We do not use it.** We run "direct mode" |
| **JawaBench** | *our* companion assembly `JawaBench.BridgeTools.dll`. It adds `jawa/*` and `deepfire/*` tools |
| **seat / window** | an agent window: `BENCH` (with the owner) or `FOUNDRY` (autonomous queue). `OWNER` is the human |
| **the lease / the lock** | who may drive the bridge. Recorded by `rimflow bridge` |
| **belt** | FOUNDRY's continuous autonomous mode: subagents run live suites back to back |
| **cold load** | launching RimWorld from nothing to a usable state |

---

## 1. Intent and history

### 1.1 Why the bridge exists

RimWorld is a closed Unity/Mono game. This project ships about 600 mods' worth of content
(a 631-mod active list, DOC CLAUDE.md, re-measure with `measure`), and most of what can go wrong only shows
**at runtime**. Examples: a def that loads but is discarded, a Harmony patch that never
attaches, a setter that returns and changes nothing, a texture that does not bind.

The bridge turns the running game into something an agent can **drive and read without a
human clicking**. Concretely, it is used to:

1. **Prove a mechanism works.** Spawn a thing, step ticks, read back the raw field
   (`skills/rimbridge/SKILL.md` §2, "The one law").
2. **Author content in the live world.** Planet tiles and biomes (33+ `jawa/world_*`
   tools), maps, pawns (`skills/rimbridge/references/*-authoring.md`).
3. **Stage scenes for the owner to judge.** Review maps and keeper savegames
   (CLAUDE.md "Options he must LOOK at ship as a savegame").
4. **Run regression and north-star suites** unattended in "belt" mode
   (`infrastructure/agents/FOUNDRY.md:128-181`).
5. **Observe health.** TPS, hangs and log loops (the sibling document's half).

The ideal it serves (CLAUDE.md "How we debug", owner 2026-10-01): *every mod gets a
functional script and is debugged through it*. The bridge is what those scripts drive.

### 1.2 Who uses it

| actor | how | authority |
|---|---|---|
| **OWNER** (Lukas) | plays the game; announces game state (`./game`); overrides the lease (`./bridge bench\|foundry\|free`) | final. His `./bridge` lands in the same ledger file |
| **FOUNDRY** | the main driver: belt suites, proofs, deploy→restart cycles | "FOUNDRY now owns bridge driving directly" (DOC `skills/rimbridge/SKILL.md:47-57`). It may reboot the game without asking (DOC `GAME_STATE_WORKFLOW.md:44-67`) |
| **BENCH** | drives only for L3 evaluation sittings and joint live reviews with the owner | DOC `skills/rimbridge/SKILL.md:54-57` |
| **subagents** of either seat | do the actual driving in belt mode ("one subagent engaged with the Bridge whenever it is available", DOC `FOUNDRY.md:132`) | inherit the parent seat's lease. **No per-subagent identity exists** (MEASURED, §4.1) |
| **scheduled observers** | `tps_observer.py` (every 2 min) and `health_observer.py` (every 5 min) run as Windows scheduled tasks, per their docstrings | read-only. They do not take the lease |

### 1.3 Principles (owner rulings, in order of authority)

1. **One driver at a time, for attributability rather than ownership.** Two simultaneous
   drivers made the bridge **stuck, not crashed**. It recovered when the other call
   finished (DOC `skills/rimbridge/SKILL.md:97-105`, measured 2026-08-15). The bigger
   cost is that you cannot tell whose action changed the world.
2. **The lease errs toward ALLOWING, never mutual lockout** (owner 2026-09-02, CLAUDE.md).
   A hold whose seat has written no ledger event for 45 minutes is simply taken.
   `--force` always works and is recorded.
3. **The owner overrides both seats** (`./bridge`).
4. **Holding the bridge is blanket authorization** (owner 2026-09-19): start Steam, launch,
   cold-load, kill and relaunch, all without asking.
5. **A reboot is the seat's to call** (owner 2026-09-02). It is gated only on the bridge
   being free or yours, and on the ~15–25 min cost.
6. **`success: true` is not evidence.** Write → read back the raw field → look
   (DOC `skills/rimbridge/SKILL.md:39-41`).
7. **The owner announces states the machine cannot see; anyone may measure the ones it can.**
   DEPLOYING vs DOWN and GOING_DOWN vs UP are his. UP/DOWN/LOADING are measured by probe
   (MEASURED `src/RimMandrake/rimflow/probe.py`, §4.2).

### 1.4 What the bridge is NOT for

- ⛔ **Unattended live flight tests or flight screenshot hunts.** The owner said it three
  times on 2026-09-25 (CLAUDE.md). Verify flight with a deterministic state read of
  `Pawn_FlightTracker` (`jawa/pawn_flight`), or wait for a joint session.
- ⛔ **Fullscreening, maximizing or focus-stealing the game window** (owner 2026-10-04,
  memory `dont-fullscreen-or-focus-the-game`).
- ⛔ **Hot-reloading defs.** `jawa/hot_reload_defs` is RETIRED (owner 2026-09-03). The
  client refuses it (MEASURED `rimbridge_client.py:160-181`, `_retired`). It is still
  compiled into the DLL (MEASURED: `hot_reload_defs` appears in `JawaBenchDebugGems1.cs`),
  so a client other than `rimbridge_client.py` can still call it.
- ⛔ **`search_debug_actions` on the full mod list.** It livelocked and killed a 568-mod
  game (DOC `skills/rimbridge/SKILL.md:401-405`). It also expands quest test loops on the
  main thread (DOC `live_test_hang_runbook.md` row 8).
- ⛔ **Worldgen in any form.** Players receive a fixed world (CLAUDE.md). The world tools
  exist to author THE map, never to roll alternatives.
- ⛔ **Proving DLC-absent configurations.** All five expansions are always loaded
  (owner 2026-09-19 and 2026-09-26).
- ⛔ **Being an LLM transport.** In-game LLM calls shell out to `claude -p` (CLAUDE.md
  2026-09-05). The bridge is the *outside-in* control path only.

### 1.5 History, compressed

| date | event | source |
|---|---|---|
| 2026-08-09 | RimBridgeServer installed from Workshop item 3727949765 (oldest DLL mtimes) | MEASURED `ls -la …/3727949765/1.6/Assemblies` |
| 2026-08-10 | `list_debug_action_roots`/`search_debug_actions` kill a 562-mod colony (AppHangB1) | DOC `rimbridge_client.py:20-31` |
| 2026-08-12 | unpause plus a forgotten hostile spawn kills 2 colonists ("unpausing is the most consequential call") | DOC `skills/rimbridge/SKILL.md:427-449` |
| 2026-08-15 | two concurrent drivers wedge the bridge (it recovers) | DOC `skills/rimbridge/SKILL.md:97-105` |
| 2026-08-19 | companion grows 32 → 91 tools in a day | DOC `skills/rimbridge/SKILL.md:190` |
| 2026-08-22/23 | `JawaBenchInit` init line added; found to be lazy (fires on the first `jawa/` call, not on load) | MEASURED `JawaBenchInit.cs:1-35` |
| 2026-08-27 | redesign #4: two windows (BENCH and FOUNDRY) replace four seats. CHECK no longer exists | DOC CLAUDE.md |
| 2026-08-30 | bare-exe launch corrupts Workshop Harmony loading. Launch via `steam.exe -applaunch 294100` | DOC memory `launch-rimworld-via-steam-not-bare-exe` |
| 2026-09-02 | lease made "errs toward allowing"; reboot made the seat's call | DOC CLAUDE.md |
| 2026-09-03 | `hot_reload_defs` retired | MEASURED `rimbridge_client.py:160-181` |
| 2026-09-25 | flyer live-test ban (×3) | DOC CLAUDE.md |
| 2026-09-29 | `./game` from a seat stamps the ledger only, with no window broadcast | MEASURED `game:9-15` |
| 2026-10-01 | late reply after a timeout desyncs later calls; `abandoned`-id fix | MEASURED `rimbridge_client.py:400-408` |
| 2026-10-03 | belt-night hangs → `belt_watchdog.py` and the hang runbook | DOC `live_test_hang_runbook.md` |
| 2026-10-07 | BENCH and FOUNDRY both "held" the bridge a minute apart (per-clone ledgers) → cross-clone shared lock `BRIDGE_SHARED.json` | MEASURED `rimflow/model.py:1001-1047` |
| 2026-10-07 | **Steam auto-updated RimBridgeServer to 2.3.0**: `RimBridgeServer*.dll` and `Lib.GAB.dll` mtimes are 2026-10-07 | MEASURED `ls -la --time-style=long-iso …/3727949765/1.6/Assemblies`, `About/Manifest.xml` `<version>2.3.0` |
| 2026-10-10 | map-awareness phases 1–3 (visitor recorder, incident journal, pawn origin) built | MEASURED `git log` 7eb8d02ca, 8d5f64275 |

---

## 2. Architecture

### 2.1 Machines, processes and boundaries

```
 ┌──────────────── Windows 11 host "Archmagi" ─────────────────────────────────────┐
 │                                                                                  │
 │  Steam.exe ──(-applaunch 294100)──▶ RimWorldWin64.exe  (Unity, Mono, ONE process)│
 │                                      ├─ Assembly-CSharp (Verse/RimWorld)         │
 │                                      ├─ 0Harmony (from brrainz.harmony)          │
 │                                      ├─ ~630 mods' assemblies + defs             │
 │                                      ├─ RimBridgeServer.dll + Lib.GAB + Gabp.Runtime
 │                                      │     TCP listen 127.0.0.1:5174 (GABP)       │
 │                                      │     loads <RimWorld>\BridgeTools\JawaBench\│
 │                                      │        JawaBench.BridgeTools.dll (ours)    │
 │                                      └─ writes Player.log, Saves, JawaBench\tps\… │
 │                                                                                  │
 │  python.exe (Windows CPython) ──TCP 127.0.0.1:5174──▶ the game                   │
 │     runs scripts from D:\Luke\dev\RimMandrake (read-only mirror of origin/main)  │
 │     or from Transient\ (repo-relative)                                           │
 │                                                                                  │
 │  Scheduled tasks: "RimMandrake\TPS Observer" (2 min), "RimMandrake\Health        │
 │     Observer" (5 min), "\WSL Keepalive"                                          │
 │                                                                                  │
 │  ┌──────────── WSL2 Ubuntu (NAT network namespace) ───────────────────────────┐  │
 │  │ Claude Code windows: BENCH, FOUNDRY (+ subagents)                          │  │
 │  │ seat clones /home/mandrake/rm/{bench,foundry} (ext4, one writer each)      │  │
 │  │ python3: rimflow (lease, ledger, game-state probe), modlist_swap,          │  │
 │  │          modset_builder, build.py/winbuild.py (stage to D:\Luke\dev\_rmbuild,│ │
 │  │          build with Windows dotnet), belt_watchdog                         │  │
 │  │ shells out to *.exe: tasklist.exe, taskkill.exe, netstat.exe, cmd.exe,     │  │
 │  │          python.exe, powershell.exe                                        │  │
 │  │ ✗ CANNOT reach 127.0.0.1:5174 on Windows (NAT mode)                        │  │
 │  └────────────────────────────────────────────────────────────────────────────┘  │
 └──────────────────────────────────────────────────────────────────────────────────┘
```

| boundary | fact | label |
|---|---|---|
| WSL → bridge socket | Not reachable. RBS binds Windows loopback and WSL2 runs NAT mode. `python3` gets `ConnectionRefusedError`; the client says so and says nothing about whether the game runs | MEASURED `rimbridge_client.py:301-322`; DOC CLAUDE.md |
| bridge talkers | must be Windows `python.exe`. It **cannot open `/tmp` or scratchpad paths**, so scripts live in `Transient\` or the D:\ mirror | DOC `skills/rimbridge/SKILL.md:138-178` |
| mirror lag | `D:\Luke\dev\RimMandrake` is a writer-free export of origin/main, refreshed every ~5 min. A script edited in the seat clone and not pushed **does not exist** for `python.exe` | DOC CLAUDE.md "Git"; the scheduler for the 5-min refresh is UNVERIFIED (no `.timer` unit found in the repo) |
| `python.exe` CRLF | values captured from `python.exe` end in `\r` | DOC CLAUDE.md |
| drvfs | `/mnt/c` and `/mnt/d` reads from WSL can be minutes stale | DOC memory `drvfs-stale-reads-mimic-revert` |
| interpreter split | `python.exe` driving the bridge cannot call WSL `python3`; it silently gets a Windows `python3` | DOC `skills/rimbridge/SKILL.md:174-178` |

### 2.2 Components and versions

| component | where | version / provenance | label |
|---|---|---|---|
| RimWorld | `C:\Program Files (x86)\Steam\steamapps\common\RimWorld` | 1.6; the runtime rev is stamped by the JawaBench context line | MEASURED `JawaBenchInit.cs:163-215` |
| RimBridgeServer | Workshop `C:\…\workshop\content\294100\3727949765\1.6\Assemblies` (`RimBridgeServer.dll`, `.Core`, `.Contracts`, `.Sdk`, `.Extensions.Abstractions`, `Lib.GAB.dll`, `Gabp.Runtime.dll`, `MoonSharp.Interpreter.dll`, `Newtonsoft.Json.dll`) | **2.3.0**; updated by Steam 2026-10-07 06:39. **Not pinned** (it is a Workshop subscription) | MEASURED (`About/Manifest.xml`, `ls`) |
| RBS source | `vendor/mod_sources/RimBridgeServer-main/` is **referenced** by `SOURCES.md:56` and by the skill, but **absent from disk** today. Only the binaries and the Workshop `README.md` (473 lines) exist locally | MEASURED (`ls vendor/mod_sources` shows only `SOURCES.md`) |
| JawaBench companion | source `src/RimMandrake/bridgetools/JawaBench.BridgeTools/` (101 entries, about 62k lines of C# including the csproj); deployed `C:\…\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll` (4,254,720 bytes, mtime 2026-10-10 09:50) | csproj `Version 0.1.0` (never bumped). Identity comes from the build hash and toolSet digest in the init line | MEASURED (`wc`, `ls -la`) |
| Harmony | `brrainz.harmony`, Workshop 2009463077 `Current\Assemblies\0Harmony.dll` | Workshop, unpinned | MEASURED csproj `HarmonyDir` |
| Python client | `src/RimMandrake/Utils/rimbridge_client.py` (608 lines, stdlib only) | in repo | MEASURED |

**Companion compile-time dependencies** (MEASURED `JawaBench.BridgeTools.csproj:133-180`):
`RimBridgeServer.Sdk` (taken *from the Workshop folder*), `Assembly-CSharp`, four
`UnityEngine.*` modules, `0Harmony`, **and five of our own mods' DLLs**: `RimMandrakeOracle`,
`RimDefDump`, `Droidworks`, `Inhabited` and `RimMandrakeGimmeSomeSlack`. Every reference is
`Private=false`, so the companion binds at runtime to whatever copy the process already loaded.
The csproj comment claims "a version skew between compile-time and run-time SDK is impossible
by construction" (MEASURED `csproj` comment, lines ~70-75). **That holds only at build time.**
Steam can update the SDK under an already-built DLL (§7, P1).

### 2.3 Wire protocol (GABP direct mode)

MEASURED from `rimbridge_client.py:42-66`, which was itself derived from the shipped DLLs'
metadata heaps, not from source:

- **Transport:** raw TCP to `127.0.0.1:<port>`, LSP-style framing:
  `Content-Length: N\r\nContent-Type: application/json\r\n\r\n<N bytes of UTF-8 JSON>`.
- **Envelope:** `{v:"gabp/1", id, type:"request"|"response"|"event", method, params, result, error}`.
  Events carry `{channel, seq, payload}`.
- **Methods:** `session/hello`, `tools/list`, `tools/call`, `events/subscribe`,
  `events/unsubscribe`, `attention/current` and `attention/ack`.
- **Handshake:** `session/hello{token, bridgeVersion, platform, launchId, clientInfo}`. The
  client falls back to `{token}` alone on "Invalid session/hello parameters"
  (MEASURED `:436-453`). Before hello the server answers "Session not established".
- **Discovery:** RBS logs `[RimBridge] GABP server running standalone on port 5174` and
  `[RimBridge] Bridge token: <tok>` (DOC Workshop README:79-90). `discover_from_log`
  scrapes the **last** pair in `Player.log` (MEASURED `:223-251`). Resolution order per field
  is CLI, then env (`RIMBRIDGE_HOST`, `GABP_SERVER_PORT`, `GABP_TOKEN`), then the log, then
  defaults (`127.0.0.1`, `5174`, empty token) (MEASURED `:254-266`).
- **Port:** 5174 "stable" (DOC skill). Whether RBS falls back to another port when 5174 is
  taken is **UNVERIFIED** (no source on disk).
- **Token:** new every launch (DOC). The fallback default token is the empty string, so a
  missing token produces an auth error rather than a hang (MEASURED `:102-104`).
- **Responses:** every reply carries `operation{OperationId, Status, Success, DurationMs,
  Warnings/Error}` plus a compact `state` with the game `tick` (DOC README:179). **The
  envelope `Success` is not the tool's `success`.** A tool that correctly refuses is a
  successful operation (DOC `skills/rimbridge/SKILL.md:264-269`).
- **Unknown argument names** are "ignored but reported as an `arguments.unknown` warning"
  (DOC README:180). Two layers guard against this:
  - The client: `check_params` raises `UnknownParameterError` against the `tools/list`
    schema (MEASURED `:508-532`), but only from `RimBridge.call`.
  - The companion: `JawaBenchArgGuard` Harmony-prefixes RBS's argument binder
    (MEASURED by the data-plane census: Harmony id `mandrake.jawabench.argguard`, target
    `BindArguments`). Strict mode throws; otherwise it counts and warns.
- **Paging:** large list replies are paged under a ~30K-character budget (DOC README:177).
  Calls made *from companions or scripts* are not paged.
- **Attention gate (new in the upstream docs):** "RimBridgeServer now also publishes blocking
  attention when severe async failures happen … ordinary game calls pause until the
  attention item is reviewed and acknowledged" (DOC README:53). That text describes GABS.
  **Whether direct mode also blocks is UNVERIFIED.** Our client never calls
  `attention/current` or `attention/ack` (MEASURED: grep finds only the docstring mention at
  `rimbridge_client.py:57-58`). See §7, P2.
- **UltraSpeedBoost:** "RimBridgeServer enables RimWorld's private
  `TickManager.UltraSpeedBoost` process-wide at startup" (DOC README:300). So speed 4 is not
  vanilla speed 4 in any bridge-loaded game, **including the owner's campaign** whenever RBS
  is active.

### 2.4 The client's connection model

MEASURED `rimbridge_client.py:273-560`:

- **One TCP socket per `RimBridge` object; one request in flight.** `_recv_response` reads
  until the matching id arrives and parks events in `self.events`, which are never consumed.
- **Timeouts:** connect 5 s; per-call socket timeout 30 s (default, `--timeout` overrides).
  A timeout raises `"timed out … long event or the call may be frame-bound"`, and the request
  id goes into `abandoned`. If the late reply later arrives on the same socket, it is dropped
  (fix of 2026-10-01). Any other unexpected id raises "stream desynced".
- **Retired tools** are refused client-side (`_retired`).
- **Read-only heuristic:** the CLI refuses non-read-looking tools without
  `--yes-i-know-this-is-live` (MEASURED `:574-590`). The library `call()` has no such gate:
  "NOTHING here stops you calling a destructive tool" (MEASURED `:535`).
- **Session log:** every connect→close appends one row to
  `D:\Luke\dev\_rmscratch\bridge_sessions.jsonl` (MEASURED `:122-140`). This is the only
  per-script attribution record. It does **not** carry the seat or lease holder.
- **No lease check.** The client never consults `rimflow` or `BRIDGE` (MEASURED: grep for
  gate/rimflow/lease in the client finds nothing).
- **No reconnect, no retry, no attention handling.**

### 2.5 Inside the game: dispatch and threading

- **Socket I/O runs off the Unity main thread** inside RBS. `rimbridge/ping` "answers off the
  main thread", so it proves the socket and **not** that the game is turning over. A
  main-thread call such as `rimworld/get_ui_state` does (DOC `live_test_hang_runbook.md`,
  "bridge" signal).
- **Companion tools run off the main thread too.** Every game-touching line must be inside
  `await ctx.MainThread.InvokeAsync(() => …)` (DOC `skills/rimbridge-companion/SKILL.md:101-121`).
  The claim that "Unity corrupts rather than throwing" when this is violated is **asserted,
  never tested** (the skill says so itself).
- **Main-thread work is frame-bound.** A call marshalled to the main thread waits for the
  next Unity `Update`. RimWorld ships `runInBackground=False`, so an **unfocused game
  barely runs its loop** (0.5% of one core against 79%), and every main-thread call times
  out at 30 s while `ping` answers in 0.5 ms (DOC `skills/rimbridge/SKILL.md:147-154`).
  The fix is the in-game Options → Run in background; `Prefs.xml` is rewritten from memory
  on exit, so a disk edit while the game runs is lost.
- **Long events** (map generation, save/load, `LongEventHandler`) hold the main thread.
  The tools `rimbridge/wait_for_long_event_idle`, `wait_for_game_loaded` and
  `wait_for_operation` exist (DOC README:309-318). The client's 30 s default timeout is
  shorter than many long events; callers must pass longer ones (e.g. the 600 s socket with
  `timeoutMs=280000` for `start_debug_game_ready`, DOC companion skill §5).
- **Async SDK surface:** companions may `await ctx.Game.NextFrameAsync()`,
  `StepTicksAsync`, `RunForTicksAsync` and `RunUntilAsync`, and call other tools via
  `ctx.Tools.CallAsync` (DOC README:206-216).
- **The bridge answering is not the game being drivable.** The game becomes drivable
  ~40 s after the bridge first responds (owner measurement 2026-08-14). Hold mutations;
  `load_session.py --settle` waits this out (DOC `skills/rimbridge/SKILL.md:156-161`).
- **Two concurrent clients:** each gets its own socket and session. The server-side
  serialization model is **UNVERIFIED** (no source). The only measurement is that two
  concurrent drivers wedged the bridge until one finished (2026-08-15).

### 2.6 Tool registration (how `jawa/*` appears)

1. At startup RimWorld loads mod assemblies. RBS "starts its bridge services after RimWorld
   has loaded normal mod assemblies, then loads companion DLLs from explicit `BridgeTools`
   folders and registers their `[Tool]` methods" (DOC README:195).
2. Companion root: `<RimWorld>\BridgeTools\<bundle>\`, a **sibling of `Mods\`**. It is not
   a mod and has no About.xml (MEASURED csproj header comment). It loads only if
   `brrainz.rimbridgeserver` is active in ModsConfig (DOC skill).
3. Registration reads `[Tool("name", Description=…)]` attributes by reflection over
   **metadata**. Nothing executes, so `JawaBenchInit`'s `[ModuleInitializer]` fires on the
   **first `jawa/` tool invocation**, not at load. The `[JawaBench] ready: N tools` and
   `[JawaBench] context: modSet …, toolSet …` lines therefore appear late, and **their
   absence from a log is UNMEASURED, never "deploy did not take"** (MEASURED
   `JawaBenchInit.cs:18-31`).
4. **Tool names are global.** "collisions are rejected and reported" (DOC README:208).
   A duplicate alias **killed the whole `jawa-bench` provider** until restart (DOC companion
   skill, 2026-09-19).
5. The TPS sampler is started by the `JawaBenchTpsTools` constructor "when RimBridgeServer
   registers companions at game load" (MEASURED comment `JawaBenchInit.cs:146-149`). This
   contradicts point 3 (nothing executes at registration) unless RBS instantiates tool
   classes during registration. That is plausible for instance-method tools but
   **UNVERIFIED**.
6. **Optional-dependency types:** the companion hard-references five of our mods' DLLs
   (§2.2). On a minimal list without them, the types touching them fail to load. The init
   line already handles `ReflectionTypeLoadException` for its own count
   (`JawaBenchInit.cs:191-200`, "(partial)"). **How RBS's registrar handles a partially
   loadable companion is UNVERIFIED** (§7, P5).

### 2.7 One call, end to end

```
agent (WSL)                    python.exe (Windows)                RimWorld process
───────────                    ────────────────────                ────────────────
rimflow bridge take  ──ledger─▶ (no enforcement downstream)
writes Transient/x.py, pushes  ← mirror refresh ≤5 min (or runs Transient\ directly)
python.exe Transient\x.py ───▶ resolve_endpoint(): read Player.log → port, token
                               connect 127.0.0.1:5174 (5 s) ──────▶ RBS socket thread
                               session/hello{token} ──────────────▶ auth
                               tools/list (for check_params) ─────▶ registry
                               tools/call{name,arguments} ────────▶ bind args (ArgGuard prefix)
                                                                    → tool method (thread pool)
                                                                    → ctx.MainThread.InvokeAsync
                                                                       waits for next Update()
                                                                       (needs focus/runInBackground,
                                                                        no long event in progress)
                                                                    → game mutation / read
                               ◀── response {result, operation{Success,…}, state{tick}}
                               (30 s socket timeout: late reply → abandoned id)
                               close → append bridge_sessions.jsonl row
agent reads stdout (CRLF) ◀───
agent: read back the RAW field / screenshot (the one law)
rimflow bridge release
```

### 2.8 The silent-success failure class

This is the property everything else must be designed around.

- "**~40 calls report success and change nothing**" (DOC memory
  `rimworld-bridge-silent-failures`). The catalogue is
  `skills/rimbridge/references/silent-failures.md` (DOC "30+").
- Its sources are layered, and a defence at one layer does not cover another:

| layer | example | defence today |
|---|---|---|
| **wire** | unknown argument name dropped; the call runs on defaults | client `check_params` + companion ArgGuard |
| **envelope** | `operation.Success: true` above payload `success: false` | convention: assert the payload field |
| **tool** | a companion swallows per-item refusals (6×6 zone took 11/36 cells) | design rule 1: return `refused[]` |
| **engine** | advisory setters (`SetFoundation` on a floored cell, `AddEquipment` on an occupied slot, backstory setter refreshes nothing) | per-tool read-back, `*_commit` tools |
| **UI** | a leftover modal absorbs input; every later `execute_debug_action` returns success (5 runs gave 759/448/0/384/384) | `window_list_close`; runner closes known modals at job start and end |
| **session** | **zombie load**: the load aborted (`ErrorWhileLoadingGame`), but the process answers every call with plausible numbers from memory | canary string in Player.log, checked after settling |
| **instrument** | a correct number to the wrong question (`canReach` with the wrong PathEndMode) | reproduce the engine's own call |
| **input** | ModsConfig read as "what is loaded" while the process holds a different list (0/16 vs 16/16 patches) | `jawa/mod_inventory`; `modSet` digest in the log |

---

## 3. Tool surface

### 3.1 Counts (MEASURED 2026-10-10, source census)

Command: a Python regex `\[Tool\(\s*"([^"]+)"` over every `JawaBench.BridgeTools/*.cs` as
whole-file text (a multi-line attribute is the normal form, so a per-line grep undercounts).
Preprocessor nesting was tracked to find `#if JAWA_GM_TOOLS` blocks. Sanity probes:
`jawa/get_defs` and `jawa/spawn_pawn` were both found, and a per-file cross-check on
`JawaBenchTerrainTools.cs` gave 32 by regex against 33 lines containing `Tool(` (one is
prose).

| surface | count | label |
|---|---|---|
| JawaBench `[Tool]` attributes in source | **398** (390 `jawa/` + 8 `deepfire/`), 0 duplicate names, across 88 files | MEASURED |
| of which `#if JAWA_GM_TOOLS` (absent unless built with `--gm`) | **48** | MEASURED |
| RBS built-in tools listed in the 2.3.0 README | **128** (110 `rimworld/` + 18 `rimbridge/`) | MEASURED `grep -cE '^- \`rimworld/'` on the Workshop README; the README is generated from the tool surface (`BEGIN GENERATED:tool-surface`) |
| expected live total with a `--gm` build | ≈526, **UNVERIFIED live** | arithmetic |
| last live count found in a comment | "51/432 live tools" | DOC `rimbridge_client.py:478`, date unknown. The skill's "125 tools" and "91 jawa/" are stale |

⇒ **The tool surface roughly quadrupled in ~7 weeks** (91 `jawa/` on 2026-08-19, 398 now).
`skills/rimbridge/SKILL.md` §1's file table is two months stale.

### 3.2 RimBridgeServer built-in families (DOC: Workshop README tool list)

| family | examples | mutates? | risk / known traps |
|---|---|---|---|
| Bridge diagnostics (12) | `rimbridge/ping`, `get_bridge_status`, `list_capabilities`, `list_operations`, `list_operation_events`, `list_logs`, `wait_for_operation`, `wait_for_game_loaded`, `wait_for_long_event_idle` | no | `ping` is off-main-thread and proves nothing about the game. All-null `get_bridge_status` means the game is unfocused or not running its loop |
| Performance profiling | Dubs Performance Analyzer drive | profiler state | only when DPA is active |
| Scripting | JSON / lowered-Lua scripts, `rimbridge/compile_lua` | yes (runs tools) | script calls are not paged; the Lua subset is not general Lua |
| Debug actions and mods | `list_debug_action_roots/children`, `search_debug_actions`, `get_debug_action`, `execute_debug_action`, mod settings surfaces, `set_colonist_job_logging`, mod load order | **yes** | 🔴 `search_debug_actions` and roots-building can livelock the full list. `execute_debug_action` reaches the whole dev menu. `ToolMapForPawns` accepts player colonists only. Leaf paths must be read, never constructed (tab-keyed nodes). `T: Destroy` by x/z destroys every thing in the cell |
| Architect and map state | `apply_architect_designator`, `get_cell_info`, `get_cells_info` | yes | designators queue work for colonists, so an empty map builds nothing. `get_cell_info` does not list pawns |
| UI and input | `get_ui_layout`, `open_main_tab`, `click_cell`, `open_context_menu`, `scroll_ui_target`, `switch_language` | UI state | modal leftovers. `switch_language` saves prefs |
| Selection and colony | `list_colonists`, `select_pawn` | selection | `pawnId` is `Thing_<id>` here, bare `<id>` from `jawa/list_pawns` |
| Camera and screenshots | `take_screenshot` (with `clipTargetId`), `jump_camera_to_cell` | camera | 🔴 `jawa/clear_ui` first. The debug log window sits where the subject is framed |
| Save/load and spawning | `save_game`, `load_game_ready`, `start_debug_game_ready`, `go_to_main_menu`, `spawn_thing`, `set_time_speed`, `step_game_ticks`, `play_for` | **yes** | 🔴 `save_game` has written the CURRENT slot instead of `saveName` (2026-08-24; the opposite was seen 2026-08-20), so back up and stat Saves. `spawn_thing` NPEs on Pawn defs under VEF (use `jawa/spawn_pawn`) and cannot set stuff. `start_debug_game_ready` once hard-crashed the full list (2026-09-11) and works on 629 mods (2026-09-27). `set_time_speed` must be verified by reading `ticksGame` twice. Unpause is the most consequential call |

### 3.3 JawaBench families (MEASURED source census; `*` = GM-gated)

| family (files) | n | what it is for | mutates | risk / known traps |
|---|---|---|---|---|
| **World authoring** (`WorldTools`, `WorldEdit2`, `LandmarkNameTool`, `MapModeTools`, `CacheTools`, `DiagnosticTools`) | ~47 | planet tiles, biomes, rivers/roads (`world_links_*`), mutators, landmarks, world objects, features, faction relations, imports, lint, seabed layer probe | **yes, persistent once saved** | nothing visible without `world_commit`. 100-row read caps. `world_tile_import` refuses on `expectTiles` mismatch (a subcount shift paints the wrong world) |
| **Terrain, map and spawn core** (`TerrainTools`, `MapTools`, `GenTools2`, `DebugGems1`, `PaintTools`) | ~64 | terrain/roof/substructure batches, `spawn_batch`, `spawn_pawn`, `destroy_batch`, prefab capture/place, fog, gas, `get_defs`, `list_things`, `clear_ui`, genstep/basegen symbol runs, `clear_area`, `make_empty_room`, `hot_reload_defs` (retired) | **yes** | 🔴 `get_defs` takes `defs` as a **string** `"Type/Name;…"`; a list raises `InvalidCastException`, `success:false`, and a substring check reads that as ABSENT. `spawn_batch ops` is a string. Foundation→terrain→things ordering. Multi-cell things spawn centred. Painting kills plants. `list_things` key is `faction` |
| **Pawn editing** (`PawnTools`, `PawnKitTools`, `NeedsTools`, `IdeoTools`, `FlightTools`, `AbilityTools`, `SwcpCharacterTools`) | ~47 | identity, backstory, traits, skills, appearance, gear, health, genes, relations, needs, thoughts, mental breaks, flight state read, abilities, xp | **yes** | raw hediff severity pokes never trigger the needs rebuild. `ResolvePawn` is colonists-only for stock tools. Report `levelRaw` and `levelEffective` |
| **Events, incidents, storyteller, lords** (`EventTools`, `IncidentTools`, `StorytellerTools2`, `GroupTools`, `LordTools2`, `LordJobTools`, `SimTools`, `SituationalTools`, `StoryTools`) | ~75, mostly GM | weather, game conditions, raids (`fire_raid` dry-run default), explosions, fires, skyfallers, incidents (fire, schedule, queue), storyteller swap, lords, social gatherings, rituals, difficulty, damage log, thing lineage | **yes; hands the WORLD permission to act** | the reason the GM gate exists (csproj comment: "a raid tool that is present announces itself as a raid"). Lord and raid spawns near the colony plus unpause equals casualties |
| **Jobs, bills, zones, research, time** (`JobTools`, `BillTools`, `ZoneTools`, `ResearchTimeTools`, `BedTools`) | ~32 | work priorities, drafts, bills, areas, storage, research finish/progress, `time_set_ticks`, `time_pin_normal_speed`, `time_perf` | yes | zone builders must report refusals |
| **Systems, inspection, diagnostics** (`SystemTools`, `StatTools`, `TypeInspect`, `TypeVisibilityTools`, `HarmonyInspect`, `CompanionProbeTools`, `ProofHookTools`, `ModSettingsFieldTools`, `ArgGuard`, `UIRootTools`, `LogAutoOpenSuppress`, `LoadStallProbe`) | ~30 | `mod_inventory`, `running_mods`, `dlc_status`, `savegame_mod_match`, `harmony_patches`, `startup_types`, `comp_read`, `map_comp_read`, `stat_explain`, `bridge_arg_report`, `window_list_close`, `screenshot_mode`, `autosave_now`, `prefs`, `static_call*` | mostly read. `autosave_now`, `prefs` and `static_call` write | `harmony_patches` is honest but answers about the **running** list, not ModsConfig. `static_call` can invoke any public static method (GM-gated) |
| **Render and review staging** (`RenderTools`, `ArtboardTools`, `MiscTools2`, `ReviewLabels`, `NorthstarTools`) | ~22 | `pawn_portrait`, `pawn_atlas`, artboard stage/capture, `take_screenshot` (non-Steam shot), `thing_graphic`, `spawn_variant`, `review_label` | writes PNGs | owner: no fullscreen or focus stealing. Screenshots need `clear_ui` |
| **Map awareness and observability** (`AwarenessTools`, `TpsSampler`, `HostileTools`) | ~10 | `awareness` (arm disk rows), `incident_journal`, `pawn_origin`, `thing_explain`, `wild_spawner_block`, `tps_report`, `kill_hostiles`, `tps_test_*` (GM) | `wild_spawner_block` and `kill_hostiles` mutate | built 2026-10-10, not yet proven live (MEASURED commit 8d5f64275 "built, not deployed"). Events before the first `jawa/` call are not recorded (lazy install) |
| **Mod-specific probes** (FlowWorks ×6 files, Deepfire, Gravship, Vehicles, Droidworks, Oracle, Kcsg, Inhabited, Trade, Transporter, Pipe, Projectile, Cathedral, LoreStage, Shade*, GssPlaytest, Scenario, Faction*, ColonyName/Visibility, Society, TargetFuel, AnimalStats, DefDump) | ~85 | white-box drivers for our mods: canal dig, flood spawn, pit report, playtest runners, gravship launch/land*, trade execute, oracle selftest, def dump run | yes | they hard-link our mod DLLs (§2.6), so on a list without the mod a call is expected to fail with a type-load error; whether registration fails too is UNVERIFIED. FlowWorks flood ticks have outrun the 30 s timeout (2026-10-01) |

### 3.4 Cross-cutting traps that belong to the surface, not one tool

1. **Namespace is provenance, not meaning.** `jawa/spawn_batch` and `rimworld/spawn_thing`
   are the same verb. Guessing `jawa/` is wrong ~84% of the time (DOC skill §1).
2. **`pawnId` formats differ by namespace** (`Thing_Human1066` vs `Human1066`).
3. **The GM gate is binary and coarse.** Without `--gm`, `build.py` refuses as "THIS DEPLOY
   WOULD REMOVE TOOLS". With `--gm`, all 48 world-acting tools ship, `static_call` included.
   There is no per-tool gate and no runtime gate. The owner's campaign game gets the same
   DLL (§7, P20).
4. **Description prose can create phantom tools.** A `jawa/world_*` mention in a description
   made `build.py`'s byte scan see a tool named `jawa/world_`. `tool_surface()` is an upper
   bound by design (DOC companion skill §3 rule 9 and §4).
5. **Discovery tools are dangerous on the full list** (`search_debug_actions`, and
   `list_debug_action_roots` once). `list_debug_action_children` is safe.

---

## 4. Control plane

### 4.1 The bridge lease (`rimflow bridge`)

MEASURED from `src/RimMandrake/rimflow/cli.py:2111-2370` and `model.py`.

| verb | who | effect |
|---|---|---|
| `bridge who` | anyone | re-derives the holder from the ledger, **rewrites** `infrastructure/state/BRIDGE`, and warns if the cross-clone shared lock disagrees (`cli.py:2111-2131`) |
| `bridge take --for "<why>" [--force]` | BENCH, FOUNDRY (and the legacy CHECK) | event `{seat, event:"bridge", state:"taken", purpose}` |
| `bridge release` | any seat, **including a non-holder** (stamped `override: "released the bridge out from under X"`) | event `state:"released"`; clears the shared lock (`cli.py:2191-2224`) |
| `bridge give BENCH\|FOUNDRY\|free` | OWNER only (`./bridge` passes `--seat OWNER`) | event under the target seat with an `override` string (`cli.py:2133-2188`) |

**The take decision** (`cli.py:2227-2330`):

1. Free, or already yours: allowed.
2. `--force`: always allowed, recorded `override: "took the bridge with --force while X still held it"`.
3. The holder's seat has written **no ledger event of any kind** for ≥ `BRIDGE_STALE_SECONDS = 45*60`
   (`model.py:971`), or its last stamp is unreadable: allowed, recorded "X went quiet for N min".
4. Otherwise refused.
5. Before writing, the holder is re-derived from a fresh ledger load. The shared lock is checked
   (refuse if another seat holds it and `touched` is < 45 min old). The event is appended.
   The mirror is re-rendered from a fresh replay. If the replay says someone else won,
   "they took it in the same instant" is printed, and the **later event wins**.
   The code says outright this is **not atomic** (`cli.py:2288-2295`).

**Two witnesses of one fact** (MEASURED):

- **Per-clone ledger shard** `infrastructure/state/ledger/events/<SEAT>.jsonl`. It is visible
  to the other clone only after commit, push and pull.
- **Cross-clone shared lock** `/mnt/d/Luke/dev/_rmscratch/BRIDGE_SHARED.json`
  (`model.py:1011`, `{holder, since, touched, purpose, clone}`). It was added after BENCH and
  FOUNDRY both "held" the bridge a minute apart on 2026-10-07. The holder's every other ledger
  emit refreshes `touched` (`cli.py:335-336`). **A read failure means allow** (`model.py:1022-1032`).
- **The mirror** `infrastructure/state/BRIDGE` is rendered from the ledger and never written
  by hand. It is committed, so it also travels by git.

**Liveness is measured by ledger events, not by bridge traffic.** A seat driving for 1.5 h
without a `rimflow` event reads as stale and can be taken (DOC `skills/rimbridge/SKILL.md:74-80`).
`bridge_sessions.jsonl` (§2.4) does record bridge traffic, but the lease never reads it.

**Enforcement is almost nil** (MEASURED by the control-plane census):

- `model.bridge_gate(seat)` exists (`model.py:2359-2380`). Its **only caller** is
  `modset_builder.py --apply/--restore` (`modset_builder.py:929-948`), and it **fails open**
  when rimflow cannot be imported.
- `rimbridge_client.py` does not check the lease. No `.claude/hooks/*` hook references it.
  `rimdrive/session.py:176-195` takes and releases optionally.
  `northstar_driver/live_session.py` requires `bridge who` to say FOUNDRY before it launches.
- **There is no per-process identity.** Subagents share their parent seat's name, and two
  BENCH windows are indistinguishable (`resolve_seat`, `cli.py:125-155`, order `RIMFLOW_SEAT`
  → `--seat` → `AGENT_SEAT` → session role file).

⇒ The lease is an **attribution and courtesy protocol**, not a lock. Its correctness rests
on every driver (including subagents and ad-hoc `Transient/*.py` scripts) choosing to call
`take` first.

### 4.2 Game state machine

```
   DOWN ──"game load announced"──▶ DEPLOYING ──"game is loading"──▶ LOADING
     ▲                                                                 │
     │                                                          "game is up"
     └──"game is closed"── GOING_DOWN ◀──"game is going down"──────── UP
```

(`infrastructure/GAME_STATE_WORKFLOW.md:22-38`; states in `model.py:283`.)

- **Recorded** by `game` ledger events. The owner announces with `./game <state>`. A seat
  relaying him adds the `--said` flag carrying his verbatim words, and a hook refuses words he
  did not type this session (MEASURED `game:1-130`; `.claude/hooks/block_forged_owner_said.py`).
  `./game` builds a sentence and execs `broadcast.py`. From a seat that only stamps the ledger
  and messages no window (owner 2026-09-29). From the owner it also broadcasts.
- **Measured** by `rimflow/probe.py` (MEASURED):
  - **Process:** `tasklist.exe` finds `RimWorldWin64`.
  - **Bridge:** under WSL, `netstat.exe -ano -p TCP` shows LISTENING on the port scraped
    from Player.log. Elsewhere, a TCP connect.
  - **Verdict:** no process → DOWN; process plus listening → UP; process without
    listening → LOADING; a tasklist failure → UNMEASURED (no reading). The result is cached
    20 s in `infrastructure/state/derived/gamestate_probe.json`.
  - **Auto-correction** (`probe.contradicts`, `probe.py:211-234`): it fixes UP, LOADING or
    GOING_DOWN with no process to DOWN, and DOWN or DEPLOYING with a process to the measured
    state. It writes `measured:true`, the only way a seat may write a `game` event.
- ⚠️ **"UP" means "a socket is LISTENING", not "the game is drivable".** The listener opens
  during the load, long before the ~40 s post-ready settle. It also stays open in a zombie
  session (§2.8) and while the main thread is wedged (runbook classes 2, 3, 7).
- `./game` warns loudly (it never refuses) when the live ModsConfig is not the owner's FULL list
  (MEASURED `game:114-128`). The check runs `modlist_swap.py --status` with stderr discarded,
  so a failing check is silent.
- `rimflow next` offers `needs: bridge` items only when the state is UP or GOING_DOWN and the
  bridge is free or yours (MEASURED `priority.py:36,73-75`).

### 4.3 Launch, kill, restart

**Launching.** Always through Steam: a bare `RimWorldWin64.exe` launch thrice produced the
"Recovered from incompatible or corrupted mods" dialog through a Harmony `TypeLoadException`
(DOC memory, 2026-08-30). **Four different launch idioms coexist** (MEASURED by the utils census):

| script | launch | kill | ready signal | wait budget |
|---|---|---|---|---|
| `bridgetools/launch_and_wait.sh` | `cmd.exe /c start "" steam://rungameid/294100` | `taskkill.exe /F /IM RimWorldWin64.exe` (by image, all instances) | log truncates, then `GABP server running standalone` | about 180 s for truncation plus about 240–300 s for the marker. **Its exit code is unreliable**: "TIMEOUT after 273s" on a load that succeeded at 1005 s (DOC companion skill) |
| `Utils/northstar_driver/live_session.py` | `powershell.exe Start-Process steam://rungameid/294100` | non-forced `taskkill`, 90 s grace, then gives up | a fresh Player.log within 90 s plus `Bridge token:` | 20 s sleep then up to 900 s |
| `Utils/loadsweep/sweep_load.sh`, `biome_load_proof.sh`, `rimbench/gl_sheet_run.sh` | `steam.exe -applaunch 294100` | `taskkill.exe /F /IM` | `Bridge token:` | up to about 420 s |
| owner | Steam UI | closes the game | his eyes | n/a |

- CLAUDE.md says "kill by PID, not pattern" (memory `pkill-f-matches-my-own-shell`). Every
  scripted kill found uses **image name**, which is safe only because exactly one RimWorld is
  ever expected.
- **Cold-load budgets disagree across the tree:** about 15 min on 599 mods (MEASURED by
  CLAUDE.md, 2026-09-07); 25 min in `GAME_STATE_WORKFLOW.md`, `modlist_swap.py` and the
  watchdog's `LOAD_BUDGET_S=1500`; 23–30 min in `modset_builder.py`'s comments; 33 min in this
  task's brief. The minimal list takes about 22 s; a quicktest map about 90 s (DOC).
- **The settle period** of about 40 s after the bridge first answers is implemented only in
  `load_session.py --settle` (MEASURED `load_session.py:177-199`).

### 4.4 Mod list control

- **The live list** is `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`.
  RimWorld reads it **only at startup**, so it describes the **next** load
  (DOC memory `modsconfig-describes-the-next-load`). To know what is loaded **now**, use
  `jawa/mod_inventory` or the `[JawaBench] context: modSet N/<hash>` log line.
- **`modlist_swap.py`** (MEASURED): FULL ⇄ MINIMAL only, from
  `infrastructure/state/modlists/ModsConfig.{FULL.LATEST,MINIMAL}.xml`. It takes a PRESWAP
  snapshot (md5-deduped) and writes atomically (`os.replace`). It has **no game-running check
  and no lease check**.
- **`modset_builder.py`** (MEASURED): 47 named tiers. Each is dependency-closed and always
  carries all five DLCs (`tier_guard` refuses otherwise). `--apply` checks, in order: the
  lease (`bridge_gate`, fail-open), then `tasklist.exe`, then the Player.log mtime < 180 s
  fallback. The backup `deployed/config/ModsConfig.before-tier-<tier>.xml` is named **per
  tier**, so chaining tiers loses the original list (DOC skill §6, still true by code).
  `write_config` writes **non-atomically** (`open(CONFIG,"wb")`, MEASURED
  `modset_builder.py:913-926`). `--restore` copies FULL.LATEST.
- **RimWorld's own recovery:** when a load throws during def resolution, RimWorld can
  **reset ModsConfig to Core-only**. This was hit twice in one night by an inert
  `MayRequire` on `<Operation>` (DOC CLAUDE.md 2026-09-27). The next launch is then a
  Core-only game, and nothing in the toolchain detects that before the launch, apart from
  `./game`'s warning, which needs someone to run `./game`.

### 4.5 Deploy path

| artifact | build | deploy | gate |
|---|---|---|---|
| **JawaBench companion** | `python3 src/RimMandrake/bridgetools/build.py --gm --apply`: stages through `winbuild.stage_build` to `D:\Luke\dev\_rmbuild`, builds with Windows `dotnet.exe` (`--no-incremental`, `-p:JawaGmTools=true`) | `shutil.copy2` straight onto `C:\…\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll` (**not atomic**) | `verify_bundle` (only our DLL in the output), `verify_gm_gate` (length-prefixed name match), refusal if the tool surface shrinks (`--allow-tool-removal`), WinError 1224 → "CANNOT DEPLOY WHILE RIMWORLD IS RUNNING" (MEASURED `build.py:405-436`). **No explicit process check, and no lease check** |
| **Mod DLLs** | `winbuild.py <Mod>`: rsync to `_rmbuild`, `dotnet.exe build -c Release -p:SourceRevisionId=<sha>`, then copies back `*.dll` plus `*.dll.srchash` with mtime ≥ start−2 s, aborting on a `# dll:` hash mismatch (exit 3) | `deploy_custom_mods.py --mod <name>` (dry run), then `--apply` into `C:\…\RimWorld\Mods\<Folder>` | `.srchash` stamp (`src/Directory.Build.targets`) checked at `git push` by `.claude/hooks/block_dll_source_mismatch.py` and `infrastructure/githooks/pre-push` (**fails open** on any checker error) |
| **XML/defs/textures** | none | `deploy_custom_mods.py --apply` | needs a restart. `hot_reload_defs` is retired |

- **The companion's identity is a git SHA**, embedded through `SourceRevisionId`. It is
  HEAD at build time, **even when the tree is dirty**. `build.py` reports
  "DRIFT: same commit, DIFFERENT BYTES" but does not block on it (MEASURED by the census,
  `build.py:354-361`). The deployed companion DLL **has no `.srchash`**: its artifact
  directory is gitignored, so the push guard never sees it.
- **What must be DOWN:** any DLL replacement (memory-mapped, so WinError 1224) and any
  ModsConfig change that should take effect. XML and texture deploys *can* be written
  while the game is up but take effect only at the next start.

### 4.6 Focus, foreground, modals and OS-level input

- **Run in background** must be ON for any unattended run (§2.5). It is a per-machine pref,
  not a per-run setting. Nothing on the machine asserts it, apart from the all-null
  `get_bridge_status` symptom.
- **`game_focus.py` / `focus_heal.py`** (MEASURED): PowerShell `AttachThreadInput` plus
  `SetForegroundWindow`, then Alt plus `AppActivate`, over 4 attempts. `focus_heal` then
  **minimises whatever window holds the foreground** and minimise/restores the game. If both
  fail, `FocusLost`, which the runner records as UNMEASURED(FOCUS_LOST), exit 3. This
  **steals focus by design and contradicts** the owner's 2026-10-04 ruling against
  focus-stealing. Which unattended callers still invoke it is UNVERIFIED.
- **Modals:** a stale `Dialog_ModSettings` or `Dialog_NamePlayerFactionAndSettlement`
  absorbs input and taints every later result. `jawa/window_list_close` closes them, and
  the live_queue runner closes the two known ones at job start and end (DOC runbook row 4).
- **OS-level tools** (MEASURED): `system_screenshot.py` (GDI BitBlt of the full virtual
  screen to a BMP) and `system_click.py` (raw `SetCursorPos` plus mouse down and up, with no
  bounds or foreground check). Both are `python.exe` only. **Under WSL `python3` both print
  "Windows-only" and exit 0**, so a caller checking only the exit code records success. The
  owner gave standing pre-authorisation for screenshots (2026-09-09). Clicks are meant for
  native dialogs such as UAC or firewall prompts.

### 4.7 Background machinery (keep-alive, timers, scheduled tasks)

| unit | where | cadence | does |
|---|---|---|---|
| `\WSL Keepalive` | Windows Task Scheduler | n/a | keeps the WSL VM alive so the systemd timers run (DOC `~/.claude/CLAUDE.md`). Not defined in this repo |
| `RimMandrake\TPS Observer` | Windows Task Scheduler, `pythonw.exe` from the D: mirror | 2 min | copies Player-prev.log into `tps\logs`, writes `observer.jsonl` and `observer_last.json` (docstring `tps_observer.py:15-18`). **Installation is not in the repo**; existence on the machine is UNVERIFIED |
| `RimMandrake\Health Observer` | Windows Task Scheduler | 5 min restart of a long-lived, locked collector | tails Player.log and writes `JawaBench\health\observer_*.jsonl` (docstring `health_observer.py:22-24`). Installation UNVERIFIED |
| `rm-memwatch.timer` | WSL systemd user | 1 min | cgroup OOM/shmem toasts; a `HOST_BUSY_SECS` mode while RimWorld runs |
| `rm-codebase-health.timer`, `rm-objstore.timer`, `rm-pulse*` | WSL systemd user | 15 min / 1 h / 2 min and daemon | not bridge-specific |
| mirror refresh of `D:\Luke\dev\RimMandrake` | "every 5 min" | 5 min | `mirror.py sync --timer` supports it; **the unit file is not in the repo** (UNVERIFIED) |
| belt heartbeat | in-process thread in each runner | 30 s | `.belt_state/heartbeat_<job>.json`; self-kill on budget (exit 4) |

---

## 5. Data and record plane

Everything the bridge system writes, by writer. "SaveData" is `GenFilePaths.SaveDataFolderPath`,
i.e. `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios`. That
mapping is DOC (`tps_record.py`), not decompiled. MEASURED by the data-plane census unless
marked otherwise.

| record | writer | path | trigger | growth / retention | readers |
|---|---|---|---|---|---|
| **Player.log** | Unity | `SaveData\Player.log`; the previous run is `Player-prev.log` | every run; truncated at launch | **one generation of history only**, unless archived (below) | client token scrape, probe, watchdog, `harvest_log.py`, humans |
| Player.log archives | companion `ArchiveLogNow` (start; at quit if `ArchivePlayerLog`); `tps_record.preserve_prev_log` (every `belt_watchdog` pass and every `tps_observer` pass) | `SaveData\JawaBench\tps\logs\Player[-prev]_<…>_<sha12>.log` | as stated | sha-deduped; **7 days / 1 GiB, pruned only by the companion** (so nothing prunes while the game is never launched) | humans, harvest |
| TPS segments (5 s windows, lifecycle, incidents, armed awareness rows) | `JawaBenchTpsWriter` (background thread, bounded queue 4096 + 512 critical reserve, drops counted) | `…\tps\tps_<start>_<session>_<pid>_<seg>.jsonl`, 2 MiB segments | sampler start at companion registration | **7 days / 256 MB**; a session with an `hb_` file modified < 60 s ago is never pruned by another process | `tps_record.py`, `jawa/tps_report` (720-window ring) |
| session / heartbeat | sampler / watchdog | `…\tps\session_<s>.json`, `hb_<s>.json` (tmp then move) | start / periodic | pruned with the segments | observers |
| settings | companion | `…\tps\tps_settings.json`, `awareness_settings.json` | first start (defaults) | static. **Retention can only be raised** | companion |
| observer findings | `tps_observer.py`, `belt_watchdog.py` (through `tps_record`) | `…\tps\observer.jsonl` (append, **no rotation**), `observer_last.json` | 2 min / per watchdog pass | unbounded but small (DOC: "a few rows a day") | `tps_record.read_record` |
| health stream | `health_observer.py` | `SaveData\JawaBench\health\observer_*.jsonl`, `collector_last.json` | scheduled task | 4 MiB segments, **14 days / 256 MB** | `health_observer.py --read`, `tps_record.py --health` |
| awareness journal / origins / damage / lineage | companion | **memory only** (rings 512 / 2048 / 8192 / 16384; 4096 ×2) | Harmony patches, installed lazily on the first `jawa/` call | lost at exit; events before the first call are not seen | `jawa/incident_journal`, `pawn_origin`, `thing_explain`, `damage_log`, `thing_lineage` |
| playtest journals and checkpoints | `GssPlaytest`, `FlowWorksPlaytest` | `SaveData\JawaBench\playtest\<runId>.jsonl`, `*.checkpoint.txt` | per run | **no cap or rotation found** | playtest collect tools |
| exports / PNGs | various tools | `SaveData\DefDump\world_tiles_*`, `world_neighbors.csv`, artboard PNGs, `GenFilePaths.ScreenshotFolderPath` | on call | overwritten or unbounded | `worldview.py`, humans |
| def dumps | `DefDumper` (RimDefDump mod) | `SaveData\DefDump\captures\<stamp>\` | `dump_request.txt` armed, then launch | `.keep` protects; the rest is UNVERIFIED | `refresh.py`, `game_paths.DEF_DUMP` |
| dump registry | `refresh.py` | `infrastructure/state/dumps/REGISTRY.jsonl` (git) | owner freeze | append-only, line-sealed | `refresh.py` |
| bridge session log | `rimbridge_client._log_session` | `D:\Luke\dev\_rmscratch\bridge_sessions.jsonl` | every client session | **append, no rotation**; carries no seat | `northstar_driver/bridge_utilization.py` |
| shared lease | rimflow | `D:\Luke\dev\_rmscratch\BRIDGE_SHARED.json` | take, release, emit | overwritten | rimflow |
| lease / game ledger | rimflow | `infrastructure/state/ledger/events/<SEAT>.jsonl` (git, `merge=union`) | events | append; git history | rimflow |
| BRIDGE mirror | rimflow | `infrastructure/state/BRIDGE` (git) | take, release, who | overwritten | humans, seats |
| probe cache | rimflow | `infrastructure/state/derived/gamestate_probe.json` | probe | 20 s TTL | rimflow |
| belt state | heartbeat, watchdog | `.belt_state/heartbeat_<job>.json`, `watchdog_last.json`, `watchdog_modals.json` (watchdog files written without a lock) | 30 s / per pass | overwritten | watchdog |
| modcheck results | modcheck | `Transient/modcheck/live_queue_results.jsonl`, `obs_amendments.jsonl` | live-queue runs | Transient (about 14 days) | watchdog, observatory |
| ModsConfig snapshots | `modlist_swap.py`, `modset_builder.py` | `infrastructure/state/modlists/*.xml` (git); `deployed/config/ModsConfig.before-tier-*.xml` | each swap / apply | unbounded in git | humans, restore |
| crash reports | `crash_watch.sh` (manual) | `Transient/crash_report_<stamp>.md`, `Transient/rimworld_mem_watch_2026-09-05.log` (hard-coded name) | while running | Transient | humans |

**Privacy and size notes.**

- Player.log contains Windows user paths and the per-launch bridge token. Archives in
  `tps\logs` therefore hold old tokens. They are useless after relaunch and loopback-only.
- `Transient/` is pushed to GitHub (private repo), so anything a bridge script prints there
  is published to origin.
- The largest unbounded writers are `bridge_sessions.jsonl`, `observer.jsonl`, the playtest
  journals and `Saves`.
