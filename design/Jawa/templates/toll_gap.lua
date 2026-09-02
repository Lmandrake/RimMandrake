-- toll_gap.lua - "The Toll Gap" (structure_injection_roster.md PROMISE #13,
-- RimUtinni tier, road tiles through cliffs, Mob'Unloo): a canyon
-- chokepoint with a toll house. "a defensible gap; ghosts of unpaid tolls" -
-- one small walled toll house (collector's desk + ledger storage) flanked
-- by sandbag barriers narrowing the gap either side, so the CHOKEPOINT
-- reads even though rimplace has no terrain/cliff authoring of its own
-- (the canyon walls themselves are the tile's existing terrain, not this
-- template's job - this places the toll house and its barrier dressing
-- only).
--
-- Real defNames verified against the live 591-mod stack via a
-- validate_patch.py PatchOperationConditional probe against the actual
-- on-disk Data/Mods/Workshop XML (same worked-around defs.sqlite gap as
-- oasis_shrine.lua, rakatan_trace.lua and cistern.lua):
--   Table1x2c / DiningChair (Core, Buildings_Furniture.xml) - the
--     collector's desk and seat.
--   Shelf (Core, Buildings_Furniture.xml) - the ledger storage, the
--     roster's own "ghosts of unpaid tolls" line.
--   TorchLamp (Core, Buildings_Furniture.xml).
--   Sandbags (Core, Buildings_Security.xml) - the barrier dressing that
--     narrows the gap.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)

  local room_w, room_h = 7, 5
  if rect.w < room_w + 4 or rect.h < room_h then
    ctx:refuse("TOLL_HOUSE", string.format(
      "%dx%d footprint too small for a %dx%d toll house plus barrier clearance either side",
      rect.w, rect.h, room_w, room_h))
    return
  end
  local rx, rz = cx - math.floor(room_w / 2), cz - math.floor(room_h / 2)

  -- ---- the toll house, walled and roofed ---------------------------------
  ctx:room("Storeroom", rx, rz, room_w, room_h, true)
  ctx:wall_rect(rx, rz, room_w, room_h)
  ctx:door(rx + math.floor(room_w / 2), rz + room_h - 1)

  -- ---- the collector's desk, facing the door so it reads as "manned" -----
  local dx, dz = rx + math.floor(room_w / 2), rz + room_h - 3
  if not ctx:occupied(dx, dz) then
    ctx:place("Table1x2c", dx, dz)
  end
  local cx2, cz2 = dx, dz - 1
  if not ctx:occupied(cx2, cz2) then
    ctx:place("DiningChair", cx2, cz2, 4) -- rot 4 (south) faces the desk
  end

  -- ---- the ledger shelves, back wall --------------------------------------
  -- Shelf is a 2x1 footprint (measured via lint's own footprint-collision
  -- check, not assumed): two shelves flanking the center column (where the
  -- chair sits one row south), each clear of its own side wall.
  local shelves = 0
  local shelf_positions = { rx + 1, rx + room_w - 3 }
  for _, sx in ipairs(shelf_positions) do
    if not ctx:occupied(sx, rz + 1) then
      ctx:place("Shelf", sx, rz + 1)
      shelves = shelves + 1
    end
  end

  if ctx:has_role("LIGHT") then
    ctx:place("TorchLamp", rx + 1, rz + room_h - 2)
  end

  -- ---- barrier dressing, narrowing the gap either side of the house ------
  -- a short sandbag run east and west of the house, at the house's own
  -- south (door) row - the traveler passes the desk, not around it.
  local barrier_row = rz + room_h - 1
  local barrier_cells = 0
  local run = math.min(3, math.max(0, rect.x2 - (rx + room_w)))
  for i = 1, run do
    local bx = rx + room_w - 1 + i
    if bx <= rect.x2 and not ctx:occupied(bx, barrier_row) then
      ctx:place("Sandbags", bx, barrier_row)
      barrier_cells = barrier_cells + 1
    end
  end
  local run_w = math.min(3, math.max(0, rx - rect.x))
  for i = 1, run_w do
    local bx = rx - i
    if bx >= rect.x and not ctx:occupied(bx, barrier_row) then
      ctx:place("Sandbags", bx, barrier_row)
      barrier_cells = barrier_cells + 1
    end
  end

  note(string.format(
    "toll gap: %dx%d toll house (desk+chair+%d ledger shelves), %d sandbag barrier cells "
      .. "narrowing the gap. Canyon terrain itself is the tile's own existing geometry, "
      .. "not placed by this template.",
    room_w, room_h, shelves, barrier_cells))
end
