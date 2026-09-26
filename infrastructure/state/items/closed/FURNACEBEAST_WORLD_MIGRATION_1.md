# FURNACEBEAST_WORLD_MIGRATION_1

Split out of FURNACEBEAST_THERMAL_CYCLE_1 on 2026-09-16, deliberately and with
the map-scale half already shipped. Not a deferral of work that was attempted
and failed — an assessment that this leg is a different machine.

## Why it is its own item

The owner's cycle (2026-09-14, verbatim on FURNACEBEAST_THERMAL_CYCLE_1) has
two legs, and only one of them is ThinkTree work:

> "let's make them build up heat in the Deep Desert and intentionally coming
> into the Pyrelands to help it burn and absorb yet more heat … then they
> migrate all the way to the near terminator where they eat everything in sight
> while they slowly bleed out all that heat … Then they return to build up heat
> again. Like a slow thermal capacitor cycle."

**SHIPPED (the map leg, FURNACEBEAST_THERMAL_CYCLE_1):** everything that is
true once a beast is on a map a player is looking at — the saved 0-1 heat
charge (`CompFurnaceThermalCharge`), charging near fire and in hot air, bleeding
in the cold, the radiant push, walking toward the burn when under-charged and
off it when full (`JobGiver_RUT_FurnaceThermalCycle`), and the thornvine diet.

**OWED (this item, the world leg):** the herd crossing the planet between
biomes over weeks while no map holds it. That needs, at minimum:

- the herd to EXIST as a thing on the world while unspawned — a `WorldObject`
  subclass or a `Caravan`-like carrier, not a `Pawn` on a `Map`;
- a route across `WorldGrid` tiles chosen by biome, not by pathing cost: Deep
  Desert (charge) -> Pyrelands (charge hard) -> near terminator (bleed, feed)
  -> back;
- a tick that runs with no `Map` in play, advancing charge from the TILE's
  temperature rather than `Thing.AmbientTemperature`;
- an arrival rule that spawns the herd into whichever map the player has when
  the route reaches its tile, and de-spawns it back onto the world when the map
  is left.

## The trap whoever takes this must not walk into

🔴 **Ash'karr is tidally locked and hand-authored, and it is FROZEN.** The
"near terminator" leg is a real region of a real planet
(`design/Jawa/worldbuilding/`), not a temperature band to compute. Read the
map's own definition before choosing tiles, and 🔴 **generate nothing** — there
is no worldgen feature in any version (CLAUDE.md).

⚠️ Do not re-implement the charge model. `CompFurnaceThermalCharge` already owns
it and is saved with the pawn; the world leg must drive THAT number, not keep a
second one, or a herd will arrive on a map and visibly snap to a different
charge than it left with.

## Verify

Offline is enough for the mechanism: a world leg is testable without the full
mod list once a quicktest world exists. Name a positive observation — a herd
object present on a named tile, and a beast spawning with the charge the world
object was carrying — never "no error".
