## spec

Coverage judge rm-coverage-judge-1794936862 gap g2 (stories_not_tax), mended in scene text by Designer run
rm-role-designer-1794939319: `design/concepts/Graffiti/scenes.json` sc_lived_in_soak now starts with a trait mix, reads
every colonist on their own against the control, and requires one unforced story. The proof script still averages:
`src/RimMandrake/Graffiti/validation.py::scene_lived_in_soak` checks a colony sum (`soak_mood_sum_stays_small`) and casts
ordinary recruits with whatever traits they roll.

Build: cast at least one colonist GraffitiTemperament reads as sensitive and one clean freak (Very Neurotic) among the
six, asserted; replace `soak_mood_sum_stays_small` with `soak_each_colonist_returns_to_zero` (each colonist's own negative
Graffiti mood thoughts summed daily, positive ones not netted; fails a colonist whose total is held on more than half the
days of weeks two and three, whatever the source, a rotating run of marks included; the only days not counted are those a
mockery of that colonist or a raid's departing marks cause, while that mockery's thought runs or until the raid's marks are
answered or weathered, listed per colonist; prints each colonist's held-day count, the limit and the days read); add
`soak_unforced_story_happens` (at least one mark painted, read with a thought, or answered, unforced, in the three weeks);
the control (painting forced every hour) is read the same way and must show the sensitive and clean-freak colonists held on
most days of weeks two and three. Coverage judge rm-coverage-judge-1794940039 struck the earlier
`soak_each_colonist_below_control`: graffiti mood is capped (RM_GraffitiKernel.BadMoodBudget), so the forced control sits at
the cap and a colonist holding a small debuff every day passed it (exam e51, k6).

## criteria

The soak fails any colonist whose graffiti debuff is held on most days, the control proves the read sees one, with a sensitive and a clean-freak colonist present, and fails an inert layer.

## verify

Acceptance test: `python3 design/concepts/Graffiti/acceptance/soak_script_per_colonist.py src/RimMandrake/Graffiti/validation.py`
prints PASS (1 check). Watched failing on 6632657a9e; rewritten for the shape check and watched failing again on 8e5243f7e0. The live run stays UNRUN until built.
