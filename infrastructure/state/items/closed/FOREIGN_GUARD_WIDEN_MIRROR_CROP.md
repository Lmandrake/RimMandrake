## spec
The codex_image.py foreign-copy guard (byte check + 16x16 picture distance + detail confirmation) does not catch a MIRRORED
or CROPPED copy. Measured 2026-10-24 (/mnt/d/ClaudeWork/rimmandrake/guard_vet/fn_gaps.out): Dustflutter r2 east mirrored is
17.82 from its source, centre 75% crop 11.86 (bar 4.0); a mirrored/cropped terrain tile passes coarse but fails detail (0.05).

## Why it may matter
A west-facing job could place a mirrored east from a peer job; an agent fitting a 1536x1024 render to a square may centre-crop.
Neither seen in the 5,205-output census. Careful: mirror detection must not refuse a legitimate west drawn from its own east
reference (inputs are already excluded), nor a sibling west/east pair generated independently.

## verify
Decide whether worth it. If yes: compare the mirrored own thumbnail too (cheap: index unchanged); for crops, index a centre-square
thumbnail as well. Calibrate against the census (pairs_classified.tsv) before choosing bars.
