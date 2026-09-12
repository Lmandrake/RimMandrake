-- rootstock.lua - "The Rootstock" (structure_injection_roster.md WHISPER
-- #20, dry lakes; roster's own §3 line tags it Oomo, sacred_sites_pass_1.md
-- §1b's own biome-class table assigns DryLake reads to Zizzik instead - a
-- real conflict between the two design docs, not resolved here, declared
-- rather than silently picking one). Anchor: the vanilla/Odyssey `DryLake`
-- TileMutatorDef (RimSage-confirmed, no MayRequire beyond Odyssey itself -
-- see TileMutatorDefs_Whisper_Batch1.xml). "the desert holds its breath,
-- not its death" - a dormant seedbank, static content only.
--
-- v1 scope, declared: this places the seedbank as STATIC terrain dressing
-- (a cluster of dead-looking scrub + loose seed-pod litter). The roster's
-- own mechanic - "blooms after any rain/water event" - is a triggered
-- comp/event this pass does not build, same discipline the promise
-- batches used for Dead Beacon's unwired lamp and the Cistern's flavor-
-- only stair: the STRUCTURAL content ships, the active behavior is a
-- named, undone gap, not invented.
--
-- Real defNames confirmed via RimSage (vanilla Core, both indexed in the
-- offline dump - no live-probe needed, unlike the modded rows other
-- batches used):
--   DryLakeBed (TerrainDef) - the cracked lakebed floor.
--   Plant_ShrubLow ("low shrubs", ThingDef) - dead-looking dry scrub,
--     exactly the "seedbank waiting" read. No dedicated "seed pod"/
--     "dormant seedbank" ThingDef exists in the stack, so scrub density
--     alone carries the read - a substitution, not an invention, same
--     discipline hunting_lodge.lua's trophy substitution used.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  if rect.w < 5 or rect.h < 5 then
    ctx:refuse("FOOTPRINT", string.format(
      "%dx%d too small for a rootstock patch (needs >=5x5)", rect.w, rect.h))
    return
  end

  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)
  local r = math.min(math.floor(rect.w / 2), math.floor(rect.h / 2)) - 1

  -- ---- cracked lakebed floor under the whole patch ----------------------
  local floored = 0
  for zz = rect.z, rect.z2 do
    for xx = rect.x, rect.x2 do
      local dist = math.max(math.abs(xx - cx), math.abs(zz - cz))
      if dist <= r then
        ctx:floor(xx, zz, "DryLakeBed")
        floored = floored + 1
      end
    end
  end

  -- ---- dormant scrub, dense at center, thinning outward -----------------
  local shrubs = 0
  for zz = rect.z, rect.z2 do
    for xx = rect.x, rect.x2 do
      if not ctx:occupied(xx, zz) then
        local dist = math.max(math.abs(xx - cx), math.abs(zz - cz))
        if dist <= r and rng.chance(0.35) then
          ctx:place("Plant_ShrubLow", xx, zz)
          shrubs = shrubs + 1
        end
      end
    end
  end

  note(string.format(
    "rootstock: %d cracked-lakebed cells, %d dry-scrub seedbank markers - " ..
    "static only, no rain-triggered bloom this pass",
    floored, shrubs))
end
