# FlowWorks north-star sitting — one page (prepared 2026-10-18)

Item: `FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING`. Bars: `design/validation_walks/RimMandrake/FlowWorks.md`
(`## north star` is hash-bound and DRAFT; `## proposed bars` just below it is not). At the sitting he does two things:
(1) reads the five changed bars and says whether each is right; (2) accepts, rewords or cuts each proposal. Then he
validates the whole section in the same sitting (`python3 src/RimMandrake/Utils/modcheck/cli.py validate FlowWorks
--owner-said "<his words>"`). Validating judges the WORDING; whether the game passes each bar is a separate live walk.

**Saves** (in `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\`):
- **REVIEW** = `FlowWorks_OwnerReview_2026-10-18.rws` (19:44, from `src/RimMandrake/FlowWorks/northstar/owner_review_stage.py`).
  Its rows are ladders, spikes, gates, shallows, sprinklers by the script's default; which rows this file actually holds
  is UNMEASURED (no run record names it). `FLOWWORKS_OWNER_REVIEW_20261018_1942.rws` is a 2-minute-older twin.
- **LAKES** = `RM_fw_lake_floors_flat_hills_mountain_20261018.rws`.
- **OLD** = `RM_FW_walk_20261016b` with `src/RimMandrake/FlowWorks/northstar/review/map/KEYSHEET.md`: pre-rebuild
  (depths "1 to 4", whole notches). Good for the unchanged bars, wrong for the metre bars.
- **BARS** = the `bars_*` rows of `owner_review_stage.py` (default sweep; `live_session.py` B9 passes them). Written 2026-10-18, **not yet run live**: a save of them exists only after FOUNDRY's next owner-save run (`FLOWWORKS_ROWS_FILL_STAGE_THE_UNSEEN`). Rows: `bars_joint`, `bars_dry`, `bars_trench`, `bars_access`, `bars_bridges`.
- **NONE** = no site can stage it (named per row).

## 1. The five changed bars (inside the section — his words decide the text)

| bar | in plain words | what he looks at | where |
|---|---|---|---|
| `fill_tier_legible` | Six water looks tell apart: dry, under 25 cm, 0.5 m, 1 m, 1.5 m, 2 m+ | six pits with water at each depth, side by side | REVIEW + BARS `shallows` row (dry 1 m hole, then 0.2/0.5/1/1.5/2/5 m). The under-25 cm look is still owed art, so today it matches 0.5 m: the bar fails until that art lands |
| `depth_and_fill_jointly_legible` | Same water in a shallow and a deep hole looks different; different water in the same hole looks different | 1 m of water in 1, 2, 4 m holes; 0.5/1/2 m of water in 4 m holes | BARS `bars_joint` |
| `still_water_one_surface_height` | Every square of one still pond, lake, canal or pit stands at the same height, to 1 cm. A state read, not a picture | the per-body surface-gap diagnostic, not the screen | REVIEW shallows row (the 0.2 m strip levels); live run of `northstar/water_scenes_walk.py` S5/S6 |
| `pit_depth_ladder_legible` | Dry holes 0.5, 1, 1.5, 2, 4 and 8 m deep each look different from each other and from flat ground | a row of dry holes at those depths | NONE (REVIEW's ladder pits are all one depth); BARS `bars_dry` (0.5/1/1.5/2/4/8 m) |
| `pawn_height_ladder_legible` | A colonist sits lower in each deeper hole up to 2 m, and no higher than that in anything deeper | a colonist standing in each hole of that row | BARS `bars_dry`, a colonist in each hole (and `bars_joint` for the wet 2 m+ holes) |

Also changed: one sentence of the section's opening prose now says a bar may be a state read "where the bar itself says
so" (it used to say every bar is checked by looking, which the level-water bar is not).

## 2. Proposals (outside the section — he accepts, rewords or cuts)

| proposal | in plain words | what he looks at | where |
|---|---|---|---|
| `limitless_body_marked` (R13) | Water that never runs dry says so in the readout; drainable water doesn't | hover a river/sea square, then a pond | LAKES or any map with a river |
| `half_metre_water_reads_as_silt` | 0.5 m is grey-brown silt; 1 m is the first blue | the 0.5 m and 1 m pits | REVIEW, shallows row |
| `deep_water_pawn_swims` | A colonist in 2 m+ water is drawn swimming at the surface | a colonist in the 2 m and 5 m pits | BARS `bars_joint` (colonists in the 2 m-water and 1 m-in-4 m holes) |
| `trench_wall_cover_shown` | Shooting at someone in a trench shows "Trench wall: blocks N%", more for chest-deep | hover a shot at a waist-deep and a chest-deep pawn | BARS `bars_trench` (1 m and 1.5 m pawn, shooter 8 squares east; the proof read lands in the run notes) |
| `raiders_never_shelter_in_a_cage` | Raiders take trench cover only where they can climb out. State read | the raid run's record | NONE (raid row of `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH`) |
| `wall_ladder_rides_on_rails` | The permanent ladder hangs on wall rails, raised and lowered, all four walls | four pits, a lowered and a raised ladder in each | REVIEW, ladders row |
| `portable_ladder_leans_on_its_wall` | The carry ladder leans on its wall; too short, it lies flat | one in a 2 m pit, one against a 4 m wall | BARS `bars_access` |
| `climbing_gear_reads_as_kit` | Climbing gear reads as ropes, hooks and claws in one kit | the item on the ground and worn | BARS `bars_access` (item on the ground, a geared colonist in a 4 m pit) |
| `geared_pawn_climbs_out` | A colonist with gear climbs out of a sheer pit, no ladder | before/after shots | BARS `bars_access` (geared and ungeared colonist side by side; the climb-out itself is a live walk) |
| `jump_into_pit_lands_unhurt` | A jump-pack jump or skip into a pit hurts nobody. State read | the pawn's health after | NONE |
| `geared_pawn_scales_built_wall` | Gear lets a pawn climb over an unroofed wall; no gear, no climb | before/after shots | NONE: no bridge call poses a mid-climb and the build is in progress (`WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS`) |
| `suspension_bridge_reads_hung` | A suspension bridge looks hung between anchors, not a floor or a vanilla bridge | one built over a pit | BARS `bars_bridges` (rope/timber/steel/heavy, railings on and off; art first pass `6af7c53432`) |
| `pawn_walks_under_deck` | A colonist on the pit floor walks under the deck | before/after shots | NONE (underpass not built yet) |
| `pit_cover_unlike_bridge` | A pit cover passes for ground; a bridge looks like a bridge | a cover next to a bridge | BARS `bars_bridges` (east end), `bars_access` |
| `pipe_meets_building_centre` | Pipes and hoses look like they run in under a tank or pump to its middle | pipe and hose into a tank, pump, tap, sprinkler | REVIEW sprinklers row; the hoses row (default sweep of the owner save now) |
| `pump_port_takes_pipe_and_hose` | The pump has a clear port on every side, taking a pipe and a hose at once | the pump with a pipe and a hose on it | hoses row (`owner_review_stage.py --only hoses`; in the next owner save) |
| `hose_and_pipe_girth_sensible` | Hose and pipe look sized for each other, the port and a colonist | the same hoses row, colonist beside each | hoses row, `HOSE_PIPE_WALK_JUDGE_GIRTH_IN_GAME`; his numbers for "sensible" are asked here |

## 3. The other 60 bars

Unchanged wording. He re-reads them only if he wants to; the validate covers the whole section. OLD + its keysheet shows most
of them in game.
