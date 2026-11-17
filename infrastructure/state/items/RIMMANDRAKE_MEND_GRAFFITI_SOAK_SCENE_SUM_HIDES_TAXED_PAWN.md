## spec

Coverage judge rm-coverage-judge-1794936862 (2026-11-17, tree e6507f3b) gap g2, severity problem, return_to 3, criterion
sound (judge and second reader). stories_not_tax's oracle now reads "no colonist's mood is ruled by them: they read as
stories, not a tax", but `design/concepts/Graffiti/scenes.json` sc_lived_in_soak still expects "summed mark thoughts stay
small", and its start asserts only "a colony of six on ordinary walls". A colony sum averages away the sensitive and
clean-freak pawns the mod amplifies on purpose, and nothing requires an unforced story, so an inert layer passes.
Evidence: `design/concepts/Graffiti/coverage_verdict.json` gaps[g2].

Fix (the judge's smallest_fix): start asserts at least one sensitive and one clean-freak colonist among the six; expect
reads each colonist's own mark-thought mood daily and every colonist stays below the forced-hourly control's level for a
colonist of the same traits (relative, no pinned number), and at least one unforced graffiti story happens in the three
weeks (a mark painted, read with a thought, or answered); the control's "visible standing tax" is a per-colonist read too.
Scene text only; no bar's words change.

## criteria

The soak scene checks every colonist against the control, with a trait mix in its start and an unforced story required.

## verify

Acceptance test: `python3 design/concepts/Graffiti/acceptance/soak_scene_per_colonist.py design/concepts/Graffiti/scenes.json`
prints PASS (1 check). Watched failing on 842c8a43dc.
Second return (coverage judge rm-coverage-judge-1794940039, gap g1): `python3 design/concepts/Graffiti/acceptance/soak_scene_shape_not_size.py design/concepts/Graffiti/scenes.json`
prints PASS (13 checks). Watched failing on 8e5243f7e0 (8 of 13).

## refs
file: design/concepts/Graffiti/scenes.json
file: design/concepts/Graffiti/acceptance/soak_scene_shape_not_size.py
