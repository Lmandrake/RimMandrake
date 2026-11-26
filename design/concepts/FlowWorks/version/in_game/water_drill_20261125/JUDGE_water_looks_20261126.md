# Judge: FlowWorks water looks in situ, 2026-11-26 (delegated look, first and full inspection)

Judge: claude-opus-5-5, blind (made none of this). The standard: `design/concepts/FlowWorks/version/water_by_depth_target.json`
(FIRM/BLEND law), `design/RimMandrake/art_judge_brief.md`, `standing_rulings.md` §The judge refuses flaws, not polish.
Evidence: `after_st17_19.png`, `after_st20_22.png`, `after_st22.png`, `after_st28_33.png` (fix build), `before_st20_22.png`
(parent, for comparison only), all in this folder, ArchSmall, owner's walk save of 2026-11-25.

Station map (checked, not assumed): station 17 (0.2 m) is the 5x1 strip west of the square pits
(`in_game/visit_13/SUMMARY.md` line 56: "the 0.2 m strip reads 0.20 m (400 L) on all five squares"); 18-22 are the five
3x3 pits (0.5 / 1 / 1.5 / 2 / 5 m); 23 is the dry pit. The chain was confirmed by matching pit colours across the
overlapping frames and the hole feature shared by `after_st20_22.png` and `after_st22.png`. Stations 28-33 by
`walk_brief/station_principles.md` rows 28-33 (31 = 0.5 m in a 4 m hole, 32 = 1 m in 4 m, 33 = 2 m in 4 m, swimmer).

## Measurements (centre 60% of each pit, full-resolution capture, 0-255)

| station | water | mean RGB | floor texture sd (L) | target law over this wet floor |
|---|---|---|---|---|
| 17 | 0.2 m | 42 47 61 | 3.6 | 40 43 52 |
| 18 | 0.5 m | 39 48 66 | 3.1 | 38 44 56 |
| 19 | 1 m | 33 46 69 | 2.3 | |
| 20 | 1.5 m | 28 45 74 | 1.8 | |
| 21 | 2 m | 25 45 80 | 1.2 | 32 47 74 |
| 22 | 5 m | 19 50 98 | 0.7 | 27 51 89 |
| 23 | dry | 72 53 34 | 6.5 | (the floor) |

Target column: lerp(dry floor x 0.70 wet darkening, body colour 24 52 96, hides(m)), from the target JSON.
The red channel falls and the blue channel rises with depth at every step, and the floor texture fades at every step.
In game the blue channel sits about 10 above the law at every depth.

## Call 1: POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD, A8 "the thin-water look seen in situ": KEEP

- At 0.2 m and 0.5 m the pit floor shows through. They keep 55% and 48% of the dry floor's texture (the law, with
  the wet darkening, gives about 43% and 39%), and the drifting ripple-light net is visible. They read as slate-blue
  water: not brown, so not mud, and clearly paler and greyer than the 2 m and 5 m pits, so not deep water.
- The look deepens with depth at every step from 17 to 22: the blue rises, the red falls and the floor fades, in
  order. There are no seams, stacked bands or square-overlap corners. The parent's stacked strips (`before_st20_22.png`)
  are gone: each pit is one surface, and below 1.5 m the walls show through as one mitred frame.
- Polish: the water is about 10/255 bluer than the law at every depth. That is the owner's own line ("Water look
  opacity is still a bit too blue, but that's polish").
- Polish: 0.2 m and 0.5 m are hard to tell apart (Δ blue 5/255). The target's own judge_polish already notes this, and
  no owner line asks for a wider step.

## Call 2: WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED, A4 (judged against the written target): KEEP

- The 5 m water reads deepest. Station 22 hides the floor completely (texture sd 0.7) and is the densest, most
  saturated navy in the row (19 50 98, against 25 45 80 at 2 m). By luminance it is not darker than 2 m (0.183 against
  0.171). Over this dark wet floor the written law predicts the same (0.189 against 0.181), because the body colour is
  brighter than the wet floor. So this does not break the standard. The deep look now comes from the one sheet at
  hides 0.9, not from a separate tint layer on dug squares. That is the drill's no-second-layer fix.
- Water below the lip (stations 31, 32, 33): the dry wall shows above the line with a soft dark band at the north and
  west walls. A profile across station 31's line goes from 81-85 on the upper wall, through 66-48 near the line, to 34
  on the water (north). The west wall goes from 108 through 49 to 36. The fade is gradual over about 20 px, with no
  step. The corners are mitred and there is one surface. The walls under the water show as one frame. I saw no hard
  seams and no stacked layers.
- Polish: the target's own fallback applies: if the owner wants 5 m darker than 2 m, lower the deep colour's value by
  about 10%. That is tuning, not a broken promise.
- Polish: under the water at 1.5 m and deeper, the north wall face reads a little paler than the floor. This is the dry
  pit's lit face seen through one sheet, not a second layer.

## Not judged

The colonist drawn over station 33's east wall (owner's 6.png). The drill names it as a different cause. It is
outside both criteria.

Refusals: none. Nothing was filed: both calls are KEEP, and the polish lines above block nothing.
