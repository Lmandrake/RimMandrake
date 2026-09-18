-- iron_rain.lua - "Iron Rain" (structure_injection_roster.md WHISPER #17,
-- Zizzik/Sh'kaar, ring-adjacent). Anchor: `RUT_BrokenRing` (our own
-- PROMISE #20 "The Broken Ring" mutator, TileMutatorDefs_Batch5.xml,
-- confirmed present in-repo by direct read - already carries its own
-- `<extraGenSteps><li>RUT_GenStep_BrokenRing</li></extraGenSteps>`, same
-- shape as PROMISE #8 RUT_Monument, which WHISPER #18 The Choir Wind
-- already rides). This whisper only rolls where that promise has already
-- been placed by the owner's pen - same live-placement debt every
-- RUT_Monument/RUT_BrokenRing content already carries. Not live-probed via
-- validate_patch.py: `mandrake.rut.injections` remains absent from the
-- live ModsConfig.xml (declared since 2026-09-09), so a live probe of our
-- own not-yet-enabled mod's own def would correctly report 0 matches -
-- same non-issue Choir Wind's WhisperBatch1.xml note already accepted for
-- RUT_Monument.
--
-- v1 scope, declared: the roster's own line is "periodic small debris
-- falls all stay — free steel, real danger · the sky sheds." The
-- PERIODIC/ongoing falling-debris behavior is a GameCondition or repeating
-- incident this pass does not build (same class of gap as Rootstock's
-- rain-trigger, Choir Wind's mood/grief mechanic, Soft Ground's pit-cover
-- hazard). This places the STATIC aftermath only — debris that has
-- already fallen and stayed, exactly "free steel" made literal - not the
-- active ongoing hazard.
--
-- Real defNames confirmed by direct read of the live Core dump (Core,
-- ThingDefs_Buildings/Buildings_Ancient_Indoors.xml and
-- Buildings_Exotic.xml both reference it as vanilla loot content):
--   ChunkSlagSteel (Core) - fused steel debris chunk, the "something fell
--     from orbit and is still hot" read.
--   Steel (Core) - the resource stack itself, standing in for "free
--     steel" literally rather than requiring a mine/smelt step.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  if rect.w < 4 or rect.h < 4 then
    ctx:refuse("FOOTPRINT", string.format(
      "%dx%d too small to scatter a legible debris fall (needs >=4x4)", rect.w, rect.h))
    return
  end

  -- Debris scattered irregularly across the whole footprint (it fell from
  -- orbit, not from a single point on the ground) - same "also under YOUR
  -- paths" spirit Soft Ground's cairns use, but denser since this is meant
  -- to read as a genuine reward, not a warning.
  local chunks, steel_piles = 0, 0
  for zz = rect.z, rect.z2 do
    for xx = rect.x, rect.x2 do
      if not ctx:occupied(xx, zz) then
        if rng.chance(0.08) then
          ctx:place("ChunkSlagSteel", xx, zz)
          chunks = chunks + 1
        elseif rng.chance(0.05) then
          ctx:place("Steel", xx, zz)
          steel_piles = steel_piles + 1
        end
      end
    end
  end

  -- Guarantee the reward reads even on the smallest legal footprint.
  if chunks == 0 and steel_piles == 0 then
    local cx = rect.x + math.floor(rect.w / 2)
    local cz = rect.z + math.floor(rect.h / 2)
    if not ctx:occupied(cx, cz) then
      ctx:place("ChunkSlagSteel", cx, cz)
      chunks = 1
    end
  end

  note(string.format(
    "iron rain: %d slag-steel chunks, %d loose steel piles scattered as fallen debris - " ..
    "static aftermath only, no ongoing periodic-fall hazard this pass",
    chunks, steel_piles))
end
