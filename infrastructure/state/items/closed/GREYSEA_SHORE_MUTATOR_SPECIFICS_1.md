# GREYSEA_SHORE_MUTATOR_SPECIFICS_1 — the shore is generic; the Grey Sea's shore should not be

## the ruling

Owner, at the bench 2026-09-26, typed: *"Make sure the shore mutator respects the specifics
of the grey sea."*

With reference art, of *"the crusty whiteness that should be on every Grey Sea shoreline"*:
`design/Jawa/worldbuilding/reference/grey_sea/02_crusted_white_shoreline.png` — lumpy
cauliflower-like salt crusts heaped over red-brown stones right at the waterline.

## what exists, MEASURED 2026-09-26

`mandrake.rm.seashores` ships exactly **one** file:
`Defs/TileMutatorDefs/RM_SeaCoast.xml` — a single `TileMutatorDef` deliberately shaped as a
drop-in twin of vanilla's `Coast` (same `Coast` category, same `genOrder` 100, same priority
0, so it cleanly replaces a Coast/Lakeshore rather than conflicting).

⇒ **It is one shore for all four seas.** A shoreline on the Grey Sea, the Twilight Sea, the
Propane Lake and the Scald all generate identically today. Nothing in it knows which sea it
borders.

🔑 That genericity was the right first move — it fixed the real bug, which was that a map
beside one of our seas got *vanilla ocean*. This item is the next step, not a correction of it.

## what the Grey Sea's shore should be
From `the_grey_deep.md` and `terminator_sea.md`, plus the owner's reference:
- **Crusted white salt** over the stones at the waterline — the defining look.
- The sea is **hypersaline and shrinking fastest**; the sheet calls the retreating shoreline
  *"free surveying for anyone who can read the terraces"*, so exposed terraces are a feature.
- The sheet's `## Always true`: *"One day this will all stand in open air (the sea is dying),
  and someone will walk the statuary dry-shod."*

## the design question this item must answer first
⚠️ **Do NOT assume the answer is four mutators.** Decide deliberately between:
- **(a) one mutator that reads the bordering sea's biome** and picks terrain/scatter from it —
  keeps one def, needs the worker to resolve which sea it faces;
- **(b) one mutator per sea**, each in the `Coast` category — simpler each, four to maintain,
  and the category-replacement behaviour must still hold;
- **(c) a shared base plus per-sea overrides.**

🔑 Read `RM_SeaCoast.xml`'s own header before choosing — it explains why the category, genOrder
and priority are what they are, and any option that breaks `Tile.AddMutator`'s
replace-on-equal-priority behaviour is wrong however good it looks.

## criteria
- [ ] Route chosen between (a)/(b)/(c) with the reason written down.
- [ ] The Grey Sea shore carries its crusted white salt, matched against the reference image.
- [ ] The other three seas keep a working shore throughout — no regression to vanilla ocean.
- [ ] Category/genOrder/priority behaviour preserved; no mutator conflict logged.

## related
- `GREYSEA_FLOOR_PASS_1` — the floor half.
- The owner's wider Grey Sea content drop of the same day, captured in
  `design/Jawa/worldbuilding/biomes/the_grey_deep_content_2026-09-26.md`, which includes salt
  domes, chimneys and harvestable crystals that may also want shore expression.
