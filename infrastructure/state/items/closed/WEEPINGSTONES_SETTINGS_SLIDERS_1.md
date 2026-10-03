# WEEPINGSTONES_SETTINGS_SLIDERS_1 — real Mod Settings sliders for the Weeping Stones: truce radius, vhorrin odds, vizhik escape chance

Caused by `WEEPINGSTONES_SCORING_SITTING_1` (turn 1). **Free tier**, `mandrake.rm.weepingstones` and
`mandrake.rm.environmentalhazards`. Design: `design/Jawa/worldbuilding/biomes/weepingstones_bedazzle_review_2026-10-02.md` §1 (d), §4 row 0, §8. Ruling: build first, land what was decided
plus the giant's story (decision taken by question card 2026-10-02 12:53 PDT; card text: *add real sliders to
its settings*). Law: every mod ships superb Mod Settings (owner, 2026-09-12; `MOD_OPTIONS_RETROFIT_1`).

## What exists

- `RM_WeepingStonesSettings` has one field, `stockedPoolsEnabled`.
- Constants in `RM_MapComponent_PoolStock.cs`: `VhorrinEmergenceChanceCrowded` 0.02, `VhorrinEmergenceChanceCrashed`
  0.01, `VizhikEscapeChance` 0.05 (per pulse; `PulseIntervalTicks` 2500).
- Truce radius: XML field `RM_WaterTruceExtension.radius` (default 10).

## spec

1. Sliders (defaults = shipped behaviour): vhorrin odds multiplier (0 to 3), vizhik escape chance (0 to 0.25),
   both in `RM_WeepingStonesSettings`, read by `RM_MapComponent_PoolStock` in place of the constants.
2. Truce radius slider (3 to 25 cells) in `RM_EnvironmentalHazardsSettings`, as a multiplier or override of the
   XML field so every truce reader (`IsTruceWater`, retribution, `WEEPINGSTONES_TRUCE_HUNT_SUPPRESSION_1`) sees one radius.
3. Tooltips say what each does in play; Reset to defaults.

## criteria

- Settings screen shows the sliders; values persist across a restart.
- Vhorrin odds 0: no vhorrin emerges from an overcrowded pen over 20 pulses; vizhik 0: no escape (controls at default).
- `IsTruceWater` honours a changed radius (bridge read at radius 5 vs 20).
