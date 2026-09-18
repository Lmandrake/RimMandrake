-- sarlacc_sign.lua - "The Sarlacc Sign" (structure_injection_roster.md
-- WHISPER #22, RSW, sarlacc-adjacent). Anchor: `sw_SarlaccLair`, the
-- Star Wars Animal Collection (Continued) TileMutatorDef PROMISE #2 (The
-- Sarlacc) already adopts as-is -- confirmed real via a validate_patch.py
-- PatchOperationConditional probe against the live 632-active-mod set (1
-- match, SW_Buildings_Natural.xml). This is a WHISPER, not PROMISE #2's own
-- "responder polish" gap (still open, still declared not-mine-to-fill --
-- see the item file): it rides the SAME anchor mutator but through its own
-- selector GenStepDef, same architecture as Choir Wind riding RUT_Monument
-- alongside PROMISE #8's own responder.
--
-- v1 scope, declared: STATIC content only -- "edge-of-map burrow signs" as
-- a scattered ring of ground markers standing in for burrow openings (no
-- dedicated "burrow hole"/"warning totem" ThingDef exists in the stack;
-- SculptureSmall is reused, the same marker discipline oasis_shrine.lua/
-- rakatan_trace.lua/choir_wind.lua/listening_dark.lua already established
-- -- and the SAME idiom `structure_procedural_spec.md` SS8.11 independently
-- specifies for this exact roster row: "sarlacc = adopt sw_SarlaccLair and
-- ring it with SculptureSmall warning totems x3-5 unevenly (roster #2)" --
-- confirms this is an already-graded design choice, not an invention here).
-- "small livestock vanish near edges" is the active predation mechanic the
-- roster names -- NOT built this pass, same discipline every static-only
-- whisper in this batch used.
--
-- Real defName (Core, already the shipped precedent across this whole
-- program): SculptureSmall.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function min_rect(params)
  return 5, 5   -- needs a real perimeter to ring unevenly
end

function build(ctx)
  if rect.w < 5 or rect.h < 5 then
    ctx:refuse("footprint", string.format(
      "%dx%d too small to ring the footprint edge with burrow signs (needs >=5x5)",
      rect.w, rect.h))
    return
  end

  -- ---- burrow-sign markers scattered unevenly along the footprint edge --
  -- "unevenly" per the spec's own phrasing: a jittered scan of the
  -- perimeter, not a lattice of evenly-spaced stations (R3's own "no
  -- mechanical arrays" rule, followed here even though this template
  -- predates that spec's formal adoption in this item).
  local placed = 0
  local target = rng.int(3, 5)
  for zz = rect.z, rect.z2 do
    for xx = rect.x, rect.x2 do
      local on_edge = xx == rect.x or xx == rect.x2 or zz == rect.z or zz == rect.z2
      if placed < target and on_edge and not ctx:occupied(xx, zz) and rng.chance(0.25) then
        ctx:place("SculptureSmall", xx, zz)
        placed = placed + 1
      end
    end
  end

  if placed == 0 then
    ctx:refuse("markers", "no edge cell landed inside the footprint for a burrow sign")
    return
  end

  note(string.format(
    "sarlacc sign: %d burrow-sign markers unevenly ringing the footprint edge - " ..
    "static only, no edge-predation mechanic this pass", placed))
end
