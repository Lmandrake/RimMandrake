# RIMMANDRAKE_ORDER_SLACK_MAST_BEHIND_TALL_SOUTHERN_PICTURES

Gimme Some Slack, **next version** (outside the range of 0.1.1 bar `poles_draw_in_front_when_south`, which is about a pole south
of something). From journal Questions 4 (a), answered by the ticket sweep of 2026-11-22 (Evidence-for-Ask, the obvious answer).

His words that set the rule (filing of `RIMMANDRAKE_DRAW_SLACK_POLES_IN_FRONT_WHEN_SOUTH`, his walk of 2026-11-20):
*"Power poles need the "huge things" ordering rule of appearing "in front" when they are south of something."*

## spec

The reverse case: a building whose picture reaches north into a mast standing just north of it draws BEHIND the mast, because the
SouthDrawsFront rule keeps such buildings on their own Building layer, under the common layer the mast prints on. Measured
2026-11-22 by `src/RimMandrake/GimmeSomeSlack/selftest_gss_pole_south_draws_front.py`: `APART BUILDING_LAYER_REACH: 1170 pairs`
(18 by a picture inside its footprint, 1152 by a picture reaching north past it). Fix offered by the run that found it: in the
rule's home (MandrakePatches' SouthDrawsFront kernel), a building whose picture reaches north of its footprint prints on the common
layer, as plants do. That changes MandrakePatches for every mod, so the fix carries its own check for the mods that use the rule.

Region (b) of the same question (the mast head over a plant over 4 cells tall) is a polish line only: no vanilla plant reaches it.

## criteria

Acceptance test (red today, watched 2026-11-22: the line reads 1170 pairs):

    python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_pole_south_draws_front.py | grep "APART BUILDING_LAYER_REACH"

passes when that line is gone (0 pairs) and the selftest still prints PASS.

## verify

Run the acceptance test under ## criteria; cite its output on the close.
