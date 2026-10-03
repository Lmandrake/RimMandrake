# Slime + Weeping settings work 2026-10-03
Started. Choices recorded below.

## GELATINOUSSLIME_SETTINGS_SWITCHES_1 (code done, build ok, selftest 45/22/0)
Six statics in SlimeSettings: slimificationEnabled, slimificationClockDays (2-30, default 7; scales on-body AND injected
rate by 7/days), fieldConversionEnabled, fieldConversionRate (0.25-4x on cells per pass, probabilistic rounding),
visitorsEnabled (also gates the mapgen seed pass), visitorArrivalRate (0.25-4x on arrival chance).
Slimification off: exposure tick adds no hediff, arrivals/seed not pre-slimified, growth cases return the
wipe-off rate (-0.5/day) so existing film clears. Round-trip: validation.py FIELDS + settings_flip, northstar_mock.

## WEEPINGSTONES_SETTINGS_SLIDERS_1
vhorrinOddsMultiplier (0-3, default 1, multiplies both emergence chances), vizhikEscapeChance (0-0.25, default 0.05),
both in RM_WeepingStonesSettings and read by RM_MapComponent_PoolStock in place of constants; Reset to defaults button.
Validation: settings_sliders chain (default + write/read-back + restore) and mock support; selftest passes.
BLOCKER: truce radius slider (spec 2) lives in RM_EnvironmentalHazardsSettings / RM_WaterTruceExtension, in
src/RimMandrake/EnvironmentalHazards (outside this mod's folder) -> not done; needs its own pass there.
