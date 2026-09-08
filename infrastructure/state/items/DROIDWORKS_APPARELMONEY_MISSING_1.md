## UPDATE 2026-09-08 (live-verify pass) — blocked on DROIDWORKS_APPAREL_ISFLESH_GATE_1
`gen_droidworks_defs.py` now emits a per-kind `<apparelMoney>` (0,0 for any
kind with no `apparelTags` at all — RimWorld's `PawnApparelGenerator.CanUsePair`
only tag-filters `if (!apparelTags.NullOrEmpty())`, so a nonzero budget on an
untagged kind draws from the WHOLE apparel pool and dresses a droid in random
human clothes, measured live on `RSW_DW_OuterRim_GNKDroid`; a nonzero
family-tier value otherwise, sized against the real `RSW_DW_Module_*` armor
`MarketValue` floor each family's own tags resolve to). Diffed clean against
the pre-change committed XML (80 added `<apparelMoney>` lines, zero removed,
zero other changes) and this part of the fix IS live-verified: `bare skin
where not intended` now holds (GNK stayed `apparel: []` across a batch after
the fix, was previously dressed in a vanilla `Apparel_Broadwrap`).

`gear where the design intends it` is NOT yet live — 15/15 spawns across
Battle/Heavy/Labour/Probe kinds with real `apparelTags` and a budget
comfortably above their own cheapest matching item still came back
`apparel: []`. Root cause (read from engine source, not guessed):
`PawnApparelGenerator.GenerateStartingApparelFor`'s first line returns
immediately when `!pawn.RaceProps.IsFlesh`, and every Droidworks race is
`isOrganic:false` by an earlier, deliberate ruling — confirmed live,
`isFlesh: False` on every spawned DW kind via `jawa/pawn_get`. `apparelMoney`
is never even read. Full writeup, the fix shape, and the reopened verify
plan: `DROIDWORKS_APPAREL_ISFLESH_GATE_1`.

This item stays open/blocked rather than closing: its own criteria requires
a live spawn showing GEAR where intended, which does not hold yet.

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
