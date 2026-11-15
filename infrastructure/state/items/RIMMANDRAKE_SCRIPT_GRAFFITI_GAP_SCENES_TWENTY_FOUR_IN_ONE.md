# RIMMANDRAKE_SCRIPT_GRAFFITI_GAP_SCENES_TWENTY_FOUR_IN_ONE

## spec

Graffiti's coverage judge (rm-coverage-judge-1794730911, design/concepts/Graffiti/coverage_verdict.json) found 24 gaps;
the Designer's stage-3 run rm-role-designer-1794732988 fixed them in design/concepts/Graffiti/scenes.json. This item builds
the script parts those fixes name that no other item owns. Each scene's start, action, expect, control and restore are in
scenes.json under the scene id; read them there, they are the spec.

New entry points (validation.py):

- `src/RimMandrake/Graffiti/validation.py::scene_weathered_raid_mark` (scene `sc_weathered_raid_mark`): age a raid exit
  mark past its RM_GraffitiKernel.WeatherDays (by setting its placed tick back); assert it despawns, RM_Graffiti_EnemyClaim
  ends for its viewers and that faction's raider pressure lifts. Control: a same-age roofed mark outlives it.
- `src/RimMandrake/Graffiti/validation.py::scene_breach_bias_raid` (scene `sc_breach_bias_raid`): a walled site with a
  colonist-painted RM_Graffiti_WarningGlyph (breachLure) on a wall that is NOT vanilla's breach pick (asserted by calling
  BreachingGrid.FindBuildingToBreach with bias off); with bias on the pick is the glyph's wall and a breaching raid's lord
  attacks it. Control: the same wall without the glyph, bias on, keeps vanilla's pick.

Additions to existing entry points (graffiti_v1_live_proof.py and validation.py):

- `graffiti_v1_live_proof.py::A3` (`sc_sigil`): a meme-gate sub-case (meme present vs absent decides a meme-gated glyph in
  the pool), the painter's ideo and colour asserted at start, zero red errors asserted at start.
- `graffiti_v1_live_proof.py::A4` (`sc_going_over`): the control case, the same Tag_A on a second cell with no enemy
  painter for the same ticks, stays.
- `graffiti_v1_live_proof.py::A6` (`sc_scrub_protection`): the ordered scrub goes through Designator_ScrubGraffiti and
  WorkGiver_ScrubGraffitiDesignated; an undesignated protected neighbour stays.
- `validation.py::wall_closeup` (`sc_wall_closeup`): the edge-on control (a cell whose only wall is east or west gets no
  mark), the far-side control (a cell whose only wall is south of it: a paint order and a pool pick leave no mark; expected
  to fail until RIMMANDRAKE_REFUSE_HIDDEN_FACE_PAINT_ORDER_OUTLIVED_ITS_WALL lands) and the wall-top assertion (option D:
  the paint climbs over the crease).
- `validation.py::gallery` (`sc_gallery`): the planted vanilla filth cell the judge must call dirt, and two vanilla dirt
  cells it must call alike.
- `validation.py::beauty_pair` (`sc_beauty_pair`): the side-swapped repeat and the identical-tally pair.
- `validation.py::breach_bias_toggle_flips` keeps its read-back; the behaviour lives in `scene_breach_bias_raid`.

Scenes whose entry points other items own carry new assertions too: RIMMANDRAKE_CLAIM_GRAFFITI_MUST_SHOWS_TWELVE_LEFT_BARE
(sc_art_skill, sc_own_fun, sc_rereads, sc_mockery, sc_tribute_memorial, sc_answer_wall, sc_raid_retaken, sc_fights,
sc_temperament, sc_settings), RIMMANDRAKE_SCRIPT_GRAFFITI_CORRIDOR_WALK_AND_WALL_LOSS_SCENES (sc_spree_corridor, sc_walk)
and RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_LETTER_NAMES_THE_WALL (sc_raider_pressure). Those items' builders read
scenes.json; nothing here duplicates them.

Each entry point is built with its offline selftest of any pure part, and its live run recorded (or UNRUN with its
command), per the owner's 2026-11-13 ruling that the test is built with the item.

## acceptance test

Partial oracle (presence of the two new entry points, not behaviour; the additions are live behaviour), watched failing
on the base 2026-11-15 (`missing 2`); expected `PASS`:

    python3 -c "
    import re;t=open('src/RimMandrake/Graffiti/validation.py').read()
    m=[n for n in ('scene_weathered_raid_mark','scene_breach_bias_raid') if not re.search(r'def %s\b'%n,t)]
    print('missing',len(m),m); assert not m; print('PASS')"
