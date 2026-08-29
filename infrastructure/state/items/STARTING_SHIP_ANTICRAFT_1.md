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

## Done, game DOWN, 2026-08-29
Placed `VGE_AnticraftCaster` (odd 3x3, position = its geometric centre cell per
the gravship-layout skill) at layout-local `(55,3)` in
`design/Jawa/worldbuilding/ship_build/exported/Gravship_v1.xml` — the ship's
narrow bow section, 30 cells wide there. All 9 footprint cells were bare
`Substructure`/`MetalTile` with no prior thing; nearest `PowerConduit`/
`HiddenConduit` cell in the whole 88x135 layout is **53 cells away** (Chebyshev
distance from centre) — no conduit reaches it, satisfying "disconnected" by
construction, not by a live check. `gravship_layout.py --roundtrip` clean
(1053 things, was 1052); `validate()`'s one warning is the pre-existing,
documented "no GravEngine in the export" condition (skill: "verified zero in
both of ours"), unrelated to this change.

Repo copy and the live `Config\GravshipExport\Gravship.xml` were byte-identical
before this edit (md5 `f4e7bf4a…`) — confirmed current, not stale — and are
byte-identical again now (md5 `1788556b…`) after copying the edited file over.

**Owner's own line already answers the disconnected-turret risk this item's
"Watch out" flags**: "disconnected... just to show this bizarre weapon" —
`VGE_AnticraftCaster` carries `CompProperties_Power`, so an unwired one reads
unpowered/inert by the game's own power system, no extra flag needed.

## Still owed
`## Watch out`'s last line — quicktest verify — needs a live game
(`rimworld-debug-testing`), which is not available while DOWN. Confirm on the
next quicktest or cold load: the caster appears on the choose-gravship page's
ship, and its inspect panel reads unpowered/no-conduit with zero other parts
disturbed.
