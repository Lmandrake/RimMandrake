
## spec
Owner, Scald sheet 2026-10-05 ("Finished with the scald sheet"). Jobs: `Transient/biome_ffar/thescald_close_jobs_2026-10-05.json` (15 artpipe jobs, ids `scald3_*`). When they finish, collect and `art.py install` each kept render:
- `scald3_shimmereel_{east,north,south}` -> RM_Thuum (label shimmer eel). North/south derive from the new east master (one creature, his note).
- `scald3_doss_*` -> RM_Doss. `scald3_iridesce_*` -> RM_ScaldWalker (label iridesce; its live picture is a byte copy of the iridai's).
- `scald3_crowncarpet_{a,b,c}` -> `LuminousPigment/Textures/Things/Plant/RM_Crowncarpet/`, then repoint RM_Crowncarpet (and RM_CrowncarpetCultured) off the borrowed `Things/Plant/Ambrosia`.
- `scald3_sandoaquamonster_*` -> RSW_SandoAquaMonster (canon `sandoaquamonster`; his note: NOT feline). The live set has a separate `_west.png`: replace or remove it so west mirrors the new east.
Put them on a sheet for his look before calling any of it final.
## verify
`art.py status` for each subject shows the new shas live; `placeholder_detect.py` reads RM_Crowncarpet REAL.
