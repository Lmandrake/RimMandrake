-- gas_station.lua - a gas-geyser power station whose line runs off the map
-- (structure_procedural_spec.md section 8.8; catalogue A5/A6 lived, A2
-- abandoned; INHABITED_AUGMENTATION_BUILD_1).
--
-- Grammar: the tap (VHGE_HelixienPump standing on the VHGE_GasGeyser it
-- brings with it) -> pipe, one bend, to a VHGE_GasPipeValve -> the tanks
-- (VHGE_GasTank x1-2, staggered) -> the generator hall (7x7 shell, Concrete,
-- entered only through the switch room:
-- generators hugging the back wall, batteries on the side walls, gas wall
-- lamps, a window onto the yard) -> the switch room (attached, sharing the
-- hall's front wall: terminal, stool, desk lamp, papers, the night
-- operator's bedroll and footlocker) -> the line: PowerConduit from the
-- batteries out through the hall wall, then a RUN (E2) to the map edge at
-- `edge_dir`. On half the rolls a second RUN of
-- VHGE_SubterraneanHelixienPipe leaves the valve the other way (A5:
-- "the refinery is elsewhere"). The whole yard is fenced, gate on the road.
--
-- The geyser is a non-edifice (VHGE_GasGeyser: isEdifice false, read from
-- the mod's own 1.6 def), so it goes down as an overlay and the 4x4 pump
-- stands on it at the same origin - the 2x2 sits in the 4x4's centre, the
-- way the vanilla geothermal generator stands on a steam geyser.
--
-- Departures from the spec text, each from a MEASURED source:
--   * VHGE_IndustrialHelixienGenerator is not in the live def dump
--     (2026-11-02): the hall runs one or two VHGE_HelixienGenerator only.
--   * AM_Wall_Atlas_Glass (spec window) is not in the dump either:
--     MUS_SpaceBase_Window (1x1, present) is the window.
--   * OuterRim_AurebeshWordReactor/Warning are absent: VFEPD_DecalWordReactor
--     (2x2 floor decal, isEdifice false) is painted on the yard.
--   * CanisterA is not in the def index: not used.
--   * The spec's Column "every 6-8 cells" along the line belongs to the RUN,
--     which the GenStep extends off-plan; a plan cannot post columns on cells
--     it does not know. None are placed.
--   * The hall is 7x7, not 7x6: two 2x2 generators and two 1x2 batteries in
--     a 5x4 interior leave the door's flood-fill under the 45% the lint asks.
-- 🔴 F4 DOCTRINE, not a template matter: a found gas tap is "found" only if
-- the player cannot BUILD a pump (required_mods.md, VHGE "MANDATORY STRIP").
-- That strip is its own item; this template places the pre-built half.
-- Gas-network connectivity (pump -> valve -> tanks -> generators, lamps)
-- is a live-only reading: the plan lays pipe under/beside every consumer.
--
-- params:
--   road_dir   world side the yard gate faces ("S" default)
--   edge_dir   side the power line RUNs to (default: the world side the
--              hall's local-east wall faces, where the line leaves)
--   state      "lived" (default) | "abandoned" (A2: AncientGenerator for the
--              gas generators, AncientPipelineSection pieces for the live
--              pipe, slag, ctx:ruin(0.3) - "roof half gone")
--   techLevel  below Industrial forces "abandoned": a Neolithic faction never
--              runs this
--
-- Canvas: 20x16 minimum, 24x20 production.

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
local function place_local(ctx, fr, def, role, u, v, lw, lh, stuff, overlay)
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
  if overlay then return ctx:place(def, x, z, rot, stuff, role, true) end
  if not ctx:can_place(def, x, z, rot) then return false end
  return ctx:place(def, x, z, rot, stuff, role)
end

local OPP = { N = "S", S = "N", E = "W", W = "E" }

function min_rect(params)
  local rd = params.road_dir or "S"
  if rd == "E" or rd == "W" then return 16, 20 end
  return 20, 16
end

function build(ctx)
  local p = params
  local road = p.road_dir or "S"
  local tech = p.techLevel or "Industrial"
  local industrial = (tech == "Industrial" or tech == "Spacer" or tech == "Ultra" or tech == "Archotech")
  local state = p.state or "lived"
  if not industrial and state == "lived" then
    state = "abandoned"
    note("techLevel " .. tostring(tech) .. " never runs a gas station: forced to the abandoned read")
  end
  local lived = (state == "lived")
  local W, H = rect.w, rect.h
  if road == "E" or road == "W" then W, H = rect.h, rect.w end
  if W < 20 or H < 16 then
    ctx:refuse("footprint", string.format("%dx%d is below the 20x16 the yard plan needs", W, H))
    return
  end
  local fr = frame(rect.x, rect.z, W, H, road)
  local lot = R(rect.x, rect.z, rect.w, rect.h)
  -- the line leaves through the hall's local-east wall, so its RUN defaults
  -- to that world side (a RIGHT_OF[road] default sent it back across the
  -- whole site whenever the road was N or W)
  local edge = p.edge_dir or fr.side("E")

  local hu, hv = W - 9, H - 9            -- the hall's SW corner (local)
  local pu, pv = 2, hv + 2               -- the pump's SW corner (4x4: v hv+2..hv+5)
  local valve_u, valve_v = 8, hv + 3

  -- ---- 1. the yard: gravel, a concrete pad around the tap and tanks --------
  do
    floor_worn(ctx, fr.rect(1, 1, W - 2, H - 2), "Gravel", "PackedDirt", 0.25)
    local pad = fr.rect(1, hv + 1, hu - 1, H - hv - 2)
    ctx:floor_rect(pad.x, pad.z, pad.w, pad.h, "Concrete")
    -- the geyser's own 2x2 stays natural ground: VHGE_GasGeyser sets
    -- neverOverlapFloors, so no poured floor belongs under it
    local g = fr.rect(pu + 1, pv + 1, 2, 2)
    ctx:floor_rect(g.x, g.z, g.w, g.h, "Gravel")
  end

  -- ---- 2. the tap: the geyser and the pump on it ---------------------------
  do
    -- the 2x2 geyser in the 4x4 pump's centre: local (pu+1, pv+1)
    place_local(ctx, fr, "VHGE_GasGeyser", "GEYSER", pu + 1, pv + 1, 2, 2, nil, true)
    if lived then
      if not place_local(ctx, fr, "VHGE_HelixienPump", "MACHINE", pu, pv, 4, 4) then
        ctx:refuse("VHGE_HelixienPump", "the 4x4 pump did not fit over its geyser")
      end
    else
      -- the pump was hauled off; its pad is scorched and littered
      for _ = 1, rng.int(2, 4) do
        local x, z = fr.cell(pu + rng.int(0, 3), pv + rng.int(0, 3))
        filth(ctx, "Filth_MachineBits", x, z)
      end
      note("abandoned: the pump is gone - the geyser stands open on its pad")
    end
  end

  -- ---- 3. the generator hall (7x7) and the switch room (6x5, attached) -----
  local hall = fr.rect(hu, hv, 7, 7)
  -- no exterior door: one on the west wall lands beside a generator or a
  -- battery on most rolls; the hall is entered through the switch room
  local hi = shell(ctx, "Workshop", hall, { floor = "Concrete", doors = {} })
  local switch = fr.rect(hu, hv - 4, 6, 5)
  local si = shell(ctx, "Office", switch, { floor = "FLOOR_WORK", doors = { { fr.side("S") } } })
  do
    -- the door between them, in the shared wall
    local dx, dz = fr.cell(hu + 2, hv)
    ctx:door(dx, dz)
  end

  local gens = 0
  do
    local gdef = lived and "VHGE_HelixienGenerator" or "AncientGenerator"
    if place_local(ctx, fr, gdef, "GENERATOR", hu + 1, hv + 4, 2, 2) then gens = gens + 1 end
    if rng.chance(0.6) and place_local(ctx, fr, gdef, "GENERATOR", hu + 4, hv + 4, 2, 2) then gens = gens + 1 end
    if gens == 0 then ctx:refuse(gdef, "no generator fitted the hall's back wall") end
    -- batteries on the two side walls, each touching its generator (a
    -- Battery and a generator both TRANSMIT, so cardinal contact joins them
    -- - netinfo.py); one slot of three dropped
    local bats = 0
    for _, bu in ipairs({ hu + 1, hu + 5 }) do
      if place_local(ctx, fr, "Battery", "BATTERY", bu, hv + 2, 1, 2) then bats = bats + 1 end
    end
    -- the two batteries joined by conduit along the hall's front row
    for u = hu + 1, hu + 5 do
      local x, z = fr.cell(u, hv + 1)
      ctx:place("PowerConduit", x, z, 0, nil, "CONDUIT", true)
    end
    -- the line: out through the east wall from the east battery, then RUN
    for u = hu + 6, hu + 7 do
      local x, z = fr.cell(u, hv + 1)
      ctx:place("PowerConduit", x, z, 0, nil, "CONDUIT", true)
    end
    local lx, lz = fr.cell(hu + 7, hv + 1)
    if ctx:has_role("CONDUIT") then ctx:run(lx, lz, edge, "CONDUIT") end
    -- the window onto the yard, in the east wall clear of the line
    local wx, wz = fr.cell(hu + 6, hv + 4)
    ctx:window(wx, wz, "MUS_SpaceBase_Window")
    wall_lights(ctx, hi, 2, lived and "GAS_WALL_LIGHT" or "WALL_LIGHT")
    clutter(ctx, hi, { { role = "CRATE", weight = 1 } }, 1, R(hi.x - 1, hi.z - 1, hi.w + 2, hi.h + 2))
    for _ = 1, rng.int(1, 3) do
      local x, z = rng.int(hi.x, hi.x2), rng.int(hi.z, hi.z2)
      filth(ctx, "Filth_MachineBits", x, z)
    end
    note(string.format("hall: %d %s generator(s), %d battery(ies); the line leaves through the wall and RUNs %s",
      gens, gdef, bats, edge))
  end

  do
    -- switch room interior: u hu+1..hu+4, v hv-3..hv-1
    local function at(u, v) local x, z = fr.cell(u, v) return x, z end
    local term = rng.chance(0.5) and "AncientSecurityTerminal" or "AncientTerminal"
    local tx, tz = at(hu + 4, hv - 1)
    try_def(ctx, term, "MACHINE", tx, tz, 0)
    local sx, sz = at(hu + 4, hv - 2)
    try_def(ctx, "Stool", "STOOL", sx, sz, 0)
    local lx, lz = at(hu + 1, hv - 1)
    try_def(ctx, "RH2_DeskLamplight", "LIGHT", lx, lz, 0)
    place_local(ctx, fr, "Bedroll", "BED", hu + 1, hv - 3, 1, 2)
    local fx, fz = at(hu + 2, hv - 3)
    try_def(ctx, "RH2_ClassicFootlocker", "FOOTLOCKER", fx, fz, 0)
    filth(ctx, "Filth_ScatteredDocuments", rng.int(si.x, si.x2), rng.int(si.z, si.z2))
    wall_lights(ctx, si, 1)
  end

  -- ---- 4. pipe: pump -> one bend -> valve -> tanks -> the hall --------------
  do
    local pipe_n = 0
    local function pipe(u, v)
      local x, z = fr.cell(u, v)
      if lived then
        if ctx:place("VHGE_HelixienPipe", x, z, 0, nil, "GAS_PIPE", true) then pipe_n = pipe_n + 1 end
      end
    end
    -- the pump's east edge, its back row, east to the valve column, then down
    for u = pu + 4, valve_u do pipe(u, pv + 3) end
    for v = pv + 2, valve_v + 1, -1 do pipe(valve_u, v) end
    local vx, vz = fr.cell(valve_u, valve_v)
    local valve_ok = try_def(ctx, "VHGE_GasPipeValve", "VALVE", vx, vz, 0)
    -- valve -> east along the hall's middle row: under the west wall and
    -- past both generators' front edges
    for u = valve_u + 1, hu + 5 do pipe(u, valve_v) end
    -- the tanks, staggered, standing on the pipe's south side
    local tanks = 0
    if place_local(ctx, fr, "VHGE_GasTank", "TANK", valve_u + 1, valve_v - 2, 1, 2) then tanks = tanks + 1 end
    if rng.chance(0.6) and place_local(ctx, fr, "VHGE_GasTank", "TANK", valve_u + 2, valve_v - 3, 1, 2) then
      tanks = tanks + 1
      pipe(valve_u + 2, valve_v - 1)
    end
    if lived then
      if valve_ok and rng.chance(0.5) and ctx:has_role("GAS_PIPE_BURIED") then
        ctx:run(vx, vz, OPP[edge], "GAS_PIPE_BURIED")
        note("A5: a buried helixien pipe leaves the valve for a refinery elsewhere (RUN " .. OPP[edge] .. ")")
      end
    else
      -- dead pipe: a few sections lying where the line was
      local laid = 0
      for _ = 1, rng.int(3, 4) * 3 do
        if laid >= 4 then break end
        local u = rng.int(pu + 4, hu - 2)
        local x, z = fr.cell(u, valve_v + rng.int(-1, 1))
        if try_def(ctx, "AncientPipelineSection", "WRECK", x, z, 0) then laid = laid + 1 end
      end
      for _ = 1, rng.int(2, 3) do
        local x, z = fr.cell(rng.int(2, hu - 2), rng.int(1, hv))
        try_def(ctx, "ChunkSlagSteel", "SCRAP", x, z, 0)
      end
    end
    note(string.format("gas: %d pipe cell(s), valve %s, %d tank(s)", pipe_n, valve_ok and "placed" or "MISSING", tanks))
  end

  -- ---- 5. the yard dressing and the fence -----------------------------------
  do
    -- the reactor word painted on the pad, a floor decal
    local r = fr.rect(pu, hv - 2, 2, 2)
    local dx, dz = origin_for(r.x, r.z, 2, 2, 0)
    ctx:place("VFEPD_DecalWordReactor", dx, dz, 0, nil, "SIGN", true)
    place_local(ctx, fr, "VFEPD_AncientElectricalEquipment", "WRECK", 2, 1, 4, 1)
    -- the gas lights burn from the pipe: each stands beside a pipe cell
    -- (the floodlight on the pump's outlet row, the lamp on the hall row)
    local lights = lived and "VHGE_GasFloodlight" or "FloodLight"
    local fx, fz = fr.cell(valve_u - 1, pv + 4)
    try_def(ctx, lights, "LIGHT", fx, fz, 0)
    if lived then
      local gx, gz = fr.cell(hu - 1, valve_v - 1)
      try_def(ctx, "VHGE_GasLamp", "LIGHT", gx, gz, 0)
    end
    for _ = 1, rng.int(2, 4) do
      local x, z = rng.int(lot.x, lot.x2), rng.int(lot.z, lot.z2)
      if not ctx:occupied(x, z) then filth(ctx, "Filth_OilSmear", x, z) end
    end
    -- the fence ring, the gate on the road side off-centre
    local gate_u = rng.chance(0.5) and rng.int(3, 6) or rng.int(W - 7, W - 4)
    for u = 0, W - 1 do
      for v = 0, H - 1 do
        if u == 0 or u == W - 1 or v == 0 or v == H - 1 then
          local x, z = fr.cell(u, v)
          if v == 0 and u == gate_u then try_place(ctx, "GATE", x, z, 0)
          else try_place(ctx, "FENCE", x, z, 0) end
        end
      end
    end
  end

  -- ---- 6. state -------------------------------------------------------------
  if not lived then
    local gone = ctx:ruin(0.3)
    note(string.format("abandoned (A2): ruin removed %d wall cell(s) - the hall roof half gone", gone or 0))
  else
    note("lived (A5/A6): the station runs; the one thing that lights the dark")
  end
end
