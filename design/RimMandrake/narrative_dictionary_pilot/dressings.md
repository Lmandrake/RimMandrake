# Room dressings — batch 1

One room plan: salvage bay, 13x9 interior, ROOM_KIND=service, door centred on the south wall. Object budget equal within each claim set (A 11, B 19 placements). Control = random draw from the same salvage-bay pool (40 defNames), random-start, 70% wall-preferring (structure_procedural_spec R4/§3.4), seeds 1 and 2.

## A-dictionary

door `Door` · floor `Concrete`

```
##b############
#hhii........g#
#.......cccf..#
#.......ccc.e.#
#........d..e.#
#.............#
#..........a..#
#.............#
#.............#
#...jj........#
#######D#######
```

| defName | x,y | state |
|---|---|---|
| `RSW_DW_RepairBench` | 7,6 | in_situ |
| `Stool` | 8,5 | askew |
| `Bedroll` | 11,5 | in_situ |
| `RUT_GaslightLamp` | 10,7 | lit |
| `PlantPot` | 12,8 | plant alive |
| `Filth_Floordrawing` | 10,3 |  |
| `Shelf` | 0,8 | slag |
| `Shelf` | 2,8 | steel + components |
| `RM_Graffiti_TallyMarks` | 1,8 | on the wall |
| `KOTOR_MineableJunk` | 4,0 | intake heap |
| `KOTOR_MineableJunk` | 3,0 | intake heap |

## B-dictionary

door `AncientBlastDoor` · floor `MetalTile`

```
##########b####
#........hh..k#
#........a.a..#
#iii......a...#
#...fe........#
#.c...e.......#
#...c..e......#
#.....ddd.....#
#.....ddd...jj#
#...lgdddgg.jj#
#######D#######
```

| defName | x,y | state |
|---|---|---|
| `AncientDestroyedConsole` | 8,8 | smashed |
| `Filth_MachineBits` | 8,7 |  |
| `Filth_MachineBits` | 9,6 |  |
| `Filth_MachineBits` | 10,7 |  |
| `RM_Graffiti_Stencil_Crown` | 9,8 | on the wall |
| `AncientLockerBank` | 0,6 | forced open |
| `AncientSecurityCrate` | 11,0 | sealed |
| `Filth_ScatteredDocuments` | 1,4 |  |
| `Filth_ScatteredDocuments` | 3,3 |  |
| `AncientPlantPot` | 12,8 | dead |
| `AncientEmergencyLight_Red` | 3,0 | on |
| `Filth_BlastMark` | 5,0 |  |
| `Filth_BloodSmear` | 6,3 |  |
| `Filth_BloodSmear` | 5,4 |  |
| `Filth_BloodSmear` | 4,5 |  |
| `Filth_DriedBlood` | 3,5 |  |
| `Filth_Sand` | 8,0 |  |
| `Filth_Sand` | 9,0 |  |
| `Filth_Sand` | 4,0 |  |

## A-control

door `Door` · floor `Sand`

```
###############
#......f....i.#
#ee...........#
c.............#
#.............#
#.............#
#........a.jjj#
#dh...........#
#...........g.#
#.........a.g.#
#b#####D#######
```

| defName | x,y | state |
|---|---|---|
| `ToolCabinet` | 0,7 |  |
| `RSW_CrackedCeramicShards` | 6,8 |  |
| `Filth_BloodSmear` | 9,0 |  |
| `Bedroll` | 11,0 |  |
| `Filth_BloodSmear` | 8,3 |  |
| `RM_Graffiti_TallyMarks` | 0,0 |  |
| `AncientSafe` | 1,2 |  |
| `PlantPot` | 11,8 | empty |
| `AncientLockerBank` | 10,3 |  |
| `RM_Graffiti_Stencil_Crown` | 0,6 |  |
| `Filth_Ash` | 0,2 |  |

## B-control

door `Door` · floor `Concrete`

```
###############
#jjj.pjjj.i.cl#
#...........nn#
#m............#
#q.......a....#
#.........o...#
#e..........nn#
#.............#
#.............#
#k.........ghh#
#######D#######
```

| defName | x,y | state |
|---|---|---|
| `Shelf` | 11,0 | holding a jumble of mixed items |
| `AncientMetalCrate` | 9,8 |  |
| `Filth_Dirt` | 8,5 |  |
| `AncientLockerBank` | 0,8 |  |
| `Filth_Floordrawing` | 6,8 |  |
| `AncientSafe` | 0,0 |  |
| `Steel` | 12,8 |  |
| `Filth_BloodSmear` | 11,8 |  |
| `AncientEmergencyLight_Red` | 0,6 | unlit |
| `AncientDestroyedConsole` | 11,7 |  |
| `Filth_MachineBits` | 0,3 |  |
| `ChunkSlagSteel` | 9,4 |  |
| `RM_Filth_Tar` | 0,3 |  |
| `AncientLockerBank` | 5,8 |  |
| `Stool` | 4,8 | pulled out at an angle |
| `AncientDestroyedConsole` | 11,3 |  |
| `Filth_DriedBlood` | 12,0 |  |
| `Filth_ScatteredDocuments` | 10,0 |  |
| `PlantPot` | 0,5 | empty |
