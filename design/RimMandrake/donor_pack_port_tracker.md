# Donor pack port tracker: mlie.starwarsanimalcollection (160 species)

Item `DONOR_DEFS_PORT_TO_OURS_1`; plan `design/RimMandrake/donor_pack_port_plan_2026-10-14.md`. Script: `src/RimMandrake/Utils/donor_pack_port.py` (`diff` = W0, `rosters`, `repoint` = W1). One row per donor race. `class` is the 2026-10-14 census class; `W0` is the twin-vs-donor diff (MATCH / DIFF with the differences / NO_TWIN); `rows` is donor-named roster rows still left; `status` is this pass's outcome; `sha` the commit that did it.

Statuses: DONE_ALREADY_OWNED (twin existed; only roster rows repointed, art and defs untouched) · PORTED (new RSW_ def this pass) · ART_BLOCKED · OWNER_QUESTION · DECLINED · OWED (not reached).

| species | class | twin | W0 | canon entry | rows left | status | sha | note |
|---|---|---|---|---|---:|---|---|---|
| Acklay | TWIN_NOT_WIRED | RSW_Acklay | MATCH | acklay | 0 | OWED |  |  |
| Aiwha | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Akk | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Anooba | TWIN_NOT_WIRED | RSW_Anooba | MATCH | anooba | 2 | OWED |  |  |
| Bantha | WIRED_DONOR_ROW | RSW_Bantha | MATCH | bantha | 2 | OWED |  |  |
| Behemoth | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Beldon | TWIN_NOT_WIRED | RSW_Beldon | MATCH | beldon | 2 | OWED |  |  |
| Blarth | TWIN_NOT_WIRED | RSW_Blarth | MATCH | blarth | 0 | OWED |  |  |
| Blixus | TWIN_NOT_WIRED | RSW_Blixus | MATCH | blixus | 0 | OWED |  |  |
| Blurrg | TWIN_NOT_WIRED | RSW_Blurrg | DIFF: stat CaravanRidingSpeedFactor: donor None ours 1.5; stat MeatAmount: donor None ours 350 | blurrg | 0 | OWED |  |  |
| Boarwolf | NOT_PORTED/PLAIN |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Bogwing | TWIN_NOT_WIRED | RSW_Bogwing | MATCH | bogwing | 0 | OWED |  |  |
| Bolotaur | PORTED_WIRED | RSW_Bolotaur | MATCH | bolotaur | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Boma | TWIN_NOT_WIRED | RSW_Boma | MATCH | boma | 1 | OWED |  |  |
| Borcatu | TWIN_NOT_WIRED | RSW_Borcatu | MATCH | borcatu | 1 | OWED |  |  |
| Bordok | NOT_PORTED/PLAIN |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Brezak | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Bursa | NOT_PORTED/PLAIN |  | NO_TWIN | NONE | 0 | OWED |  |  |
| CanCell | TWIN_NOT_WIRED | RSW_CanCell | MATCH | cancell | 1 | OWED |  |  |
| Cannok | TWIN_NOT_WIRED | RSW_Cannok | MATCH | cannok | 1 | OWED |  |  |
| ChrysalideRancor | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Clodhopper | WIRED_DONOR_ROW | RSW_Clodhopper | MATCH | clodhopper | 1 | OWED |  |  |
| Convor | TWIN_NOT_WIRED | RSW_Convor | MATCH | convor | 4 | OWED |  |  |
| CorellianHound | NOT_PORTED/PLAIN |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Corinathoth | TWIN_NOT_WIRED | RSW_Corinathoth | MATCH | corinathoth | 1 | OWED |  |  |
| Dactillion | TWIN_NOT_WIRED | RSW_Dactillion | MATCH | dactillion | 1 | OWED |  |  |
| Dalgo | TWIN_NOT_WIRED | RSW_Dalgo | MATCH | dalgo | 1 | OWED |  |  |
| Devourers | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Dewback | TWIN_NOT_WIRED | RSW_Dewback | MATCH | dewback | 1 | OWED |  |  |
| Dianoga | TWIN_NOT_WIRED | RSW_Dianoga | MATCH | dianoga | 0 | OWED |  |  |
| Dragonsnake | TWIN_NOT_WIRED | RSW_Dragonsnake | MATCH | dragonsnake | 1 | OWED |  |  |
| Drexl | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| EnergySpider | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Eopie | WIRED_DONOR_ROW | RSW_Eopie | MATCH | eopie | 3 | OWED |  |  |
| Falumpaset | WIRED_DONOR_ROW | RSW_Falumpaset | MATCH | falumpaset | 1 | OWED |  |  |
| Fambaa | TWIN_NOT_WIRED | RSW_Fambaa | MATCH | fambaa | 2 | OWED |  |  |
| Fanback | TWIN_NOT_WIRED | RSW_Fanback | MATCH | fanback | 1 | OWED |  |  |
| FeralGrazer | PORTED_WIRED | RSW_FeralGrazer | MATCH | grazer | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| FeralNerf | TWIN_NOT_WIRED | RSW_FeralNerf | MATCH | NONE | 1 | OWED |  |  |
| FrilledGorg | WIRED_DONOR_ROW | RSW_FrilledGorg | MATCH | NONE | 1 | OWED |  |  |
| FrogDog | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Gelagrub | TWIN_NOT_WIRED | RSW_Gelagrub | MATCH | gelagrub | 2 | OWED |  |  |
| Gizka | PORTED_WIRED | RSW_Gizka | MATCH | gizka | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Gorg | WIRED_DONOR_ROW | RSW_Gorg | DIFF: baseBodySize: donor 0.3 ours 0.21 | gorg | 1 | OWED |  |  |
| Gornt | TWIN_NOT_WIRED | RSW_Gornt | MATCH | gornt | 1 | OWED |  |  |
| GraniteSlug | WIRED_DONOR_ROW | RSW_GraniteSlug | MATCH | graniteslug | 1 | OWED |  |  |
| Grank | TWIN_NOT_WIRED | RSW_Grank | MATCH | grank | 2 | OWED |  |  |
| Grazer | NOT_PORTED/PLAIN_DEPS |  | NO_TWIN | grazer | 0 | OWED |  |  |
| GreaterKraytDragon | PORTED_WIRED | RSW_GreaterKraytDragon | MATCH | greaterkraytdragon | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Gualaar | NOT_PORTED/PLAIN |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Gullipud | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Gundark | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Gutkurr | PORTED_WIRED | RSW_Gutkurr | MATCH | gutkurr | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| HarvesterBeetle | NOT_PORTED/PLAIN_DEPS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Hawkbat | TWIN_NOT_WIRED | RSW_Hawkbat | MATCH | hawkbat | 1 | OWED |  |  |
| Horax | PORTED_WIRED | RSW_Horax | MATCH | horax | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Hrumph | PORTED_WIRED | RSW_Hrumph | MATCH | hrumph | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Hssiss | TWIN_NOT_WIRED | RSW_Hssiss | MATCH | hssiss | 1 | OWED |  |  |
| Igitz | TWIN_NOT_WIRED | RSW_Igitz | MATCH | igitz | 1 | OWED |  |  |
| Insectomorph | NOT_PORTED/SHARED_BODY |  | NO_TWIN | insectomorph | 0 | OWED |  |  |
| Iriaz | WIRED_DONOR_ROW | RSW_Iriaz | MATCH | iriaz | 1 | OWED |  |  |
| IridonianReek | PORTED_WIRED | RSW_IridonianReek | MATCH | iridonianreek | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| IthorianReek | NOT_PORTED/PLAIN_DEPS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Jakobeast | PORTED_WIRED | RSW_Jakobeast | MATCH | jakobeast | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Jamel | WIRED_DONOR_ROW | RSW_Jamel | MATCH | jamel | 1 | OWED |  |  |
| Jimvu | PORTED_WIRED | RSW_Jimvu | DIFF: lifeExpectancy: donor 22 ours 30 | jimvu | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| JungleRancor | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Kaadu | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Katarn | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| KellDragon | NOT_PORTED/PLAIN_DEPS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Kinrath | TWIN_NOT_WIRED | RSW_Kinrath | MATCH | kinrath | 1 | OWED |  |  |
| Klorslug | TWIN_NOT_WIRED | RSW_Klorslug | MATCH | klorslug | 1 | OWED |  |  |
| KowakianMonkeyLizard | TWIN_NOT_WIRED | RSW_KowakianMonkeyLizard | MATCH | kowakianmonkeylizard | 1 | OWED |  |  |
| KraytDragon | PORTED_WIRED | RSW_KraytDragon | MATCH | kraytdragon | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Kreetle | PORTED_WIRED | RSW_Kreetle | MATCH | kreetle | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Krykna | PORTED_WIRED | RSW_Krykna | MATCH | krykna | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| KwazelMaw | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Kwi | PORTED_WIRED | RSW_Kwi | MATCH | kwi | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Kybuck | TWIN_NOT_WIRED | RSW_Kybuck | MATCH | kybuck | 1 | OWED |  |  |
| LavaFlea | TWIN_NOT_WIRED | RSW_LavaFlea | MATCH | lavaflea | 1 | OWED |  |  |
| Leaftail | NOT_PORTED/PLAIN |  | NO_TWIN | NONE | 0 | OWED |  |  |
| LongtailGorg | WIRED_DONOR_ROW | RSW_LongtailGorg | DIFF: baseBodySize: donor 0.6 ours 0.42 | longtailgorg | 2 | OWED |  |  |
| LothWolf | NOT_PORTED/PLAIN_DEPS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Lothcat | TWIN_NOT_WIRED | RSW_Lothcat | MATCH | lothcat | 1 | OWED |  |  |
| Lylek | TWIN_NOT_WIRED | RSW_Lylek | MATCH | lylek | 1 | OWED |  |  |
| Maalraas | NOT_PORTED/PLAIN_DEPS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Manka | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| MarshHaunt | TWIN_NOT_WIRED | RSW_MarshHaunt | MATCH | marshhaunt | 0 | OWED |  |  |
| Massiff | TWIN_NOT_WIRED | RSW_Massiff | MATCH | massiff | 1 | OWED |  |  |
| MastiffPhalone | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Mastmot | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Mawvorr | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Mott | TWIN_NOT_WIRED | RSW_Mott | MATCH | mott | 1 | OWED |  |  |
| Mudhorn | TWIN_NOT_WIRED | RSW_Mudhorn | MATCH | mudhorn | 1 | OWED |  |  |
| Mynock | DECLINED | RSW_Mynock | DECLINED | mynock | 2 | DECLINED |  | owner 2026-09-18: donor Mynock stays unported; RSW_Mynock is an unrelated owner-authored species |
| Narglatch | NOT_PORTED/PLAIN |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Neebray | TWIN_NOT_WIRED | RSW_Neebray | MATCH | neebray | 1 | OWED |  |  |
| Nerf | PORTED_WIRED | RSW_Nerf | MATCH | nerf | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Nexu | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Nuna | PORTED_WIRED | RSW_Nuna | MATCH | nuna | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Ollopom | TWIN_NOT_WIRED | RSW_Ollopom | MATCH | ollopom | 1 | OWED |  |  |
| Orray | TWIN_NOT_WIRED | RSW_Orray | MATCH | orray | 0 | OWED |  |  |
| PaintedSpat | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| PekoPeko | TWIN_NOT_WIRED | RSW_PekoPeko | MATCH | pekopeko | 1 | OWED |  |  |
| Pikobis | TWIN_NOT_WIRED | RSW_Pikobis | MATCH | pikobis | 1 | OWED |  |  |
| Porg | TWIN_NOT_WIRED | RSW_Porg | MATCH | porg | 1 | OWED |  |  |
| Pufferpig | TWIN_NOT_WIRED | RSW_Pufferpig | MATCH | pufferpig | 1 | OWED |  |  |
| Qormot | TWIN_NOT_WIRED | RSW_Qormot | MATCH | qormot | 1 | OWED |  |  |
| Rancor | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Raxshir | NOT_PORTED/PLAIN |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Reek | NOT_PORTED/PLAIN_DEPS |  | NO_TWIN | iridonianreek | 0 | OWED |  |  |
| Rikknit | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Roggwart | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Ronto | WIRED_DONOR_ROW | RSW_Ronto | MATCH | ronto | 1 | OWED |  |  |
| Runyip | WIRED_DONOR_ROW | RSW_Runyip | MATCH | runyip | 1 | OWED |  |  |
| Rycrit | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Scavrat | TWIN_NOT_WIRED | RSW_Scavrat | MATCH | NONE | 0 | OWED |  |  |
| Scurrier | WIRED_DONOR_ROW | RSW_Scurrier | DIFF: texPath not in our tree: swanimals/Scurrier/Scurrier_m | scurrier | 1 | OWED |  | W0: twin names swanimals/Scurrier/Scurrier_m, which exists only in the donor bundle (male art never extracted) |
| Shaak | PORTED_WIRED | RSW_Shaak | DIFF: baseBodySize: donor 2.0 ours 3 | shaaks | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Shiro | TWIN_NOT_WIRED | RSW_Shiro | MATCH | shiro | 2 | OWED |  |  |
| ShiroTrap | WIRED_DONOR_ROW | RSW_ShiroTrap | MATCH | shirotrap | 1 | OWED |  |  |
| Shyrack | WIRED_DONOR_ROW | RSW_Shyrack | MATCH | shyrack | 1 | OWED |  |  |
| Silooth | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | silooth | 0 | OWED |  |  |
| Skalder | WIRED_DONOR_ROW | RSW_Skalder | MATCH | skalders | 1 | OWED |  |  |
| Sketto | WIRED_DONOR_ROW | RSW_Sketto | MATCH | sketto | 1 | OWED |  |  |
| Snoruuk | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | snoruuk | 1 | OWED |  |  |
| Squall | NOT_PORTED/PLAIN |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Stintaril | NOT_PORTED/PLAIN |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Strill | TWIN_NOT_WIRED | RSW_Strill | MATCH | strill | 1 | OWED |  |  |
| Tach | NOT_PORTED/PLAIN |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Taozin | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Tauntaun | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | tauntaun | 0 | OWED |  |  |
| TeeMuss | PORTED_WIRED | RSW_TeeMuss | MATCH | teemuss | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| TetnissCrab | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Thranta | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Tibidee | NOT_PORTED/SHARED_BODY |  | NO_TWIN | tibidee | 0 | OWED |  |  |
| Tooke | NOT_PORTED/PLAIN |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Torton | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Tukata | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| TuskCat | NOT_PORTED/PLAIN |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Urusai | TWIN_NOT_WIRED | RSW_Urusai | MATCH | urusai | 2 | OWED |  |  |
| Uvak | PORTED_WIRED | RSW_Uvak | MATCH | uvak | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Vapaad | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | vaapad | 0 | OWED |  |  |
| Varactyl | PORTED_WIRED | RSW_Varactyl | MATCH | varactyl | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Veermok | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Voorpak | WIRED_DONOR_ROW | RSW_Voorpak | MATCH | voorpak | 1 | OWED |  |  |
| Vornskyr | TWIN_NOT_WIRED | RSW_Vornskyr | MATCH | vornskyr | 1 | OWED |  |  |
| Vulptex | TWIN_NOT_WIRED | RSW_Vulptex | MATCH | vulptex | 1 | OWED |  |  |
| Wampa | TWIN_NOT_WIRED | RSW_Wampa | MATCH | wampa | 0 | OWED |  |  |
| WarWyrm | PORTED_WIRED | RSW_WarWyrm | DIFF: baseBodySize: donor 15.0 ours 22.5 | sith_wyrm | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Warbird | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Whisperbird | TWIN_NOT_WIRED | RSW_Whisperbird | MATCH | whisperbird | 4 | OWED |  |  |
| WompRat | TWIN_NOT_WIRED | RSW_WompRat | MATCH | womprat | 0 | OWED |  |  |
| Woolamander | TWIN_NOT_WIRED | RSW_Woolamander | MATCH | woolamander | 1 | OWED |  |  |
| Worrt | PORTED_WIRED | RSW_Worrt | MATCH | worrt | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Wraid | PORTED_WIRED | RSW_Wraid | MATCH | wraid | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Wyyyschokk | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | wyyyschokk | 1 | OWED |  |  |
| Yobshrimp | TWIN_NOT_WIRED | RSW_Yobshrimp | DIFF: stat ArmorRating_Blunt: donor 0.08 ours 0.10; stat ArmorRating_Sharp: donor 0.12 ours 0.20; stat ComfyTemperatureMax: donor 60 ours 55; stat ComfyTemperatureMin: donor -10 ours -5; stat LeatherAmount: donor 0 ours None; stat MarketValue: donor 60 ours 40; stat MoveSpeed: donor 2.5 ours 3.2; stat Wildness: donor 0.2 ours 0.8; baseBodySize: donor 0.4 ours 0.2; baseHealthScale: donor 0.4 ours 0.35; lifeExpectancy: donor 3 ours 8; body: donor Yobshrimp ours BeetleLike; lifeStageAges: donor [('AnimalBaby', '0'), ('AnimalJuvenile', '0.05'), ('AnimalAdult', '0.1')] ours [('AnimalBaby', '0'), ('AnimalJuvenile', '0.1'), ('AnimalAdult', '0.25')] | paleyobshrimp | 1 | OWED |  |  |
| Zakkeg | TWIN_NOT_WIRED | RSW_Zakkeg | MATCH | zakkeg | 1 | OWED |  |  |
| Zeer | PORTED_WIRED | RSW_Zeer | DIFF: baseBodySize: donor 3.0 ours 4.5 | zeer | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |

## W0 findings (2026-10-14)

`donor_pack_port.py diff`: 160 donor races; 91 twins MATCH the donor on statBases, body, bodySize, healthScale,
lifeExpectancy, lifeStageAges and PawnKind lifeStage count, with every texPath resolving in our tree; 9 DIFF;
59 have no twin; Mynock DECLINED. No twin is a stub. Nothing was rewritten.

| twin | difference | reading |
|---|---|---|
| RSW_Gorg, RSW_LongtailGorg | bodySize 0.7x donor | owner sheet ruling (`f4027c934` "30% smaller") |
| RSW_WarWyrm, RSW_Shaak, RSW_Zeer | bodySize 1.5x donor | owner sheet ruling (`a89376420` "50% bigger", same pass) |
| RSW_Blurrg | adds CaravanRidingSpeedFactor 1.5, MeatAmount 350 | deliberate mount sizing (its header comment) |
| RSW_Yobshrimp | different creature (BeetleLike body, sea swarm) | our SeaBeasts redesign, not a port |
| RSW_Jimvu | lifeExpectancy 30 vs donor 22 | set at its port (`bab45edca`); unexplained; reported, not changed |
| RSW_Scurrier | texPath `swanimals/Scurrier/Scurrier_m` has no PNG in our tree | binds only through the donor; fix row: extract the male art (same picture the game shows today) |
