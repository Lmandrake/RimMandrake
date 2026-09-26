# GREENTIDE_UNDERSTORY_PLANT_ROSTER_1 — the seven invented non-tree understory plants

Follow-on from `GREENTIDE_JUNGLE_TREE_ROSTER_1` (closed 2026-09-26), filed at that
item's own close per its spec step 5 ("Not an eviction sweep — the non-tree donor
rows are out of this item's scope").

## what shipped already, and what this item owes

`GREENTIDE_JUNGLE_TREE_ROSTER_1` built the roster's 14 invented TREES (rows 1-14,
`RM_Greentide_TreeRoster.xml`) and the signature giant (`RM_Greatbole`,
`RM_Greatbole.xml`), wired into `RM_Greentide_Biome.xml`'s own `<wildPlants>`.

**Owed by this item**: the design doc's seven non-tree understory `Plant` rows —
`design/Jawa/worldbuilding/biomes/greentide_tree_roster_2026-09-22.md` §3d, rows
15-21:

| # | defName | label | replaces the role of | job |
|---|---|---|---|---|
| 15 | `RM_Brakkel` | brakkel | a fruit bush | the forageable staple — **replaces `RM_Greentide`'s `foragedFood` off `RawBerries`** (ruled 2026-09-22; still `RawBerries` today, checked this pass) |
| 16 | `RM_Tumbel` | tumbel | a gourd plant | food plus containers |
| 17 | `RM_Sarquin` | sarquin | a sugar-producing plant | the sugar source — primary host of `RM_Skerrel` (`GREENTIDE_WASP_SWARM_1`), do not design a different tenant |
| 18 | `RM_Phorrik` | phorrik | a spore plant | hazard-with-payoff, medicinal spores |
| 19 | `RM_Wollick` | wollick | a root plant | bulk carbohydrate |
| 20 | `RM_Maddrick` | maddrick | a trap plant | pure hazard, a free perimeter |
| 21 | `RM_Illurin` | illurin | a glowing understory plant | the only light under the canopy — **existing art transfers**: `infrastructure/artpipe/_artsrc/felucianglowspore_v1/felucianglowspore_v1.png`, 256x256, under-resolved against its 7-cell brief (owed re-render, same defect class as the three tree subjects the parent item shipped with) |

## the sight-blocking ruling — read before authoring any of these

🔴 **All seven must block sight** — owner ruling 2026-09-22, verbatim bar: "tall
and broad enough that a colonist cannot see over or past them." This is the
mechanism behind the whole biome (hides the floor for `HOSTILE_MOBILE_PLANTS_1`'s
rooted ambushers, makes "choked with foliage" real at ground level).

⚠️ **How a plant blocks sight in this engine is UNMEASURED and must not be
guessed.** Plant cover and line-of-sight involve `fillPercent` and cover
mechanics — establish the exact field/value live, and establish the side
effects too (shooting, pathing, the player's own visibility of their
colonists) before these seven ship. This is the one thing the parent item's
design doc explicitly flagged as blocking, and it still is.

## art

Six of seven owe art outright (nothing in `artpipe/done/`, `_artsrc/`, or
`registry.jsonl` keys to any of the six non-tree Greentide understory names —
re-check before queuing, per the standing rule, since time has passed). Illurin
transfers existing art per the table above.

## spec

1. Confirm the sight-blocking mechanism on the Desktop (fillPercent/cover) before
   authoring — do not guess a field or value.
2. Author the seven `Plant` ThingDefs (not `TreeBase` — these are non-tree per the
   design doc's own §3d header) at `RM_` tier, wired into `RM_Greentide_Biome.xml`'s
   `<wildPlants>` directly, same file/pattern as the tree roster.
3. Move `RM_Greentide`'s `foragedFood` off `RawBerries` onto `RM_Brakkel`, per the
   already-ruled 2026-09-22 decision — set its nutrition/value deliberately, do not
   inherit the vanilla berry's.
4. Wire sarquin as `RM_Skerrel`'s host per `GREENTIDE_WASP_SWARM_1` — check that
   item's own state before assuming it is still unbuilt.
5. `validate_patch.py --defs` clean (the real 628-mod load set at
   `/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/{Data,Mods}` +
   `.../steamapps/workshop/content/294100` — the WSL view of `/mnt/d/SteamLibrary`
   is a different, mostly-empty install and will falsely report 0 mods found).

## verify

`RM_Greentide`'s `wildPlants` carries all seven rows; `foragedFood` no longer
names `RawBerries`; a colonist genuinely cannot see past a patch of any of the
seven, confirmed live, not assumed from the def.

## criteria

The understory floor is as hidden as the design doc promised, and the biome's
own foraged food is one of its own invented plants.

## Watch out

- Same `<li>`-discards-the-whole-def and `<DefName>commonality</DefName>`
  shorthand traps the parent item's own Watch-out already named.
- ⛔ Do not re-litigate the multi-homing/eviction questions — none of these rows
  touch another biome's roster.
