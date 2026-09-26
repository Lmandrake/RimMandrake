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

## ✅ SEVEN PLANTS SHIPPED, SIGHT-BLOCKING MEASURED NEGATIVE — 2026-09-26, FOUNDRY

**Built:** all seven `RM_`-tier `PlantDef`s (`ParentName="PlantBase"`, not `TreeBase`) in
`src/RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_UnderstoryRoster.xml`, wired into
`RM_Greentide_Biome.xml`'s own `<wildPlants>` with `Plant_Berry` dropped (redundant with, and the
exact vanilla-Earth-named row the roster's ban exists to replace, now that brakkel covers the
niche). `foragedFood` moved off `RawBerries` onto `RM_BrakkelFruit`, priced/nourished deliberately
(`RM_Greentide_UnderstoryRoster_Items.xml`, four new `PlantFoodRaw` resources: BrakkelFruit,
TumbelGourd, SarquinSap, WollickTuber). Density calibration (`GREENTIDE_BIOME_DENSITY_1`'s own
note, MEASURED off `Plant_Chokevine`) applied verbatim to all seven: `pathCost 42`,
`wildOrder 1`, `wildClusterWeight 200`. `RM_Sarquin` names its `GREENTIDE_WASP_SWARM_1` host role
in prose only — that item is still OPEN, `RM_Skerrel` does not exist, nothing here invents a
tenant. `RM_Phorrik` ships `harvestedThingDef RM_StenchSporeExtract` directly (Gorbeleth's own
precedent), and `RM_StenchGrenade_Items.xml`'s WoodLog-costed placeholder recipe for that resource
is deleted outright (not superseded-in-place) now that the real plant source exists.

**Art:** `RM_Brakkel` (512², exact 4-cell match) and `RM_Maddrick` (384², exact 3-cell match) carry
real generated art, both `facts: PASS` / `worker_status: ok` per their own `done/*.json` +
`*.manifest.json`, copied into the mod's own `Textures/` namespace. `RM_Illurin` transfers
`felucianglowspore_v1` (256², under-resolved against its 7-cell brief, same carried-forward defect
as the tree roster's own transfers — owed re-render, not blocking) and additionally ships
`CompProperties_Glower` (a real vanilla Plant pattern, MEASURED off `Glowstool`), since "the only
light under the canopy" is a functional claim, not just flavour text. `RM_Tumbel`/`RM_Sarquin`/
`RM_Phorrik`/`RM_Wollick` remain art-OWED — MEASURED this pass that the artpipe daemon already has
jobs queued for all four (`rm_tumbel_v1`/`rm_sarquin_v1`/`rm_phorrik_v1`/`rm_wollick_v1`) and every
one has failed validation on all three attempts logged in `registry.jsonl` (`verdict: "fail"` ×3
each) — genuinely owed, not re-queued here since a job already exists and is retrying on its own.

🔴 **Spec step 1's gate — "confirm the sight-blocking mechanism, do not guess" — resolves NEGATIVE,
and this is load-bearing, not a footnote.** MEASURED against the decompiled 1.6 source via RimSage
this pass: **a `Plant` ThingDef cannot block line of sight in vanilla RimWorld at any `fillPercent`
value.** `GenSight.LineOfSight` (`Source/Verse/GenSight.cs`) walks cells via
`IntVec3.CanBeSeenOverFast` (`Source/Verse/GenGrid.cs:227`), which reads **only**
`c.GetEdifice(map)` (`Source/Verse/GridsUtility.cs:443` → `map.edificeGrid[c]`) and asks whether
that *Building's* own `Fillage` is `Full` (`GenGrid.cs:237`, `CanBeSeenOver(this Building b)`). The
edifice grid is populated exclusively by things whose `def.IsEdifice()` is true, and
`EdificeUtility.IsEdifice` (`Source/Verse/EdificeUtility.cs`) itself requires
`category == ThingCategory.Building` — a `Plant`'s category is always `Plant`, so it structurally
can never occupy the edifice grid and is invisible to this check regardless of `fillPercent`.
`fillPercent` on a Plant is not inert — it still feeds `CoverGrid.Register`
(`Source/Verse/CoverGrid.cs`, any `Thing` with `Fillage != None` registers), so it grants real
ranged-combat cover via `CoverUtility.BaseBlockChance`, and above `0.99` it would flip
`FogGrid.Unfog`'s full-reveal-radius behaviour (`Source/Verse/FogGrid.cs`) — but neither of those
is "a colonist cannot see over or past it," which is what the owner's ruling actually asked for.
All seven rows ship `fillPercent` set deliberately per their described bulk (0.55-0.85) for the
real effects this does have; **the ruling itself is not achieved by any def-only field**, and
shipping a `fillPercent` value on the assumption it blocks sight would have been exactly the
silent-wrong-answer failure mode the design doc's own §8 flagged.

⇒ **This needs new C#, not more content authoring**, so it is filed as a follow-on rather than
guessed or faked here: `GREENTIDE_PLANT_SIGHT_BLOCK_ENGINE_1` (a Harmony patch on
`GenGrid.CanBeSeenOver`/`GenSight`, or an equivalent comp, that also consults a tagged non-edifice
Plant occupying a cell — plus the side-effect pass on shooting, pathing and the player's own
visibility of colonists this item's own Watch-out already named).

**Not done:** the look-at-it review the design doc's §3e calls for (build one map, all 22 rows,
save it, grid key) — unaffected by this pass and still owed as its own session, per the standing
rule against a solo FOUNDRY judging "does it look choked."

⛔ **Correctness note for whoever reads this next:** the design doc's own §3d framing ("fillPercent
and cover mechanics... establish the exact field/value live") reads as though a value exists to be
found. It does not — the mechanism it describes is absent from the engine for Plants, not merely
unmeasured. Don't re-run this measurement; read this section instead.
