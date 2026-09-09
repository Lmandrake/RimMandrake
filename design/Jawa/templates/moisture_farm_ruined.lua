-- moisture_farm_ruined.lua - "The Ruined Farm" (MOISTURE_FARM_TEMPLATES_1,
-- RimUtinni tier, ZBiome_Badlands): the_cracked_lands.md section 8/11's
-- flood-marked ruin - "the farm that was built one meter too low." Builds a
-- small homestead + vaporator cluster like moisture_homestead.lua, then runs
-- ctx:ruin() to breach the walls, drop the roof near the breach, ash the
-- floor and roll the furniture - the family did not get out. This template
-- stands in for the family's abandoned/raided/flooded states collectively:
-- ctx:ruin's structural-damage pass is the cheap route the flat-plan format
-- actually supports; a full working/abandoned/flooded/raided state MATRIX
-- was not built (see the queue item's report for why).
--
-- Designed for --rect 0,0,18,15 --faction OutlanderCivil --tech Industrial.

function build(ctx)
  local hx, hz = rect.x + 2, rect.z + 2
  local hw, hh = 8, 6

  ctx:room("Homestead", hx, hz, hw, hh, true)
  ctx:wall_rect(hx, hz, hw, hh)
  local door_x = hx + math.floor(hw / 2)
  ctx:door(door_x, hz + hh - 1)

  -- ElectricStove is 3x1 CENTRED on its origin (defsize.footprint) -
  -- everything below is spaced to clear that and every other footprint.
  ctx:place_role("STOVE", hx + 2, hz + 1)      -- spans hx+1..hx+3
  ctx:place_role("CHAIR", hx + 4, hz + 1)
  ctx:place_role("TABLE", hx + 5, hz + 1)      -- spans hz+1..hz+2
  ctx:place_role("BED", hx + 2, hz + 3)        -- spans hz+3..hz+4
  ctx:place_role("BED", hx + 5, hz + 3)        -- spans hz+3..hz+4
  ctx:place_role("STORAGE", hx + 1, hz + 2)    -- spans hx+1..hx+2
  ctx:place_role("END_TABLE", hx + 4, hz + 2)

  -- vaporator cluster, shade (west) side
  local vap_x = rect.x
  local placed = 0
  for _, vz in ipairs({ hz, hz + 3 }) do
    if ctx:in_bounds(vap_x, vz) and not ctx:occupied(vap_x, vz) then
      ctx:place("KotOR_MoistureVaporator_big", vap_x, vz)
      placed = placed + 1
    end
  end
  ctx:floor_rect(vap_x, hz, 1, 5, "MossyTerrain")

  -- the family did not get out
  ctx:place_role("GRAVE", door_x - 1, hz + hh)
  ctx:place_role("GRAVE", door_x + 1, hz + hh)

  -- ---- the flood pass: breach, attrition, roof-drop, ash, furniture rolls -
  local removed = ctx:ruin(0.55)

  -- high-water line: flood-stain filth reaching past the structure's own
  -- footprint into the yard - what marks a ruin as FLOOD damage rather than
  -- a raid (the raiders leave no silt).
  for x = rect.x, rect.x2 do
    if ctx:in_bounds(x, hz + hh + 1) and not ctx:occupied(x, hz + hh + 1)
        and rng.chance(0.5) then
      ctx:place_overlay("Filth_Dirt", x, hz + hh + 1)
    end
  end

  note(string.format("ruined farm: %d wall cell(s) breached/attrited by "
    .. "ctx:ruin, %d/2 vaporators (one likely rolled to scrap), 2 graves - "
    .. "the flood-marked ruin, built one bench too low", removed, placed))
end
