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
