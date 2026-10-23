# FlowWorks north star — your re-validation (FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING)

**What you are asked:** read the `## north star` section of
`D:\Luke\dev\RimMandrake\design\validation_walks\RimMandrake\FlowWorks.md` (lines 59-452) and, if it says what you want,
say so; an agent then runs `modcheck validate FlowWorks --owner-said "<your words>"`, which records the section's hash.
Nobody edits the section for this review.

**State today:** `DRAFT`, no hash. It has been DRAFT since you released the old record on 2026-10-05 (*"not mature enough to
protect past records"*). Validating it binds **73 must-show and 8 cannot-show bars** at once. All 73 must-show bars have a
check that claims them (measured today), so validating does not refuse the mod for a bar nobody measures.

Since the last validation the section gained the 16 bars you accepted on 2026-10-20 (pit access, bridges, pipes and ports,
the water ladder, trench cover), plus the five below.

## The new bar

- **`still_water_one_surface_height`** — *"every square of one connected body of still water (a pond, lake, canal or pit,
  joined below its surface) stands at the same surface height, to within 1 cm, read from the game's state, not from the
  picture."* Your words it comes from (2026-10-17): *"Yes, north star should check for level surfaces"*.
  **Measured by:** a state read, not a picture. `validation.py` chain `water_level_surface` runs
  `northstar/level_surface_bar.py`, which asks the game for the gap between the highest and lowest water surface in each
  connected body. It passes under 1 cm and reports "could not measure" on a site with no still water. Rivers and the sea
  are excluded.

## The four bars reworded in metres (2026-10-17 depth rebuild)

| bar | what it now says | measured by |
|---|---|---|
| `fill_tier_legible` | dry, under 25 cm, about 0.5 m, 1 m, 1.5 m and 2 m+ of water are **six** looks you can tell apart, whatever the hole's depth | validation_v2 row `S2_fill_clamp` + screenshots: extensions plot B `fill_tier_four_look` (stages F=0..3 in 1.5 m runs), review sheet `S_ladder` |
| `depth_and_fill_jointly_legible` | in one view: 1 m of water in holes 1, 2 and 4 m deep, and 4 m holes holding 0.5, 1 and 2 m of water, all tell apart | v2 rows `S1_dig_ladder`, `S2_fill_clamp` + screenshot: extensions plot B `depth_and_fill_joint_look` (pads 0.5-2 m, half full) |
| `pit_depth_ladder_legible` | undug ground and dry holes 0.5, 1, 1.5, 2, 4 and 8 m deep, side by side, each tell apart without a tooltip | v2 row `S1_dig_ladder` (digs 0.5-2 m) + screenshot: extensions plot H `depth_ladder_look` (pads 0-2 m) |
| `pawn_height_ladder_legible` | a colonist sits lower in each deeper hole down to 4 m, and no lower past 4 m | state read v2 `X1_pawn_height_ladder` + extensions plot H `pawn_height_ladder_look` |

⚠️ **One thing to know before you validate (filed as `LADDER_ROWS_WIDEN_STILL_COUNT_TO_TWO`):** the checks above still use
the old ladder. They dig to 2 m at most (four 0.5 m steps), the "six looks" check stages four, and the pawn-height state
read (`X1`) measures a **hare**, not a colonist. So once validated, these four bars **cannot pass until those checks are widened** to the
metres the bars name (8 m pits, 4 m sinking, six fill looks). Validating now is still fine: a bar that fails because its
check lags is the bar doing its job. But expect them to read red on the next run until the fix lands.

**Nothing to decide but yes/no on the section.** If you want any wording changed, say it in your words; the text is
corrected first and you validate it in the same sitting.
