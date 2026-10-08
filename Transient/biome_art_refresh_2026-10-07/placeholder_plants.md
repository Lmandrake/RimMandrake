# Placeholder textures still in game (2026-10-07)

## The 21 plant circles

Test: dominant opaque colour share > 0.75 at 64x64 (nearest) over src/**/Textures/Things/Plant; every hit is a flat circle (3 colours at full res), referenced by its biome flora def. 21 files, all `_a.png` of RM_ plants in two biomes. Not regenerated; the owner rules on sheets.

| biome mod | plant | owner ruling(s) on file | note |
|---|---|---|---|
| FeverWood | RM_Ammeth | keep, redo (art protected) | too cartoonish, but good concept.  Regenerate twice as big from the de |
| FeverWood | RM_Cistrel | keep, redo (art protected) | More realistic but good concept, add variants |
| FeverWood | RM_Corvath | keep, redo (art protected) | Redo more realistically and add variants |
| FeverWood | RM_Halquin | keep (art protected) | add variants realistically |
| FeverWood | RM_Maulith | keep (art protected) | add more realistic variants |
| FeverWood | RM_Nubrith | keep (art protected) | add more realistic variants |
| FeverWood | RM_Plennith | keep (art protected) | add more realistic variants |
| FeverWood | RM_Seepril | keep (art protected) | add more realistic variants |
| FeverWood | RM_Skethral | hold, keep (art protected) | cut no longer needed |
| FeverWood | RM_Skimmel | redo (art protected) | add more realistic variants |
| FeverWood | RM_Sodderel | keep, redo (art protected) | add more realistic variants |
| FeverWood | RM_Thulvane | keep, redo (art protected) | add more realistic variants |
| FeverWood | RM_Tullick | keep, redo (art protected) | add more realistic variants |
| FeverWood | RM_Varnoth | keep, redo (art protected) | add more realistic variants |
| FeverWood | RM_Verrow | keep, redo (art protected) | add more realistic variants |
| FeverWood | RM_Wanlith | keep, redo (art protected) | add more realistic variants |
| Webwork | RM_Brennoth | keep (art protected) |  |
| Webwork | RM_Dulloth | keep, redo (art protected) | Huge flat leaves held up high on stilt-like stems. Like lilly pads gro |
| Webwork | RM_Kollavane | keep, redo | Much more realistic, this is a big graphic. Variants please. Read the |
| Webwork | RM_Ruddreth | keep (art protected) |  |
| Webwork | RM_Sorrivel | keep (art protected) |  |

Count by biome mod: FeverWood 16, Webwork 5

Notes: Webwork Dulloth and Kollavane (his redo rows) are flat circles until the v2 redo renders in `_artpipe/done` are reviewed. "keep" on a row whose only picture is the flat circle (e.g. Halquin, Ruddreth, Brennoth, Sorrivel) means he kept the placeholder or picked A as the only option; redo rows (Ammeth, Cistrel...) are queued for regen.

## Placeholders, all kinds (2026-10-07, geometric detector, owner rule 22:33 PDT)

Detector: `src/RimMandrake/Utils/art/placeholder_detect.py` `placeholder_reason()` — flat circle/ellipse/rectangle, <=8 colours, one dominant colour. Shrink-only allowlist: `src/RimMandrake/Utils/art/placeholder_allowlist.json` (lint: `placeholder_lint.py`, required selftest).

### A. Shipped by a def today, beyond the 21 plant circles above: 45 textures

| kind | mod | texture | job(s) | status |
|---|---|---|---|---|
| animal | FeverWood | RM_Chellow_east | regen_fw_chellow_flying_1_v1_east, regen_fw_chellow_flying_1_v1_north, regen_fw_chellow_flying_1_v1_south | queued |
| animal | FeverWood | RM_Chellow_north | regen_fw_chellow_flying_1_v1_east, regen_fw_chellow_flying_1_v1_north, regen_fw_chellow_flying_1_v1_south | queued |
| animal | FeverWood | RM_Chellow_south | regen_fw_chellow_flying_1_v1_east, regen_fw_chellow_flying_1_v1_north, regen_fw_chellow_flying_1_v1_south | queued |
| animal | FeverWood | RM_Drommath | regen_fw_drommath_v2_east, regen_fw_drommath_v2_north | queued |
| animal | FeverWood | RM_Murrelith_east | regen_fw_murrelith_flying_1_v1_east, regen_fw_murrelith_flying_1_v1_north, regen_fw_murrelith_flying_1_v1_south | queued |
| animal | FeverWood | RM_Murrelith_north | regen_fw_murrelith_flying_1_v1_east, regen_fw_murrelith_flying_1_v1_north, regen_fw_murrelith_flying_1_v1_south | queued |
| animal | FeverWood | RM_Murrelith_south | regen_fw_murrelith_flying_1_v1_east, regen_fw_murrelith_flying_1_v1_north, regen_fw_murrelith_flying_1_v1_south | queued |
| animal | FeverWood | RM_Ollareth | feverwood_ollareth_east, feverwood_ollareth_north, feverwood_ollareth_south | rendered earlier, never installed |
| animal | FeverWood | RM_Sekkulaath_Juvenile | phfix_RM_Sekkulaath_Juvenile_a, phfix_RM_Sekkulaath_Juvenile_b | queued 2026-10-07 priority 0 |
| animal | FeverWood | RM_Thavrik_east | feverwood_thavrik_east, feverwood_thavrik_north, feverwood_thavrik_south | rendered earlier, never installed |
| animal | FeverWood | RM_Thavrik_north | feverwood_thavrik_east, feverwood_thavrik_north, feverwood_thavrik_south | rendered earlier, never installed |
| animal | FeverWood | RM_Thavrik_south | feverwood_thavrik_east, feverwood_thavrik_north, feverwood_thavrik_south | rendered earlier, never installed |
| animal | TerminalBiomes | RM_Sorruth | greysea_sorruth_v1_east, greysea_sorruth_v1_south | rendered earlier, never installed |
| building | FeverWood | RM_LureStake | phfix_RM_LureStake_a, phfix_RM_LureStake_b | queued 2026-10-07 priority 0 |
| building | FeverWood | RM_SekkulaathTank | RM_SekkulaathYoungCask (finished, in _artsrc; def RM_SekkulaathYoungCask shares this texPath) | finished art exists, never installed |
| building | FeverWood | RM_Sekkulaath_Feeler | phfix_RM_Sekkulaath_Feeler_a, phfix_RM_Sekkulaath_Feeler_b | queued 2026-10-07 priority 0 |
| building | FeverWood | RM_Sekkulaath_Lash | phfix_RM_Sekkulaath_Lash_a, phfix_RM_Sekkulaath_Lash_b | queued 2026-10-07 priority 0 |
| building | FeverWood | RM_Sekkulaath_Porter | phfix_RM_Sekkulaath_Porter_a, phfix_RM_Sekkulaath_Porter_b | queued 2026-10-07 priority 0 |
| building | FeverWood | RM_Sekkulaath_Sentinel | phfix_RM_Sekkulaath_Sentinel_a, phfix_RM_Sekkulaath_Sentinel_b | queued 2026-10-07 priority 0 |
| building | FeverWood | RM_Sekkulaath_Snare | phfix_RM_Sekkulaath_Snare_a, phfix_RM_Sekkulaath_Snare_b | queued 2026-10-07 priority 0 |
| building | FeverWood | RUT_FeverTrunkHeartwood | phfix_RUT_FeverTrunkHeartwood_a, phfix_RUT_FeverTrunkHeartwood_b | queued 2026-10-07 priority 0 |
| building | LuminousPigment | RM_DeepfirePress | phfix_RM_DeepfirePress_a, phfix_RM_DeepfirePress_b | queued 2026-10-07 priority 0 |
| building | LuminousPigment | RM_GlowTank | RM_SunSphere_v2_south (finished, in _artsrc; def RM_SunSphere uses this texPath) | finished art exists, never installed |
| building | Webwork | RM_Webwork_NestWall | phfix_RM_Webwork_NestWall_a, phfix_RM_Webwork_NestWall_b | queued 2026-10-07 priority 0 |
| building | Webwork | RM_Webwork_Web | webwork_web | rendered earlier, never installed |
| item | Bacta | RSW_BactaPatch | phfix_RSW_BactaPatch_a, phfix_RSW_BactaPatch_b | queued 2026-10-07 priority 0 |
| item | FeverWood | RM_DrommathBurstSap | phfix_RM_DrommathBurstSap_a, phfix_RM_DrommathBurstSap_b | queued 2026-10-07 priority 0 |
| item | FeverWood | RM_DrommathSap | phfix_RM_DrommathSap_a, phfix_RM_DrommathSap_b | queued 2026-10-07 priority 0 |
| item | FeverWood | RM_OssagrelSap | phfix_RM_OssagrelSap_a, phfix_RM_OssagrelSap_b | queued 2026-10-07 priority 0 |
| item | FeverWood | RM_PottersClay | phfix_RM_PottersClay_a, phfix_RM_PottersClay_b | queued 2026-10-07 priority 0 |
| item | FeverWood | RM_RadioactiveSuppressant | phfix_RM_RadioactiveSuppressant_a, phfix_RM_RadioactiveSuppressant_b | queued 2026-10-07 priority 0 |
| item | FeverWood | RM_SeepOil | phfix_RM_SeepOil_a, phfix_RM_SeepOil_b | queued 2026-10-07 priority 0 |
| item | FeverWood | RM_SekkulaathSpleenChemicals | phfix_RM_SekkulaathSpleenChemicals_a, phfix_RM_SekkulaathSpleenChemicals_b | queued 2026-10-07 priority 0 |
| item | FeverWood | RM_ThornbugNectar | phfix_RM_ThornbugNectar_a, phfix_RM_ThornbugNectar_b | queued 2026-10-07 priority 0 |
| item | FeverWood | RM_VaulmLacquer | phfix_RM_VaulmLacquer_a, phfix_RM_VaulmLacquer_b | queued 2026-10-07 priority 0 |
| item | LuminousPigment | RM_CrowncarpetDead | phfix_RM_CrowncarpetDead_a, phfix_RM_CrowncarpetDead_b | queued 2026-10-07 priority 0 |
| item | LuminousPigment | RM_CrowncarpetFresh_a | rm_crowncarpetfresh_icon_b, rm_crowncarpetfresh_icon_c | rendered earlier, never installed |
| item | TheSump | RM_StrongTarSolvent | phfix_RM_StrongTarSolvent_a, phfix_RM_StrongTarSolvent_b | queued 2026-10-07 priority 0 |
| item | TheSump | RM_TarRuinedGoods | phfix_RM_TarRuinedGoods_a, phfix_RM_TarRuinedGoods_b | queued 2026-10-07 priority 0 |
| item | TheSump | RM_ThrummelSeepwax | phfix_RM_ThrummelSeepwax_a, phfix_RM_ThrummelSeepwax_b | queued 2026-10-07 priority 0 |
| item | UtinniPatches | RUT_Greenwood | phfix_RUT_Greenwood_a, phfix_RUT_Greenwood_b | queued 2026-10-07 priority 0 |
| item | UtinniPatches | RUT_Hardwood | phfix_RUT_Hardwood_a, phfix_RUT_Hardwood_b | queued 2026-10-07 priority 0 |
| item | Webwork | RM_BrimlockWater | phfix_RM_BrimlockWater_a, phfix_RM_BrimlockWater_b | queued 2026-10-07 priority 0 |
| item | Webwork | RM_OllathrixEgg | phfix_RM_OllathrixEgg_a, phfix_RM_OllathrixEgg_b | queued 2026-10-07 priority 0 |
| item | Webwork | RM_TavroskLiquor | phfix_RM_TavroskLiquor_a, phfix_RM_TavroskLiquor_b | queued 2026-10-07 priority 0 |

By kind: animal 13, building 12, item 20

### B. Placeholder candidate sets on the 27 served sheets (now greyed, not selectable)

3914 pictures checked across 27 sheets; 359 not in the art store (UNMEASURED, not judged).

| sheet | rows (column) | what |
|---|---|---|
| feverwood | RM_Chellow (A), RM_Claithe (A), RM_Drommath (A), RM_Murrelith (A), RM_Ollareth (A), RM_Skellick (A), RM_Thavrik (A), RM_Vaulm (A) | IN GAME (snapshot) |
| greysea | RM_Corrik (A), RM_Essarn (A), RM_Fessk (A), RM_Otheska (A), RM_Sorruth (A) | IN GAME (snapshot); history column |
| miasma | RM_Karravel (A), RM_Karrimeth (A), RM_Karrolun (A) | IN GAME (snapshot) |
| thechill | RM_Heemin (A), RM_Oovanam (A), RM_OovanamCatch (A) | history column |
| thescald | RM_Noohm (B), RM_Shulla (B) | history column |
| twilightsea | RM_Loohn (B), RM_Lunoowa (B), RM_Noolim (B), RM_Weloon (B) | history column |
| webwork | RM_Brimlock (A), RM_Cravvet (A), RM_Fellome (A), RM_Grennick (A), RM_Kessaroth (A), RM_Norrveth (A), RM_Pellareth (A), RM_Quarrok (A), RM_Sellith (A), RM_Sivvern (A), RM_Skennet (A), RM_Tavrosk (A), RM_Threllick (A), RM_Varrisk (A), RM_Vennick (A), RM_Vessark (A) | history column |

Not shipped any more (replaced on disk since the snapshot): FeverWood Claithe, Skellick, Vaulm; Miasma Karravel, Karrimeth, Karrolun — their sheet column still says IN GAME until the next rebuild, and it is now greyed out.
History columns (Grey Sea / The Chill / The Scald / Twilight Sea script-drawn shapes of 2026-09-24/26; Webwork circles of 2026-09-25 on rows whose real art is installed) were pickable until tonight's rebuild; they are now `placeholder — not selectable`.

### C. Follow-through 2026-10-07 night

All 31 formerly OWED rows now have a job or finished art (none OWED). 29 textures got 2 priority-0 candidate jobs each (58 jobs, `phfix_<def>_a/_b`, builder `build_placeholder_owed_jobs.py`, rows `placeholder_owed_jobs.json`); nothing installed or deployed. RM_SekkulaathTank and RM_GlowTank reuse finished art (above). No canon-library entry exists for any of the 31 (invented FeverWood/Sump/Webwork subjects, bacta patch, timber).
Not art, not queued (flagged by the detector, outside the allowlist's art scope): 3 UI buttons and Blank.png.
Trap found: RUT_Hardwood.png and RUT_Greenwood.png are also the texPath of the fish items RUT_Tekk (and others in RUT_CrackedLandsFish_Items / RUT_WastelandBrine_Items), so a heartwood/greenwood painting would show on those fish until they get their own texPath.
