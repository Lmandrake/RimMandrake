-- droid_battery_bunker.lua - the enclave's battery bunker: a double wall, one
-- door two cells deep, and inside it the enclave's stored charge - batteries
-- in loose banks around a medium reactor, terminals watching them.
-- DISTRICT_TEMPLATE_LIBRARY_1, Free Droid Enclaves district #4 (The Cracking
-- Yard manifest slot "battery bunker", required=false).
--
-- CANON: faction_roster_v2.md, Free Droid Enclaves "Technology and economy":
-- "battery bunker". For a people who ARE their charge, this is the larder
-- and the vault at once, and it is built like one.
--
-- Built to the owner's live-review bar (TILE_STRUCTURE_REVIEW_SAVE_1):
--   FLOORING   steel plate (FLOOR_PLATE) inside; the wall ring is solid.
--   GRIDS      batteries land in two or three loose banks by scatter around
--              a jittered centre, never a stepped row.
--   CLUTTER    small fuel tanks, crates, a component stack, terminals, wall
--              lamps, REACTOR and WARNING signs.
-- The DOUBLE WALL is the point: rimplace declares the room on the INNER
-- ring so the seal/door lint reads the real shell; the outer ring is walls
-- and roof laid by hand around it.
-- --tech Spacer (FactionDef techLevel).

function min_rect(params)
  return 12, 11
end

function build(ctx)
  local w, h = rect.w, rect.h
  if w < 12 or h < 11 then
    ctx:refuse("footprint", string.format("%dx%d too small for a double-walled bunker with a reactor and battery banks", w, h))
    return
  end
  local outer = R(rect.x, rect.z, w, h)
  local shell_r = inner(outer, 1)

  -- the inner shell is the room; the outer ring is laid around it by hand
  local bi = shell(ctx, "BatteryBunker", shell_r, { floor = "FLOOR_PLATE" })
  ctx:wall_rect(outer.x, outer.z, outer.w, outer.h)
  ctx:roof_rect(outer.x, outer.z, outer.w, outer.h)
  local door_x = shell_r.x + rng.int(3, shell_r.w - 4)
  ctx:door(door_x, shell_r.z)
  ctx:door(door_x, outer.z)

  -- ---- the reactor in a back corner, banks of batteries around the floor ----
  local placed = along_wall(ctx, "REACTOR_BIG", bi, rng.pick({ "N", "W", "E" }), 1)
  if placed == 0 then placed = along_wall(ctx, "REACTOR", bi, "N", 1) end
  if placed == 0 then ctx:refuse("REACTOR", "no reactor fitted the bunker") end
  local banks, cells = 0, 0
  for i = 1, rng.int(3, 4) do
    local cx, cz = rng.int(bi.x + 2, bi.x2 - 2), rng.int(bi.z + 2, bi.z2 - 2)
    local got = scatter(ctx, "BATTERY", R(cx - 2, cz - 2, 5, 5), rng.int(3, 5), { rot = rng.pick({ 0, 1 }), tries = 60 })
    if got > 0 then banks = banks + 1 end
    cells = cells + got
  end
  dress(ctx, bi, {
    { role = "TERMINAL",        n = { 1, 2 }, where = "wall" },
    { role = "FUEL_TANK_SMALL", n = { 1, 2 }, where = "corner" },
    { role = "CRATE",           n = { 0, 1 }, where = "corner" },
    { role = "COMPONENT",       n = { 0, 1 } },
    { role = "LIGHT",           n = 1,        where = "corner" },
  })
  wall_lights(ctx, bi, rng.int(1, 2))
  if ctx:has_role("SIGN_WARNING") then ctx:place_overlay("SIGN_WARNING", door_x, bi.z, 0) end
  if ctx:has_role("SIGN_REACTOR") then ctx:place_overlay("SIGN_REACTOR", bi.x + rng.int(1, bi.w - 2), bi.z2, 0) end
  note(string.format("battery bunker: double wall, %d battery(ies) in %d bank(s), reactor %s",
    cells, banks, placed > 0 and "in the corner" or "MISSING"))
  note("security props: the wall IS the security prop; nothing else is placed")
end
