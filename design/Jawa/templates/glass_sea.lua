-- glass_sea.lua - "The Glass Sea" (structure_injection_roster.md PROMISE #16,
-- RimUtinni tier, Sh'kaar): a stretch of fused sand, mirror-flat and blinding.
-- "solar output soars; so does exposure" - a pure terrain read, no props, no
-- walls/rooms - the simplest promise in this batch by design (the roster's
-- own "NEW terrain" framing, distinct from every other row this batch and
-- prior batches, which are all prop/building sites).
--
-- Real defNames verified against vanilla Odyssey source (RimSage-indexed,
-- not guessed): VolcanicRock_Smooth (Defs/Odyssey/TerrainDefs/Terrain_
-- Natural.xml, ParentName="NaturalTerrainBase", texturePath "Terrain/
-- Surfaces/SmoothVolcanicRock", Beauty +2, Walkable) - fused, glassy, flat:
-- exactly "mirror-flat icon" and "brutal glare" read straight off its own
-- vanilla flavor. VolcanicRock (same file, its own rough precursor,
-- texturePath "Terrain/Surfaces/VolcanicRock") edges the smooth core so the
-- site fades into ordinary desert rather than snapping to a hard rectangle.
-- Both require Odyssey (this TileMutatorDef's own MayRequire), same gate
-- every prior batch's Odyssey-sourced row already carries.
--
-- A pure-terrain plan places zero Things, which the engine's own lint (rule
-- 9, "a plan that builds nothing is a bug") correctly cannot distinguish
-- from an author forgetting to build anything — so this scatters a couple
-- ChunkSlagSteel pieces (same "junk debris" vocabulary as podracer_wreck.lua/
-- mynock_roost.lua), read as scorched wreckage fused INTO the glass by
-- whatever event vitrified this stretch of desert. Still overwhelmingly a
-- terrain site, not a scatter site - the chunks are flavor, not the point.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local smooth, rough, chunks = 0, 0, 0

  -- core: smooth fused glass across most of the footprint
  -- edge: one ring of rough volcanic rock so the transition into ordinary
  -- ground reads as a real glare-field, not a stamped-out rectangle
  for x = rect.x, rect.x2 do
    for z = rect.z, rect.z2 do
      local on_edge = x == rect.x or x == rect.x2 or z == rect.z or z == rect.z2
      if on_edge and rng.chance(0.6) then
        ctx:floor(x, z, "VolcanicRock")
        rough = rough + 1
      else
        ctx:floor(x, z, "VolcanicRock_Smooth")
        smooth = smooth + 1
      end
    end
  end

  -- a sparse handful of scorched chunks caught in the glass - just enough
  -- that the plan is not literally propless (see the note above)
  for x = rect.x, rect.x2 do
    for z = rect.z, rect.z2 do
      if not ctx:occupied(x, z) and rng.chance(0.03) then
        ctx:place("ChunkSlagSteel", x, z)
        chunks = chunks + 1
      end
    end
  end
  if chunks == 0 then
    local cx = rect.x + math.floor(rect.w / 2)
    local cz = rect.z + math.floor(rect.h / 2)
    ctx:place("ChunkSlagSteel", cx, cz)
    chunks = 1
  end

  note(string.format(
    "glass sea: %d cells fused smooth (glare core), %d rough volcanic-rock edge cells, %d scorched chunks caught in the glass",
    smooth, rough, chunks))
end
