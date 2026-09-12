-- choir_wind.lua - "The Choir Wind" (structure_injection_roster.md WHISPER
-- #18, Ozzik, "monument reads"). Wired onto the Monument's own
-- `RUT_Monument` TileMutatorDef (co-located with PROMISE #8, the same
-- roster row's own "monument reads" gating), not a standalone mutator -
-- this whisper only rolls where that promise has already been placed by
-- the owner's pen, same live-placement debt every RUT_Monument-anchored
-- content already carries. "wind through the ruins sings at dusk; mood
-- up, grief pressure up" - beauty with a hook in it.
--
-- v1 scope, declared: this places STATIC resonant markers only (small
-- standing sculptures ringing the plaza edge, standing in for "things that
-- catch the wind and sing" - no dedicated "wind chime"/"aeolian totem"
-- ThingDef exists in the stack, confirmed via RimSage). The roster's own
-- active mechanic - mood buff / grief-pressure rise at dusk - is a
-- GameCondition/hediff hook this pass does not build, same discipline
-- Dead Beacon's unwired lamp and the Cistern's flavor-only stair used:
-- ship the structural content, name the undone behavior as a gap.
--
-- Real defNames confirmed via RimSage (vanilla Core, offline dump):
--   SculptureSmall (Core) - already the shipped precedent for a resonant/
--     marker prop (oasis_shrine.lua's offering bowls, rakatan_trace.lua's
--     glyph markers) - reused here for "something that sings," not
--     invented as a new marker type.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function min_rect(params)
  return 3, 3   -- needs at least a ring around a center cell
end

function build(ctx)
  if rect.w < 3 or rect.h < 3 then
    ctx:refuse("footprint", string.format(
      "%dx%d too small to ring the plaza with resonant markers (needs >=3x3)",
      rect.w, rect.h))
    return
  end

  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)
  local r = math.min(math.floor(rect.w / 2), math.floor(rect.h / 2))

  -- ---- resonant markers at the four cardinal edges of the plaza ring -----
  local stations = {
    { cx, cz - r }, { cx, cz + r },
    { cx - r, cz }, { cx + r, cz },
  }
  local placed = 0
  for _, s in ipairs(stations) do
    local sx, sz = s[1], s[2]
    local in_bounds = sx >= rect.x and sx <= rect.x2 and sz >= rect.z and sz <= rect.z2
    if in_bounds and not ctx:occupied(sx, sz) then
      ctx:place("SculptureSmall", sx, sz)
      placed = placed + 1
    end
  end

  if placed == 0 then
    ctx:refuse("markers", "no cardinal station landed inside the footprint")
    return
  end

  note(string.format(
    "choir wind: %d resonant markers ringing the plaza edge - static only, " ..
    "no dusk mood/grief mechanic this pass", placed))
end
