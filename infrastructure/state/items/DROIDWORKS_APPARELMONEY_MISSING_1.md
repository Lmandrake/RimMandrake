## spec
Found 2026-09-08 while live-verifying `DROIDWORKS_MODULE_ABSORB_1` (B2). Three
Droidworks KotOR kinds spawned via `rimworld/execute_debug_action` `Spawn Pawn...`
came in with `apparel: []`, `equipment: []` — not missing modules specifically,
missing apparel entirely. `grep -n "apparelMoney"
src/RimStarWars/Droidworks/Source/gen_droidworks_defs.py` returns zero hits: the
generator that writes all 80 `PawnKindDef`s (`Defs/PawnKinds_*.xml`) has never
emitted an `<apparelMoney>` field on any of them. `apparelTags` are present and
correct (spot-checked against real absorbed apparel from B2), but vanilla
`PawnGenerator` will not spend anything on apparel for a kind with no/zero
`apparelMoney`, regardless of how many tagged items exist to match against.

This is upstream of, and blocks, every packet that expects a Droidworks kind to
visually carry gear: B2 (module apparel), B3 (heads — different slot, may be
unaffected, check), B9 (Primitive tier fabricated modules), and any faction
loadout work (C1) that expects a spawned droid to look armed/armored.

## verify
```
PROVE   spawn one kind per family (or a representative sample) via the bridge,
        read jawa/pawn_get's apparel list
EXPECT  a Battle/Heavy-family kind spawns wearing at least one tagged item once
        apparelMoney is set; a Labour/Protocol kind may deliberately stay bare
        if that is the intended design choice (check droid_verbs_decisions.json
        for any existing ruling on how "dressed" different families should be
        before inventing numbers)
LIES    checking only that apparelMoney now has a nonzero value in the XML —
        PawnGenerator's actual apparel-selection roll is probabilistic and
        budget-gated in ways a static read cannot confirm; a live spawn (ideally
        several, per this project's own "spawn many" discipline) is the only
        real proof
```

## criteria
Every concrete Droidworks `PawnKindDef` (or at minimum every Battle/Heavy/Power
family kind — the ones with combat-relevant apparelTags) carries an
`apparelMoney` FloatRange sized to its family/tier, verified by a live spawn
showing gear where the design intends it and bare skin where it doesn't.
