# Pit depth ladder: lift the 2 m floor, keep the grain, let the north face carry 3 m against 4 m

Item: `RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR`. The art judge refused options A, B and C (note of
2026-11-23 on the item) and ruled: lift the 2 m floor so the ladder has room, spread the doubling ladder over that range, never
darken a floor until its grain disappears, and tell 3 m from 4 m by a north wall face that grows taller with depth.

- `ladder.py`: the two functions. `K(z)` the tone of a floor (and of a face at its top), a multiplier on undug ground;
  `H(z)` the north face. `pitrule.py` (the stepped-pit twin) reads both, so its golden tables carry them into the C# checks.
- `sweep.py img`: sweeps 0.5 to 32 m, writes `img/ladder_table.txt` (tone, CIE L*, face, a verdict for every pair of
  {2,3,4,6,8,12,16} m, his L's arms) and `img/sweep.png` (today against the new ladder at default and close zoom, and the 12
  stepped cases). Exit 1 when a promise fails. Red on the shipped ladder (three pairs alike, grain lost, 2 m not lifted),
  green on the new one.

## What changed

| depth | floor before | floor now | north face before | north face now |
|---|---|---|---|---|
| 0.5 m | 0.62 | 0.85 | 0.084 | 0.084 |
| 2 m | 0.38 | 0.63 | 0.350 | 0.350 |
| 3 m | 0.31 | 0.56 | 0.461 | 0.435 |
| 4 m | 0.27 | 0.51 | 0.498 | 0.520 |
| 8 m | 0.19 | 0.41 | 0.565 | 0.598 |
| 16 m | 0.12 | 0.34 | 0.609 | 0.676 |
| 32 m | 0.08 | 0.29 | 0.620 | 0.701 |

(floor: share of the undug ground's brightness; face: share of a square.)

- The terrain defs RM_Channel_Deep and RM_Channel_Superdeep were lifted (0.58 to 0.69, 0.38 to 0.64): the draw darkens a floor
  with a black shade, so the terrain must be at least as light as the tone. The old law (relief setting off, and floors under
  liquid) draws exactly as before: its shade takes the difference.
- Shallow floors are lighter than before: the 2 m floor could not rise above the old 1.5 m floor otherwise. Under 2 m the
  north face's steep table tells each half metre apart.

## Limits, measured offline

- The pairs are told apart by tone (at least 2 L*) or by the north face (at least 0.07 of a square, 1.6 px at default zoom)
  or by both together. 12 m against 16 m reaches 0.97 of that bar: marginal. Both thresholds are my reading of the judge's
  numbers (1.9 L* read as steps, 1.3 read alike), not a measurement of a player.
- His L's 4 m north arm keeps 0.475 of a square of floor (0.50 before, 0.26 when he called it "incredibly narrow").

## In game (ArchBig, 2026-11-23 00:22-00:30 PST, 23-mod tier of the save, 14 h sun and 2 h night)

- `live_look.py` loads `RM_STEPPED_PIT_12_CASES` from the main menu, digs one-depth 3x3 pits of 2 to 16 m at 80,44 with a
  colonist beside them, and captures default zoom and close, day and night. Run on the shipped build (`before`) and on
  81ee41df54 (`after`); `compose.py` makes the before/after. Captures and both images:
  `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR\` (`ingame\`,
  `BEFORE_AFTER_pit_depth_ladder.png`). Keeper save on ArchBig: `RM_PIT_DEPTH_LADDER_AFTER`.
- Centre-square grey mean / spread [measured, close captures]:

| | 2 m | 3 m | 4 m | 6 m | 8 m | 12 m | 16 m |
|---|---|---|---|---|---|---|---|
| before | 27.1 / 3.6 | 22.8 / 2.8 | 19.9 / 2.3 | 15.3 / 1.8 | 12.5 / 1.8 | 9.8 / 1.1 | 8.5 / 0.8 |
| after | 45.3 / 6.0 | 41.1 / 5.1 | 37.8 / 4.2 | 31.7 / 3.9 | 27.0 / 4.5 | 22.2 / 3.6 | 19.4 / 2.2 |

- `pit_floor_ladder_live.py --origin 80,60`: 5 of 5 rows PASS (`northstar/pit_floor_ladder_result_20261123T002943.json`); the
  grain row reads 2.38 with the relief on and 1.2 on the old law (relief off), so it can go red.
- What I saw: every floor keeps its grain; 2, 4, 8 and 16 m read as four steps; the north face is visibly taller at 8 and 16 m
  than at 2 m. 3 m against 4 m, and 12 m against 16 m, are still close at default zoom (the face step 3 -> 4 m is about 2 px
  there); the art judge decides whether that is enough. At night every floor is dark and no pit shadow is drawn (the moon at
  2 h casts none).
