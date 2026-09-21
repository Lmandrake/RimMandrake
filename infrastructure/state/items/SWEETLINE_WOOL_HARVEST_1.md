# SWEETLINE_WOOL_HARVEST_1 — the harvest the sweetline trees exist for is not built

## what is wrong

`design/Jawa/worldbuilding/biomes/arid_shrubland.md` §4 defines the sweetline trees around a
specific reward:

> Giants rub against them, so the bark snags shed giant-wool — a rare hanging harvest for
> whoever dares the traffic.

MEASURED 2026-09-21 (found while designing the tree guardian): **there is no giant-wool def
anywhere in `src/`.** The only occurrence of the phrase is the prose above, quoted in a
comment in `src/RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/RUT_AshkarrFlora_Plants.xml`.

Worse, `RUT_SweetlineTree` inherits `TreeBase`'s **wood** harvest with `HarvestDestroys`
true — so the only way to get anything off a sweetline tree today is to **fell it**. The
tree is a named, ancient landmark that roads follow. Felling it is the opposite of the
design.

## why this blocks something

🔴 The owner ruled on 2026-09-21 that the sweetline trees get a **generic guardian species**
(`SHRUBLAND_TREE_GUARDIAN_1`). The guardian's entire purpose is to make the harvest
dangerous — *"dares the traffic"*. **A guardian protecting a harvest that does not exist
guards nothing**, so this is a prerequisite, not a sibling.

## spec

1. A giant-wool item def. Precedent on disk: `RSW_WoolBantha`
   (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Items/RSW_Bantha_Items.xml`) — follow how we
   already do a wool item rather than inventing a shape.
2. A **non-destructive** harvest on `RUT_SweetlineTree` that yields it. ⛔ The tree must
   survive being harvested — override `TreeBase`'s `HarvestDestroys`.
3. Decide whether the wool accumulates over time (it is *shed* by passing giants, not grown
   by the tree) or is a flat plant yield. The fiction says the former; the cheaper build is
   the latter. Say which and why.
4. 🔑 Naming: the label is provisional either way — the giants themselves are under
   `ARIDSHRUBLAND_SHIPPING_NAMES_1`, awaiting the owner's pick from
   `Transient/shrubland_name_drafts_2026-09-21.md`. **Do not ship a wool name that hardcodes
   a giant name he has not chosen.**

## Watch out

- ⚠️ `RUT_SweetlineTree` already shipped (`TREE_GRAPHICS_OWNERSHIP_1`) as a `wildOrder: 4`,
  `wildClusterWeight: 0.05` plant. It is NOT hand-placed one-per-named-instance yet, so
  "every one has a name" is still aspirational — do not build anything that assumes named
  instances exist.
- ⛔ Check `infrastructure/artpipe/done/`, `_artsrc/` and `registry.jsonl` by subject before
  concluding any art is owed.

## criteria

A sweetline tree can be harvested for giant-wool without being destroyed, and the guardian
item has something real to guard.
