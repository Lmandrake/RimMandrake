## why
Child of `VANILLA_BEAST_EXCISION_1` (owner, 2026-09-24: *"No vanilla beasts in Utinni scenario. We make our own."*).
Its wave 4 cut 21 official animals as Cherry Picker ThingDefs (`src/RimMandrake/Utils/vanilla_beast_cut.py`,
`WAVES[4]`). A ThingDef cut is a NEUTER, not a delete (`design/Jawa/worldbuilding/cherrypick_resolved.md` §0c): it
clears trade tags and roster entries, but a def that names the race or kind still spawns it.

## spec
1. `python3 src/RimMandrake/Utils/vanilla_beast_cut.py` prints `leaks:`, the uncut spawn-route defs that still name a cut
   race. On 2026-11-02 they were: TileMutatorDef `VEE_DomesticatedEscapees` (Chicken, Cow), `VEE_Megafauna`
   (Wolf_Great), ThingSetMakerDef `RareFishingCatches_Tropical` (Monkey), `RareFishingCatches_Temperate` (Squirrel).
2. Routes the def read cannot see, because they choose their kind in C#: VEE IncidentDefs `VEE_AnimalPodCrash`,
   `VEE_CaravanAnimalsWanderIn`, `VEE_BattleAnimalsWanderIn`, `VEE_ManhunterSingleArrival`, and Odyssey's
   `AnimalHabitat` tile mutator. Read each worker's selection rule (RimSage or the DLL) before deciding.
3. Close each one with a Cherry Picker cut of the route def, or a Utinni patch that strikes the name. Never edit the
   vanilla animal def.

## verify
`vanilla_beast_cut.py` reports `leaks: 0`, and each C#-route worker's rule is written down with the reason it can (or
cannot) still pick an official animal.
