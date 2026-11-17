## spec

Coverage judge rm-coverage-judge-1794936862 (2026-11-17, tree e6507f3b) gap g1, severity problem, return_to 3, criterion
sound (judge and second reader). The card reword d1542a3675 made marks_various a judge's call ("a judge shown the lanes'
marks tells several kinds of mark apart, not recolours of one"), but `design/concepts/Graffiti/scenes.json`
sc_spree_variety still reads "read def and variant of every mark" (no capture) and its only control is "the pool gated to
one def", which the judge never sees. Nothing rules out one shape in several tints. Evidence:
`design/concepts/Graffiti/coverage_verdict.json` gaps[g1].

Fix (the judge's smallest_fix): sc_spree_variety's action captures every lane's mark at play zoom, unlabelled, for a judge
who names the kinds; a control shows the same judge a recolour set (one def's texture in the six lanes' tints, or six defs
sharing one texture) with expect "the judge calls them recolours of one". The pool-gate check can stay. Scene text only;
no bar's words change (marks_various' oracle already says this).

## criteria

The scene's action names a capture shown to a judge, and a control names a recolour set the judge must call recolours of one.

## verify

Acceptance test: `python3 design/concepts/Graffiti/acceptance/variety_scene_judge_capture.py design/concepts/Graffiti/scenes.json`
prints PASS (1 check). Watched failing on 842c8a43dc.
