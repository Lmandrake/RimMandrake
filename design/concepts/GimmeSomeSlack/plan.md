# Gimme Some Slack: plan (stage 3)

Tree `design/concepts/GimmeSomeSlack/tree.json`, sheet `sheet.md`, scenes `scenes.json`, floor `floor.json`. The mod is
built and he walked it (d_owner_walk_verified, 2026-10-16); this plan is one owed change, one instrument and the proof
work, nothing new.

## Owed change (Relentless builds it from the tree)

1. **Modern junctions draw the long power strip** (d_modern_junction_strip, OWNER:1793909100631838579; item
   `GSS_MODERN_STRIP_BUILD_PLUGS_AT_LAST`). In `src/RimMandrake/GimmeSomeSlack/Source/Core/CordBuilder.cs` (PoseJunction)
   the Modern family poses the PowerStrip art at every 3- and 4-way `NodeType.Junction`, each arm ending in a socket; a
   3-way takes two cords plus the strip's own lead. Industrial keeps Junction_T/X; Scrapper and Futuristic unchanged.
   `CordAudit.cs` arm alignment must cover blob junctions too. Leaf `strip_at_every_junction`.

## Order

1. `cord_shape_variation_probe` (instrument, first; item `GSS_SHAPE_PROBE_MEASURE_NO_TWO_ALIKE`): a bridge read of the
   sampled curve per cord edge and an offline pairwise distance table per length class. `cords_never_repeat` waits on it.
2. The owed Modern strip change.
3. Scene entry points (item `GSS_SCENES_BUILD_EVERY_CORD_A_FOIL`): every acceptance, interaction and exploration scene in
   `scenes.json` as a named `scene_<id>` in `src/RimMandrake/GimmeSomeSlack/validation.py` (the walk in
   `northstar/gss_playtest_runner.py`), each with its asserted start, its control and a scene-begin snapshot restore. The
   stage 0 audit found row-based checks with controls only for M14, M19n, theft no-witness, the dive ring and setting
   restores. New controls: never-powered cut (`sc_cut_ends`), planted cross-net cord and adjacent-feed pump
   (`sc_true_to_grid`, his 2026-10-16 phantom case), 2-way bend (`sc_junction_strips`), skipped rebuild
   (`sc_rewire_cost`), unregistered patch (`sc_settings`). The two showcase stagings (`workshop_floor`, `yard_of_masts`)
   hold for his review (`owner_review`).
4. The walk `walk_scavenger_base` on his full list, through Relentless's game_prove lane.

## Proof debt carried from stage 2

- `cost_partial`: the lone-rebuild case (`GSS_SLICE_FIX_LONE_REBUILD_HITS_140MS`, verify partial) is `sc_rewire_cost`,
  lone and burst actions read separately, bar 20 ms (the floor's tick ceiling).
- `switches_partial`: keepWiresOnGravship, cutWiresOnOwnerChange, dripLoops and slideUnder flip in `sc_settings`;
  keepWiresOnGravship also in `sc_gravship` (`GSS_SWITCHES_PROVE_LAST_FOUR_STANDING`).
- `no_repeat_unmeasured`: the instrument above plus a judge agent predicting his eye.

## Reuse

`validation.py` SITE prep and OFF_SITE_RECTS, `validation_aerial.py` four_switches_block, theft_catch and flips_block,
`validation_style.py` s9_runs and s12 style reads, `CordAudit.cs` arm checks, SliceWindow's timer. Captures through
`human_review.py`.

## Risks

- The fixer exemption passes vacuously if the re-stringer's path never crosses the sparking cell: `sc_shock` asserts the
  crossing.
- A connectivity read on the conduit graph would pass a lying drawing: `sc_true_to_grid` reads the drawn cords.
- Gravship flight on a quicktest is unreliable: `sc_gravship` is live_minimal.

## Showcases

`workshop_floor` (6 new) and `yard_of_masts` (5 new), overlap 0; the rest by their own scenes (`coverage_rest`). Showcase 1
is the workshop floor, his pick by card 2026-11-05 (`d_flagship`, OWNER:1793950666234031543).
