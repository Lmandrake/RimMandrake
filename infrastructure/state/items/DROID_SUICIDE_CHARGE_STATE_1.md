# DROID_SUICIDE_CHARGE_STATE_1

Split out of `DROID_FACTION_LOADOUTS_1` (packet C1) on 2026-09-08, deliberately
and with the reasoning recorded — not forgotten.

## spec

§3.2 of `design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` asks the Junker
row for a "`MentalState` charge-and-detonate": a droid that *chooses* to run at
the nearest enemy or wall and destroy itself, rather than one that explodes when
something else kills it.

C1 shipped the second thing, because it already existed and already satisfies the
owner's actual words. Ruling 2, verbatim: *"Junkers might have one or two
atrocious, clumsy droids spewing fire and able to blow themselves up against the
enemy or their structures."* `CompDroidDetonation` fires on death for any race
with `energyDensity > 0` and stored charge; `RSW_DW_Race_Primitive_Junker` carries
`energyDensity 3` + `deliberateDenyModule true` (B9), and C1 set its explosion's
`damageDef` to vanilla `Flame`. In a raid, the thing that kills a Junker droid IS
the colony — so it does blow up against the enemy, on the enemy's own doorstep.

What is missing is **intent**. A droid that walks up and detonates on purpose
reads differently from one that happens to explode, and it is the difference
between a hazard and a weapon.

## What this needs, and why it was not one more line of XML

A genuinely proactive version is a new mechanism, not a field:

- a `MentalStateDef` + `MentalStateWorker` (or a `ThinkNode`/`JobGiver` on the
  Primitive family's think tree) that seeks the nearest hostile pawn or wall;
- a self-kill route on arrival that goes through `Pawn.Kill` so
  `CompDroidDetonation.Notify_Killed` still owns the explosion maths — ⛔ do NOT
  add a second explosion path, or the two will drift and the detonation review
  (B7) will be measuring the wrong one;
- a trigger rule: always, on a threshold of damage taken, or on the raid lord's
  assault stage. Undecided, and it is a design question rather than a build one.

## criteria

- The droid selects a target and closes on it under its own think tree.
- The explosion is still `CompDroidDetonation`'s — same `50 × charge × density`,
  same radius, same `Flame` damageDef. One explosion path, not two.
- A Junker droid that is simply shot still detonates exactly as it does today.

## verify

Quicktest: spawn a Junker band, watch one droid break off and charge; confirm the
explosion radius and damage match what `DROIDWORKS_DETONATION_REVIEW_1` (B7)
recorded for `energyDensity 3`.
