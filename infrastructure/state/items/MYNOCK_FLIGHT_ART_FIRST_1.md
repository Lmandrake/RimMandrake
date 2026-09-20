# MYNOCK_FLIGHT_ART_FIRST_1 — the mynock was made a flyer with no art to fly with

## what is wrong

Found 2026-09-20 during `DESERT_PORT_DUPLICATE_DEFS_1`'s dedup. The desert
port's copy of `RSW_Mynock` carried **real 1.6 native flight** — `MaxFlightTime`
30, `FlightCooldown` 10, `canFlyIntoMap`, and a 4-frame
`flyingAnimationFramePathPrefix`.

**`Textures/swanimals/Mynock/` does not exist.** It was a flyer pointed at
nothing. That copy was the duplicate and has been deleted; the surviving
pre-existing `RSW_Mynock` does not fly.

## why this is owed, not dropped

The standing rule (owner, 2026-09-19): *"if we're going to wait for it as though
it's not available, we might as well make it a Flyer while we're here. Standing
rule: we make flyers flyers when we can, ok?"* A mynock is canonically a winged
thing that clings to ship hulls. It qualifies.

🔑 **The trigger is touching the def, not a sweep** — and this item is the
touching.

## the work, in the right order

**Art first, because that is what was missing.** See CLAUDE.md's flight section
and `~/Desktop/RIMWORLD_1_6_NATIVE_ANIMAL_FLIGHT_IMPLEMENTATION.md`.

1. **Grounded art first** — `Textures/swanimals/Mynock/` has no files at all, so
   the mynock needs its base `_north`/`_east`/`_south` set before anything else.
   File through `fill_queue.py`; grade against
   `design/RimStarWars/canon_references/` (the mynock is canon — its entry is the
   acceptance target, appearance is READ from it, not invented).
2. **Then the flight stat**, which is the switch and is a STAT, not a bool:
   `MaxFlightTime > 0` is what `Pawn_FlightTracker.CanEverFly` reads. There is no
   `canFly` field.
3. **Then the flip-book, or knowingly without it.** The flying animation is a
   whole-animal directional flip-book — one full-body pose per frame,
   `<prefix><N>_<direction>` for `north`/`east`/`south` only. With no frames,
   `GetBestFlyAnimation` returns null and the creature flies with no wing-beat:
   correct behaviour, plainer look. **Never block flight waiting on frames.**

⛔ **Do NOT build a `PawnRenderNodeProperties_Spastic` wing-layer render tree.**
That approach was tried on `FIREHAWK_FLIGHT_BEHAVIOR_1`, failed the owner's own
live test, and was reversed 2026-09-19. Spastic drives an idle wiggle on ONE
static texture per node; it cannot express wings-up vs wings-down and nothing
keeps a single wing texture aligned across four facings.

## Watch out

- ⚠️ **The deleted copy is not a spec.** It was a raw donor re-import whose
  reference values did not resolve on our side. Read its fields for intent only,
  and re-derive the numbers.
- ⚠️ A mynock lairs rather than migrating, so `canLeaveMapFlying` is probably
  wrong for it even though `canFlyIntoMap` is right. Decide deliberately.
- 🔑 Check first whether the mynock already has art under a different `texPath` —
  **a texture binds by `texPath`, not defName**, and the port's paths were the
  donor's. Prove the art is missing before generating any.

## verify

`RSW_Mynock` renders from real art in all facings; `MaxFlightTime > 0`; the
creature is observed flying in game; landing restores the grounded graphic;
save/load is clean.

## criteria

A mynock in the sky reads as a mynock, not as a pink square or a grounded bat.
