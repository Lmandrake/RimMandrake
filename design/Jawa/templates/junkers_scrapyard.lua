-- junkers_scrapyard.lua - a Junkers salvage yard: one roofed sorting shed,
-- one roofed forge lean-to, and an open, unwalled lot scattered with scrap
-- heaps. DISTRICT_TEMPLATE_LIBRARY_1, Junkers district #1
-- (ownership_settlement_spec.md item 10, "Pilot town: Junkers"; The Claim
-- Jump's manifest names this slot "scrapyard",
-- src/RimUtinni/AshkarrInhabited/Defs/SettlementManifestDefs/SettlementManifestDefs_TheClaimJump.xml).
--
-- WHAT THIS FILE DEMONSTRATES:
--   * an open-air district (no perimeter wall at all) next to two small
--     roofed structures - not every district is a single building
--   * scattered decoration (junk heaps) placed by rng with a footprint
--     exclusion check, so nothing lands inside a room it cannot see
--   * the NO-SECURITY-PROPS decision, made explicit rather than silent
--
-- Reused art only, no new sprites: WALL/DOOR/STORAGE/TABLE/CHAIR/STOVE/
-- LIGHT/SANDBAG all resolve through the existing rimplace palette
-- (palette.json). Run with --tech Neolithic: Junkers scavenge, they do not
-- run a power grid, and Neolithic gives Campfire/Bedroll/TorchLamp - every
-- piece here is un-powered by construction, which is also why this
-- template needs nothing from the (nonexistent) power/pipe-net layer.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

-- ---------------------------------------------------------------------------
-- helpers
-- ---------------------------------------------------------------------------

-- A small roofed, walled, single-door structure. Returns its rect so the
-- caller can furnish the interior and exclude it from later scatter.
local function place_shed(ctx, x, z, w, h, roleLabel)
  ctx:room(roleLabel, x, z, w, h, true)
  ctx:wall_rect(x, z, w, h)
  ctx:door(x + math.floor(w / 2), z)
  return { x = x, z = z, w = w, h = h }
end

local function in_rect(x, z, r)
  return x >= r.x and x <= r.x + r.w - 1 and z >= r.z and z <= r.z + r.h - 1
end

-- ---------------------------------------------------------------------------
-- the entry point
-- ---------------------------------------------------------------------------
-- The declared canvas floor; the engine checks it before build() runs
-- (TEMPLATE_CANVAS_UNDECLARED_1). `rimplace minrect junkers_scrapyard`.
function min_rect(params)
  return 16, 14
end

function build(ctx)
  local p = params
  local w, h = rect.w, rect.h

  if w < 16 or h < 14 then
    ctx:refuse("footprint", string.format(
      "%dx%d too small for a scrapyard (sorting shed + forge + open lot)", w, h))
    return
  end

  -- ---- ground cover: the whole lot is cleared dirt/gravel, not paved -----
  ctx:floor_rect(rect.x, rect.z, w, h)

  -- ---- the sorting shed: parts get triaged here before they go anywhere -
  local shed = place_shed(ctx, rect.x + 1, rect.z + 1, 10, 8, "Storeroom")
  do
    local ix, iz, iw, ih = shed.x + 1, shed.z + 1, shed.w - 2, shed.h - 2
    if ctx:has_role("STORAGE") then
      local sw = ctx:width_of("STORAGE")
      local xx = ix
      while xx <= ix + iw - sw do
        ctx:place_role("STORAGE", xx, iz)
        xx = xx + sw
      end
    end
    if ctx:has_role("TABLE") then ctx:place_role_fit("TABLE", ix, iz + 2, iw, ih - 2) end
    if ctx:has_role("CHAIR") then ctx:place_role_fit("CHAIR", ix, iz + 2, iw, ih - 2) end
    if ctx:has_role("LIGHT") then ctx:place_role_fit("LIGHT", ix, iz, iw, ih) end
  end

  -- ---- the forge lean-to: a second small roofed room, smelting scrap -----
  local forge = nil
  local forge_x = rect.x + w - 9
  if forge_x > shed.x + shed.w + 1 then
    forge = place_shed(ctx, forge_x, rect.z + 1, 8, 6, "Workshop")
    local ix, iz, iw, ih = forge.x + 1, forge.z + 1, forge.w - 2, forge.h - 2
    if ctx:has_role("STOVE") then
      -- from the far corner backwards, same idiom as dwelling.lua's kitchen
      local placed = false
      for zz = iz + ih - 1, iz, -1 do
        for xx = ix + iw - 1, ix, -1 do
          if ctx:can_place("STOVE", xx, zz) then
            ctx:place_role("STOVE", xx, zz)
            placed = true
            break
          end
        end
        if placed then break end
      end
    end
    if ctx:has_role("STORAGE") then ctx:place_role_fit("STORAGE", ix, iz, iw, ih) end
    if ctx:has_role("LIGHT") then ctx:place_role_fit("LIGHT", ix, iz, iw, ih) end
  else
    note("forge lean-to skipped: footprint too narrow to clear the sorting shed")
  end

  -- ---- open lot: scattered junk heaps, no walls, no roof -----------------
  -- SANDBAG stands in for an unsorted scrap heap - there is no dedicated
  -- "junk pile" ThingDef in the palette and this item's brief is reused art
  -- only, no new sprites. Excluded from both sheds by rect check, not just
  -- occupancy, so a heap never reads as "inside" a room it cannot see.
  if ctx:has_role("SANDBAG") then
    local heaps = rng.int(5, 9)
    local placed, attempts = 0, 0
    while placed < heaps and attempts < heaps * 12 do
      attempts = attempts + 1
      local xx = rng.int(rect.x + 1, rect.x + w - 2)
      local zz = rng.int(rect.z + 1, rect.z + h - 2)
      if not in_rect(xx, zz, shed) and (forge == nil or not in_rect(xx, zz, forge))
         and ctx:can_place("SANDBAG", xx, zz) then
        ctx:place_role("SANDBAG", xx, zz)
        placed = placed + 1
      end
    end
    note(string.format("%d/%d scrap heaps placed in the open lot", placed, heaps))
  end

  -- ---- security: NONE, deliberately ---------------------------------------
  -- ownership_settlement_spec.md item 8 asks for "security props" per
  -- district; The Claim Jump's own manifest sets searchesLeavers=false
  -- (Inhabited_SecurityProfile_Junkers) - low security, "forgiving". This
  -- pilot PROVES the negative: no camera, no watchtower, no fence prop is
  -- placed here on purpose, rather than forcing a security prop onto a
  -- settlement that canonically waves visitors through both ways. See
  -- junkers_depot.lua for a sketch of what the vocabulary would look like
  -- for a future higher-security settlement.
  note("no security props placed: Junkers/The Claim Jump is low security by design (searchesLeavers=false)")
end
