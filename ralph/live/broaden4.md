# FlowWorks (RimWorld 1.6 mod): pits and depth — broaden, Artisan pass 4

## What the player should get
The owner's player story (2026-11-04), the journey I am judged on: "Raiders run down a passage towards the colony's doorway,
only to have the first two warriors plunge down through a covered pit trap into a series of spikes. Trapped and wounded, the
other raiders immediately begin hacking down saplings to build a makeshift ladder to retrieve them, but the defenders standing
on the other side begin peppering them with arrows while they try. The raiders are driven off, leaving some injured prisoners
already in a tidy prison." Also his rule (2026-10-31): raiders only fill shallow pits; deep pits they must go around or stand
and shoot.

The 28 must-show lines of this aspect (pass/fail by looking at ordinary play at play zoom):
depth reads (0.5/1/1.5/2/4/8 m holes each distinguishable; a pawn sits lower in each deeper hole, no lower past 4 m; the same
pawn drawn lower/higher as it steps deeper/shallower), the pit reads as a hole with wall faces, not vanilla's spike trap, reads
as one place at size; its occupant reads as down in it, occupied vs empty at a glance, walls rise ~a fifth over the head; a
covered pit looks like the ground at play zoom but shows a slight seam at max zoom; ladder raised vs lowered legible; sluice
gate open vs shut legible; spikes visibly project; a "trench wall" cover line on hit chance, larger chest-deep than waist-deep;
raiders never shelter in a pocket they can't leave; the permanent ladder on rails on each of four walls (raise from below or
above, lower only from above); a portable ladder leans on its wall, lies flat if too short; climbing gear reads as a kit, on
ground and worn; a geared colonist climbs out of a sheer pit; jump pack into a pit lands unhurt; geared pawn scales a built
wall, ungeared can't; suspension bridge reads hung between anchors over a hole; a pawn walks under a deck; pit cover never
looks like a bridge; digging one square by shovel takes hours, raiders carry fill in first. Cannot show: a pawn snared upright
on a labelled tile; the bare excavation reading as a placed building.

## What I have tested and how (all on quick-test maps, game spawned by bridge; nothing on a lived-in colony)
- The story, once (last pass), on a STAGED layout: walls built by god-mode round the colonists, a 3-wide walled passage south
  of the one doorway, a 3x2 pit 2 m deep across it, spikes and woven-scrap covers, three drafted tribal archers just north of
  the pit, a 540-point tribal raid fired at the map edge. Seen: one raider fell, one began chopping for a rescue ladder, then
  1,200 ticks later the whole raid left "satisfied with the damage done" — vanilla's 900-damage exit, reached by raiders
  bashing the passage walls plus our missed arrows. This pass I built a hold on that exit while a rescue is under way (capped)
  and fixed 8 review findings in rescue and the bed-less pit prison; not yet replayed.
- Depth look: a contrast sheet of 0.5..8 m 2x2 holes each with a drafted colonist (attached). Staged.
- Ladders, portable ladders, sod over a covered pit, spikes, timber bridge with a colonist under it: staged 5x5/3x3 holes on a
  quick-test map (look4 sheets attached). The wall ladders were 0.6-cell sprites, the south one invisible; I have just rebuilt
  them to print down the wall face at the hole's drawn depth (lowered: in the hole on its rails; raised: out on the ground
  beyond its rim, bare rails left in the hole). Not yet seen.
- Costs: cover scan 0.30 ms on a 400-cover deck; cliff-mask rebuild 1.96 ms for a 900-cell hole after reload; per-map
  invalidation holds across two maps.

## What I plan next
Deploy; replay the story on the same staged layout in the oblique look; shoot the new ladders on all four walls; then a second
story with no walls: a covered pit line across open ground in front of an ordinary quick-test colony, raid, watch.
