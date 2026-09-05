-- droid_cracking_works.lua - the reason a free droid enclave sits where it
-- sits: a walled yard around a starship fuel refinery that cracks the water
-- nobody else can drink into fuel, its tank farm, a control shed, and one
-- turret that is the enclave's whole argument. DISTRICT_TEMPLATE_LIBRARY_1,
-- Free Droid Enclaves district #2 (The Cracking Yard manifest slot
-- "cracking works").
--
-- CANON: "They settle on water and crack it for fuel, so an attacker arrives
-- thirsty at a source it cannot drink" (JawaFreeDroidEnclaves.xml);
-- faction_roster_v2.md: "hydrogen cracking plant - the reason they hold
-- water tiles"; the frozen map's "The Cracking Yard" / "The Cracking
-- Station" / "Vent Twelve". The refinery is KOTOR_FuelRefinery (7x7,
-- 'starship fuel refinery', Jawa Armoury Rebalance's absorbed KotOR core).
--
-- Built to the owner's live-review bar (TILE_STRUCTURE_REVIEW_SAVE_1):
--   FLOORING   concrete yard (FLOOR_YARD), a vented-steel apron (FLOOR_WORK)
--              around the refinery, grating in the control shed. Open to the
--              sky: walled by hand, not declared as a room.
--   GRIDS      the tank farm is a cluster, not a row; small tanks and
--              power droids scatter; crates pile by the gate.
--   CLUTTER    power droids, small fuel tanks, crates, slag, a WARNING and a
--              REFINERY sign, lamps on the wall line.
-- SECURITY PROPS with teeth: one auto-turret covering the gate. "Raids are
-- retaliation only" - the enclave defends, it does not patrol.
-- --tech Spacer (FactionDef techLevel).

function min_rect(params)
  return 20, 20
end

function build(ctx)
  local w, h = rect.w, rect.h
  if w < 20 or h < 20 then
    ctx:refuse("footprint", string.format("%dx%d too small for a 7x7 refinery, a tank farm and a control shed inside a wall", w, h))
    return
  end
  local yard = R(rect.x, rect.z, w, h)
  local inn = inner(yard, 1)
  ctx:wall_rect(yard.x, yard.z, yard.w, yard.h)
  floor_patch(ctx, inn, "FLOOR_YARD")
  local gate_x = yard.x + rng.int(4, w - 6)
  ctx:door(gate_x, yard.z)
  ctx:door(gate_x + 1, yard.z)

  -- ---- the refinery, off-centre, on its apron ------------------------------
  local rw = ctx:width_of("REFINERY")
  local rx = inn.x + math.floor((inn.w - rw) / 2) + rng.int(-2, 2)
  local rz = inn.z + math.floor((inn.h - rw) / 2) + rng.int(0, 2)
  local ox, oz = origin_for(rx, rz, rw, rw, 0)
  floor_patch(ctx, R(rx - 1, rz - 1, rw + 2, rw + 2), "FLOOR_WORK", inn)
  local refinery = try_place(ctx, "REFINERY", ox, oz, 0)
  if not refinery then ctx:refuse("REFINERY", "the refinery did not seat - this yard is nothing without it") end
  local keep = { R(rx - 2, rz - 2, rw + 4, rw + 4), R(gate_x - 2, yard.z + 1, 6, 4) }
  if ctx:has_role("SIGN_REFINERY") then ctx:place_overlay("SIGN_REFINERY", rx + 2, rz - 2, 0) end

  -- ---- the control shed in a corner away from the gate -------------------------
  local shed_w, shed_h = 7, 6
  local shed_side = (gate_x < yard.x + w / 2) and "E" or "W"
  local shed = R((shed_side == "W") and (yard.x + 1) or (yard.x2 - shed_w), yard.z2 - shed_h, shed_w, shed_h)
  local si = shell(ctx, "Control", shed, { floor = "FLOOR", doors = { { "S", rng.int(2, shed_w - 3) } } })
  along_wall(ctx, "SCREEN", si, "N", 1)
  along_wall(ctx, "TERMINAL", si, rng.pick({ "N", "E", "W" }), rng.int(1, 2), { gap = 1 })
  along_wall(ctx, "WORKBENCH", si, rng.pick({ "E", "W" }), 1)
  dress(ctx, si, {
    { role = "CRATE",     n = { 1, 2 }, where = "corner" },
    { role = "COMPONENT", n = { 0, 1 } },
    { role = "LIGHT",     n = 1,        where = "corner" },
  })
  wall_lights(ctx, si, 1)
  keep[#keep + 1] = R(shed.x - 1, shed.z - 1, shed.w + 2, shed.h + 3)

  -- ---- the tank farm: a cluster on the side opposite the shed ------------------
  local farm_x = (shed_side == "W") and (yard.x2 - 7) or (yard.x + 2)
  local farm = R(farm_x, yard.z2 - 8, 6, 7)
  floor_patch(ctx, farm, "FLOOR_WORK", inn)
  local tanks = scatter(ctx, "FUEL_TANK", farm, rng.int(2, 3), { tries = 40 })
  tanks = tanks + scatter(ctx, "GAS_TANK", farm, rng.int(0, 1), { tries = 20 })
  local small = scatter(ctx, "FUEL_TANK_SMALL", inner(inn, 1), rng.int(3, 5), { keep_clear = keep })
  keep[#keep + 1] = R(farm.x - 1, farm.z - 1, farm.w + 2, farm.h + 2)
  if ctx:has_role("SIGN_WARNING") then ctx:place_overlay("SIGN_WARNING", farm.x + 2, farm.z - 1, 0) end

  -- ---- the yard: power droids, crates by the gate, slag, light --------------------
  local gonks = scatter(ctx, "GONK", inner(inn, 1), rng.int(2, 4), { keep_clear = keep, rot = "any" })
  scatter(ctx, "CRATE", R(gate_x - 4, yard.z + 1, 10, 2), rng.int(2, 3), { keep_clear = { keep[2] } })
  scatter(ctx, "CRATE_WIDE", inner(inn, 1), rng.int(0, 1), { keep_clear = keep })
  scatter(ctx, "SCRAP", inner(inn, 1), rng.int(3, 5), { keep_clear = keep })
  dress(ctx, inn, { { role = "LIGHT", n = { 2, 3 }, where = "wall" } })
  wall_lights(ctx, inn, rng.int(2, 3))

  -- ---- security: one turret covering the gate ----------------------------------
  local turret = 0
  if ctx:has_role("TURRET") then
    local tx = (shed_side == "W") and (yard.x2 - 3) or (yard.x + 3)
    if try_near(ctx, "TURRET", tx, yard.z + 3, 0, 1, inn) then turret = 1 end
  end
  note(string.format("cracking works: refinery %s, %d tank(s) in the farm, %d small tank(s), %d power droid(s), %d turret(s) on the gate",
    refinery and "seated" or "MISSING", tanks, small, gonks, turret))
end
