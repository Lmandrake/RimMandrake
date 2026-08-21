## spec
`CAST_ROSTER_269_LOAD_1`'s criterion is *"dev mode → debug action `Inhabited` / `Spawn
authored character` → pick anyone"*. **That action does not exist in the running game.**

Walked live 2026-08-21, map loaded, dev mode on (the tree answers), FactionControl out:

    Actions   146 children      Outputs   261      Settings  184      = 591 entries
    Actions\Show more actions     8 more
    matches for "Inhabited" or "authored":  NONE

✅ **The assembly itself is fine.** `Player.log` carries
`[Inhabited] ready: 2 patches, 269 characters, 0 places, 0 casts`, and the deployed
`Inhabited.dll` contains the literal **`Spawn authored`** plus two `DebugAction` references.
So it is compiled in and not registering — or registering somewhere the walker does not
reach.

⛔ **CAUSE UNTESTED. Do not write a guess into this item.** The candidates, none checked:
- `[DebugAction]` with `allowedGameStates` that the current state does not satisfy
- registration under a category node `list_debug_action_children` does not traverse — it
  walks ONE bounded level by design, so a nested category is invisible to it
- a `godMode` gate rather than a dev-mode one

⚠️ **What it costs right now:** the hook-versus-traits half of `CAST_ROSTER_269_LOAD_1` has
no instrument. That half is the only moment anyone can see whether an authored hook agrees
with the traits behind it — *"drinks herself into a stupor"* is only honest if she carries
`DrugDesire` — and it stays unverifiable until this resolves.

## verify
Cheapest first, and stop at the one that answers it:

1. Read the `[DebugAction]` attributes in the `Inhabited` source — category, `allowedGameStates`,
   and whether it is `DebugActionType.ToolMap` or an `Action`. That alone may explain it.
2. If it declares a category, try `rimworld/get_debug_action` on the composed path
   `Actions\<category>\Spawn authored character` **verbatim** — the walker not listing a node
   does not mean the path fails to resolve. 🔑 Never CONSTRUCT a leaf path from a guess; read
   it out of the source and use it exactly.
3. Only then consider that it is not registering at all.

## criteria
- the action either resolves through `rimworld/get_debug_action`, or the reason it cannot is
  named from the source rather than inferred
- and `CAST_ROSTER_269_LOAD_1` gets an instrument for the hook-versus-traits check — the
  debug action, or a `jawa/` tool that lists an authored character's name, traits and hook
  together

## notes
Filed by CHECK 2026-08-21 from `CAST_ROSTER_269_LOAD_1`'s partial run. ⚠️ This is NOT a
regression from removing FactionControl — the tree was never walked for this action before,
so there is no earlier state to compare against and nobody should read it as one.

## resolution — BUILD, 2026-08-21, offline, read out of the source

**Cause named, not inferred. The item's step 1 answered it on its own.**
`src/Jawa/Inhabited/Source/DebugActions_Inhabited.cs:40` sets
`private const string Cat = "Inhabited"`, and **all seven** `[DebugAction]`s pass it as
the FIRST argument — the category. So none of them is a child of `Actions`; they are
children of a **category node named `Inhabited`**, one level below it. A single-level
listing of `Actions` returns that category and never its leaves, which is exactly why a
search of the 146 children for `"Inhabited"` or `"authored"` matched no leaf label.
⇒ **candidate 2, confirmed.**

The other two candidates are ruled OUT by the same read:

| candidate | source says |
|---|---|
| `allowedGameStates` unsatisfied | ⛔ NO. `Spawn authored character` is `AllowedGameStates.PlayingOnMap` and the tree was walked with a map loaded. The other six are `AllowedGameStates.Playing`. |
| a `godMode` gate | ⛔ NO. The string `godMode` does not appear in the file. |

🔑 **The repo already held a walker that gets this right** —
`src/RimMandrake/Utils/inhabited_soak.py:find_action()` descends **twice**: `Actions` →
the node whose label is `Inhabited` → its children. It is the one-level walk that was
wrong, not the mod.

⭐ **And nobody needs to walk at all.** The bridge ships
`rimworld/search_debug_actions` — *"search the full debug-action tree globally … so
callers do not need to walk one subtree at a time"*. The call, with the category and
label read out of the source rather than constructed:

    rimworld/search_debug_actions   {"query": "Spawn authored character"}

⚠️ `includeHidden` defaults to **false** on all four discovery tools. If that returns
nothing, re-run with `includeHidden: true` before concluding the action is unregistered.

⛔ **STILL OWED, and it is one call.** BUILD does not drive the bridge — that is CHECK's.
Filed as `INHABITED_ACTION_BRIDGE_CONFIRM_1`.

### the instrument the second criterion asked for — built, and it needs no game

`src/RimMandrake/Utils/cast_hook_audit.py` lists every authored character's **name,
traits and hook together**, because both halves are already in the generated XML: 294
characters in under a second, offline, game up or down.

    python3 src/RimMandrake/Utils/cast_hook_audit.py --who "Adda Wesh"

It flags **15 of 294** hooks whose language promises a mechanic no trait backs — the
`DrugDesire` case the item names is exactly its shape. ⛔ Every flag is a QUESTION for
the author, never a verdict, and the tool always exits 0.

### 🔑 and the "269" is settled in passing

`Player.log`'s `269 characters` is not a loader defect. **294 are authored; 25 are not
deployed.** `CastRoster_DEEPWATER.xml` exists in the repo and is absent from
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Inhabited\Defs\CastRosters\`.
294 − 25 = 269, exact. ⛔ Not deployed by BUILD: the game is up and that mod folder also
holds an assembly the OS has open, so it is a deploy-window action belonging to
`CAST_ROSTER_269_LOAD_1`.
