---
name: rimbridge-companion
description: Write, build, deploy and prove new [Tool] methods in the JawaBench companion DLL so the RimBridge bridge can do something it currently cannot - the C# pattern, the one-minute edit-build-deploy-test cycle on a minimal mod list, build.py's guards, and the design rules that stop a new tool becoming another silent failure. Use when a bridge call does not exist, when extending JawaBench.BridgeTools, when a newly added tool is missing from the live tool list, when build.py refuses to deploy, or before writing any C# that touches a running RimWorld from outside.
---

# Adding a tool to the bridge

**The bridge is extensible and doing so is routine, not heroic.** 59 of the companion's 91
tools were written, built, deployed and proven live in a single day. What follows is the
whole loop.

Driving the bridge is the `rimbridge` skill. This one is about *making it able to do more*.

---

## 0. Before you write anything: is it possible?

`design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md` is ~95 candidate tools, each with an
**exact API anchor read from 1.6 source**. Check there first — the hard research is done.

If your target is not there, **read the source via RimSage before writing a line**.
Guessing an API costs a build cycle; guessing a *behaviour* costs a session.
🔴 **Never guess a defName either** — 1,225 BackstoryDefs, 2,129 ThoughtDefs, 336
TileMutatorDefs. Read the def dump.

---

## 1. The cycle — about ONE MINUTE

```
taskkill RimWorld              ⬅ MUST be first; the DLL is memory-mapped
python.exe .../build.py --gm --apply
./launch_and_wait.sh           ⬅ waits for the log to TRUNCATE, then for the marker
python.exe .../prove_<thing>.py
```

* ⚠️ **`python.exe`, not WSL `python3`.** `build.py` hard-exits under WSL, and the bridge
  binds Windows loopback which WSL2 has no route to. The client says so if you forget.
* ⚠️ **Kill the game BEFORE building.** `build.py` cannot overwrite a running DLL and says
  so — but a piped `grep` hides the refusal and you then test stale code and conclude your
  new tool "was not found". **Check for the word `deployed`.**
* 🔴 **`Player.log` persists between runs.** Grepping it for the bridge-ready marker matches
  the PREVIOUS session and returns instantly. `launch_and_wait.sh` waits for truncation
  first — use it, do not hand-roll the wait.
* On the 13-mod minimal list a cold load is **22 s** and a quicktest world **5 s**. See the
  `rimworld-load-round` skill for the swap.

---

## 2. The `[Tool]` pattern

One flat `partial class JawaBenchTerrainTools`, split across files by domain
(`...TerrainTools.cs`, `...WorldTools.cs`, `...MapTools.cs`, `...PawnTools.cs`,
`...EventTools.cs`). The csproj is SDK-style with **no explicit `<Compile>` items**, so a
new `.cs` file in the folder is picked up automatically.

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
    });
}
```

🔴 **Thread affinity is the whole game.** Companion methods are invoked **off** RimWorld's
main thread. Touching a Map or a Pawn from there races the simulation and the renderer, and
Unity does not politely throw — it corrupts or hard-crashes. **Everything inside
`ctx.MainThread.InvokeAsync`, nothing outside it.**

Shared helpers already in the file: `Fail(message, extra)` · `TicksGameSafe()` ·
`DefSuggestions<T>(name)` · `TryParseOps(...)`. There is **no** `Ok` helper — build an
anonymous object with `success` and `ticksGame`.

**Gate anything that acts on the player** behind `#if JAWA_GM_TOOLS` … `#endif`, the same
gate `fire_incident` and `send_letter` use.

---

## 3. The nine design rules, each learned by getting it wrong

1. 🔴 **Report refusals; never `catch {}`.** My own zone builder swallowed `AddCell`
   refusals and a 6×6 stockpile silently took 11 of 36 cells while reporting success —
   *the exact bug class this whole bridge exists to expose.* Return `cellsRequested`,
   `refusedCount` and a `refused[]` list with a reason per item.
2. 🔴 **Read back the RAW field, not the convenient getter.** `SkillRecord.Level` adds
   aptitudes; `Tile.HillinessLabel` is cached forever; `SurfaceTile.Rivers` is
   biome-filtered. Report both when they differ — `pawn_get` returns `levelRaw` *and*
   `levelEffective` so no one can mistake inflation for a failed write.
3. 🔴 **Put the trap in the `Description`.** The tool description is where a future caller
   actually looks. "DOES NOT REDRAW — call `jawa/world_commit`" belongs there, not in a
   commit message.
4. **Destructive defaults to off.** `fire_raid` defaults `dryRun=true`; `pawn_health
   restore` needs `confirmDestructive=true`. Make the caller opt in.
5. **Bulk takes a FILE PATH, not an ops string.** The batch convention caps at
   `MaxOps = 4096`; 21,872 tiles would be six calls and a multi-megabyte payload.
6. **Separate the commit.** `world_commit` / `map_commit` exist because regenerating a mesh
   per write is pathological, and because the invalidation recipe should live in one place.
7. **Check the precondition the engine will not.** `SetFoundation` errors on under-terrain;
   `AddEquipment` no-ops on an occupied primary; `AddLandmark` ignores `IsValidTile`.
   Check first and return a reason.
8. **Assert the identity of what you are editing.** `world_tile_import` takes `expectTiles`
   and refuses loudly — a different planet subcount shifts every tile id and paints the
   wrong world silently.
9. **Avoid `jawa/` prefixes in prose inside descriptions.** `build.py` scans the assembly
   for `jawa/...` literals; a docstring saying *"the `jawa/world_*` family"* created a
   phantom tool named `jawa/world_` and the next build refused to deploy.

---

## 4. `build.py`'s guards are right — read them, do not bypass

| it says | it means |
|---|---|
| `CANNOT DEPLOY WHILE RIMWORLD IS RUNNING` | the OS holds the DLL. Kill the game |
| `THIS DEPLOY WOULD REMOVE TOOLS` | you forgot `--gm`, **or** a docstring made a phantom name |
| `*** DRIFT *** same commit, DIFFERENT BYTES` | uncommitted source. Expected mid-session |
| `built from a DIFFERENT COMMIT` | normal after any commit |

`--allow-tool-removal` exists but **verify the loss is a phantom before using it** — count
the real `[Tool(` attributes in source first.

---

## 4b. Where the rest of the detail lives

| read | when |
|---|---|
| **`references/extending-detail.md`** | you need the exact source/artifact/deploy paths, the `#if JAWA_GM_TOOLS` wiring, the compile errors that will happen to you, and the harness scripts |
| `skills/rimbridge/references/extending.md` | assembly references, the csproj pattern, `IRimBridgeContext`'s composition surface, the `ExcludeAssets="runtime"` gotcha |
| 🔴 `skills/rimbridge/references/silent-failures.md` | **before designing any tool.** It is the catalogue of engine calls that report success and change nothing — i.e. the failures your tool exists to prevent |
| `design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md` | ~95 candidate tools with exact API anchors, already researched |

---

## 5. Prove it, or it is not done

Every tool ships with a `src/RimMandrake/bridgetools/prove_<area>.py`. The bar:

* **read back the value you wrote**, from the raw field
* **a second, independent instrument** where one exists — `jawa/world_stats`' biome
  histogram moved 2059→6035 for a 4,000-tile paint, and the water percentage moved too
* **a screenshot** when the criterion is visual — and `set_fog action=unfogAll` first,
  because a slab in unvisited territory photographs as nothing
* **exercise the refusal path**, not just the happy one. The best evidence in the whole
  session was `Coast` added to 4 tiles being reported as 3, because the fourth was
  genuinely coastal

⛔ **`success: true` is not evidence.** It never was.
