## spec

Coverage judge rm-coverage-judge-1794936862 gap g1 (marks_various), mended in scene text by Designer run
rm-role-designer-1794939319: `design/concepts/Graffiti/scenes.json` sc_spree_variety now captures every lane's marks at
play zoom, unlabelled, for a judge that did not make the art, and calibrates that judge on a recolour set. The proof
script does not do either yet: `src/RimMandrake/Graffiti/validation.py::spree_variety` gates on a def count
(`variety_three_defs`) and screenshots lanes nobody judges.

Build: replace `variety_three_defs` with a component `variety_judge_names_kinds` (the lane captures go to a fresh judge,
who names the kinds of mark it sees), and add `control_recolour_set_judged_one` (one def's texture in the six lanes'
tints, and six defs sharing one texture, shown to the same judge the same way; it must call each set "recolours of one").
The pool-gated-to-one-def read stays as a script read. No pinned count anywhere.

## criteria

spree_variety asks a judge to name the kinds in unlabelled play-zoom captures and calibrates it on a recolour set.

## verify

Acceptance test: `python3 design/concepts/Graffiti/acceptance/variety_script_judge_capture.py src/RimMandrake/Graffiti/validation.py`
prints PASS (1 check). Watched failing on 6632657a9e. The live run stays UNRUN until built.
