# STARTING_SHIP_ANTICRAFT_1 — the disconnected anticraft caster on the starting ship

Owner, 2026-08-29 (verbatim): "let's absolutely keep your decision anticraft
caster for the Utinni... In fact I want to put one on the starting ship
(disconnected) just to show this bizarre weapon, and let that be part of the
initial v1 challenge."

Build: add one `VGE_AnticraftCaster` (3x3, VGE Chapter 1) to the starting
gravship layout, UNPOWERED/disconnected — a bizarre relic the player sees on
day one and must research/power to use (ties to
[[TECH_TREE_WEAPON_GROUPS_1]]'s ship-systems-online arc).

## Watch out
- The ship layout is authored via the gravship-layout skill (ShipLayoutDefV2);
  substructure must exist under a 3x3 hardpoint (`rimworld-layout-layers`).
- "Disconnected" must be TRUE at spawn: no conduit reaching it, and verify it
  draws nothing / shows unpowered — a turret that arrives live changes the
  v1 challenge into a free gun.
- Verify on a quicktest new-start before it rides a cold load.
