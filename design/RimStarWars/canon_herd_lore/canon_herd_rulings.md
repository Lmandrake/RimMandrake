# Canon herd and pack rulings

Delegated design calls under item `CANON_HERD_LORE_ARBITRATION_1`, 2026-11-01. They settle the 45 creatures the
lore pass (`canon_herd_lore_2026-10-08.md`, CSV beside it) left UNCLEAR. Every row is in
`canon_herd_lore_decisions.csv`; judge record `infrastructure/state/delegated/2026-11-01/CANON_HERD_LORE_ARBITRATION_1.json`.
Owner by card 2026-10-08: each creature is settled at its biome's group-size walk (`BIOME_GROUP_SIZE_WALK_1`), so the
tables below are per biome and carry no numbers: the walk set those, and nothing here changes a def.

**Result on the 45:** 8 herd, 6 solitary, 31 leave default, 0 pack. Canon is simply silent on most of them; leave default
is that honest answer, not a gap.

**How it was judged.** Three blind rounds decided the 45 from the 2026-11-01 Wookieepedia pages, without seeing the maker's
draft, which was written first (`judge/maker_draft.json`). They agreed on 37 and the judge's value stands on the other 8.
Dianoga and Gorg went once to a fresh judge on a written rebuttal: Dianoga moved to leave default, Gorg stayed herd.

## What the four values mean in game

| value | def | meaning |
|---|---|---|
| herd | `race/herdAnimal` true, `wildGroupSize` above 1 | vanilla `JobGiver_WanderHerd` keeps them together; earns gender art (owner: "every herd animal") |
| pack | `predator` true, `wildGroupSize` above 1 | a predator that attacks in a group |
| solitary | `wildGroupSize` 1, `herdAnimal` unset | |
| leave default | unchanged | canon gives no basis; the walk may still set a number |

🔴 **`race/packAnimal` is not "pack".** It means a caravan load-carrier. Dalgo, Orray and Dactillion carry it today and that
says nothing about hunting.

## GROUP maps to herd unless the predators attack together

Rule, as the judge restated it: established wild schools, hives, flocks, colonies, groups and pairs map to **herd**;
predators explicitly attacking together map to **pack**. Territoriality, predation and defensive cooperation alone do not
make a pack. Conditional benefits of grouping do not establish wild grouping, and those stay leave default.

Applied to the 14 GROUP subjects: 13 herd, including the hives (Lylek, Kinrath, Krykna), Wraid and Qormot, because canon
shows them grouped but never attacking together. Ysalamiri is leave default: canon describes what a group would do, not
that they live in one.

## Invented morphs take the parent's verdict

Yes, for all eight, on social status only; the walk may set a morph's number separately. `RSW_ElderSando`, `RSW_StormSando`:
leave default. `RSW_CrimsonOpee`, `RSW_AbyssalColo`, `RSW_ThornbackColo`: solitary. `RSW_WraidAlpha`, `RSW_LongtailGorg`,
`RSW_FrilledGorg`: herd. The two gorgs are a design convention, since neither has canon evidence of its own.

## Corrections to the lore report

- **Whisper bird** is herd on canon evidence the pass missed: "silently traveling in flocks" (*Whisper bird*).
- **Loth-cat** is solitary: the canon page says "led solitary lives, coming together only to mate and raise kits".
- **Krayt dragon** is leave default, and no live race def carries that name: `RSW_GreaterKraytDragon` is the live krayt.
- `RSW_GreatDevourer` was retired and `RSW_YobshrimpLand` consolidated after the pass; their rows bind nothing.

## By biome, for the group-size walk

Creatures on an `RM_` roster, read from the BiomeDefs and the `WildAnimals_*` patches on 2026-11-01. The group-size walk
set every number on 2026-11-03: `design/RimMandrake/biome_group_sizes/biome_group_sizes.csv` (checked by
`src/RimMandrake/Utils/selftest_biome_group_sizes.py`). Only `RSW_YobshrimpJuv` is still on RM_Miasma; the adult left it.

### RM_Cauldron

| creature | decision |
|---|---|
| Granite slug | leave default |
| Skalder | leave default |

### RM_FeverWood

| creature | decision |
|---|---|
| Gelagrub | leave default |
| Gorg | herd |
| Nuna | herd |
| Urusai | leave default |
| Whisper bird | herd |

### RM_FloodedCanyon

| creature | decision |
|---|---|
| Can-cell | leave default |

### RM_Greentide

| creature | decision |
|---|---|
| Gizka | leave default |
| Dalgo | leave default |
| Gelagrub | leave default |
| Worrt | solitary |
| Nuna | herd |
| Dragonsnake | solitary |
| K'lor'slug | leave default |
| Shiro | leave default |
| Whisper bird | herd |

### RM_LeaningScrub

| creature | decision |
|---|---|
| Gizka | leave default |
| Igitz | leave default |
| Puffer pig | herd |
| Worrt | solitary |
| Saw-toothed grank | leave default |
| Gorg | herd |
| Nuna | herd |
| Loth-cat | solitary |
| Urusai | leave default |
| Whisper bird | herd |
| Skalder | leave default |

### RM_LongShade

| creature | decision |
|---|---|
| Bolotaur | leave default |
| Worrt | solitary |
| Jamel | leave default |
| Runyip | leave default |
| Tee-muss | herd |
| Gorg | herd |
| Nuna | herd |
| Jimvu | leave default |
| Skalder | leave default |

### RM_Miasma

| creature | decision |
|---|---|
| Saw-toothed grank | leave default |
| Runyip | leave default |
| Blarth | leave default |
| Yobshrimp | herd |
| Opee sea killer | solitary |
| Laa | herd |
| Shiro | leave default |
| Whisper bird | herd |
| Blixus | leave default |

### RM_Pyrelands

| creature | decision |
|---|---|
| Gizka | leave default |
| Dalgo | leave default |
| Orray | leave default |
| Nuna | herd |

### RM_Stillsand

| creature | decision |
|---|---|
| Gizka | leave default |
| Greater krayt dragon | leave default |
| Granite slug | leave default |

### RM_TheForge

| creature | decision |
|---|---|
| Lava flea | leave default |

### RM_TheRot

| creature | decision |
|---|---|
| Shiro | leave default |

### RM_TwilightSea

| creature | decision |
|---|---|
| Sando aqua monster | leave default |

### RM_Wastes

| creature | decision |
|---|---|
| Borcatu | leave default |

### RM_WeepingStones

| creature | decision |
|---|---|
| Jamel | leave default |
| Dactillion | leave default |
| Boma | leave default |
| Fanback | leave default |
| Ollopom | leave default |

On no `RM_` roster today: Blurrg, Acklay, Krayt dragon, Sarlacc, Colo claw fish, Dianoga, Great Devourer, Brain worm.
