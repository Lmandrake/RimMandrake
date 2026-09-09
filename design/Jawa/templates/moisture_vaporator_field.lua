-- moisture_vaporator_field.lua - "The Vaporator Field" (MOISTURE_FARM_TEMPLATES_1,
-- RimUtinni tier, ZBiome_Badlands): an open field of moisture vaporators
-- terraced into the shade-soil bench (the_cracked_lands.md section 11 -
-- "fields terraced into the shade line"), watched from one small roofed
-- lean-to, ringed by a low sandbag line gated on the flood-approach edge. No
-- family home here - a satellite field a homestead or compound tends.
-- Placement gate (higher bench, never the canyon floor) belongs to the
-- TileMutatorDef/world-tile pass, out of this template's reach.
--
-- Designed for --rect 0,0,24,20 --faction OutlanderCivil --tech Industrial.

function build(ctx)
  -- ---- the watch lean-to, NW corner ---------------------------------------
  local hx, hz = rect.x, rect.z
  local hw, hh = 4, 4
  ctx:room("Storeroom", hx, hz, hw, hh, true)
  ctx:wall_rect(hx, hz, hw, hh)
  ctx:door(hx + 1, hz + hh - 1)
  -- 2x2 interior: the door opens onto (hx+1,hz+2) only, so that ONE cell
  -- stays empty and everything else sits where a single lateral step reaches
  -- it - a 2-wide Shelf on the entry row would otherwise seal the room shut.
  ctx:place_role("STORAGE", hx + 1, hz + 1)   -- spans hx+1..hx+2, top row
  ctx:place_role("BENCH", hx + 2, hz + 2)
  ctx:wall_attach("WALL_LIGHT", hx + 2, hz + 1, 1)
  -- droid marker (DROID_FACTION_LOADOUTS_1 concept only; no PawnKindDef -
  -- placed by defName since GONK has no OutlanderCivil palette entry) ------
  ctx:place("KOTOR_GonkBuilding", hx + hw + 1, hz)

  -- ---- the shade-soil strip the field is terraced into --------------------
  local field_x0 = hx + hw + 3
  local field_x1 = rect.x2 - 2
  local field_z0 = rect.z + 2
  local field_z1 = rect.z2 - 2
  ctx:floor_rect(field_x0, field_z0, field_x1 - field_x0 + 1, field_z1 - field_z0 + 1,
    "MossyTerrain")

  -- ---- the vaporator rows: 3-cell stride both axes, matching
  -- KotOR_MoistureVaporator_big's own minDistanceToSameTypeOfBuilding=3 so
  -- the rows read as a working field, not a jammed pile.
  local placed = 0
  local row_z = field_z0 + 1
  while row_z <= field_z1 - 1 do
    local col_x = field_x0 + 1
    while col_x <= field_x1 - 1 do
      if ctx:in_bounds(col_x, row_z) and not ctx:occupied(col_x, row_z) then
        ctx:place("KotOR_MoistureVaporator_big", col_x, row_z)
        placed = placed + 1
      end
      col_x = col_x + 3
    end
    row_z = row_z + 3
  end

  -- ---- sandbag ring, gated on the south (flood-approach) edge -------------
  local gate_x = rect.x + math.floor(rect.w / 2)
  for x = rect.x, rect.x2 do
    if not ctx:occupied(x, rect.z) then ctx:place_role("SANDBAG", x, rect.z) end
    if x ~= gate_x and not ctx:occupied(x, rect.z2) then
      ctx:place_role("SANDBAG", x, rect.z2)
    end
  end
  for z = rect.z + 1, rect.z2 - 1 do
    if not ctx:occupied(rect.x, z) then ctx:place_role("SANDBAG", rect.x, z) end
    if not ctx:occupied(rect.x2, z) then ctx:place_role("SANDBAG", rect.x2, z) end
  end

  note(string.format("vaporator field: %d vaporator(s) on the shade-soil "
    .. "strip, watch lean-to NW, GONK marker, sandbag ring gated south", placed))
end
