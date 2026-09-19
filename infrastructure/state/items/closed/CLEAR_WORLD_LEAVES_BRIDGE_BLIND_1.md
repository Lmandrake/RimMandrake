# CLEAR_WORLD_LEAVES_BRIDGE_BLIND_1 — the teardown that blinds the instrument you would diagnose it with

Row 4 of 5 split out of `BRIDGE_TOOLS_HARD_BLOCK_1`.

## spec
`MemoryUtility.ClearAllMapsAndWorld()`.

## 🔴 Why this is not merely destructive
It leaves the process with **null fields until a new `Game` is installed**, and in that window
**every other bridge tool throws — including the one you would use to find out what happened.**
That is not a bad outcome, it is an *unreportable* one, and it is the exact shape of
`rimworld-zombie-game-state`: a seat cannot tell a wedged bridge from a dead game.

⇒ **A tool that can wedge the bridge is worse than no tool**, because the next seat's first move
is to distrust the bridge rather than the call.

## The only acceptable design
🔑 **It installs a new `Game` in the SAME call, or it refuses.** There is no third option and no
`force` flag that makes one — an argument that leaves the process bare is a footgun with a
label on it, not a safety.

- `confirmDestructive: true` required, like `jawa/pawn_health restore`.
- The result must be read back through a tool that only works when a Game exists, so a success
  that did not restore the process cannot report success.

## verify
Build clean; then on a SCRATCH session only: call it, and immediately afterwards
`jawa/map_info` or `rimworld/get_game_info` must answer normally. A throw there is a FAIL,
not a caveat.

## criteria
- [ ] Never leaves the process without a Game.
- [ ] `confirmDestructive` required.
- [ ] Proven by a call that succeeds *and* by a following read that works.

---

## Not built

Three other tools in this block were written and compiled today. This one was researched to
the point of writing and then deliberately stopped. **The research is below so the next
attempt starts from evidence instead of repeating it.**

## 1. 🔴 Vanilla has NO teardown that leaves a Game installed. There is exactly one caller.
`MemoryUtility.ClearAllMapsAndWorld()` is called from **one** place in the shipped source:

```csharp
// Verse/GenScene.cs:16
public static void GoToMainMenu()
{
    LongEventHandler.ClearQueuedEvents();
    Current.Game?.Dispose();
    LongEventHandler.QueueLongEvent(delegate
    {
        MemoryUtility.ClearAllMapsAndWorld();
        Current.Game = null;                    // <- the exact blinding this item forbids
    }, "Entry", "LoadingLongEvent", doAsynchronously: true, null, showExtraUIInfo: false);
}
```

⇒ The engine's only teardown **ends with `Current.Game = null`**, which is precisely the
state this item says must never be reachable. So "clear, then install a new Game" is not a
variation on an existing call — it has to be assembled.

## 2. What the assembled version would have to be
The only shipped recipe that installs a fresh Game is `Verse/Root_Play.cs:85`:

```csharp
public static void SetupForQuickTestPlay()
{
    Current.ProgramState = ProgramState.Entry;
    Game.ClearCaches();
    Current.Game = new Game();
    Current.Game.InitData = new GameInitData();
    Current.Game.Scenario = ScenarioDefOf.Crashlanded.scenario;
    Find.Scenario.PreConfigure();
    Current.Game.storyteller = new Storyteller(StorytellerDefOf.Cassandra, DifficultyDefOf.Rough);
    Current.Game.World = WorldGenerator.GenerateWorld(0.3f, GenText.RandomSeedString(), ...);
    Find.GameInitData.ChooseRandomStartingTile();
    Find.GameInitData.mapSize = 250;
    Find.Scenario.PostIdeoChosen();
}
```

## 3. 🔴 THE BLOCKER: doing that inline would be the very failure this item is about
`WorldGenerator.GenerateWorld` at 0.3 coverage is **tens of seconds of synchronous work**.
A bridge tool runs its body inside `ctx.MainThread.InvokeAsync`, so that work would happen
**on RimWorld's main thread with every other bridge call queued behind it** — which is
character-for-character the defect measured in `DEBUG_ACTION_SEARCH_WEDGES_BRIDGE_1`: 30 s
timeout, then minutes of a bridge that reads as wedged.

⚠️ And vanilla never does this inline. **Every one of these calls is wrapped in
`LongEventHandler.QueueLongEvent(..., doAsynchronously: true)`.** Driving a long event from
inside a bridge call, then returning a result that claims the Game is installed before the
event has run, is a *worse* unreportable state than the one this item was filed against.

⇒ **A tool that can wedge the bridge is worse than no tool** — the item's own words, and
they rule out the straightforward implementation, not just the careless one.

## 4. ⚠️ And a scope question that is NOT BUILD's to settle
`CLAUDE.md`, owner 2026-08-18: *"Do not build, extend or tune anything that produces
ALTERNATIVE planets… A knob that can produce a second planet is out of scope even if we
only ever turn it once."*

There is a real argument that a **throwaway debug reset** is the same category as
`rimworld/start_debug_game_ready`, which already generates quicktest worlds and which
`skills/rimworld-debug-testing` is built around. ✅ If so, the resolution is narrow and
obvious: **no seed parameter and no coverage parameter** — hard-code the quicktest shape so
the tool cannot roll a second planet even in principle. But that reading is DECIDE's to
confirm, not BUILD's to assume, because the wording is deliberately absolute.

## What the next attempt should do
1. **Get the scope answer first** — it is one sentence and it decides whether to proceed.
2. Design around `LongEventHandler`, not around a synchronous call: the tool should
   **queue** the rebuild and return immediately with a handle, and a second read tool
   reports whether a Game is now installed. ⛔ Do not return `success: true` from the
   queueing call — that is a success that outruns the work.
3. Keep this item's criteria exactly as written. They are right; only the implementation
   route in the spec is wrong.

---

# CLOSED 2026-08-28 on the owner's word: "close item (3) and (2). Not interested."
Dropped, not deferred. Re-raisable as a fresh item only on a new owner ruling.
