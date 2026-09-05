-- deepwater_hospital_ward.lua - the Compact's hospital: a ward of monitored
-- beds, a surgery, and the scrub room between them. DISTRICT_TEMPLATE_LIBRARY_1,
-- Deepwater Compact district #3 (Deepwater Hold manifest slot "hospital ward").
--
-- CANON (faction_roster_v2.md, Deepwater Compact "Technology and economy"):
-- "hydroponics, refrigeration, sterile hospital rooms"; "hospital, water
-- storage, battery rooms". Water is medicine on a desert world, and the
-- people who own the water run the hospital.
--
-- Built to the owner's live-review bar (TILE_STRUCTURE_REVIEW_SAVE_1):
--   FLOORING   sterile tile (FLOOR) in the ward and surgery, mosaic
--              (FLOOR_WET) in the scrub room.
--   GRIDS      beds hug the ward's long walls at random slots with gaps,
--              each with its own vitals monitor and end table where it fits.
--   CLUTTER    medicine stacks by the shelving, basins and a tub in the
--              scrub room, plant pots, a terminal, standing and wall lamps,
--              HOSPITAL and MEDICAL signs.
-- --tech Industrial (FactionDef techLevel).

-- a bed's own monitor and table, placed at the free end of its footprint
local function bedside(ctx, r, x, z, rot)
  local x0, z0, bw, bh = footprint_sw(ctx, "HOSPITAL_BED", x, z, rot)
  local cand = {}
  for dx = -1, bw do
    for dz = -1, bh do
      local onx, onz = (dx >= 0 and dx < bw), (dz >= 0 and dz < bh)
      if (onx ~= onz) then cand[#cand + 1] = { x0 + dx, z0 + dz } end
    end
  end
  local got = 0
  for _, c in ipairs(shuffle(cand)) do
    if got >= 2 then break end
    if in_rect(c[1], c[2], r) and not blocks_a_door(ctx, c[1], c[2], r) then
      local role = (got == 0) and "VITALS" or "END_TABLE"
      if try_place(ctx, role, c[1], c[2], 0) then got = got + 1 end
    end
  end
  return got
end

function min_rect(params)
  return 16, 13
end

function build(ctx)
  local w, h = rect.w, rect.h
  if w < 16 or h < 13 then
    ctx:refuse("footprint", string.format("%dx%d too small for a ward (>=9 wide) beside a surgery over a scrub room", w, h))
    return
  end
  local east_w = 8
  local ward = R(rect.x, rect.z, w - east_w + 1, h)
  local east = R(ward.x2, rect.z, east_w, h)
  local scrub_h = math.max(5, math.floor(h / 2) - 1)
  local scrub = R(east.x, east.z, east.w, scrub_h)
  local surgery = R(east.x, scrub.z2, east.w, east.h - scrub_h + 1)

  local wi = shell(ctx, "Hospital", ward, { floor = "FLOOR", doors = { { "S", rng.int(3, ward.w - 4) } } })
  local si = shell(ctx, "Scrub", scrub, { floor = "FLOOR_WET" })
  local gi = shell(ctx, "Surgery", surgery, { floor = "FLOOR" })
  ctx:door(scrub.x, scrub.z + rng.int(2, scrub.h - 3))
  ctx:door(surgery.x, surgery.z + rng.int(2, surgery.h - 3))
  ctx:door(surgery.x + rng.int(2, surgery.w - 3), surgery.z)   -- scrub <-> surgery

  -- ---- the ward: beds on the long walls, a monitor and a table each -------------
  local beds, kit = 0, 0
  for _, side in ipairs({ "N", "W" }) do
    local want = (side == "N") and rng.int(2, 3) or rng.int(1, 2)
    beds = beds + along_wall(ctx, "HOSPITAL_BED", wi, side, want, { face = "wall", gap = 1 })
    local placed = {}
    for i, t in ipairs(LAST_PLACED) do placed[i] = t end   -- bedside() overwrites LAST_PLACED
    for _, t in ipairs(placed) do kit = kit + bedside(ctx, wi, t[1], t[2], t[3]) end
  end
  along_wall(ctx, "STORAGE", wi, "E", 1)
  dress(ctx, wi, {
    { role = "MEDICINE",  n = { 2, 3 } },
    { role = "PLANT_POT", n = { 1, 2 }, where = "wall" },
    { role = "TERMINAL",  n = { 0, 1 }, where = "corner" },
    { role = "STOOL",     n = { 1, 2 } },
    { role = "LIGHT",     n = { 1, 2 }, where = "corner" },
  })
  wall_lights(ctx, wi, rng.int(2, 3))
  if ctx:has_role("SIGN_HOSPITAL") then ctx:place_overlay("SIGN_HOSPITAL", wi.x + math.floor(wi.w / 2), wi.z, 0) end
  note(string.format("ward: %d hospital bed(s) with %d monitor(s)/table(s) beside them", beds, kit))

  -- ---- the surgery ----------------------------------------------------------------
  do
    local cx, cz = center(gi)
    local ok, bx, bz = try_near(ctx, "HOSPITAL_BED", cx, cz, 0, 1, gi)
    if ok then bedside(ctx, gi, bx, bz, 0) end
    along_wall(ctx, "STORAGE", gi, rng.pick({ "N", "E" }), 1)
    dress(ctx, gi, {
      { role = "BASIN",    n = 1,        where = "wall" },
      { role = "MEDICINE", n = { 1, 2 } },
      { role = "LIGHT",    n = { 1, 2 }, where = "corner" },
    })
    wall_lights(ctx, gi, 1)
    if ctx:has_role("SIGN_MEDICAL") then ctx:place_overlay("SIGN_MEDICAL", gi.x + 1, gi.z + 1, 0) end
  end

  -- ---- the scrub room ----------------------------------------------------------------
  do
    along_wall(ctx, "SINK", si, rng.pick({ "E", "S" }), 1)
    dress(ctx, si, {
      { role = "BASIN",   n = { 1, 2 }, where = "wall" },
      { role = "TUB",     n = 1,        where = "corner" },
      { role = "STORAGE", n = { 0, 1 }, where = "wall" },
      { role = "CRATE",   n = { 0, 1 }, where = "corner" },
      { role = "LIGHT",   n = 1,        where = "corner" },
    })
    wall_lights(ctx, si, 1)
  end
  note("security props: none - a hospital is the one room the Compact leaves unguarded on purpose")
end
