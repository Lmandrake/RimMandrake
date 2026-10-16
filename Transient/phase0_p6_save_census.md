# Phase 0 P6: donor census of the canonical save (2026-10-15)

Save: `CANONICAL_ASHKARR_START_2026-09-12.rws` (sha256 `1ff329161abeaa8c66ebe2818de5428b8a1a9d95676f106dcd2b8d6f98a008c6`, untouched).
Tool: `src/RimMandrake/Utils/save_donor_census.py` (ElementTree; a hit = an element whose WHOLE text is a donor defName; donor
names from every `Defs/` folder under each donor's workshop `1.6/` plus engine-made Blueprint_/Frame_/Corpse_/Meat_ names).
Control: `<def>Human</def>` = 75 before and after, so the instrument can see. Runtime owner check against the 2026-10-04 def
dump: 1389 of 1410 names are donor-only; `Devourers` is also an Anomaly PawnGroupKindDef, but every save hit is a ThingDef context, which is SWAC's (renamed to `RSW_Devourers`); 19 `VCEF_*` are alphabiomes-shipped (report only).

## Before / after (text)

| donor | names before | hits before | names after | hits after |
|---|---:|---:|---:|---:|
| mlie.starwarsanimalcollection | 626 | 4226 | 6 | 6 (ideo icons, held) |
| sarg.alphaanimals | 493 | 2442 | 2 | 7 (the ikee pawn, held) |
| sarg.alphabiomes (report only) | 291 | 1187 | 291 | 1187 |
| packageId rows in `<meta>` | 3 | | 1 (alphabiomes) | |

Where the hits were: storage filters 5683, price history 1548 (key+value), auto-slaughter 288, Big & Small caches 54,
work priorities 54 (45 are alphabiomes), landmarks 26, drug policies 20, everything else under 15.

## Grids (binary, NOT text; decoded with shortHashes from the 2026-10-04 def dump)

Map terrain/roof/thing/deep-resource/biome grids: 0 donor hashes. **World `tileMutatorDefsDeflate` holds SWAC mutators on
1429 tiles**: `WildTattooinePlants` 1403, `sw_DeadSarlaccCave` 12, `sw_SarlaccLair` 8, `WildDantooinePlants` 4,
`WildGalacticPlants` 2 (plus 21 alphabiomes mutators, report only). The earlier text grep that read `sw_SarlaccLair` = 0
was blind to this grid. **Not rewritten**: `RSW_SarlaccLair`/`RSW_DeadSarlaccCave` are in no def dump yet (no shortHash
of the load mod set), and the three `Wild*Plants` mutators have no port.

## Per-name census (before)

- control `<def>Human</def>` = 75
- donor defNames known: mlie.starwarsanimalcollection 1617, sarg.alphaanimals 1132, sarg.alphabiomes 829
- donor names present in save: 1410 (total element hits 7855)
- packageIds as `<li>` rows: mlie.starwarsanimalcollection 1, sarg.alphaanimals 1, sarg.alphabiomes 1
- names also appearing inside other text (not whole-element): `Behemoth` +2, `Mynock` +1, `Kreetle` +1, `Dewback` +1, `Gizka` +2, `Anooba` +1, `Dalgo` +1, `Dragonsnake` +1, `Fambaa` +1, `Grank` +1, `Horax` +2, `Insectomorph` +1, `Iriaz` +1, `Kinrath` +1, `Nuna` +1, `Ollopom` +1, `Orray` +1, `Ronto` +1, `Shiro` +1, `Vornskyr` +1, `Whisperbird` +1, `Wyyyschokk` +1, `Zakkeg` +1, `Zeer` +1

| donor | defName | def type | count | where (element path, count) |
|---|---|---|---:|---|
| mlie.starwarsanimalcollection | `Acklay` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `AcklayClaw` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Aiwha` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Akk` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Anooba` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Anthropoid_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Bantha` | ThingDef | 11 | `li/BS_scribedCache/li/BS_OriginalThing` 7; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `BanthaHorn` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Bantha_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Behemoth` | BodyDef | 5 | `li/BS_scribedCache/li/BS_OriginalThing` 1; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `BehemothSkull` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `li/precepts/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Beldon` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Blarth` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Blixus` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `BlueMilk` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Blueprint_Install_DeadSarlacc` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| mlie.starwarsanimalcollection | `Blueprint_Install_SarlaccPit` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| mlie.starwarsanimalcollection | `Blurrg` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Boarwolf` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Bogwing` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Bolotaur` | ThingDef | 7 | `li/BS_scribedCache/li/BS_OriginalThing` 3; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Boma` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Borcatu` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Bordok` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Brezak` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Bullet_AnimalToxbomb` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| mlie.starwarsanimalcollection | `Bursa` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Cameloid_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `CanCell` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Cannok` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `ChrysalideHeart` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `ChrysalideRancor` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Clodhopper` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Convor` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `CorellianHound` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Corinathoth` | ThingDef | 9 | `li/BS_scribedCache/li/BS_OriginalThing` 5; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Corpse_Acklay` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Aiwha` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Akk` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Anooba` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Bantha` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Behemoth` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Beldon` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Blarth` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Blixus` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Blurrg` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Boarwolf` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Bogwing` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Bolotaur` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Boma` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Borcatu` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Bordok` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Brezak` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Bursa` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_CanCell` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Cannok` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_ChrysalideRancor` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Clodhopper` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Convor` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_CorellianHound` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Corinathoth` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Dactillion` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Dalgo` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Devourers` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Dewback` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Dianoga` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Dragonsnake` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Drexl` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_EnergySpider` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| mlie.starwarsanimalcollection | `Corpse_Eopie` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Falumpaset` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Fambaa` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Fanback` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_FeralGrazer` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_FeralNerf` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_FrilledGorg` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_FrogDog` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Gelagrub` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| mlie.starwarsanimalcollection | `Corpse_Gizka` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Gorg` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Gornt` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_GraniteSlug` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Grank` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Grazer` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_GreaterKraytDragon` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Gualaar` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Gullipud` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Gundark` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Gutkurr` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_HarvesterBeetle` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| mlie.starwarsanimalcollection | `Corpse_Hawkbat` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Horax` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Hrumph` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Hssiss` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Igitz` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Insectomorph` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Iriaz` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_IridonianReek` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_IthorianReek` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Jakobeast` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Jamel` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Jimvu` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_JungleRancor` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Kaadu` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Katarn` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_KellDragon` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Kinrath` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| mlie.starwarsanimalcollection | `Corpse_Klorslug` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| mlie.starwarsanimalcollection | `Corpse_KowakianMonkeyLizard` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_KraytDragon` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Kreetle` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| mlie.starwarsanimalcollection | `Corpse_Krykna` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| mlie.starwarsanimalcollection | `Corpse_KwazelMaw` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Kwi` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Kybuck` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_LavaFlea` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Leaftail` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_LongtailGorg` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_LothWolf` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Lothcat` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Lylek` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Maalraas` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Manka` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_MarshHaunt` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Massiff` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_MastiffPhalone` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Mastmot` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Mawvorr` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Mott` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Mudhorn` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Mynock` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Narglatch` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Neebray` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Nerf` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Nexu` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Nuna` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Ollopom` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Orray` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_PaintedSpat` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_PekoPeko` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Pikobis` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Porg` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Pufferpig` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Qormot` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Rancor` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Raxshir` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Reek` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Rikknit` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Roggwart` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Ronto` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Runyip` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Rycrit` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Scavrat` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Scurrier` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Shaak` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Shiro` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_ShiroTrap` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Shyrack` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Silooth` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| mlie.starwarsanimalcollection | `Corpse_Skalder` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Sketto` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Snoruuk` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Squall` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Stintaril` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Strill` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Tach` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Taozin` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| mlie.starwarsanimalcollection | `Corpse_Tauntaun` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_TeeMuss` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_TetnissCrab` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Thranta` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Tibidee` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Tooke` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Torton` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Tukata` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_TuskCat` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Urusai` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Uvak` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Vapaad` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Varactyl` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Veermok` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Voorpak` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Vornskyr` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Vulptex` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Wampa` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_WarWyrm` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Warbird` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Whisperbird` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_WompRat` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Woolamander` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Worrt` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Wraid` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Wyyyschokk` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| mlie.starwarsanimalcollection | `Corpse_Yobshrimp` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Zakkeg` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Corpse_Zeer` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Crustapod_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Dactillion` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Dalgo` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `DeadSarlacc` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Devourers` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Dewback` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Dianoga` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `DoBillsFeedSarlacc` | WorkGiverDef | 9 | `li/Priorities/li/Workgiver` 9 |
| mlie.starwarsanimalcollection | `Dragonsnake` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Drexl` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `EggAcklayFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggAcklayUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggAkkFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggAkkUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggAmphispawnUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggBeldonFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggBeldonUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggBlixusFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggBlixusUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggBlurrgFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggBlurrgUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggBogwingFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggBogwingUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggBolotaurFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggBolotaurUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggBomaFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggBomaUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggBrezakFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggBrezakUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggCanCellFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggCanCellUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggChrysalideRancorFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggChrysalideRancorUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggClodhopperFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggClodhopperUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggConvorFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggConvorUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggDactillionFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggDactillionUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggDewbackFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggDewbackUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggDragonsnakeFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggDragonsnakeUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggDrexlFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggDrexlUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggEnergySpiderFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggEnergySpiderUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggFambaaFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggFambaaUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggFanbackFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggFanbackUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggFrilledGorgFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggFrilledGorgUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggGelagrubFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggGelagrubUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggGizkaFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggGizkaUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggGorgFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggGorgUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggGreaterKraytDragonFertilized` | ThingDef | 12 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `li/npcSubmittedContracts/li/item` 1 |
| mlie.starwarsanimalcollection | `EggGreaterKraytDragonUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggGullipudFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggGullipudUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggGutkurrFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggGutkurrUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggHarvesterBeetleFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggHarvesterBeetleUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggHawkbatFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggHawkbatUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggHoraxFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggHoraxUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggHssissFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggHssissUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggIgitzFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggIgitzUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggInsectileUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggJungleRancorFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggJungleRancorUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKaaduFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKaaduUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKellDragonFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKellDragonUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKinrathFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKinrathUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKlorslugFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKlorslugUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKraytDragonFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKraytDragonUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKryknaFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKryknaUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKwazelMawFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKwazelMawUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKwiFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggKwiUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggLavaFleaFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggLavaFleaUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggLongtailGorgFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggLongtailGorgUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggLylekFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggLylekUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggMammavianUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggMastiffPhaloneFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggMastiffPhaloneUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggMudhornFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggMudhornUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggNunaFertilized` | ThingDef | 12 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `li/npcSubmittedContracts/li/item` 1 |
| mlie.starwarsanimalcollection | `EggNunaUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggPaintedSpatFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggPaintedSpatUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggPekopekoFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggPekopekoUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggPikobisFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggPikobisUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggPodUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggPorgFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggPorgUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggRancorFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggRancorUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggReptavianUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggRikknitFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggRikknitUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggRoeUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggShiroFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggShiroTrapFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggShiroTrapUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggShiroUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggShyrackFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggShyrackUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggSiloothFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggSiloothUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggSnoruukFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggSnoruukUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggTaozinFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggTaozinUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggTetnissCrabFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggTetnissCrabUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggThrantaFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggThrantaUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggTortonFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggTortonUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggUrusaiFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggUrusaiUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggUvakFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggUvakUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggVaractylFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggVaractylUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggWarbirdFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggWarbirdUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggWhisperbirdFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggWhisperbirdUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggWorrtFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggWorrtUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggWraidFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggWraidUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggWyyyschokkFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggWyyyschokkUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggYobshrimpFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EggYobshrimpUnFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `EnergySpider` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Eopie` | BodyDef | 15 | `li/BS_scribedCache/li/BS_OriginalThing` 11; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Falumpaset` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Fambaa` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Fanback` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Felinoid_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `FeralGrazer` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `FeralNerf` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `FrilledGorg` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `FrogDog` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Gelagrub` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Gizka` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Glitterstim` | ThingDef | 7 | `li/drugs/li/drug` 4; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Gorg` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Gorg_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Gornt` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Gornt_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `GraniteSlug` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Grank` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Grazer` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `GreaterKraytDragon` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `GreenMilk` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Gualaar` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Gullipud` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Gundark` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `GundarkSkull` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Gutkurr` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `HarvesterBeetle` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Hawkbat` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Horax` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `HoraxMaw` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Hrumph` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Hssiss` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Igitz` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Insectile_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Insectomorph` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Iriaz` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `IridonianReek` | ThingDef | 7 | `li/BS_scribedCache/li/BS_OriginalThing` 3; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `IthorianReek` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Jakobeast` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `JakobeastHorn` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Jamel` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `JiRikknit` | ThingDef | 7 | `li/drugs/li/drug` 4; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Jimvu` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `JungleRancor` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Kaadu` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Katarn` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `KellDragon` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Kinrath` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Klorslug` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `KowakianMonkeyLizard` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `KraytDragon` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `KraytDragonHorn` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `KraytDragonSkull` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `KraytPearl` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Krayt_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Kreetle` | BodyDef | 7 | `li/BS_scribedCache/li/BS_OriginalThing` 1; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `worldPawns/pawnsAlive/li/def` 1; `worldPawns/pawnsAlive/li/kindDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Krykna` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `KwazelMaw` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Kwi` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Kybuck` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `LavaFlea` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Leaftail` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Leather_Bantha` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Bright` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Crustapod` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Dark` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `li/precepts/li/stuff` 1 |
| mlie.starwarsanimalcollection | `Leather_Fambaa` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `wornApparel/innerList/li/stuff` 1 |
| mlie.starwarsanimalcollection | `Leather_Felinoid` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `wornApparel/innerList/li/stuff` 1 |
| mlie.starwarsanimalcollection | `Leather_Gundark` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Horax` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Insectile` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Insectine` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_KraytDragon` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_LavaFlea` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `wornApparel/innerList/li/stuff` 1 |
| mlie.starwarsanimalcollection | `Leather_Mammavian` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `wornApparel/innerList/li/stuff` 1 |
| mlie.starwarsanimalcollection | `Leather_Nerf` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Rancor` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Reptavian` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_ReptoFur` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Reptomammal` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Roggwart` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Ronto` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Rycrit` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Saurian` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_SoftFur` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Testudine` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Tough` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Vapaad` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Wampa` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `wornApparel/innerList/li/stuff` 1 |
| mlie.starwarsanimalcollection | `Leather_Wraid` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Leather_Zakkeg` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `LongtailGorg` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `LothWolf` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Lothcat` | ThingDef | 7 | `li/BS_scribedCache/li/BS_OriginalThing` 1; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `worldPawns/pawnsAlive/li/def` 1; `worldPawns/pawnsAlive/li/kindDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Lylek` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Maalraas` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Mammavian_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Manka` | BodyDef | 6 | `li/BS_scribedCache/li/BS_OriginalThing` 2; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `MankaTooth` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `MarshHaunt` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Massiff` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `MastiffPhalone` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Mastmot` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `MastmotTusk` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Mawvorr` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Mott` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Mudhorn` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `MudhornSkull` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `MunchFungusBread` | ThingDef | 6 | `li/filter/allowedDefs/li` 3; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Mynock` | BodyDef | 5 | `li/BS_scribedCache/li/BS_OriginalThing` 1; `li/packUpFilter/allowedDefs/li` 1; `worldPawns/pawnsAlive/li/def` 1; `worldPawns/pawnsAlive/li/kindDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Narglatch` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Neebray` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Nerf` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `NerfHorn` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Nerf_Meat` | ThingDef | 11 | `li/filter/allowedDefs/li` 6; `li/npcSubmittedContracts/li/item` 2; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Nexu` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `NexuTongue` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Nuna` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Ollopom` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Orray` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Pachydermoid_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `PaintedSpat` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `PekoPeko` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Pikobis` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Plant_Bloddle` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_Bubblespore` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_Bubblespore_Wild` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_Chakroot` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_Chakroot_Wild` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_Dantuber` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_Dantuber_Wild` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_FelucianGlowspore` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_FelucianGlowspore_Wild` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_HubbaGourd` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_HubbaGourd_Wild` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_HydenockTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_HydenockTree_Wild` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_JoganTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_JoganTree_Wild` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_ManaxFungus` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_Meiloorun` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_Meiloorun_Wild` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_MujaFruit` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_MujaFruit_Wild` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_MunchFungus` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_MunchFungus_Wild` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_Nysyllin` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_Nysyllin_Wild` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_TookeTrap` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Plant_TookeTrap_Wild` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| mlie.starwarsanimalcollection | `Porg` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Pufferpig` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Qormot` | BodyDef | 7 | `li/BS_scribedCache/li/BS_OriginalThing` 3; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Rancor` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `RancorSkull` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `RancorTooth` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Rancor_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `RawBloddle` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `RawBubblespore` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `RawChakroot` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `RawDantuber` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `RawFelucianLettuce` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `RawHubbaGourd` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `RawJoganFruit` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `RawManaxFungus` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `RawMeiloorun` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `RawMujaFruit` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `RawMunchFungus` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `RawNysyllin` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `RawTookeTrapRoot` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Raxshir` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Reek` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Reptavian_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Reptomammal_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Rikknit` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `RikknitOvum` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Rodentia_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Roggwart` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Ronto` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Ronto_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Runyip` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Rycrit` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Rycrit_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `SW_Calamity` | AbilityDef | 2 | `abilities/abilities/li/def` 2 |
| mlie.starwarsanimalcollection | `SW_ForcePushprojectile` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| mlie.starwarsanimalcollection | `SW_Spitprojectile` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| mlie.starwarsanimalcollection | `SW_WebShotprojectile` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| mlie.starwarsanimalcollection | `SarlaccPit` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `SarlacciSpore` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Saurian_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Scavrat` | BodyDef | 14 | `li/BS_scribedCache/li/BS_OriginalThing` 3; `li/things/thing/def` 3; `li/things/thing/kindDef` 3; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1; `hediffs/li/part/body` 1 |
| mlie.starwarsanimalcollection | `Scurrier` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Shaak` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Shiro` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `ShiroTrap` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Shyrack` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Silica_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Silooth` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Skalder` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `SkalderTusk` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Sketto` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Snoruuk` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Squall` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Stintaril` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Strill` | BodyDef | 5 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `li/precepts/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Tach` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `TachGland` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Taozin` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `TaozinNodule` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `TarisianAle` | ThingDef | 7 | `li/drugs/li/drug` 4; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Tauntaun` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `TeeMuss` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Tender_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `TetnissCrab` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Thranta` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Tibidee` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Tooke` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Torton` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Tough_Meat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Tukata` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `TukataSpike` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `TuskCat` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Urusai` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Uvak` | ThingDef | 6 | `li/BS_scribedCache/li/BS_OriginalThing` 2; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Vapaad` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Varactyl` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Veermok` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Voorpak` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Vornskyr` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Vulptex` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Wampa` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `WampaSkull` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `WarWyrm` | BodyDef | 15 | `hediffs/li/part/body` 5; `li/BS_scribedCache/li/BS_OriginalThing` 2; `worldPawns/pawnsAlive/li/def` 2; `worldPawns/pawnsAlive/li/kindDef` 2; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `WarWyrmSkull` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Warbird` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Whisperbird` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `WompRat` | ThingDef | 10 | `li/BS_scribedCache/li/BS_OriginalThing` 2; `worldPawns/pawnsAlive/li/def` 2; `worldPawns/pawnsAlive/li/kindDef` 2; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `WoolBantha` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceModifiers/keys/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `WoolCoarse` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceModifiers/keys/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `WoolMastmot` | ThingDef | 5 | `li/packUpFilter/allowedDefs/li` 1; `li/priceModifiers/keys/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `wornApparel/innerList/li/stuff` 1 |
| mlie.starwarsanimalcollection | `WoolNerf` | ThingDef | 5 | `li/packUpFilter/allowedDefs/li` 1; `li/priceModifiers/keys/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `wornApparel/innerList/li/stuff` 1 |
| mlie.starwarsanimalcollection | `WoolTaozin` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceModifiers/keys/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `WoolWyyyschokk` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceModifiers/keys/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `Woolamander` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Worrt` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Wraid` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Wyyyschokk` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Yobshrimp` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Zakkeg` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `Zeer` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| mlie.starwarsanimalcollection | `sw_Apparel_KrathWarMask` | ThingDef | 7 | `li/filter/allowedDefs/li` 4; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `sw_Bantha` | IdeoIconDef | 1 | `ideoManager/ideos/li/iconDef` 1 |
| mlie.starwarsanimalcollection | `sw_DeadSarlacc` | LandmarkDef | 7 | `landmarks/values/li/def` 7 |
| mlie.starwarsanimalcollection | `sw_JediGray` | IdeoIconDef | 1 | `ideoManager/ideos/li/iconDef` 1 |
| mlie.starwarsanimalcollection | `sw_JediNova` | IdeoIconDef | 1 | `ideoManager/ideos/li/iconDef` 1 |
| mlie.starwarsanimalcollection | `sw_OnderonRoyalty` | IdeoIconDef | 1 | `ideoManager/ideos/li/iconDef` 1 |
| mlie.starwarsanimalcollection | `sw_Pentastar` | IdeoIconDef | 1 | `ideoManager/ideos/li/iconDef` 1 |
| mlie.starwarsanimalcollection | `sw_Sarlacc` | LandmarkDef | 8 | `landmarks/values/li/def` 8 |
| mlie.starwarsanimalcollection | `sw_SithExarKun` | IdeoIconDef | 1 | `ideoManager/ideos/li/iconDef` 1 |
| mlie.starwarsanimalcollection | `swfish_Burra` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `swfish_Dactopus` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `swfish_Daggert` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `swfish_Doshianjelly` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `swfish_Faa` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `swfish_FleekEel` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `swfish_Laa` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `swfish_Nyork` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `swfish_PaddyFrog` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `swfish_Ray` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `swfish_See` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| mlie.starwarsanimalcollection | `swfish_SinkCrab` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_AcanthamoebaGiganteaHuge` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_AcanthamoebaGiganteaLarge` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_AcanthamoebaGiganteaSmall` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_AcidBolt` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_AcidicVomit` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_AcidicWeb` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Aerofleet` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_AerofleetMeat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_AgariluxRawFungus` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Agaripawn` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_AgaripawnSpores` | ThingDef | 9 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Agaripod` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_AgaripodSpores` | ThingDef | 9 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_AlienGrass` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `AA_AlienTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `AA_AngelMoth` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_AngelMothEggFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_AngelMothLarva` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_AnimaColossus` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Animalisk` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_AnimaliskEggFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_AnimusVox` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_ArcticLion` | PawnRenderTreeDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_ArcticLion_Leather` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Atispec` | BodyDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_AtispecEggFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_AtispecEggUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_AuroraSylph` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Barbslinger` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_BedBug` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_BedBugEggFertilized` | ThingDef | 9 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_BedBugEggUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Behemoth` | ThingDef | 9 | `li/BS_scribedCache/li/BS_OriginalThing` 5; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_BioMechDisruptor` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_BlackCreeper` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_BlackDefiler` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_BlackDefiler_Gun` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_BlackDefiler_Projectile` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_BlackHive` | FactionDef | 1 | `components/li/ignoredFactions/li` 1 |
| sarg.alphaanimals | `AA_BlackHiveBolt` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_BlackInsectJelly` | ThingDef | 8 | `li/filter/allowedDefs/li` 5; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_BlackJellyMorpher` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_BlackJellyWall` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_BlackScarab` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_BlackSpelopede` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_BlackSpider` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_BlackTruffles` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Blizzarisk` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_BlizzariskClutchMother` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_BlizzariskEggFertilized` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_BlizzariskSuperEggFertilized` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_BloodShrimp` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_BlueGel` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_BlueGelBattery` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_BlueMilk` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Bobeene` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_BoulderMit` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Bullet_Barb` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Bullet_Rock` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Bullet_VenomBarb` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Bumbledrone` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_BumbledroneHierophant` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_BumbledroneQueen` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_BumbledroneQueenEggFertilized` | ThingDef | 9 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_ButterflyEggUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Cactipine` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_CactipineQuill` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_CactusMeat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_ChameleonYak` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_ChameleonYakWoolDesert` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceModifiers/keys/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_ChameleonYakWoolJungle` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceModifiers/keys/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_ChameleonYakWoolTemperate` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceModifiers/keys/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_ChameleonYakWoolWinter` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceModifiers/keys/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_ChemfuelMyrmidon` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_CinderSilk` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Cinderlisk` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_CinderliskEggFertilized` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_ColossalAerofleet` | PawnRenderTreeDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_CrepuscularBeetle` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_CrepuscularBeetleEggFertilized` | ThingDef | 9 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_CrepuscularBeetleEggUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_CrescendoAnole` | PawnRenderTreeDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_CrystalMit` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_CrystallineCaracal` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_DarkBolt` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_DarkGlowPod` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_DarkGlowPodFormation` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_DarkLargeGlowPod` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_DarkVandal` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Darkbeast` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_DecayDrake` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_DesertAve` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_DevilSheep` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_DisgustingMealNutrientPaste` | ThingDef | 10 | `li/filter/allowedDefs/li` 7; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Drainer` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_DrainerEggFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_DrainerLarva` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Dunealisk` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_DunealiskClutchMother` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_DunealiskEggFertilized` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_DunealiskSuperEggFertilized` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_DuskProwler` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_DuskRat` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_EggCrescendoAnoleFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_EggCrescendoAnoleUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_EggDesertAveFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_EggFlamingoPhoenixFertilized` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_EggGiantCrownedSilkieFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_EggGiantCrownedSilkieUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_EggMeadowAveFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_EggMeadowAveUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_EggNightAveFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_EggNightlingFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_EggNightlingUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_EggPedigreedRaptorFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_EggPedigreedRaptorUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_EggRoughPlatedMonitorFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_EggRoyalAveFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_ElectricBolt` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_EmpressButterfly` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_EmpressButterflyEggFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_EmpressButterflyLarva` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_EngorgedTentacularAberration` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Erin` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_EyeBody` | BodyDef | 1 | `hediffs/li/part/body` 1 |
| sarg.alphaanimals | `AA_Eyeling` | ThingDef | 10 | `li/BS_scribedCache/li/BS_OriginalThing` 2; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `worldPawns/pawnsAlive/li/def` 1; `worldPawns/pawnsAlive/li/kindDef` 1; `autoSlaughterManager/configs/li/animal` 1; `li/things/thing/def` 1; `li/things/thing/kindDef` 1 |
| sarg.alphaanimals | `AA_Feralisk` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_FeraliskClutchMother` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_FeraliskEggFertilized` | ThingDef | 9 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_FeraliskEggUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_FeraliskSuperEggFertilized` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_FilthSlimyPuke` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Filth_BlackJelly` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Filth_BlueBlood` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Filth_RedSlime` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Filth_Slime` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_FireSpit` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_FireWasp` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_FireWaspEggFertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_FireWaspEggUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_FireWeb` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_FissionMouse` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_FissionMouseSecond` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_FissionMouseThird` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_FlamingoPhoenix` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_FoamBelcher` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_FoamBelcher_Gun` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_FreezePod` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_FrostAve` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_FrostBolt` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_FrostLynx` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_FrostPuff` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_FrostWeb` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_FrostboundBehemoth` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Frostling` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Frostmite` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_FungalHusk` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Gallatross` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_GallatrossHorn` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_GallatrossMoribund` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_GazeAttack` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Genix` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_GiantCrownedSilkie` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_GiantCrownedSilkieSilk` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceModifiers/keys/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Gigantelope` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_GowMilk` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_GreatDevourer` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_GreatDevourerEggFertilized` | ThingDef | 9 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_GreatDevourerEggUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_GreaterBlackHiveBolt` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_GreenGoo` | PawnRenderTreeDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_GreyCoatedMouflon` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_GreyCoatedMouflonWool` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceModifiers/keys/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Groundrunner` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Heat_Ambrosia` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `AA_Helixien` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_HexaGelBattery` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Hexagel` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_HexagelCore` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_HexagelCoreReactor` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_HugeAnimaPearl` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_IncendiaryMote` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_InfectedAerofleet` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_IronhuskBeetle` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_IronhuskEggFertilized` | ThingDef | 9 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_IronhuskEggUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Junglelisk` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_JungleliskEggFertilized` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_LarvalAtispec` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_LaserBullet` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Leather_Aerofleet` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Leather_Behemoth` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Lockjaw` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Locusts` | BodyDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_LuciferBug` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_MammothWorm` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_MammothWormEggFertilized` | ThingDef | 9 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_MammothWormEggUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Mantrap` | PawnRenderTreeDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_MatureFleshbeast` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_MeadowAve` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_MegaLouse` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_MegalouseEggFertilized` | ThingDef | 9 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_MegalouseEggUnfertilized` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Metallovore` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Mime` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_MothSilk` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Murkling` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_MutantArm` | HediffDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_MutantEye` | HediffDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_MutantLeg` | HediffDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_MycoidColossus` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_MycoidColossusSpores` | ThingDef | 9 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Needlepost` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Needleroll` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_NightAve` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_NightMilk` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_NightMule` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_NightRam` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_NightWool` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceModifiers/keys/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Nightling` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_OcularCactus` | ThingDef | 3 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_OcularGas` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_OcularJelly` | PawnRenderTreeDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_OcularJellyMeat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_OcularNightling` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_OvergrownColossus` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_PebbleMit` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_PedigreedRaptor` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_PhoenixOwlcat` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Plant_PollenTrumpet` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `AA_Plasma` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Plasmorph` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_PoisonBolt` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_PsyWeb` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Quill` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Radyak` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_RandomBricks` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_RandomStones` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_RaptorShrimp` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Ravager` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_RayHound` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Razorjack` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_RedGas` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_RedGoo` | PawnRenderTreeDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_RedLeaves` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `AA_RedPlantsTall` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `AA_RedPoisonBolt` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_RedSpore` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_RipperHound` | PawnRenderTreeDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_RottingMound` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `AA_RottingMoundItem` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_RoughPlatedMonitor` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_RoyalAve` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_SandLion` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_SandLion_Leather` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_SandProwler` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_SandPuff` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_SandSquid` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_ShadowCharger` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_ShockGoat` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Skiphound` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_SkySteel` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_SkySteelClumps` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Skyeel` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Slurrypede` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_SmallButterfly` | BodyDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_SmokeInk` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_SpinedGow` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_SummitCrab` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Swarmling` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_TarGuzzler` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_TeratogenicOriginator` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Terramorph` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_TetraSlug` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_TheHeuristicEye` | HediffDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_TheMeretriciousEye` | HediffDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_TheNumbingEye` | HediffDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_TheOmniscientEye` | HediffDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_TheQuiescentEye` | HediffDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_TheRecalcitrantEye` | HediffDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_TheSpasmodicEye` | HediffDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Thermadon` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Thunderbeast` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_Thunderox` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_UnblinkingEye` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_UraniumCrystals` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `AA_Web` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Wildpawn` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_WildpawnSpores` | ThingDef | 9 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_Wildpod` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_WildpodSpores` | ThingDef | 9 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AA_WindBeast` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `AA_WindBolt` | AbilityDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `AB_RawRedSlime` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Blueprint_AA_BlackDefiler` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Blueprint_AA_BlackJellyWall` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Blueprint_AA_BlueGelBattery` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Blueprint_AA_FoamBelcher` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Blueprint_AA_HexaGelBattery` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Blueprint_AA_HexagelCoreReactor` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Blueprint_Install_AA_BlackDefiler` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Blueprint_Install_AA_BlackJellyWall` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Blueprint_Install_AA_BlueGelBattery` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Blueprint_Install_AA_FoamBelcher` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Blueprint_Install_AA_HexaGelBattery` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Blueprint_Install_AA_HexagelCoreReactor` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Blueprint_Install_VFEI2_AA_ArtificialBlackHive` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Blueprint_Install_VFEI2_BlackInsectoidCocoon` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Blueprint_VFEI2_AA_ArtificialBlackHive` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Corpse_AA_AcanthamoebaGiganteaHuge` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_AcanthamoebaGiganteaLarge` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_AcanthamoebaGiganteaSmall` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Aerofleet` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Agaripawn` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Agaripod` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_AngelMoth` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_AngelMothLarva` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_AnimaColossus` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Animalisk` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_AnimusVox` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_ArcticLion` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Atispec` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_AuroraSylph` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_Barbslinger` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_BedBug` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_Behemoth` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_BlackScarab` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_BlackSpelopede` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_BlackSpider` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_Blizzarisk` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_BlizzariskClutchMother` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_BloodShrimp` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Bobeene` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_BoulderMit` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Bumbledrone` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_BumbledroneHierophant` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_BumbledroneQueen` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_Cactipine` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_ChameleonYak` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_ChemfuelMyrmidon` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_Cinderlisk` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_ColossalAerofleet` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_CrepuscularBeetle` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_CrescendoAnole` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_CrystalMit` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_CrystallineCaracal` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_DarkVandal` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Darkbeast` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_DecayDrake` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_DesertAve` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_DevilSheep` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Drainer` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_DrainerLarva` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_Dunealisk` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_DunealiskClutchMother` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_DuskProwler` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_DuskRat` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_EmpressButterfly` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_EmpressButterflyLarva` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_EngorgedTentacularAberration` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Erin` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Eyeling` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Feralisk` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_FeraliskClutchMother` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_FireWasp` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_FissionMouse` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_FissionMouseSecond` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_FissionMouseThird` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_FlamingoPhoenix` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_FrostAve` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_FrostLynx` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_FrostboundBehemoth` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_Frostling` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Frostmite` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_FungalHusk` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Gallatross` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_GallatrossMoribund` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Genix` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_GiantCrownedSilkie` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Gigantelope` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_GreatDevourer` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_GreenGoo` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_GreyCoatedMouflon` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Groundrunner` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Helixien` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_InfectedAerofleet` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_IronhuskBeetle` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_Junglelisk` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_LarvalAtispec` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_Lockjaw` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Locusts` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_LuciferBug` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_MammothWorm` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_Mantrap` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_MatureFleshbeast` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_MeadowAve` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_MegaLouse` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_Metallovore` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Mime` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Murkling` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_MycoidColossus` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Needlepost` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Needleroll` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_NightAve` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_NightMule` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_NightRam` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Nightling` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_OcularJelly` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_OcularNightling` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_OvergrownColossus` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_PebbleMit` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_PedigreedRaptor` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_PhoenixOwlcat` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Plasmorph` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Radyak` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_RaptorShrimp` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Ravager` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_RayHound` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Razorjack` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_RedGoo` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_RedSpore` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_RipperHound` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_RoughPlatedMonitor` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_RoyalAve` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_SandLion` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_SandProwler` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_SandSquid` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_ShadowCharger` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_ShockGoat` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Skiphound` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Skyeel` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Slurrypede` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_SmallButterfly` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_SpinedGow` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_SummitCrab` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Swarmling` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_TarGuzzler` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_TeratogenicOriginator` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Terramorph` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_TetraSlug` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Thermadon` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_AA_Thunderbeast` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Thunderox` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_UnblinkingEye` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Wildpawn` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_Wildpod` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_AA_WindBeast` | ThingDef(engine) | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphaanimals | `Corpse_VFEI2_BlackEmpress` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_VFEI2_BlackQueen` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `Corpse_VFEI2_BlackSwarmling` | ThingDef(engine) | 7 | `li/filter/allowedDefs/li` 7 |
| sarg.alphaanimals | `FF_FlameBreathAnimated` | VEF.Weapons.ExpandableProjectileDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Frame_AA_BlackDefiler` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Frame_AA_BlackJellyWall` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Frame_AA_BlueGelBattery` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Frame_AA_FoamBelcher` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Frame_AA_HexaGelBattery` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Frame_AA_HexagelCoreReactor` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Frame_VFEI2_AA_ArtificialBlackHive` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `GU_RedWood` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Leather_BlackChitin` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Leather_Cactus` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `li/npcSubmittedContracts/li/item` 1 |
| sarg.alphaanimals | `Leather_Chitin` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Leather_Gallatross` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Leather_IronChitin` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Leather_Night` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Leather_RaptorPlates` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_ArcticLion` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_Atispec` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_Behemoth` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_BoulderMit` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_DevilSheep` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphaanimals | `Meat_AA_Frostling` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_Gallatross` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_Gigantelope` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_Groundrunner` | ThingDef(engine) | 10 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `li/npcSubmittedContracts/li/item` 1 |
| sarg.alphaanimals | `Meat_AA_Helixien` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_MeadowAve` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_NightMule` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_Nightling` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_OvergrownColossus` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_RaptorShrimp` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_Razorjack` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_RipperHound` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_RoughPlatedMonitor` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_SandSquid` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `Meat_AA_Skyeel` | ThingDef(engine) | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `VFEI2_AA_ArtificialBlackHive` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `VFEI2_BlackEmpress` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `VFEI2_BlackQueen` | ThingDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `VFEI2_BlackSwarmling` | PawnRenderTreeDef | 4 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphaanimals | `VFEI2_PherocoreBlack` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphaanimals | `VFEI2_Thumper_BlackEmpress` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Aaklac` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_AbandonedShipPart` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_AgaricusDomeCap` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_Agarilux` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_AlcyoniteChunk` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_AlcyoniteSolar` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_AlcyoniteSolar_Advanced` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_AlienComplianceCenter` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_AlienGrass` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_AlienTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_AlienTree_Polluted` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_AncientBone_Stuff` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_ArbuscularMycorrhiza` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_AsphaltBucket` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_BlocksCragstone` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_BlocksMudstone` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_BlocksObsidian` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_BloodBouquet` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_BlueRawFungus` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_BoneDistillery` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_BoneWall` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_BrownBarrelCactus` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_Bryolux` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_Bullet_Shell_Tar` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_BumbledroneFood` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_CordaxResin` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_CoreDrill` | WorkGiverDef | 9 | `li/Priorities/li/Workgiver` 9 |
| sarg.alphabiomes (report) | `AB_CoreSampleDrill` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Cragstone` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_CrystalFlower` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_CrystalHorn` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_CrystalWood` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_DeadBowerTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_DerelictBeachUmbrella` | KCSG.SymbolDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_DerelictRecliner` | KCSG.SymbolDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_DessertTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_DoBillsCook` | WorkGiverDef | 9 | `li/Priorities/li/Workgiver` 9 |
| sarg.alphabiomes (report) | `AB_DoBillsMachiningTable` | WorkGiverDef | 9 | `li/Priorities/li/Workgiver` 9 |
| sarg.alphabiomes (report) | `AB_DoBillsMakeWeapons` | WorkGiverDef | 9 | `li/Priorities/li/Workgiver` 9 |
| sarg.alphabiomes (report) | `AB_DoBillsSmelter` | WorkGiverDef | 9 | `li/Priorities/li/Workgiver` 9 |
| sarg.alphabiomes (report) | `AB_DribblingCap` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_EuphorbiaDesiccata` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_EuphorbiaRimworldia` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_ExoticAutoDoor` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_ExoticColumn` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_ExoticDoor` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_ExoticWall` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_EyeGrass` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_FanPalm` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_FeraliskInfestedJungle` | BiomeDef | 2 | `worldGenerationData/biomeCommonalities/keys/li` 1; `worldGenerationData/biomeScoreOffsets/keys/li` 1 |
| sarg.alphabiomes (report) | `AB_Filth_Propane` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_Filth_Tar` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_FirevineTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_FlashFrozenTree` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_FleshTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_Flowers` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_FrostLeaf` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GallatrossGraveyard` | BiomeDef | 2 | `worldGenerationData/biomeCommonalities/keys/li` 1; `worldGenerationData/biomeScoreOffsets/keys/li` 1 |
| sarg.alphabiomes (report) | `AB_GargantuanLithops` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GelatinousSuperorganism` | BiomeDef | 2 | `worldGenerationData/biomeCommonalities/keys/li` 1; `worldGenerationData/biomeScoreOffsets/keys/li` 1 |
| sarg.alphabiomes (report) | `AB_GiantAgariTox` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GiantAgarilux` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GiantFlower` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GiantGamma` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GiantSeeds` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_GiantSeptimum` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GiantStikehr` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GiantSunflower` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GiantToxicFlower` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GiantTulip` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GlobularPlant` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GlobularPlant_Polluted` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GlowingAgarilux` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GlowingGrass` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_Glowstool` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GoldenCubeTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_Gomphoeria` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_GreenRockFern` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_HalfAlienTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_HardyGrass` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_Iashiphus` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_JungleTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_JungleTree_Polluted` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_KeeningCordax` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_LandCoral` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_LargeSlimyTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_LilacBeacon` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_LuminescentTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_MagmaMote` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_MagmaThermalPlant` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_MagmaticQuagmire` | LandmarkDef | 3 | `landmarks/values/li/def` 3 |
| sarg.alphabiomes (report) | `AB_MangrovePalm` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_MangroveTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_Mech_RuinedActivator` | KCSG.SymbolDef | 10 | `li/things/thing/def` 8; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Mech_RuinedAssembler` | KCSG.SymbolDef | 15 | `li/things/thing/def` 13; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Mech_RuinedCapsule` | KCSG.SymbolDef | 15 | `li/things/thing/def` 13; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Mech_RuinedCell` | KCSG.SymbolDef | 14 | `li/things/thing/def` 12; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Mech_RuinedLargeGunPlatform` | KCSG.SymbolDef | 7 | `li/things/thing/def` 5; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Mech_RuinedMortar_Full` | KCSG.SymbolDef | 8 | `li/things/thing/def` 6; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Mech_RuinedMortar_Single` | ThingDef | 8 | `li/things/thing/def` 6; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Mech_RuinedShield` | KCSG.SymbolDef | 8 | `li/things/thing/def` 6; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Mech_RuinedTurret_Full` | KCSG.SymbolDef | 18 | `li/things/thing/def` 16; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Mech_RuinedTurret_Single` | KCSG.SymbolDef | 8 | `li/things/thing/def` 6; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_MechanoidIntrusion` | BiomeDef | 2 | `worldGenerationData/biomeCommonalities/keys/li` 1; `worldGenerationData/biomeScoreOffsets/keys/li` 1 |
| sarg.alphabiomes (report) | `AB_MechanoidReceiver` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_MiasmicMangrove` | BiomeDef | 2 | `worldGenerationData/biomeCommonalities/keys/li` 1; `worldGenerationData/biomeScoreOffsets/keys/li` 1 |
| sarg.alphabiomes (report) | `AB_Mudstone` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_MushroomWoodLog` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_MycoticCollector` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_MycoticJungle` | BiomeDef | 2 | `worldGenerationData/biomeCommonalities/keys/li` 1; `worldGenerationData/biomeScoreOffsets/keys/li` 1 |
| sarg.alphabiomes (report) | `AB_MycoticSpores` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_NeutroamineSynthetizer` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_ObsidianSpire` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Obsidianstone` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_OcularForest` | BiomeDef | 2 | `worldGenerationData/biomeCommonalities/keys/li` 1; `worldGenerationData/biomeScoreOffsets/keys/li` 1 |
| sarg.alphabiomes (report) | `AB_OcularGas` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_OcularGasSpewer` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_ParasiticMangrove` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_PinkRawFungus` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_PollutedStikehr` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_Propane` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_PropaneDrain` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_PropaneFueledSmithy` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_PropaneHeater` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_PropaneLakes` | BiomeDef | 2 | `worldGenerationData/biomeCommonalities/keys/li` 1; `worldGenerationData/biomeScoreOffsets/keys/li` 1 |
| sarg.alphabiomes (report) | `AB_PropanePipe` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_PropanePipe_Underground` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_PropanePump` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_PropaneSmelter` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_PropaneStorage` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_PropaneStove` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_PropaneTableMachining` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_PropaneTap` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Propane_Valve` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_PsychotropicFungus` | ThingDef | 15 | `li/filter/allowedDefs/li` 8; `li/drugs/li/drug` 4; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_PurpleRawFungus` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_PyroclasticConflagration` | BiomeDef | 2 | `worldGenerationData/biomeCommonalities/keys/li` 1; `worldGenerationData/biomeScoreOffsets/keys/li` 1 |
| sarg.alphabiomes (report) | `AB_QuicksandPits` | LandmarkDef | 1 | `landmarks/values/li/def` 1 |
| sarg.alphabiomes (report) | `AB_RavenNettle` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_RawBloodBouquet` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_RawBrownBarrelCactus` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_RawCrystalHorn` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_RawFrostLeaf` | ThingDef | 8 | `li/filter/allowedDefs/li` 6; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_RawIashiphus` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_RawRagadast` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_RawRimeNodules` | ThingDef | 7 | `li/drugs/li/drug` 4; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_RawSlime` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_RawSugarFamewort` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_RawTentacularFruit` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_RecurvedStropharia` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_RedBugloss` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_RedLeaves` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_RedPlantsTall` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_RimeNodules` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_RockyCrags` | BiomeDef | 2 | `worldGenerationData/biomeCommonalities/keys/li` 1; `worldGenerationData/biomeScoreOffsets/keys/li` 1 |
| sarg.alphabiomes (report) | `AB_RustedWall` | KCSG.SymbolDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_SessileMechanoid` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_ShackledGamma` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Shell_Tar` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_SlagRubble` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_SlimeCompressor` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_SlimeMeal` | ThingDef | 11 | `li/filter/allowedDefs/li` 8; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_SlimeStone` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_Slimecasia` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_SlimyFern` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_SlimyPholiota` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_SlimyTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_SmoothedAncientMetals` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_SmoothedCragstone` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_SmoothedMudstone` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_SmoothedObsidian` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_SmoothedSlimeStone` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_SugarChunk` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_SugarFamewort` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_TallSlimyGrass` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_TangleTea` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_TarLakes` | LandmarkDef | 7 | `landmarks/values/li/def` 7 |
| sarg.alphabiomes (report) | `AB_TarMote` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_TarPits` | BiomeDef | 2 | `worldGenerationData/biomeCommonalities/keys/li` 1; `worldGenerationData/biomeScoreOffsets/keys/li` 1 |
| sarg.alphabiomes (report) | `AB_TarPump` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_TechnoTree` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_TentacularPlant` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_TinkleGrass` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_ToxiBulb` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_ToxiGrass` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_ToxicGamma` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_TrapIED_Tar` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Turret_Propane` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_Turret_Propane_Bullet` | VEF.Weapons.ExpandableProjectileDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_Turret_Propane_Gun` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_UnshackledCompanionDryad` | ThingDef | 3 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1; `autoSlaughterManager/configs/li/animal` 1 |
| sarg.alphabiomes (report) | `AB_WarpedStonePillar` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_WeaponPoisonDart` | ThingDef | 3 | `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `AB_WeaponPoisonDartProjectile` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `AB_WildRadagast` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `AB_WitchesOyster` | ThingDef | 6 | `li/filter/allowedDefs/li` 6 |
| sarg.alphabiomes (report) | `Blueprint_AB_CoreSampleDrill` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_ExoticColumn` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_ExoticWall` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_MagmaThermalPlant` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_MechanoidReceiver` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_MycoticCollector` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_PropaneDrain` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_PropaneFueledSmithy` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_PropanePipe` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_PropanePipe_Underground` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_PropanePump` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_PropaneSmelter` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_PropaneStove` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_PropaneTableMachining` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_PropaneTap` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_Propane_Valve` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_SlimeCompressor` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_TarPump` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_AB_Turret_Propane` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_AbandonedShipPart` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_BoneWall` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_BumbledroneHive` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_CoreSampleDrill` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_DerelictArchonexusCore` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_DerelictArchotechTower` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_DerelictBeachUmbrella` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_DerelictMajorArchotechStructure` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_DerelictPoolLadder` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_DerelictRecliner` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_DerelictSwimmingPool` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_DirtyBeachBall` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_DirtyPoolFloat` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_ExoticColumn` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_ExoticWall` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_MagmaThermalPlant` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_MagmaVent` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_MechanoidReceiver` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_MycoticCollector` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_PropaneDrain` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_PropaneFueledSmithy` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_PropanePipe` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_PropanePipe_Underground` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_PropanePump` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_PropaneSmelter` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_PropaneStove` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_PropaneTableMachining` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_PropaneTap` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_Propane_Valve` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_RustedWall` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_SlimeCompressor` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_TarHole` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_TarPump` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Blueprint_Install_AB_Turret_Propane` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_CoreSampleDrill` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_ExoticColumn` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_ExoticWall` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_MagmaThermalPlant` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_MechanoidReceiver` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_MycoticCollector` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_PropaneDrain` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_PropaneFueledSmithy` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_PropanePipe` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_PropanePipe_Underground` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_PropanePump` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_PropaneSmelter` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_PropaneStove` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_PropaneTableMachining` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_PropaneTap` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_Propane_Valve` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_SlimeCompressor` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_TarPump` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `Frame_AB_Turret_Propane` | ThingDef(engine) | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `GU_AncientMetals` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `GU_BlocksRoseQuartz` | ThingDef | 2 | `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `GU_RoseQuartz` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `GU_SmoothedQuartz` | ThingDef | 1 | `li/packUpFilter/allowedDefs/li` 1 |
| sarg.alphabiomes (report) | `VCEF_AbyssalEel` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_BloodLeech` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_BorealSardine` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_DuskySprat` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_ForsakenAnglerfish` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_FrigidSwimmer` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_GiantPolarPrawn` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_HabdakLongfin` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_Jellyfungus` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_MudSplasherCarp` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_MutantFlatfish` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_OcularFish` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_PinkBlobfish` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_PropaneBag` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_ShadowFry` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_Slimefish` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_Spiderfish` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_Spinyfish` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
| sarg.alphabiomes (report) | `VCEF_Sturgeon` | ThingDef | 9 | `li/filter/allowedDefs/li` 6; `li/packUpFilter/allowedDefs/li` 1; `li/priceHistoryRecorders/keys/li` 1; `priceHistoryRecorders/values/li/thingDef` 1 |
