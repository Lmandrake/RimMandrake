-- junkers_scrapyard.lua - a Junkers salvage yard: a roofed sorting shed, a
-- forge lean-to, the boss's shack, and between them an open lot of wrecks,
-- junk heaps and slag under a half-finished fence. DISTRICT_TEMPLATE_LIBRARY_1,
-- Junkers district #1 (The Claim Jump manifest slot "scrapyard",
-- src/RimUtinni/AshkarrInhabited/Defs/SettlementManifestDefs/SettlementManifestDefs_TheClaimJump.xml).
--
-- REWORKED 2026-09-05 against the owner's live-review verdict
-- (TILE_STRUCTURE_REVIEW_SAVE_1 - flooring, regular grids, clutter):
--   FLOORING   the shed floor is salvaged steel plate (FLOOR_PLATE), the forge
--              floor iron grating (FLOOR_WORK), the shack rust plating (FLOOR).
--              The lot itself is cleared stony ground with broken-asphalt
--              patches worn in around the buildings - an outdoor yard, not an
--              interior, and the one place bare ground is the honest answer.
--   GRIDS      the shed's stepped shelf row is gone; shelving hugs walls at
--              random slots, and every heap, wreck and chunk in the lot lands
--              by seeded scatter in loose clusters.
--   CLUTTER    real wrecks (a landspeeder hulk, a rusted car), Piled Junk
--              mineables, slag chunks, barrels, crates, a campfire with
--              stools, torches in every room, and a fence nobody finished.
--
-- The old SANDBAG-as-junk-heap stand-in is retired: the palette now carries
-- JUNK_PILE (KOTOR_MineableJunk, an impassable mineable) and WRECK/WRECK_BIG
-- (Core's AncientPodCar - this project's landspeeder reskin - and
-- AncientRustedCar). Security props: NONE, deliberately (searchesLeavers=false).
-- --tech Neolithic: Junkers scavenge, they do not run a grid.

function min_rect(params)
  return 24, 22
end

function build(ctx)
  local w, h = rect.w, rect.h
  if w < 24 or h < 22 then
    ctx:refuse("footprint", string.format(
      "%dx%d too small for a scrapyard (shed 11x8 + forge 8x7 abreast, shack, open lot)", w, h))
    return
  end
  local lot = R(rect.x, rect.z, w, h)

  -- ---- the lot: cleared ground, worn to asphalt in patches -----------------
  floor_worn(ctx, lot, "FLOOR_CHEAP", "FLOOR_YARD", 0.12)

  -- ---- three buildings, each nudged off its anchor so no two yards match ---
  local shed = R(rect.x + 1 + rng.int(0, 1), rect.z2 - 8 - rng.int(0, 1), 11, 8)
  local forge = R(rect.x2 - 8 - rng.int(0, 1), rect.z2 - 7 - rng.int(0, 2), 8, 7)
  local shack = R(rect.x + 1 + rng.int(0, 2), rect.z + 1 + rng.int(0, 1), 6, 6)
  local keep = {}
  for _, b in ipairs({ shed, forge, shack }) do
    keep[#keep + 1] = R(b.x - 2, b.z - 2, b.w + 4, b.h + 4)
    floor_patch(ctx, R(b.x - 1, b.z - 1, b.w + 2, b.h + 2), "FLOOR_YARD", lot)
  end

  -- sorting shed: parts get triaged here before they go anywhere
  do
    local si = shell(ctx, "Storeroom", shed, { floor = "FLOOR_PLATE", doors = { "S" } })
    local shelves = along_wall(ctx, "STORAGE", si, "N", rng.int(2, 3), { gap = 1 })
    shelves = shelves + along_wall(ctx, "STORAGE", si, "W", 1)
    local ok, tx, tz = try_near(ctx, "TABLE", si.x + math.floor(si.w / 2), si.z + 2, 1, 2, si)
    if ok then
      seat_around(ctx, "STOOL", tx, tz, 1, si, 1)
      seat_around(ctx, "CHAIR", tx, tz, 1, si, 1)
    end
    dress(ctx, si, {
      { role = "CRATE",       n = { 2, 4 }, where = "wall" },
      { role = "SHELF_SMALL", n = { 1, 2 }, where = "wall" },
      { role = "SCRAP",       n = { 2, 3 } },
      { role = "BARREL",      n = 1,        where = "corner" },
      { role = "LIGHT",       n = 1,        where = "corner" },
    })
    wall_lights(ctx, si, rng.int(1, 2))
    note(string.format("sorting shed: %d shelving unit(s) against the walls, sorting table with a stool", shelves))
  end

  -- forge lean-to: scrap gets smelted here
  do
    local fi = shell(ctx, "Workshop", forge, { floor = "FLOOR_WORK", doors = { "S" } })
    local forged = along_wall(ctx, "FORGE", fi, "N", 1)
    if forged == 0 then forged = along_wall(ctx, "FORGE", fi, "E", 1) end
    if forged == 0 then note("forge lean-to: the smithy did not fit; room reads as a scrap store") end
    along_wall(ctx, "STORAGE", fi, "W", 1)
    dress(ctx, fi, {
      { role = "BARREL", n = { 1, 2 }, where = "corner" },
      { role = "SCRAP",  n = { 2, 4 } },
      { role = "CRATE",  n = 1,        where = "wall" },
      { role = "STOOL",  n = 1 },
      { role = "LIGHT",  n = 1,        where = "corner" },
    })
    wall_lights(ctx, fi, 1)
  end

  -- the boss's shack: the one cast slot the manifest puts in this district
  do
    local bi = shell(ctx, "Bedroom", shack, { floor = "FLOOR", doors = { rng.pick({ "N", "E" }) } })
    along_wall(ctx, "BED", bi, rng.pick({ "N", "W" }), 1, { face = "wall" })
    dress(ctx, bi, {
      { role = "END_TABLE",   n = 1,        where = "wall" },
      { role = "SHELF_SMALL", n = 1,        where = "wall" },
      { role = "CRATE",       n = { 1, 2 }, where = "corner" },
      { role = "STOOL",       n = 1 },
      { role = "LIGHT",       n = 1,        where = "corner" },
    })
    wall_lights(ctx, bi, 1)
  end

  -- ---- the open lot -------------------------------------------------------
  -- wrecks first (biggest footprints get first pick of the ground)
  local wrecks = 0
  wrecks = wrecks + scatter(ctx, "WRECK_BIG", inner(lot, 2), 1, { keep_clear = keep, rot = "any", tries = 40 })
  wrecks = wrecks + scatter(ctx, "WRECK", inner(lot, 2), rng.int(1, 2), { keep_clear = keep, rot = "any", tries = 40 })

  -- junk heaps in two or three loose clusters, never a spread
  local heaps = 0
  for i = 1, rng.int(2, 3) do
    local cx, cz = rng.int(lot.x + 3, lot.x2 - 3), rng.int(lot.z + 3, lot.z2 - 3)
    heaps = heaps + scatter(ctx, "JUNK_PILE", R(cx - 2, cz - 2, 5, 5), rng.int(2, 4),
      { keep_clear = keep, tries = 40 })
  end
  -- slag everywhere, thin
  local slag = scatter(ctx, "SCRAP", inner(lot, 1), rng.int(8, 12), { keep_clear = keep })
  -- a couple of crates and a barrel left out by the shed
  scatter(ctx, "CRATE", R(shed.x - 2, shed.z - 3, shed.w + 4, 3), rng.int(1, 2))
  scatter(ctx, "BARREL", R(forge.x - 2, forge.z - 3, forge.w + 4, 3), 1)

  -- the fire pit by the shack, stools pulled up to it
  do
    local ok, fx, fz = try_near(ctx, "STOVE", shack.x2 + 4, shack.z + 2, 0, 2, lot)
    if ok then
      floor_patch(ctx, R(fx - 1, fz - 1, 3, 3), "FLOOR_CHEAP", lot)
      local seats = 0
      for _, c in ipairs(shuffle({ { fx - 1, fz - 1, 1 }, { fx + 1, fz - 1, 3 }, { fx - 1, fz + 1, 1 }, { fx + 1, fz + 1, 3 }, { fx, fz - 2, 0 }, { fx, fz + 2, 2 } })) do
        if seats >= rng.int(2, 3) then break end
        if try_place(ctx, "STOOL", c[1], c[2], c[3]) then seats = seats + 1 end
      end
      try_near(ctx, "LIGHT", fx + 3, fz, 0, 2, lot)
    end
  end

  -- a fence nobody finished, along the south edge east of the shack
  if ctx:has_role("FENCE") then
    local fenced = 0
    for x = shack.x2 + 3, lot.x2 - 1 do
      if not rng.chance(0.3) and try_place(ctx, "FENCE", x, lot.z, 0) then fenced = fenced + 1 end
    end
    note(string.format("boundary: %d fence cell(s) with gaps - nobody finished it", fenced))
  end

  note(string.format("open lot: %d wreck(s), %d junk heap(s), %d slag chunk(s)", wrecks, heaps, slag))
  note("no security props placed: Junkers/The Claim Jump is low security by design (searchesLeavers=false)")
end
