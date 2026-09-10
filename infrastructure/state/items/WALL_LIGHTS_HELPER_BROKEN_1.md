# WALL_LIGHTS_HELPER_BROKEN_1

## What was found (offline, 2026-09-10, during the road-warehouse archetype build)

`design/Jawa/templates/prelude.lua`'s `wall_lights()` helper (used by at
least `road_warehouse.lua`, `trading_post.lua`, and `homestead.lua` for a
guaranteed-secondary or ambiance pass) silently places **zero** lights at
every call site checked.

**Proven, not assumed**: ran `trading_post.lua` directly across 20 seeds —
`WALL_LIGHT` placement count was 0/20. Every call site passes the room's
**outer shell rect** (the wall-inclusive footprint), but `wall_lights()`'s
own geometry needs the **interior rect** to correctly find a wall one step
past its own edge — with the shell rect, its search starts already outside
any real wall, so `can_place` never finds a valid site and the function
returns having placed nothing, with no error, warning, or log line.

This is exactly the class of bug this project's own doctrine warns about:
success with nothing happening, invisible unless someone tests the specific
output.

## Why it wasn't caught until now

None of the 3 templates depend on `wall_lights()` for a REQUIRED element (a
guaranteed primary/secondary) — `road_warehouse.lua`'s own pass worked
around it by using a walkability-guarded `BARREL` instead once this was
discovered. So every prior seed sweep passed lint/verify cleanly; nothing
downstream checks "did the ambiance lights actually appear."

## spec

1. Read `wall_lights()` in `design/Jawa/templates/prelude.lua` (or wherever
   it actually lives — confirm the exact file) and confirm the interior-vs-
   shell-rect diagnosis directly from its own geometry math, not by
   re-testing black-box.
2. Fix the function itself (either accept the shell rect and derive the
   interior internally, or clearly re-document that it requires the
   interior rect and is being called wrong everywhere) — a single fix in
   `prelude.lua` should repair all 3+ call sites at once.
3. Grep every `.lua` template under `design/Jawa/templates/` for
   `wall_lights(` to find every call site once the real fix/contract is
   known, and confirm each one now either passes the right rect or was
   already not relying on the result.

## verify

Re-run `trading_post.lua`'s own seed sweep (or a smaller targeted one) and
confirm `WALL_LIGHT` (or whatever the placed defName actually is) count is
now nonzero across a real sample, not just "no lint error." A screenshot or
`rimplace verify`-style defName presence check is not sufficient here — the
original bug produced zero errors and zero lint findings; only counting
actual placements catches it.
