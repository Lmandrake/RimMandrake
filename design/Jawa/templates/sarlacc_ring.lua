-- sarlacc_ring.lua - "The Sarlacc" (structure_injection_roster.md PROMISE
-- #2, RSW tier): "adopt existing sw_Sarlacc/sw_SarlaccLair + responder
-- polish (warning totems ring the pit)". Declared a GAP-DESIGN in this
-- item's own lint table since 2026-08-31, re-diagnosed 2026-09-18 as a
-- confirmed ENGINE gap, not a design one: the geometry was already MEASURED
-- (vendor/mod_sources/StarWarsAnimalCollection_src/1.6/Defs/ThingDefs_
-- Buildings/SW_Buildings_Natural.xml, read directly: SarlaccPit is a 9x6
-- ThingDef, placed by its own sw_SarlaccPit GenStepDef, order 950, via
-- vanilla GenStep_ScatterThings with countPer10kCellsRange 1~1 -- the pit
-- lands at a mapgen-time-random cell this template's own XML cannot know
-- ahead of time). Old blocker: GenStep_RimplacePlan only supported
-- centerOnMap (map center) or a caller-fixed offsetX/offsetZ -- neither
-- can chase a coordinate a DIFFERENT, independently-scheduled GenStep
-- rolls at runtime.
--
-- Closed this pass: GenStep_RimplacePlan.cs grew a third placement mode,
-- anchorThingDef -- at mapgen time it finds the first live Thing of the
-- named def already on the map (this responder's own GenStepDef order is
-- set to 960 in Defs/GenStepDefs_SarlaccRing.xml, strictly after
-- sw_SarlaccPit's own order 950, per MapGenerator's order-sort of every
-- extraGenSteps entry) and centers THIS plan's footprint on that Thing's
-- OccupiedRect().CenterCell -- not the map center. If no SarlaccPit exists
-- on the map when this GenStep runs, the C# skips the plan entirely rather
-- than mis-centering a ring around nothing.
--
-- Because the anchor is a LIVE Thing found at mapgen time, not a
-- coordinate this template chose, the template's OWN job is simply: given
-- that the real pit sits centered in this plan's own footprint (that is
-- what centering the footprint ON the anchor MEANS), place totems only in
-- the outer margin and never inside the pit's own known 9x6 footprint --
-- guessed nowhere; SarlaccPit's <size> is (9,6) per its own def, read
-- directly above. countPer10kCellsRange 1~1 means exactly one pit per map,
-- so "first Thing found" in the C# is not a fragile assumption.
--
-- "small livestock vanish near edges" (the active predation mechanic the
-- roster names) is NOT built -- same discipline every other static-only
-- promise/whisper row in this program has declared (Dead Beacon's unwired
-- lamp, Rootstock's rain trigger, Choir Wind's mood mechanic, etc.): this
-- is the physical marker only.
--
-- Known limitation, declared not hidden: GenStep_ScatterThings does not
-- randomize a scattered building's rotation by default and none is set on
-- sw_SarlaccPit's own def (checked directly, no <rotation>/<allowRotation>
-- field present) -- SarlaccPit always spawns at its default Rot4.North
-- orientation, so this template's assumed 9x6 (W x H) keep-clear zone
-- matches its real OccupiedRect exactly. If a future SWAC update ever adds
-- scatter rotation to that GenStepDef, this template's keep-clear zone
-- would need re-checking against the new possible 6x9 footprint.
--
-- Real defName (Core, already the shipped precedent every marker-row
-- template in this program uses): SculptureSmall.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

-- 15x12: the pit's own 9x6 footprint plus a uniform 3-cell margin on every
-- side for the totem ring to occupy. `rimplace minrect sarlacc_ring`.
function min_rect(params)
  return 15, 12
end

function build(ctx)
  local W, H = 15, 12
  if rect.w < W or rect.h < H then
    ctx:refuse("footprint", string.format(
      "%dx%d cannot ring a 9x6 anchor with a clear 3-cell margin (needs >=%dx%d)",
      rect.w, rect.h, W, H))
    return
  end

  local x, z = rect.x, rect.z

  -- ---- the anchor's own keep-clear zone: SarlaccPit is 9x6, centered in
  -- this 15x12 footprint by construction (the C# centers THIS plan's
  -- footprint center on the real pit's own center) -- NEVER placed into.
  local pit_w, pit_h = 9, 6
  local pit_x0 = x + math.floor((W - pit_w) / 2)
  local pit_z0 = z + math.floor((H - pit_h) / 2)
  local pit_x1 = pit_x0 + pit_w - 1
  local pit_z1 = pit_z0 + pit_h - 1

  local function in_pit(xx, zz)
    return xx >= pit_x0 and xx <= pit_x1 and zz >= pit_z0 and zz <= pit_z1
  end

  -- ---- warning totems, ringed unevenly through the margin, never inside
  -- the pit's own footprint -- same "jittered scan, not a lattice" idiom
  -- sarlacc_sign.lua/listening_dark.lua already established for a scatter
  -- ring, tuned to this template's larger margin band.
  local placed = 0
  local target = rng.int(6, 9)
  for zz = z, z + H - 1 do
    for xx = x, x + W - 1 do
      if placed < target and not in_pit(xx, zz) and not ctx:occupied(xx, zz) and rng.chance(0.12) then
        ctx:place("SculptureSmall", xx, zz)
        placed = placed + 1
      end
    end
  end

  if placed == 0 then
    ctx:refuse("markers", "no margin cell landed a warning totem")
    return
  end

  note(string.format(
    "sarlacc ring: %d SculptureSmall warning totems scattered through the margin around (never inside) the anchor pit's own 9x6 footprint",
    placed))
end
