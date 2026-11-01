# Canon herd and pack rulings

Delegated design calls under item `CANON_HERD_LORE_ARBITRATION_1`, 2026-11-01. They settle the 45 creatures the
lore pass (`canon_herd_lore_2026-10-08.md`, CSV beside it) left UNCLEAR. Every row is in
`canon_herd_lore_decisions.csv`; judge record `infrastructure/state/delegated/2026-11-01/CANON_HERD_LORE_ARBITRATION_1.json`.
Owner by card 2026-10-08: each creature is settled at its biome's group-size walk (`BIOME_GROUP_SIZE_WALK_1`), so the
tables below are per biome and carry no numbers: the walk sets those, and nothing here changes a def.

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

Creatures on an `RM_` roster, read from the BiomeDefs and the `WildAnimals_*` patches on 2026-11-01. Today's values are for
the walk to compare; they are not a verdict.

### RM_Cauldron

| creature | decision | today herdAnimal | today wildGroupSize |
|---|---|---|---|
| Granite slug | leave default | RSW_GraniteSlug=unset | RSW_GraniteSlug=2~4 |
| Skalder | leave default | RSW_Skalder=true | RSW_Skalder=3~7 |

### RM_FeverWood

| creature | decision | today herdAnimal | today wildGroupSize |
|---|---|---|---|
| Gelagrub | leave default | RSW_Gelagrub=true | RSW_Gelagrub=3~9 |
| Gorg | herd | RSW_Gorg=unset; RSW_LongtailGorg=unset; RSW_FrilledGorg=unset | RSW_Gorg=2~5; RSW_LongtailGorg=2~4; RSW_FrilledGorg=2~4 |
| Nuna | herd | RSW_Nuna=true | RSW_Nuna=2~6 |
| Urusai | leave default | RSW_Urusai=true | RSW_Urusai=1~3 |
| Whisper bird | herd | RSW_Whisperbird=true | RSW_Whisperbird=2~6 |

### RM_FloodedCanyon

| creature | decision | today herdAnimal | today wildGroupSize |
|---|---|---|---|
| Can-cell | leave default | RSW_CanCell=true | RSW_CanCell=1~3 |

### RM_Greentide

| creature | decision | today herdAnimal | today wildGroupSize |
|---|---|---|---|
| Gizka | leave default | RSW_Gizka=true | RSW_Gizka=4~6 |
| Dalgo | leave default | RSW_Dalgo=true | RSW_Dalgo=3~6 |
| Gelagrub | leave default | RSW_Gelagrub=true | RSW_Gelagrub=3~9 |
| Worrt | solitary | RSW_Worrt=unset | RSW_Worrt=unset |
| Nuna | herd | RSW_Nuna=true | RSW_Nuna=2~6 |
| Dragonsnake | solitary | RSW_Dragonsnake=unset | RSW_Dragonsnake=unset |
| K'lor'slug | leave default | RSW_Klorslug=true | RSW_Klorslug=3~6 |
| Shiro | leave default | RSW_Shiro=unset; RSW_ShiroTrap=unset | RSW_Shiro=unset; RSW_ShiroTrap=unset |
| Whisper bird | herd | RSW_Whisperbird=true | RSW_Whisperbird=2~6 |

### RM_LeaningScrub

| creature | decision | today herdAnimal | today wildGroupSize |
|---|---|---|---|
| Gizka | leave default | RSW_Gizka=true | RSW_Gizka=4~6 |
| Igitz | leave default | RSW_Igitz=unset | RSW_Igitz=unset |
| Puffer pig | herd | RSW_Pufferpig=unset | RSW_Pufferpig=2~4 |
| Worrt | solitary | RSW_Worrt=unset | RSW_Worrt=unset |
| Saw-toothed grank | leave default | RSW_Grank=unset | RSW_Grank=unset |
| Gorg | herd | RSW_Gorg=unset; RSW_LongtailGorg=unset; RSW_FrilledGorg=unset | RSW_Gorg=2~5; RSW_LongtailGorg=2~4; RSW_FrilledGorg=2~4 |
| Nuna | herd | RSW_Nuna=true | RSW_Nuna=2~6 |
| Loth-cat | solitary | RSW_Lothcat=unset | RSW_Lothcat=unset |
| Urusai | leave default | RSW_Urusai=true | RSW_Urusai=1~3 |
| Whisper bird | herd | RSW_Whisperbird=true | RSW_Whisperbird=2~6 |
| Skalder | leave default | RSW_Skalder=true | RSW_Skalder=3~7 |

### RM_LongShade

| creature | decision | today herdAnimal | today wildGroupSize |
|---|---|---|---|
| Bolotaur | leave default | RSW_Bolotaur=true | RSW_Bolotaur=2~4 |
| Worrt | solitary | RSW_Worrt=unset | RSW_Worrt=unset |
| Jamel | leave default | RSW_Jamel=true | RSW_Jamel=2~6 |
| Runyip | leave default | RSW_Runyip=true | RSW_Runyip=2~6 |
| Tee-muss | herd | RSW_TeeMuss=true | RSW_TeeMuss=2~6 |
| Gorg | herd | RSW_Gorg=unset; RSW_LongtailGorg=unset; RSW_FrilledGorg=unset | RSW_Gorg=2~5; RSW_LongtailGorg=2~4; RSW_FrilledGorg=2~4 |
| Nuna | herd | RSW_Nuna=true | RSW_Nuna=2~6 |
| Jimvu | leave default | RSW_Jimvu=true | RSW_Jimvu=4~8 |
| Skalder | leave default | RSW_Skalder=true | RSW_Skalder=3~7 |

### RM_Miasma

| creature | decision | today herdAnimal | today wildGroupSize |
|---|---|---|---|
| Saw-toothed grank | leave default | RSW_Grank=unset | RSW_Grank=unset |
| Runyip | leave default | RSW_Runyip=true | RSW_Runyip=2~6 |
| Blarth | leave default | RSW_Blarth=unset | RSW_Blarth=unset |
| Yobshrimp | herd | RSW_Yobshrimp=true; RSW_YobshrimpJuv=unset | RSW_Yobshrimp=6~12; RSW_YobshrimpJuv=unset |
| Opee sea killer | solitary | RSW_OpeeSeaKiller=unset; RSW_OpeeSeaKillerJuv=unset; RSW_CrimsonOpee=unset | RSW_OpeeSeaKiller=1; RSW_OpeeSeaKillerJuv=unset; RSW_CrimsonOpee=1 |
| Laa | herd | RSW_Laa=true; RSW_LaaJuv=unset | RSW_Laa=3~6; RSW_LaaJuv=unset |
| Shiro | leave default | RSW_Shiro=unset; RSW_ShiroTrap=unset | RSW_Shiro=unset; RSW_ShiroTrap=unset |
| Whisper bird | herd | RSW_Whisperbird=true | RSW_Whisperbird=2~6 |
| Blixus | leave default | RSW_Blixus=unset | RSW_Blixus=unset |

### RM_Pyrelands

| creature | decision | today herdAnimal | today wildGroupSize |
|---|---|---|---|
| Gizka | leave default | RSW_Gizka=true | RSW_Gizka=4~6 |
| Dalgo | leave default | RSW_Dalgo=true | RSW_Dalgo=3~6 |
| Orray | leave default | RSW_Orray=unset | RSW_Orray=unset |
| Nuna | herd | RSW_Nuna=true | RSW_Nuna=2~6 |

### RM_Stillsand

| creature | decision | today herdAnimal | today wildGroupSize |
|---|---|---|---|
| Gizka | leave default | RSW_Gizka=true | RSW_Gizka=4~6 |
| Greater krayt dragon | leave default | RSW_GreaterKraytDragon=unset | RSW_GreaterKraytDragon=1 |
| Granite slug | leave default | RSW_GraniteSlug=unset | RSW_GraniteSlug=2~4 |

### RM_TheForge

| creature | decision | today herdAnimal | today wildGroupSize |
|---|---|---|---|
| Lava flea | leave default | RSW_LavaFlea=true | RSW_LavaFlea=2~6 |

### RM_TheRot

| creature | decision | today herdAnimal | today wildGroupSize |
|---|---|---|---|
| Shiro | leave default | RSW_Shiro=unset; RSW_ShiroTrap=unset | RSW_Shiro=unset; RSW_ShiroTrap=unset |

### RM_TwilightSea

| creature | decision | today herdAnimal | today wildGroupSize |
|---|---|---|---|
| Sando aqua monster | leave default | RSW_SandoAquaMonster=unset; RSW_ElderSando=unset; RSW_StormSando=unset | RSW_SandoAquaMonster=1; RSW_ElderSando=1; RSW_StormSando=1 |

### RM_Wastes

| creature | decision | today herdAnimal | today wildGroupSize |
|---|---|---|---|
| Borcatu | leave default | RSW_Borcatu=unset | RSW_Borcatu=1~3 |

### RM_WeepingStones

| creature | decision | today herdAnimal | today wildGroupSize |
|---|---|---|---|
| Jamel | leave default | RSW_Jamel=true | RSW_Jamel=2~6 |
| Dactillion | leave default | RSW_Dactillion=unset | RSW_Dactillion=unset |
| Boma | leave default | RSW_Boma=unset | RSW_Boma=1~3 |
| Fanback | leave default | RSW_Fanback=unset | RSW_Fanback=1~2 |
| Ollopom | leave default | RSW_Ollopom=true | RSW_Ollopom=1~3 |

On no `RM_` roster today: Blurrg, Acklay, Krayt dragon, Sarlacc, Colo claw fish, Dianoga, Great Devourer, Brain worm.
