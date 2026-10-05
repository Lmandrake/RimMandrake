# ART_SUBJECT_RESOLVER_1 phase 2 — progress 2026-10-04

- [ ] texture index
- [ ] resolver wiring
- [ ] sheets rebuilt
- [ ] audit before/after

## 23:03 texture index built
`src/RimMandrake/Utils/art/gametex.py index` — 65 s cold (find over 897 mods with Textures: 87 local Mods + 810 workshop, 96,017 PNGs; + 7,945 bundle extracts); def texPaths from DefDump capture 2026-10-04T17-39-06Z, 21,530 defs, 4 s. Cache /tmp/rm_gametex.
AA_Thunderox male: IN GAME = Thunderox Art Override [603], shadowed Alpha Animals [404]. AA_NightRam: IN GAME Alpha Animals.

## 23:20 done
- ingest: 532 game-copy variants (478 loose PNGs from 282 mod copies + 55 bundle extracts) for 854 texPaths of 879 census defs, bound by live-dump texPath. 4 texPaths have no file anywhere (RM_Braskeen, RM_Greatbole_a, RM_Ismerrow, RM_Kaddrath_a — ours, never shipped; rows show renders).
- NO ART YET: Abyss 20 -> 0, Cauldron 19 -> 0, Contagion 1 -> 0. check_sheet 0 FAIL x3. Ruled sheets untouched.
- audit: A2 census NO ART 102 -> 0; A1 5 -> 3; B6 20 -> 0; name-only columns 403 -> 384.
- audit probe: desert_swaca_wraid replaced by pyrelands_anooba_v1 — every desert_swaca_* _artsrc dir is gone (done/ records remain).
- code PUBLISHED 39d25dd42.
