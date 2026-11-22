# RIMMANDRAKE_LET_HUGETHINGS_TITANS_WALK_OVER_WALLS_PHASE_TWO

Filed 2026-11-22 by the HugeThings ticket sweep (`RIMMANDRAKE_SWEEP_HUGETHINGS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE`).
Sweep record: `D:\ClaudeWork\rimmandrake\conductor\ticket_sweep_20261122\HugeThings.md`.

**Version: next.** His card of 2026-10-19 put the step-over in phase 2 ("break through now (walk-over phase 2)"). It is an
addition (Divergent): phase 1, "breaks through", ships and passes the bar `titan_crossing_destroys` without it.

## spec

Design: `design/RimMandrake/big_creatures_walls_and_slots_2026-10-18.md` (option C, "true step-over"). When phase 2 lands,
"breaks through" becomes "walks over, leaving the wall damaged", for the same trample budget. A very large creature sees
a thin wall as something it steps over, damaging it as if it were an object. A thin passage through a mountain is not
stepped over.

The risk named in the design: step-over needs per-creature walkability of walls, as request-owned, immutable data handed
to 1.6's threaded path jobs (a swap-and-restore can restore before the job runs), with a main-thread recheck of each
crossing. Phase 1 (squeeze, breaking through, thickness ladder, scrape, restlessness, roof factors) is built and on
origin (`6a540188a4f7`; `src/RimMandrake/HugeThings/Source/Titanic/WallsSlots/`).

## Acceptance test

None, the step-over is not specified to a testable contract yet: the pathing design (how walkability reaches the threaded
path job) is open. Write the rows with that design. The design's §7 canyon-lane and thickness-ladder scenes are the
starting point, each watched red on the phase-1 build first.

## Merged into this ticket (2026-11-22)

| item | class | one line |
|---|---|---|
| `BIG_CREATURES_DESIGN_WALLS_AND_SLOTS` | DONE (phase 1) | phase 1 built on origin; its unbuilt phase 2 is this ticket; its phase-1 live rows (A2-A8) are owed only where a validated bar needs them (`RIMMANDRAKE_PROVE_HUGETHINGS_BARS_LIVE_SIXTEEN_TICKETS_ONE_RUN`) |

## His words on the merged items (word for word)

- 2026-10-18 (`BIG_CREATURES_DESIGN_WALLS_AND_SLOTS`): "Let's talk about this. A very large creature (say 10 cell) may see
  a narrow slot in a wall as 'something way down there, I don't care' and simply walk over a wall, damaging the wall as
  though it were an object. This would not be true of a thin passage through a mountain. If a large creature is trapped
  by thin wooden walls around it, it walks through them effortlessly; if the walls were as thick as it is, no longer. I
  like squeezing through logic if at least half its width: slowing, not a stop. Do a design pass for the options so we
  can have different ideas for maximum game fun. Do a GPT review of your idea. Likely also involves whether the building
  is roofed or not: a free-standing thin unroofed wall is easier to smash than a roofed one."
- 2026-10-19, by card: "Six §8 questions → package yes; break through now (walk-over phase 2); step over trenches < B/4;
  thrumbo class (B2) ALSO breaks thin walls (default on); roof ×1.5 HP ⅔ damage; squeeze ×2 at half width".
