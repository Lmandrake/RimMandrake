## spec
Pyrelands 0.1.0, seen in in-game visit 5 (ArchBig, tier pyrelands, 2026-11-22, build e63595716c), strange thing, class MOD
(presumed, unproven). Check `sc_burn_line_walks` (bar `burn_line_walks`, whose wording asks a judge shown the 24 hourly
captures to confirm "a natural grass fire that moves"). Every state row of burn_line PASSed (4/4), but the hourly captures
show the fire's trail as many parallel, ruler-straight north-south lanes one or two cells wide, a fire at the head of each
lane and unburned grass standing between the lanes (hours 04 to 23). A natural grass fire spreads as a broad, ragged front.
The pattern reads like the wind carry (fire spreads downwind cell by cell and almost never sideways). A judge shown these
captures is likely to refuse "natural" [guess ~70%].
Evidence: design/concepts/Pyrelands/version/in_game/visit_5/screenshots/burn_line__burn_line_hour_08_1795356989096_10_stitched__cell_rect.jpg
(and hours 04-23 beside it); the full captures are in the game's Screenshots folder (names in visit_5/evidence/pv5_burn_line.json).

## verify
Stage 6: a judge (not the maker) is shown the 24 hourly captures of `burn_line` unlabelled and answers whether the fire
reads as a natural grass fire. If not: the Designer decides how much sideways spread the wind carry keeps, the mod is
fixed, and the captures are judged again.

## criteria
- A judge shown the hourly captures calls the burn a natural moving grass fire, not lanes.

## Acceptance test
none yet: a taste reading by a judge of the hourly captures (the bar's own clause). A measurable proxy the fixer may build:
the share of newly burned cells in the hour-12 front rect whose east and west neighbours are both unburned (lane cells);
on visit 5's captures it is high by eye; a broad front reads low.

## refs
file: src/RimMandrake/Pyrelands/Source/
file: src/RimMandrake/Pyrelands/validation.py
