# Big-pit key

Origin (SW corner of the site) 40,89; site rect (40, 89, 77, 43). One pit is 16x16 cells dug 8 notches (4.0 m); one notch = 0.5 m.
Local coordinates (i east, j north) run 0..15 from a pit's SW corner; things keep 1 clear cell(s) from each wall, so they use i, j in 1..14.

## Copies

| copy | SW corner (x,z) | fill | liquid | camera centre |
|---|---|---|---|---|
| BP0_dry | 42,111 | 0 notch(es) = 0.0 m | dry | 50.0,119.0 |
| BP1_0.5m | 61,111 | 1 notch(es) = 0.5 m | water | 69.0,119.0 |
| BP2_1m | 80,111 | 2 notch(es) = 1.0 m | water | 88.0,119.0 |
| BP3_2m | 99,111 | 4 notch(es) = 2.0 m | water | 107.0,119.0 |
| BP4_3m | 42,91 | 6 notch(es) = 3.0 m | water | 50.0,99.0 |
| BP5_brim | 61,91 | 8 notch(es) = 4.0 m | water | 69.0,99.0 |
| BP6_tar1.5m | 80,91 | 3 notch(es) = 1.5 m | RM_Fluid_Tar | 88.0,99.0 |

Spare dry pit (for `owner_look_regressions.py --acts`: brimmed, overflowed, drained; nothing in it): SW corner 104,96, 6x6 cells dug 8 notches.

Series label header at 42,130 (tag `bigpit`). The deepest copy is the brim one (BP5_brim).

## Contents (identical in every copy)

| kind | def | source | local cell | stack | stuff |
|---|---|---|---|---|---|
| furn | SculptureGrand | Core | 2,2 |  | Steel |
| furn | DoubleBed | Core | 5,2 |  | Steel |
| furn | RM_GlowTank | RimMandrake LuminousPigment | 8,2 |  |  |
| furn | RM_HoseReel | RimMandrake FlowWorks | 11,2 |  |  |
| furn | Table2x2c | Core | 2,5 |  | Steel |
| furn | TableButcher | Core | 5,4 |  | Steel |
| furn | HandTailoringBench | Core | 8,4 |  | Steel |
| furn | SculptureLarge | Core | 14,4 |  | Steel |
| furn | Bed | Core | 13,2 |  | Steel |
| furn | Shelf | Core | 11,4 |  | Steel |
| furn | Dresser | Core | 5,5 |  | Steel |
| furn | RM_ResinSealingJarShelf | RimMandrake ColdStorage | 8,5 |  |  |
| furn | Bedroll | Core | 14,2 |  | Cloth |
| furn | Battery | Core | 13,5 |  |  |
| furn | PlantPot | Core | 10,5 |  | Steel |
| furn | SculptureSmall | Core | 11,5 |  | Steel |
| furn | DiningChair | Core | 12,5 |  | Steel |
| furn | Stool | Core | 14,5 |  | Steel |
| furn | Armchair | Core | 4,6 |  | Cloth |
| furn | EndTable | Core | 5,6 |  | Steel |
| furn | StandingLamp | Core | 6,6 |  |  |
| furn | TorchLamp | Core | 7,6 |  |  |
| furn | Cooler | Core | 8,6 |  |  |
| furn | RM_BrineCrock | RimMandrake ColdStorage | 9,6 |  |  |
| furn | RM_EvaporativeCrock | RimMandrake ColdStorage | 10,6 |  | BlocksGranite |
| furn | RM_AncientStasisLocker_Refurbished | RimMandrake ColdStorage | 11,6 |  |  |
| item | WoodLog | Core | 12,6 | 75 |  |
| item | Plasteel | Core | 14,6 | 10 |  |
| item | Gold | Core | 1,7 | 50 |  |
| item | ComponentIndustrial | Core | 2,7 | 3 |  |
| item | Cloth | Core | 3,7 | 60 |  |
| item | Hay | Core | 4,7 | 40 |  |
| item | Silver | Core | 5,7 | 500 |  |
| item | Steel | Core | 6,7 | 1 |  |
| item | Leather_Plain | Core | 7,7 | 30 |  |
| item | MealSimple | Core | 8,7 | 1 |  |
| item | MealFine | Core | 9,7 | 5 |  |
| item | RawPotatoes | Core | 10,7 | 40 |  |
| item | Meat_Cow | Core | 11,7 | 60 |  |
| item | Pemmican | Core | 12,7 | 75 |  |
| item | Beer | Core | 13,7 | 10 |  |
| item | Chocolate | Core | 14,7 | 20 |  |
| item | MedicineIndustrial | Core | 1,8 | 5 |  |
| item | MedicineHerbal | Core | 2,8 | 1 |  |
| item | Neutroamine | Core | 3,8 | 25 |  |
| item | MeleeWeapon_Knife | Core | 4,8 | 1 | Steel |
| item | Gun_BoltActionRifle | Core | 5,8 | 1 |  |
| item | Gun_Revolver | Core | 6,8 | 1 |  |
| item | MeleeWeapon_LongSword | Core | 7,8 | 1 | Steel |
| item | Apparel_Parka | Core | 8,8 | 1 | Cloth |
| item | Apparel_CowboyHat | Core | 9,8 | 1 | Cloth |
| item | Apparel_FlakVest | Core | 10,8 | 1 |  |
| item | ChunkGranite | Core | 11,8 | 1 |  |
| item | ChunkSlagSteel | Core | 12,8 | 1 |  |
| item | Shell_HighExplosive | Core | 13,8 | 5 |  |
| item | Shell_EMP | Core | 14,8 | 1 |  |
| item | Jade | Core | 1,9 | 10 |  |
| item | Novel | Core | 2,9 | 1 |  |
| item | RM_ResinSealedMeat | RimMandrake ColdStorage | 3,9 | 10 |  |
| item | RM_ResinSealedFruit | RimMandrake ColdStorage | 4,9 | 10 |  |
| item | RM_AmberAgedMeat | RimMandrake ColdStorage | 5,9 | 4 |  |
| mini | Armchair | Core | 6,9 |  | Cloth |
| mini | EndTable | Core | 7,9 |  | Steel |
| mini | RM_BrineCrock | RimMandrake ColdStorage | 8,9 |  |  |
| corpse | Muffalo | Core (animal corpse) | 9,9 |  |  |
| corpse | Villager | Core (human corpse) | 10,9 |  |  |

World cell of a local cell: copy SW corner + local. Corpses are a Muffalo (factionless) and a Villager, stripped of inventory and apparel before the kill. Minified: the three `mini` rows (spawned, then minified).

## Changing a level by hand (dev mode)

Route today: the engine driver write `RM_SubmergeDraw.ProofFillRect` (`jawa/static_call`, args `x,z,w,h,waterM[,fluid]`), the route `fill` uses. The god-mode pour/drain tools of RIMMANDRAKE_GIVE_GODMODE_LIQUID_POUR_DRAIN had not landed when this was written; use them once they exist. The dev menu's `Fill excavated cell with fluid...` / `Place level holder (50%)` (RM_MapControls.cs near line 709) are the in-game equivalents; neither was exercised here.
