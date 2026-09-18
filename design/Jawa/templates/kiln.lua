-- kiln.lua - canvas floor: see min_rect() below (`rimplace minrect kiln`).
-- "The Kiln" (structure_injection_roster.md PROMISE #11, RimUtinni tier,
-- Zizzik primary / Mob'Unloo secondary). RULED 2026-09-18 (owner, commit
-- 70d98e9fa): it is sacred_sites_pass_1.md's own blast crater - five
-- Wasteland tiles inside 878 tiles of otherwise ordinary sand, where a
-- Hutt cargo manifest "cleared by the people whose job was to clear it"
-- detonated an entire settlement - NOT the roster's earlier "Ohm vs
-- Sh'kaar geothermal works, free power" framing, which was wrong and is
-- dropped. "NEW: scorched dead ground, no power output ... hazard/
-- atmosphere only" (roster row 11's own corrected text) - so this is
-- deliberately propless-of-function: no walls, no room, nothing a pawn
-- operates. Terrain-led, same discipline glass_sea.lua/broken_ring.lua
-- already used for a "the site IS the ground" read.
--
-- Real defNames verified against the live, active 636-mod set (this
-- session has RimSage; Wasteland itself is NOT in RimSage's own index,
-- so it was confirmed the harder way - a validate_patch.py
-- PatchOperationConditional probe against --defs Data+Mods+Workshop,
-- same authority every prior batch fell back on when RimSage/defs.sqlite
-- couldn't answer):
--   Wasteland (BiomeDef) - confirmed 1 real hit, "Advanced Biomes
--     (Continued)" (packageId Mlie.AdvancedBiomes),
--     Defs/BiomeDefs/Biomes_Wasteland.xml: "A highly radioactive desert.
--     Nuclear contamination from weapons testing, war or meltdowns has
--     permanently altered the landscape." - matches sacred_sites_pass_1.md
--     §1b's own "contamination class... the weapon was used and left"
--     read for Zizzik almost verbatim. This mutator's own biomeWhitelist,
--     same shape as RSW_DeadCrawler's Desert/ExtremeDesert whitelist -
--     a wholly NEW TileMutatorDef, no adoption of anyone else's def
--     (the promise pattern every non-adopted row already uses).
--   CraterLarge (Core, ParentName="CraterBase", size (5,5), isInert=true,
--     claimable=false, Beauty -20, "A small pit formed by a powerful
--     impact or explosion" - the literal blast crater centerpiece, read
--     straight off its own vanilla flavor text) - RimSage get_def_details
--     confirmed.
--   ChunkSlagSteel / Filth_RubbleBuilding / Filth_Ash (Core) - the blast
--     debris vocabulary every prior "something detonated here" row
--     (podracer_wreck.lua, broken_ring.lua) already established, plus
--     Filth_Ash for the one new "still visibly scorched" beat this row's
--     own text asks for that no prior row needed.
--   Gravel (Core, "stony soil") - the dead-flat ground itself: barren,
--   no-growth terrain, distinct from ordinary sand/dirt so the crater
--   reads as its own five-tile anomaly, matching the roster's "5 dead-
--   flat tiles inside 878 tiles of otherwise ordinary sand" almost
--   literally.
--
-- No power mechanism (the owner's own ruling text) and no walls/room -
-- "hazard/atmosphere only" is deliberately NOT built as a mechanic here
-- (no toxic-fallout hediff, no radiation zone - RimWorld/this stack has
-- no such system to hook without inventing one); it is narrative/letter-
-- text framing only, same discipline mirage_twin.lua's "resolves to
-- nothing up close" half and rootstock.lua's rain-trigger already used
-- for an unbuildable half of a roster line.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

-- The declared canvas floor; the engine checks it before build() runs
-- (TEMPLATE_CANVAS_UNDECLARED_1). `rimplace minrect kiln`.
function min_rect(params)
  return 6, 6   -- CraterLarge's own 5x5 bounds plus one cell of margin so
                -- the crater never clamps flush against the footprint edge
end

function build(ctx)
  if rect.w < 6 or rect.h < 6 then
    ctx:refuse("footprint", string.format(
      "%dx%d cannot hold the 5x5 CraterLarge centerpiece with any margin", rect.w, rect.h))
    return
  end

  -- ---- the dead-flat ground: barren stony soil across the whole
  -- footprint, no crops, no ordinary sand read ----------------------------
  local ground = ctx:floor_rect(rect.x, rect.z, rect.w, rect.h, "Gravel")

  -- ---- the crater itself, centered (clamped so its 5x5 bounds never run
  -- outside the footprint, same clamp discipline monument.lua's own
  -- code-review fix established) -------------------------------------------
  local cx = rect.x + math.floor(rect.w / 2) - 2
  local cz = rect.z + math.floor(rect.h / 2) - 2
  if cx < rect.x then cx = rect.x end
  if cz < rect.z then cz = rect.z end
  if cx + 4 > rect.x2 then cx = rect.x2 - 4 end
  if cz + 4 > rect.z2 then cz = rect.z2 - 4 end
  ctx:place("CraterLarge", cx, cz)

  -- ---- blast debris and ash scattered densest near the crater, thinning
  -- toward the footprint's own edge - "the weapon was used and left" made
  -- physical, not a tidy ring --------------------------------------------
  local rubble, ash, slag = 0, 0, 0
  for x = rect.x, rect.x2 do
    for z = rect.z, rect.z2 do
      if ctx:can_place("ChunkSlagSteel", x, z) then
        local d = math.sqrt((x - (cx + 2)) ^ 2 + (z - (cz + 2)) ^ 2)
        local near = d <= math.max(rect.w, rect.h) * 0.4
        local chance = near and 0.14 or 0.04
        if rng.chance(chance) then
          if rng.chance(0.5) then
            ctx:place("Filth_Ash", x, z)
            ash = ash + 1
          elseif rng.chance(0.5) then
            ctx:place("Filth_RubbleBuilding", x, z)
            rubble = rubble + 1
          else
            ctx:place("ChunkSlagSteel", x, z)
            slag = slag + 1
          end
        end
      end
    end
  end

  if rubble == 0 and ash == 0 and slag == 0 then
    local fx, fz = cx + 4, cz + 4
    if fx > rect.x2 then fx = rect.x2 end
    if fz > rect.z2 then fz = rect.z2 end
    if ctx:can_place("ChunkSlagSteel", fx, fz) then
      ctx:place("ChunkSlagSteel", fx, fz)
      slag = slag + 1
    end
  end

  note(string.format(
    "the kiln: %d cells dead-flat gravel, 1 blast crater (5x5, centered), %d ash filth, %d rubble filth, %d slag chunks - no power, no walls, hazard/atmosphere only",
    ground, ash, rubble, slag))
end
