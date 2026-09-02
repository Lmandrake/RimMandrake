-- cistern.lua - "The Cistern" (structure_injection_roster.md PROMISE #19,
-- RimUtinni tier, terminator band, Oomo): buried waterworks in a single
-- walled pump room. "water security; the stair goes further down than the
-- pumps need" - the roster's own line implies a lower level. RimWorld has
-- no multi-level/basement mechanic, so the "dark stair" is deliberately
-- NOT modeled as geometry here - it stays flavor text for the landing
-- letter/inspect string, same as `hunting_lodge.lua`'s COOLER note pattern
-- of naming what a template cannot prove. Documented, not silently dropped.
--
-- Real defNames verified against the live 591-mod stack via a
-- validate_patch.py PatchOperationConditional probe against the actual
-- on-disk Data/Mods/Workshop XML (same worked-around defs.sqlite gap as
-- oasis_shrine.lua and rakatan_trace.lua):
--   PrimitiveWell (Dubs Bad Hygiene Lite, BuildingsB_Hygiene.xml) - the
--     pump/waterworks centerpiece, same shipped precedent as
--     moisture_farm.lua's cistern hut.
--   Shelf (Core, Buildings_Furniture.xml) - tool/parts storage against the
--     back wall.
--   TorchLamp (Core, Buildings_Furniture.xml).
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)

  local room_w, room_h = 7, 7
  if rect.w < room_w or rect.h < room_h then
    ctx:refuse("PUMP_ROOM", string.format(
      "%dx%d footprint too small for a %dx%d pump room", rect.w, rect.h, room_w, room_h))
    return
  end
  local rx, rz = cx - math.floor(room_w / 2), cz - math.floor(room_h / 2)

  -- ---- the pump room, walled and roofed ----------------------------------
  ctx:room("Storeroom", rx, rz, room_w, room_h, true)
  ctx:wall_rect(rx, rz, room_w, room_h)
  ctx:door(rx + math.floor(room_w / 2), rz)

  -- ---- the well, off-center so the room reads as WORKED not decorative ---
  local wx, wz = rx + room_w - 2, rz + room_h - 2
  if not ctx:occupied(wx, wz) then
    ctx:place("PrimitiveWell", wx, wz)
  end

  -- ---- shelving for pump parts/tools along the entry wall -----------------
  -- Shelf is a 2x1 footprint (measured via lint's own footprint-collision
  -- check, not assumed) - two shelves spaced to leave a 1-cell gap between
  -- them and clear of both side walls.
  local shelves = 0
  local sz = rz + 1
  local shelf_positions = { rx + 1, rx + room_w - 3 }
  for _, sx in ipairs(shelf_positions) do
    if not ctx:occupied(sx, sz) then
      ctx:place("Shelf", sx, sz)
      shelves = shelves + 1
    end
  end

  if ctx:has_role("LIGHT") then
    ctx:place("TorchLamp", rx + 1, rz + room_h - 2)
  end

  note(string.format(
    "cistern: %dx%d pump room, well off-center, %d shelving cells. "
      .. "'the stair goes further down than the pumps need' is flavor only - "
      .. "no basement/multi-level geometry exists to model it; TEMPLATE CANNOT PROVE depth.",
    room_w, room_h, shelves))
end
