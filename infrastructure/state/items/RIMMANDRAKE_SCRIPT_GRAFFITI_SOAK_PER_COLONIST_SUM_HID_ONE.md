## spec

Coverage judge rm-coverage-judge-1794936862 gap g2 (stories_not_tax), mended in scene text by Designer run
rm-role-designer-1794939319: `design/concepts/Graffiti/scenes.json` sc_lived_in_soak now starts with a trait mix, reads
every colonist on their own against the control, and requires one unforced story. The proof script still averages:
`src/RimMandrake/Graffiti/validation.py::scene_lived_in_soak` checks a colony sum (`soak_mood_sum_stays_small`) and casts
ordinary recruits with whatever traits they roll.

Build: cast at least one colonist GraffitiTemperament reads as sensitive and one clean freak (Very Neurotic) among the
six, asserted; replace `soak_mood_sum_stays_small` with `soak_each_colonist_below_control` (each colonist's own Graffiti
mood thoughts, daily, below the forced-hourly control's level for a colonist of the same temperament; relative, no pinned
number); add `soak_unforced_story_happens` (at least one mark painted, read with a thought, or answered, unforced, in the
three weeks); the control is read per colonist too.

## criteria

The soak checks every colonist against the control, with a sensitive and a clean-freak colonist present, and fails an inert layer.

## verify

Acceptance test: `python3 design/concepts/Graffiti/acceptance/soak_script_per_colonist.py src/RimMandrake/Graffiti/validation.py`
prints PASS (1 check). Watched failing on 6632657a9e. The live run stays UNRUN until built.
