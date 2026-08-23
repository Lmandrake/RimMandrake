## 🔴 DROPPED 2026-08-23 — the owner ruled the Volcano does not need wood

> *"Volcano doesn't need wood, that's fine."* — owner, 2026-08-23

⛔ **Do not add `Plant_TreeDrago` to `Volcano`.** The 23-tile biome stays woodless, and it
stays woodless **by choice** — which is the only thing this item ever actually asked for.
A colony landing there hauls its wood in.

✅ **The `AridShrubland` half stands as ruled:** `RG_Plant_Raspberry` was its only
`RawBerries` source and the loss is accepted.

🔑 **What survives this drop is the CHECK, not the fix.**
`python3 design/Jawa/mods/plant_harvest_coverage.py --against-decisions` still reports
`Volcano` losing `WoodLog`, and that is now a KNOWN and ACCEPTED line, not a defect.
⚠️ Anyone reading its non-zero exit must not re-file this.

---

## spec

🔴 **The owner's plant cuts left the `Volcano` biome with NO wood at all.** Found by
`plant_harvest_coverage.py --against-decisions` the first time it ran, 2026-08-22.

He cut `Plant_TreePine`, `Plant_TreeBirch` and `Plant_TreePoplar` — correctly; a pine
forest on a desert world is exactly the absurdity the pass exists to remove. But those
three were **`Volcano`'s only three `WoodLog` sources**, and nothing else there yields wood.

```
Volcano — 23 tiles
plants 8 -> 5 · wood sources 3 -> 0
🔴 WoodLog leaves this biome entirely. Its only source here was
   Plant_TreePine, Plant_TreeBirch, Plant_TreePoplar.
```

⚠️ **Nothing warns a player.** A colony landing on a Volcano tile has no local wood — no
campfire, no wooden anything — and the game gives no error, because an empty
`wildPlants` intersection is legal.

## 🔴 DECIDE's ruling: the Volcano gets the drago tree

**Add `Plant_TreeDrago` to `Volcano`'s `wildPlants`.** ⛔ Do NOT reinstate any of the three
cut trees; the owner cut them on theme and that ruling stands.

**Why the drago tree specifically:**
- 🔑 **The owner has explicitly endorsed it** — 2026-08-22, verbatim: *"I love the strange
  drago tree, twisting thornwood, and martyr. Very nice!"* It is the wood source he already
  wants on this planet.
- It already grows in `LavaField`, the Volcano's nearest neighbour in every sense —
  volcanic, hot, barren — so this is an extension of an existing placement, not a new idea.
- It is a Core def, so no mod dependency and no load-order question.

✅ **The fallback, if the owner prefers a bare volcano:** leave it woodless and say so out
loud in the biome's description. 23 tiles is 0.1% of the planet and a wood-free volcano is
defensible. ⚠️ But it must be a CHOICE, not an accident — which is what this item makes it.

## what to change

A `PatchOperationAdd` into `BiomeDef[defName="Volcano"]/wildPlants`, in `src/Jawa/Jawa_Patches/`:

```xml
<li Class="PatchOperationAdd">
  <xpath>Defs/BiomeDef[defName="Volcano"]/wildPlants</xpath>
  <value><li><plant>Plant_TreeDrago</plant><commonality>1.0</commonality></li></value>
</li>
```

⚠️ **Read the real `wildPlants` shape off the def before writing this** — the `li` schema
for `BiomeDef.wildPlants` is `BiomePlantRecord`, and the field names above are from memory,
not measured. `measure record Volcano` or the live dump settles it in one call.

⚠️ **Biome plant rosters are read at LOAD, not baked at worldgen.** This is not
worldgen-gated and does not need the world regenerated — unlike biome *assignment*.

## verify

    python3 design/Jawa/mods/plant_harvest_coverage.py --against-decisions

**PASS = exit 0 for `Volcano`**, i.e. it no longer appears in the loss list and reports
`wood sources 0 -> 1` or better. ⛔ A patch that matches nothing logs nothing, so the
coverage run is the proof, not the absence of a red error.

## criteria

- [ ] `Volcano` has at least one `WoodLog` source after the owner's cuts are applied.
- [ ] None of `Plant_TreePine` / `Plant_TreeBirch` / `Plant_TreePoplar` was reinstated.
- [ ] `plant_harvest_coverage.py --against-decisions` no longer lists `Volcano`.

## watch out

- **`AridShrubland` also lost a resource and that one is ACCEPTED, not a defect.**
  `RG_Plant_Raspberry` was its only `RawBerries` source. DECIDE ruled 2026-08-22 that
  berries are a minor forageable, agave covers foraging there, and a desert scrubland
  without raspberry bushes reads better. ⛔ Do not "fix" it.
- `plant_cherrypick_candidates.csv` is derived from `BiomeDef.wildPlants`, so once this
  patch lands the CSV must be rebuilt or the coverage tool will still report zero wood.
