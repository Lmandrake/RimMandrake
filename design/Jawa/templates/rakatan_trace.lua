-- rakatan_trace.lua - "The Rakatan Trace" (structure_injection_roster.md
-- PROMISE #9, RimUtinni tier, vault-adjacent tiles / dungeons arc, voice:
-- Narrator): a sealed door and forecourt only - the vault teaser. "nothing
-- opens yet; everything is implied" - deliberately NOT a room, NOT an
-- interior, NOT a functioning entrance. A wall stub with one door that
-- backs onto nothing, angular glyphs flanking, a paved forecourt in front.
-- This is set dressing for `VAULT_DUNGEON_BUILD_1`'s eventual real vaults,
-- not a vault itself.
--
-- Real defNames verified against the live 591-mod stack via a
-- validate_patch.py PatchOperationConditional probe against the actual
-- on-disk Data/Mods/Workshop XML (this session's defs.sqlite capture is
-- scoped to ResearchProjectDef only, so `rimplace verify` cannot currently
-- confirm ThingDefs - same gap noted in oasis_shrine.lua, same worked
-- around the same way):
--   Wall / Door (Core, Buildings_Structure.xml) - the sealed face.
--   SculptureSmall (Core, Buildings_Art.xml) - reused as the "angular-glyph"
--     marker; no dedicated glyph/relief ThingDef exists in the stack.
--   PavedTile (Core, Terrain_Floors.xml) - the forecourt.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  -- The wall runs along one full edge of the footprint (rect.z, the row the
  -- renderer draws last in this build's convention - not asserting a
  -- specific compass direction, that's unmeasured); the forecourt is
  -- everything on the other side of it. A door centered in the wall,
  -- backing onto nothing (no room is ever declared past the wall line) -
  -- the refusal-to-open is structural, not just narrative.
  local wall_z = rect.z
  local door_x = rect.x + math.floor(rect.w / 2)

  if rect.w < 5 then
    ctx:refuse("SEALED_FACE", string.format(
      "%dx%d footprint too narrow for a legible sealed face + flanking glyphs", rect.w, rect.h))
    return
  end

  -- ---- the sealed face --------------------------------------------------
  for x = rect.x, rect.x2 do
    if x == door_x then
      ctx:door(x, wall_z)
    elseif not ctx:occupied(x, wall_z) then
      ctx:place("Wall", x, wall_z)
    end
  end

  -- ---- angular glyphs flanking the door, one step off it -----------------
  local gx1, gx2 = door_x - 2, door_x + 2
  local glyph_z = wall_z + 1
  local glyphs = 0
  if gx1 >= rect.x and not ctx:occupied(gx1, glyph_z) then
    ctx:place("SculptureSmall", gx1, glyph_z)
    glyphs = glyphs + 1
  end
  if gx2 <= rect.x2 and not ctx:occupied(gx2, glyph_z) then
    ctx:place("SculptureSmall", gx2, glyph_z)
    glyphs = glyphs + 1
  end

  -- ---- the forecourt: paved, everything south of the wall to the edge ----
  local paved = 0
  for z = wall_z + 1, rect.z2 do
    for x = rect.x, rect.x2 do
      if not ctx:occupied(x, z) then
        ctx:floor(x, z, "PavedTile")
        paved = paved + 1
      end
    end
  end

  note(string.format(
    "rakatan trace: sealed wall + 1 door (backs onto nothing - never a room), "
      .. "%d glyph markers, %d paved forecourt cells", glyphs, paved))
end
