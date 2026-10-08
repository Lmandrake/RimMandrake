# DEBUG_ACTION_ENUM_CRASH_1 — debug-action tree enumeration crashes on any broad query

Surfaced while correcting `Inhabited/validation.py` for
MODCHECK_SUITE_CORRECTIONS_1 (2026-09-13): trying to discover Inhabited's
real debug-action paths via the bridge's own discovery tools instead of
guessing again.

## spec

`rimworld/search_debug_actions` (ANY query, even `"Inhabited"`) and
`rimworld/list_debug_action_children(path="Actions")` both throw a
`System.NullReferenceException` server-side and return `success: false`
with a full exception dump, rather than a result. Root cause (from the
returned stack trace, not guessed): `RimWorldDebugActions.PrepareNode`
calls `LudeonTK.DebugActionNode.TrySetupChildren()` EAGERLY on every node
it walks while building the response — and `Verse.DebugActionsIncidents.
RitualSiegeWithSpecifics()` (a vanilla debug action living under the same
`Actions` root as every mod's own debug actions) NREs inside its own
`TrySetupChildren` override, in the current game state (no map/no
raid-eligible faction available — reproduced with `hasCurrentGame: false`,
sitting at the main menu). Because `PrepareNode` prepares EVERY sibling
node (not just the ones matching the query) before filtering, one broken
vanilla node poisons every broad enumeration under `Actions`, including
`list_debug_action_children("Actions")` itself.

`rimworld/get_debug_action(path=<exact path>, includeChildren=false)`
(no enumeration, no `TrySetupChildren` on OTHER nodes) still works fine —
that's the tool this session used instead to confirm Inhabited's real
debug-action paths.

## verify

```
PROVE   the crash reproduces on a fresh call (both search_debug_actions and
        list_debug_action_children("Actions")), and reproduces the same way
        whether or not a game/save is currently loaded (confirm both states,
        since RitualSiegeWithSpecifics' own NRE may be state-dependent)
EXPECT  a fix (upstream RimBridgeServer patch, or a defensive try/catch
        around each child's TrySetupChildren in PrepareNode/GetChildren so
        one broken vanilla or mod debug action can't poison the whole
        response) makes both tools return real results again
LIES    none yet -- the tool is honest about failing (success:false +
        exception), not silently wrong; this item exists because the
        DISCOVERY surface is unusable, not because it lies
```

## criteria

`search_debug_actions` and `list_debug_action_children("Actions")` both
return real results again on a fresh call, in both game states (main menu
and a loaded save) -- a broken node anywhere in the tree degrades to a
per-node error entry, never a whole-call crash.

## not chasing

Fixing `Verse.DebugActionsIncidents.RitualSiegeWithSpecifics` itself (base
game code, not ours) -- the fix belongs in RimBridgeServer's own node
enumeration defensiveness (vendored source at
`vendor/mod_sources/RimBridgeServer-main/`), not in patching vanilla.
