-- moisture_cistern_head.lua - "The Cistern Head" (MOISTURE_FARM_TEMPLATES_1,
-- RimUtinni tier, ZBiome_Badlands): the found-and-held flood water
-- (the_cracked_lands.md section 7 - "the planet's most defensible water").
-- One small, thick-walled stone room over the well, a sign at the door, and
-- shelving for the crack-wax the Farmers line a cistern with. Deliberately
-- the smallest, most defended footprint of the family - no vaporators here,
-- this is the WELL, not the field.
--
-- Designed for --rect 0,0,11,11 --faction OutlanderCivil --tech Industrial.

function build(ctx)
  local hx, hz = rect.x + 1, rect.z + 1
  local hw, hh = 7, 7

  ctx:room("Storeroom", hx, hz, hw, hh, true)
  ctx:wall_rect(hx, hz, hw, hh)

  local door_x = hx + math.floor(hw / 2)
  ctx:door(door_x, hz + hh - 1)
  ctx:place_role("SIGN", door_x, hz + hh)

  -- the well, dead center
  local cx = hx + math.floor(hw / 2)
  local cz = hz + math.floor(hh / 2)
  ctx:place_role("WATER", cx, cz)

  -- crack-wax / tool storage flanking the well
  ctx:place_role("SHELF_SMALL", hx + 1, hz + 1)
  ctx:place_role("CRATE", hx + hw - 2, hz + 1)
  ctx:place_role("BARREL", hx + 1, hz + hh - 2)
  ctx:wall_attach("WALL_LIGHT", hx + 1, hz + 1, 3)
  ctx:wall_attach("WALL_LIGHT", hx + hw - 2, hz + 1, 1)

  -- a stool by the door - the Farmer who watches the water
  ctx:place_role("STOOL", door_x - 1, hz + hh - 2)

  -- sandbag apron just outside the door, facing the flood approach (south)
  for x = hx - 1, hx + hw do
    if x ~= door_x and ctx:in_bounds(x, hz + hh + 1) and not ctx:occupied(x, hz + hh + 1) then
      ctx:place_role("SANDBAG", x, hz + hh + 1)
    end
  end

  note("cistern head: well sealed inside a thick single stone room, sign at "
    .. "the door, sandbag apron on the flood-facing side")
end
