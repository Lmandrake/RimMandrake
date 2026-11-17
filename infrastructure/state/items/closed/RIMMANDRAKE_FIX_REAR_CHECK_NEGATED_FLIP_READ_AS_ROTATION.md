# RIMMANDRAKE_FIX_REAR_CHECK_NEGATED_FLIP_READ_AS_ROTATION

## spec

`art_calibration.outcome` grades the planted `north_from_south_RM_DecayDrake_r2` case: it must be refused on C1 at
north.png with a rear-view redraw as the fix, never a rotation of the south. It tested the fix text with
`ROTATE_RE` (`rotat|180|\bflip`) anywhere in it, so a fix that names a flip only to forbid it read as a rotate fix.
In the 2026-11-17 08:33Z calibration the judge wrote "Redraw north.png as a rear view of the same subject at 512x512
real alpha, keeping south.png's proportions, palette, scale and footprint (mash mounds optional). Do not copy or flip
south.png." and the case came out "refuse, misdirected (C1)", a correct refusal graded wrong.

Fix: `rotate_fix(what)` counts a ROTATE_RE hit only when no negation (not, never, no, don't, without, avoid, instead
of) precedes it in its own sentence. A fix that asks for a flip or rotation is still misdirected.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_art_calibration.py` prints `PASS: 0 failure(s)`. Watched
failing on the base with 2 failures (the judge's own words above, and "never a rotation of the south"); the two
guard cases ("Flip south.png and paint over the face…", "rotate south.png 180 degrees, not a new drawing") come out
misdirected before and after.

## criteria

- The judge's 08:33Z fix text grades "refuse"; a fix asking for a flip or rotation still grades misdirected.

## refs

file: src/RimMandrake/rimflow/art_calibration.py
file: src/RimMandrake/rimflow/selftest_art_calibration.py
