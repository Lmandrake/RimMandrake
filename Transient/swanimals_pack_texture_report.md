# swanimals / SWBestiary `...Pack` texture report (2026-10-16)

## Mechanism
No def field names these paths. Every `...Pack` path is **derived by the engine**: for a race with
`<race><packAnimal>true</packAnimal>`, the animal render tree's pack node loads
`Graphic_Multi` at `<body texPath of the active lifeStage/variant> + "Pack"` (north/east/south PNGs, no west).
It is drawn only while the animal carries inventory/caravan load. No C#/comp in `src/` consumes it
(no `Pack` hits in SWBestiary Source). Absent => one `Failed to find any textures at ...Pack` error per
distinct body path at first graphic resolve (the SPAWN_RSW_* FAIL rows in `Transient/l1_round_run2.log`);
a loaded animal would draw the engine's bad-graphic placeholder instead of a pack. Nothing else breaks.

## Why no class (c) fix was applied
The reference is not a def field, so there is nothing to repoint. The only def-side fix would be dropping
`packAnimal` (loses caravan hauling, a gameplay change) or patching the pack node out per race. Neither is
"dead/unneeded", so both are left to the owner; no def edits made.

## (a) Art exists in src - copy needed (art ledger installs; NOT copied)
Same species adult sprite sheet; source is the only Pack set that exists for Bantha. Candidates, owner/art
ledger to confirm they read right on the `BanthaR`/`BanthaV_*` bodies:
for each facing in north,east,south:
- `src/RimStarWars/SWBestiary/Textures/swanimals/Bantha/BanthaPack_<f>.png` -> `.../swanimals/Bantha/BanthaRPack_<f>.png` (logged)
- same source -> `BanthaV_GPack`, `BanthaV_HPack`, `BanthaV_IPack`, `BanthaV_JPack` (variants, not yet logged)
Note: `BanthaPack` is currently used by RSW_Jerba (`swanimals/Bantha/Bantha`). Behemoth, Ronto, Holcorobeus,
Bantha `BanthaW_j` Pack already exist and are fine. Behemoth Pack was copied into SWBestiary by 0c6368c3b
(the earlier log rows for JawaBehemoth_f/mPack predate it).
Nothing else: no Pack PNG exists anywhere in `src/` for any other species (12 `*Pack_south.png` total).

## (b) Pack art never produced - owed (3 facings each: north, east, south)
Each row = missing texture path (relative to Textures/), for every pack-animal race below.
Logged in the donor-off run: Bordok, Brezak, HarvesterBeetle, IthorianReek (+Reek_j), Jamel, Kaadu_m, KellDragon,
Reek, Runyip, Bolotaur, Orray, Blurrg. The rest are the same defect, not yet spawned.

| race | missing path |
|---|---|
| RSW_TelluroxRace | `Things/Pawn/Animal/Tellurox/TelluroxPack` |
| RSW_Bantha | `swanimals/Bantha/BanthaV_GPack` |
| RSW_Bantha | `swanimals/Bantha/BanthaV_HPack` |
| RSW_Bantha | `swanimals/Bantha/BanthaV_IPack` |
| RSW_Bantha | `swanimals/Bantha/BanthaV_JPack` |
| RSW_Bantha | `swanimals/Bantha/BanthaRPack` |
| RSW_Dalgo | `swanimals/Dalgo/DalgoPack` |
| RSW_Fambaa | `swanimals/Fambaa/Fambaa_jPack` |
| RSW_Fambaa | `swanimals/Fambaa/Fambaa_j_SwimmingPack` |
| RSW_Fambaa | `RimStarWars/SWBestiary/Fambaa/FambaaPack` |
| RSW_Fambaa | `swanimals/Fambaa/Fambaa_SwimmingPack` |
| RSW_CorellianHound | `swanimals/CorellianHound/CorellianHoundPack` |
| RSW_Bolotaur | `swanimals/Bolotaur/BolotaurPack` |
| RSW_Gelagrub | `swanimals/Gelagrub/GelagrubPack` |
| RSW_KellDragon | `swanimals/KellDragon/KellDragonPack` |
| RSW_IthorianReek | `swanimals/Reek/Reek_jPack` |
| RSW_IthorianReek | `swanimals/IthorianReek/IthorianReekPack` |
| RSW_Jamel | `swanimals/Jamel/JamelPack` |
| RSW_Eopie | `swanimals/Eopie/EopieAPack` |
| RSW_Eopie | `swanimals/Eopie/EopieBPack` |
| RSW_Eopie | `swanimals/Eopie/EopieCPack` |
| RSW_Eopie | `swanimals/Eopie/EopieDPack` |
| RSW_Eopie | `swanimals/Eopie/EopieEPack` |
| RSW_Eopie | `swanimals/Eopie/Eopie_jPack` |
| RSW_Eopie | `swanimals/Eopie/EopiePack` |
| RSW_TuskCat | `swanimals/TuskCat/TuskCatPack` |
| RSW_Falumpaset | `swanimals/Falumpaset/FalumpasetAPack` |
| RSW_Falumpaset | `swanimals/Falumpaset/FalumpasetBPack` |
| RSW_Falumpaset | `swanimals/Falumpaset/FalumpasetCPack` |
| RSW_Falumpaset | `swanimals/Falumpaset/FalumpasetDPack` |
| RSW_Falumpaset | `swanimals/Falumpaset/FalumpasetEPack` |
| RSW_Falumpaset | `swanimals/Falumpaset/FalumpasetPack` |
| RSW_Orray | `RimStarWars/SWBestiary/Orray/OrrayPack` |
| RSW_Runyip | `swanimals/Runyip/Runyip_jPack` |
| RSW_Runyip | `swanimals/Runyip/Runyip_j_SwimmingPack` |
| RSW_Runyip | `swanimals/Runyip/RunyipPack` |
| RSW_Runyip | `swanimals/Runyip/Runyip_SwimmingPack` |
| RSW_Bordok | `swanimals/Bordok/BordokPack` |
| RSW_Brezak | `swanimals/Brezak/BrezakPack` |
| RSW_TeeMuss | `swanimals/TeeMuss/TeeMussPack` |
| RSW_Tauntaun | `Things/Pawn/Animal/RSW_Tauntaun_Canon/RSW_Tauntaun_CanonPack` |
| RSW_Reek | `swanimals/Reek/Reek_jPack` |
| RSW_Reek | `swanimals/Reek/ReekPack` |
| RSW_HarvesterBeetle | `swanimals/HarvesterBeetle/HarvesterBeetle_jPack` |
| RSW_HarvesterBeetle | `swanimals/HarvesterBeetle/HarvesterBeetlePack` |
| RSW_Shaak | `swanimals/Shaak/ShaakPack` |
| RSW_Kaadu | `swanimals/Kaadu/Kaadu_mPack` |
| RSW_Kaadu | `swanimals/Kaadu/Kaadu_m_SwimmingPack` |
| RSW_Kaadu | `swanimals/Kaadu/Kaadu_fPack` |
| RSW_Kaadu | `swanimals/Kaadu/Kaadu_f_SwimmingPack` |
| RSW_Nerf | `swanimals/Nerf/Nerf_jPack` |
| RSW_Nerf | `swanimals/Nerf/Nerf_mPack` |
| RSW_Nerf | `swanimals/Nerf/Nerf_fPack` |
| RSW_Uvak | `swanimals/Uvak/UvakPack` |
| RSW_Kybuck | `swanimals/Kybuck/KybuckPack` |
| RSW_Mastmot | `swanimals/Mastmot/Mastmot_jPack` |
| RSW_Mastmot | `swanimals/Mastmot/Mastmot_mPack` |
| RSW_Mastmot | `swanimals/Mastmot/Mastmot_fPack` |
| RSW_Mudhorn | `swanimals/Mudhorn/Mudhorn_jPack` |
| RSW_Mudhorn | `swanimals/Mudhorn/MudhornPack` |
| RSW_Skalder | `swanimals/Skalder/SkalderPack` |
| RSW_Skalder | `swanimals/Skalder/Skalder_SwimmingPack` |
| RSW_Dewback | `RimStarWars/SWBestiary/Dewback/DewbackPack` |
| RSW_Gualaar | `RimStarWars/SWBestiary/Gualaar/GualaarPack` |
| RSW_Narglatch | `swanimals/Narglatch/Narglatch_mPack` |
| RSW_Narglatch | `swanimals/Narglatch/Narglatch_fPack` |
| RSW_Dactillion | `swanimals/Dactillion/DactillionPack` |
| RSW_LavaFlea | `swanimals/LavaFlea/LavaFlea_jPack` |
| RSW_LavaFlea | `swanimals/LavaFlea/LavaFleaPack` |
| RSW_Varactyl | `swanimals/Varactyl/VaractylV_EPack` |
| RSW_Varactyl | `swanimals/Varactyl/VaractylV_FPack` |
| RSW_Varactyl | `swanimals/Varactyl/Varactyl_mPack` |
| RSW_Varactyl | `swanimals/Varactyl/Varactyl_fPack` |
| RSW_Blurrg | `Things/Pawn/Animal/RSW_Blurrg/RSW_BlurrgPack` |
| RSW_Thranta | `swanimals/Thranta/ThrantaPack` |
| RSW_RoyalRhino | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/RoyalRhinoBeetle/RoyalRhinoPack` |
| RSW_FoundryBeetle | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/FoundryBeetle/FoundryBeetlePack` |
| RSW_Maxolotl | `swanimals/BiomesTeam/BiomesCore_Things/Animal/Maxolotl/MaxolotlPack` |
| RSW_Sacapillar | `swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/SacaPillar/SacaPillarPack` |

Orray: `RimStarWars/SWBestiary/Orray/OrrayPack` (body at `.../Orray/Orray_{north,east,south}.png`). Blurrg:
`Things/Pawn/Animal/RSW_Blurrg/RSW_BlurrgPack` (body `RSW_Blurrg_{north,east,south}.png`). Both class (b).
Rows for `*_Swimming` / `_j` bodies only matter if that body is drawn with a load (juveniles are not pack-eligible
in practice; owner may waive `_j`/Dessicated).

## Decision owed
Either commission Pack sprites for ~48 races (79 body paths) (each shows saddlebags on the existing body) or decide which species keep
`packAnimal` (e.g. keep only ones that are caravan beasts in the fiction: Bantha, Ronto, Dewback, Eopie, Behemoth...).
