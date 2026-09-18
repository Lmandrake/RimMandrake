-- listening_dark.lua - "The Listening Dark" (structure_injection_roster.md
-- WHISPER #2, Ishko, nightside). Anchor: the roster's own line names it --
-- "(Hollow/Caves mutators)" -- both `Hollow` (Odyssey) and `Caves` (Core)
-- TileMutatorDefs, confirmed real via a validate_patch.py
-- PatchOperationConditional probe against the live 632-active-mod set
-- (1 match each, Odyssey TileMutators_Natural.xml / Core TileMutators.xml).
-- Both mutators already carve the "pre-connected cave network under the
-- map" themselves -- that half of the roster line is native to the anchor,
-- not authored here, same as how a promise's gating tile already IS the
-- terrain it names. This template places what the roster adds ON TOP of
-- that native cave: "free hidden base; something already listens in it."
--
-- v1 scope, declared: STATIC content only -- a small stocked nook (the
-- "free hidden base") and one marker prop standing in for "something
-- already listens" (no dedicated eavesdropping/watcher ThingDef exists in
-- the stack; SculptureSmall is reused as the marker, the same substitute-
-- prop discipline oasis_shrine.lua/rakatan_trace.lua/choir_wind.lua already
-- established). No AI/threat/audio mechanic is built -- "something already
-- listens" stays a reveal for a future hook, not a new comp, same
-- discipline Dead Beacon's unwired lamp and Choir Wind's static markers
-- used.
--
-- Real defNames (Core, already the shipped precedent in this program --
-- Shelf/TorchLamp in cistern.lua, SculptureSmall everywhere from
-- oasis_shrine.lua on): Shelf, TorchLamp, SculptureSmall.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function min_rect(params)
  return 4, 4   -- a small nook: 2 shelves + a lamp + a marker need room to not collide
end

function build(ctx)
  if rect.w < 4 or rect.h < 4 then
    ctx:refuse("footprint", string.format(
      "%dx%d too small for the hidden-base nook (needs >=4x4)", rect.w, rect.h))
    return
  end

  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)

  -- ---- the free hidden base: two stocked shelves, corners of the nook ----
  -- Shelf is 2x1 (rimworld-modding lesson from batch 3's Cistern/Toll Gap
  -- fix), so these sit on opposite sides rather than adjacent cells.
  local shelves = 0
  local shelf_spots = {
    { rect.x, cz - 1 }, { rect.x2, cz + 1 },
  }
  for _, s in ipairs(shelf_spots) do
    local sx, sz = s[1], s[2]
    local in_bounds = sx >= rect.x and sx <= rect.x2 and sz >= rect.z and sz <= rect.z2
    if in_bounds and not ctx:occupied(sx, sz) then
      ctx:place("Shelf", sx, sz)
      shelves = shelves + 1
    end
  end

  -- ---- one torch, so the "free base" is usable, not just decorative -----
  if not ctx:occupied(cx, cz) then
    ctx:place("TorchLamp", cx, cz)
  end

  -- ---- the watcher marker: "something already listens" -------------------
  local mx, mz = cx, rect.z
  if ctx:occupied(mx, mz) then mx, mz = cx, rect.z2 end
  local marker = 0
  if not ctx:occupied(mx, mz) then
    ctx:place("SculptureSmall", mx, mz)
    marker = 1
  end

  if shelves == 0 and marker == 0 then
    ctx:refuse("content", "no shelf or marker cell landed inside the footprint")
    return
  end

  note(string.format(
    "listening dark: %d stocked shelves, %d watcher marker - static only, " ..
    "no AI/threat mechanic this pass; the cave network itself is the anchor " ..
    "mutator's own native content, not authored here",
    shelves, marker))
end
