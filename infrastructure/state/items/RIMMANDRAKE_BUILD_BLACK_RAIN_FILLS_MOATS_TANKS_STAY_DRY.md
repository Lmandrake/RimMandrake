# RIMMANDRAKE_BUILD_BLACK_RAIN_FILLS_MOATS_TANKS_STAY_DRY

## spec
Owner, 2026-11-13 (on RIMMANDRAKE_PROVE_PYRELANDS_IN_FOUR_SCENES, walk_season_on_the_pyre): *"The Black Ash rain: a violent time with violent plenty right after, and a rare chance to fill your moat against the fire
and fill your water tanks."*

Partial (read 2026-11-13 at a68d89e622). Exists: RM_FE_BlackRain's penalties and fire-out (`src/RimMandrake/Pyrelands/Defs/WeatherDefs/BlackRain.xml`)
and the watered-ash lift after it (`src/RimMandrake/Pyrelands/Source/PyrelandsAshField.cs`, blackRainWaterHours). Missing: the
filling. FlowWorks liquid tanks fill only over the liquid net (`src/RimMandrake/FlowWorks/Defs/LiquidTypes/ThingDefs/RM_LiquidTank.xml`);
nothing catches rain. A limited water body's refill is ooze x (1 + 3 x rainRate) (`src/RimMandrake/FlowWorks/Source/RM_StockMath.cs`
RefillPerDay): about 0.06 fill units a cell over a 2.4 h black rain, and a moat dug dry into ash is likely not a body at all
(guess ~65%, unread). Owed: (1) Designer pass on how much a black rain fills (an open-sky tank, a dug moat or canal on the
Pyrelands) and whether it is Pyrelands-only or any heavy rain; (2) the build; (3) a Mod Setting per the superb-settings rule.
Census and walk criteria: `D:\ClaudeWork\rimmandrake\conductor\cards_20261113_am\walk_season_criteria.md`.

Acceptance test: none, the fill amounts are unspecified until the Designer sets them; the Designer's spec writes the red-first
test (a FlowWorks kernel row: N hours at rainRate 1.1 fills an open tank and a dug moat by the stated amount).
