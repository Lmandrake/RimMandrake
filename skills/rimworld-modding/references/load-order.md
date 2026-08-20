# load-order.md — asserting load order, and what a broken one looks like

Moved out of `SKILL.md` §5b on 2026-08-14 to keep the skill body under its
500-line budget. The rules that change your default behaviour stayed in the
skill; what is here is the evidence behind them, the assertion recipe, and the
mod-manager database detail. Open it when an inheritance error appears, when you
are writing the order assertion, or when you are about to touch a sorter's rules
database.

## The damage escapes your mod

A `PawnKindDef` that failed to inherit has no `race`, so `RaceProperties` is null
on it — and vanilla code enumerates *all* pawnkinds. That produced NREs inside
`ThingDef.ResolveIcon`, `ScenPart_StartingAnimal.PossibleAnimals` and
`BiomeDef.CommonalityOfAnimal`, breaking map generation. **None of those stack
traces named a mod.** If worldgen starts throwing, grep the log for
`Could not find parent node` and `Config error in <YourDefPrefix>` before
believing it is a vanilla bug.

## Assert the order in code before every launch

Not by eye, not by trusting the manager. Resolve the load set, find the index of
your mod and of each mod it patches, and fail loudly:

```python
low = [m['packageId'].lower() for m in mods]
for mine, target, why in CHECKS:
    assert low.index(mine) > low.index(target), f"{mine} must load after {target}: {why}"
```

Keep one entry per mod you actually reach into. A three-check version passed
while the order was still broken for a fourth mod.

## Teach the mod manager, or it will keep undoing you

RimSort (and similar) re-sort on demand and will silently scatter your mods.
Fixing the resulting order by hand works but treats the symptom. The manager has
a **user rules** database — for RimSort,
`%LOCALAPPDATA%/RimSort/dbs/userRules.json` — and the distinction that matters
is:

- **`loadAfter`** is a *constraint* — it compiles to a real edge in the dependency
  graph, and a topological sort cannot violate it. **This is the one you want.**
- **`loadBottom`** is neither a hint nor a stronger constraint. It compiles to
  membership in a **tier**, and RimSort sorts four tiers independently then
  concatenates them. ⚠️ **The tier split silently DELETES any `loadAfter` /
  `loadBefore` edge that crosses a tier boundary** (`app/sort/dependencies.py`
  intersects each tier's subgraph with `& tier_mods`). Nothing is logged.
  🔑 Read out of RimSort's own source, 2026-08-19 — see
  `skills/rimworld-start-prep/SKILL.md`, which owns this and carries the code.

Write one `loadAfter` edge per mod you patch. After that the manager produces the
right order unaided and your assertion becomes a cheap safety net rather than a
repeated repair.

(The two ⚠️/🔴 traps in the rules file itself — the `packageId` orphaning, the
stale in-memory view, and reading `ModsConfig.xml`'s mtime before writing it —
stayed in `SKILL.md` §5b, because they are rules you need before you act.)

## The community rules database is not yours to edit

Do not hand-edit the *community* rules database: it is a git clone refreshed on
startup, so local changes vanish. Community rules are a pull request to a public
third-party repo, which is the user's call, never yours.
