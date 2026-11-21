## spec
The Suite empty-game adapter (RIMMANDRAKE_ADAPT_SUITE_SCENES_TO_EMPTY_GAME_FLOWWORKS_ONLY) found, on its first real run
(`python3 src/RimMandrake/rimflow/maturation.py certificate Pyrelands --to in_game`, 2026-11-19), that the live chain
`sand_shovel` in `src/RimMandrake/Pyrelands/validation.py` reads PASS on row `sand_carries_the_dig_yield` with nothing
in the game. The row (validation.py ~3201) checks `RM_FE_Ground_Sand`'s dig-yield extension and the Orders patch in the
mod's XML on disk; it never asks the game. The certificate therefore refuses bars `inv_sand_shovel` and
`sand_shovel_yields_glass_sand` at `asks_on_empty_game`. A disk check is honest as an offline test; inside a live chain
it lets a bar read as proved in game when nothing was seen. Make the live chain's rows read FAIL, UNMEASURED or ERROR on
an empty game (move the disk check to an offline chain or test, or make the row ask the game), keeping the check itself.

## refs
file: src/RimMandrake/Pyrelands/validation.py
item: RIMMANDRAKE_ADAPT_SUITE_SCENES_TO_EMPTY_GAME_FLOWWORKS_ONLY

## verify
python3 src/RimMandrake/Utils/scene_empty_game.py --suite src/RimMandrake/Pyrelands/validation.py --chains sand_shovel

## criteria
- A1: that command exits 0 and prints `0 row(s) pass on an empty game` (watched failing 2026-11-19: exit 1,
  `VACUOUS sand_shovel sand_carries_the_dig_yield`).
- A2: the dig-yield and Orders-patch check still runs somewhere (an offline test or chain) and still fails on a
  deliberately broken ScorchableGround.xml.

## acceptance
Acceptance test: `python3 src/RimMandrake/Utils/scene_empty_game.py --suite src/RimMandrake/Pyrelands/validation.py
--chains sand_shovel` exits 0. Watched failing on the commit that lands the adapter: exit 1, one vacuous row.
