-- rib_vault.lua - "The Rib-Vault" (Probe P5, wasteland.md section 8
-- "Everything else": "Rib-vaults and the other dead sarlacc throats
-- (bunker, vault, dungeon, the dump's dump)"). One dead sarlacc's throat,
-- sunk into the ground for a thousand years, that the Junkers dug out and
-- sealed with a steel bunker at its deepest point - the worst casks they
-- won't admit to burying go HERE, past the ordinary dump.
--
-- COMPOSITION (rimworld-scene-composition skill):
--   section 2 (ground-plane change) - the throat itself is a jagged pit,
--     sunk one grade below the surrounding waste, same technique as
--     waste_camp.lua's sunken floor.
--   section 3 (implied structure, one dominant mass) - the sarlacc's ribs
--     (AB_AncientVerticalBone, already used for exactly this "standing
--     rib/vertebra" read in boneyard.lua) line the throat's flanks, denser
--     at the back and thinning toward the open mouth, so the pit reads as
--     a GULLET, not a random hole. The vault itself - one walled steel
--     bunker nested at the throat's deepest point, door facing the mouth -
--     is the single dominant mass the scene organizes around; the crate
--     anchoring its center ("the worst cask") is deliberately alone, not
--     one of an even scatter, with the lesser junk pulled in tight around
--     IT rather than spread across the whole pit (section 3's skeleton
--     rule: one thing, not a props bag).
--
-- Palette, not guessed defNames: WALL/DOOR/FLOOR_CHEAP resolve through
-- whatever faction palette is active (Junker steel plate & doors if
-- faction:Jawa_Junkers is selected, vanilla defaults otherwise - same
-- resolution toll_gap.lua's room relies on). CRATE/JUNK_PILE/SCRAP are
-- Junker-only palette roles (see rimplace/palette.json
-- faction:Jawa_Junkers: CRATE=OuterRim_StorageCrate, JUNK_PILE=
-- KOTOR_MineableJunk, SCRAP=ChunkSlagSteel) and gate on ctx:has_role() so a
-- non-Junker faction contributes nothing there rather than guessing a
-- defName outside its own palette layer, exactly the discipline dress()
-- documents in prelude.lua. AB_AncientVerticalBone (Alpha Biomes, 1x2, "a
-- standing rib/vertebra") is placed as a raw defName because no palette
-- role exists for it, the same choice krayt_graveyard.lua and boneyard.lua
-- made for their own bone dressing - UNVERIFIED against a live def dump
-- for THIS run (no defs.sqlite present in this workspace; boneyard.lua
-- records it verified against a 2026-09-05 capture, so it is a real
-- ThingDef in the active mod stack, just not re-checked here).
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)

  local pit_w, pit_h = 15, 11
  if rect.w < pit_w + 2 or rect.h < pit_h + 2 then
    ctx:refuse("RIB_VAULT", string.format(
      "%dx%d footprint too small for a %dx%d throat-pit plus clearance",
      rect.w, rect.h, pit_w, pit_h))
    return
  end

  local sx0, sz0 = cx - 7, cz - 5
  local sx1, sz1 = sx0 + pit_w - 1, sz0 + pit_h - 1

  -- ---- the throat-pit floor, jagged edge, one grade below grade ----------
  -- north (row 0) is the throat's back; south (row 10) is the open mouth -
  -- the inset widens toward the mouth so the opening itself reads flared,
  -- not a rectangle with a door cut in it.
  local row_inset = {
    [0] = { 2, 1 }, [1] = { 1, 1 }, [2] = { 0, 1 }, [3] = { 1, 0 },
    [4] = { 0, 0 }, [5] = { 0, 1 }, [6] = { 1, 0 }, [7] = { 1, 2 },
    [8] = { 2, 1 }, [9] = { 3, 2 }, [10] = { 4, 3 },
  }
  local function in_pit(x, z)
    local i = z - sz0
    local inset = row_inset[i]
    if inset == nil then return false end
    return x >= sx0 + inset[1] and x <= sx1 - inset[2]
  end

  local floor_role = ctx:role("FLOOR_CHEAP")
  local floor_placed = 0
  for i = 0, pit_h - 1 do
    local z = sz0 + i
    local inset = row_inset[i]
    for x = sx0 + inset[1], sx1 - inset[2] do
      if ctx:in_bounds(x, z) and ctx:floor(x, z, floor_role) then
        floor_placed = floor_placed + 1
      end
    end
  end

  -- ---- the vault, nested at the throat's deepest (north) point ----------
  local vault_w, vault_h = 5, 5
  local vx, vz = cx - 2, sz0 + 1
  local vault_r = R(vx, vz, vault_w, vault_h)
  local vault_inner = shell(ctx, "Storeroom", vault_r,
    { floor = "FLOOR_CHEAP", doors = { "S" } })

  -- ---- the worst cask: one crate, alone at the vault's center ------------
  local anchor_placed = false
  local ax, az = center(vault_inner)
  if ctx:has_role("CRATE") and try_place(ctx, "CRATE", ax, az, 0) then
    anchor_placed = true
  end

  -- lesser junk pulled in TIGHT around the one anchor crate, never spread
  -- across the whole vault (section 3: a props bag reads as a props bag).
  local junk_placed = scatter(ctx, "JUNK_PILE", vault_inner, 2,
    { rot = "any", avoid = function(x, z) return x == ax and z == az end })
  local scrap_placed = scatter(ctx, "SCRAP", vault_inner, 2,
    { rot = "any", avoid = function(x, z) return x == ax and z == az end })

  -- ---- the ribs: denser at the back, thinning toward the open mouth -----
  -- both flanks of the throat corridor south of the vault, jittered off the
  -- rim rather than laid on a fixed stride (composition skill's REGULAR
  -- GRIDS ban - never a fixed-step loop in a template).
  local ribs_placed = 0
  for i = 3, pit_h - 1 do
    local z = sz0 + i
    local inset = row_inset[i]
    -- density falls off toward the mouth (row 10)
    local chance = math.max(0.15, 0.85 - (i - 3) * 0.10)
    if rng.chance(chance) then
      local wx = sx0 + inset[1] - 1 + rng.int(0, 1)
      if ctx:in_bounds(wx, z) and not ctx:occupied(wx, z) then
        ctx:place("AB_AncientVerticalBone", wx, z, rng.int(0, 1) == 0 and 1 or 3)
        ribs_placed = ribs_placed + 1
      end
    end
    if rng.chance(chance) then
      local ex = sx1 - inset[2] + 1 - rng.int(0, 1)
      if ctx:in_bounds(ex, z) and not ctx:occupied(ex, z) then
        ctx:place("AB_AncientVerticalBone", ex, z, rng.int(0, 1) == 0 and 1 or 3)
        ribs_placed = ribs_placed + 1
      end
    end
  end
  -- a few teeth-ribs arcing the mouth itself (row 10), spaced with gaps so
  -- the entry stays legibly open, not fenced shut.
  local mouth_i = pit_h - 1
  local mouth_inset = row_inset[mouth_i]
  local mouth_z = sz0 + mouth_i
  for x = sx0 + mouth_inset[1], sx1 - mouth_inset[2], 3 do
    local jx = x + rng.int(-1, 1)
    if ctx:in_bounds(jx, mouth_z) and not ctx:occupied(jx, mouth_z)
        and in_pit(jx, mouth_z) then
      ctx:place("AB_AncientVerticalBone", jx, mouth_z, 0)
      ribs_placed = ribs_placed + 1
    end
  end

  note(string.format(
    "rib-vault: %d throat-pit floor cells (jagged, %s), %dx%d steel vault "
    .. "(door S), %s worst-cask anchor, %d junk piles, %d scrap around it, "
    .. "%d ribs lining the throat",
    floor_placed, tostring(floor_role), vault_w, vault_h,
    anchor_placed and "1" or "0", junk_placed, scrap_placed, ribs_placed))
end
