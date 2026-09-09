-- moisture_walled_compound.lua - "The Walled Compound" (MOISTURE_FARM_TEMPLATES_1,
-- RimUtinni tier, ZBiome_Badlands): a real wall ring (not sandbags) around a
-- family house, a small cistern room, a vaporator cluster on the shade side,
-- an animal pen and family graves - the_cracked_lands.md section 8's "walled
-- compounds", walls facing the sun and the flood: the gate sits on the
-- north wall, away from both, and the south (flood-facing) wall is unbroken.
--
-- Designed for --rect 0,0,34,28 --faction OutlanderCivil --tech Industrial.

function build(ctx)
  local ex0, ez0, ew, eh = rect.x, rect.z, rect.w, rect.h
  ctx:wall_rect(ex0, ez0, ew, eh)
  local gate_x = ex0 + math.floor(ew / 2)
  ctx:door(gate_x, ez0) -- gate on the NORTH wall, away from sun+flood (south)

  -- ---- the house, center-north, furthest from the flood-facing wall ------
  local hx, hz = ex0 + math.floor(ew / 2) - 4, ez0 + 3
  local hw, hh = 8, 6
  ctx:room("Homestead", hx, hz, hw, hh, true)
  ctx:wall_rect(hx, hz, hw, hh)
  local hdoor_x = hx + math.floor(hw / 2)
  ctx:door(hdoor_x, hz + hh - 1)
  -- ElectricStove is 3x1 CENTRED on its origin (defsize.footprint) -
  -- everything below is spaced to clear that and every other footprint.
  ctx:place_role("STOVE", hx + 2, hz + 1)      -- spans hx+1..hx+3
  ctx:place_role("CHAIR", hx + 6, hz + 1)
  ctx:place_role("TABLE", hx + 5, hz + 1)      -- spans hz+1..hz+2
  ctx:place_role("END_TABLE", hx + 6, hz + 2)
  ctx:place_role("STORAGE", hx + 1, hz + 2)    -- spans hx+1..hx+2
  ctx:place_role("BED", hx + 2, hz + 3)        -- spans hz+3..hz+4
  ctx:place_role("BED", hx + 5, hz + 3)        -- spans hz+3..hz+4
  ctx:wall_attach("WALL_LIGHT", hx + 6, hz + 1, 1)
  ctx:place_role("GENERATOR", hx + 2, hz + hh + 3)   -- 4x4, spans hx+1..hx+4
  ctx:place_role("CONDUIT", hx + 5, hz + hh + 3)
  ctx:place_role("BATTERY", hx + 6, hz + hh + 3)     -- 1x2, spans z..z+1

  -- ---- the cistern room, east side ----------------------------------------
  local cx0, cz0 = ex0 + ew - 8, ez0 + math.floor(eh / 2) - 2
  ctx:room("Storeroom", cx0, cz0, 5, 5, true)
  ctx:wall_rect(cx0, cz0, 5, 5)
  ctx:door(cx0 + 2, cz0 + 4)
  ctx:place_role("WATER", cx0 + 2, cz0 + 2)
  ctx:place_role("SHELF_SMALL", cx0 + 1, cz0 + 1)
  if ctx:in_bounds(cx0 + 2, cz0 + 5) then
    ctx:place_role("SIGN", cx0 + 2, cz0 + 5)   -- just outside the door, not on the wall
  end

  -- droid marker (DROID_FACTION_LOADOUTS_1 concept only; no PawnKindDef -
  -- placed by defName since GONK has no OutlanderCivil palette entry) ------
  ctx:place("KOTOR_GonkBuilding", cx0 + 6, cz0 + 2)

  -- ---- the vaporator cluster, west (shade) side ---------------------------
  ctx:floor_rect(ex0 + 2, ez0 + 3, 3, eh - 8, "MossyTerrain")
  local placed = 0
  local vz = ez0 + 4
  while vz <= ez0 + eh - 6 do
    if ctx:in_bounds(ex0 + 3, vz) and not ctx:occupied(ex0 + 3, vz) then
      ctx:place("KotOR_MoistureVaporator_big", ex0 + 3, vz)
      placed = placed + 1
    end
    vz = vz + 3
  end

  -- ---- the pen, interior side of the flood-facing (south) wall -----------
  local px0, pz0, pw, ph = ex0 + 10, ez0 + eh - 7, 10, 5
  local pgate_x = px0 + math.floor(pw / 2)
  for x = px0, px0 + pw - 1 do
    if not ctx:occupied(x, pz0) then ctx:place_role("FENCE", x, pz0) end
    if x ~= pgate_x and not ctx:occupied(x, pz0 + ph - 1) then
      ctx:place_role("FENCE", x, pz0 + ph - 1)
    end
  end
  for z = pz0 + 1, pz0 + ph - 2 do
    if not ctx:occupied(px0, z) then ctx:place_role("FENCE", px0, z) end
    if not ctx:occupied(px0 + pw - 1, z) then ctx:place_role("FENCE", px0 + pw - 1, z) end
  end
  ctx:place_role("GATE", pgate_x, pz0 + ph - 1)
  ctx:place_role("TROUGH", px0 + 2, pz0 + 2)
  ctx:place_role("ANIMAL_BED", px0 + 4, pz0 + 2)

  -- ---- family graves, SW corner --------------------------------------------
  ctx:place_role("GRAVE", ex0 + 2, ez0 + eh - 3)
  ctx:place_role("GRAVE", ex0 + 3, ez0 + eh - 3)

  -- ---- shared campfire circle, south of the power apron --------------------
  local fx, fz = hx + math.floor(hw / 2), hz + hh + 7
  ctx:place("Campfire", fx, fz)
  ctx:place_role("BENCH", fx - 2, fz)
  ctx:place_role("BENCH", fx + 2, fz)

  note(string.format("walled compound: real wall ring gated north (away from "
    .. "sun+flood), house + cistern room + %d vaporator(s) on the shade "
    .. "strip, pen, 2 graves, GONK marker", placed))
end
