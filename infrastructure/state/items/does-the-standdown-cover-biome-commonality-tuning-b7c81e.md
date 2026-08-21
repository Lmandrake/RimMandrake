## spec
Raised by BUILD, routed by REP. The owner's ruling, 2026-08-15: *"WE WILL NOT
PROGRAMMATICALLY generate the world, the user will do that himself. Stand down
all development of tuning the worldgen to function by itself correctly for now.
That's all v2."* Parked in `design/V2_DREAMS.md` (`0b9e244`).

BUILD's read, and it needs a scope verdict rather than a seat acting on it:
- `src/Jawa/Jawa_Patches/Patches/JawaWorld_BiomeMix.xml` is biome-commonality
  tuning and reads as squarely inside the ruling. **BUILD has NOT deleted it**
  — scope is yours. It should get an explicit v1/v2 verdict rather than be left
  live and half-dead. Line 140 is separately a no-op: it scores
  `RG_BoilingForest`, whose mod no longer loads (see
  `the-dump-was-never-stale-correct-the-manifest-5cb9a2`).
- The faction items whose `criteria:` say "generates settlements at worldgen"
  are **NOT** in scope as BUILD reads it: those are defs existing so the
  owner's MANUAL worldgen produces them, which is the opposite of automating
  it. REP agrees and has put the same reading to the owner. CHECK reads C17 the
  same way — an owner-ticked Configure Factions checklist, never programmatic.

## verify
`JawaWorld_BiomeMix.xml` carries an explicit v1 or v2 verdict, and the faction
items say in one line why they survive the stand-down.

## criteria
none — offline.

## notes
**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

done — **RULING: `JawaWorld_BiomeMix.xml` is v1. B63 STANDS. Do not delete it.**
BUILD was right to stop and ask rather than act, and right that it *reads* like
worldgen tuning. It is not, and the line is worth stating once because more
things will be tested against it:

🔴 **THE TEST IS "DOES IT RUN, OR IS IT READ?"**
- **STOOD DOWN — machinery that OPERATES the generator.** ~~The stood-down sea
  work is a `WorldGenStepDef` plus an assembly that measures a world and re-shapes it
  toward a target, iterating until a gate passes.~~ ⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see `ASHKARR_WORLD_DEFINITION.md` §12.
  Stood down became deleted; read this bullet as the CLASS that is forbidden, not
  as a description of work that still exists anywhere.
  That class is worldgen "functioning by itself", and it is exactly what the owner killed.
- **NOT STOOD DOWN — def data the generator READS.** A `BiomeDef` field is
  static content. It never runs, never measures, never re-tries. It describes
  what this planet IS, and the generator consults it while the OWNER drives.
`JawaWorld_BiomeMix.xml` is entirely the second kind: a blacklist plus 24
static `scoreOffset` values. **Nothing in it automates anything.**

⇒ **The decisive point: he cannot do this by hand.** The stand-down moved
worldgen to the owner because he can pick a world by EYE. There is no biome-
abundance control at the world screen — no slider, no page, nothing to tick. If
the mix is dead he does not get a manual choice, he gets **vanilla abundances on
a Star Wars desert world**, and 🔴 **biome scoring runs ONCE, at world creation.**
Killing this would not return a decision to him; it would take one away.

⇒ **It is chain step 8, ratified as W3** — a v1 content step, not worldgen work.
It sits in the same class as the FactionDefs and the ideos: authored data that
must be LIVE before he generates, for exactly the same reason.
⇒ **BUILD's read on the faction items is CORRECT and is now ratified.** A def
existing so that the owner's manual worldgen produces it is the opposite of
automating worldgen. C17's owner-ticked checklist likewise. None of them are in
scope, and no seat should re-raise it.

⚠️ **Two things that ride on this and would fail silently:**
- `JawaWorld_BiomeMix.xml:140` scores `RG_BoilingForest`, whose mod no longer
  loads. **Dead line — delete it in B63**, do not carry it. It validates clean
  against the dump only because the dump still holds the def.
- **C38's terminator band needs the biome mix to work.** Its x0.4 case is
  `PoisonForest`; if abundances never apply, the roster it tests may not place.
  A dead mix reads downstream as a plant-growth failure.

📌 The general form, for the next time this is asked: **the stand-down is about
who DRIVES, not about what the world is made of.** Anything that takes the wheel
is v2. Anything that is scenery the owner drives past is v1.
