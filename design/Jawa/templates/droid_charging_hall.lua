-- droid_charging_hall.lua - the dormancy hall of a free droid enclave: charging
-- bays along the walls where the residents stand down, a few heavy rechargers
-- in the open floor, power droids parked where they stopped, terminals on the
-- walls; behind it the reactor alcove that feeds the bays and the speakers'
-- room where the enclave decides things around a holo-table.
-- DISTRICT_TEMPLATE_LIBRARY_1, Free Droid Enclaves district #1 (The Cracking
-- Yard manifest slot "charging hall").
--
-- CANON (faction_roster_v2.md, Free Droid Enclaves "Technology and economy"):
-- "dormancy/charging hall, fabrication room, battery bunker, cracking works";
-- "no food stores beyond emergency goods for visitors". "Battle droids
-- abandoned after the war who woke up and decided they belong to themselves"
-- (FactionDef). So: NO beds, NO chairs, NO stove, NO stools - the palette's
-- faction block nulls them and this file never asks. A droid does not sit.
-- The world map names an enclave seat "Second Speaker": the enclave has a
-- speaker, and the speakers' room is where that word is spoken.
--
-- Built to the owner's live-review bar (TILE_STRUCTURE_REVIEW_SAVE_1):
--   FLOORING   grey steel grating (FLOOR) throughout, bolted durasteel
--              (FLOOR_FINE) in the speakers' room, vented steel (FLOOR_WORK)
--              under the reactor.
--   GRIDS      charging bays hug the walls at random slots with gaps; the
--              heavy rechargers and power droids scatter; terminals and
--              screens hug walls where they fall.
--   CLUTTER    power droids, small fuel tanks, crates, component and slag
--              stacks, wall lamps, an Aurebesh SLEEPING sign at the door.
-- --tech Spacer (FactionDef techLevel).

function min_rect(params)
  return 18, 16
end

function build(ctx)
  local w, h = rect.w, rect.h
  if w < 18 or h < 16 then
    ctx:refuse("footprint", string.format("%dx%d too small for a charging hall (>=18 wide) plus a 7-row back strip", w, h))
    return
  end
  local back_h = 7
  local hall = R(rect.x, rect.z, w, h - back_h + 1)
  local back = R(rect.x, hall.z2, w, back_h)
  local split = back.x + math.floor(w * 0.4) + rng.int(-1, 1)
  local reactor = R(back.x, back.z, split - back.x + 1, back_h)
  local speakers = R(split, back.z, back.x2 - split + 1, back_h)

  local hi = shell(ctx, "ChargingHall", hall, { floor = "FLOOR", doors = { { "S", rng.int(3, w - 4) } } })
  local ri = shell(ctx, "Reactor", reactor, { floor = "FLOOR_WORK" })
  local si = shell(ctx, "Council", speakers, { floor = "FLOOR_FINE" })
  ctx:door(reactor.x + rng.int(2, reactor.w - 3), reactor.z)
  ctx:door(speakers.x + rng.int(2, speakers.w - 3), speakers.z)

  -- ---- the hall: charging bays on the walls, heavies in the open ------------
  local bays = 0
  for _, side in ipairs({ "W", "E", "N" }) do
    bays = bays + along_wall(ctx, "CHARGER", hi, side, rng.int(2, 3), { gap = 1 })
  end
  local heavies = scatter(ctx, "CHARGER_BIG", inner(hi, 3), rng.int(1, 2), { rot = "any", tries = 40 })
  -- a durasteel lane from the door up the middle, worn where the bays are used
  local lane = R(hi.x + math.floor(hi.w / 2) - 1, hi.z, 3, hi.h)
  floor_patch(ctx, lane, "FLOOR_FINE", hi)
  -- a hall deeper than 11 interior rows puts its middle beyond vanilla's roof
  -- support radius (rimplace lint rule 6): two steel columns carry it, one
  -- either side of the lane, and read as the hall's structure
  local cols = 0
  if hi.h > 11 and ctx:has_role("PILLAR") then
    local pz = hi.z + math.floor(hi.h / 2)
    for _, px in ipairs({ lane.x - 3, lane.x2 + 3 }) do
      if try_near(ctx, "PILLAR", px, pz, 0, 1, hi) then cols = cols + 1 end
    end
  end
  local gonks = scatter(ctx, "GONK", inner(hi, 1), rng.int(2, 3), { rot = "any" })
  dress(ctx, hi, {
    { role = "TERMINAL",      n = { 1, 2 }, where = "wall" },
    { role = "TERMINAL_TALL", n = { 0, 1 }, where = "corner" },
    { role = "SCREEN",        n = { 0, 1 }, where = "wall" },
    { role = "FUEL_TANK_SMALL", n = { 1, 2 }, where = "corner" },
    { role = "CRATE",         n = { 1, 2 }, where = "wall" },
    { role = "COMPONENT",     n = { 1, 2 } },
    { role = "SCRAP",         n = { 0, 2 } },
    { role = "LIGHT",         n = { 1, 2 }, where = "corner" },
  })
  wall_lights(ctx, hi, rng.int(2, 4))
  if ctx:has_role("SIGN_SLEEPING") then ctx:place_overlay("SIGN_SLEEPING", lane.x + 1, hi.z, 0) end
  note(string.format("charging hall: %d wall bay(s), %d heavy recharger(s), %d power droid(s) parked - no beds, no chairs, by canon",
    bays, heavies, gonks))

  -- ---- the reactor alcove -----------------------------------------------------
  do
    local placed = along_wall(ctx, "REACTOR", ri, rng.pick({ "N", "W" }), 1)
    if placed == 0 then ctx:refuse("REACTOR", "the reactor did not fit its alcove") end
    along_wall(ctx, "BATTERY", ri, "E", rng.int(1, 2), { gap = 0 })
    dress(ctx, ri, {
      { role = "TERMINAL",        n = 1,        where = "wall" },
      { role = "FUEL_TANK_SMALL", n = { 1, 2 }, where = "corner" },
      { role = "LIGHT",           n = 1,        where = "corner" },
    })
    if ctx:has_role("SIGN_REACTOR") then ctx:place_overlay("SIGN_REACTOR", ri.x + rng.int(1, ri.w - 2), ri.z, 0) end
    wall_lights(ctx, ri, 1)
  end

  -- ---- the speakers' room: a holo-table, nothing to sit on ---------------------
  do
    local cx, cz = center(si)
    local ok = try_near(ctx, "HOLO_TABLE", cx, cz, 0, 1, si)
    if not ok then along_wall(ctx, "TABLE", si, "N", 1) end
    dress(ctx, si, {
      { role = "SCREEN",   n = { 0, 1 }, where = "wall" },
      { role = "TERMINAL", n = { 1, 2 }, where = "corner" },
      { role = "LIGHT",    n = 1,        where = "corner" },
    })
    wall_lights(ctx, si, rng.int(1, 2))
    note(string.format("speakers' room: holo-table %s", ok and "at the centre" or "did not fit; a steel table stands in"))
  end

  note("security props: none in the hall - the enclave's defence is at the cracking works")
end
