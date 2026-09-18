-- soft_ground.lua - "Soft Ground" (structure_injection_roster.md WHISPER
-- #5, Ta'Baa/Ishko, dunes). Anchor: the vanilla/Odyssey `Dunes`
-- TileMutatorDef (confirmed real via a validate_patch.py
-- PatchOperationConditional probe against the live 634-active-mod set: 1
-- match, Data/Odyssey/Defs/TileMutators/TileMutators_Natural.xml — this is
-- the FIRST whisper row anchored on a vanilla base-game mutator rather than
-- an Odyssey/modded one; `Dunes` carries `biomeWhitelist: ExtremeDesert`
-- and no <extraGenSteps> element of its own, so the patch Adds a whole new
-- element to the TileMutatorDef node, same shape as Cavern/DryLake/Hollow/
-- Caves).
--
-- v1 scope, declared: the roster's own line is "natural sink-cells that
-- behave as unrated pit covers (pit-trap synergy; mass rules apply) — free
-- kill-zone; also under YOUR paths." There is no pit mechanism in the
-- engine to trigger — `PIT_SUPERDEEP_COLLAPSE_1` is RULED (a pit is a
-- SUPERDEEP cell, spikes only) but explicitly "nothing built" as of that
-- item's own record. So this pass cannot wire an actual unrated-pit-cover
-- behavior; it places STATIC warning cairns only, the same substitute-prop
-- discipline `oasis_shrine.lua`/`rakatan_trace.lua`/`choir_wind.lua`/
-- `sarlacc_sign.lua`/`listening_dark.lua` all used (no "warning cairn" or
-- "sink cell" ThingDef exists in the stack). The active hazard — cells that
-- actually behave as pit covers — is a named, undone gap, not invented
-- here, and cannot legally be built until PIT_SUPERDEEP_COLLAPSE_1 ships
-- engine-side.
--
-- Real defNames confirmed via the same validate_patch.py probe (Core,
-- already used repeatedly across this program, RimSage-independent):
--   SculptureSmall (Core, Buildings_Art.xml) - reused again as the
--   "someone already marked this ground" cairn, exactly the substitution
--   every prior whisper batch used for a described-but-unmodeled object.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  if rect.w < 4 or rect.h < 4 then
    ctx:refuse("FOOTPRINT", string.format(
      "%dx%d too small to scatter legible warning cairns (needs >=4x4)", rect.w, rect.h))
    return
  end

  -- Scattered, not clustered — the roster's own line says the sink-cells
  -- turn up "also under YOUR paths," i.e. anywhere in the footprint, not
  -- concentrated in one spot the way a shrine or roost would be.
  local cairns = 0
  for zz = rect.z, rect.z2 do
    for xx = rect.x, rect.x2 do
      if not ctx:occupied(xx, zz) and rng.chance(0.06) then
        ctx:place("SculptureSmall", xx, zz)
        cairns = cairns + 1
      end
    end
  end

  -- A patch this small could legitimately roll zero cairns at 6% density;
  -- guarantee at least one so the whisper never generates completely inert.
  if cairns == 0 then
    local cx = rect.x + math.floor(rect.w / 2)
    local cz = rect.z + math.floor(rect.h / 2)
    if not ctx:occupied(cx, cz) then
      ctx:place("SculptureSmall", cx, cz)
      cairns = 1
    end
  end

  note(string.format(
    "soft ground: %d warning-cairn markers scattered across the footprint - " ..
    "static only, no functional pit-cover hazard this pass (engine doesn't exist yet)",
    cairns))
end
