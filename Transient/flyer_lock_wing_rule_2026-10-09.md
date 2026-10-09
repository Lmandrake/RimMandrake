# Flyer lock wing rule, option C — 2026-10-09 (BENCH helper)

Implemented in `src/RimMandrake/Utils/art/flyer_lock.py` (`lock_frame`; new `--wing-far 4`, `--wing-depth 12`).
Outside the plate a wing must join something reaching > 4 px from the body. Inside the plate a pixel counts only within 12 px of that wing.
`check`, floors and the 0.92 gate are untouched. The old rule remains reachable with `--wing-far 0 --wing-depth 1000000`, and `--keep-isolated` is unchanged.
Selftest: 3 new cases (body patch is not wing; a wing sweeping the body is kept; far body noise stays plate; C is no looser than old).

Offline re-run on plateA + Sketto master_v3/wing2/wing3 (`/home/mandrake/rm/scratch/BENCH/sketto/lock_2026-10-09_C/`, `result.json`, `run.py`; locked frames under `after/`):

| facing | frame | body px reclassified as wing, before -> after |
|---|---|---|
| south | master / wing2 / wing3 | 3 -> 0 / 1431 -> 497 / 1040 -> 63 |
| north | master / wing2 / wing3 | 11 -> 11 / 891 -> 268 / 1213 -> 354 |

Locked share: south 0.116 -> 0.279, north 0.129 -> 0.260. Still below the 0.38 floor (ceiling 0.338/0.318 from wing size). That is the owner's decision, and the floor was not touched. Plate-identity stays 1.0.
East not re-run (its frames came from master v2 and don't align to plate v2).
