# Live art with no pipeline record, adjudicated (TEXREGEN_UNPROVEN_ASK_THE_SHEETS)

Generated 2026-11-03T12:05:36-0800 at `1dc250ae25` by `src/RimMandrake/Utils/art/unproven_adjudicate.py` from `/mnt/d/ClaudeWork/rimmandrake/scratch/texregen_unproven/audit.json` and `/mnt/d/ClaudeWork/rimmandrake/scratch/texregen_unproven/census/census.json`. Data: `design/RimMandrake/texregen_unproven_adjudication.json`. Every picture the texture audit classes UNPROVEN (no artpipe / install / donor / derived record of its exact bytes), in the def view and on every UNPROVEN roster row, gets one of three verdicts (OWNER_PICKED, HAND_MADE, STAND_IN), keyed on the commit that first brought those bytes into the repo. Meanings and the basis labels: the tool's docstring.

dhash threshold 10/256, measured: `{"resave": {"n": 264, "p50": 2, "p99": 8, "over_max": 2}, "nearest_other_res": {"n": 150, "p05": 2, "p10": 9, "p50": 59, "at_or_under_max": 17}}`

| verdict | pictures |
|---|---|
| OWNER_PICKED | 71 |
| HAND_MADE | 93 |
| STAND_IN | 245 |

| basis | pictures |
|---|---|
| STAND_IN | 245 |
| OWNER_PICKED | 71 |
| OURS_PRELEDGER | 63 |
| HAND_MADE | 15 |
| OURS_RESAVED | 15 |

## By mod

| mod | OWNER_PICKED | HAND_MADE | STAND_IN |
|---|---|---|---|
| Abyss | 2 | 1 | 3 |
| Cauldron | 0 | 1 | 0 |
| Contagion | 0 | 2 | 1 |
| Greentide | 0 | 2 | 2 |
| LanternDeeps | 14 | 3 | 8 |
| LeaningScrub | 0 | 14 | 0 |
| LongShade | 1 | 0 | 2 |
| Miasma | 0 | 1 | 3 |
| Pyrelands | 4 | 3 | 0 |
| ROSTER:RM_Abyss | 2 | 0 | 0 |
| ROSTER:RM_BlueDesert | 6 | 0 | 0 |
| ROSTER:RM_Cauldron | 0 | 1 | 0 |
| ROSTER:RM_FloodedCanyon | 0 | 0 | 2 |
| ROSTER:RM_GelatinousSlime | 2 | 0 | 0 |
| ROSTER:RM_Greentide | 0 | 0 | 2 |
| ROSTER:RM_LanternDeeps | 1 | 0 | 0 |
| ROSTER:RM_Miasma | 2 | 0 | 0 |
| ROSTER:RM_Pyrelands | 1 | 1 | 0 |
| ROSTER:RM_Stillsand | 2 | 0 | 0 |
| ROSTER:RM_TheRot | 1 | 0 | 0 |
| ROSTER:RM_TheScald | 2 | 0 | 0 |
| ROSTER:RM_TheSump | 1 | 0 | 0 |
| ROSTER:RM_TwilightSea | 2 | 0 | 0 |
| ROSTER:RM_Warscar | 0 | 0 | 2 |
| ROSTER:RM_Wastes | 0 | 2 | 0 |
| RustCathedral | 0 | 3 | 1 |
| Stillsand | 0 | 0 | 5 |
| TWIN:RimStarWars/SWBestiary | 13 | 17 | 146 |
| TWIN:RimUtinni/UtinniPatches | 0 | 14 | 12 |
| TerminalBiomes | 15 | 21 | 0 |
| TheForge | 0 | 1 | 0 |
| TheRot | 0 | 3 | 53 |
| TheSump | 0 | 1 | 0 |
| Warscar | 0 | 2 | 3 |

## Where the bytes came from

| pictures | verdict (basis) | evidence |
|---|---|---|
| 156 | STAND_IN (STAND_IN) | bytes from 891c0c76ee: BMT_FAUNA_ABSORPTION_1: script port of 68 biomesteam creatures with the donor mods' own art |
| 45 | STAND_IN (STAND_IN) | bytes from 1213bd07b8: FUNGALFOREST_RAID_MERGE_1: spore kit 'with real art copied from the donor's live Workshop install' |
| 15 | HAND_MADE (OURS_RESAVED) | dhash <= 10/256 from our render |
| 15 | STAND_IN (STAND_IN) | bytes from e3737f3a9e: STAT_NORM_WAVE2_RETIRE_1: port of Cephaloids / VE Succulents / VAE Waste content with its art |
| 15 | HAND_MADE (OURS_PRELEDGER) | bytes from 23b12670b3: SW_SEA_MONSTERS_ART_1: image-model sea-beast art (scavenger swarm, reefback) before the art ledger |
| 14 | OWNER_PICKED (OWNER_PICKED) | bytes from 02ab863c09: Lantern Deeps art wired; owner 2026-09-18: 'We approve all of the art review of Lantern deeps!' |
| 11 | HAND_MADE (HAND_MADE) | bytes from 27b87b5608: faction marks built from the owner's references, then ring-carved by hand |
| 10 | HAND_MADE (OURS_PRELEDGER) | bytes from a9ad6a949e: Art-review platform: 'install every gate-passed render awaiting verdict' |
| 10 | OWNER_PICKED (OWNER_PICKED) | bytes from 37a31bab8e: SW_SEA_MONSTERS_ART_1: abyssal colo + sandos from 'kept mockups' |
| 8 | OWNER_PICKED (OWNER_PICKED) | bytes from 57dd8e8879: SW_SEA_MONSTERS_ART_1: crimson opee, 'west IS the owner's kept mockup' |
| 8 | HAND_MADE (OURS_PRELEDGER) | bytes from fd3439b596: SeaBeasts: Starmaw and Lanternwhale generated (codex $imagegen) before the art ledger |
| 7 | STAND_IN (STAND_IN) | bytes from ae40b6b241: KOTORCORE_ABSORPTION_MISSING_TEXTURES_1: 'Copied the real PNGs from those donor-adjacent mods' |
| 6 | OWNER_PICKED (OWNER_PICKED) | bytes from ee57eaf398: SW_SEA_MONSTERS_ART_1: ShaleGorger 'Four facings from the owner's kept mockup' |
| 6 | STAND_IN (STAND_IN) | bytes from b544ff05fb: BMT_FAUNA_ABSORPTION_1: Rocktooth/Boneblade, 'art copied under swanimals/BiomesTeam/' |
| 5 | STAND_IN (STAND_IN) | dhash <= 10/256 from a donor/vanilla extract |
| 4 | HAND_MADE (OURS_PRELEDGER) | bytes from 853261aa72: SW_SEA_MONSTERS_ART_1: image-model scalefish (mee, faa, laa) before the art ledger |
| 4 | OWNER_PICKED (OWNER_PICKED) | bytes from 8bc82c5d6d: Scorch-fruit candidates for owner review; 0da8422dfc ships the four per his sheet ruling |
| 4 | HAND_MADE (OURS_PRELEDGER) | bytes from 040c99f685: SCARROACH_CATHEDRALROACH_TEXTURES_MISSING_1: 'Generated original 512x512 art for both' |
| 4 | HAND_MADE (OURS_PRELEDGER) | bytes from 43c20c453e: SW_SEA_MONSTERS_ART_1: image-model ThornbackColo facings before the art ledger |
| 4 | HAND_MADE (OURS_PRELEDGER) | bytes from a43c1f0109: ART_REGEN_WAVE4 renders wired |
| 3 | OWNER_PICKED (OWNER_PICKED) | bytes from de490265d3: FORSAKEN_CRAGS_PREDATORS_BUILD_1: 'Art is the owner-approved mockup itself' |
| 3 | STAND_IN (STAND_IN) | bytes from 589fecf3f2: POLLUTED_LANDS_FLORA_PORT_1: 'art copied from the live Workshop install' |
| 3 | STAND_IN (STAND_IN) | bytes from 8062d94d32: SHRUBLAND_SCRAPNEST_BIRDS_1: 'Art/body reuses RSW_Whisperbird's under a new defName and retint' |
| 2 | HAND_MADE (OURS_PRELEDGER) | bytes from 987e369fb0: CAVERNS_PARITY_BUILD_1 wall atlases: 'RGB 100% generated', donor alpha as layout only (owner card) |
| 2 | STAND_IN (STAND_IN) | bytes from 1f993c3fc3: FILTH_ON_NATURAL_TERRAIN_NOOP_1: 'real Core dung-tinted art, copied under this mod's own Textures/' |
| 2 | HAND_MADE (OURS_PRELEDGER) | bytes from d556f6b757: ART_PAINTERLY_RESTORATION_1: EmberGrass 'repainted painterly (Codex)' |
| 2 | HAND_MADE (OURS_PRELEDGER) | bytes from 42cd4d2089: Pyrelands full-review art wave: painterly renders |
| 2 | HAND_MADE (OURS_PRELEDGER) | bytes from 9d4ea39838: 'Wire finished renders' (Foundry tower entrance, salvage cache) |
| 2 | OWNER_PICKED (OWNER_PICKED) | bytes from cec36a2f0b: Gizka: 'dino_v5 is the locked set (owner, 2026-09-17)' |
| 2 | OWNER_PICKED (OWNER_PICKED) | stem 'oommok' ruled in a review sheet's decisions.json |
| 2 | OWNER_PICKED (OWNER_PICKED) | stem 'dorrak' ruled in a review sheet's decisions.json |
| 2 | OWNER_PICKED (OWNER_PICKED) | stem 'rmvekkit' ruled in a review sheet's decisions.json |
| 2 | OWNER_PICKED (OWNER_PICKED) | stem 'rmzhaaz' ruled in a review sheet's decisions.json |
| 2 | OWNER_PICKED (OWNER_PICKED) | stem 'cindermare' ruled in a review sheet's decisions.json |
| 2 | OWNER_PICKED (OWNER_PICKED) | stem 'gappo' ruled in a review sheet's decisions.json |
| 2 | OWNER_PICKED (OWNER_PICKED) | stem 'shulla' ruled in a review sheet's decisions.json |
| 2 | OWNER_PICKED (OWNER_PICKED) | stem 'rmnoolim' ruled in a review sheet's decisions.json |
| 1 | HAND_MADE (HAND_MADE) | script-drawn dark noise, 11 colours: a placeholder in effect (ef61e507f2 names no source) |
| 1 | HAND_MADE (OURS_PRELEDGER) | bytes from cc9c150901: POISONFOREST_RM_MOD_BUILD_1: DarkCrust 'copied ... from the already-generated rutdarkcrust_v1' |
| 1 | HAND_MADE (OURS_PRELEDGER) | image-model style, 12k colours (248f24a28c); no render of it in the artpipe state |
| 1 | HAND_MADE (OURS_PRELEDGER) | image-model style; dhash 17 from our RM_LashA_east render, the same lash (e0823872a5) |
| 1 | HAND_MADE (HAND_MADE) | bytes from 79f3454dc5: GREATBOLE_BARK_EDGE_ART_1: bespoke atlas built cell-for-cell against vanilla Rock_Atlas |
| 1 | HAND_MADE (OURS_PRELEDGER) | bytes from 0d1a84cf57: DEEP_FLORA_RENAME_1: twitching puffer v2 art wired (renders, purple-tinted) |
| 1 | OWNER_PICKED (OWNER_PICKED) | bytes from 42b40b2ae2: Long Shade: 'the 7 owner-kept fills' |
| 1 | STAND_IN (STAND_IN) | bytes from cd06277d89: Stillsand caves: 'wall and glyph art are placeholders, jobs queued' |
| 1 | HAND_MADE (HAND_MADE) | script-drawn green blobs, 6 colours: a placeholder in effect (a86443642b names no source) |
| 1 | HAND_MADE (OURS_PRELEDGER) | bytes from f6c01bf661: art review sheet 2026-09-12: validated creature renders (bytes entered with the sheet) |
| 1 | STAND_IN (STAND_IN) | bytes from 60dfa5177c: FOOTPRINT_TRACK_GRID_1: 'print art is placeholder (artpipe jobs pending)' |
| 1 | HAND_MADE (HAND_MADE) | bytes from 9cabd9ff93: Jawa faction icon redrawn (face in shadow) from the owner's reference |
| 1 | STAND_IN (STAND_IN) | bytes from 58020220bb: RSW_Maguana port: 'Donor art accepted without review on owner ruling' |
| 1 | HAND_MADE (OURS_PRELEDGER) | bytes from 4202352cf5: Opee sprite pilot output (SW_SEA_MONSTERS_ART_1 toolchain) before the art ledger |
| 1 | OWNER_PICKED (OWNER_PICKED) | bytes from b998d027f4: SW_SEA_MONSTERS_ART_1: ColoClawFish 'Four facings from the owner's kept mockup' |
| 1 | OWNER_PICKED (OWNER_PICKED) | bytes from fd81873d50: Moornak, the trio's third entry built the same way as onnik (owner-picked mockup) |
| 1 | OWNER_PICKED (OWNER_PICKED) | bytes from f4b6a37918: Onnik: 'a generated body sprite conformed from the owner's picked mockup' |
| 1 | OWNER_PICKED (OWNER_PICKED) | stem 'bloodropmoth' ruled in a review sheet's decisions.json |
| 1 | OWNER_PICKED (OWNER_PICKED) | stem 'feplantquickgrass' ruled in a review sheet's decisions.json |
| 1 | OWNER_PICKED (OWNER_PICKED) | stem 'chittik' ruled in a review sheet's decisions.json |
| 1 | OWNER_PICKED (OWNER_PICKED) | stem 'sumpmouse' ruled in a review sheet's decisions.json |

## The audit's 'owner sheet decided' class, re-judged

texture_regen_audit.py calls an UNPROVEN picture 'sheet decided' when its stem appears anywhere in a decisions.json. Traced to its bytes, that class is mostly NOT his pick:

- defs: STAND_IN 63, HAND_MADE 37, OWNER_PICKED 17, HAND_MADE + STAND_IN 3, OWNER_PICKED + STAND_IN 1
- roster: HAND_MADE 27, OWNER_PICKED 21, STAND_IN 6

## Every UNPROVEN roster row

| biome | def | verdict | faces | files |
|---|---|---|---|---|
| RM_Stillsand | `RM_Oommok` | OWNER_PICKED | OWNER_PICKED | `src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Oommok/RM_Oommok_north.png`<br>`src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Oommok/RM_Oommok_south.png` |
| RM_Stillsand | `RSW_Gizka` | OWNER_PICKED | OWNER_PICKED | `src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/Gizka/Gizka_north.png`<br>`src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/Gizka/Gizka_south.png` |
| RM_BlueDesert | `RM_Dorrak` | OWNER_PICKED | OWNER_PICKED | `src/RimMandrake/BlueDesert/Textures/Things/Pawn/Animal/RM_Dorrak/RM_Dorrak_north.png`<br>`src/RimMandrake/BlueDesert/Textures/Things/Pawn/Animal/RM_Dorrak/RM_Dorrak_south.png` |
| RM_BlueDesert | `RM_Vekkit` | OWNER_PICKED | OWNER_PICKED | `src/RimMandrake/BlueDesert/Textures/Things/Pawn/Animal/RM_Vekkit/RM_Vekkit_north.png`<br>`src/RimMandrake/BlueDesert/Textures/Things/Pawn/Animal/RM_Vekkit/RM_Vekkit_south.png` |
| RM_BlueDesert | `RM_Zhaaz` | OWNER_PICKED | OWNER_PICKED | `src/RimMandrake/BlueDesert/Textures/Things/Pawn/Animal/RM_Zhaaz/RM_Zhaaz_north.png`<br>`src/RimMandrake/BlueDesert/Textures/Things/Pawn/Animal/RM_Zhaaz/RM_Zhaaz_south.png` |
| RM_Abyss | `RM_Cindermare` | OWNER_PICKED | OWNER_PICKED | `src/RimMandrake/Abyss/Textures/RM_Abyss/Things/Pawn/Animal/RM_Cindermare/RM_Cindermare.png`<br>`src/RimMandrake/Abyss/Textures/RM_Abyss/Things/Pawn/Animal/RM_Cindermare/RM_Cindermare_north.png`<br>`src/RimMandrake/Abyss/Textures/RM_Abyss/Things/Pawn/Animal/RM_Cindermare/RM_Cindermare_south.png` |
| RM_Abyss | `RM_Skarnix` | OWNER_PICKED | OWNER_PICKED | `src/RimMandrake/Abyss/Textures/RM_Abyss/Things/Pawn/Animal/RM_Skarnix/RM_Skarnix.png` |
| RM_Cauldron | `RSW_Mynock` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/ShipVermin/Mynock/Mynock_south.png` |
| RM_Cauldron | `RM_DarkCrust` | HAND_MADE | HAND_MADE | `src/RimMandrake/Cauldron/Textures/Things/Plant/RM_DarkCrust/RM_DarkCrust_a.png` |
| RM_FloodedCanyon | `RSW_Creature_Mantrap` | STAND_IN | STAND_IN | `src/RimStarWars/SWBestiary/Textures/swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/MantrapCreature/Mantrap_east.png`<br>`src/RimStarWars/SWBestiary/Textures/swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/MantrapCreature/Mantrap_north.png`<br>`src/RimStarWars/SWBestiary/Textures/swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/MantrapCreature/Mantrap_south.png` |
| RM_FloodedCanyon | `RM_TwistingThorngrass` | STAND_IN | STAND_IN | `src/RimMandrake/CrackedLands/Textures/Things/Plant/RM_TwistingThorngrass/TwistingThorngrass_b.png`<br>`src/RimMandrake/CrackedLands/Textures/Things/Plant/RM_TwistingThorngrass/TwistingThorngrass_c.png` |
| RM_GelatinousSlime | `RM_Gappo` | OWNER_PICKED | OWNER_PICKED | `src/RimMandrake/GelatinousSlime/Textures/Things/Pawn/Animal/Gappo/RM_Gappo_north.png`<br>`src/RimMandrake/GelatinousSlime/Textures/Things/Pawn/Animal/Gappo/RM_Gappo_south.png` |
| RM_Greentide | `RM_Gristle` | STAND_IN | STAND_IN | `src/RimMandrake/Greentide/Textures/Things/Pawn/Animal/RM_Gristle/RM_Gristle_east.png`<br>`src/RimMandrake/Greentide/Textures/Things/Pawn/Animal/RM_Gristle/RM_Gristle_north.png`<br>`src/RimMandrake/Greentide/Textures/Things/Pawn/Animal/RM_Gristle/RM_Gristle_south.png` |
| RM_Greentide | `RSW_Gizka` | OWNER_PICKED | OWNER_PICKED | `src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/Gizka/Gizka_north.png`<br>`src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/Gizka/Gizka_south.png` |
| RM_Greentide | `RM_Vashuu` | HAND_MADE | HAND_MADE | `src/RimMandrake/Greentide/Textures/Things/Item/Fish/RM_Vashuu.png` |
| RM_GreySea | `RM_Reefback` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/Reefback/Reefback_west.png` |
| RM_GreySea | `RSW_Reefback` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/Reefback/Reefback_west.png` |
| RM_LanternDeeps | `RM_BloodropMoth` | OWNER_PICKED | OWNER_PICKED | `src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/Fauna/BMT_Caverns/Things/Animal/BloodropMoth/BloodropMoth_south.png` |
| RM_LanternDeeps | `RM_ThrakkCap` | OWNER_PICKED | OWNER_PICKED | `src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/Things/Plant/ThrakkCap/B.png` |
| RM_LeaningScrub | `RSW_Gizka` | OWNER_PICKED | OWNER_PICKED | `src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/Gizka/Gizka_north.png`<br>`src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/Gizka/Gizka_south.png` |
| RM_Miasma | `RM_CrimsonOpeeJuv` | OWNER_PICKED | OWNER_PICKED | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/CrimsonOpee/CrimsonOpee_east.png`<br>`src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/CrimsonOpee/CrimsonOpee_north.png`<br>`src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/CrimsonOpee/CrimsonOpee_south.png`<br>`src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/CrimsonOpee/CrimsonOpee_west.png` |
| RM_Miasma | `RM_Liliana` | HAND_MADE | HAND_MADE | `src/RimMandrake/Miasma/Textures/Things/Pawn/Animal/RM_Liliana/RM_Liliana_east.png` |
| RM_Miasma | `RM_ReefbackJuv` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/Reefback/Reefback_west.png` |
| RM_Miasma | `RM_RustNipperJuv` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/RustNipper/RustNipper_east.png`<br>`src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/RustNipper/RustNipper_west.png` |
| RM_Miasma | `RM_ShaleGorgerJuv` | OWNER_PICKED | OWNER_PICKED | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/ShaleGorger/ShaleGorger_east.png`<br>`src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/ShaleGorger/ShaleGorger_west.png` |
| RM_Miasma | `RM_SiltLampreyJuv` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/SiltLamprey/SiltLamprey_west.png` |
| RM_Miasma | `RM_ThornbackColoJuv` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/ThornbackColo/ThornbackColo_west.png` |
| RM_Miasma | `RSW_FaaJuv` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/Faa/Faa_west.png` |
| RM_Miasma | `RSW_MeeJuv` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/Mee/Mee_east.png`<br>`src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/Mee/Mee_west.png` |
| RM_Miasma | `RSW_OpeeSeaKillerJuv` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/OpeeSeaKiller/OpeeSeaKiller_west.png` |
| RM_Miasma | `RSW_RustNipperJuv` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/RustNipper/RustNipper_east.png`<br>`src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/RustNipper/RustNipper_west.png` |
| RM_Miasma | `RSW_SiltLampreyJuv` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/SiltLamprey/SiltLamprey_west.png` |
| RM_Miasma | `RSW_YobshrimpJuv` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/Yobshrimp/Yobshrimp_west.png` |
| RM_Miasma | `RM_Nogtyl` | STAND_IN | STAND_IN | `src/RimMandrake/TheRot/Textures/RotSporeKit/Things/Plant/Nogtyl/Nogtyl_B.png`<br>`src/RimMandrake/TheRot/Textures/RotSporeKit/Things/Plant/Nogtyl/Nogtyl_C.png` |
| RM_Pyrelands | `RM_Sytheclaw` | HAND_MADE | HAND_MADE | `src/RimMandrake/Pyrelands/Textures/Things/Pawn/Animal/Pyrelands/Sytheclaw/Sytheclaw_east.png`<br>`src/RimMandrake/Pyrelands/Textures/Things/Pawn/Animal/Pyrelands/Sytheclaw/Sytheclaw_south.png` |
| RM_Pyrelands | `RSW_Gizka` | OWNER_PICKED | OWNER_PICKED | `src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/Gizka/Gizka_north.png`<br>`src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/Gizka/Gizka_south.png` |
| RM_Pyrelands | `RM_FE_Plant_EmberGrass` | HAND_MADE | HAND_MADE | `src/RimMandrake/Pyrelands/Textures/Things/Plant/RM_FE_EmberGrass/RM_FE_EmberGrassB.png`<br>`src/RimMandrake/Pyrelands/Textures/Things/Plant/RM_FE_EmberGrass/RM_FE_EmberGrassC.png` |
| RM_Pyrelands | `RM_FE_Plant_Quickgrass` | OWNER_PICKED | OWNER_PICKED | `src/RimMandrake/Pyrelands/Textures/Things/Plant/RM_FE_Quickgrass/RM_FE_QuickgrassB.png` |
| RM_RustCathedral | `RSW_Mynock` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/ShipVermin/Mynock/Mynock_south.png` |
| RM_TheForge | `RM_FirevineTree` | HAND_MADE | HAND_MADE | `src/RimMandrake/TheForge/Textures/Things/Plant/RM_FirevineTree/RM_FirevineTree_a.png` |
| RM_TheRot | `RM_Chittik` | OWNER_PICKED | OWNER_PICKED | `src/RimMandrake/TheRot/Textures/Things/Pawn/Animal/RM_Chittik/RM_Chittik_south.png` |
| RM_TheRot | `RM_Bryolux` | HAND_MADE | HAND_MADE | `src/RimUtinni/UtinniPatches/Textures/Things/Plant/Bryolux/BryoluxA.png` |
| RM_TheRot | `RM_GlowingAgarilux` | HAND_MADE | HAND_MADE | `src/RimUtinni/UtinniPatches/Textures/Things/Plant/Agarilux/AgariluxA.png` |
| RM_TheRot | `RM_Glowstool` | HAND_MADE | HAND_MADE | `src/RimUtinni/UtinniPatches/Textures/Things/Plant/Glowstool/GlowstoolA.png` |
| RM_TheScald | `RM_Shulla` | OWNER_PICKED | OWNER_PICKED | `src/RimMandrake/TerminalBiomes/Textures/Things/Pawn/Animal/RM_Shulla/RM_Shulla_north.png`<br>`src/RimMandrake/TerminalBiomes/Textures/Things/Pawn/Animal/RM_Shulla/RM_Shulla_south.png` |
| RM_TheSump | `RM_SumpMouse` | OWNER_PICKED | OWNER_PICKED | `src/RimMandrake/TheSump/Textures/Things/Pawn/Animal/RM_SumpMouse/RM_SumpMouse_south.png` |
| RM_TwilightSea | `RM_GrippingTerror` | OWNER_PICKED | OWNER_PICKED | `src/RimMandrake/TerminalBiomes/Textures/Things/Pawn/Animal/SeaBeasts/GrippingTerror/GrippingTerror_west.png` |
| RM_TwilightSea | `RM_Lanternwhale` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/Lanternwhale/Lanternwhale_west.png` |
| RM_TwilightSea | `RM_Noolim` | OWNER_PICKED | OWNER_PICKED | `src/RimMandrake/TerminalBiomes/Textures/Things/Pawn/Animal/RM_Noolim/RM_Noolim_north.png`<br>`src/RimMandrake/TerminalBiomes/Textures/Things/Pawn/Animal/RM_Noolim/RM_Noolim_south.png` |
| RM_TwilightSea | `RSW_Faa` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/Faa/Faa_west.png` |
| RM_TwilightSea | `RSW_Lanternwhale` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/Lanternwhale/Lanternwhale_west.png` |
| RM_TwilightSea | `RSW_Mee` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/Mee/Mee_east.png`<br>`src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/Mee/Mee_west.png` |
| RM_Warscar | `RM_Rimclaw` | HAND_MADE | HAND_MADE | `src/RimMandrake/Scarlands/Textures/Things/Pawn/Animal/RM_Rimclaw/RM_Rimclaw_east.png` |
| RM_Warscar | `RM_ScarRoach` | HAND_MADE | HAND_MADE | `src/RimMandrake/Scarlands/Textures/Things/Pawn/Animal/RM_ScarRoach/RM_ScarRoach_east.png` |
| RM_Warscar | `RSW_MegaphoridLarva` | STAND_IN | STAND_IN | `src/RimStarWars/SWBestiary/Textures/swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/Megaphorid/MegaphoridLarva_east.png`<br>`src/RimStarWars/SWBestiary/Textures/swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/Megaphorid/MegaphoridLarva_north.png`<br>`src/RimStarWars/SWBestiary/Textures/swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/Megaphorid/MegaphoridLarva_south.png` |
| RM_Warscar | `RSW_Mynock` | HAND_MADE | HAND_MADE | `src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/ShipVermin/Mynock/Mynock_south.png` |
| RM_Warscar | `RM_ScorchedStars` | STAND_IN | STAND_IN | `src/RimMandrake/Scarlands/Textures/Things/Plant/RM_ScorchedStars/RM_ScorchedStars_b.png` |
| RM_Wastes | `RM_Frethik` | HAND_MADE | HAND_MADE | `src/RimMandrake/Wastes/Textures/Things/Pawn/Animal/RM_Frethik/RM_Frethik_east.png`<br>`src/RimMandrake/Wastes/Textures/Things/Pawn/Animal/RM_Frethik/RM_Frethik_north.png` |
