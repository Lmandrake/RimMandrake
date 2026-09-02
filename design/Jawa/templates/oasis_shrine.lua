-- oasis_shrine.lua - "The Oasis Shrine" (structure_injection_roster.md
-- PROMISE #10, RimUtinni tier, `Oasis` mutator tiles, Oomo): a spring-side
-- shrine with offering bowls at a natural well. "fertility boon ground;
-- desecration is remembered" - the roster's own line: small, open, no
-- walls/room (a shrine at a spring is a gathering place, not a fort).
--
-- Real defNames verified against the live 591-mod stack via a
-- validate_patch.py PatchOperationConditional probe (this session's
-- defs.sqlite capture is currently scoped to ResearchProjectDef only, 522
-- rows, no ThingDef/TerrainDef coverage - `rimplace verify` legitimately
-- reports UNMEASURED against it right now; this probe against the real
-- on-disk Data/Mods/Workshop XML is the actual authority, same source
-- validate_patch.py --defs always reads):
--   PrimitiveWell (Dubs Bad Hygiene Lite, BuildingsB_Hygiene.xml) - the
--     spring itself. Already the shipped precedent in moisture_farm.lua.
--   SculptureSmall (Core, Buildings_Art.xml) - reused as the offering-bowl
--     / shrine-marker prop; no dedicated "offering bowl" ThingDef exists in
--     the stack. Substitution, not invention, same discipline as
--     hunting_lodge.lua's trophy substitution.
--   TorchLamp (Core, Buildings_Furniture.xml).
--   PavedTile (Core, Terrain_Floors.xml) - the shrine's paved footing.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)

  -- ---- the spring, centered --------------------------------------------
  ctx:place("PrimitiveWell", cx, cz)

  -- ---- paved footing around the spring ----------------------------------
  local pave_r = math.min(math.floor(rect.w / 2), math.floor(rect.h / 2)) - 1
  if pave_r < 2 then
    ctx:refuse("PAVED_FOOTING", string.format(
      "%dx%d footprint too small to pave a shrine ring around the spring", rect.w, rect.h))
    pave_r = 0
  end
  local paved = 0
  if pave_r >= 2 then
    for zz = cz - pave_r, cz + pave_r do
      for xx = cx - pave_r, cx + pave_r do
        local in_bounds = xx >= rect.x and xx <= rect.x2 and zz >= rect.z and zz <= rect.z2
        local dist = math.max(math.abs(xx - cx), math.abs(zz - cz))
        if in_bounds and dist <= pave_r and not (xx == cx and zz == cz) then
          ctx:floor(xx, zz, "PavedTile")
          paved = paved + 1
        end
      end
    end
  end

  -- ---- offering bowls: four stations at the footing's cardinal edge ------
  -- "offering bowls" plural, per the roster line - one per cardinal
  -- direction so the shrine reads as tended from every approach, not just
  -- the obvious one.
  local bowls = 0
  if pave_r >= 2 then
    local stations = {
      { cx, cz - pave_r }, { cx, cz + pave_r },
      { cx - pave_r, cz }, { cx + pave_r, cz },
    }
    for _, s in ipairs(stations) do
      local bx, bz = s[1], s[2]
      local in_bounds = bx >= rect.x and bx <= rect.x2 and bz >= rect.z and bz <= rect.z2
      if in_bounds and not ctx:occupied(bx, bz) then
        ctx:place("SculptureSmall", bx, bz)
        bowls = bowls + 1
      end
    end
  end

  -- ---- two torch lamps flanking, so the shrine reads at night too --------
  if ctx:has_role("LIGHT") and pave_r >= 3 then
    local lx1, lz1 = cx - pave_r + 1, cz - pave_r + 1
    local lx2, lz2 = cx + pave_r - 1, cz + pave_r - 1
    if not ctx:occupied(lx1, lz1) then ctx:place("TorchLamp", lx1, lz1) end
    if not ctx:occupied(lx2, lz2) then ctx:place("TorchLamp", lx2, lz2) end
  end

  note(string.format(
    "oasis shrine: spring + %d paved cells, %d offering-bowl stations, no walls/room by design",
    paved, bowls))
end
