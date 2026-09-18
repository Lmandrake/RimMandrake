-- mirage_twin.lua - "The Mirage Twin" (structure_injection_roster.md WHISPER
-- #19, Sh'kaar). Anchor: `AB_MagmaVents` (Alpha Biomes, packageId
-- `sarg.alphabiomes`) - confirmed real by direct read of
-- `TileMutators_Natural.xml` inside the workshop copy of Alpha Biomes
-- (`.../workshop/content/294100/1841354677/1.6/Mods/Odyssey/Defs/
-- TileMutators/TileMutators_Natural.xml`, defName + full XML both read, not
-- guessed - RimSage's own index came back empty for every AB_-prefixed def
-- this pass tried, because the CURRENTLY LOADED mod list is the 30-mod
-- minimal regime (confirmed: live ModsConfig.xml has exactly 30 <li>
-- entries right now, Alpha Biomes not among them) - so this pass fell back
-- to reading the mod's own on-disk source directly, same discipline the
-- item's every prior batch used when the live/indexed set couldn't answer).
--
-- `AB_MagmaVents` `biomeWhitelist`s onto `AB_PyroclasticConflagration`,
-- which `sacred_sites_pass_1.md` SS1b names explicitly as one biome in
-- Sh'kaar's own volcanic-province cluster ("Volcano-LavaField-
-- AB_PyroclasticConflagration-Scarlands-AB_TarPits, all one cluster on the
-- Scald rim") - the SAME cluster batch 3's own note says it probed and
-- missed (it guessed the bare names `Volcano`/`LavaField`/`Scarlands`/
-- `AB_TarPits`/`AB_PyroclasticConflagration` AS TileMutatorDefs; reading the
-- real source this pass found `AB_TarPits` and `AB_PyroclasticConflagration`
-- are actually BiomeDefs referenced inside OTHER mutators' biomeWhitelists,
-- and the real anchoring TileMutatorDef sitting on that biome is
-- `AB_MagmaVents`/`AB_GeothermalHotspots` - neither guessed by name before).
-- `AB_MagmaVents` carries no `<extraGenSteps>` of its own (only a
-- VEF.Maps.TileMutatorExtension prefab-spawner modExtension), so the patch
-- Adds a whole new element to the TileMutatorDef node, same shape as
-- Cavern/DryLake/Hollow/Caves/Dunes.
--
-- v1 scope, declared: the roster's own line is "a structure visible at map
-- edge that resolves to nothing up close (scam-prop tech from the trap
-- spec)". RimWorld's engine has no distance-based LOD or proximity-despawn
-- mechanism (checked: no such Verse system exists for a placed Thing to
-- change appearance/disappear as a colonist approaches it - fog-of-war
-- toggles visibility by sight range, not physical distance from a fixed
-- viewpoint), so the "resolves to nothing up close" half of this whisper is
-- narrative framing for the landing letter (not authored by this pass; see
-- the item file) rather than a buildable mechanic. This pass places the
-- STATIC illusion-prop half only - one marker sitting at the footprint's
-- edge, the same substitute-prop discipline every prior whisper batch used
-- (no "mirage"/"scam-prop" ThingDef exists in the stack; `trap_renaissance_
-- spec.md`'s own "VFEPD fake pit/gibbet props" reference names a DIFFERENT,
-- not-yet-built defense-prop track under a different item, not a defName
-- this pass can borrow).
--
-- Real defName (Core, already the shipped precedent across this whole
-- program): SculptureSmall.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function min_rect(params)
  return 4, 4   -- needs a real edge to sit a lone marker on
end

function build(ctx)
  if rect.w < 4 or rect.h < 4 then
    ctx:refuse("footprint", string.format(
      "%dx%d too small to place an edge-sited illusion marker (needs >=4x4)", rect.w, rect.h))
    return
  end

  -- One apparition, not a ring — the roster's own line is singular ("a
  -- structure"), unlike Sarlacc Sign's x3-5 burrow-sign ring for the same
  -- footprint-edge idiom. Pick one of the four edges, then walk it looking
  -- for the first free cell.
  local edges = {"N", "S", "E", "W"}
  local side = edges[rng.int(1, 4)]
  local placed = false

  local function try_place(xx, zz)
    if not placed and not ctx:occupied(xx, zz) then
      ctx:place("SculptureSmall", xx, zz)
      placed = true
    end
  end

  if side == "N" then
    for xx = rect.x, rect.x2 do
      try_place(xx, rect.z)
      if placed then break end
    end
  elseif side == "S" then
    for xx = rect.x, rect.x2 do
      try_place(xx, rect.z2)
      if placed then break end
    end
  elseif side == "E" then
    for zz = rect.z, rect.z2 do
      try_place(rect.x2, zz)
      if placed then break end
    end
  else -- "W"
    for zz = rect.z, rect.z2 do
      try_place(rect.x, zz)
      if placed then break end
    end
  end

  -- If the chosen edge was fully occupied, fall back to any free edge cell
  -- before refusing outright.
  if not placed then
    for zz = rect.z, rect.z2 do
      for xx = rect.x, rect.x2 do
        local on_edge = xx == rect.x or xx == rect.x2 or zz == rect.z or zz == rect.z2
        if on_edge then
          try_place(xx, zz)
          if placed then break end
        end
      end
      if placed then break end
    end
  end

  if not placed then
    ctx:refuse("marker", "no free edge cell for the mirage's own marker")
    return
  end

  note(string.format(
    "mirage twin: one illusion marker sited on the %s edge of the footprint - " ..
    "static only, no distance-based disappear mechanic this pass (engine has none)",
    side))
end
