# TWILIGHT_BAND_DECIDE_HOW_FAR_DUSK_REACHES

Filed 2026-10-20 (FOUNDRY, offline glow-consumer audit). Spec: `design/RimMandrake/glow_consumers_2026-10-20.md` §B.

"Light follows the sun" ships with a 6° dusk band (`tidalTwilightBandDegrees`, CreatureBehaviors Mod Settings). The
biome sheets call places twilight that sit deeper than 6° below the horizon:
- The Sump: *"permanent deep twilight"*, median −10.6°. At a 6° band, 61% of its tiles read glow 0.
- The Twilight/Forsaken Crags: arc 100–116, median −18°. At 6°, 98% read glow 0.

Real twilight goes to 18° (civil 6°, nautical 12°, astronomical 18°). Median glow at a 6 / 12 / 18° band: Sump
0.00 / 0.02 / 0.22 (before its ×0.55 biome multiplier), Wasteland 0.00 / 0.18 / 0.37, Crags 0 at all three. Every band
stays psychologically Dark (< 0.3) and too dim for sun-needing plants. Day-side rules do not change.

Card question: *"How far below the horizon should dusk light reach? 6° (civil; the Sump and Crags are pitch black) /
12° (nautical) / 18° (astronomical; the Sump gets a faint glow)."* Only the default changes. One constant
(`RM_TidalSunGlowMath.DefaultTwilightBandDegrees` plus the settings default), the selftest, and the Python port in
`world_physics_audit.py`.

NEXT: put the 6/12/18° dusk-band card to the owner, then set the default he picks in RM_TidalSunGlowMath and its port.
