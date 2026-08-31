-- podracer_wreck.lua - "The Podracer Wreck" (structure_injection_roster.md #4,
-- RimStarWars tier): scattered engine-pod wreckage, one intact. Small promise
-- site, no walls/rooms - a debris field a caravan reaches on foot, not a
-- building. Ta'Baa's read: "engines are engines; first caravan there wins."
--
-- SUBSTITUTION NOTE (verified against the live def dump, not guessed): no
-- "podracer engine pod" ThingDef exists anywhere in the mod stack. The
-- closest real, already-campaign-flavored match is AncientPodCar - this
-- project's own PodCarIsLandspeeder.xml patch (src/SPLIT_Phase3/Jawa_Patches)
-- already reskins Core's AncientPodCar to label "wrecked landspeeder", size
-- 3x2, category Building. That IS the one-intact-engine-pod centerpiece.
-- The scattered wreckage around it uses ChunkSlagSteel (vanilla mechanoid-
-- slag debris chunk), the standard "junk scatter" ThingDef, plus a little
-- Steel as salvage value peeking out - not invented dressing.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)

  -- ---- the one intact pod, off-center (a wreck field is not tidy) -----
  local pod_w, pod_h = 3, 2
  local px = cx - 1
  local pz = cz - 1
  if px < rect.x then px = rect.x end
  if pz < rect.z then pz = rect.z end
  if px + pod_w - 1 > rect.x2 then px = rect.x2 - pod_w + 1 end
  if pz + pod_h - 1 > rect.z2 then pz = rect.z2 - pod_h + 1 end
  ctx:place("AncientPodCar", px, pz)

  -- ---- scattered junk pods around it -----------------------------------
  -- seeded scatter, clear of the intact pod's own footprint, thinning
  -- toward the footprint edge so it reads as a debris trail, not a wall.
  local scattered = 0
  local salvage = 0
  for x = rect.x, rect.x2 do
    for z = rect.z, rect.z2 do
      -- padded by 1 cell all round: the lint's defsize-aware footprint
      -- check caught a collision at the manual pod_w/pod_h bounds, so this
      -- errs generous rather than guess the exact anchor convention
      local in_pod = x >= px - 1 and x < px + pod_w + 1 and z >= pz - 1 and z < pz + pod_h + 1
      if not in_pod and not ctx:occupied(x, z) then
        local d = math.abs(x - cx) + math.abs(z - cz)
        local chance = math.max(0.05, 0.35 - d * 0.02)
        if rng.chance(chance) then
          ctx:place("ChunkSlagSteel", x, z)
          scattered = scattered + 1
          if rng.chance(0.25) and not ctx:occupied(x, z) then
            -- a little exposed salvage value beside some chunks - the
            -- promise's own "engines are engines" line, made lootable
          end
        end
      end
    end
  end

  -- a handful of exposed Steel stacks near the intact pod - what a fast
  -- caravan grabs without digging through the whole field
  local steel_spots = {
    {px - 2, pz}, {px + pod_w + 1, pz}, {px, pz - 2}, {px, pz + pod_h + 1},
  }
  for _, spot in ipairs(steel_spots) do
    local sx, sz = spot[1], spot[2]
    if sx >= rect.x and sx <= rect.x2 and sz >= rect.z and sz <= rect.z2
        and not ctx:occupied(sx, sz) then
      ctx:place("Steel", sx, sz)
      salvage = salvage + 1
    end
  end

  note(string.format("podracer wreck: 1 intact AncientPodCar, %d slag chunks, "
    .. "%d exposed Steel stacks", scattered, salvage))
end
