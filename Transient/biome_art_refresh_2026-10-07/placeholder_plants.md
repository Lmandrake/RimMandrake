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
| animal | FeverWood | RM_Sekkulaath_Juvenile | — | OWED: no job queued |
| animal | FeverWood | RM_Thavrik_east | feverwood_thavrik_east, feverwood_thavrik_north, feverwood_thavrik_south | rendered earlier, never installed |
| animal | FeverWood | RM_Thavrik_north | feverwood_thavrik_east, feverwood_thavrik_north, feverwood_thavrik_south | rendered earlier, never installed |
| animal | FeverWood | RM_Thavrik_south | feverwood_thavrik_east, feverwood_thavrik_north, feverwood_thavrik_south | rendered earlier, never installed |
| animal | TerminalBiomes | RM_Sorruth | greysea_sorruth_v1_east, greysea_sorruth_v1_south | rendered earlier, never installed |
| building | FeverWood | RM_LureStake | — | OWED: no job queued |
| building | FeverWood | RM_SekkulaathTank | — | OWED: no job queued |
| building | FeverWood | RM_Sekkulaath_Feeler | — | OWED: no job queued |
| building | FeverWood | RM_Sekkulaath_Lash | — | OWED: no job queued |
| building | FeverWood | RM_Sekkulaath_Porter | — | OWED: no job queued |
| building | FeverWood | RM_Sekkulaath_Sentinel | — | OWED: no job queued |
| building | FeverWood | RM_Sekkulaath_Snare | — | OWED: no job queued |
| building | FeverWood | RUT_FeverTrunkHeartwood | — | OWED: no job queued |
| building | LuminousPigment | RM_DeepfirePress | — | OWED: no job queued |
| building | LuminousPigment | RM_GlowTank | — | OWED: no job queued |
| building | Webwork | RM_Webwork_NestWall | — | OWED: no job queued |
| building | Webwork | RM_Webwork_Web | webwork_web | rendered earlier, never installed |
| item | Bacta | RSW_BactaPatch | — | OWED: no job queued |
| item | FeverWood | RM_DrommathBurstSap | — | OWED: no job queued |
| item | FeverWood | RM_DrommathSap | — | OWED: no job queued |
| item | FeverWood | RM_OssagrelSap | — | OWED: no job queued |
| item | FeverWood | RM_PottersClay | — | OWED: no job queued |
| item | FeverWood | RM_RadioactiveSuppressant | — | OWED: no job queued |
| item | FeverWood | RM_SeepOil | — | OWED: no job queued |
| item | FeverWood | RM_SekkulaathSpleenChemicals | — | OWED: no job queued |
| item | FeverWood | RM_ThornbugNectar | — | OWED: no job queued |
| item | FeverWood | RM_VaulmLacquer | — | OWED: no job queued |
| item | LuminousPigment | RM_CrowncarpetDead | — | OWED: no job queued |
| item | LuminousPigment | RM_CrowncarpetFresh_a | rm_crowncarpetfresh_icon_b, rm_crowncarpetfresh_icon_c | rendered earlier, never installed |
| item | TheSump | RM_StrongTarSolvent | — | OWED: no job queued |
| item | TheSump | RM_TarRuinedGoods | — | OWED: no job queued |
| item | TheSump | RM_ThrummelSeepwax | — | OWED: no job queued |
| item | UtinniPatches | RUT_Greenwood | — | OWED: no job queued |
| item | UtinniPatches | RUT_Hardwood | — | OWED: no job queued |
| item | Webwork | RM_BrimlockWater | — | OWED: no job queued |
| item | Webwork | RM_OllathrixEgg | — | OWED: no job queued |
| item | Webwork | RM_TavroskLiquor | — | OWED: no job queued |

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
