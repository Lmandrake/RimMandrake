# RIMMANDRAKE_MEASURE_SCORCHFRUIT_FREEZER_FILL_CAPPED_AT_FORTY

## spec
Owner, 2026-11-13 (on RIMMANDRAKE_PROVE_PYRELANDS_IN_FOUR_SCENES, walk_season_on_the_pyre): *"The scorchfruit makes it worthwhile: rich abundance from the ashes, and your freezer stuffed if you're prepared with room."*

Partial (read 2026-11-13 at a68d89e622). The mechanism exists: pods seed 1 in 20 burned cells (`RM_PyrelandsMod.cs`
scorchFruitChance 0.05), harvestYield 5, pod rot 1.1 days; the fruit (RM_FE_ScorchFruitYield) is nutrition 0.09, rots in 4
days unfrozen (`src/RimMandrake/Pyrelands/Defs/ThingDefs_ScorchFruit/ScorchFruit.xml`). The map cap is 40 standing pods
(scorchFruitMapCap), so one full stand is 200 fruit = 18 nutrition at full yield, about 11 colonist-days (arithmetic from the
defs). Whether that is "rich abundance" and fills a freezer over a season is unmeasured, and the Deep Tribes' rite carries some off.
Measure on a live Pyrelands colony (or the season walk's log): fruit harvested and stored per burn and over a season against what
the colony eats; if it falls short, propose the tuning (cap, chance, yield) with the numbers, and the tuning goes to the Conductor
as a design call.
Census and walk criteria: `D:\ClaudeWork\rimmandrake\conductor\cards_20261113_am\walk_season_criteria.md`.

Acceptance test: none, live behaviour: the bar ("freezer stuffed") is a reading on a played season, not an offline function;
the measured numbers per burn and per season are the deliverable.
