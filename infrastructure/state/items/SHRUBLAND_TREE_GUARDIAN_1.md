# SHRUBLAND_TREE_GUARDIAN_1 — owner card: tree-guardian uniques (candidate, not yet ruled)

## the ask

`COMMISSION_LEDGER_CLEANUP_1`'s arid_shrubland sheet slug
`tree-guardian-uniques-owner-candidate-not-yet-ruled` names itself, verbatim,
as unruled. The roster's own `new_defs` entry
(`design/Jawa/worldbuilding/biomes/rosters/arid_shrubland.json`) tags its
`mechanic_load` as `"unruled"` — the only slug in this sheet marked that way,
distinct from the others' `"none blocking"` or `"C#: ..."` tags.

The source text, `arid_shrubland.md` §4 "The sweetline trees":

> Each grows only on the optimum, so each is a living surveyor's mark, visible
> for a day's walk; roads follow them and every one has a name. Giants rub
> against them, so the bark snags shed giant-wool — a rare hanging harvest for
> whoever dares the traffic. *(Candidate, owner's suggestion: unique animals
> that dwell near the trees and defend them from human-sized things.)*

**What it is, in one breath:** each sweetline tree (`RUT_SweetlineTree`,
already shipped — `TREE_GRAPHICS_OWNERSHIP_1`) is a named, ancient, huge
landmark. The candidate is a set of unique animals — one per notable tree, or
a species that generically dwells near them — that defend the tree from
anything human-sized, making each sweetline tree a small, dangerous, valuable
place rather than just scenery and a wool harvest.

## the decision this needs

Whether to build this at all, and if so:

- **(a) Build it as a per-tree unique** — each named sweetline tree (roads
  already follow them, they're already landmarks) gets its own named unique
  creature, à la RimWorld's own unique/quest-boss creatures. Heaviest to
  build, most flavourful, and ties directly into the "every one has a name"
  detail already shipped.
- **(b) Build it as a generic species** — one `PawnKindDef` that spawns near
  any sweetline tree and behaves as its guardian (territorial, aggressive
  only near the tree). Cheaper, loses the "every tree is unique" flavour.
- **(c) Drop it** — the sweetline trees stand on their own (named landmark +
  giant-wool harvest) without a guardian mechanic. Simplest; loses the
  "dares the traffic" danger/reward loop the candidate text describes.
- **(d) something else entirely** — your words, verbatim, land straight on
  the design.

## why it matters

This is the one slug in the arid_shrubland sheet's owed-commission list that
cannot be resolved by a builder alone — the register itself flags it
`"unruled"` rather than giving it a mechanic_load a builder could act on, and
the source text calls it a "candidate" (an owner suggestion, not yet a
decision) rather than a specified design. Building ahead of a ruling risks
the exact rework `COMMISSION_LEDGER_CLEANUP_1`'s own "watch out" section
warns against for mechanics-shaped slugs.

## Watch out

- `RUT_SweetlineTree` (the tree itself) is already shipped and is a
  `wildOrder: 4`, `wildClusterWeight: 0.05` plant — it is NOT currently
  hand-placed per-named-instance on the map (`TREE_GRAPHICS_OWNERSHIP_1`'s own
  notes flag "a true monumental multi-cell object... hand-placed
  one-per-sweetline rather than random wildPlants scatter" as still Owed).
  A per-tree unique guardian (option a) likely depends on that hand-placement
  work landing first, or the guardian has nothing specific to guard.
- Re-verify currency before building anything, per this item's own parent's
  standing warning — check `infrastructure/artpipe/` and open items for
  "tree guardian" before queuing art once a ruling lands.

## criteria

An owner ruling lands (which of a/b/c/d, or a rewrite), and either a build
item gets filed against it or this item closes as dropped with the ruling
recorded.
