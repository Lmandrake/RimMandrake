# Sketto option A prep — 2026-10-09 (BENCH helper, offline)
Status: DONE. Nothing installed, nothing filed. Scratch: `/home/mandrake/rm/scratch/BENCH/sketto/optionA_2026-10-09/` (run.py, run2.py, plateA_*.png, lockNG_* = gate bypassed).
Script: `/home/mandrake/rm/bench/src/RimMandrake/Utils/art/flyer_plate_from_master.py` (+ `selftest_flyer_plate_from_master.py`). Picture: `D:\Luke\dev\RimMandrake\Transient\sketto_optionA_2026-10-09.png` (columns: plate v2 / option-A plate / locked wing2 frame).

## One-step action on his "yes"
```
python3 src/RimMandrake/Utils/art/flyer_plate_from_master.py --master <master_v3_FACING.png> --donor <plate_v2_FACING.png> --out plateA_FACING.png
python3 src/RimMandrake/Utils/art/flyer_lock.py lock --plate plateA_FACING.png --frame master_v3 --frame wing2 --frame wing3 --facing FACING --prefix Sketto_Flying_ --out DIR
```
Parameters, all facings: `--open 2 --grow 2 --search 8` (defaults). Resulting donor shift / plate px: south (1,4) / 3104, north (0,1) / 2674, east (-1,-7) / 2194.

## Measured (flyer_lock lock + check, option C already in the lock; `--min-cover 0` rerun for share)
| facing | gate cover master / wing2 / wing3 (floor 0.92) | locked share (floor) | still failing |
|---|---|---|---|
| north | 0.974 / 0.939 / 0.955 PASS | 0.260 (0.38) | share only (ceiling 0.318: wings are 2/3 of the frame) |
| south | 0.981 / **0.836** / 0.973 | 0.279 (0.38) | wing2 re-posed at the head (needs a regen from master); share; frames touch the 6 px margin |
| east | 0.975 / **0.892** / **0.719** | 0.128 (0.45) | east master v3 does not match plate v2 east (frames derive from master v2), so plate A east is **invalid** (picture shows a broken body). Not a candidate; east is already filed. |
Plate pixels never under a wing are byte-identical in every frame (1.0) on all three.

## Reading
Option A makes the unchanged 0.92 gate pass for north and for south master/wing3. It does not fix the share floor (owner question 2) or south wing2 (one regen). The wing roots at the shoulders are master wing colour inside the plate (a few px).

## East follow-up

`sketto_fly_plate_v3_east` is **FAILED** (artpipe `failed/`, validator verdict fail on canon; only `_artsrc/sketto_fly_plate_v3_east/sketto_fly_plate_v3_east.canon_attempt1.png` exists). Tried that attempt1 PNG as the leg donor anyway (scratch `.../optionA_2026-10-09/east_v3/`): it aligns (shift 1,2; plate 3141 px, 171 leg px pasted), `--search` 8 and 16 give identical results. Frames: master_v3_east, wing2_v1_east, wing3_v1_east.
- cover (floor 0.92): master v3 **0.946**, wing2 **0.929** (shift -3,6), wing3 **0.531** REJECTED (shift 7,8). Only wing3 fails; wing3_v1 and wing2_v1 east derive from master v2, not v3.
- locked share (`--min-cover 0`, 4 frames): **0.333** vs floor 0.45; plate-never-under-wing px identical 1.0; all 4 frames also fail the 6 px margin.
- Legs from the master itself: master as donor keeps its wings (trunk opening cannot separate them): plate 6008 px with wings in it, wing2 0.512, wing3 0.360. Invalid. The master has no wing-free legs to extract with this script.
- Verdict: east is better than plate v2 east (0.892/0.719) but not passing: wing3 (needs a re-pose from master v3), share, margin. Picture east row updated (attempt1 plate; canon-failed donor, so illustrative only).
