-- junkers_dwelling_cluster.lua - four small huts of unequal size, nudged off a
-- loose quadrant layout around a shared open-air commons with a fire.
-- DISTRICT_TEMPLATE_LIBRARY_1, Junkers district #2 (The Claim Jump manifest
-- slot "dwelling cluster").
--
-- REWORKED 2026-09-05 against the owner's live-review verdict
-- (TILE_STRUCTURE_REVIEW_SAVE_1 - flooring, regular grids, clutter):
--   FLOORING   every hut interior is rust-plating (FLOOR); the commons is
--              cleared ground worn to asphalt around the fire and the paths
--              to each door. Nothing inside sits on stony soil.
--   GRIDS      the huts were four identical squares on a quadrant grid with
--              beds on a 2-cell stride. Now each hut is 5x5..7x7, its anchor
--              jittered, its door on whichever side faces the commons, and
--              beds hug a wall at random slots.
--   CLUTTER    end tables, crates, small shelves, stools, a wall torch and a
--              floor torch per hut; the commons has a fire pit with stools,
--              a table and chairs, a barrel, crates, and fence fragments
--              between the huts that read as yards.
--
-- --tech Neolithic, same reasoning as junkers_scrapyard.lua: huts unpowered.

local function hut_door_side(q)
  -- the side that faces the commons at the centre
  if q == "NW" then return rng.pick({ "S", "E" }) end
  if q == "NE" then return rng.pick({ "S", "W" }) end
  if q == "SW" then return rng.pick({ "N", "E" }) end
  return rng.pick({ "N", "W" })
end

local function furnish_hut(ctx, r, beds_needed, q)
  local side = hut_door_side(q)
  local hi = shell(ctx, "Barracks", r, { floor = "FLOOR", doors = { side } })
  -- beds head-to-wall on the walls that do not hold the door
  local walls = shuffle({ "N", "E", "S", "W" })
  local beds = 0
  for _, s in ipairs(walls) do
    if beds >= beds_needed then break end
    if s ~= side then
      beds = beds + along_wall(ctx, "BED", hi, s, beds_needed - beds, { face = "wall", gap = 0 })
    end
  end
  if ctx:has_role("BED") and beds < beds_needed then
    note(string.format("hut %s: %d of %d beds fitted", q, beds, beds_needed))
  end
  dress(ctx, hi, {
    { role = "END_TABLE",   n = { 0, 1 }, where = "wall" },
    { role = "SHELF_SMALL", n = { 0, 1 }, where = "wall" },
    { role = "CRATE",       n = { 1, 2 }, where = "corner" },
    { role = "STOOL",       n = { 0, 1 } },
    { role = "LIGHT",       n = 1,        where = "corner" },
  })
  wall_lights(ctx, hi, 1)
  return beds, side
end

-- From build()'s own arithmetic: two 5-wide huts plus a 3-cell commons gap.
function min_rect(params)
  return 15, 15
end

function build(ctx)
  local p = params
  local w, h = rect.w, rect.h
  if w < 15 or h < 15 then
    ctx:refuse("footprint", string.format("%dx%d cannot hold four huts around a commons", w, h))
    return
  end
  local lot = R(rect.x, rect.z, w, h)
  floor_worn(ctx, lot, "FLOOR_CHEAP", "FLOOR_YARD", 0.08)

  local occ = p.occupants or 6
  local beds_per_hut = math.max(1, math.ceil(occ / 4))

  -- quadrant anchors; each hut takes a random size that still leaves the
  -- centre band free, and slides off its anchor by up to a cell
  local half_w, half_h = math.floor(w / 2), math.floor(h / 2)
  local max_hw, max_hh = math.min(7, half_w - 2), math.min(7, half_h - 2)
  local huts = {}
  for _, q in ipairs({ "NW", "NE", "SW", "SE" }) do
    local hw, hh = rng.int(5, max_hw), rng.int(5, max_hh)
    local jx, jz = rng.int(0, 1), rng.int(0, 1)
    local x = (q == "NW" or q == "SW") and (rect.x + jx) or (rect.x2 - hw - jx)
    local z = (q == "SW" or q == "SE") and (rect.z + jz) or (rect.z2 - hh - jz)
    huts[#huts + 1] = { q = q, r = R(x, z, hw, hh) }
  end

  local total_beds, keep = 0, {}
  for _, hut in ipairs(huts) do
    local beds, side = furnish_hut(ctx, hut.r, beds_per_hut, hut.q)
    total_beds = total_beds + beds
    keep[#keep + 1] = R(hut.r.x - 1, hut.r.z - 1, hut.r.w + 2, hut.r.h + 2)
    -- a worn path from the door toward the commons
    local d = DIR[SIDE_ROT[side]]
    local cx, cz = center(hut.r)
    for i = 1, 3 do
      local px, pz = cx + d[1] * (math.floor(hut.r.w / 2) + i), cz + d[2] * (math.floor(hut.r.h / 2) + i)
      if in_rect(px, pz, lot) then ctx:floor(px, pz, ctx:role("FLOOR_YARD")) end
    end
  end
  note(string.format("dwelling cluster: 4 huts of unequal size, %d bed(s) total for %d occupant(s)",
    total_beds, occ))

  -- ---- the commons: the open centre between the huts ----------------------
  local cx, cz = center(lot)
  local commons = R(cx - 3, cz - 3, 7, 7)
  local fx, fz = jitter(cx, 1), jitter(cz, 1)
  if try_place(ctx, "STOVE", fx, fz, 0) then
    floor_patch(ctx, R(fx - 1, fz - 1, 3, 3), "FLOOR_CHEAP", lot)
    local seats, want = 0, rng.int(3, 4)
    for _, c in ipairs(shuffle({ { fx - 1, fz - 1, 1 }, { fx + 1, fz - 1, 3 }, { fx - 1, fz + 1, 1 },
                                 { fx + 1, fz + 1, 3 }, { fx, fz - 2, 0 }, { fx, fz + 2, 2 },
                                 { fx - 2, fz, 1 }, { fx + 2, fz, 3 } })) do
      if seats >= want then break end
      if try_place(ctx, "STOOL", c[1], c[2], c[3]) then seats = seats + 1 end
    end
  end
  -- a table and chairs off to one side of the fire, a barrel, crates, a torch
  do
    local trot = rng.int(0, 1)
    local ok, tx, tz = try_near(ctx, "TABLE", fx + rng.pick({ -3, 3 }), fz + rng.pick({ -2, 2 }), trot, 2, lot)
    if ok then seat_around(ctx, "CHAIR", tx, tz, rng.int(1, 2), lot, trot) end
  end
  scatter(ctx, "BARREL", commons, 1, { keep_clear = keep })
  scatter(ctx, "CRATE", inner(lot, 1), rng.int(2, 3), { keep_clear = keep })
  scatter(ctx, "LIGHT", commons, 1, { keep_clear = keep })

  -- fence fragments between neighbouring huts: yards, not walls
  if ctx:has_role("FENCE") then
    local fenced = 0
    for _, pair in ipairs({ { huts[1], huts[2] }, { huts[3], huts[4] } }) do
      local a, b = pair[1].r, pair[2].r
      local zz = (a.z == rect.z or a.z == rect.z + 1) and (a.z2 + 1) or (a.z - 1)
      if rng.chance(0.7) then
        for x = a.x2 + 2, b.x - 2 do
          if not rng.chance(0.35) and try_place(ctx, "FENCE", x, zz, 0) then fenced = fenced + 1 end
        end
      end
    end
    note(string.format("%d fence cell(s) between huts", fenced))
  end

  note("no security props placed: dwelling cluster is residential, not a checkpoint")
end
