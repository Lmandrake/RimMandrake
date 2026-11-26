---
name: rimbridge-companion
description: Write, build, deploy and prove new [Tool] methods in the JawaBench companion DLL so the RimBridge bridge can do something it currently cannot - the C# pattern, the one-minute edit-build-deploy-test cycle on a minimal mod list, build.py's guards, and the design rules that stop a new tool becoming another silent failure. Use when a bridge call does not exist, when extending JawaBench.BridgeTools, when a newly added tool is missing from the live tool list, when build.py refuses to deploy, or before writing any C# that touches a running RimWorld from outside. For DRIVING tools that already exist, use the rimbridge skill instead.
---

# Adding a tool to the bridge

**The bridge is extensible and doing so is routine, not heroic.** In a single day
(2026-08-19), 59 of the companion's 91 tools were written, built, deployed and proven live. This skill gives the whole loop. The companion is the
JawaBench DLL, which adds tools to the bridge.

To drive the bridge with tools that exist, use the `rimbridge` skill. This skill is about *making it able to do more*.

**You do not need permission to add a generic bridge tool for a thing that Python cannot control or measure today.** Build
the bridge tool, test first. File a ticket for it only with the test-2 evidence (the list under test 2 of `CLAUDE.md` §Touching code has a cost). Tests, scene steps and verdicts stay in Python (§3, rule 11).
The owner's words: `design/RimMandrake/standing_rulings.md` §What Python cannot reach goes into the bridge's C#.

---

## 0. Before you write anything: does it already exist?

**Hundreds of tools already ship.** The likeliest waste of a session is a rebuild of one of them. Check in this order:

```bash
# 1. what the LIVE bridge reports (authoritative - companions register at startup)
python.exe 'D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\rimbridge_client.py' --list-tools
# 2. or, with the game down, what the SOURCE declares, run from your clone
#    (the jawa/ names only; JawaBenchDeepfireTools.cs also declares deepfire/ names)
grep -ho '"jawa/[a-z_]*"' src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs | sort -u
```

Only after those checks, check whether the tool is *possible*. Read `design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md`. The
roster lists **candidate** tools, each with an **exact API anchor read from 1.6 source**. An API anchor is the engine
member that the tool would call. So the hard research is done.

- The roster lists what could be built, not what has been built.
- The roster's own head says that the list is superseded by `design/Jawa/bridge/dll_capability_roster.html` (185
  capabilities). Use the roster for its API anchors and its reasons.
- The roster was 103 rows on 2026-08-22: 56 built, 10 partial, 37 open.

If your target is not in the roster, **read the source via RimSage before writing a line**. A guessed API costs a build
cycle. A guessed *behaviour* costs a session. 🔴 **Never guess a defName either.** There were 1,225 BackstoryDefs, 2,129
ThoughtDefs and 336 TileMutatorDefs on 2026-08-19. Read the def dump.

**A near-miss existing tool beats a new one.** If an existing tool almost does the job, upgrade that tool. Do not
write a parallel tool. The example is `jawa/get_defs`, which reads DefType/defName pairs plus reflective fields in one
call. By default `jawa/get_defs` is **SCALAR-only**: scalars, Defs, and lists of those. A list of other
objects, such as a `ThoughtDef.stages` array, comes back as type names. A single nested object is left out. A deep-serialize upgrade to `get_defs` closed
that gap (2026-09-01). Pass `deep=true` to read nested objects to 3 levels.

---

## 1. The cycle — about ONE MINUTE

Take the game's driver lock first (the `rimbridge` skill, §0b). Commit your source: `build.py --apply` refuses uncommitted
companion sources, unless you pass `--allow-dirty` because every listed change is yours. Then run this
whole block in ONE Bash call, at the root of your clone:

```bash
GAME=ArchSmall                                                     # the game that you hold: ArchSmall or ArchBig
eval "$(python3 src/RimMandrake/Utils/game_instance.py env $GAME)"  # prints nothing for ArchBig
case "$GAME:${RM_GAME_INSTANCE:-a}" in ArchSmall:b|ArchBig:a) ;; *) echo "this shell means another game"; false;; esac &&
python3 src/RimMandrake/Utils/game_instance.py stop --force --instance $GAME --for "<why>" &&   # MUST be first; the DLL is memory-mapped
python3 src/RimMandrake/bridgetools/build.py --gm --apply --instance $GAME &&   # from your seat clone: stages on D:\ClaudeWork\rimmandrake\build, builds with Windows dotnet, copies the DLL back
src/RimMandrake/bridgetools/launch_and_wait.sh &&
python.exe 'D:\Luke\dev\RimMandrake\src\RimMandrake\bridgetools\prove_<thing>.py'
```

* ⛔ **Keep the block whole.** `launch_and_wait.sh` takes the game from `RM_GAME_INSTANCE`, with ArchBig as the default.
  The launcher kills that game with no lock check. So a lost `eval`, or a launch after a refused `stop`, kills a game that is not yours.
* **Never stop a game by image name** (`taskkill.exe` with `/F /IM RimWorldWin64.exe`). Both games on Archmagi have that
  image name, so the command kills the other game too. `game_instance.py stop` kills by process id.
* **Quote each `D:\` path in bash.** Bash removes the backslashes of an unquoted path, and then `python.exe` cannot find
  the file.
* **Two interpreters, and it is not a contradiction.** You run everything from a **WSL bash shell**.
  `launch_and_wait.sh` is a bash wrapper around `launch_ready.py`. That launcher drives Windows through `.exe` shims, for
  example `taskkill.exe` and `cmd.exe /c start`.
  - Only the bridge-talking **Python** parts must be Windows `python.exe`. The bridge binds Windows loopback, which the WSL
    client cannot reach. Under WSL, `rimbridge_client.py` prints exactly that and tells you to re-run under `python.exe`.
  - Run each such part against the read-only mirror `D:\Luke\dev\RimMandrake`. Push your change first. The mirror tracks
    origin/main within 5 min. `./mirror sync` forces the update.
* ⚠️ **Kill the game BEFORE building.** `build.py` cannot overwrite the DLL of a running game and says so. But a piped
  `grep` hides the refusal. Then you test stale code and conclude that your new tool "was not found". **Check for the line
  that starts with `deployed`**, or for `already deployed`. `state: not deployed yet` is the plan, not a deploy.
* 🔴 **`Player.log` persists between runs.** A grep of the old log for the bridge-ready marker matches the PREVIOUS session
  and returns instantly. `launch_and_wait.sh` moves the old log away first. So use `launch_and_wait.sh`. Do not hand-roll
  the wait.
* On the 13-mod minimal list a cold load is **22 s** and a quicktest world is **5 s**. Both were measured, on 2026-08-19.
  The build and prove steps are not separately timed. So **"about a minute" is practice, not a benchmark.** See the
  `rimworld-load-round` skill for the swap of the mod list.
* ⚠️ **Read the verdict line of `launch_and_wait.sh`, not only its exit code.**
  - Exit 0 is READY. A new game process wrote this run's token line, owns the port and answered a ping. (ArchSmall writes a
    port line, not a token line.)
  - Exit 2 is `DEADLINE_ALIVE`. The process lives but is not ready, and the launcher left that process running. Exit 2 is
    not proof that the load failed.
  - Exit 1 is every other verdict. The game can be up after exit 1 also. To see, run
    `python3 src/RimMandrake/Utils/game_instance.py pid ArchSmall` (or `ArchBig`). Write the name, because `$GAME` is empty
    in a new Bash call.
  - So no exit code but 0 settles the load. The log of this run does: look there for the bridge-ready line and the first
    exception.

🔴 **Two agents that add the same `[Tool]` name kill every tool of the companion.** The bridge refuses a duplicate name.
Then the WHOLE `jawa-bench` tool provider is dead until the next restart, not only the duplicate.

- On 2026-09-19 the foreground session had just committed `jawa/visibility_report`. A fork (a background subagent) added a
  tool of the same name. The error was *"Capability alias 'jawa/visibility_report' is already registered"*.
- The danger is shared state: one game install has one deployed `BridgeTools` DLL and one `RimWorldWin64.exe` process.
- Might a fork or subagent touch `src/RimMandrake/bridgetools/`, deploy, or stop and relaunch RimWorld? Then, before you
  dispatch that fork or subagent, do one of these:
  - keep the fork scoped away from bridge-companion work;
  - in both processes (yours and the fork), grep the tool name against the current tree first.

---

## 2. The `[Tool]` pattern

The tools are one flat `partial class JawaBenchTerrainTools`, split across many files by domain. Examples: `...TerrainTools.cs`,
`...WorldTools.cs`, `...MapTools.cs`, `...PawnTools.cs`, `...EventTools.cs`. The csproj is SDK-style with **no
explicit `<Compile>` items**. So the build picks up a new `.cs` file in the folder automatically.

```csharp
[Tool(
    "jawa/thing_do",
    Description  = "What it does, WHAT IT REFUSES, and what must be called after.",
    ResultDescription = "success, plus the fields a caller will actually check.")]
public static async Task<object> ThingDo(
    IRimBridgeContext ctx,
    CancellationToken cancellationToken,
    [ToolParameter(Description = "...")] string thing = null)
{
    return await ctx.MainThread.InvokeAsync(() =>
    {
        if (Find.CurrentMap == null) return Fail("No current map.");
        // ... every line that touches game state lives inside here, and nothing else does
        return (object)new { success = true, /* read-back */, ticksGame = TicksGameSafe() };
    }, cancellationToken);
}
```

🔴 **Thread affinity is the whole game.** The bridge invokes companion methods **off** RimWorld's main thread. Code that
touches a Map or a Pawn from there races the simulation and the renderer. **Everything inside `ctx.MainThread.InvokeAsync`, nothing
outside it.** Always pass `cancellationToken` to `InvokeAsync` ([references/traps.md](references/traps.md) § 3).

📌 *Provenance, because this skill's whole thesis is that received wisdom is the enemy:* the "Unity corrupts rather than
throwing" claim is in the header comment of `JawaBenchTerrainTools.cs`. The claim is **asserted from the RimBridge SDK
contract and that header comment. Nobody has ever deliberately tested the claim here.** Most other rules below
name the incident that produced them. The thread rule does not. So treat the thread rule as a design constraint
that you have no reason to doubt, not as a measurement.

Shared helpers already in `JawaBenchTerrainTools.cs`: `Fail(message, extra)` · `TicksGameSafe()` · `DefSuggestions<T>(name)`
· `TryParseOps(...)`. There is **no** `Ok` helper. Build an anonymous object with `success` and `ticksGame`.

**Gate anything that acts on the player** behind `#if JAWA_GM_TOOLS` … `#endif`. `fire_incident` and `send_letter` use the
same gate.

---

## 3. The eleven design rules, each learned by getting it wrong

1. 🔴 **Report refusals; never `catch {}`.** An early zone builder of this companion swallowed `AddCell` refusals. A 6×6
   stockpile silently took 11 of 36 cells while the tool reported success. The silent loss is *the exact bug class this whole bridge exists to
   expose*. Return `cellsRequested`, `refusedCount` and a `refused[]` list with a reason per item.
2. 🔴 **Read back the RAW field, not the convenient getter.** `SkillRecord.Level` adds aptitudes. `Tile.HillinessLabel` is
   cached forever. `SurfaceTile.Rivers` is biome-filtered. When the raw field and the getter differ, report both.
   `pawn_get` returns `levelRaw` *and* `levelEffective`, so no one can mistake inflation for a failed write.
3. 🔴 **Put the trap in the `Description`.** The tool description is where a future caller actually looks. "DOES NOT REDRAW
   — call `jawa/world_commit`" belongs there, not in a commit message.
4. **Destructive defaults to off.** `fire_raid` defaults `dryRun=true`. `pawn_health restore` needs
   `confirmDestructive=true`. Make the caller opt in.
5. **Bulk takes a FILE PATH, not an ops string.** The batch convention caps at `MaxOps = 4096`. 21,872 tiles would be six
   calls and a multi-megabyte payload.
6. **Find the invalidation recipe, then either call it or name it in the `Description`.** That recipe is the
   engine call that makes a write visible, for example a mesh rebuild. Bulk world and map writes got `world_commit` /
   `map_commit`. A mesh rebuild per write is pathological, and the recipe belongs in one place. A single-pawn write
   has no such volume. So `set_pawn_appearance` just calls `SetAllGraphicsDirty()` inline. The rule is not "always add a
   commit tool". The rule is: **never leave the caller to discover that a refresh was needed.**
7. **Check the precondition the engine will not.** `SetFoundation` errors on under-terrain. `AddEquipment` no-ops on an
   occupied primary. `AddLandmark` ignores `IsValidTile`. Check first and return a reason.
8. **Assert the identity of what you are editing.** `world_tile_import` takes `expectTiles` and refuses loudly. A different
   planet subcount shifts every tile id, and then the import paints the wrong world silently.
9. **In a description, write another tool's complete name, never a partial `jawa/` prefix.** A docstring said *"the
   `jawa/world_*` family"*. The docstring created a phantom tool named `jawa/world_`, and the next build refused to deploy. `build.py` now
   reads only the real `[Tool]` names, so a phantom no longer stops a deploy. A grep for `jawa/...` with no
   opening quote mark still counts a mention.
10. **Test the empty-collection path, not just the happy one.** `Letter.lookTargets` is a `LookTargets` CLASS field, null on
    any letter with no targets. `jawa/letter_list` dereferenced `.IsValid` unguarded, and only ever ran while the letter
    stack was non-empty (FOUNDRY 2026-08-30). The code now checks for null. A read tool that nobody ran on an empty
    result is not tested.
11. **Build a generic primitive, not a test suite in C#.** A new read is a probe (one named read of game state). A new wait
    is a condition that a stepped advance can stop on. So every proof can reuse the probe or the condition.
    - Ask of each new tool: could a scene of another mod call this tool unchanged? Yes: an instrument, so add it without
      asking. No: a test, a scene or a check of one mod, so keep it in Python.
    - The verdict stays in Python. A probe that cannot see returns `gone` / `oob` / `unbound` / `error`, never 0 or false.
    - Spec: `design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md`.
    - Built: the evaluator (CONDCORE_BUILD_THREE_VALUED_TREES) and the `cond_eval` tool, `jawa/cond_eval`
      (CONDPROBES_WIRE_ENGINE_READS). The ledger records no pass of the live checks of `jawa/cond_eval`. Its item was dropped
      as DONE, because the work landed.
    - Still PLANNED: until-on-advance (ADVANCEUNTIL_WIRE_PER_TICK_STOP) and `cond_watch` (CONDWATCH_BUILD_OWNED_RINGS).
    - Batch a read over a rect or a list rather than add a per-cell call. The batch reads of BATCHREADS_BUILD_ROUND_TRIP_CUT
      are built, for example `jawa/list_things_batch`.
- **A companion C# file may not use #else or #elif:** `selftest_tool_metadata.py` models only '#if JAWA_GM_TOOLS ... #endif' and fails the file. To call a GM-only tool body from an always-built tool, look the method up by reflection (null in a --no-gm build) and say so in the reply.

---

More traps for this section: [references/traps.md](references/traps.md) § 3. The eleven design rules, each learned by getting it wrong.

## 4. `build.py`'s guards are right — read them, do not bypass

| it says | it means |
|---|---|
| `CANNOT DEPLOY WHILE RIMWORLD IS RUNNING` | the OS holds the DLL. Kill the game |
| `THIS DEPLOY WOULD REMOVE TOOLS` | you passed `--no-gm`, **or** your source lacks a tool that the game copy has: an older checkout, a renamed tool or a deleted tool |
| `*** DRIFT *** same commit, DIFFERENT BYTES` | uncommitted source, `--gm` against `--no-gm`, or a changed reference-dir variable. Otherwise someone changed the deployed DLL by hand, or it is from another checkout. Investigate before you overwrite |
| `built from a DIFFERENT COMMIT` | normal after any commit |

⚠️ **With `--no-gm`, `build.py` prints about 50 lost tools** (weather, incident, lord, social and mech-cluster tools are behind
the same flag). The output reads like missing source or a broken checkout, but the flag is the cause.

`--allow-tool-removal` exists, but **verify that each named tool is gone on purpose before you use it**. Count the real
`[Tool(` attributes in source first.

**A scan of tool names must be exact, and a mention is not a declaration.** `verify_gm_gate` is the `--gm` check.
`tool_surface()` is the tool-count census. Both read the attribute table of the compiled DLL through `tool_metadata.py`.
Both are exact for `jawa/` names. Neither sees a `deepfire/` name. A name that another tool's `Description` quotes does not count.

- The reason: an early check was a bare substring match on `jawa/fire_incident`. A tool name merely MENTIONED in another
  `Description` matched, and that blocked every default (non-`--gm`) deploy until 2026-08-28.
- Calibrate any such scan against a known true-positive AND a known true-negative, in both directions.
- `prove_stat_and_room.py` still subtracts a `PHANTOMS` set: two `jawa/` names quoted only in prose, `revoke` and
  `anomaly_`. The subtraction is now a harmless no-op.

---

More traps for this section: [references/traps.md](references/traps.md) § 4. `build.py`'s guards are right — read them, do not bypass.

## 5. Prove it, or it is not done

🔴 **`launch_and_wait.sh` leaves you at the MAIN MENU.** There is no map and no pawn until you start one. A `prove_*.py`
that needs a map opens like this. Copy this opening, because it is the part nobody writes down:

```python
import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\RimMandrake\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()          # scrapes the LIVE token from Player.log
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0); S.connect()

def call(t, **p):                                   # unwraps the GABP content envelope
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

call("rimworld/start_debug_game_ready", timeoutMs=280000,
     readiness="mapData", pauseIfNeeded=True)       # ⬅ THE STEP PEOPLE MISS
for _ in range(120):                                # mapData != Playing; some calls need Playing
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing": break
    time.sleep(1)
```

⚠️ ArchBig's token **changes every launch**, and `resolve_endpoint()` reads it from the log. ArchSmall keeps its token, and
`resolve_endpoint()` takes that token from `GABP_TOKEN` or from ArchSmall's own folder. Never hardcode a token. ⚠️ `readiness="mapData"` does **not** mean `ProgramState.Playing`. Several calls
(anything that touches the camera) silently do nothing until the game is Playing.

The bar for a proof:

* **read back the value you wrote**, from the raw field
* **a second, independent instrument** where one exists. For a 4,000-tile paint, the biome histogram of `jawa/world_stats`
  moved 2059→6035, and the water percentage moved too.
* **a screenshot** when the criterion is visual. Call `jawa/set_fog` with `action=unfogAll` (`set_fog action=unfogAll`)
  first, because a slab in unvisited territory photographs as nothing.
* **exercise the refusal path**, not just the happy one. The best evidence of the 2026-08-19 session: a call
  asked for `Coast` on 4 tiles, and the tool reported 3. The fourth tile was genuinely coastal already.

⛔ **`success: true` is not evidence.** It never was.

---

More traps for this section: [references/traps.md](references/traps.md) § 5. Prove it, or it is not done.

## 6. Where the rest of the detail lives

| read | when |
|---|---|
| **`references/extending-detail.md`** | you need the exact source/artifact/deploy paths (both games' deploy paths), the `#if JAWA_GM_TOOLS` wiring, the compile errors that will happen to you, and the harness scripts |
| `skills/rimbridge/references/extending.md` | assembly references, the csproj pattern, `IRimBridgeContext`'s composition surface, the `ExcludeAssets="runtime"` gotcha |
| 🔴 `skills/rimbridge/references/silent-failures.md` | **before designing any tool.** It is the catalogue of engine calls that report success and change nothing — i.e. the failures your tool exists to prevent |
| `design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md` | candidate tools with exact API anchors, already researched (superseded as a list: see §0) |
| `references/history.md` | the old figures and the lines that are no longer true |

## Building and exporting the companion

More traps for this section: [references/traps.md](references/traps.md) § Building and exporting the companion.
