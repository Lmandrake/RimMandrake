# GREYSEA_SALTDOME_SCATTER_OOB_1 — RM_SaltDomeShore's failed cluster-centre search reaches ThingsListAt as IntVec3.Invalid

## the defect, MEASURED 2026-09-26 (Scald load round, 12-mod tier, quicktest map-gen)

Three consecutive `Player.log` lines, in order:

```
Scatterer Verse.GenStep_ScatterThings from def RM_GreySeaScatterShoreDomes could not find cell to generate at.
Could not find cluster center to scatter RM_SaltDomeShore
Got ThingsListAt out of bounds: (-1000, -1000, -1000)
```

`(-1000,-1000,-1000)` is `IntVec3.Invalid`. Something passes the failed cluster-centre
result onward to `ThingsListAt` instead of bailing. The first two lines are benign on a
non-Grey-Sea map; the third is a real out-of-bounds read, and it fires on an ordinary
quicktest map — i.e. on every map generation, not only a Grey Sea one.

## criteria
- [ ] A quicktest map generates with no `Got ThingsListAt out of bounds` line.
- [ ] A Grey Sea map still scatters `RM_SaltDomeShore` normally.
