# HOIST_FIXED_SITE_FRAMES_1 — fixed hoists built into sites

## spec
Authority: `design/RimMandrake/ship_cargo_hoist_design_2026-10-01.md` §2a, §2c and §5 row 2. `RM_HoistFrame`: the same comp on a fixed head-frame, **placed only by
site gensteps and never player-buildable** (owner ruling). Add the third target kind, a **sealed holder feature**
(a building holding pawns that nobody can enter), which the Hutt oubliette needs. First reuse: a ruined head-frame
beside `RUT_FoundryTowerEntrance`.

## criteria
- The frame does not appear in the architect menu. A genstep places it. Pawns can load it on the site map.
- A holder feature's pawns can be lifted out by a hoist when its gate condition is met, and not before.

## Watch out
- Depends on HOIST_SHIP_PART_BUILD_1.
- 🔑 **Animation is optional polish, and it comes LAST.** Ship with a drawn cable line (`GenDraw.DrawLineBetween`) and static sprites; transit is a hidden timer (vanish, wait, appear). Art is the final step and may be skipped. A descent animation is never in scope (owner: *"careful we don't get caught in endless animation development"*).
