-- tar_refinery.lua - an oil refinery worked off a tar seep
-- (structure_procedural_spec.md section 8.7; catalogue A7 derelict, F3
-- tar-seep rig, F4 Rimefeller; INHABITED_AUGMENTATION_BUILD_1).
--
-- Grammar, road (front) to tar (back): road apron (chem truck, barrel
-- pallets) -> control shack + bunk + power pad on one flank, the cracker
-- yard on a concrete pad in the middle, the cracker shed and the fenced
-- tank farm on the other flank -> the wellheads at the edge of a tar blob
-- painted across the back band. Every wellhead pipes to ONE valve (a
-- Manhattan route with one bend each, never a straight bus), the valve
-- feeds the tank farm and the cracker, and a RUN (E2) carries an
-- OilPipeline from the valve off-map toward `edge_dir`: the pipeline goes
-- to a customer.
--
-- Departures from the spec text, each forced by a MEASURED size (the def
-- size index, rimplace/defsize.py):
--   * CrudeCracker is 6x6 and KOTOR_FuelRefinery 7x7, so neither can "hug the
--     back wall" of the spec's 7x5 shed (a 5x3 interior). The cracker
--     stands OUTDOORS on the concrete pad (the cracker yard) and the 7x5 shed
--     keeps the loading bay, the hopper and the barrels. The VE read's
--     VGE_CompactRefinery (2x1) stands on the same pad.
--   * The control shack is 6x5, not R-OFFICE 3x3: ResourceConsole is 3x2 and
--     a 3x3 interior leaves no cell for the stool, the cabinet or the lamp.
--   * CanisterA, named in the spec's catalogue, is not in the def index;
--     not used.
-- Departures forced by the LIVE MOD SET (def dump 2026-11-02, rimplace lint
-- def-unverified): Alpha Biomes, HMC and VFE Furniture are not loaded, so
--   AB_Tar -> palette TAR (RM_TarShallow, our own FlowWorks tar),
--   HMC_Wall_Tool_Cabinet -> VGE_WallToolCabinet, VFE_DeskLamp ->
--   RH2_DeskLamplight, OuterRim_AurebeshWordRefinery (absent) ->
--   VFEPD_DecalWordRefinery (2x2 decal).
-- 🔴 F4 DOCTRINE, not a template matter: a placed OilWell is "found" only if
-- the player cannot BUILD one. The Rimefeller buildability strip
-- (required_mods.md, Rimefeller "Authoring step: place pre-built + strip
-- buildability") is its own item; this template places the pre-built half.
-- Also a live-only question: a Rimefeller well reads the map's deep-oil
-- grid, which a mapgen-placed well does not create - whether it pumps on a
-- tile without a pool is for the live proof, not this file.
--
-- params:
--   road_dir   world side the road is on ("S" default); the tar is opposite
--   edge_dir   side the export pipeline RUNs to (default: road_dir)
--   state      "lived" (default) | "derelict" (A7: ctx:ruin(0.3), no bunk
--              bedding, more spill, the drill platform as a dead, unpiped
--              second head)
--   faction    Jawa_* -> KOTOR_FuelRefinery replaces the cracker;
--   read       "ve" -> VGE_CompactRefinery replaces it
--
-- Canvas: 26x22 minimum, 34x28 production (wider pad, deeper tar band).

local SIDE_MAP = {
  S = { S = "S", N = "N", E = "E", W = "W" },
  N = { S = "N", N = "S", E = "E", W = "W" },
  E = { S = "E", N = "W", E = "N", W = "S" },
  W = { S = "W", N = "E", E = "N", W = "S" },
}

-- (same private frame helper as mining_site.lua / homestead.lua)
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

-- (mining_site.lua's place_local: the world rect decides the Rot4)
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

local function key(u, v) return u * 1000 + v end

function min_rect(params)
  local rd = params.road_dir or "S"
  if rd == "E" or rd == "W" then return 22, 26 end
  return 26, 22
end

function build(ctx)
  local p = params
  local road = p.road_dir or "S"
  local state = p.state or "lived"
  local derelict = (state == "derelict")
  local W, H = rect.w, rect.h
  if road == "E" or road == "W" then W, H = rect.h, rect.w end
  if W < 26 or H < 22 then
    ctx:refuse("footprint", string.format("%dx%d is below the 26x22 the band plan needs", W, H))
    return
  end
  local fr = frame(rect.x, rect.z, W, H, road)
  local lot = R(rect.x, rect.z, rect.w, rect.h)
  local jawa = (p.faction == "Jawa_Junkers" or p.faction == "Jawa_IndigenousTribes")
  local edge = p.edge_dir or road

  -- ---- bands (local u across, v from the road) -----------------------------
  local band_v = 17                       -- the tar band: v 17..H-1
  local right = W - 8                     -- shed / tank-farm flank starts here
  local walk_u = right - 1                -- the walkway column the valve sits on
  local bus_u = 7                         -- the conduit bus column
  local pad_u0, pad_u1 = 9, walk_u - 1    -- the cracker pad (concrete)

  -- ---- 1. the tar blob (TERRAIN palette TAR, random walk) ------------------
  local tar = {}
  local tar_n = 0
  local tar_def = ctx:role("TAR") or "RM_TarShallow"
  do
    -- the seep lies along the BACK of the band (v >= band_v+3) and spreads
    -- sideways, so the heads can stand in a row in front of it
    local left_side = rng.chance(0.5)
    local mid = math.floor(W / 2)
    local u = left_side and rng.int(mid - 4, mid) or rng.int(mid, mid + 4)
    local v = rng.int(band_v + 3, H - 1)
    local want = rng.int(24, 30 + (W - 26) + (H - 22) * 2)
    for _ = 1, want * 6 do
      if tar_n >= want then break end
      if not tar[key(u, v)] then
        tar[key(u, v)] = true
        tar_n = tar_n + 1
        -- no per-cell CLEAR: every plan opens with CLEAR(all) over its whole
        -- footprint (luaenv.run_template), which already covers the blob
        local x, z = fr.cell(u, v)
        ctx:floor(x, z, tar_def)
      end
      local d = rng.chance(0.7) and rng.int(1, 2) or rng.int(3, 4)   -- spread along the band
      local nu, nv = u, v
      if d == 1 then nu = u + 1 elseif d == 2 then nu = u - 1
      elseif d == 3 then nv = v + 1 else nv = v - 1 end
      -- keep the blob in the band and off the outermost column so a wellhead
      -- can stand beside it on either flank
      if nu >= 1 and nu <= W - 2 and nv >= band_v + 3 and nv <= H - 1 then u, v = nu, nv end
    end
    note(string.format("tar: a %d-cell %s blob, random-walked on the %s side of the back band",
      tar_n, tar_def, left_side and "left" or "right"))
  end

  -- ---- 2. wellheads at the tar edge ----------------------------------------
  -- a 3x3 origin (local SW corner u,v) is a candidate when its footprint is
  -- off the tar, inside the band, and touches the tar within one cell
  local function touches_tar(u, v)
    for du = -1, 3 do for dv = -1, 3 do
      if tar[key(u + du, v + dv)] then return true end
    end end
    return false
  end
  local function on_tar(u, v)
    for du = 0, 2 do for dv = 0, 2 do
      if tar[key(u + du, v + dv)] then return true end
    end end
    return false
  end
  local cands = {}
  for u = 0, W - 3 do
    for v = band_v, H - 3 do
      if not on_tar(u, v) and touches_tar(u, v) then cands[#cands + 1] = { u, v } end
    end
  end
  shuffle(cands)
  local heads = {}
  local want_heads = rng.int(2, 3)
  local function spaced(c)
    for _, h in ipairs(heads) do
      local du, dv = math.abs(c[1] - h[1]), math.abs(c[2] - h[2])
      -- 3-5 cells of open ground between two 3-wide heads: centres 6-8 apart
      -- on the long axis, and never overlapping on the short one
      local gap = math.max(du, dv) - 3
      if gap < 3 or gap > 5 + math.max(W - 26, H - 22) then return false end
    end
    if #heads == 2 then
      -- not collinear: three heads on one row or one column read as a bus
      local a, b = heads[1], heads[2]
      if (a[2] == b[2] and b[2] == c[2]) or (a[1] == b[1] and b[1] == c[1]) then return false end
    end
    return true
  end
  for _, c in ipairs(cands) do
    if #heads >= want_heads then break end
    if spaced(c) then
      local def = (derelict and #heads == 1) and "AncientDrillPlatform"
                  or (rng.chance(0.5) and "OilWell" or "DeepOilWell")
      if place_local(ctx, fr, def, (def == "AncientDrillPlatform") and "WRECK" or "WELL", c[1], c[2], 3, 3) then
        heads[#heads + 1] = { c[1], c[2], def }
      end
    end
  end
  if #heads < 2 then
    ctx:refuse("wellheads", string.format("only %d of %d wellhead(s) found ground at the tar edge", #heads, want_heads))
  end
  -- oil pools around each head
  for _, h in ipairs(heads) do
    for _ = 1, rng.int(3, 5) do
      local u, v = h[1] + rng.int(-1, 3), h[2] + rng.int(-1, 3)
      if u >= 0 and u < W and v >= band_v and v < H then
        local x, z = fr.cell(u, v)
        filth(ctx, rng.chance(0.5) and "Filth_OilSlick" or "FilthOil", x, z)
      end
    end
  end

  -- ---- 3. the cracker yard (concrete pad, the cracker standing on it) ------
  local cu = pad_u0 + math.floor((pad_u1 - pad_u0 + 1 - 7) / 2)
  do
    local pad = fr.rect(pad_u0, 3, pad_u1 - pad_u0 + 1, 9)
    ctx:floor_rect(pad.x, pad.z, pad.w, pad.h, "Concrete")
    local placed
    if jawa then
      placed = place_local(ctx, fr, "KOTOR_FuelRefinery", "MACHINE", cu, 3, 7, 7)
    elseif p.read == "ve" then
      placed = place_local(ctx, fr, "VGE_CompactRefinery", "MACHINE", cu + 2, 6, 2, 1)
    else
      placed = place_local(ctx, fr, "CrudeCracker", "MACHINE", cu, 4, 6, 6)
    end
    if not placed then ctx:refuse("cracker", "the cracker did not fit its pad") end
    -- the word painted on the pad's free back rows (v 10-11; every cracker
    -- read ends by v 9). A floor decal (isEdifice false, Standable - read
    -- from the def dump), so it goes down as an overlay.
    do
      local r = fr.rect(pad_u0, 10, 2, 2)
      local sx, sz = origin_for(r.x, r.z, 2, 2, 0)
      ctx:place("VFEPD_DecalWordRefinery", sx, sz, 0, nil, "SIGN", true)
    end
    for _ = 1, rng.int(2, 4) do
      local x, z = fr.cell(rng.int(pad_u0, pad_u1), rng.int(3, 11))
      if not ctx:occupied(x, z) then filth(ctx, "Filth_OilSmear", x, z) end
    end
  end

  -- ---- 4. the cracker shed (7x5): loading bay, hopper, barrels -------------
  do
    local shed = fr.rect(right, 3, 7, 5)
    local si = shell(ctx, "Workshop", shed, { floor = "Concrete", doors = { { fr.side("W") } } })
    local sh = R(si.x - 1, si.z - 1, si.w + 2, si.h + 2)
    -- door_on centres a 5-long wall's door on its middle cell (local v=5),
    -- so the back row (v=6) is the working wall: the loading bay beside the
    -- door, the hopper, then the barrels, which turn down the far wall. Every
    -- one of them keeps an open cell on the v=5 aisle (lint aisle-blocked).
    local function at(u, v) local x, z = fr.cell(u, v) return x, z end
    local bx0, bz0 = at(right + 1, 6)
    try_def(ctx, "RefineryLoadingBay", "MACHINE", bx0, bz0, 0)
    local hx, hz = at(right + 2, 6)
    try_def(ctx, "ChemfuelHopper", "MACHINE", hx, hz, 0)
    -- the far corner (right+5, 6) stays empty: a barrel there is walled in
    -- by its two neighbours
    local slots = { { right + 5, 4 }, { right + 5, 5 }, { right + 4, 6 }, { right + 3, 6 } }
    shuffle(slots)
    local barrels = 0
    for i = 1, rng.int(3, 4) do
      local bx, bz = at(slots[i][1], slots[i][2])
      if try_def(ctx, "OilBarrel", "BARREL", bx, bz, 0) then
        barrels = barrels + 1
        filth(ctx, "Filth_Fuel", bx, bz)
      end
    end
    wall_lights(ctx, si, 1)
    note(string.format("cracker shed: loading bay by the door, hopper, %d oil barrel(s) on spilled fuel", barrels))
  end

  -- ---- 5. the tank farm: fenced concrete pad, a gate on the road side ------
  local farm = fr.rect(right, 9, 8, 8)
  do
    local fi = inner(farm)
    ctx:floor_rect(fi.x, fi.z, fi.w, fi.h, "Concrete")
    local gate_u = right + rng.int(3, 4)
    for u = right, right + 7 do
      for v = 9, 16 do
        if u == right or u == right + 7 or v == 9 or v == 16 then
          local x, z = fr.cell(u, v)
          if u == gate_u and v == 9 then try_place(ctx, "GATE", x, z, 0)
          else try_place(ctx, "FENCE", x, z, 0) end
        end
      end
    end
    local tanks = 0
    if place_local(ctx, fr, "OilStorage", "TANK", right + 1, 13, 3, 3) then tanks = tanks + 1 end
    if place_local(ctx, fr, "FuelStorage", "TANK", right + 5, 12, 2, 4) then tanks = tanks + 1 end
    local dead = { "VFEPD_ChemfuelTank_Prop", "ChemfuelTank" }
    shuffle(dead)
    if place_local(ctx, fr, dead[1], "WRECK", right + 1, 10, 2, 2) then tanks = tanks + 1 end
    if rng.chance(0.7) and place_local(ctx, fr, dead[2], "WRECK", right + 4, 10, 2, 2) then tanks = tanks + 1 end
    note(string.format("tank farm: %d tank(s) on a fenced concrete pad; no flame within 6 of it", tanks))
  end

  -- ---- 6. the control shack (7x6) and the bunk (7x5) ------------------------
  do
    local shack = fr.rect(0, 3, 7, 6)
    local si = shell(ctx, "Office", shack, { floor = "FLOOR_WORK", doors = { { fr.side("S") } } })
    local sh = R(si.x - 1, si.z - 1, si.w + 2, si.h + 2)
    if not place_local(ctx, fr, "ResourceConsole", "MACHINE", 1, 6, 3, 2) then
      ctx:refuse("ResourceConsole", "the 3x2 console did not fit the shack's back wall")
    end
    local cx, cz = fr.cell(5, 7)
    try_def(ctx, "VGE_WallToolCabinet", "TOOL_CABINET", cx, cz, 0)
    local lx, lz = fr.cell(5, 6)
    try_def(ctx, "RH2_DeskLamplight", "LIGHT", lx, lz, 0)
    local stx, stz = fr.cell(2, 5)
    try_def(ctx, "Stool", "STOOL", stx, stz, 0)
    filth(ctx, "Filth_ScatteredDocuments", rng.int(si.x, si.x2), rng.int(si.z, si.z2))
    wall_lights(ctx, si, 1)
  end
  do
    local bunk = fr.rect(0, 9, 7, 5)
    local bi = shell(ctx, "Bedroom", bunk, { floor = "FLOOR_POOR", doors = { { fr.side("E") } } })
    local sh = R(bi.x - 1, bi.z - 1, bi.w + 2, bi.h + 2)
    if not derelict then
      local beds = along_wall(ctx, "BED", bi, fr.side("W"), 2, { face = "wall", gap = 0 })
      note(string.format("bunk: %d bedroll(s) for the two-hand crew", beds))
    else
      filth(ctx, "Filth_MoldyUniform", rng.int(bi.x, bi.x2), rng.int(bi.z, bi.z2))
    end
    clutter(ctx, bi, { { role = "FOOTLOCKER", weight = 2 }, { role = "CRATE", weight = 1 } }, 1, sh)
    wall_lights(ctx, bi, 1)
  end

  -- ---- 7. power: FuelPowerplant burns the product; battery; the bus --------
  do
    local pad = fr.rect(0, 14, 5, 3)
    ctx:floor_rect(pad.x, pad.z, pad.w, pad.h, "Concrete")
    local ok_gen = place_local(ctx, fr, "FuelPowerplant", "GENERATOR", 1, 15, 2, 2)
    local ok_bat = place_local(ctx, fr, "Battery", "BATTERY", 3, 15, 1, 2)
    if not ok_gen then ctx:refuse("FuelPowerplant", "the 2x2 powerplant did not fit its pad") end
    -- the bus: from the battery's flank east to column bus_u, then toward the road
    local bus = 0
    for u = 4, bus_u do
      local x, z = fr.cell(u, 15)
      if ctx:place("PowerConduit", x, z, 0, nil, "CONDUIT", true) then bus = bus + 1 end
    end
    for v = 2, 16 do
      local x, z = fr.cell(bus_u, v)
      if ctx:place("PowerConduit", x, z, 0, nil, "CONDUIT", true) then bus = bus + 1 end
    end
    -- two floodlights over the wells, within ConnectMaxDist 6 of the bus top
    for _, u in ipairs({ bus_u - 1, bus_u + 1 }) do
      local x, z = fr.cell(u, 16)
      try_def(ctx, "FloodLight", "LIGHT", x, z, 0)
    end
    note(string.format("power: FuelPowerplant + Battery on a pad (%s), a %d-cell conduit bus up column 7; "
      .. "the shack console, lamps and floodlights hang within 6 of it", ok_bat and "battery placed" or "NO battery", bus))
  end

  -- ---- 8. the valve, the pipe runs, the export RUN --------------------------
  do
    local vv = band_v
    local vx, vz = fr.cell(walk_u, vv)
    local valve_ok = try_def(ctx, "pipelineValve", "VALVE", vx, vz, 0)
    if not valve_ok then
      vv = band_v - 1
      vx, vz = fr.cell(walk_u, vv)
      valve_ok = try_def(ctx, "pipelineValve", "VALVE", vx, vz, 0)
    end
    if not valve_ok then ctx:refuse("pipelineValve", "the walkway cell for the valve was taken") end
    local pipe_n = 0
    local function pipe(u, v)
      if u == walk_u and v == vv then return end
      local x, z = fr.cell(u, v)
      if ctx:place("OilPipeline", x, z, 0, nil, "OIL_PIPE", true) then pipe_n = pipe_n + 1 end
    end
    -- one bend per head: along the head's middle row to the valve column,
    -- then along the column to the valve
    for _, h in ipairs(heads) do
      if h[3] == "AncientDrillPlatform" then goto continue end   -- the dead head is not piped
      local hu, hv = h[1] + 1, h[2] + 1
      local su = (hu < walk_u) and 1 or -1
      local u0 = (hu < walk_u) and (h[1] + 3) or (h[1] - 1)
      for u = u0, walk_u, su do pipe(u, hv) end
      local sv = (hv < vv) and 1 or -1
      for v = hv, vv, sv do pipe(walk_u, v) end
      ::continue::
    end
    -- valve -> the oil tank (under the fence) and -> the cracker
    for u = walk_u, right + 1 do pipe(u, 15) end
    for v = 15, vv do pipe(walk_u, v) end
    for v = 10, 15 do pipe(walk_u, v) end
    -- row 10 runs from the cracker's west column to the walkway: every
    -- cracker read (6x6 at v4, 7x7 at v3) ends on v9, so the row lies along
    -- its whole back edge; the VE read's 2x1 at v6 gets a spur up to it
    for u = cu, walk_u do pipe(u, 10) end
    if not jawa and p.read == "ve" then
      for v = 7, 9 do pipe(cu + 2, v) end
    end
    -- the export line: off-map toward edge_dir, engine-side
    if valve_ok and ctx:has_role("OIL_PIPE") then
      ctx:run(vx, vz, edge, "OIL_PIPE")
    end
    note(string.format("pipes: %d head(s) -> one valve, %d OilPipeline cell(s); RUN to the %s edge",
      #heads, pipe_n, edge))
  end

  -- ---- 9. the road apron: the chem truck and the barrel pallets ------------
  do
    local apron = fr.rect(0, 0, W, 3)
    floor_worn(ctx, apron, "Gravel", "PackedDirt", 0.2)
    local tu = rng.chance(0.5) and 1 or (W - 6)
    place_local(ctx, fr, "AncientChemtruck", "WRECK", tu, 0, 4, 2)
    local n = rng.int(1, 2)
    local pu = (tu == 1) and 9 or (W - 12)
    for i = 0, n - 1 do
      place_local(ctx, fr, "AncientChembarrelPallet", "WRECK", pu + i * 3, 0, 2, 2)
    end
  end

  -- ---- 10. state ------------------------------------------------------------
  if derelict then
    local gone = ctx:ruin(0.3)
    for _ = 1, rng.int(3, 6) do
      local x, z = rng.int(lot.x, lot.x2), rng.int(lot.z, lot.z2)
      if not ctx:occupied(x, z) then filth(ctx, rng.chance(0.5) and "Filth_OilSlick" or "Filth_Sand", x, z) end
    end
    note(string.format("derelict (A7): ruin removed %d wall cell(s); the drill platform is the dead second head", gone or 0))
  else
    note("lived (F3): a two-hand crew; nothing that burns stands within 6 of a tank")
  end
end
