# INHABITED_ACTION_BRIDGE_CONFIRM_1 — run 1, live, full-583

Game UP, world `Ash'karr` seed `grasshopper` (21,872 tiles), a map loaded (ticksGame 361),
dev mode on. Bridge held by CHECK.

## RESULT: PASS. The action is registered, resolvable and executable.

**The path, verbatim — the string nobody had:**

    Actions\Spawn authored character

`rimworld/get_debug_action` on it:

    "visible": false,  "active": true,  "hasDirectAction": true,
    "execution": { "kind": "Direct", "supported": true, "reason": null }
    "source": { "category": "Inhabited", "allowedGameStates": "PlayingOnMap",
                "hideInSubMenu": false }

## The item's premise was WRONG, and the real cause is simpler

The spec said the action is "two levels deep, a child of a category node named
`Inhabited`". It is not. **`category` is METADATA on a leaf, not a level in the tree.**
All seven Inhabited actions are DIRECT children of `Actions`:

    Actions\Create place at current tile      category Inhabited   visible true
    Actions\Stuff roster (3 pawns)            category Inhabited   visible true
    Actions\Report roster                     category Inhabited   visible true
    Actions\Report displaced pool             category Inhabited   visible true
    Actions\Absorb roster into pool           category Inhabited   visible true
    Actions\Draw 3 from pool                  category Inhabited   visible true
    Actions\Spawn authored character          category Inhabited   visible FALSE

🔑 **Why the original walk missed it, and it is the one thing to remember:**
`Actions` has **childCount 646 but visibleChildCount 146**. The earlier report of "146
children" was the VISIBLE count and read as the whole tree. 500 children were never
listed. `includeHidden` defaults to false on every discovery tool, so a hidden node is
indistinguishable from an absent one.

**And `Spawn authored character` is hidden for a boring, correct reason.** It is the ONLY
one of the seven declared `AllowedGameStates.PlayingOnMap`
(`src/Jawa/Inhabited/Source/DebugActions_Inhabited.cs:227`); the other six are
`AllowedGameStates.Playing` (lines 42, 71, 136, 158, 178, 204). The session is on the
WORLD view, so `PlayingOnMap` evaluates false and the node hides itself. Nothing is
broken. Return to a map and it is visible.

## Not executed
Per the spec, step 4: `CAST_ROSTER_269_LOAD_1` owns the spawn.

## Separate defect found while doing this
`rimworld/search_debug_actions` — the tool the spec named specifically so nobody would
have to walk — **timed out twice** on this stack, at 30s and again at 150s, with
`{"query":"Spawn authored character"}` (params verified against its own schema). The
bridge was healthy either side of both attempts: `jawa/map_zones` answered in seconds
before and after. `rimworld/list_debug_action_children` walked the same 646 nodes with
`includeHidden: true` in seconds. Filed as SEARCH_DEBUG_ACTIONS_TIMES_OUT_1.
