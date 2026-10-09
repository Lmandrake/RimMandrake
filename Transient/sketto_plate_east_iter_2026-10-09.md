# Sketto plate east iteration 2026-10-09

## v2 east failure (canon 3/4, 1 n/a)
Only failing line: Must-show 5, "four thin spindly clawed legs". Grader reason: tucked limbs merge with belly folds. Other lines pass; wings line is canon_na on the wingless plate (grader handled it correctly).
Render check (`D:\Luke\dev\_artpipe\_artsrc\sketto_fly_plate_v2_east\sketto_fly_plate_v2_east.png`): a row of ~4 tiny curled claw tips under the belly, no limb segments. The master v3 east has the same blob. Genuine miss, grader right.

## Action
Filed `sketto_fly_plate_v3_east` (derive_from sketto_fly_master_v3_east, canon_na [2] kept). Prompt targets legs only: four separate limbs, two pairs, visible upper+bent lower segment, hanging just below belly line, gaps between each. Row: `Transient/sketto_pilot_2026-10-08/stage2_plate_v3_east.json`. fill_queue warned no biome_register (same as v2).

## Offline lock check, S/N (scratch, NOT installed)
Output: `/home/mandrake/rm/scratch/BENCH/sketto/lock_2026-10-09/{north,south}` (+ .lock.json). Inputs: plate v2 + frames master v3, wing2_v1, wing3_v1.
Lock REFUSED both facings at the re-pose gate (alpha cover floor 0.92), so no locked share exists vs floor 0.38:
- north: cover master 0.831, wing2 0.867, wing3 0.921 (ok)
- south: cover master 0.819, wing2 0.777 (wing2_south is a canon-failed render, in failed/), wing3 0.931 (ok)
Only the wing3 frame passes; the master and wing2 frames differ from the plate body (plate redraw drifts from master) more than the gate allows. NEXT: either regenerate wing poses from the plate (derive_from plate) or lower --min-cover with owner's say; wing2_south also needs canon fix.
