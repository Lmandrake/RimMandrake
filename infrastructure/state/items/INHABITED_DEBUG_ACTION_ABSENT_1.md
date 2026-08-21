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
