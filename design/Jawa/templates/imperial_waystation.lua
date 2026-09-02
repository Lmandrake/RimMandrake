-- imperial_waystation.lua - canvas floor: see min_rect() below (`rimplace
-- minrect imperial_waystation`).
-- "The Imperial Waystation" (structure_injection_
-- roster.md PROMISE #21, RimUtinni tier, Ozzik): a modular prefab outpost
-- along an old Imperial road, its stores still intact - unlike a ruin, this
-- one was left in working order. "loot and statecraft hooks; pursuit heat
-- rises on looting" - the administrative desk is the statecraft read, the
-- stocked shelves are the loot.
--
-- Real defNames verified against vanilla source (RimSage-indexed):
--   Shelf (Core, 2x1, a REAL functional storage building - checked
--     AncientIndustrialShelf first as a more "Imperial ruin" flavored
--     alternative, but its own description says "offers nothing of value"
--     and isInert=true/claimable=false: it cannot actually hold anything,
--     which contradicts this row's own "INTACT stores" framing. Plain
--     Shelf is the correct pick precisely because this site is not ruined.
--   Steel / ComponentIndustrial (Core) - the stocked goods, same "rich
--     tech scrap" vocabulary broken_ring.lua already established.
--   MedicineIndustrial (Core) - a third goods type so the stores read as a
--     real depot's mixed inventory, not a single-resource stash.
--   Table1x2c / DiningChair / TorchLamp (Core) - the administrative desk,
--     already the shipped precedent from toll_gap.lua's own toll house.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

-- The declared canvas floor; the engine checks it before build() runs
-- (TEMPLATE_CANVAS_UNDECLARED_1). `rimplace minrect imperial_waystation`.
function min_rect(params)
  return 9, 6   -- store room + admin desk side by side, with their shared shell
end

function build(ctx)
  local W, H = 9, 6
  if rect.w < W or rect.h < H then
    ctx:refuse("footprint", string.format(
      "%dx%d cannot hold a %dx%d waystation", rect.w, rect.h, W, H))
    return
  end

  local x, z = rect.x, rect.z

  -- ---- the prefab shell ---------------------------------------------------
  ctx:room("Storeroom", x, z, W, H, true)
  ctx:wall_rect(x, z, W, H)
  ctx:door(x + math.floor(W / 2), z)

  -- ---- the administrative desk, near the door -----------------------------
  -- Table1x2c is 1 wide x 2 TALL (its own footprint spans (x,z) and
  -- (x,z+1), confirmed by lint's own footprint-collision report, not
  -- assumed from the name) - the chair sits beside it, not below it.
  local desk_x, desk_z = x + math.floor(W / 2) - 1, z + 1
  ctx:place("Table1x2c", desk_x, desk_z, 0)
  ctx:place("DiningChair", desk_x + 1, desk_z)
  ctx:place("TorchLamp", x + 1, z + 1)

  -- ---- the stores: three shelves along the back wall, stocked ------------
  local goods = { "Steel", "ComponentIndustrial", "MedicineIndustrial" }
  local stocked = 0
  local shelf_z = z + H - 2
  for i = 0, 2 do
    local sx = x + 2 + i * 2
    if sx + 1 <= x + W - 2 and not ctx:occupied(sx, shelf_z) then
      ctx:place("Shelf", sx, shelf_z, 0)
      if not ctx:occupied(sx, shelf_z - 1) then
        ctx:place(goods[i + 1], sx, shelf_z - 1)
        stocked = stocked + 1
      end
    end
  end

  note(string.format(
    "imperial waystation: %dx%d prefab, admin desk near the door, %d/3 stocked shelves along the back wall",
    W, H, stocked))
end
