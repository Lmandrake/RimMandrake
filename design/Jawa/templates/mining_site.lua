-- mining_site.lua - a small quarry/mine worked into a rock mass
-- (structure_procedural_spec.md section 8.3; catalogue E1 "AncientQuarry";
-- roster whisper #16 The Prospector's Bones as its `abandoned` read).
--
-- Grammar, front (road) to back (rock): road-side apron -> ore yard -> the
-- works (rail, cars, ore dresser, conveyors, tool shed, bunkhouse, a power
-- apron on Industrial+) -> the face: a 3-wide cut into rock with a poor seam
-- left in its walls.
--
-- 🔴 THE FACE BRINGS ITS OWN ROCK. Every plan rimplace builds carries an
-- unconditional CLEAR(all) over its whole footprint ahead of anything a
-- template says (luaenv.run_template, R1) - so the spec's "CLEAR mode soft
-- on the back 3 rows so the seam stays" cannot be honoured: whatever rock
-- the tile had under the back rows is mined out before this plan runs. The
-- honest answer is to rebuild the rock mass from the palette's ROCK def
-- (Sandstone by default - params.rock_side/rock pick the side and the
-- stone) and cut the face into THAT, so the site reads the same on any
-- tile. Reported in INHABITED_AUGMENTATION_BUILD_1 as an E1 gap: a template
-- cannot say "keep the map's rock here".
--
-- params:
--   rock_side  world side the rock mass is on ("N" default) - the front
--              faces away from it
--   state      "abandoned" (default - this IS the ancient-quarry read) |
--              "lived" (a crew still works it: hay in a fence corner for the
--              cart animal, no bones, no Prospector)
--   techLevel  Industrial+ gets the generator/bus/floodlight/lamp; Neolithic
--              gets torches and no power
--
-- Canvas: 24x18 minimum, from build()'s own column plan
--   [shed 5][1][rail zone 5][1][ore dresser 5][1][bunkhouse 6] = 24 across,
--   apron 3 + yard 4 + works 7 (the bunkhouse) + face 4 = 18 deep;
-- 32x24 production (the face deepens to 6, the works band to 11, a mud
-- carriage appears in the widened yard).

local SIDE_MAP = {
  S = { S = "S", N = "N", E = "E", W = "W" },
  N = { S = "N", N = "S", E = "E", W = "W" },
  E = { S = "E", N = "W", E = "N", W = "S" },
  W = { S = "W", N = "E", E = "N", W = "S" },
}
local OPP = { N = "S", S = "N", E = "W", W = "E" }

-- (same private frame helper as homestead.lua - see the note there)
local function frame(ox, oz, W, H, face)
  local f = { W = W, H = H, face = face }
  function f.rect(u, v, w, h)
    if face == "S" then return R(ox + u, oz + v, w, h)
    elseif face == "N" then return R(ox + u, oz + (H - v - h), w, h)
    elseif face == "E" then return R(ox + (H - v - h), oz + u, h, w)
    else return R(ox + v, oz + u, h, w) end
  end
  function f.cell(u, v) local r = f.rect(u, v, 1, 1) return r.x, r.z end
  function f.side(s) return SIDE_MAP[face][s] end
  -- a Rot4 authored in the local frame, turned to the world
  local TURN = { S = 0, W = 1, N = 2, E = 3 }
  function f.rot(r) return (r + TURN[face]) % 4 end
  return f
end

local function try_def(ctx, def, role, x, z, rot)
  rot = rot or 0
  if not ctx:can_place(def, x, z, rot) then return false end
  return ctx:place(def, x, z, rot, nil, role)
end

local function filth(ctx, def, x, z)
  return ctx:place(def, x, z, 0, nil, "FILTH", true)
end

-- Place `def` so its footprint covers the LOCAL rect (u,v,lw,lh): the world
-- rect decides the Rot4 (0 if the def's own w x h matches it, 1 if turned),
-- and `origin_for` applies GenAdj's even-size origin shift for that
-- rotation. This is what makes a 5x3 mining car or a 2x2 generator land on
-- the same cells whichever way the whole site faces - the first draft
-- passed a turned Rot4 and a naive origin, and a 2x2 generator slid one
-- cell onto the conduit bus when the rock was on the east.
local function place_local(ctx, fr, def, role, u, v, lw, lh, stuff)
  if def == nil then return false end
  local r = fr.rect(u, v, lw, lh)
  local dw, dh = ctx:width_of(def), ctx:height_of(def)
  local rot
  if dw == r.w and dh == r.h then rot = 0
  elseif dh == r.w and dw == r.h then rot = 1
  else
    ctx:refuse(def, string.format("is %dx%d, not the %dx%d the site plan assumed", dw, dh, r.w, r.h))
    return false
  end
  local x, z = origin_for(r.x, r.z, r.w, r.h, rot)
  if not ctx:can_place(def, x, z, rot) then return false end
  return ctx:place(def, x, z, rot, stuff, role)
end

local function clamp(v, lo, hi) return math.max(lo, math.min(hi, v)) end

-- a clump of n 1x1 things around (x,z): random-start, spiral outward
local function clump(ctx, def, role, x, z, n, within)
  local got = 0
  for _ = 1, n * 4 do
    if got >= n then break end
    local cx, cz = x + rng.int(-2, 2), z + rng.int(-1, 1)
    if in_rect(cx, cz, within) and try_def(ctx, def, role, cx, cz, 0) then got = got + 1 end
  end
  return got
end

function min_rect(params)
  -- the column plan is 24 across the front and 18 deep toward the rock; a
  -- rock mass on the E or W side turns the whole canvas on its side
  local rs = params.rock_side or "N"
  if rs == "E" or rs == "W" then return 18, 24 end
  return 24, 18
end

function build(ctx)
  local p = params
  local rock_side = p.rock_side or "N"
  local face_dir = OPP[rock_side]
  local state = p.state or "abandoned"
  local tech = p.techLevel or "Neolithic"
  local industrial = (tech == "Industrial" or tech == "Spacer" or tech == "Ultra" or tech == "Archotech")
  local W, H = rect.w, rect.h
  if face_dir == "E" or face_dir == "W" then W, H = rect.h, rect.w end
  if W < 24 or H < 18 then
    ctx:refuse("footprint", string.format("%dx%d is below the 24x18 the column plan needs", W, H))
    return
  end
  local fr = frame(rect.x, rect.z, W, H, face_dir)
  local lot = R(rect.x, rect.z, rect.w, rect.h)
  local jawa = (p.faction == "Jawa_Junkers" or p.faction == "Jawa_IndigenousTribes")

  -- ---- bands -----------------------------------------------------------------
  local depth = clamp(H - 13, 5, 7)                 -- rock rows: a 4-deep cut + back wall at 18 deep, 6 + wall at 24+
  local face_v = H - depth                          -- first rock row
  local works_v0 = 6                                -- yard is v 3..5
  local extra_w = W - 24
  local ur = 8                                      -- the rail column
  local shed = fr.rect(0, works_v0, 5, 6)                -- R-WORK: 3x4 interior
  local dresser_u = 14
  local bunk_u = W - 6
  local bunk_v = works_v0 + rng.int(0, math.max(0, face_v - works_v0 - 7))
  local bunk = fr.rect(bunk_u, bunk_v, 6, 7)

  -- ---- the apron (road side): gravel, the cart, the sign, spoil cuts -------
  local apron = fr.rect(0, 0, W, 3)
  floor_worn(ctx, apron, "Gravel", "PackedDirt", 0.2)
  do
    local cart_u = rng.chance(0.5) and 3 or (W - 4)
    -- the ox cart (3x5) lies along the road as 5x3; the truck (2x4) as 4x2
    if industrial then
      place_local(ctx, fr, "AncientRustedTruck", "WRECK", cart_u - 2, 0, 4, 2)
    else
      place_local(ctx, fr, "VFEPD_OxCart", "WRECK", cart_u - 2, 0, 5, 3)
    end
    -- a sign by the road, off the cart's end. The spec's ES_QuarrySign is
    -- UNMEASURED in the def size index (defsize's scan does not see the
    -- Medieval Signs defs at all - a scanner gap, reported), so the
    -- palette's measured SIGN stands in until the index knows it.
    local sx, sz = fr.cell(cart_u + rng.pick({ -4, 4 }), 0)
    try_place(ctx, "SIGN", sx, sz, 0)
    if industrial then
      -- spoil cuts: a short jagged line of trench at the road edge
      local tu = rng.int(8, W - 9)
      for i = 0, rng.int(1, 2) do
        local tx, tz = fr.cell(tu + i, rng.int(0, 1))
        try_def(ctx, "FT_Trench", "BARRICADE", tx, tz, fr.rot(1))
      end
    else
      local tu = rng.int(8, W - 9)
      for i = 0, rng.int(1, 2) do
        local tx, tz = fr.cell(tu + i, 0)
        try_def(ctx, "FT_Ditch", "BARRICADE", tx, tz, fr.rot(1))
      end
    end
  end

  -- ---- the rail: packed dirt from the yard to the face mouth ---------------
  for v = 3, face_v - 1 do
    local x, z = fr.cell(ur, v)
    ctx:floor(x, z, "PackedDirt")
  end
  -- the yard's own worn ground around the rail head
  floor_patch(ctx, fr.rect(ur - 3, 3, 7, 4), "Gravel", lot)

  -- ---- the ore yard: chunk heaps, a little steel, the mud carriage ---------
  local chunk = ctx:role("ROCK_CHUNK") or "ChunkSandstone"
  local heaps = 0
  for _ = 1, 2 do
    local hu = rng.pick({ rng.int(1, 5), rng.int(11, W - 8) })
    -- v capped at 4, not 5: clump()'s own +/-1 vertical scatter can reach one
    -- row past this anchor, and the tool shed's rect starts at works_v0 (6) -
    -- an anchor at v=5 could scatter a chunk into v=6, colliding with the
    -- shed's wall once shell() builds it later in this same function. Found
    -- by lint at seed 0/1 (rock_side N): "Wall: footprint overlaps
    -- ChunkSandstone at (3,6)".
    local hx, hz = fr.cell(hu, rng.int(3, 4))
    heaps = heaps + clump(ctx, chunk, "SCRAP", hx, hz, rng.int(3, 5), lot)
  end
  for _ = 1, rng.int(1, 2) do
    local sx, sz = fr.cell(rng.int(11, 17), rng.int(3, 6))
    try_def(ctx, "Steel", "STEEL", sx, sz, 0)
  end
  if extra_w >= 5 then
    -- 5 wide, centred: keep its east end 2 clear of the bus column (W-7)
    local mu = math.min(17 + math.floor(extra_w / 2), W - 10)
    place_local(ctx, fr, "VFEPD_AncientMudCarriage", "WRECK_BIG", mu - 2, 3, 5, 3)
  end

  -- ---- the works ----------------------------------------------------------
  -- cars on the rail: one on the line, one derailed a cell off it
  do
    local cv = math.min(face_v - 3, works_v0 + 4)
    local car = rng.pick({ "VFEPD_AncientRockMiningCar", "VFEPD_AncientEmptyMiningCar", "VFEPD_AncientSteelMiningCars" })
    place_local(ctx, fr, car, "RAIL_CAR", ur - 1, cv - 2, 3, 5)
    place_local(ctx, fr, "VFEPD_AncientEmptyMiningCar", "RAIL_CAR", ur + 1, 3, 3, 5)
  end
  -- the ore dresser beside the rail, conveyors from it toward the yard
  do
    local dv = works_v0 + 2 + rng.int(0, math.max(0, face_v - works_v0 - 6))
    local machine = rng.chance(0.5) and "BreadMoAM_AncientOreDressingMachine" or "VFEPD_AncientOreDressingMachine"
    if not place_local(ctx, fr, machine, "MACHINE", dresser_u - 2, dv - 2, 5, 5) then
      ctx:refuse(machine, "the 5x5 ore dresser did not fit beside the rail")
    end
    for i, cu in ipairs({ dresser_u - 1, dresser_u + 1 }) do
      if i == 1 or rng.chance(0.6) then
        -- 1x4 conveyors butting against the dresser's yard-side row
        place_local(ctx, fr, "BreadMoAM_AncientMineralConveyor", "MACHINE", cu, dv - 6, 1, 4)
      end
    end
    for _ = 1, rng.int(2, 4) do
      local fx, fz = fr.cell(dresser_u + rng.int(-3, 3), dv + rng.int(-3, 3))
      if in_rect(fx, fz, lot) and not ctx:occupied(fx, fz) then filth(ctx, "Filth_RubbleRock", fx, fz) end
    end
  end

  -- tool shed (R-WORK 3x4): bench on the back wall, tool cabinet, a shelf
  -- with a pickaxe on it, dirt at the door - everything after the bench
  -- goes in under the walkability guard, this room is small
  do
    local si = shell(ctx, "Workshop", shed, { floor = industrial and "FLOOR_WORK" or "FLOOR_POOR", doors = { { fr.side("E") } } })
    along_wall(ctx, "WORKBENCH", si, fr.side("N"), 1, {})
    local sh = R(si.x - 1, si.z - 1, si.w + 2, si.h + 2)
    local ok, tx, tz = try_near_walkable(ctx, "STORAGE", si.x, si.z, 0, 2, si, sh)
    if ok then ctx:place("SurvivalTools_Pickaxe", tx, tz, 0, nil, "TOOL", true) end
    try_near_walkable(ctx, "TOOL_CABINET", si.x2, si.z, 0, 2, si, sh)
    clutter(ctx, si, { { role = "CRATE", weight = 2 }, { role = "STOOL", weight = 2 } }, 2, sh)
    for _ = 1, rng.int(1, 2) do
      local px, pz = rng.int(si.x, si.x2), rng.int(si.z, si.z2)
      if not ctx:occupied(px, pz) then ctx:place("BreadMoAM_PickAxe", px, pz, 0, nil, "TOOL", true) end
    end
    filth(ctx, "Filth_Dirt", rng.int(si.x, si.x2), rng.int(si.z, si.z2))
    wall_lights(ctx, si, 1)
    if ctx:has_role("LIGHT") and not industrial then hug(ctx, "LIGHT", si, { fr.side("N") }, { mode = "corner" }) end
  end

  -- bunkhouse (R-BARRACKS 4x5 for 3-4): bedrolls head-to-wall on the two
  -- long walls, alternating, one slot dropped; footlockers at some feet; a
  -- stove corner; lockers, a stool, a crate, a ragged uniform; the quarry
  -- sign at its door
  do
    -- door on the short (yard) wall. The spec's "beds along the two long
    -- walls" cannot work in a 4-wide interior: a 2-long bedroll from each
    -- side fills a row, and two on staggered rows leave no path (measured:
    -- 3 unreached). So bedrolls head-to-wall on the BACK wall - up to 4
    -- slots, one dropped - and the fourth, if any, on a side wall near the
    -- back; the front half of the room stays open to the door.
    local bside = fr.side("S")
    local bi = shell(ctx, "Barracks", bunk, { floor = industrial and "FLOOR_WORK" or "FLOOR_POOR", doors = { { bside } } })
    local sh = R(bi.x - 1, bi.z - 1, bi.w + 2, bi.h + 2)
    -- four slots on the back wall, three taken: the dropped slot is the
    -- crew's empty bunk (R-BARRACKS "1 in 4 slots dropped")
    local want = 3
    local beds = along_wall(ctx, "BED", bi, fr.side("N"), want, { face = "wall", gap = 0 })
    local feet = {}
    for _, b in ipairs(LAST_PLACED) do feet[#feet + 1] = b end
    for _, b in ipairs(feet) do
      if rng.chance(0.6) then try_near_walkable(ctx, "FOOTLOCKER", b[1], b[2], 0, 1, bi, sh) end
    end
    -- the stove on the door wall (never a back corner, which boxes a bunk)
    if along_wall(ctx, "STOVE", bi, bside, 1, { gap = 1 }) == 0 then
      try_near_walkable(ctx, "STOVE", bi.x, bi.z, 0, 2, bi, sh)
    end
    clutter(ctx, bi, {
      { role = "CRATE", weight = 2 }, { role = "STOOL", weight = 2 },
      { role = "SHELF_SMALL", weight = 1 }, { role = "CANDLE", weight = 1 },
      { role = "LOCKER", weight = 2 },
    }, 3, sh)
    filth(ctx, "Filth_MoldyUniform", rng.int(bi.x, bi.x2), rng.int(bi.z, bi.z2))
    wall_lights(ctx, bi, 1)
    if industrial then
      -- a standing lamp, kept within ConnectMaxDist 6 of the bus column
      local lx, lz = fr.cell(bunk_u + 1, bunk_v + rng.int(1, 5))
      try_place(ctx, "LIGHT", lx, lz, 0)
    else
      hug(ctx, "LIGHT", bi, { fr.side("S") }, { mode = "corner" })
    end
    local d = DIR[SIDE_ROT[bside]]
    local lat = (bside == "N" or bside == "S") and { 1, 0 } or { 0, 1 }
    for _, c in ipairs(wall_cells(bi, bside)) do
      if ctx:role_at(c[1] + d[1], c[2] + d[2]) == "DOOR" then
        -- the sign one cell out from the door and one to the side
        local sx, sz = c[1] + d[1] * 2 + lat[1], c[2] + d[2] * 2 + lat[2]
        try_place(ctx, "SIGN", sx, sz, 0)
        break
      end
    end
    note(string.format("bunkhouse: %d bedroll(s) for a crew of %d", beds, want))
  end

  -- power (Industrial+): a wood-fired generator in the yard against the bus
  -- column between the dresser and the bunkhouse; the bus runs to the face
  -- mouth and bends west to a floodlight there. Transmitters first is the
  -- GenStep's job; cardinal contiguity is this template's.
  local bus_u = bunk_u - 1
  if industrial and ctx:has_role("CONDUIT") then
    local gen_def = rng.chance(0.5) and "WoodFiredGenerator" or "ChemfuelPoweredGenerator"
    if not place_local(ctx, fr, gen_def, "GENERATOR", bus_u + 1, works_v0 - 3, 2, 2) then
      ctx:refuse(gen_def, "the 2x2 generator did not fit in the yard against the bus")
    end
    for v = works_v0 - 3, face_v - 1 do
      local x, z = fr.cell(bus_u, v)
      if not ctx:occupied(x, z) then ctx:place_role("CONDUIT", x, z, 0) end
    end
    for u = ur + 3, bus_u - 1 do
      local x, z = fr.cell(u, face_v - 1)
      if not ctx:occupied(x, z) then ctx:place_role("CONDUIT", x, z, 0) end
    end
    local fx, fz = fr.cell(ur + 2, face_v - 1)
    try_def(ctx, "FloodLight", "LIGHT", fx, fz, 0)
    for _ = 1, rng.int(2, 3) do
      local mx, mz = fr.cell(bus_u + rng.int(0, 2), works_v0 - 3 + rng.int(-1, 2))
      if in_rect(mx, mz, lot) and not ctx:occupied(mx, mz) then filth(ctx, "Filth_MachineBits", mx, mz) end
    end
    note("power: generator is a TRANSMITTER cardinally on the conduit bus; the floodlight at the "
      .. "mouth and the bunkhouse lamp are CONNECTORS within 6 of it")
  else
    local tx, tz = fr.cell(ur + 2, face_v - 1)
    try_place(ctx, "LIGHT", tx, tz, 0)
    local tx2, tz2 = fr.cell(ur - 2, face_v - 1)
    try_place(ctx, "LIGHT", tx2, tz2, 0)
  end

  -- ---- the face: E1 CLEAR over the cut, then the rock mass, the cut, the
  -- seam, supports, rubble, a lamp, a charge, the Prospector -------------
  local cut = fr.rect(ur - 1, face_v, 3, depth - 1)
  ctx:clear(cut.x, cut.z, cut.w, cut.h, "all")     -- documents the intent; the footprint clear precedes it anyway
  local rock = ctx:role("ROCK")
  local seam = ctx:role("SEAM")
  local rock_roof = ctx:role("ROOF_ROCK") or "RoofRockThin"
  local rock_n, seam_n = 0, 0
  for v = face_v, H - 1 do
    for u = 0, W - 1 do
      local x, z = fr.cell(u, v)
      local in_cut = (v < H - 1) and (u >= ur - 1 and u <= ur + 1)
      if in_cut then
        ctx:floor(x, z, "Gravel")
      else
        -- a seam cell where the cut's back or side wall would be, 50/50
        local on_wall = (v == H - 1 and u >= ur - 1 and u <= ur + 1)
                     or (v < H - 1 and (u == ur - 2 or u == ur + 2))
        local def = (on_wall and seam and rng.chance(0.5)) and seam or rock
        if def and ctx:place(def, x, z, 0, nil, (def == seam) and "SEAM" or "WALL") then
          rock_n = rock_n + 1
          if def == seam then
            seam_n = seam_n + 1
            -- rubble in front of it, inside the cut
            local du = (u < ur) and 1 or ((u > ur) and -1 or 0)
            local dv = (v == H - 1) and -1 or 0
            local rx, rz = fr.cell(u + du, v + dv)
            filth(ctx, "Filth_RubbleRock", rx, rz)
          end
        end
      end
      ctx:roof(x, z, rock_roof)
    end
  end
  -- two supports at the mouth, lining the cut's side columns 4 deep
  -- (1x4, even along its length: the origin's own shift differs per world
  -- rotation, so try the two candidate origins and keep whichever fits
  -- entirely inside the cut)
  local supports = 0
  for i, su in ipairs({ ur - 1, ur + 1 }) do
    local def = (i == 1) and "VFEPD_AncientTunnelStructuralSupport_a" or "VFEPD_AncientTunnelStructuralSupport_b"
    if place_local(ctx, fr, def, "SUPPORT", su, face_v, 1, 4) then supports = supports + 1 end
  end
  if supports < 2 then note(string.format("only %d of 2 tunnel supports fitted the cut", supports)) end
  -- the walkway keeps a lamp just inside the mouth on one side
  do
    local lx, lz = fr.cell(ur, face_v)
    if not industrial then try_def(ctx, "AncientLamp", "LIGHT", lx, lz, 0) end
  end
  if industrial and rng.chance(0.7) then
    local mx, mz = fr.cell(ur, H - 2)
    try_def(ctx, "AncientMiningCharge", "TRAP", mx, mz, 0)
  end
  note(string.format("face: %d rock cell(s) rebuilt from ROCK=%s, %d seam cell(s) of %s in a %d-deep cut",
    rock_n, tostring(rock), seam_n, tostring(seam), depth - 1))

  -- ---- state ----------------------------------------------------------------
  if state == "abandoned" then
    for _ = 1, rng.int(2, 4) do
      local bx, bz = fr.cell(ur + rng.int(-1, 1), face_v + rng.int(0, depth - 2))
      if not ctx:occupied(bx, bz) then
        try_def(ctx, rng.chance(0.5) and "DA_GnawedBones" or "VFEPD_FilthBones", "DECOR", bx, bz, 0)
      end
    end
    if rng.chance(0.5) then
      -- the Prospector, where the seam ran out (E3: remains, never a colonist)
      local px, pz = fr.cell(ur, H - 3)
      ctx:pawn("Miner", px, pz, "wild", "skeleton")
      note("the Prospector's Bones: a Miner's skeleton at the end of the cut (PAWN, mapgen-only)")
    else
      place_local(ctx, fr, ctx:role("GRAVE"), "GRAVE", bunk_u - 2, bunk_v + rng.int(0, 3), 1, 2)
      note("a grave by the bunkhouse - whoever came back buried the Prospector")
    end
    for _ = 1, 3 do
      local sx, sz = rng.int(lot.x, lot.x2), rng.int(lot.z, lot.z2)
      if not ctx:occupied(sx, sz) then filth(ctx, "Filth_Sand", sx, sz) end
    end
  else
    -- a working crew: a 2x2 fence corner with hay for the cart animal
    local fu, fv = (rng.chance(0.5) and 6 or (W - 8)), 3
    for _, c in ipairs({ { fu, fv }, { fu + 1, fv }, { fu, fv + 1 } }) do
      local x, z = fr.cell(c[1], c[2])
      try_place(ctx, "FENCE", x, z, 0)
    end
    local hx, hz = fr.cell(fu + 1, fv + 1)
    try_def(ctx, "Hay", "HAY", hx, hz, 0)
    filth(ctx, "Filth_AnimalFilth", hx, hz)
    note("lived: a crew still works the seam; hay in a fence corner for the cart animal")
  end
  if jawa and ctx:has_role("JUNK") then
    local jx, jz = fr.cell(rng.int(1, 6), rng.int(3, 6))
    try_place(ctx, "JUNK", jx, jz, 0)
  end
end
