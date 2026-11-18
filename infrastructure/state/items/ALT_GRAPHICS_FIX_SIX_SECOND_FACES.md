# ALT_GRAPHICS_FIX_SIX_SECOND_FACES

## proof (corrected 2026-11-17, drain of the retired judge)
The proof the retired Relentless judge was asked to rebind runs clean as a plain shell line; the box parser,
not the proof, was the obstacle. Run it with the CV interpreter (the art selftests import numpy/pillow/cv2):

    "$RM_CV_PYTHON" src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/art/selftest_alt_graphic_slots.py

Measured 2026-11-17 in a shared clone: rc=0, RESULT: GREEN.
Evidence: /Users/mandrake/ClaudeWork/scratch/rm-drain-logs/proofs/ALT_GRAPHICS_FIX_SIX_SECOND_FACES.txt

## why this is ready, not done
The slot tracker half landed at b4fc40a331 and its selftest is green, but the item's own work — the 54
alternate PNGs on the five approved creatures — is still owed. A green selftest over an empty slot table is
not the deliverable. Next worker: draw and install the alternates through `art.py install`, then re-run the
selftest above.
