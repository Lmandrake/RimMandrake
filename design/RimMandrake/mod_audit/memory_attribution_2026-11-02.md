# Full-list native memory attribution — 2026-11-02 (FULL_LIST_MEMORY_AUDIT_THIRTY_GB_PRIVATE)

**Question (item, 2026-10-10):** the 550-mod list held 30.6 GB private / 18.3 GB working set with ~5 GB managed
heap. Which mods own the ~25 GB native share?

**Instrument:** `src/RimMandrake/Utils/modaudit/memory_attribution.py` (selftest
`selftest_memory_attribution.py`, mutant-checked). It walks every mod of a list under the 1.6 engine's own load
rules, read from the decompile (`D:\ClaudeWork\rimmandrake\decomp\rw16\all\Verse\ModContentLoader.cs`,
`ModContentPack.cs`, `ModLoadFolders.cs`): LoadFolders for 1.6 with IfModActive*, one file per relative path
(overrides replace), PNG decoded then made non-readable and DXT5-compressed (1 B/px) when both sides are a
multiple of 4 and Prefs `textureCompression` is on (it is, on Archmagi), else RGBA32 (4 B/px), mips x 4/3; DDS
payload as-is; audio files <= 300 KB decoded whole (float PCM upper estimate), larger ones streamed.
Static atlases: `atlas_attribution.py` replays `GlobalTextureAtlasManager.BakeStaticAtlases` from the live def dump
(capture 2026-11-02T17:59:18Z, the same 317 mods): every ThingDef with graphicData and drawerType != RealtimeOnly
inserts its graphic's textures under 512 px into its category's group (Building + minifiable also into Item),
ScatterableDefs into Terrain; per (group, mask) the textures fill pages of (maxTextureSize/2)^2 px sized by
`CalcRectsForAtlasNew`, RGBA32 then DXT5 with floor(log2(w/512))+1 mips; a page's bytes go to mods by pixel share.
The atlas is EXTRA memory: the source textures stay loaded. maxTextureSize 16384 is assumed, not read.
These are ESTIMATES from disk, not measurements.

## Results

| list | mods | textures | decoded audio | static atlases | attributed |
|---|---|---|---|---|---|
| FULL.LATEST at 2026-10-10 (git `e6d99502af`, the item's 551-list; today's folders) | 542 resolved | 10.4 GB (1.3 GB of it RGBA32) | 1.14 GB | UNMEASURED (no def dump of that list exists) | **11.5 GB** + atlases |
| FULL.LATEST now (317 ids after the retirement waves) | 316 resolved | 5.6 GB (0.5 GB RGBA32) | 0.75 GB | 0.81 GB (10 pages, 6331 mod textures) | **7.2 GB** |

Findings:

1. **Loose mod content explains under half of the native share.** 11.5 GB attributed against ~25 GB native leaves
   about 13 GB unexplained. **Static atlases are not it:** on today's list they cost 0.81 GB, 11% on top of the
   loose textures (the biggest shares: `mandrake.rm.biomes` 134 MB, `vanillaexpanded.vfepropsanddecor` 105 MB,
   `sarg.alphamemes` 75 MB). Scaled by the same ratio, the 551-list's atlases were roughly 1-1.5 GB, an
   extrapolation, not a measurement. **That leaves >= 11 GB the disk cannot attribute**: RenderTexture pools (facial animation pools never
   release: `design/RimMandrake/mod_deepdive_faces.md`), AssetBundles (~0.5 GB on disk across the list, DLCs
   included), Core/DLC textures in resources.assets, Unity/Mono native overhead. Whether GPU texture memory lands in
   private bytes at all depends on the driver, so even the 11.5 GB is an upper bound on its private-bytes share.
2. **The naive census overstated textures 4x.** `diskfacts.py`'s `decoded_mb_est` (RGBA32 for every image, every
   version folder) totals 41.7 GB on the 551-list; under the engine's real rules it is 10.4 GB. Do not cite
   `decoded_mb_est` as memory.
3. **The tail is long.** On the 551-list the top 20 mods hold about half of the attribution; no single mod
   exceeds 0.9 GB. Ours lead: `mandrake.rm.biomes` 0.85 GB, `mandrake.rsw.armoury` 0.78 GB,
   `mandrake.rsw.swbestiary` 0.50 GB textures + up to 0.33 GB decoded audio.
4. **The retirement waves already halved it** (11.5 -> 6.4 GB of textures + audio); a fresh measurement on today's list is
   the live clause A1 (`infrastructure/state/live_proofs/FULL_LIST_MEMORY_AUDIT_THIRTY_GB_PRIVATE.txt`).
5. **Cheap wins if memory ever matters:** textures with a side not a multiple of 4 stay uncompressed at 4x the
   cost (1.3 GB on the 551-list, 0.5 GB now; e.g. `redmattis.bigsmall.core` 135 MB, `sihv.rombonesport` 120 MB
   from one 38 MB throne texture).

### Top of the 551-list (tex GB · RGBA32 MB · files · audio MB)

| # | packageId | tex GB | RGBA32 MB | tex files | audio MB | biggest texture |
|---|---|---|---|---|---|---|
| 1 | `mandrake.rm.biomes` | 0.85 | 9 | 3150 | 14 | `Textures/RotSpecies/AgariluxPrime.png` 21 MB |
| 2 | `mandrake.rsw.armoury` | 0.78 | 1 | 2738 | 76 | `Textures/SWApparel/CharacterOutfits/Immortalus_SithLords/Capes/JediRevan/apparel_Thin_south.png` 1 MB |
| 3 | `mandrake.rsw.swbestiary` | 0.50 | 0 | 2456 | 328 | `Textures/Things/Building/Natural/RSW_SarlaccPit/RSW_SarlaccPitA.png` 3 MB |
| 4 | `vesper.egihologramsandprojectors` | 0.37 | 0 | 2521 | 0 | `Textures/SpecialProjections/Projector-Throne/Hologram_16_south.png` 0 MB |
| 5 | `redmattis.bigsmall.core` | 0.33 | 135 | 997 | 0 | `Textures/Xenotypes/unprocessed/BS_Snek.png` 5 MB |
| 6 | `vanillaexpanded.vtexe.facialanims` | 0.33 | 0 | 972 | 0 | `Textures/Things/Pawn/Humanlike/Lids/BIGEYE/None/normal_south.png` 1 MB |
| 7 | `sarg.alphamemes` | 0.26 | 10 | 3520 | 56 | `Textures/Things/Building/BuildingStyles/Mesoamerican/AM_MesoamericanPyramid.png` 3 MB |
| 8 | `xmb.ancienturbanruins.mo` | 0.25 | 76 | 935 | 30 | `Textures/Things/Building/AscendingEscalator_south.png` 9 MB |
| 9 | `mandrake.rsw.starwarsraces` | 0.25 | 0 | 926 | 5 | `Textures/Things/Pawn/Humanlike/Heads/Male/Male_Bone_Normal_south.png` 0 MB |
| 10 | `sd.fa.geneticheadsmods` | 0.26 | 2 | 808 | 0 | `Textures/Eyes_Roos_Faun/RBSF_HorizontalPupils/Male/normal_south.png` 1 MB |
| 11 | `vanillaexpanded.backgrounds` | 0.24 | 81 | 39 | 0 | `Textures/Sacrifice.png` 81 MB |
| 12 | `grimterra.biomesmod` | 0.21 | 27 | 1183 | 0 | `Textures/World/Biomes/Biome_Toxlands.png` 1 MB |
| 13 | `sarg.alphaanimals` | 0.15 | 9 | 1649 | 58 | `Textures/Things/Building/AA_WallBlackJelly_Atlas.png` 2 MB |
| 14 | `who.vfee.isopodageneline` | 0.20 | 0 | 121 | 1 | `Textures/Things/Lightning/Lightning_007_0035.png` 5 MB |

### Top of today's list

| # | packageId | tex GB | RGBA32 MB | tex files | audio MB | biggest texture |
|---|---|---|---|---|---|---|
| 1 | `mandrake.rm.biomes` | 0.85 | 9 | 3150 | 14 | `Textures/RotSpecies/AgariluxPrime.png` 21 MB |
| 2 | `mandrake.rsw.armoury` | 0.78 | 1 | 2738 | 76 | `Textures/SWApparel/CharacterOutfits/Immortalus_SithLords/Capes/JediRevan/apparel_Thin_south.png` 1 MB |
| 3 | `mandrake.rsw.swbestiary` | 0.50 | 0 | 2456 | 328 | `Textures/Things/Building/Natural/RSW_SarlaccPit/RSW_SarlaccPitA.png` 3 MB |
| 4 | `redmattis.bigsmall.core` | 0.33 | 135 | 997 | 0 | `Textures/Xenotypes/unprocessed/BS_Snek.png` 5 MB |
| 5 | `sarg.alphamemes` | 0.26 | 10 | 3520 | 56 | `Textures/Things/Building/BuildingStyles/Mesoamerican/AM_MesoamericanPyramid.png` 3 MB |
| 6 | `mandrake.rsw.starwarsraces` | 0.25 | 0 | 926 | 5 | `Textures/Things/Pawn/Humanlike/Heads/Male/Male_Bone_Normal_south.png` 0 MB |
| 7 | `co.uk.epicguru.meleeanimation` | 0.16 | 12 | 64 | 4 | `Textures/AM/UI/BG/Combined.png` 11 MB |
| 8 | `mandrake.rm.flowworks` | 0.15 | 0 | 636 | 0 | `Textures/RimMandrake/FlowWorks/Pipe/Scrapper/UniversalPipe_Atlas.png` 3 MB |
| 9 | `vanillaexpanded.vfepropsanddecor` | 0.14 | 3 | 1072 | 0 | `Textures/Things/Building/Spaceships/Reactors/ShipReactor.png` 1 MB |
| 10 | `aoba.fortress.industrial` | 0.12 | 56 | 429 | 5 | `Textures/Prince/Prince_Base_south.png` 8 MB |
| 11 | `sihv.rombonesport` | 0.13 | 120 | 72 | 0 | `Textures/Things/Building/Furniture/BoneThroneErok/Left.png` 38 MB |
| 12 | `vanillaexpanded.vgeneticse` | 0.12 | 2 | 1246 | 6 | `Textures/Terrain/Surfaces/GR_WhiteTile.png` 1 MB |
| 13 | `mingtuwuxiang.spacebasedecorative` | 0.12 | 0 | 450 | 0 | `Textures/floor_1SpaceBase/MUS_SpaceBase_MetalFlooringVertical.png` 1 MB |
| 14 | `redmattis.betterprerequisites` | 0.10 | 54 | 199 | 0 | `Textures/RaceDefaults/Spooder/bp_male_north.png` 3 MB |

Rerun: `python3 src/RimMandrake/Utils/modaudit/memory_attribution.py --check` (today's list; report
`Transient/memory_attribution.md`), `--list <ModsConfig.xml> --report <path>` for another list, `--reconcile` with
the game up to read its private bytes beside the estimate.
