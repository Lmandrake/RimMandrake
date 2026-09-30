## Scope
Follow-on to CONTAGION_RULED_CONTENT_1 Wave A. This is cast bible §2/§8's
**flight wiring** (Part 4 of the original item's scope), quoted verbatim
from `design/Jawa/worldbuilding/biomes/contagion_grotesque_cast_2026-09-27.md`:

> **Flyers** (Blisterfloat, Sparkleech, Skinflap, Gorekite — Gawpsack is
> ruled a GROUNDED floater): MaxFlightTime/FlightCooldown + race flight
> fields, Locust shape. Never block on animation frames.

Exact statBases already specified in the cast bible §2 for the two Wave-A
ports (do not re-derive, just apply):

- **Blisterfloat** (`RM_Blisterfloat`, already shipped, currently NO flight
  stats): `MaxFlightTime 15`, `FlightCooldown 8`, `flightSpeedFactor 1.8`,
  `canFlyIntoMap true`, `canLeaveMapFlying true` (leaving IS its story — the
  ones that leave are the ones that die off-map).
- **Sparkleech** (`RM_Sparkleech`, already shipped, currently NO flight
  stats — NOT the grub, `RM_SparkleechGrub` is never a flyer):
  `MaxFlightTime 10`, `FlightCooldown 5`, `flightSpeedFactor 2.2`,
  `flightStartChanceOnJobStart 0.15`.
- **Skinflap** and **Gorekite** ship their flight stats as part of whichever
  item builds them (`CONTAGION_NEW_SPECIES_FLORA_1` unless split out) —
  their statBases are in the cast bible §3.

## Watch out
- The switch is the STAT (`MaxFlightTime > 0`), not a bool — CLAUDE.md's own
  Flyer Law section has the full field list and the vanilla Locust shape to
  copy from.
- Flight ANIMATION frames are a separate, optional system
  (`flyingAnimationFramePathPrefix`/`flyingAnimationFrameCount`) — never
  block shipping the flight STAT on having frame art. With none, the
  creature flies with no wing-beat; that is correct, not broken.
- 🔴🔴 NEVER live-test a flyer's flight without the owner present (said 3x,
  CLAUDE.md). Verify via a deterministic state read (`Pawn_FlightTracker`'s
  CanEverFly/current state through a debug bridge tool, see
  `rimbridge-companion` skill), never an unattended screenshot hunt.
- Gawpsack stays grounded — do not add flight stats to it; the owner's card
  ruling (2026-09-27) is explicit that a drifting jelly is a floater, not a
  flapper.

## Verify
- statBases present and correct on RM_Blisterfloat/RM_Sparkleech (+
  Skinflap/Gorekite once built), validate_patch.py --defs 0 errors.
- CanEverFly true via a state read, not a live visual flight sighting.
