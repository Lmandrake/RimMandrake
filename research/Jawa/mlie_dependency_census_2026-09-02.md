# Mlie StarWarsAnimalCollection dependency census — 2026-09-02

Read-only census for STARWARS_DONOR_SUNSET_1 wave planning. Method: extracted every ThingDef/PawnKindDef defName from Mlie's `Races_Animal_SW.xml`, then cross-referenced against the fauna cast CSVs, the deployed biome-spawn patch, and every XML patch under src/ that names one of these defNames.

## Source mod

`/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3497316713/` — packageId `Mlie.StarWarsAnimalCollection`, name "Star Wars Animal Collection (Continued)". (A second candidate, `3557220601` / `lee.theforce.standalone`, does NOT match the packageId and was excluded.)

## Total creature defNames — MEASURED

**160.** Counted from `1.6/Defs/ThingDefs_Races/Races_Animal_SW.xml`: 160 `<ThingDef>` blocks and 160 `<PawnKindDef>` blocks (verified by raw open/close tag counts, not a substring scan), each pair sharing the same bare-species defName (e.g. `Bantha`, `Rancor`, `Wampa` — no mod prefix).

## Dependency tiers

| Tier | Meaning | Count |
|---|---|---|
| A | Wild-spawns on Ashkarr today — live nonzero `<DefName>commonality</DefName>` entry in the deployed patch `src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml` (verified none are inside XML comments) | 133 |
| B | Not a wild spawn, but a real, separately-verified functional dependency (faction pawnGroupMaker carrier, or a downstream mod's biome patch) | 2 |
| C | Referenced only by blanket cross-mod normalization sweeps (`BeastNorm_Law3.xml`, `Doctrine/Patches/MegafaunaYield.xml`) and/or the cosmetic pet-naming rule pack (`Jawa_PetNames.xml`) — these `PatchOperationConditional`/`FindMod` patches silently no-op if the defName is absent, so nothing breaks if the mod is dropped | 24 |
| D | Zero reference anywhere (cast CSVs, deployed patch, src/, design docs) | 1 |

**DEPENDED-ON = Tier A + Tier B = 135 of 160.** These must be ported (or an equivalent creature substituted) to retire the mod without losing planet fauna.

## Full table

| defName | tier | where |
|---|---|---|
| Acklay | C - cosmetic/blanket-patch only | no functional dependency found |
| Aiwha | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:199 |
| Akk | C - cosmetic/blanket-patch only | no functional dependency found |
| Anooba | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:1070 |
| Bantha | B - functional, non-wild | src/SPLIT_Phase3/Jawa_Patches/Defs/FactionDefs/JawaHuttCartel.xml:231, JawaWildsteamClan.xml:180 (pawnGroupMaker carrier) |
| Behemoth | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:327 |
| Beldon | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:647 |
| Blarth | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:746 (+1 more) |
| Blixus | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:404 |
| Blurrg | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:761 |
| Boarwolf | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:602 |
| Bogwing | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:28 |
| Bolotaur | C - cosmetic/blanket-patch only | no functional dependency found |
| Boma | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:561 |
| Borcatu | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:188 (+1 more) |
| Bordok | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:951 |
| Brezak | C - cosmetic/blanket-patch only | no functional dependency found |
| Bursa | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:120 |
| CanCell | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:312 |
| Cannok | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:73 |
| ChrysalideRancor | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:887 |
| Clodhopper | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:585 (+1 more) |
| Convor | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:946 |
| CorellianHound | D - zero reference (dead) | none (design/Jawa/fauna/refill_cast.py:60 flags MEASURED_DEAD) |
| Corinathoth | C - cosmetic/blanket-patch only | no functional dependency found |
| Dactillion | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:564 |
| Dalgo | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:639 |
| Devourers | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:84 |
| Dewback | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:925 |
| Dianoga | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:644 |
| Dragonsnake | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:645 |
| Drexl | C - cosmetic/blanket-patch only | no functional dependency found |
| EnergySpider | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:565 |
| Eopie | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:313 |
| Falumpaset | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:79 |
| Fambaa | B - functional, non-wild | src/RimStarWars/SeasWaterline/Patches/Waterline_Lane1.xml:158-182 (wildBiomes Lake/Ocean patch) |
| Fanback | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:562 |
| FeralGrazer | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:160 |
| FeralNerf | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:114 |
| FrilledGorg | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:587 |
| FrogDog | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:952 |
| Gelagrub | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:800 |
| Gizka | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:580 (+1 more) |
| Gorg | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:507 |
| Gornt | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:317 |
| GraniteSlug | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:141 (+3 more) |
| Grank | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:597 (+1 more) |
| Grazer | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:123 |
| GreaterKraytDragon | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:522 |
| Gualaar | C - cosmetic/blanket-patch only | no functional dependency found |
| Gullipud | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:669 |
| Gundark | C - cosmetic/blanket-patch only | no functional dependency found |
| Gutkurr | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:640 |
| HarvesterBeetle | C - cosmetic/blanket-patch only | no functional dependency found |
| Hawkbat | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:641 |
| Horax | C - cosmetic/blanket-patch only | no functional dependency found |
| Hrumph | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:325 |
| Hssiss | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:642 |
| Igitz | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:347 |
| Insectomorph | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:603 |
| Iriaz | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:867 (+1 more) |
| IridonianReek | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:521 |
| IthorianReek | C - cosmetic/blanket-patch only | no functional dependency found |
| Jakobeast | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:245 (+1 more) |
| Jamel | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:643 |
| Jimvu | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:801 |
| JungleRancor | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:847 |
| Kaadu | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:878 |
| Katarn | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:926 |
| KellDragon | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:844 |
| Kinrath | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:558 (+1 more) |
| Klorslug | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:598 (+1 more) |
| KowakianMonkeyLizard | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:868 |
| KraytDragon | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:607 |
| Kreetle | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:1020 (+1 more) |
| Krykna | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:236 (+2 more) |
| KwazelMaw | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:80 |
| Kwi | C - cosmetic/blanket-patch only | no functional dependency found |
| Kybuck | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:476 (+1 more) |
| LavaFlea | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:723 |
| Leaftail | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:102 (+1 more) |
| LongtailGorg | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:508 (+1 more) |
| LothWolf | C - cosmetic/blanket-patch only | no functional dependency found |
| Lothcat | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:748 |
| Lylek | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:646 |
| Maalraas | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:162 |
| Manka | C - cosmetic/blanket-patch only | no functional dependency found |
| MarshHaunt | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:841 |
| Massiff | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:917 (+1 more) |
| MastiffPhalone | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:842 |
| Mastmot | C - cosmetic/blanket-patch only | no functional dependency found |
| Mawvorr | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:802 |
| Mott | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:909 |
| Mudhorn | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:845 |
| Mynock | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:149 (+2 more) |
| Narglatch | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:445 |
| Neebray | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:142 (+3 more) |
| Nerf | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:763 |
| Nexu | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:803 |
| Nuna | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:588 (+1 more) |
| Ollopom | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:550 |
| Orray | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:362 |
| PaintedSpat | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:358 |
| PekoPeko | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:527 |
| Pikobis | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:869 |
| Porg | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:982 |
| Pufferpig | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:348 |
| Qormot | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:995 |
| Rancor | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:567 |
| Raxshir | C - cosmetic/blanket-patch only | no functional dependency found |
| Reek | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:805 |
| Rikknit | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:949 |
| Roggwart | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:846 |
| Ronto | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:1044 |
| Runyip | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:1075 |
| Rycrit | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:716 |
| Scavrat | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:870 |
| Scurrier | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:60 (+1 more) |
| Shaak | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:481 |
| Shiro | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:627 (+1 more) |
| ShiroTrap | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:628 (+1 more) |
| Shyrack | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:829 (+1 more) |
| Silooth | C - cosmetic/blanket-patch only | no functional dependency found |
| Skalder | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:879 |
| Sketto | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:67 (+1 more) |
| Snoruuk | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:670 |
| Squall | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:910 |
| Stintaril | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:68 |
| Strill | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:117 |
| Tach | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:509 (+1 more) |
| Taozin | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:927 |
| Tauntaun | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:756 |
| TeeMuss | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:482 |
| TetnissCrab | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:988 |
| Thranta | C - cosmetic/blanket-patch only | no functional dependency found |
| Tibidee | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:1002 |
| Tooke | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:61 (+1 more) |
| Torton | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:367 |
| Tukata | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:880 |
| TuskCat | C - cosmetic/blanket-patch only | no functional dependency found |
| Urusai | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:350 (+1 more) |
| Uvak | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:881 |
| Vapaad | C - cosmetic/blanket-patch only | no functional dependency found |
| Varactyl | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:806 |
| Veermok | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:843 |
| Voorpak | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:750 (+1 more) |
| Vornskyr | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:1080 |
| Vulptex | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:990 |
| Wampa | C - cosmetic/blanket-patch only | no functional dependency found |
| WarWyrm | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:82 |
| Warbird | C - cosmetic/blanket-patch only | no functional dependency found |
| Whisperbird | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:629 (+1 more) |
| WompRat | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:1029 (+1 more) |
| Woolamander | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:710 |
| Worrt | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:510 (+1 more) |
| Wraid | C - cosmetic/blanket-patch only | no functional dependency found |
| Wyyyschokk | C - cosmetic/blanket-patch only | no functional dependency found |
| Yobshrimp | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:590 (+1 more) |
| Zakkeg | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:1082 |
| Zeer | A - wild spawns Ashkarr | src/SPLIT_Phase3/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml:606 |

## Notable findings

- **`CorellianHound` (Tier D) is already known-dead by the fauna tooling itself**: `design/Jawa/fauna/refill_cast.py:60` sets `MEASURED_DEAD = {'CorellianHound'}` with a comment explaining it reads commonality 0 in all 9 biomes it was candidate for, and it is absent from `cast_assignment.csv` entirely (0 rows) and from every src/ XML patch. Safe to drop.
- **`Bantha` and `Fambaa` (Tier B) would be MISSED by a biome-spawn-only check.** `Bantha` is a pack-animal `carrier` in two faction defs (`src/SPLIT_Phase3/Jawa_Patches/Defs/FactionDefs/JawaHuttCartel.xml:231`, `JawaWildsteamClan.xml:180`) and its label is patched onto a vehicle-beast harness (`src/SPLIT_Phase3/Jawa_Patches/Patches/VehicleBeastLabels.xml:89,93`). `Fambaa` is one of "the seven Star Wars aquatics" a *separate* downstream mod (`src/RimStarWars/SeasWaterline/`) patches `race/wildBiomes` onto (`Waterline_Lane1.xml:158-182`) to make it spawn in Lakes/Oceans — a dependency the fauna-cast CSVs never see because that patch runs after the cast pipeline.
- **`cast_assignment.csv` status=`ours` (115 rows) undercounts the real spawn table.** 18 defNames tagged `dormant` in that CSV (e.g. `Grazer`, `Tauntaun`, `JungleRancor`) still get written into `BiomeCast_Ashkarr.xml` with a live nonzero commonality — the deployed patch, not the design CSV, is the ground truth for "does this creature actually spawn."
- **One false-positive collision, correctly excluded:** `Horax` — the *only* non-BiomeCast hit outside the blanket-sweep files is a comment in `JawaTribes.xml:134` ("Pattern copied from Anomaly's Horax cult"), which names RimWorld Anomaly's Horax entity, not the Mlie animal. Not counted as a dependency.
- **`Nuna` is a defName collision with vanilla Core** (RimWorld's own bird). The census pipeline's `animal_census.csv` attributes the live `Nuna` defName to "Star Wars Animal Collection (Continued)" (mod field, not vanilla) — meaning in the currently-dumped mod list, Mlie's `Nuna` def is the one that resolved (load-order override), and it is genuinely Tier A (wild-spawns on Ashkarr, `BiomeCast_Ashkarr.xml`). A human should confirm this is the intended pick before porting, since porting the wrong `Nuna` (Mlie's vs vanilla's) changes its stats/art.
- No `design/Jawa/worldbuilding/the_one_map.md` hits for any Mlie defName (grep returned zero); the planet map doc names biomes/settlements, not individual creatures. `design/Jawa/mods/required_mods.md` (lines 477, 485, 499, 1311) is the adoption record and explicitly names Bantha, Sarlacc (a building, out of scope here), Rancor + Chrysalide/Jungle variants, Greater/regular Krayt Dragon, Dewback, Tauntaun, Wampa, Acklay, Reek, Nexu, Varactyl, Kaadu, Dianoga, Mynock, Womp Rat, Massiff, Gizka, Porg, Vulptex, Frogdog, Nerf as the reasons for adopting the mod — of these, `Wampa` and `Acklay` are Tier C (no functional dependency found beyond blanket sweeps / cosmetic naming), despite being cited as adoption rationale.
