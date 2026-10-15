# Donor pack port tracker: mlie.starwarsanimalcollection (160 species)

Item `DONOR_DEFS_PORT_TO_OURS_1`; plan `design/RimMandrake/donor_pack_port_plan_2026-10-14.md`. Script: `src/RimMandrake/Utils/donor_pack_port.py` (`diff` = W0, `rosters`, `repoint` = W1). One row per donor race. `class` is the 2026-10-14 census class; `W0` is the twin-vs-donor diff (MATCH / DIFF with the differences / NO_TWIN); `rows` is donor-named roster rows still left; `status` is this pass's outcome; `sha` the commit that did it.

Statuses: DONE_ALREADY_OWNED (twin existed; only roster rows repointed, art and defs untouched) · PORTED (new RSW_ def this pass) · ART_BLOCKED · OWNER_QUESTION · DECLINED · OWED (not reached).

| species | class | twin | W0 | canon entry | rows left | status | sha | note |
|---|---|---|---|---|---:|---|---|---|
| Acklay | TWIN_NOT_WIRED | RSW_Acklay | MATCH; namer | acklay | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Aiwha | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Akk | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Anooba | TWIN_NOT_WIRED | RSW_Anooba | MATCH; namer | anooba | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Bantha | WIRED_DONOR_ROW | RSW_Bantha | MATCH; namer | bantha | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Behemoth | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Beldon | TWIN_NOT_WIRED | RSW_Beldon | MATCH; namer | beldon | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Blarth | TWIN_NOT_WIRED | RSW_Blarth | MATCH; namer | blarth | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Blixus | TWIN_NOT_WIRED | RSW_Blixus | MATCH; namer | blixus | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Blurrg | TWIN_NOT_WIRED | RSW_Blurrg | DIFF: stat CaravanRidingSpeedFactor: donor None ours 1.5; stat MeatAmount: donor None ours 350; namer | blurrg | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Boarwolf | NOT_PORTED/PLAIN | RSW_Boarwolf | NO_TWIN | boarwolf (new) | 0 | PORTED | W2b | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings); canon is a 3 m predator; the donor def/sprite is a farm-boar: reported in the entry |
| Bogwing | TWIN_NOT_WIRED | RSW_Bogwing | MATCH; namer | bogwing | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Bolotaur | PORTED_WIRED | RSW_Bolotaur | MATCH; namer | bolotaur | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Boma | TWIN_NOT_WIRED | RSW_Boma | MATCH; namer | boma | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Borcatu | TWIN_NOT_WIRED | RSW_Borcatu | MATCH; donor-only refs: Borcatu; namer | borcatu | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Bordok | NOT_PORTED/PLAIN | RSW_Bordok | NO_TWIN | bordok (new) | 0 | PORTED | W2b | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) |
| Brezak | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Bursa | NOT_PORTED/PLAIN | RSW_Bursa | NO_TWIN | bursa (new) | 0 | PORTED | W2b | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings); canon entry is Legends-only |
| CanCell | TWIN_NOT_WIRED | RSW_CanCell | MATCH; namer | cancell | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Cannok | TWIN_NOT_WIRED | RSW_Cannok | MATCH; namer | cannok | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| ChrysalideRancor | NOT_PORTED/SHARED_BODY_ITEMS | RSW_ChrysalideRancor | NO_TWIN | chrysaliderancor (new) | 0 | PORTED | W3a | donor art extracted; unrostered (placement belongs to the biome sittings); canon is the Legends page "Chrysalide" (green skin); donor sprites are white/grey: reported |
| Clodhopper | WIRED_DONOR_ROW | RSW_Clodhopper | MATCH; namer | clodhopper | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Convor | TWIN_NOT_WIRED | RSW_Convor | MATCH; namer | convor | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| CorellianHound | NOT_PORTED/PLAIN | RSW_CorellianHound | NO_TWIN | corellianhound (new) | 0 | PORTED | W2b | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings); BodyDef RSW_CorellianHound already existed (Grank port); reused |
| Corinathoth | TWIN_NOT_WIRED | RSW_Corinathoth | MATCH; namer | corinathoth | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Dactillion | TWIN_NOT_WIRED | RSW_Dactillion | MATCH; namer | dactillion | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Dalgo | TWIN_NOT_WIRED | RSW_Dalgo | MATCH; donor-only refs: SW_Spur; namer | dalgo | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Devourers | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Dewback | TWIN_NOT_WIRED | RSW_Dewback | MATCH; namer | dewback | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Dianoga | TWIN_NOT_WIRED | RSW_Dianoga | MATCH; namer | dianoga | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Dragonsnake | TWIN_NOT_WIRED | RSW_Dragonsnake | MATCH; donor-only refs: Dragonsnake; namer | dragonsnake | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Drexl | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| EnergySpider | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Eopie | WIRED_DONOR_ROW | RSW_Eopie | MATCH; donor-only refs: Cameloid_Meat, SW_Spit; namer | eopie | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Falumpaset | WIRED_DONOR_ROW | RSW_Falumpaset | MATCH; donor-only refs: Cameloid_Meat, SW_Spur; namer | falumpaset | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Fambaa | TWIN_NOT_WIRED | RSW_Fambaa | MATCH; namer | fambaa | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Fanback | TWIN_NOT_WIRED | RSW_Fanback | MATCH; namer | fanback | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| FeralGrazer | PORTED_WIRED | RSW_FeralGrazer | MATCH; donor-only refs: Grazer; namer | grazer | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| FeralNerf | TWIN_NOT_WIRED | RSW_FeralNerf | MATCH; donor-only refs: Grazer, SW_Spit; namer | NONE | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| FrilledGorg | WIRED_DONOR_ROW | RSW_FrilledGorg | MATCH; namer | NONE | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| FrogDog | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Gelagrub | TWIN_NOT_WIRED | RSW_Gelagrub | MATCH; namer | gelagrub | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Gizka | PORTED_WIRED | RSW_Gizka | MATCH; namer | gizka | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Gorg | WIRED_DONOR_ROW | RSW_Gorg | DIFF: baseBodySize: donor 0.3 ours 0.21; namer | gorg | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Gornt | TWIN_NOT_WIRED | RSW_Gornt | MATCH; namer | gornt | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| GraniteSlug | WIRED_DONOR_ROW | RSW_GraniteSlug | MATCH; namer | graniteslug | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Grank | TWIN_NOT_WIRED | RSW_Grank | MATCH; donor-only refs: Grank; namer | grank | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Grazer | NOT_PORTED/PLAIN_DEPS | RSW_Grazer | NO_TWIN | grazer | 0 | PORTED | W2c | donor art extracted; unrostered (placement belongs to the biome sittings); canon entry is the existing grazer/ entry (written for RSW_FeralGrazer; not edited) |
| GreaterKraytDragon | PORTED_WIRED | RSW_GreaterKraytDragon | MATCH; donor-only refs: KellDragon; namer | greaterkraytdragon | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Gualaar | NOT_PORTED/PLAIN | RSW_Gualaar | NO_TWIN | gualaar (new) | 0 | PORTED | W2b | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings); owner ArtFold art carried over; it contradicts canon (single big head horn, snout horns, white coat): reported in the entry, not changed |
| Gullipud | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Gundark | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Gutkurr | PORTED_WIRED | RSW_Gutkurr | MATCH; namer | gutkurr | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| HarvesterBeetle | NOT_PORTED/PLAIN_DEPS | RSW_HarvesterBeetle | NO_TWIN | harvesterbeetle (new) | 0 | PORTED | W2c | donor art extracted; unrostered (placement belongs to the biome sittings) |
| Hawkbat | TWIN_NOT_WIRED | RSW_Hawkbat | MATCH; namer | hawkbat | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Horax | PORTED_WIRED | RSW_Horax | MATCH; namer | horax | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Hrumph | PORTED_WIRED | RSW_Hrumph | MATCH; namer | hrumph | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Hssiss | TWIN_NOT_WIRED | RSW_Hssiss | MATCH; namer | hssiss | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Igitz | TWIN_NOT_WIRED | RSW_Igitz | MATCH; namer | igitz | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Insectomorph | NOT_PORTED/SHARED_BODY |  | NO_TWIN | insectomorph | 0 | OWED |  |  |
| Iriaz | WIRED_DONOR_ROW | RSW_Iriaz | MATCH; namer | iriaz | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| IridonianReek | PORTED_WIRED | RSW_IridonianReek | MATCH; donor-only refs: IthorianReek, Reek; namer | iridonianreek | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| IthorianReek | NOT_PORTED/PLAIN_DEPS | RSW_IthorianReek | NO_TWIN | ithorianreek (new) | 0 | PORTED | W2c | donor art extracted; unrostered (placement belongs to the biome sittings); no page of its own: a section of Reek/Legends; juvenile shares swanimals/Reek/Reek_j with the reeks |
| Jakobeast | PORTED_WIRED | RSW_Jakobeast | MATCH; donor-only refs: SW_ForcePush; namer | jakobeast | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Jamel | WIRED_DONOR_ROW | RSW_Jamel | MATCH; donor-only refs: Cameloid_Meat, Jamel; namer | jamel | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Jimvu | PORTED_WIRED | RSW_Jimvu | DIFF: lifeExpectancy: donor 22 ours 30; namer | jimvu | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| JungleRancor | NOT_PORTED/SHARED_BODY_ITEMS | RSW_JungleRancor | NO_TWIN | junglerancor (new) | 0 | PORTED | W3a | donor art extracted; unrostered (placement belongs to the biome sittings); male draws the donor BullRancor sprite (grey, tusked), contradicting canon: reported in the entry |
| Kaadu | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Kaadu | NO_TWIN | kaadu (new) | 0 | PORTED | W3b | donor art extracted; unrostered (placement belongs to the biome sittings); body RSW_Kaadu shared with PaintedSpat; PathfindingFramework MovementExtension kept MayRequire-guarded |
| Katarn | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| KellDragon | NOT_PORTED/PLAIN_DEPS | RSW_KellDragon | NO_TWIN | kelldragon (new) | 0 | PORTED | W2c | donor art extracted; unrostered (placement belongs to the biome sittings); canon entry Legends-only |
| Kinrath | TWIN_NOT_WIRED | RSW_Kinrath | MATCH; namer | kinrath | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Klorslug | TWIN_NOT_WIRED | RSW_Klorslug | MATCH; namer | klorslug | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| KowakianMonkeyLizard | TWIN_NOT_WIRED | RSW_KowakianMonkeyLizard | MATCH; namer | kowakianmonkeylizard | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| KraytDragon | PORTED_WIRED | RSW_KraytDragon | MATCH; donor-only refs: KellDragon; namer | kraytdragon | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Kreetle | PORTED_WIRED | RSW_Kreetle | MATCH; namer | kreetle | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Krykna | PORTED_WIRED | RSW_Krykna | MATCH; namer | krykna | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| KwazelMaw | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Kwi | PORTED_WIRED | RSW_Kwi | MATCH; donor-only refs: Kwi, SW_Spur; namer | kwi | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Kybuck | TWIN_NOT_WIRED | RSW_Kybuck | MATCH; namer | kybuck | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| LavaFlea | TWIN_NOT_WIRED | RSW_LavaFlea | MATCH; namer | lavaflea | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Leaftail | NOT_PORTED/PLAIN | RSW_Leaftail | NO_TWIN | leaftail (new) | 0 | PORTED | W2b | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) |
| LongtailGorg | WIRED_DONOR_ROW | RSW_LongtailGorg | DIFF: baseBodySize: donor 0.6 ours 0.42; namer | longtailgorg | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| LothWolf | NOT_PORTED/PLAIN_DEPS | RSW_LothWolf | NO_TWIN | lothwolf (new) | 0 | PORTED | W2c | donor art extracted; unrostered (placement belongs to the biome sittings); canon Loth-wolves are SENTIENT and speak Basic; ported as an animal, reported in the entry; ports SW_ForceChaosSkip as RSW_SW_ForceChaosSkip |
| Lothcat | TWIN_NOT_WIRED | RSW_Lothcat | MATCH; namer | lothcat | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Lylek | TWIN_NOT_WIRED | RSW_Lylek | MATCH; namer | lylek | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Maalraas | NOT_PORTED/PLAIN_DEPS | RSW_Maalraas | NO_TWIN | maalraas (new) | 0 | PORTED | W2c | donor art extracted; unrostered (placement belongs to the biome sittings); ports SW_ForceInvisibility as RSW_SW_ForceInvisibility |
| Manka | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| MarshHaunt | TWIN_NOT_WIRED | RSW_MarshHaunt | MATCH; namer | marshhaunt | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Massiff | TWIN_NOT_WIRED | RSW_Massiff | MATCH; namer | massiff | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| MastiffPhalone | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Mastmot | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Mawvorr | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Mott | TWIN_NOT_WIRED | RSW_Mott | MATCH; namer | mott | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Mudhorn | TWIN_NOT_WIRED | RSW_Mudhorn | MATCH; namer | mudhorn | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Mynock | DECLINED | RSW_Mynock | DECLINED | mynock | 2 | DECLINED |  | owner 2026-09-18: donor Mynock stays unported; RSW_Mynock is an unrelated owner-authored species |
| Narglatch | NOT_PORTED/PLAIN | RSW_Narglatch | NO_TWIN | narglatch (new) | 0 | PORTED | W2b | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) |
| Neebray | TWIN_NOT_WIRED | RSW_Neebray | MATCH; namer | neebray | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Nerf | PORTED_WIRED | RSW_Nerf | MATCH; donor-only refs: Grazer, SW_Spit; namer | nerf | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Nexu | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Nuna | PORTED_WIRED | RSW_Nuna | MATCH; namer | nuna | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Ollopom | TWIN_NOT_WIRED | RSW_Ollopom | MATCH; namer | ollopom | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Orray | TWIN_NOT_WIRED | RSW_Orray | MATCH; namer | orray | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| PaintedSpat | NOT_PORTED/SHARED_BODY_ITEMS | RSW_PaintedSpat | NO_TWIN | paintedspat (new) | 0 | PORTED | W3b | donor art extracted; unrostered (placement belongs to the biome sittings); shares RSW_Kaadu body |
| PekoPeko | TWIN_NOT_WIRED | RSW_PekoPeko | MATCH; namer | pekopeko | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Pikobis | TWIN_NOT_WIRED | RSW_Pikobis | MATCH; namer | pikobis | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Porg | TWIN_NOT_WIRED | RSW_Porg | MATCH; namer | porg | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Pufferpig | TWIN_NOT_WIRED | RSW_Pufferpig | MATCH; donor-only refs: Pufferpig; namer | pufferpig | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Qormot | TWIN_NOT_WIRED | RSW_Qormot | MATCH; namer | qormot | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Rancor | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Rancor | NO_TWIN | rancor (new) | 0 | PORTED | W3a | donor art extracted; unrostered (placement belongs to the biome sittings); body RSW_Rancor shared by the three rancors; ports SW_ToxicSpew |
| Raxshir | NOT_PORTED/PLAIN | RSW_Raxshir | NO_TWIN | raxshir (new) | 0 | PORTED | W2b | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) |
| Reek | NOT_PORTED/PLAIN_DEPS | RSW_Reek | NO_TWIN | reek (new) | 0 | PORTED | W2c | donor art extracted; unrostered (placement belongs to the biome sittings) |
| Rikknit | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Roggwart | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Ronto | WIRED_DONOR_ROW | RSW_Ronto | MATCH; namer | ronto | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Runyip | WIRED_DONOR_ROW | RSW_Runyip | MATCH; namer | runyip | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Rycrit | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Scavrat | TWIN_NOT_WIRED | RSW_Scavrat | MATCH; namer | NONE | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Scurrier | WIRED_DONOR_ROW | RSW_Scurrier | DIFF: texPath not in our tree: swanimals/Scurrier/Scurrier_m; namer | scurrier | 0 | OWNER_QUESTION | W1 | rows repointed; the male art (swanimals/Scurrier/Scurrier_m) exists only in the donor bundle and the art ledger refuses it: the owner purged that picture (16618daa21c9). Needs a regen of the male before W4. |
| Shaak | PORTED_WIRED | RSW_Shaak | DIFF: baseBodySize: donor 2.0 ours 3; namer | shaaks | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Shiro | TWIN_NOT_WIRED | RSW_Shiro | MATCH; namer | shiro | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| ShiroTrap | WIRED_DONOR_ROW | RSW_ShiroTrap | MATCH; donor-only refs: RawTookeTrapRoot; namer | shirotrap | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Shyrack | WIRED_DONOR_ROW | RSW_Shyrack | MATCH; namer | shyrack | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Silooth | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | silooth | 0 | OWED |  |  |
| Skalder | WIRED_DONOR_ROW | RSW_Skalder | MATCH; donor-only refs: SkalderTusk; namer | skalders | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Sketto | WIRED_DONOR_ROW | RSW_Sketto | MATCH; namer | sketto | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Snoruuk | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | snoruuk | 1 | ART_BLOCKED |  | adult art is the donor picture the owner sent back for redo (therot_sheet_2026-10-05); the ledger refuses it. Candidate renders exist (artpipe done/rotrow_snoruuk_v2_*, enact_6811876e_snoruuk_v1_*) awaiting his pick. Not ported; both TheRot rows stay on the donor. |
| Squall | NOT_PORTED/PLAIN | RSW_Squall | NO_TWIN | squall (new) | 0 | PORTED | W2b | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings); Wookieepedia title is "Squall (species)"; canon page is a stub |
| Stintaril | NOT_PORTED/PLAIN | RSW_Stintaril | NO_TWIN | stintaril (new) | 0 | PORTED | W2b | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) |
| Strill | TWIN_NOT_WIRED | RSW_Strill | MATCH; namer | strill | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Tach | NOT_PORTED/PLAIN | RSW_Tach | NO_TWIN | tach (new) | 0 | PORTED | W2b | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) |
| Taozin | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Tauntaun | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Tauntaun | NO_TWIN | tauntaun | 0 | PORTED | W2a | owner canon art (Tauntaun_CanonArt patch) baked in; only the two dessicated textures are extracted donor art; NightsideIce row repointed, its FindMod guard moved to SWBestiary |
| TeeMuss | PORTED_WIRED | RSW_TeeMuss | MATCH; namer | teemuss | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| TetnissCrab | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Thranta | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Tibidee | NOT_PORTED/SHARED_BODY | RSW_Tibidee | NO_TWIN | tibidee | 0 | PORTED | W2a | donor art extracted; canon says flier: real flight owed (MaxFlightTime + flip-book art; never live-test flight without the owner); TheForge row repointed |
| Tooke | NOT_PORTED/PLAIN | RSW_Tooke | NO_TWIN | tooke (new) | 0 | PORTED | W2b | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) |
| Torton | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Tukata | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| TuskCat | NOT_PORTED/PLAIN | RSW_TuskCat | NO_TWIN | tuskcat (new) | 0 | PORTED | W2b | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) |
| Urusai | TWIN_NOT_WIRED | RSW_Urusai | MATCH; namer | urusai | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Uvak | PORTED_WIRED | RSW_Uvak | MATCH; namer | uvak | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Vapaad | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Vapaad | NO_TWIN | vaapad | 0 | PORTED | W2a | owner Blue Desert art + canon description (Vapaad_BlueDesertArt patch) baked in; that art lives in UtinniPatches (RUT tier) while the def is RSW: tier smell, not moved; BlueDesert row repointed, FindMod guard moved to SWBestiary |
| Varactyl | PORTED_WIRED | RSW_Varactyl | MATCH; namer | varactyl | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Veermok | NOT_PORTED/SHARED_BODY |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Voorpak | WIRED_DONOR_ROW | RSW_Voorpak | MATCH; namer | voorpak | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Vornskyr | TWIN_NOT_WIRED | RSW_Vornskyr | MATCH; donor-only refs: Vornskyr; namer | vornskyr | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Vulptex | TWIN_NOT_WIRED | RSW_Vulptex | MATCH; namer | vulptex | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Wampa | TWIN_NOT_WIRED | RSW_Wampa | MATCH; namer | wampa | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| WarWyrm | PORTED_WIRED | RSW_WarWyrm | DIFF: baseBodySize: donor 15.0 ours 22.5; donor-only refs: WarWyrmSkull; namer | sith_wyrm | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Warbird | NOT_PORTED/SHARED_BODY_ITEMS |  | NO_TWIN | NONE | 0 | OWED |  |  |
| Whisperbird | TWIN_NOT_WIRED | RSW_Whisperbird | MATCH; namer | whisperbird | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| WompRat | TWIN_NOT_WIRED | RSW_WompRat | MATCH; namer | womprat | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Woolamander | TWIN_NOT_WIRED | RSW_Woolamander | MATCH; namer | woolamander | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Worrt | PORTED_WIRED | RSW_Worrt | MATCH; namer | worrt | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Wraid | PORTED_WIRED | RSW_Wraid | MATCH; namer | wraid | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |
| Wyyyschokk | NOT_PORTED/SHARED_BODY_ITEMS | RM_Ollathrix | NO_TWIN | wyyyschokk | 0 | DONE_ALREADY_OWNED | W2a | not ported: owner 2026-10-03 ruled RM_Ollathrix is THE wyyyschokk (RSW_Wyyyschokk retired, WYYYSCHOKK_IDENTITY_COLLISION_1); the RUT_Webwork donor row is repointed to RM_Ollathrix (mandrake.rm.webwork) |
| Yobshrimp | TWIN_NOT_WIRED | RSW_Yobshrimp | DIFF: stat ArmorRating_Blunt: donor 0.08 ours 0.10; stat ArmorRating_Sharp: donor 0.12 ours 0.20; stat ComfyTemperatureMax: donor 60 ours 55; stat ComfyTemperatureMin: donor -10 ours -5; stat LeatherAmount: donor 0 ours None; stat MarketValue: donor 60 ours 40; stat MoveSpeed: donor 2.5 ours 3.2; stat Wildness: donor 0.2 ours 0.8; baseBodySize: donor 0.4 ours 0.2; baseHealthScale: donor 0.4 ours 0.35; lifeExpectancy: donor 3 ours 8; body: donor Yobshrimp ours BeetleLike; lifeStageAges: donor [('AnimalBaby', '0'), ('AnimalJuvenile', '0.05'), ('AnimalAdult', '0.1')] ours [('AnimalBaby', '0'), ('AnimalJuvenile', '0.1'), ('AnimalAdult', '0.25')] | paleyobshrimp | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Zakkeg | TWIN_NOT_WIRED | RSW_Zakkeg | MATCH; namer | zakkeg | 0 | DONE_ALREADY_OWNED | W1 | donor roster rows repointed to the twin; defs and art untouched |
| Zeer | PORTED_WIRED | RSW_Zeer | DIFF: baseBodySize: donor 3.0 ours 4.5; namer | zeer | 0 | DONE_ALREADY_OWNED | W0 | twin wired, no donor row; untouched |

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

## Wave commits

| wave | sha | what |
|---|---|---|
| W0 | 5d97437d51ff | twin diff + this tracker |
| W1 | deab5ccedac4 | 82 donor roster rows in 10 `RUT_*` BiomeDefs repointed to the RSW_ twin under `MayRequire="mandrake.rsw.swbestiary"`; 4 left (Mynock x2 declined, Snoruuk, Wyyyschokk not yet ported) |
| W2a | 584de64af490 | the 5 roster-named species: Tauntaun, Tibidee, Vapaad ported; Snoruuk ART_BLOCKED; Wyyyschokk is RM_Ollathrix |
| W2b | 695812d5ec72 | 13 plain species ported, 13 canon entries written (one per species, all sourced from Wookieepedia; Bursa Legends-only) |
| W2c | dd2dea5ffead | 7 plain-with-deps species ported; 6 canon entries written (Ithorian reek from a Reek/Legends section) |
| W3a+W3b | see git log of this file | rancor family (Rancor, JungleRancor, ChrysalideRancor; one shared body) and Kaadu + PaintedSpat (one shared body) |

W1 check: `validate_patch.py --live --defs` 10 files 0 errors 0 warnings, but it does NOT check BiomeDef roster names
(probe: a bogus `RSW_NotABeastZZ` row passed), so `donor_pack_port.py check` does: 188 RSW_ roster rows resolve to an
RSW_ race with a PawnKindDef, 0 unresolved (probe: the bogus row is caught, exit 1).

## W4 blockers found in the twins (W0b, `donor_pack_port.py diff`, `donor_refs`)

A name the donor alone defines fails as a cross-reference the moment the donor is off. 99 of the 100 twins still name
the donor's `SWAnimalNamerMale` / `SWAnimalNamerFemale` RulePackDefs (`namer` in the W0 column); 16 also name other
donor-only defs (`donor-only refs`): `canCrossBreedWith` partners not yet ported or never renamed (Grazer, KellDragon,
Reek, IthorianReek, and bare names of species we DO own: Borcatu, Dragonsnake, Grank, Jamel, Kwi, Pufferpig, Vornskyr),
abilities `SW_Spur`/`SW_Spit`/`SW_ForcePush`, `Cameloid_Meat`, `RawTookeTrapRoot`, `SkalderTusk`, `WarWyrmSkull`.
Not rewritten (twin defs are out of this pass's scope). Fix owed before W4: the new ports carry
`RSW_SWAnimalNamerMale`/`Female` (ported in W2), so each twin needs a one-token repoint, and each bare partner/item a
repoint to its RSW_ copy or a port.

## How a port is made (W2 on)

`donor_pack_port.py port --batch B --species A,B --extract <bundle dump> --active <active list> --vanilla <names>`:
race ThingDef + PawnKindDef to `SWBestiary/Defs/ThingDefs_Races/RSW_<Sp>.xml`; every donor-only def they reach to
`SWBestiary/Defs/DonorPackPort/RSW_DonorPack_<B>.xml` as RSW_<name> (once; existing RSW_ copies are reused);
**our own patches that target the donor defName are applied first** (owner art folds and canon-art patches,
BeastNorm, tolerances, evictions, resizes), so the port is the creature the game shows today and owner-handled art is
moved over, not regenerated. A species whose art the ledger refuses (owner purge or send-back) or the bundle lacks is
ART_BLOCKED and left out whole. Art goes through `artwrite.TextureWriter` (the art ledger).
Owed when the donor is retired (W4): the patch ops that still name a ported donor defName go dead (their effect is
baked into the port); generators that emit them (BeastNorm manifest, MegafaunaYield, AnimalTolerances, evictions)
should learn the RSW_ names before they are next regenerated.

New ports differ from the raw donor only where our own patches already changed the donor in game (W0 diff on the
ports: comfy-temperature pins from `AnimalTolerances_Ashkarr.xml` on 9 of 23; BeastNorm tool numbers are not in
the diff). No new port names a donor-only def (`donor_refs` empty for all of them).
