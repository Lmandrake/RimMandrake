
## spec

Owner answered 'Queue all' on a question card 2026-10-08 (decision taken by question card) for the remaining work of `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`. Row CB-3 there is the spec:

| CB-3 | Breeding vermin eat what they breed on. Each litter uses up part of the food pile, and food behind a locked door does not count. Clearing food then starves an infestation in a way the player can see. | Consume N units per litter, plus a reachability check in FoodExistsNearby. | S–M | low (tune litter cost) | CreatureBehaviors, ShipVermin (consumers) | `RM_CompVerminBreeder.cs:127-150` counts a stack in range as food, never consumes it and never checks a path; the hard cap in `RM_MapComponent_VerminPopulation` does exist |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

Record each owed criterion with `rimflow verify VERMIN_EAT_BREEDING_FOOD_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- A2 (L1): verminBreedingEatsFood wired and gated (mechanic_toggles.verminBreedingEatsFood_wired_and_gated)
- A3 (L2): a grub litter shrinks the fruit pile by the setting and a walled-off pile starves the breeder (tune verminLitt
Evidence is the Player.log line or bridge state read the criterion names.

### Exact checks 2026-10-09 (acceptance sitting)
- A2 CHECK: Same arms as the existing validation chain `CreatureBehaviors/validation.py` `mechanic_toggles` (step `verminBreedingEatsFood_wired_and_gated`): `jawa/type_probe typeName="RimMandrake.CreatureBehaviors.RM_CompVerminBreeder"`; `jawa/type_probe typeName="RimMandrake.CreatureBehaviors.RM_VerminFoodMath"`. Then `jawa/mod_settings_field typeName="RimMandrake.CreatureBehaviors.RM_CreatureBehaviorsSettings" action=get field="verminBreedingEatsFood"`, `action=set field="verminBreedingEatsFood" value="False"`, `action=get` again, then restore the old value. PASS: every type_probe resolved=true; get_defs success=true, foundCount=0, notFound empty; get returns true, after set False get returns false, restored value equals the first read. FAIL: any resolved=false (DLL not loaded or not in csproj), foundCount short or notFound non-empty, or the off arm reads true (toggle not wired). A failed get_defs call (success=false) is UNMEASURED, never absent.
