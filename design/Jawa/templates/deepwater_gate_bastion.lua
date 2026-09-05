-- deepwater_gate_bastion.lua - the Compact's gate: two wall lines with their
-- gates staggered so nothing walks straight through, a killing yard between
-- them under sandbag lines and EMP traps, turrets behind the sandbags and
-- behind the inner gate, and the guardhouse where the wardens who search
-- every leaver live. DISTRICT_TEMPLATE_LIBRARY_1, Deepwater Compact district
-- #2 (Deepwater Hold manifest slot "gate bastion").
--
-- CANON (faction_roster_v2.md, Deepwater Compact): "layered walls, sandbags,
-- turrets, EMP traps"; "Turret density | High"; "EMP-weapon share 10-20%";
-- "Inside our walls no one raises a hand. Outside our walls, we do not go"
-- (ideoDescription). "Their wardens cannot follow you inland, and both of
-- you know it" (FactionDef) - so the gate is where everything happens.
--
-- THIS IS THE SECURITY PROPS VOCABULARY WITH TEETH that junkers_depot.lua's
-- retired sketch stood in for: a faction whose canon asks for eyes and guns
-- at the gate gets them, placed by the same seeded helpers as everything
-- else, and named in the plan's notes so a reviewer can count them.
--
-- Built to the owner's live-review bar (TILE_STRUCTURE_REVIEW_SAVE_1):
--   FLOORING   concrete yard (FLOOR_YARD), a steel-plate walk (FLOOR_PLATE)
--              from gate to gate, sterile tile in the guardhouse. The yard is
--              open to the sky: walled by hand, not a room.
--   GRIDS      sandbag lines have gaps; traps scatter; turrets sit where the
--              lines leave them a field of fire, not at fixed corners.
--   CLUTTER    barricade fragments, crates by the inner gate, standing lamps,
--              a SECURITY sign at the inner gate and a WARNING at the outer;
--              the guardhouse has beds, a table and chairs, a terminal, a
--              screen, shelving, crates, lamps.
-- --tech Industrial (FactionDef techLevel).

function min_rect(params)
  return 18, 12
end

function build(ctx)
  local w, h = rect.w, rect.h
  if w < 18 or h < 12 then
    ctx:refuse("footprint", string.format("%dx%d too small for two wall lines, a yard between and a guardhouse behind", w, h))
    return
  end
  local site = R(rect.x, rect.z, w, h)
  local yard_h = 6
  ctx:wall_rect(site.x, site.z, site.w, site.h)
  floor_patch(ctx, inner(site, 1), "FLOOR_YARD")

  -- ---- two gates, staggered -----------------------------------------------------
  local outer_gx = site.x + rng.int(3, math.floor(w / 2) - 2)
  local inner_z = site.z + yard_h
  local inner_gx = site.x2 - rng.int(3, math.floor(w / 2) - 2)
  for x = site.x, site.x2 do ctx:place_role("WALL", x, inner_z, 0) end
  ctx:door(outer_gx, site.z); ctx:door(outer_gx + 1, site.z)
  ctx:door(inner_gx, inner_z); ctx:door(inner_gx - 1, inner_z)
  local yard = R(site.x + 1, site.z + 1, w - 2, yard_h - 1)
  -- the walk: plate from the outer gate across to the inner gate
  for x = math.min(outer_gx, inner_gx - 1), math.max(outer_gx + 1, inner_gx) do
    ctx:floor(x, yard.z + math.floor(yard.h / 2), ctx:role("FLOOR_PLATE"))
  end
  for z = yard.z, yard.z + math.floor(yard.h / 2) do ctx:floor(outer_gx, z, ctx:role("FLOOR_PLATE")); ctx:floor(outer_gx + 1, z, ctx:role("FLOOR_PLATE")) end
  for z = yard.z + math.floor(yard.h / 2), yard.z2 do ctx:floor(inner_gx, z, ctx:role("FLOOR_PLATE")); ctx:floor(inner_gx - 1, z, ctx:role("FLOOR_PLATE")) end
  if ctx:has_role("SIGN_WARNING") then ctx:place_overlay("SIGN_WARNING", outer_gx, yard.z, 0) end
  if ctx:has_role("SIGN_SECURITY") then ctx:place_overlay("SIGN_SECURITY", inner_gx - 1, yard.z2, 0) end

  -- ---- the killing yard: sandbag lines with gaps, traps, turrets ------------------
  local bags = 0
  if ctx:has_role("SANDBAG") then
    -- a line two cells inside the inner wall, broken at the inner gate and at random
    local lz = inner_z - 2
    for x = yard.x, yard.x2 do
      local at_gate = (x >= inner_gx - 2 and x <= inner_gx + 1)
      if not at_gate and not rng.chance(0.3) and try_place(ctx, "SANDBAG", x, lz, 0) then bags = bags + 1 end
    end
    -- a short elbow flanking the outer gate on the inside
    for _, x in ipairs({ outer_gx - 2, outer_gx + 3 }) do
      for z = yard.z, yard.z + 1 do
        if try_place(ctx, "SANDBAG", x, z, 0) then bags = bags + 1 end
      end
    end
  end
  local traps = scatter(ctx, "TRAP", R(yard.x + 1, yard.z + 1, yard.w - 2, 2), rng.int(3, 5),
    { avoid = function(x, z) return x >= outer_gx - 1 and x <= outer_gx + 2 end })
  local turrets = 0
  if ctx:has_role("TURRET") then
    -- behind the sandbag line, either side of the inner gate's approach
    for _, x in ipairs({ inner_gx - 5, inner_gx + 4 }) do
      if try_near(ctx, "TURRET", x, inner_z - 1, 0, 1, yard) then turrets = turrets + 1 end
    end
    -- and one just inside the inner gate, covering it from behind
    if try_near(ctx, "TURRET", inner_gx - 4, inner_z + 2, 0, 1, inner(site, 1)) then turrets = turrets + 1 end
  end
  local barr = scatter(ctx, "BARRICADE", R(yard.x, yard.z + 2, yard.w, 2), rng.int(1, 3),
    { avoid = function(x, z) return (x >= outer_gx - 1 and x <= outer_gx + 2) end })
  scatter(ctx, "LIGHT", yard, 2)
  note(string.format("security props: %d sandbag cell(s), %d EMP trap(s), %d turret(s), %d barricade(s) - every leaver is searched here",
    bags, traps, turrets, barr))

  -- ---- the guardhouse behind the inner line ----------------------------------------
  local gw, gh = math.min(9, w - 8), h - yard_h - 1
  local guard = R(site.x + 1, inner_z + 1, gw, gh)
  if gh >= 5 then
    local gi = shell(ctx, "Barracks", guard, { floor = "FLOOR", doors = { { "E", rng.int(1, gh - 2) } } })
    local beds = 0
    for _, side in ipairs(shuffle({ "N", "W", "S" })) do
      if beds >= 2 then break end
      beds = beds + along_wall(ctx, "BED", gi, side, 2 - beds, { face = "wall", gap = 1 })
    end
    local trot = rng.int(0, 1)
    local ok, tx, tz = try_near(ctx, "TABLE", gi.x + math.floor(gi.w / 2), gi.z + math.floor(gi.h / 2), trot, 2, gi)
    if ok then seat_around(ctx, "CHAIR", tx, tz, 2, gi, trot) end
    dress(ctx, gi, {
      { role = "STORAGE",     n = { 0, 1 }, where = "wall" },
      { role = "TERMINAL",    n = 1,        where = "corner" },
      { role = "SCREEN",      n = { 0, 1 }, where = "wall" },
      { role = "SHELF_SMALL", n = { 0, 1 }, where = "wall" },
      { role = "CRATE",       n = 1,        where = "corner" },
      { role = "LIGHT",       n = 1,        where = "corner" },
    })
    wall_lights(ctx, gi, rng.int(1, 2))
    note(string.format("guardhouse: %d warden bed(s), table and chairs, terminal", beds))
  else
    note("guardhouse skipped: footprint too shallow behind the inner line")
  end
  -- crates and a lamp inside the inner gate
  scatter(ctx, "CRATE", R(inner_gx + 1, inner_z + 1, 4, 3), rng.int(1, 2))
  scatter(ctx, "LIGHT", R(guard.x2 + 2, inner_z + 1, site.x2 - guard.x2 - 2, gh), 1)
end
