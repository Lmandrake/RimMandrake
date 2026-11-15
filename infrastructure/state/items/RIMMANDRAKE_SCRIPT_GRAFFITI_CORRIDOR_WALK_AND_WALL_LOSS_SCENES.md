# RIMMANDRAKE_SCRIPT_GRAFFITI_CORRIDOR_WALK_AND_WALL_LOSS_SCENES

## spec

Three proof-scene entry points Graffiti's design (design/concepts/Graffiti/scenes.json) names and no script has yet, outside
the twelve unclaimed must-show lines (RIMMANDRAKE_CLAIM_GRAFFITI_MUST_SHOWS_TWELVE_LEFT_BARE owns those):

- `src/RimMandrake/Graffiti/validation.py::scene_spree_corridor`: his flagship (owner OWNER:1794728091811038301, "I'd say
  B"): one colonist's painting spree down a fresh 1x20 corridor, a skilled colonist's script-forced piece mid-corridor (RM_PaintGraffitiJob, no designator, asserted designations 0), a 64 px
  capture held for his review. Start, action, expect, control and restore are in the scene `sc_spree_corridor`.
- `src/RimMandrake/Graffiti/validation.py::scene_wall_loss`: a painted wall deconstructed and another destroyed, both marks
  gone the tick their wall goes; an untouched neighbour keeps its mark (scene `sc_wall_loss`; inventory `inv_wall_loss`,
  proof missing).
- `src/RimMandrake/Graffiti/validation.py::scene_walk_lived_in`: the walk leaf `walk_lived_in`: reload a lived-in save made
  mid-way, repeat a spree, raid then trader, reload, trader then raid (scene `sc_walk`). Needs the lived-in save from
  RIMMANDRAKE_WALK_GRAFFITI_LIVED_IN_WALL_WEEKS_NOT_MINUTES and the raider pressure record from
  RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_LETTER_NAMES_THE_WALL.

Each entry point is built with its offline selftest of any pure part, and its live run recorded (or UNRUN with its
command), per the owner's 2026-11-13 ruling that the test is built with the item.

## acceptance test

Partial oracle (presence, not behaviour), watched failing on the base 2026-11-15 (`missing 3`); expected `PASS`:

    python3 -c "
    import re;t=open('src/RimMandrake/Graffiti/validation.py').read()
    m=[n for n in ('scene_spree_corridor','scene_wall_loss','scene_walk_lived_in') if not re.search(r'def %s\b'%n,t)]
    print('missing',len(m),m); assert not m; print('PASS')"

The behaviour bar is each scene's expect and control in scenes.json, run live; that live half has no offline oracle.
