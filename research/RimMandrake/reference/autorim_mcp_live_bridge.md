# AutoRim MCP — a second, independent live bridge into RimWorld
## What it does, how it differs from ours, and the four ideas worth stealing

**Study date:** 2026-08-19
**Upstream:** `https://github.com/Critical-Reynolds/autorim-mcp` · Workshop `3771536321`
**Licence:** MIT, © 2026 Critical-Reynolds · **Version studied:** commit `89fadf3` (2026-07-25)
**Local clone:** `D:\Luke\dev\reference\autorim-mcp`
**Targets:** RimWorld 1.6, developed against build **1.6.4871** — ⭐ *byte-for-byte the build we
run* (`1.6.4871 rev590` installed, `rev591` in our log)

---

## 1. In one paragraph

AutoRim solves the same problem our RimBridge stack solves — get an agent inside a running
RimWorld — and solves it **differently in every structural choice**. It is a self-contained
mod: a C# assembly that runs its own loopback HTTP server inside the game, plus a Node MCP
server that fronts it. No Harmony, no third-party host mod, no shared SDK. 119 commands are
collapsed into 24 MCP tools. It is aimed at *playing* a colony by natural language, where ours
is aimed at *authoring and measuring* one.

## 2. Why this matters to us specifically

We do not need a second way to reach the game. What we need is a second opinion on the design
of the one we have, and this is the best available: an independent team, same game build, same
problem, different answers. **§6 is the part to act on.**

## 3. Architecture, side by side with ours

```
AutoRim :   Claude ──MCP/stdio──► server/ ──HTTP+token on 127.0.0.1:7789──► AutoRim.dll
                                                                     (a real RimWorld mod)
Ours    :   Claude ──────────────────────► RimBridgeServer (third-party Workshop mod
                                            3727949765, GABP over TCP 5174)
                                                     └─► JawaBench.BridgeTools.dll
                                                         (companion assembly, no About.xml)
```

| | **AutoRim** | **Ours (JawaBench + RimBridgeServer)** |
|---|---|---|
| what ships | one self-contained mod | a *companion* to someone else's mod |
| host we depend on | none | third-party Workshop `3727949765` |
| transport | HTTP/1.1, hand-parsed, port **7789** | GABP over TCP, port **5174** |
| auth | 🔴 **mandatory 32-byte token**, constant-time compare, non-loopback peers rejected at accept | token scraped from `Player.log` each launch |
| main-thread safety | central: queue + `Dispatcher.Pump()` from `GameComponentUpdate` | per-tool: every game-touching line inside `ctx.MainThread.InvokeAsync` |
| surface | 119 commands → **24 MCP tools** (`subsystem` + `action` enum) | **32** `jawa/` tools, flat, plus 125 host tools |
| code shape | ~25 command files by subsystem | **one 6,199-line C# file** |
| Harmony | none — plain `GameComponent` | none |
| JSON | hand-rolled, deliberately | via the host SDK |
| destructive actions | 🔴 **gated: `confirm:true`, preview, autosave, audit log** | ungated; `--gm` compile flag gates two tools |
| tests | 2 PowerShell scripts, incl. a concurrency stress | offline build verification |

**Ports do not collide (7789 vs 5174), and neither does the load order.** The two could run
side by side in the same game.

## 4. The command surface (119, in 21 files)

`analyze` · `bills` · `build` · `caravan`/`world`/`ideology` · `colony` · `control` ·
`designate` (19 commands — hunt, mine, chop, tame, haul, forbid, claim, smooth, slaughter,
deconstruct, strip…) · `equip` · `health`/`animals` · `jobs` · `map` · `meta` ·
`pawns` (manage + read) · `prisoners` · `query` · `research` · `trade` · `work` · `zones`/
`storage`/`areas`.

⇒ **The overlap with our 32 tools is small.** Ours are authoring and measurement primitives —
`set_terrain_batch`, `spawn_batch`, `get_roof_batch`, `world_stats`, `biome_probe`,
`world_tile_export`. Theirs are colony-management verbs — `work.set_priority`,
`bills.add`, `research.set_current`, `designate.hunt`. Almost nothing we rely on is in their
list, and almost nothing in their list is in ours.

## 5. The mechanism worth reading in full

**Their main-thread discipline is centralised and ours is distributed.** Socket threads never
touch game state: a request is enqueued on a `ConcurrentQueue`, the socket thread blocks on a
`ManualResetEventSlim`, and the queue is drained by `Dispatcher.Pump()` called every frame from
`AutoRimGameComponent.GameComponentUpdate()` (`mod-src/AutoRim/AutoRimGameComponent.cs:33`).

Four details in that loop that ours does not have:

1. **An 8 ms per-frame budget** (`Bridge/Dispatcher.cs:20`) — overflow rolls to the next frame,
   so a burst cannot stall the simulation.
2. **A queue cap of 256** (`Dispatcher.cs:23`).
3. **A `GameLoopAlive` heartbeat** with an explicit "never ran" sentinel, so requests are
   rejected at the main menu instead of hanging.
4. **Abandoned-request marking** — a timed-out request is skipped by the pump rather than
   applied after the caller was told it failed. *This is the subtle one*: without it, a
   timeout can still mutate the game.

`GameComponentUpdate` is chosen over `GameComponentTick` deliberately, so the bridge still
pumps **while the game is paused**.

## 6. 🔑 The four ideas worth stealing

1. **Abandoned-request marking.** A timed-out call that lands anyway is the worst failure mode
   a bridge has, because the caller has already been told it did not happen. We should check
   whether `ctx.MainThread.InvokeAsync` can do this at all.
2. **The confirm/preview/autosave/audit gate.** 10 destructive commands refuse without
   `confirm:true`, return a consequence preview, trigger a rate-limited rolling autosave
   (`AutoRim-safety`, once per 60 s), announce in game, and append to `actions.log`
   (`Core/SafetyGate.cs:44-75`). We have nothing equivalent; our nearest analogue is the
   `--gm` **compile-time** flag on two tools. Compile-time is coarser but harder to bypass —
   these are complementary, not competing.
3. **`verify.ps1` asserts the write took effect, not that the call returned success.** It reads
   the value back, greps a save for the mutation, checks the XML still parses, and confirms the
   audit log gained no destructive entries. That is exactly the standard this project already
   demands of a `verify:` clause, implemented for a live bridge.
4. **A startup drift warning.** Their MCP server calls `meta.list_commands` on connect and
   names any tool it exposes that the running mod lacks. We have hit this exact problem: our
   own skill docs said 26 companion tools while the source has 32.

⚠️ **And one anti-pattern confirmed, not stolen:** they too refuse to ship third-party
libraries into RimWorld's AppDomain, hand-rolling JSON rather than loading a second copy of a
common library. Our `build.py` `FORBIDDEN` list enforces the same rule from the other side.
Two independent teams reaching the same conclusion is about as strong as design evidence gets.

## 7. Build and deploy

```powershell
.\scripts\deploy.ps1        # dotnet build -p:RimWorldDir=… then copy About\ + AutoRim.dll
cd server; npm install; npm run build
.\scripts\smoke.ps1                  # /health, 401 on no token, meta.ping round-trip
.\scripts\smoke.ps1 -Concurrency 50  # burst, specifically to surface marshalling bugs
```

- `net472`, references `Assembly-CSharp.dll` + Unity modules with `<Private>false</Private>`
  (copying them would break type identity — the same rule our `FORBIDDEN` list enforces).
- **No prebuilt DLL in the repo**, deliberately: `.gitignore` excludes it with the note that
  committing a binary which must match source ships stale copies.
- **The DLL is memory-mapped while RimWorld runs — close the game before redeploying.**
  Identical constraint to ours (`build.py` hits WinError 1224).

## 8. What would stop us adopting it as-is

- 🔴 **No Node on this machine** — neither WSL nor Windows. Their MCP server needs it.
  (`dotnet.exe` is present, so the *mod* half would build.)
- ⚠️ **WSL cannot reach a Windows loopback port** — our own skill already records this for
  port 5174 (separate network namespace). The same wall stands in front of 7789, so an
  MCP client running under WSL cannot talk to it without the same workaround we already use.
- **It is a player-facing colony-automation tool.** Our campaign is authored, frozen and
  hand-made; "ask for a hunting run and it happens" is not a need we have.
- **Adding a second bridge mod is load-order and support surface** we would carry forever.

⇒ **Recommendation: do not install it. Read it.** The value is §6, and §6 costs nothing.

## 9. Unknowns worth stating

- No CI, no automated tests beyond two PowerShell scripts.
- `About.xml` says "around 115 commands"; the code registers 119. Nothing reconciles them.
- No policy for two MCP clients sharing one bridge.
- Nothing documents multiplayer, dev mode, or non-Windows behaviour.

---

**Related:** `research\RimMandrake\reference\rimsage_rimcp_source_index_mcp.md` (the static
counterpart) · `skills\rimbridge\SKILL.md` and `skills\rimbridge\references\` (our bridge) ·
`src\RimMandrake\bridgetools\JawaBench.BridgeTools\JawaBenchTerrainTools.cs` (all 32 of our
`[Tool]` methods, in one file)
