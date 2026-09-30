# BRIDGE_MOD_DEBUGACTIONS_NOOP_1 — offline root cause

## Symptom

`rimworld/execute_debug_action` on `Actions\Forge cycle: report state (current map)` and
`...advance one phase (current map)` answered `success: true`, `effects.logCount: 0`, and
Player.log held no line from either method body, though both call `Log.Message`/`Log.Error`
unconditionally.

## Root cause: RimWorld's 10,000-message log cap had switched logging OFF

The debug actions almost certainly RAN. Logging did not.

- `Verse/Log.cs`: `Notify_MessageReceivedThreadedInternal` counts every message; at
  **10,000** it logs `Reached max messages limit. Stopping logging to avoid spam.`, sets
  `reachedMaxMessagesLimit = true` and `Debug.unityLogger.logEnabled = false`. After that
  `PreventLogging` is true and `Log.Message`, `Log.Warning` and `Log.Error` all return at
  the first line. Nothing reaches the in-game log, RimBridge's LogJournal (so
  `logCount: 0`), or Player.log.
- **MEASURED in `Player-prev.log` (the session that ended 2026-09-29 23:30):** line 73836 of
  73864 is `Reached max messages limit. Stopping logging to avoid spam.` Everything after it
  is native Unity asset-unload lines (7 unload cycles, which fits bridge map work), and
  there are no managed log lines at all.
- **What used up the budget:** **8,994** lines of
  `<def> must have plant.MaxMeshCount that is a perfect square.` (`RimWorld/Plant.cs:1000`,
  the `switch` on `maxMeshCount` accepts only 1/4/9/16/25). They come from 8 of our plants:
  RM_RavenNettle 1881, RM_CrystalFlower 1698, RM_RedBugloss 1469, RM_DarkCrust 1274,
  RM_BloodBouquet 1252, RM_Ultracactus 908, RM_Dewfringe 314, RM_Bleedleaf 198. The error
  fires on every mesh print, so it scales with map size and redraws.
- **This is also a real visual defect.** On the `default` branch `num8` stays 1, so extra
  meshes are offset by whole cells (`x += num6 / 1`) and spill into neighbouring cells.

### Hypotheses ruled out (offline)

- **Bridge only invokes `node.action`:** true, but vanilla
  `DebugTabMenu_Actions.GenerateCacheForMethod` builds `node.action` as
  `Delegate.CreateDelegate(typeof(Action), method)` for any `[DebugAction]` with a void
  return. That covers private static methods, since `InitActions` scans `Static|Public|NonPublic`.
  The bridge's `DebugActionExecutionPolicy.Evaluate` returns Direct only when `hasAction`.
  A null delegate would have come back `success: false, "No direct action delegate..."`.
- **Category or submenu node:** `HasChildren` would refuse with "This debug node is a
  submenu". It did not refuse.
- **allowedGameStates:** the bridge does not check it on execute. It only affects visibility.
- **Duplicate TheForge assembly:** irrelevant. Either copy's delegate logs, or would, if
  logging were on.
- **Vanilla `Regenerate Current Map` "working":** it writes no log line, so it was never
  a control for this.

(RimBridgeServer 1.6 ships as DLL only, workshop 3727949765. I decompiled it with
ilspycmd: `RimWorldDebugActions.ExecuteDebugActionResponse`,
`RimBridgeServer.Core.DebugActionExecutionPolicy`.)

## Fix

1. **Content (done here):** every non-square `maxMeshCount` in `src/` is now a perfect
   square: 15 defs in 11 files (2,3→4; 8,10→9). That covers the 8 spammers plus RM_Glower,
   RM_CruciblePod, RM_HoolimbrePlant, RM_Boilbulb, RSW_Ultracactus, RUT_DarkCrust and
   RUT_Glower, which carry the same latent bug. Deploy is owed: the game reads the Mods
   folder, not this repo.
2. **No change to the Forge debug actions.** They are correct.
3. **Bridge workaround while a session is past the cap:** the only reset path in 1.6 is
   the Debug log window's **Clear** button (`EditWindow_Log.cs:139` → `Log.Clear` →
   `ResetMessageCount`). No bridge tool exposes it. Before trusting `logCount: 0` from any
   debug action, check Player.log for `Reached max messages limit`.

## Discriminating live call

This is only needed if doubt remains after the fix deploys. On the next session,
`grep "Reached max messages limit" Player.log` should come back empty. Then run
`execute_debug_action Actions\Forge cycle: report state (current map)`: its `effects.logs`
should hold a `[RMTheForgeDebug]` line. If the cap line is absent and `logCount` is still 0,
the log cap is not the cause and the delegate path needs a second look.
