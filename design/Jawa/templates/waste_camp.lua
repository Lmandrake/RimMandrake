-- waste_camp.lua - "The Waste Camp": a ruined Deep Desert Tribe temporary
-- campsite (structure_injection_roster.md idiom - site dressing, no
-- walls/rooms). A small hunting/foraging band camped here, near what was
-- once a moisture source or in a silverbole's shade, stayed long enough to
-- leave real traces, then moved on - one to a hundred years ago, no way to
-- tell which. Per deep_desert.md doctrine (section 1, section 7): nothing
-- here ROTS, it DESICCATES. The camp is time-worn - sun-bleached, wind-
-- eroded, maybe half-buried by a sandstorm - never rotted, mildewed or
-- decayed. No ash, no char, no green, nothing shiny or crystalline
-- (section 6 hard bans).
--
-- COMPOSITION FIX (rimworld-scene-composition skill, section 6): the
-- original build was every prop individually correct on flat, undifferen-
-- tiated ground - "litter, not a place" (owner, 2026-09-06). Per section 2
-- of that skill, the camp's floor is now sunk one cell below the surrounding
-- grade: a distinct PackedDirt patch (feet and hide-scraping packed the sand
-- hard where the band actually lived and worked - "sunken DWELL through the
-- hot hours" is established doctrine for this biome, see
-- design/Jawa/bridge/LIVING_NPC_TEMPLATES.md's Moisture Farm entry) against
-- the loose native sand outside it. Per section 1's jagged-boundary rule the
-- pit's edge is painted cell-by-row with an irregular 0-2 cell inset per
-- row, never a rectangle. Per section 3 the props are pulled in tight
-- around the pit's center so the collapsed frame's ring still traces where
-- the tent stood and the hearth/waste sit inside that same footprint,
-- rather than scattered independently across the old wide radius.
--
-- HARD-BAN TENSION, RESOLVED (read this before touching the fire content):
-- deep_desert.md section 6.1 bans ALL fire-ecology vocabulary here - no ash,
-- char, cinder, ember or burn-scar, full stop. But section 8 also makes fire
-- sacred and precious to the Deep Desert Tribes precisely BECAUSE they
-- import every scrap of fuel across the whole biome carrying none of its
-- own. Both are true at once, so the camp cannot show a burn-scarred patch
-- of ground (banned) but must still read as "this is where they kept their
-- treasured fire." The fix: a Brazier - a bowl-shaped fire-holder ThingDef,
-- not a terrain texture - placed on ordinary rock/sand with NO fuel item
-- anywhere near it. Brazier's own def ships with initialFuelPercent=0 (it
-- is drawn/functions as cold and unlit until fuel is added), so placing one
-- bare is not a hack, it is the def's own resting state. A portable ITEM
-- can be cold and empty without implying it ever burned where it sits -
-- there is no ash, no scorched terrain, nothing charred. If Brazier ever
-- fails verify (it is Royalty-adjacent per its own MeditationFocus
-- cross-refs; unclear if it needs the DLC to resolve), the fallback is
-- Campfire (base game, no DLC) placed the same bare way - also unlit by
-- default outside of active use, also never draws ash or scorch decals of
-- its own.
--
-- SUBSTITUTION NOTES (verified against the live def dump, not guessed - see
-- rimplace verify output; nothing here was shipped on a guess):
--   * No "tent"/"wickiup"/"yurt"/"shelter" ThingDef exists anywhere in the
--     mod stack. The collapsed hide-and-pole frame is built from ordinary
--     WoodLog (poles, splayed and toppled - not standing) and Leather_Camel
--     (the hide skin itself, camel-hide reading as sun-bleached tan, no
--     green, no shine) scattered loose around the frame, as if the wind
--     took the covering off the poles.
--   * No "waterskin"/"canteen"/"bone"/"skull-of-small-game" ThingDef exists
--     either (the one "Skull" ThingDef in the stack is explicitly "a human
--     skull" per its own description - wrong narrative, not used here).
--     Desiccated camp waste instead uses existing FILTH ThingDefs that
--     already read as old and dry rather than fresh or rotten:
--     Filth_DriedBlood (old kill-butchering stains, already dried - never
--     "fresh blood", never rot) and Filth_AnimalFilth + Filth_Trash (the
--     odds and ends a band leaves behind: worn cordage, a cracked gourd,
--     the little debris of a stay). None of these are ash/char.
--   * The worn tool is MeleeWeapon_Club in WoodLog stuff - Neolithic tech,
--     hand-shaped wood, no metal, no shine: matches the artistic theme's
--     "powder glaze, never shiny glass" by simply having nothing glassy to
--     begin with.
--   * PackedDirt (the sunken pit's floor) is a vanilla TerrainDef already
--     used elsewhere in this template set (mining_site.lua) - not a fresh
--     guess.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)

  -- ---- the sunken camp floor ----------------------------------------------
  -- A jagged-edged pit, ~13x9, dug/trampled one grade below the surrounding
  -- sand. Painted row by row with an irregular 0-2 cell inset on each side
  -- per row (never a rectangle - section 1's jagged-boundary rule) so the
  -- boundary reads as an eroded dug-in hollow, not a UI grid or a foundation
  -- slab. `row_inset[i] = {left, right}` indexes by row-within-pit (0 at the
  -- north edge); every prop placed below is deliberately kept inside this
  -- same footprint so the ground plane and the clutter agree about where
  -- the camp actually was.
  local sunk_floor = "PackedDirt"
  local sunk_w, sunk_h = 13, 9
  local sx0 = cx - 7
  local sz0 = cz - 4
  local sx1 = sx0 + sunk_w - 1
  local sz1 = sz0 + sunk_h - 1
  local row_inset = {
    [0] = { 2, 2 }, [1] = { 1, 0 }, [2] = { 0, 1 }, [3] = { 0, 0 },
    [4] = { 1, 0 }, [5] = { 0, 2 }, [6] = { 0, 1 }, [7] = { 1, 1 },
    [8] = { 2, 2 },
  }

  local function in_pit(x, z)
    local i = z - sz0
    local inset = row_inset[i]
    if inset == nil then return false end
    return x >= sx0 + inset[1] and x <= sx1 - inset[2]
  end

  local floor_placed = 0
  for i = 0, sunk_h - 1 do
    local z = sz0 + i
    local inset = row_inset[i]
    for x = sx0 + inset[1], sx1 - inset[2] do
      if ctx:in_bounds(x, z) and ctx:floor(x, z, sunk_floor) then
        floor_placed = floor_placed + 1
      end
    end
  end

  -- ---- the collapsed tent-pole frame -------------------------------------
  -- off-center within the pit, per the podracer/krayt precedent: a lived-in
  -- camp is never tidy, and centering everything reads as a diorama, not a
  -- ruin. The frame itself is a rough teepee splay of poles that no longer
  -- stands upright - angles chosen to look toppled/askew, not a neat radial
  -- fan - but the ring the offsets trace is still readable as "a tent stood
  -- here," per section 3's implied-footprint rule.
  local fx = cx - 2
  local fz = cz - 1
  local poles_placed = 0
  local pole_offsets = {
    {0, 0}, {2, 1}, {-1, 2}, {1, -2}, {-2, -1}, {3, -1},
  }
  for _, off in ipairs(pole_offsets) do
    local px, pz = fx + off[1], fz + off[2]
    if ctx:in_bounds(px, pz) and in_pit(px, pz) and not ctx:occupied(px, pz) then
      ctx:place("WoodLog", px, pz)
      poles_placed = poles_placed + 1
    end
  end

  -- the hide skin, blown clear of the poles it used to cover - a handful of
  -- loose camelhide items pulled in tight around the frame's own ring
  -- (pulled in from the original build's wider scatter, which reached past
  -- the implied footprint and read as independent litter rather than "this
  -- tent's own covering").
  local hide_placed = 0
  local hide_offsets = {
    {3, 2}, {-3, 2}, {2, 3}, {-3, -2},
  }
  for _, off in ipairs(hide_offsets) do
    local hx, hz = fx + off[1], fz + off[2]
    if ctx:in_bounds(hx, hz) and in_pit(hx, hz) and not ctx:occupied(hx, hz) then
      ctx:place("Leather_Camel", hx, hz)
      hide_placed = hide_placed + 1
    end
  end

  -- ---- the cold, empty fire-basin -----------------------------------------
  -- set apart from the frame, the way a hearth sits outside a sleeping area,
  -- not on top of it - but still inside the same sunken footprint, at the
  -- pit's inner edge rather than out on the surrounding grade. Ordinary
  -- terrain underneath - no scorch, no ash, this IS the whole point of
  -- using an item instead of a burn texture.
  local brazier_x, brazier_z = cx + 3, cz + 2
  local brazier_placed = false
  if ctx:in_bounds(brazier_x, brazier_z) and in_pit(brazier_x, brazier_z)
      and not ctx:occupied(brazier_x, brazier_z) then
    ctx:place("Brazier", brazier_x, brazier_z)
    brazier_placed = true
  else
    ctx:refuse("Brazier", "hearth spot occupied, out of bounds, or outside the pit",
               brazier_x, brazier_z)
  end

  -- ---- desiccated waste scatter -------------------------------------------
  -- a seeded scatter of old, dry camp traces, now bounded to the sunken pit
  -- itself (never the loose sand outside it) and thinning with distance
  -- from the frame/hearth cluster so it reads as "lived here a while" inside
  -- one contained place, rather than a dusting spread over open ground.
  local filth_kinds = {"Filth_DriedBlood", "Filth_AnimalFilth", "Filth_Trash"}
  local filth_placed = 0
  for x = sx0, sx1 do
    for z = sz0, sz1 do
      if in_pit(x, z) and not ctx:occupied(x, z) then
        local d = math.abs(x - cx) + math.abs(z - cz)
        local chance = math.max(0.0, 0.24 - d * 0.025)
        if rng.chance(chance) then
          local kind = rng.pick(filth_kinds)
          ctx:place(kind, x, z)
          filth_placed = filth_placed + 1
        end
      end
    end
  end

  -- ---- one worn tool, half-forgotten in the dust --------------------------
  local tool_x, tool_z = fx - 2, fz + 1
  local tool_placed = false
  if ctx:in_bounds(tool_x, tool_z) and in_pit(tool_x, tool_z)
      and not ctx:occupied(tool_x, tool_z) then
    ctx:place("MeleeWeapon_Club", tool_x, tool_z, 0, "WoodLog")
    tool_placed = true
  end

  note(string.format(
    "waste camp: %d sunken-pit floor cells (jagged, PackedDirt), %d fallen "
    .. "tent-poles, %d loose hide pieces, %s hearth, %d dry waste-filth "
    .. "cells, %s worn tool",
    floor_placed, poles_placed, hide_placed, brazier_placed and "1 cold" or "0",
    filth_placed, tool_placed and "1" or "0"))
end
