-- moisture_homestead.lua - "The Moisture Homestead" (MOISTURE_FARM_TEMPLATES_1,
-- RimUtinni tier, ZBiome_Badlands): a Homestead Defense League family house on
-- a canyon bench. One hearth room split off a small bedroom, a lean-to store,
-- three vaporators clustered on the shade side (never the open-sun side), a
-- family grave by the door, a GONK power-droid prop marking a utility spot
-- (DROID_FACTION_LOADOUTS_1 concept - no PawnKindDef spawned), solar+battery
-- feeding the house, and a sandbag yard line on the sun/flood-facing edges.
-- the_cracked_lands.md section 8/11: build on the higher bench, never the
-- canyon floor - that placement gate belongs to the TileMutatorDef/world-tile
-- pass, out of this template's reach.
--
-- Designed for --rect 0,0,20,16 --faction OutlanderCivil --tech Industrial.

function build(ctx)
  local hx, hz = rect.x + 2, rect.z + 2
  local hw, hh = 9, 7

  ctx:room("Homestead", hx, hz, hw, hh, true)
  ctx:wall_rect(hx, hz, hw, hh)

  -- south door onto the yard
  local door_x = hx + math.floor(hw / 2)
  ctx:door(door_x, hz + hh - 1)

  -- partition: bedroom north, hearth/dining south. The partition door sits
  -- on the SAME column as the main south door, so column hx+4 is a clear
  -- aisle from the yard straight through to the bedroom - every other
  -- placement below is kept off that column on purpose.
  local part_z = hz + 3
  for x = hx + 1, hx + hw - 2 do
    ctx:place_role("WALL", x, part_z)
  end
  local bed_door_x = door_x
  ctx:door(bed_door_x, part_z)

  -- window on the shade (west) wall of the hearth room
  ctx:window(hx, hz + 4)

  -- hearth room furniture (south of the partition). ElectricStove is 3x1
  -- CENTRED on its origin (defsize.footprint), Table1x2c/Shelf/Bed are
  -- 1x2/2x1 growing +x/+z - spaced to clear every footprint AND leave
  -- column hx+4 (the door aisle) empty at every row.
  ctx:place_role("STOVE", hx + 2, hz + 4)     -- spans hx+1..hx+3
  ctx:place_role("CHAIR", hx + 3, hz + 5)
  ctx:place_role("TABLE", hx + 5, hz + 4)     -- spans hz+4..hz+5
  ctx:place_role("CHAIR", hx + 6, hz + 4)
  ctx:place_role("STORAGE", hx + 1, hz + 5)   -- spans hx+1..hx+2
  ctx:wall_attach("WALL_LIGHT", hx + 7, hz + 4, 1)

  -- bedroom (north of the partition). Both beds are 1 column wide and span
  -- 2 rows - each seals off its OWN edge column as a dead pocket (no south
  -- exit past the partition wall), so clutter stays off hx+1/hx+7 and off
  -- the hx+4 aisle, landing only on the columns the flood-fill can reach.
  ctx:place_role("BED", hx + 2, hz + 1)       -- spans hz+1..hz+2
  ctx:place_role("BED", hx + 6, hz + 1)       -- spans hz+1..hz+2
  ctx:place_role("END_TABLE", hx + 3, hz + 2)
  ctx:place_role("CHEST", hx + 5, hz + 2)

  -- store lean-to on the east wall: a roofed porch shelf, matching the
  -- family homestead's own lean-to convention (homestead.txt)
  local lean_x = hx + hw
  for x = lean_x, lean_x + 2 do
    for z = hz + 2, hz + 5 do
      ctx:roof(x, z)
    end
  end
  ctx:place_role("SHELF_SMALL", lean_x, hz + 2)
  ctx:place_role("CRATE", lean_x + 1, hz + 2)
  ctx:place_role("BARREL", lean_x, hz + 4)

  -- power apron: solar (4x4!) + battery feeding the house only - the
  -- vaporators are their own unwired promise, same convention as the
  -- reference moisture_farm.lua/.txt (RimStarWars tier), which does not
  -- wire its vaporators either.
  ctx:place_role("GENERATOR", hx + 1, hz + hh + 2)
  ctx:place_role("CONDUIT", hx + 5, hz + hh + 2)
  ctx:place_role("BATTERY", hx + 6, hz + hh + 2)

  -- ---- the vaporator cluster, shade side (west of the house) -------------
  local vap_x = rect.x
  local vap_positions = { { vap_x, hz }, { vap_x, hz + 3 }, { vap_x, hz + 6 } }
  local placed = 0
  for _, p in ipairs(vap_positions) do
    if ctx:in_bounds(p[1], p[2]) and not ctx:occupied(p[1], p[2]) then
      ctx:place("KotOR_MoistureVaporator_big", p[1], p[2])
      placed = placed + 1
    end
  end

  -- shade-soil patch under the vaporators - the_cracked_lands.md's "soil in
  -- the shade", the only real farmland on the dryland ladder.
  ctx:floor_rect(vap_x, hz, 1, 8, "MossyTerrain")

  -- ---- the family grave, by the door --------------------------------------
  ctx:place_role("GRAVE", door_x + 1, hz + hh)

  -- ---- the droid marker (DROID_FACTION_LOADOUTS_1 concept only; a static
  -- GONK power-droid prop, no PawnKindDef spawned - placed by defName since
  -- GONK has no OutlanderCivil palette entry, only the Jawa faction blocks) -
  ctx:place("KOTOR_GonkBuilding", hx + hw + 1, hz + hh)

  -- ---- yard perimeter: sandbags, on the south+east (sun/flood) edges -----
  for x = rect.x, rect.x2 do
    if not ctx:occupied(x, rect.z2) then ctx:place_role("SANDBAG", x, rect.z2) end
  end
  for z = rect.z, rect.z2 do
    if not ctx:occupied(rect.x2, z) then ctx:place_role("SANDBAG", rect.x2, z) end
  end
  if ctx:occupied(door_x, rect.z2) then
    note("south sandbag line breaks at the door line - the family's own path out")
  end

  note(string.format("moisture homestead: %d/3 vaporators on the shade patch, "
    .. "hearth+bedroom house, grave by the door, GONK marker at the yard corner",
    placed))
end
