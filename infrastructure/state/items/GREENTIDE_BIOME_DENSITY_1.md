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
