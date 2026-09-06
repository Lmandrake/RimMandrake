-- boneyard.lua - "The Boneyard" (structure_injection_roster.md, new promise
-- candidate for Deep Desert / ExtremeDesert). Site dressing, not a building -
-- no walls, no rooms, matching krayt_graveyard.lua's idiom.
--
-- THE IMAGE this exists to build - deep_desert.md section 4b, verbatim:
--   "It grows among the true bones of vast creatures that also died out
--    here long ago, and it is nursing the very source of water that might
--    sustain it - the seep, the corpse, the buried moisture. The bones and
--    the tree are one system, not scenery beside each other."
-- One enormous animal died here (decades to centuries ago - nothing decays
-- in this biome, deep_desert.md section 6.2, so what is left is bone, never
-- a mummy), predators/scavengers appraised and drained it at time of death
-- (section 4, "the prize is a full animal, and a dried one is worthless"),
-- and a silverbole later rooted in the moisture its remains still hold.
--
-- ⚠️ DELIBERATELY DIFFERENT FROM structure_injection_roster.md #3 "The Krayt
-- Graveyard" (design/Jawa/templates/krayt_graveyard.lua): that reads as MANY
-- individuals in a loot-bearing crescent (alternating skulls/horns, pearls
-- worth a fortune, Star Wars krayt-dragon flavor). This reads as ONE animal,
-- fallen and staying exactly where it fell - a single 8x4 skeleton anchor
-- with its own skull and tail, never a ring - and every bone prop used here
-- carries MarketValue 0 (verified below): ecological/atmospheric dressing,
-- not a treasure hunt.
--
-- ⚠️ SILVERBOLE_STANDIN - READ BEFORE TOUCHING THE TREE LINE BELOW. No
-- Silverbole/Silverpan TreeDef exists anywhere yet - checked by grepping
-- `silverbole`/`silverpan` (case-insensitive) across src/, design/ and the
-- live def dump; the biome sheet itself says the final name is still
-- owner-to-pick (deep_desert.md, "Owed / ticketed elsewhere"). Stand-in used
-- per this task's option (a): vanilla `TreeDead` - already a LEGAL wild plant
-- IN ExtremeDesert itself (confirmed in the live BiomeDef: commonality 0.04
-- alongside AB_DeadBowerTree and GRimTreeDead), bare/leafless
-- (plant.dropLeaves = false, so it never contradicts "no leaves"), and
-- thermally fine to 77.1C - comfortably past this biome's 29-43C band. It
-- carries NONE of the real silverbole's payoff: no bone-white reflective
-- read, no heat/flame-immune wood stat, no geological growth story. It is a
-- PLACEHOLDER FOR POSITION AND SILHOUETTE ONLY. The moment a real Silverbole
-- TreeDef ships, change the single `TREE = "TreeDead"` line below - nothing
-- else in this file needs to move.
--
-- Bone assets: Alpha Biomes' "ancient Gallatross" fossil set - ThingDefs
-- AB_HugeGallatrossSkeleton (8x4, the whole animal), AB_AncientGallatrossSkull
-- (2x2), AB_AncientBone (2x2), AB_AncientBrokenBone (1x1, a fragment),
-- AB_AncientVerticalBone (1x2, a standing rib/vertebra) and AB_BoneWall (1x1,
-- "giant bones", a loose chunk) - all category Building, all MarketValue 0.
-- Verified against the live def dump (2026-09-05 capture,
-- DefDump/defs.sqlite, 851MB) and against the active mod's own size index
-- (observed/def_sizes.json) for the footprint math below.
-- ⚠️ Alpha Biomes' OWN flavor text calls these bones "fosilized" [sic] -
-- their baked-in description, not reachable from this template - which
-- leans closer to deep_desert.md section 6.3's banned "mineralized/shiny"
-- language than the sheet wants. The geometry and the zero market value are
-- both right for this use; a human should eyeball the ACTUAL rendered
-- sprite for a bone-white/dusty read (not a grey-stone/gem read) before this
-- ships as a promise - a description string cannot be checked from here.
--
-- 🔴 TENANT FLORA REMOVED 2026-09-06, after a live quicktest screenshot
-- (not a def-dump read - this needed LOOKING): AB_EuphorbiaDesiccata is
-- legally an ExtremeDesert plant and its name says "desiccated," but its
-- actual sprite renders as an ordinary solid dark-green cactus - a direct
-- hit on deep_desert.md hard ban #5 ("No green in the open"). The def's own
-- naming cannot be trusted for a visual compliance check, same lesson as
-- the Alpha Biomes bone flavor-text warning above. No pale/bleached desert
-- flora candidate was found to replace it with this pass, so the tenant
-- loop below is disabled rather than shipping a banned green plant -
-- omission over violation, same call the waste_camp.lua fire-basin made.
-- Re-enable TENANT once a genuinely bone-white/dusty plant def is found.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)

  local SKELETON   = "AB_HugeGallatrossSkeleton"  -- 8x4 - the whole animal, one piece
  local SKULL      = "AB_AncientGallatrossSkull"  -- 2x2
  local BONE_A     = "AB_AncientBone"             -- 2x2
  local BONE_B     = "AB_AncientBrokenBone"       -- 1x1, a fragment
  local BONE_C     = "AB_AncientVerticalBone"     -- 1x2, a standing rib/vertebra
  local BONE_CHUNK = "AB_BoneWall"                -- 1x1, "giant bones", a loose chunk
  local TREE       = "TreeDead"                   -- SILVERBOLE_STANDIN - see file header
  local TENANT     = nil                           -- DISABLED 2026-09-06 - renders green, see file header

  -- Below this the 8x4 anchor plus its head/tail run has nowhere legible to
  -- go; a compact bone-and-tree pairing still reads as one animal's remains
  -- rather than cramming the anchor somewhere it collides with its own tail.
  local compact = (rect.w < 14 or rect.h < 6)
  if compact then
    ctx:refuse("BONEYARD_SKELETON", string.format(
      "%dx%d footprint too small for the 8x4 anchor skeleton plus head/tail "
      .. "run - compact bone-and-tree fallback used instead", rect.w, rect.h))
  end

  local anchor, skulls, bones, chunks, trees, tenants = 0, 0, 0, 0, 0, 0

  -- ---- bounding box of everything actually placed, tracked live so the
  -- CLEAR footprint below (BONEYARD_SCATTER_GUARD_1) can cover the real
  -- assembly - the tail/chunk spread is seeded per-render and cannot be
  -- known ahead of placement, so this is measured, never guessed. Approx
  -- (ignores the rotation origin-shift defsize.footprint applies to
  -- even-sized things) is fine here: this only sizes a generous CLEAR
  -- margin, not a collision check - that precision lives in can_place().
  local min_x, max_x, min_z, max_z = nil, nil, nil, nil
  local function expand_bounds(defName, x, z)
    local w, h = ctx:width_of(defName), ctx:height_of(defName)
    local x0 = x - math.floor((w - 1) / 2)
    local z0 = z - math.floor((h - 1) / 2)
    local x1, z1 = x0 + w - 1, z0 + h - 1
    if min_x == nil or x0 < min_x then min_x = x0 end
    if max_x == nil or x1 > max_x then max_x = x1 end
    if min_z == nil or z0 < min_z then min_z = z0 end
    if max_z == nil or z1 > max_z then max_z = z1 end
  end

  if not compact then
    -- ---- the one animal ---------------------------------------------------
    -- "what died here is still lying where it fell" (deep_desert.md section
    -- 1) - a single fossil skeleton dropped at the footprint's own center,
    -- never scattered like a graveyard of many.
    if ctx:can_place(SKELETON, cx, cz) then
      anchor = 1
      ctx:place(SKELETON, cx, cz)
      expand_bounds(SKELETON, cx, cz)

      -- Footprint math for an 8x4 Building at rot 0 (both dims even, so the
      -- rotation shift at rot 0 is (0,0) - rimplace.defsize.footprint):
      -- x0 = cx - (8-1)//2 = cx-3, spanning cx-3 .. cx+4. z is symmetric
      -- (cz-1 .. cz+2). Computed here, not guessed, because the tail/skull
      -- placements below must sit flush against these edges, not overlap
      -- them.
      local skel_west, skel_east = cx - 3, cx + 4

      -- head end vs tail end: seeded per-tile variety (same seed, same
      -- animal), never per-render noise - but the skull needs ~4 clear
      -- cells past whichever edge it lands on (1-cell neck bone + 2-wide
      -- skull, BOTH now flush against each other and against the ribcage,
      -- see below, +1 margin), and a narrow rect (the CLI's own 16x12
      -- default among them) does not always have that on BOTH sides. Pick
      -- whichever side actually has room; only randomize between the two
      -- when both do, so this never quietly loses the skull the way a
      -- fixed side would.
      local SKULL_ROOM = 4
      local room_west, room_east = skel_west - rect.x, rect.x2 - skel_east
      local head_dir
      if room_west >= SKULL_ROOM and room_east >= SKULL_ROOM then
        head_dir = rng.chance(0.5) and 1 or -1
      elseif room_west >= SKULL_ROOM then
        head_dir = -1
      elseif room_east >= SKULL_ROOM then
        head_dir = 1
      else
        -- neither side has full room - use whichever is less bad; can_place
        -- below still refuses cleanly if the skull truly does not fit.
        head_dir = (room_west >= room_east) and -1 or 1
      end
      local head_edge = (head_dir < 0) and skel_west or skel_east
      local tail_edge = (head_dir < 0) and skel_east or skel_west
      local tail_dir = -head_dir

      -- ---- the skull, flush against the ribcage - BONEYARD_TWO_SKULLS_1 --
      -- Was: neck bone 2 cells past the edge, skull 5 cells past the edge -
      -- a 3-4 cell OPEN gap that read as a second, disconnected skull/animal
      -- (owner, looking at a live screenshot; see the skill's §6 worked
      -- example). A real skeleton's skull sits AT its spine: the neck bone
      -- now touches the ribcage's own edge (zero gap) and the skull touches
      -- the neck bone (zero gap) - one continuous chain, not three floating
      -- pieces. defsize.footprint's rot-0 origin always extends toward +x,
      -- regardless of which way head_dir points, so the skull's offset
      -- (unlike the neck bone's, which is 1-wide and symmetric) cannot use
      -- the same head_dir multiplier on both sides without overlapping the
      -- neck bone - hence the explicit branch below.
      local neck_x = head_edge + head_dir       -- touches the ribcage edge
      if ctx:can_place(BONE_C, neck_x, cz) then
        ctx:place(BONE_C, neck_x, cz)
        expand_bounds(BONE_C, neck_x, cz)
        bones = bones + 1
      end
      local skull_x
      if head_dir > 0 then
        skull_x = neck_x + 1                    -- skull's near edge touches the neck bone
      else
        skull_x = neck_x - 2                    -- skull is 2-wide and its footprint always
                                                  -- extends toward +x, so its FAR edge must
                                                  -- land one cell short of the neck bone
      end
      if ctx:can_place(SKULL, skull_x, cz) then
        ctx:place(SKULL, skull_x, cz)
        expand_bounds(SKULL, skull_x, cz)
        skulls = skulls + 1
      else
        ctx:refuse(SKULL, "no room for the skull at the ribcage's head end")
      end

      -- ---- the tail: vertebrae tapering to broken fragments at the tip --
      -- the SAME animal's tail, never a second creature's remains.
      local n_tail = 5
      for i = 1, n_tail do
        local tx = tail_edge + tail_dir * (2 * i)
        local tz = cz + rng.int(-1, 1)
        -- the last two read as fragments only - the tip thinning out.
        local def = (i <= n_tail - 2) and BONE_C or BONE_B
        if ctx:can_place(def, tx, tz) then
          ctx:place(def, tx, tz)
          expand_bounds(def, tx, tz)
          bones = bones + 1
        end
      end

      -- ---- loose chunks: ribs that broke off and settled nearby, still
      -- this one animal, never implying a second body ---------------------
      for i = 1, 4 do
        local ang = rng.int(0, 359) * math.pi / 180
        local r = rng.int(3, 5)
        local bx = cx + math.floor(r * math.cos(ang) + 0.5)
        local bz = cz + math.floor(r * math.sin(ang) + 0.5)
        if ctx:can_place(BONE_CHUNK, bx, bz) then
          ctx:place(BONE_CHUNK, bx, bz)
          expand_bounds(BONE_CHUNK, bx, bz)
          chunks = chunks + 1
        end
      end
    else
      ctx:refuse(SKELETON, "center cell already occupied")
      compact = true
    end
  end

  if compact then
    -- ---- compact fallback: no room for the full skeleton, still one
    -- animal's remains, not a graveyard --------------------------------
    if ctx:can_place(SKULL, cx, cz) then
      ctx:place(SKULL, cx, cz)
      expand_bounds(SKULL, cx, cz)
      skulls = skulls + 1
    end
    for _, off in ipairs({ { -2, 0 }, { 2, 0 }, { 0, -2 }, { 0, 2 } }) do
      local bx, bz = cx + off[1], cz + off[2]
      if ctx:can_place(BONE_A, bx, bz) then
        ctx:place(BONE_A, bx, bz)
        expand_bounds(BONE_A, bx, bz)
        bones = bones + 1
      end
    end
  end

  -- ---- the silverbole (standin): rooted immediately against the ribcage,
  -- where the seep and the buried moisture would pool. deep_desert.md 4b:
  -- "The bones and the tree are one system, not scenery beside each other."
  -- Placed ADJACENT to the skeleton's edge, never overlapping it - RimWorld
  -- has no way to grow a plant through a building's own footprint, so
  -- "rooted in the remains" reads as touching them, not passing through.
  local tree_z = cz + (compact and 2 or 3)
  if ctx:can_place(TREE, cx, tree_z) then
    ctx:place(TREE, cx, tree_z)
    expand_bounds(TREE, cx, tree_z)
    trees = trees + 1

    -- ---- tenants: small desert life paying rent in the one patch of shade
    -- this whole footprint has (4b: "its shade is rented ... a small
    -- ecosystem standing alone in open ground") -------------------------
    -- DISABLED 2026-09-06 - see TENANT above and the file header note.
    if TENANT then
      for _, off in ipairs({ { 1, 0 }, { -1, 0 }, { 0, 1 } }) do
        local px, pz = cx + off[1], tree_z + off[2]
        if ctx:can_place(TENANT, px, pz) then
          ctx:place(TENANT, px, pz)
          tenants = tenants + 1
        end
      end
    end
  else
    ctx:refuse(TREE, "no room beside the ribcage for the silverbole-standin tree")
  end

  -- ---- CLEAR a margin beyond the assembly's own bounding box, not just its
  -- footprint - BONEYARD_SCATTER_GUARD_1. A live screenshot showed a second,
  -- unrelated skull-shaped object sitting near this site: ambient map
  -- scatter this template never placed, but which read as part of the scene
  -- because nothing controlled the ground around the bones. This site now
  -- clears MARGIN cells past whatever it actually built (tracked live above
  -- via expand_bounds, since the tail/chunk spread is seeded per-render) so
  -- stray plants/filth/items from the wider map do not land inside the
  -- frame a viewer will screenshot. "soft" mode only - this is a bone field
  -- on open desert ground, not a mined excavation, so any natural mineable
  -- rock nearby is left standing rather than replaced with rough-rock
  -- terrain. CLEAR always executes before THING placement at mapgen time
  -- (GenStep_RimplacePlan's fixed step order), regardless of Lua call
  -- order, so clearing this same ground the tree/bones just landed on does
  -- not un-place them.
  if min_x then
    local MARGIN = 3
    local cx0 = math.max(rect.x, min_x - MARGIN)
    local cz0 = math.max(rect.z, min_z - MARGIN)
    local cx1 = math.min(rect.x2, max_x + MARGIN)
    local cz1 = math.min(rect.z2, max_z + MARGIN)
    ctx:clear(cx0, cz0, cx1 - cx0 + 1, cz1 - cz0 + 1, "soft")
  end

  note(string.format(
    "boneyard: %s%d anchor skeleton(s) (8x4), %d skull(s), %d bone piece(s), "
    .. "%d loose chunk(s), %d tree(s) [SILVERBOLE_STANDIN=TreeDead pending "
    .. "the real def], %d shade tenant(s)",
    compact and "COMPACT FALLBACK - " or "", anchor, skulls, bones, chunks,
    trees, tenants))
end
