
## spec

Owner answered 'Queue all' on a question card 2026-10-08 (decision taken by question card) for the remaining work of `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`. Row CB-3 there is the spec:

| CB-3 | Breeding vermin eat what they breed on. Each litter uses up part of the food pile, and food behind a locked door does not count. Clearing food then starves an infestation in a way the player can see. | Consume N units per litter, plus a reachability check in FoodExistsNearby. | S–M | low (tune litter cost) | CreatureBehaviors, ShipVermin (consumers) | `RM_CompVerminBreeder.cs:127-150` counts a stack in range as food, never consumes it and never checks a path; the hard cap in `RM_MapComponent_VerminPopulation` does exist |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.
