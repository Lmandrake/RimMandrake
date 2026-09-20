# DESERT_STAGGERSEED_BUILD_1 — author the staggerseed cycle plant

## what is wrong

desert.md §4b/§7 names the desert's third signature plant — the cycle plant,
working name **staggerseed** (owner's name still owed, unlike the ultracactus,
which the owner already named) — and it has no def, no C#, and no card asking
the owner for a shipping name. `DESERT_SIGNATURE_FLORA_1` authored the
ultracactus and filed this item and `DESERT_SHADE_PLANTS_DESIGN_1` as its
correctly-scoped successors rather than building all three at once.

## why it matters

Per §4b/§7 the staggerseed is not scenery — it is "an active participant in
the patch economy," the desert's only seed-disperser, and its prepared dish is
named a target for the Star Wars cuisine track (§4b: "a controlled near-miss
with a lethal parasite... producing euphoria").

## the work — two mechanisms, both needing C#

- **Corpse-dispersal.** The fruit, eaten raw, "hatches its seeds inside your
  belly," kills the eater, and the dying animal "staggers toward the next
  shade — and dies in it," where the seeds then germinate. This is a
  post-death dispersal mechanic (a lethal ingestion hediff that also biases
  the dying pawn/animal's movement toward the nearest shade before death, then
  spawns the plant near the corpse) — no vanilla CompProperties covers
  "dying creature seeks shade then seeds germinate at its corpse."
- **Euphoric prepared-seed dish.** "Prepared correctly, the preparation lets
  them begin to grow and then perish before they can hurt you — producing
  euphoria." A cooked/prepared meal item with its own ingestible outcome
  (Hediff, euphoria-flavoured) distinct from the raw fruit's lethal one — the
  same plant's two harvested products (raw = deadly, prepared = a delicacy)
  need two different ingestible outcomes on two different ThingDefs.

## gated on a name card

Unlike the ultracactus (owner's name already stands), desert.md marks this
plant's name as "owner's pick. Working: staggerseed." — §7 and §4b both use
the working name only. **File the card before building**: a short,
Star-Wars-flavoured name ask for this one plant, kept separate from the
`EXTREME_DESERT_UNRULED_VERMIN_1` / `SURRA_GRASS_FERTILITYMIN_1` cards per
`DESERT_SIGNATURE_FLORA_1`'s own "Watch out" note — this is a smaller, single-item
ask and should not be bundled with theirs.

## verify

A staggerseed ThingDef (raw fruit, lethal-ingestion + shade-seeking + corpse-seed
mechanic) and a prepared-dish ThingDef (euphoric hediff) both exist, wired into
`RUT_Desert`, under whatever shipping name the owner's card returns — or, if
the name card is still outstanding, this item stays open rather than shipping
under the working name.

## criteria

The staggerseed ships as two ThingDefs plus the C# behind both mechanisms,
under an owner-given name.
