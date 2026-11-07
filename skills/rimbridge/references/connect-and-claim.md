# Claiming the bridge and connecting to it

The full text behind `SKILL.md` §0b and §1: every rule there is stated once in SKILL.md, with its measurement and incidents here.

## 0b. 🔴 Claim the bridge before you drive it — `rimflow bridge take`/`release`

Whoever drives the bridge (a Relentless live round, a Test Pilot, a BENCH sitting
for an owner live look, an L3 evaluation per `infrastructure/VALIDATION_LADDER.md`)
runs `rimflow bridge take` before driving and `rimflow bridge release` the instant
it stops. There is no chat message, no asking and no waiting on another seat's grant.

```
python3 src/RimMandrake/rimflow/cli.py bridge take
...drive it...
python3 src/RimMandrake/rimflow/cli.py bridge release
```

Release it the moment you stop — a borrower who goes quiet has taken the
bridge indefinitely and blocks whoever needs it next, same hazard as before,
just enforced by `rimflow` state rather than a chat handshake. If `bridge
take` refuses because someone else holds it, that is your answer: wait for
their release, or check with the owner if it looks abandoned. `rimflow`'s own
take/release state is the handshake.

🔴 **`rimflow bridge`'s 45-minute staleness rule measures EVENT SILENCE, not game
activity.** Driving the bridge does not by itself refresh the lock — only a `rimflow`
ledger event does — so a seat that drives for 1.5h emitting no events reads as stale to
anyone checking, even though the game is genuinely live. Emit a periodic note while
driving a long session. Before restarting or swapping the mod list on a "stale" hold,
cross-check `rimworld/get_game_info` and `Player.log`'s own mtime against wall-clock —
a session can be genuinely live despite a long-idle ledger (2026-09-08).

⚠️ **And the reverse check matters too: `Player.log`'s mtime can read HOURS stale
relative to a just-recorded `bridge take` event**, if a restart hasn't produced a load
yet or crashed before Unity opened the file. Always `stat` the log's mtime and check
`tasklist.exe` before trusting log content as "this session" — a fresh `bridge take`
event is not proof a fresh process exists yet (2026-09-18).

🔴 **A subagent dispatched to start or wait on a cold load must be told, up front, to
block in a foreground loop — never to end its own turn "to wait for the monitor's
notification."** A subagent has no channel a background-task notification can reach;
only the PARENT session does. Three separate incidents (2026-09-08, 2026-09-12 ×2) had
a bridge-driving or load-waiting agent park itself this way and then sit idle until the
parent noticed and resent the same correction. State it explicitly in the dispatch
prompt, every time — the agent will otherwise reach for it under a genuinely long wait
(a 15–25 min cold load) even when the prompt never asked for anything async.

### What two drivers actually does — measured 2026-08-15 (pre-redesign, still true)

Two seats (then named CHECK and BUILD) called the bridge at the same time and it **went unresponsive**.

⭐ **It did NOT crash, and the game did not need reloading.** It was **stuck**,
and it came back on its own the instant BUILD's call finished. That distinction
is worth a cold load: **if the bridge stops answering, find out who else is on it
and wait for them to release — do not restart the game.** A reload costs ~25–30
minutes and would have bought nothing here.

---


## 1. Connect

```bash
python src/RimMandrake/Utils/rimbridge_client.py --call rimbridge/get_bridge_status --yes-i-know-this-is-live
```

The client scrapes host/port/token from `Player.log`, so a session never starts
with a paste-the-token step that silently uses last launch's value.

* Port **5174**, stable. Token **changes every launch**.
* Protocol **GABP** (`gabp/1`); `session/hello` first or *"Session not established."*
* Tool names use **slashes** — `rimworld/get_game_info`. Dotted MCP spelling is rejected.
* **547 tools on a `--gm` build**, live `tools/list` of 2026-11-01: `jawa/` (411), `rimworld/` (110),
  `rimbridge/` (18), `deepfire/` (8); names in `skills/rimbridge/references/tool_census.txt`.
  49 `jawa/` tools sit behind `JAWA_GM_TOOLS`, so a build without `--gm` should have 498 (arithmetic,
  never read live). This number moves: recount with `python.exe src/RimMandrake/Utils/rimbridge_client.py --list-tools`. The
  `[JawaBench] ready: N tools` log line counts the companion only (419 from source), not the bridge.

**Drive it as a library, never through `--json` on the command line.** Debug
action paths contain backslashes and die twice through bash then JSON.

```python
import sys; sys.path.insert(0, r"D:\Luke\dev\RimMandrake\src\RimMandrake\Utils")   # WSL: /mnt/d/Luke/dev/RimMandrake/src/RimMandrake/Utils  (read-only mirror)
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/list_colonists", {"currentMapOnly": True})
```

In heredocs prefer `chr(92)` over `"\\"` — one escaping layer fewer to get wrong.

### Before the first call

🔴 **From WSL run `python.exe`, never `python3`.** RimBridge binds **Windows
loopback** and WSL2 is a separate network namespace, so `python3` gets
`ConnectionRefusedError` and an empty token — no route, not a timeout. The choice
is **per script, not per project**: talks to the bridge → `python.exe`; reads
`/mnt/c` paths → `python3` (Windows Python cannot resolve `/mnt/c`). A script
doing both must resolve its roots per platform, and no interpreter saves it. When
a run disagrees with a peer's run of the same file, suspect the interpreter
before the data.

🔴 **Turn on Options → Run in background before any unattended run.** RimWorld
ships `<runInBackground>False</runInBackground>`; unfocused it stops running its
main loop — measured 0.5% of one core against 79% — so every game-touching call
times out at 30 s while `rimbridge/ping` answers in 0.5 ms. Set it **in the
game's menu**: `Prefs.xml` is rewritten from memory on exit, so a disk edit while
the game runs is discarded. `src/RimMandrake/Utils/game_focus.py` has a
`preflight()`. An **all-null** `get_bridge_status` — `version` included, which
cannot depend on game state — is this, not "no map is loaded".

⏳ **The bridge answering is NOT the game being reactive.** Owner's measurement,
2026-08-14: the game becomes drivable about **forty seconds** after the bridge
first responds, and every readiness flag we have describes the earlier event.
Read-only calls are fine inside that window; **hold mutations.**
`load_session.py --settle` waits it out and records the wait. Do not optimise it
away because a run once worked without it.

⚠️ **A timeout is fatal to the CONNECTION, not to the call.** The late response
sits in the socket buffer and the next request reads it as its own reply
(`unexpected response id '<guid>'`), so later numbers are quietly wrong rather
than absent. Drop the socket, open a fresh `RimBridge`, and **poll the
post-condition** — never retry on the same connection, and never re-issue a call
whose idempotence you have not established.

🔴 **`python.exe` cannot open a script under `/tmp/...` or the session scratchpad** — those
paths are WSL-only and invisible to Windows Python. Write bridge test scripts into
`Transient/` and run them with a repo-relative or `D:\...` path (2026-09-08).

⚠️ **`python.exe` can spawn `python3` with exit code 0 — but it is a WINDOWS `python3`**,
which dies on `fcntl`/Unix imports. An orchestration script that shells out to `python3`
from inside a `python.exe` process is not reaching WSL. Split responsibilities instead:
`python.exe` drives the bridge only; WSL `python3` owns swap/rimflow/anything Unix-only.
Grade the answer (which interpreter actually ran), never the exit code (2026-09-13).

🔑 **Never type a namespace prefix you did not just read.** `jawa/` records
**which assembly registered the tool**, not what it does — `jawa/spawn_batch` and
`rimworld/spawn_thing` are the same verb in different namespaces, because one was
added and one was already there. Read the leaf out of
`references/capability-matrix.md`, which prints every call fully qualified.
Guessing `jawa/` is wrong about 84% of the time by count.


### Census the companion before you trust any `jawa/` call

**The companion was 91 `jawa/` tools on 2026-08-19** (32 that morning), across five source
files. 🔴 **That number rots — count it, never quote it.** This table is a map of WHERE
things live, not an authority on how many:

| file | tools | reference |
|---|---|---|
| `JawaBenchTerrainTools.cs` | 32 | the original terrain/pawn/thing set — incl. `set_faction_relation`, `ideo_of`, `fire_quest`, `world_neighbors` |
| `JawaBenchWorldTools.cs` | 25 | `references/world-authoring.md` |
| `JawaBenchMapTools.cs` | 15 | `references/map-authoring.md` |
| `JawaBenchPawnTools.cs` | 14 | `references/pawn-authoring.md` |
| `JawaBenchEventTools.cs` | 5 | `weather_get` · `raid_preview` (reads) · `weather_set` · `game_condition` · `fire_raid` (GM-gated) |

**First call of any session: count the `jawa/` names the bridge reports.** Companions
register only at RimBridgeServer startup, so a low count means the deploy did not take,
not that a tool is missing. **0 means the bundle did not load at all.**

🔴 **The deploy must use `--gm`** or the game copy loses every player-acting tool —
`fire_incident`, `send_letter`, `weather_set`, `game_condition`, `fire_raid`. `build.py`
refuses and names them, which is the guard working.

🔴 **`brrainz.rimbridgeserver` must be ACTIVE in ModsConfig.** The companion lives in
`<gamedir>\BridgeTools\`, a **sibling of `Mods\`**, and is discovered *by the bridge
mod at startup* — deploying the DLL is not enough if the mod is off.

⚠️ **Three documents disagreed about this number on 2026-08-13** — 17 in
`EXPECTED_FAILURES_next_load.md`, 20 in `NEXT_RELOAD.md`, 21 here — and the
number moved again to **22** the same night, and to **26** on 2026-08-14.
**Measure it, do not quote it** — `load_session.py` now derives the gate from
`EXPECTED_TOOLS` and `prove_new_tools.py` reads it out of the deployed DLL, so
neither carries a literal to go stale.
A census gate that three files answer differently is worse than no gate, so
measure the DLL rather than quoting any of the three.

⛔ **Not `strings -a … | grep -o "jawa/[a-z_]*" | wc -l`.** That command IS this
incident: it reported **16 of 115** tool names present. A tool name is a custom-attribute
argument living in the UTF-8 blob heap; a method-body MESSAGE is a UTF-16LE literal in
`#US`. One scan can only ever see one heap, and it reports the other as ABSENT with no
error. The blind-scan hook now refuses `strings`/`grep` on a `.dll` outright.

**Game down** — `tool_surface()` reads BOTH heaps, and is an upper bound (a name quoted
inside a message counts once):

```bash
python3 -c "import sys;sys.path.insert(0,'src/RimMandrake/bridgetools');import build;\
print(len(build.tool_surface(open('<gamedir>/BridgeTools/JawaBench/JawaBench.BridgeTools.dll','rb').read())))"
```

**Game up** — `python.exe src/RimMandrake/bridgetools/prove_new_tools.py --census`
(read only). It compares what the GAME registered against what the deployed DLL holds, so
neither side is a quoted number. Deciding strings per tool are in the same file.
