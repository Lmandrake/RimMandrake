-- broken_ring.lua - "The Broken Ring" (structure_injection_roster.md
-- PROMISE #20, RimUtinni tier, Zizzik): a segment of some orbital
-- structure, fallen and half-fused into the ground, still carrying rich
-- tech scrap. "everything salvaged from it carries his spark for a season."
-- Terrain-led rather than a building, same discipline glass_sea.lua used
-- for its own "the site IS the ground" read - the ring segment is the
-- ground itself, not a prop standing on ordinary dirt.
--
-- Real defNames verified against vanilla source (RimSage-indexed):
--   AncientMegastructure (Odyssey, Defs/Odyssey/TerrainDefs/Terrain_
--     Natural.xml, ParentName="NaturalTerrainBase", Beauty -3, scatterType
--     Rocky) - the ring segment's own hull surface, fused into the ground;
--     read directly off its own vanilla flavor rather than invented.
--   Steel / ComponentIndustrial / ChunkSlagSteel (Core) - the "rich tech
--     scrap" itself; ComponentIndustrial is the upgrade from podracer_
--     wreck.lua's plain Steel-and-slag vocabulary, matching this row's own
--     "rich" line (a crashed HABITAT ring, not a joyriding pod).
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)
  local max_r = math.max(1, math.min(math.floor(rect.w / 2), math.floor(rect.h / 2)))

  -- ---- the hull segment: an off-center arc of fused ground, not a tidy
  -- circle (a crash embeds unevenly) --------------------------------------
  local hull = 0
  local hcx, hcz = cx - math.floor(max_r * 0.15), cz + math.floor(max_r * 0.1)
  for x = rect.x, rect.x2 do
    for z = rect.z, rect.z2 do
      local d = math.sqrt((x - hcx) ^ 2 + (z - hcz) ^ 2)
      if d <= max_r * 0.75 then
        ctx:floor(x, z, "AncientMegastructure")
        hull = hull + 1
      end
    end
  end

  -- ---- rich tech scrap scattered densest over the hull, thinning off it -
  local steel, components, chunks = 0, 0, 0
  for x = rect.x, rect.x2 do
    for z = rect.z, rect.z2 do
      if not ctx:occupied(x, z) then
        local d = math.sqrt((x - hcx) ^ 2 + (z - hcz) ^ 2)
        local on_hull = d <= max_r * 0.75
        local chance = on_hull and 0.16 or 0.05
        if rng.chance(chance) then
          local roll_a = rng.chance(0.5)
          if on_hull and rng.chance(0.3) then
            ctx:place("ComponentIndustrial", x, z)
            components = components + 1
          elseif roll_a then
            ctx:place("Steel", x, z)
            steel = steel + 1
          else
            ctx:place("ChunkSlagSteel", x, z)
            chunks = chunks + 1
          end
        end
      end
    end
  end

  if steel == 0 and components == 0 and chunks == 0 then
    ctx:place("ComponentIndustrial", cx, cz)
    components = 1
  end

  note(string.format(
    "broken ring: %d cells of fused hull terrain, %d steel stacks, %d component salvage, %d slag chunks",
    hull, steel, components, chunks))
end
