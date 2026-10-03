# GELATINOUSSLIME_SETTINGS_SWITCHES_1 — Mod Settings switches and sliders: the hazard, farm conversion, the wanderers

**Free tier**, `mandrake.rm.gelatinousslime` (`Source/SlimeMod.cs`, `SlimeSettings`). Design: `design/Jawa/worldbuilding/biomes/gelatinousslime_bedazzle_review_2026-10-02.md` §1 (d), §4 row 0b, §8.
Caused by `GELATINOUSSLIME_SCORING_SITTING_1` (turn 1). Ruling: build first, land what was decided (decision taken by question card 2026-10-02 ~14:25 PDT). Underlying ruling: every mod ships superb Mod Settings (owner, 2026-09-12; `MOD_OPTIONS_RETROFIT_1`).

## What exists

Ten `SlimeSettings` fields, each with a reader. **Slimification, field conversion and the visitors have no
switch and no tuning**; the week-long clock, the conversion rate and the arrival rate are `[INVENTED]` constants.

## spec

1. Slimification: on/off, clock length (default = today's ~week).
2. Field conversion (`MapComponent_SlimeFieldConversion`): on/off, rate.
3. The visitors (`MapComponent_SlimeVisitors`): on/off, arrival rate.
4. Defaults = shipped behaviour; all-off degrades gracefully (a body you can stand on).

## criteria

- Each new field has a reader outside `SlimeMod.cs` (offline grep); selftests pass.
- Live: slimification off → an exposed pawn gains no slimification over a day on liquid slime.
