# GREENTIDE_BIOME_DENSITY_1 — choked with foliage, brutal to cross

## the ruling

**Owner, 2026-09-22**, verbatim. He was answering a card about what ~17 new jungle plants should *do*
for the player, and ruled the biome's whole feel alongside it:

> *"2+3, most are useful, many are dangerous. There should be virtually no squares uncovered by lush
> foliage. Choked with foliage. Immediately intimidating to hack through, movement extremely
> difficult."*

Two rulings in one answer:

1. **The economy is BOTH options he was offered, not one** — a real harvest economy (the jungle pays
   for entering it) **and** danger attached to the harvest (the valuable ones are the ones that
   bite). *"Most are useful, many are dangerous."* ⇒ Reward and hazard are frequently the same
   object; that is the design, not a coincidence to be balanced away.
2. **Near-total ground coverage and severe movement cost.** *"Virtually no squares uncovered."*
   Arriving should read as *immediately intimidating*, and crossing it should be a real cost in time
   and work.

## why it is its own item

It is not flora content and not a creature — it is the biome's **generation density and movement
profile**, which lives on the BiomeDef and its plant rows rather than in any one def. It also gates
two other items' designs, so it needs to be settleable on its own:

- 🔑 **`HOSTILE_MOBILE_PLANTS_1` depends on it.** A rooted ambusher is only frightening because the
  ground is invisible. And that item's swarm mechanic (*"activates if others of its own kind
  activate nearby"*) becomes dangerous specifically in proportion to this density — an unbounded
  activation chain across a fully-covered map is a colony-killer. The two must be designed against
  each other.
- `GREENTIDE_JUNGLE_TREE_ROSTER_1` supplies what does the choking, and its strata design (canopy /
  mid-storey / understory) is the vocabulary this density is expressed in.

## what exists — MEASURED 2026-09-22 (parsed off our own files, on the Mac)

`src/RimMandrake/Greentide/Defs/BiomeDefs/RM_Greentide_Biome.xml`:

- `wildPlants` — six vanilla rows (`Plant_TreeOak` 2.0, `Plant_TreePoplar` 1.2, `Plant_Bush` 1.5,
  `Plant_Grass` 2.0, `Plant_TallGrass` 1.0, `Plant_Berry` 0.6). Commonalities are **relative weights
  between plants**, not a coverage figure.
- `forageability` 0.8, `foragedFood` `RawBerries`
- `mudTerrain` `RM_GreentideChurnmud`
- ⚠️ **No `plantDensity`-style field is set on this def** — MEASURED absent. What field actually
  governs total vegetation density, and its vanilla default, is **UNMEASURED and not guessable from
  the Mac** (no game, no def dump, no decompiler here). ⛔ Do not name a field or a number for it
  until it is read off the engine or a vanilla BiomeDef on the Desktop.

✅ **A movement-cost mechanism for this biome already ships, and it is not the answer to this item.**
`RM_GreentideChurnmud` is a high-`pathCost` mire with an escalating `RM_Mired` hediff (slowed, then
stuck) driven by `RM_MapComponent_TerrainMire`. That is **terrain** difficulty. His *"immediately
intimidating to hack through"* is **vegetation** difficulty — a different axis, and the two stack.
⇒ Settle deliberately how much of the movement penalty is mud versus plants, or the biome becomes
impassable by accident.

## spec

1. **Establish the real mechanism on the Desktop first.** Which field(s) govern total plant coverage,
   what vanilla's densest biome uses, and whether "virtually no uncovered squares" is reachable
   through density alone or needs generation help. ⛔ No authoring before this — a guessed field name
   is a silent no-op.
2. **Decide the movement budget across the two axes** (churnmud terrain vs. vegetation), as one
   number the player experiences rather than two systems that happened to add up.
3. **Apply the economy ruling to the roster**: most rows useful, many dangerous, with the valuable
   and the dangerous frequently the same plant. That is guidance for
   `GREENTIDE_JUNGLE_TREE_ROSTER_1`'s rows, not a separate content pass.
4. **Feature-gate it in Mod Settings** per the standing every-mod-ships-settings rule — density and
   movement penalty are exactly the "a number is the experience" case that rule names for tuning
   sliders, and an extreme default needs an escape hatch.

## verify

A generated Greentide map has near-total plant coverage. Crossing it is materially slower than
crossing the biome's own churnmud alone, and the two costs were chosen together rather than
stacking by accident. Settings can soften both. ⛔ No live-proven claim from the Mac.

## criteria

You look at the map when you land and decide to go around.

## ✅ MECHANISM ESTABLISHED AND TUNED — 2026-09-26, FOUNDRY, against live RimSage source

**This is a tuning pass, not a new mechanic.** No new C# is needed; every field named below is a
real, engine-supported BiomeDef/ThingDef/TerrainDef field, verified against the decompiled 1.6
source via RimSage (`Source/RimWorld/BiomeDef.cs`, `Source/RimWorld/WildPlantSpawner`/
`GenStep_Plants.cs`, `Source/Verse/AI/PathGrid.cs`, `Source/RimWorld/Planet/WorldPathGrid.cs`) —
not guessed, and this supersedes the "MEASURED absent"/"UNMEASURED" lines above, which were true
of an earlier revision of `RM_Greentide_Biome.xml` and are stale now (the file already carried
`plantDensity 0.95` / `movementDifficulty 1.6` by the time this item was picked up — added by the
tree-roster work in flight alongside this item, not by this pass).

**🔴 Correction to this item's own framing, and to `greentide_risk_reward_2026-09-22.md`'s §1
table: `BiomeDef.movementDifficulty` is a WORLD-TILE stat, not an in-map one.** It feeds
`WorldPathGrid.CalculatedMovementDifficultyAt` (planet-map caravan travel speed between tiles)
exclusively — MEASURED zero references anywhere in `Verse/AI/PathGrid.cs`, the in-map pathfinder.
So it does **not** stack with churnmud's `pathCost` as the risk-reward doc's §1 assumed ("Two
independent movement taxes stack"); they are different axes entirely, one world-map, one in-map.
This is good news for the item's own acceptance bar, not a problem: **"you look at the map when
you land and decide to go around" is literally the world-map axis**, and `movementDifficulty` is
exactly the field that drives it.

**Two axes, tuned separately, both by real vanilla precedent — no invented numbers:**

1. **World-map avoidance** (`BiomeDef.movementDifficulty`, `BiomeDef.plantDensity`). Calibrated
   against `TropicalSwamp` (`Defs/Core/BiomeDefs/Biomes_Warm.xml`) — vanilla's own closest analog,
   whose description reads "plant-choked... difficult movement... a nightmare." It carries
   `plantDensity 0.99` (the highest of any vanilla BiomeDef found — next is `TropicalRainforest`
   at 0.90) and `movementDifficulty 4` (world tiles only). `RM_Greentide` is now set to match both
   exactly: `plantDensity 0.99`, `movementDifficulty 4` (was 0.95 / 1.6 — undershooting the
   ruling's own comparison class by more than half on the world-map axis). Applied directly to
   `src/RimMandrake/Greentide/Defs/BiomeDefs/RM_Greentide_Biome.xml`.
2. **In-map crossing cost** (`TerrainDef.pathCost` + `ThingDef.pathCost`, both real
   `BuildableDef` fields). `Verse/AI/PathGrid.CalculatedCostAt` (MEASURED, full method read) takes
   the terrain's `pathCost` and then the **MAX** (not sum) of every Thing's `pathCost` standing in
   that cell — plants do not stack with each other or with terrain, but a plant that beats the
   terrain's own cost replaces it for that cell. `RM_GreentideChurnmud` already carries `pathCost
   34` plus the shipped `RM_MapComponent_TerrainMire` escalating-immobilize hediff on top (M8,
   already live) — that axis needs no change from this item. The tree roster's 14 rows (all
   `ParentName="TreeBase"`) inherit `pathCost 42` unchanged from the vanilla base
   (`Defs/Core/ThingDefs_Plants/Plants_Bases.xml` — the same value vanilla's own `Plant_TreeOak`
   ships), and `pathCostIgnoreRepeat` is `false` on every plant base in this project and in
   vanilla, meaning the cost is paid on **every** cell crossed with no discount for walking through
   a solid run of the same plant. Combined with `plantDensity 0.99`, a colonist will be paying a
   tree-tier or bush-tier path cost on very close to every cell of the map — the same order of
   magnitude vanilla's own hardest biome achieves with ordinary trees (`Plant_TreeWillow`,
   `Plant_TreeCypress`, `Plant_TreeMaple`, all plain `TreeBase` descendants at the same 42) plus one
   purpose-built ground plant.
3. **The one piece still owed, and it belongs to a different item.** Vanilla's own precedent for
   ground-level (not canopy) choking is `Plant_Chokevine` (`TropicalSwamp`'s own roster,
   `wildOrder 1` — the same low layer as grass): `pathCost 42` (tree-tier, on a ground plant),
   `wildClusterWeight 200` (vs. `Plant_TallGrass` 10, `Plant_Bush` 5 — deliberately far more
   common), description *"greatly slows down anyone who moves over it."* `RM_Greentide`'s seven
   invented understory rows (`GREENTIDE_UNDERSTORY_PLANT_ROSTER_1`, open, not this item's content
   to author — needs its own coined names, sight-blocking `fillPercent` measurement, and art) are
   the right home for this, and a note citing this exact precedent (pathCost/wildOrder/
   wildClusterWeight neighbourhood) has been left on that item so its pathCost values are chosen
   against real vanilla calibration rather than invented cold.

**Feature-gating (spec step 4, every-mod-ships-settings rule):** not built this pass — the two
tuned BiomeDef fields are exactly the "a number is the experience" case the standing rule names,
so a Mod Settings slider for `plantDensity`/`movementDifficulty` is real owed work, filed as a
follow-on (`GREENTIDE_DENSITY_SETTINGS_1`) rather than guessed here without touching the mod's
`Mod_GreentideSettings`-equivalent scaffolding blind.

**Not done, and correctly out of scope:** no live/visual verification ("judge by LOOKING, ship as
a savegame") — this item's own Watch-out already says so, and per the standing rule against
unattended flyer-style live hunts, a def-level tuning pass reads its own values; a human-judged
"does it look choked" pass needs the owner or a `rimworld-live-review` session, not a solo FOUNDRY
bridge session guessing at what "looks right."

## Watch out

- 🔴 **Judge this by LOOKING, and ship it as a savegame.** "Choked" and "immediately intimidating"
  are visual judgments, not numbers — the standing rule is that options he must look at ship as a
  save he can walk, not a screenshot. Density that reads as *lush* versus *noisy* cannot be settled
  from a def file.
- ⚠️ **Near-total coverage has costs beyond feel**: plant count affects performance, and it interacts
  with fire spread, with the biome's own hard ban on flammable living flora, and with whether a
  player can build anything without a clearing pass. Say which of those were considered.
- ⚠️ `foragedFood` is currently `RawBerries`, a vanilla row. If most of the new flora is useful, the
  foraged yield probably should not stay a vanilla berry — but that is a roster decision, flagged
  here rather than assumed.
- ⛔ Do not express density by inflating `wildPlants` commonalities. Those are relative weights;
  raising them all changes nothing about total coverage.
