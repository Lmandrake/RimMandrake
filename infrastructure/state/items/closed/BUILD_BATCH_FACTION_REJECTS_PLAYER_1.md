# BUILD_BATCH_FACTION_REJECTS_PLAYER_1 — two tools, two faction grammars

Measured live 2026-08-26.

```
jawa/spawn_pawn  {faction: "player"}   -> works; the tool documents 'player' | 'hostile' | 'none'
jawa/build_batch {faction: "player"}   -> "No FactionDef 'player'."   8 calls lost
```

`build_batch` wants a FactionDef defName (`PlayerColony`); `spawn_pawn` accepts the friendly aliases.
A caller who learned the grammar from one tool loses a whole batch on the other, and the message
names the value rather than the difference.

**Fix:** accept `player` / `hostile` / `none` in `build_batch` the way `spawn_pawn` does, or say in
the refusal that this tool takes a defName and that `PlayerColony` is what you meant.

⚙️ Same shape, same session: **`jawa/destroy_batch` takes `rects` (plural), not `rect`** — a caller
coming from `jawa/room_get` or `set_terrain_batch`'s `rect` gets *"rects is required"*. Both refuse
loudly, which is right; the inconsistency is the cost.

Found while running `TEMPLATE_ENGINE_ACCEPTANCE_1` criteria 1 and 2.

---

## Already fixed in source

`ResolveFactionAliasOrDef` in `JawaBenchMapInfoTools.cs` is now the ONE faction grammar for the
companion — `player` / `hostile` / `none` aliases plus a FactionDef defName, with a refusal message
that names both grammars. `jawa/build_batch` in `JawaBenchMapTools.cs` calls it.

The `destroy_batch` `rects`-vs-`rect` naming difference is unchanged — the item only asked that the
inconsistency be visible, not that the parameter be renamed.

Undeployed, which is why the live measurement still showed the defect.

## Prove it
```
jawa/build_batch {ops:"DiningChair:20,20", faction:"player"}
```
Expect `placed 1`, no `"No FactionDef 'player'"` refusal.
