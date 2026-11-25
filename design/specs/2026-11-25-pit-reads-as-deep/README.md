# A pit should look as deep as it is (FlowWorks 0.2.0)

Item: `RIMMANDRAKE_DEEPEN_FLOWWORKS_PIT_LOOK_HE_SUSPECTS_READS_SHALLOW`. His words, 2026-11-24, approving the stepped-pit
look and `RM_PIT_DEPTH_LADDER_AFTER` for 0.1.0: *"please file a ticket for the NEXT version that we need to make pits look
as deep as they are... they read way too shallow compared to their actual look (I suspect). But for now both of these looks
pass."* This is Divergent work for FlowWorks 0.2.0. It moves no 0.1.0 bar.

## The measurement

`measure.py` turns each depth cue that the build draws back into the depth that it shows, for one-depth 3x3 pits of 2 to
16 m. It writes `table.md` and `readings.json`. With `--check` it writes nothing and exits 1 when the offline twin's constants (pitrule.py,
ladder.py) differ from the C# build (`RM_PitReliefMath.cs`), so it cannot describe a look that is not shipped (seen red on a
planted `SHADOW_K` change, green on the build, 2026-11-25).

Scales: a colonist draws 1.29 squares tall [measured, from `after_ladder_close_02m.png` of the depth-ladder live look,
ArchBig 2026-11-23]; a person is 1.75 m [assumed]; so one square of upright draw shows 1.36 m. A square is 1.41 m a side.
The sun is the pick's (elevation 55 degrees, slope 1).

| true depth | north face (squares) | face / colonist | face reads as | shadow drawn (sq) | shadow true (sq) | shadow reads as | floor in view, drawn | floor in view, true |
|---|---|---|---|---|---|---|---|---|
| 2 m | 0.35 | 0.27 | 0.5 m | 0.20 | 1.0 | 0.4 m | 88% | 51% |
| 4 m | 0.52 | 0.40 | 0.7 m | 0.32 | 2.0 | 0.6 m | 83% | 2% |
| 8 m | 0.60 | 0.47 | 0.8 m | 0.51 | 4.0 | 1.0 m | 80% | 0% |
| 16 m | 0.68 | 0.53 | 0.9 m | 0.84 | 7.9 | 1.7 m | 77% | 0% |

(3, 6 and 12 m in `table.md`.)

What it says [measured against the build's constants; the scale rests on one capture and an assumed person]:

- **He is right.** No drawn cue shows more than about 1.7 m, at any depth to 16 m.
- **The north face is shorter than the colonist beside it at every depth.** A 16 m pit is nine people deep; its far wall
  draws half a person tall. Depth grows 8 times from 2 to 16 m; the face grows 1.9 times.
- **The cast shadow is 5 to 9 times too short.** At the same sun a real 16 m wall throws its shadow 7.9 squares; the build
  draws 0.84. In a 3x3 pit a real shadow covers the whole floor past about 6 m at that sun.
- **The floor stays in full view.** 77 to 88% of the pit shows floor at every depth. On the colonist's own upright scale,
  a 3x3 pit deeper than about 4 m shows no floor at all, only wall.
- **Tone has run out.** Each step past 4 m darkens the floor by 1.0 to 2.3 L*; three of those four steps are under the
  2 L* that the depth ladder took as told apart.

## What the look cannot do

The true picture hides the floor of every 3x3 pit past about 4 m. A pawn trapped in a pit must stay in sight
(`pit_trapped_reads_as_trapped`, a 0.1.0 bar), and so must liquid on the floor. So the 0.2.0 look is a compression that
still reads as deep, not the true projection.

## Design directions (for the Designer; a judge picks among mocks, he judges the result at his walk)

1. **A true shadow** (recommended). Cast length is depth / tan(sun elevation), clipped by the pit's own walls. A deep
   pit's floor is in shadow for most of the day and lit only in a strip near noon. This is his Direct Sun principle,
   *"low sun is less intense AND produces longer shade"* (2026-10-19): geometry, not a number per depth. The floor stays
   visible, dark with its grain. The build's march reads a 7x7 window and caps the slope at 2, so a shadow of up to 8
   squares needs an analytic per-wall shadow, not a longer march.
2. **Less sky at the bottom** (recommended, with 1). A floor's ambient light falls with the share of sky it can see, which a
   narrow deep pit almost loses. This replaces the depth-tone ladder with a geometric one: a 1-square shaft at 4 m reads
   darker than a 9x9 pit at 4 m, as it should.
3. **A face that outgrows the colonist.** The north face reaches a colonist's height near 4 m and about half the pit's span
   at 16 m, cut by strata bands at a fixed depth interval so the eye can count down. It costs floor in view; the narrow
   north shelf (`RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM`) must still show.
4. Not recommended: draw pawns and things smaller at the bottom. It breaks RimWorld's flat drawing of pawns and makes a
   trapped pawn harder to read.

Before building: read `design/RimMandrake/standing_rulings.md` §A pit is a SUPERDEEP cell and §Direct Sun.

## The bar (proposed, an experience; the Designer adopts or rewrites it when 0.2.0 opens)

> At default zoom by day, a player who sees a dug pit beside a standing colonist puts its depth in the right band without
> reading a number: shallower than the colonist, a few colonists deep, or a deep shaft; and a pawn or liquid on its floor
> stays in sight.

It pins no tuning number. It must not pass by a pit that reads deep only through a label or overlay, or by a floor so dark
that a trapped pawn is lost.
