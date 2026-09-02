-- monument.lua - canvas floor: see min_rect() below (`rimplace minrect monument`).
-- "The Monument" (structure_injection_roster.md PROMISE #8,
-- RimUtinni tier, Ozzik): a half-buried colossus and its plaza. "pride on
-- claiming it; the pride-meter knows" - a single centerpiece statue, not a
-- building, matching the roster's "colossus icon" read: this is a landmark
-- to stand beside, not a room to enter.
--
-- Real defNames verified against vanilla source (RimSage-indexed), same
-- ground-truth discipline glass_sea.lua's Odyssey terrain picks used:
--   SculptureGrand (Core, ParentName="SculptureBase", 2x2, Beauty 400,
--     MadeFromStuff via stuffCategories Metallic/Woody/Stony) - the
--     colossus itself, stuffed BlocksGranite for an ancient-stone read
--     ("half-buried", not a fresh commission).
--   BlocksGranite (Core) - the statue's stuff.
--   PavedTile (Core, Terrain_Floors.xml) - the plaza, already the shipped
--     precedent (oasis_shrine.lua, rakatan_trace.lua).
--   ChunkGranite (Core) - a few half-buried rubble chunks around the base,
--     the "half-buried" read made physical rather than left as label text.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

-- The declared canvas floor; the engine checks it before build() runs
-- (TEMPLATE_CANVAS_UNDECLARED_1). `rimplace minrect monument`.
function min_rect(params)
  return 2, 2   -- SculptureGrand's own 2x2 bounds; below this it lands outside
end

function build(ctx)
  -- SculptureGrand is 2x2 (verified against source, see header) - a
  -- footprint narrower than that has no legal cell for its own bounds
  -- clamp to land on (code-review finding, 2026-09-02: on rect.w==1 the old
  -- clamp pushed the statue to rect.x-1, ONE CELL OUTSIDE the footprint,
  -- which ctx:place silently refuses rather than draws - the plaza and
  -- rubble still built around a colossus that was never placed). Refuse
  -- cleanly instead, same convention dead_beacon.lua/imperial_waystation.lua
  -- already use for their own minimum footprints.
  if rect.w < 2 or rect.h < 2 then
    ctx:refuse("footprint", string.format(
      "%dx%d cannot hold the 2x2 SculptureGrand centerpiece", rect.w, rect.h))
    return
  end

  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)

  -- ---- the plaza: paved, filling the footprint -------------------------
  local paved = ctx:floor_rect(rect.x, rect.z, rect.w, rect.h, "PavedTile")

  -- ---- the colossus itself, centered ------------------------------------
  local sx, sz = cx, cz
  if sx + 1 > rect.x2 then sx = rect.x2 - 1 end
  if sz + 1 > rect.z2 then sz = rect.z2 - 1 end
  ctx:place("SculptureGrand", sx, sz, 0, "BlocksGranite")

  -- ---- half-buried rubble at its base ------------------------------------
  local rubble = 0
  local stations = {
    { sx - 1, sz - 1 }, { sx + 2, sz - 1 }, { sx - 1, sz + 2 }, { sx + 2, sz + 2 },
  }
  for _, s in ipairs(stations) do
    local rx, rz = s[1], s[2]
    local in_bounds = rx >= rect.x and rx <= rect.x2 and rz >= rect.z and rz <= rect.z2
    if in_bounds and not ctx:occupied(rx, rz) then
      ctx:place("ChunkGranite", rx, rz)
      rubble = rubble + 1
    end
  end

  note(string.format(
    "monument: 1 grand sculpture (granite) on a %d-cell paved plaza, %d half-buried rubble chunks at its base",
    paved, rubble))
end
