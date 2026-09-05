-- junkers_depot.lua - a Junkers goods depot: a loading apron out front, a
-- warehouse floor behind two loading doors, and a trader's office plus the
-- trader's own quarters across the back. DISTRICT_TEMPLATE_LIBRARY_1, Junkers
-- district #4 (The Claim Jump manifest slot "depot", required=false).
--
-- REWORKED 2026-09-05 after the owner's live review of the first version
-- (TILE_STRUCTURE_REVIEW_SAVE_1: "these are pretty horrible... not accept any
-- rooms yet"; this file was named for its "ridiculously regular grid" and
-- oppressive aisles). What changed, against each of his three defect axes:
--   FLOORING   every interior is floored by name: the depot floor is iron
--              grating (FLOOR_WORK) worn through to steel plate in patches,
--              the office is iron divoted tile (FLOOR_FINE), the quarters rust
--              plating (FLOOR), the apron outside is broken asphalt. Nothing
--              sits on the tech-default stony soil any more.
--   GRIDS      the nested while-loop of shelving is gone. Shelves hug the two
--              long walls at random slots with gaps (along_wall), and two
--              short island runs sit at jittered rows, offset from each other
--              and from the walls by real aisles - a 3-cell centre aisle
--              from the loading doors to the office door is kept clear by
--              construction, and every island is at least 2 cells off the
--              wall shelving. Aisles are walkable; shelving is sparse.
--   CLUTTER    crates against the walls, barrels in corners, slag chunks on
--              the floor, a receiving desk with a stool just inside the doors,
--              wall torches and a floor torch; the office has its own desk,
--              chair, small shelf and lamp; the quarters a bedroll, end table
--              and crate. Nothing is a bare furniture set.
--
-- Security props: NONE, same ruling as the other three Junkers districts
-- (searchesLeavers=false). The old maybe_place_security() sketch is retired
-- here: the Deepwater bastion (deepwater_gate_bastion.lua) now places real
-- security props for a faction whose canon asks for them, which is the proof
-- the sketch was standing in for.
--
-- Reused art only: everything resolves through palette.json's
-- faction:Jawa_Junkers block. --tech Neolithic (unpowered depot floor).

function min_rect(params)
  return 14, 15
end

function build(ctx)
  local w, h = rect.w, rect.h
  if w < 14 or h < 15 then
    ctx:refuse("footprint", string.format(
      "%dx%d too small for a depot (apron + 11-row floor + 6-row office, >=14 wide)", w, h))
    return
  end

  -- ---- the loading apron: two rows of broken asphalt out front -----------
  local apron_h = 2
  local apron = R(rect.x, rect.z, w, apron_h)
  floor_worn(ctx, apron, "FLOOR_YARD", "FLOOR_CHEAP", 0.3)

  -- ---- two bays sharing a wall row: depot floor south, office/quarters north
  local bld = R(rect.x, rect.z + apron_h, w, h - apron_h)
  local office_h = 6
  local floorBay = R(bld.x, bld.z, w, bld.h - office_h + 1)
  local officeBay = R(bld.x, floorBay.z2, w, office_h)

  local fl = shell(ctx, "Storeroom", floorBay, { floor = "FLOOR_WORK" })
  floor_worn(ctx, fl, "FLOOR_WORK", "FLOOR_PLATE", 0.12)

  -- two loading doors side by side, off-centre: a bay, not a front door
  local door_t = rng.int(4, w - 7)
  ctx:door(floorBay.x + door_t, floorBay.z)
  ctx:door(floorBay.x + door_t + 1, floorBay.z)
  local aisle = R(floorBay.x + door_t - 1, fl.z, 4, fl.h)   -- kept clear floor to office

  -- office (west) and the trader's quarters (east) split the back bay
  local split = officeBay.x + math.floor(w / 2) + rng.int(-1, 1)
  local office = R(officeBay.x, officeBay.z, split - officeBay.x + 1, office_h)
  local quarters = R(split, officeBay.z, officeBay.x2 - split + 1, office_h)
  local oi = shell(ctx, "Office", office, { floor = "FLOOR_FINE" })
  local qi = shell(ctx, "Bedroom", quarters, { floor = "FLOOR" })
  -- the office door opens onto the centre aisle; the quarters door where it falls
  local office_door_x = math.max(office.x + 1, math.min(office.x2 - 1, floorBay.x + door_t + rng.int(0, 1)))
  ctx:door(office_door_x, officeBay.z)
  ctx:door(quarters.x + rng.int(2, quarters.w - 3), officeBay.z)

  -- ---- depot floor: wall shelving with gaps, two loose island runs ---------
  local shelves = 0
  shelves = shelves + along_wall(ctx, "STORAGE", fl, "W", rng.int(2, 3), { gap = 1 })
  shelves = shelves + along_wall(ctx, "STORAGE", fl, "E", rng.int(2, 3), { gap = 1 })
  -- islands: short east-west runs, each on its own jittered row, never in the
  -- centre aisle and at least 2 cells from the wall shelving on either side
  local sw = ctx:width_of("STORAGE")
  local rows = { fl.z + rng.int(3, 4), fl.z2 - rng.int(2, 3) }
  for _, zz in ipairs(rows) do
    for _, half in ipairs({ { fl.x + 3, aisle.x - sw - 1 }, { aisle.x2 + 2, fl.x2 - 3 - sw + 1 } }) do
      local lo, hi = half[1], half[2]
      if hi >= lo then
        local xx = rng.int(lo, hi)
        local run = rng.int(2, 3)
        for i = 1, run do
          local ox = xx + (i - 1) * sw
          if ox <= hi and not rng.chance(0.2) then
            if try_place(ctx, "STORAGE", ox, zz, 0) then shelves = shelves + 1 end
          end
        end
      end
    end
  end

  -- the receiving desk: just inside the doors, beside the aisle, a stool at it
  do
    local ok, tx, tz = try_near(ctx, "TABLE", aisle.x2 + 2, fl.z + 1, 1, 2, fl)
    if ok then try_near(ctx, "STOOL", tx, tz + 1, 2, 1, fl) end
  end

  -- clutter and light
  dress(ctx, fl, {
    { role = "CRATE",  n = { 3, 5 }, where = "wall" },
    { role = "BARREL", n = { 1, 2 }, where = "corner" },
    { role = "SCRAP",  n = { 2, 4 } },
    { role = "LIGHT",  n = 1, where = "corner" },
  })
  wall_lights(ctx, fl, rng.int(2, 3))
  note(string.format("depot floor: %d shelving unit(s) - wall runs plus two island rows, %d-cell centre aisle kept clear",
    shelves, aisle.w))

  -- ---- roof support: only a floor bay TALLER than 12 interior rows puts its
  -- centre more than 6 cells from both long walls (vanilla's support radius,
  -- rimplace lint rule 6); then two pillars at the aisle edges carry it and
  -- mark the aisle. At the manifest's 18x18 the bay is 9 rows and needs none.
  local need = fl.h > 12
  if need and ctx:has_role("PILLAR") then
    local pz = fl.z + math.floor(fl.h / 2)
    local placed = 0
    for _, px in ipairs({ aisle.x - 1, aisle.x2 + 1 }) do
      local ok = try_near(ctx, "PILLAR", px, pz, 0, 1, fl)
      if ok then placed = placed + 1 end
    end
    if placed < 2 then
      ctx:refuse("PILLAR", "could not seat both aisle pillars; roof over the centre may be unsupported")
    end
  end

  -- ---- the trader's office ------------------------------------------------
  do
    local ok, tx, tz = try_near(ctx, "TABLE", oi.x + math.floor(oi.w / 2), oi.z + 1, 1, 2, oi)
    if ok then seat_around(ctx, "CHAIR", tx, tz, 1, oi, 1) end
    along_wall(ctx, "STORAGE", oi, "N", 1)
    dress(ctx, oi, {
      { role = "SHELF_SMALL", n = { 1, 2 }, where = "wall" },
      { role = "CRATE",       n = 1,        where = "corner" },
      { role = "LIGHT",       n = 1,        where = "corner" },
    })
    wall_lights(ctx, oi, 1)
  end

  -- ---- the trader's quarters: the one person who sleeps on the goods -------
  do
    local beds = along_wall(ctx, "BED", qi, rng.pick({ "N", "E" }), 1, { face = "wall" })
    if beds == 0 then note("quarters: no bed fitted - trader sleeps on the depot floor") end
    dress(ctx, qi, {
      { role = "END_TABLE", n = 1,        where = "wall" },
      { role = "CRATE",     n = { 1, 2 }, where = "corner" },
      { role = "STOOL",     n = 1 },
      { role = "LIGHT",     n = 1,        where = "corner" },
    })
    wall_lights(ctx, qi, 1)
  end

  note("no security props placed: Junkers/The Claim Jump is low security by design (searchesLeavers=false)")
end
