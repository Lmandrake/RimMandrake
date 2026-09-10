-- battle_site.lua - "Battle site / mashed settlement" (structure_procedural_
-- spec.md sec 8.12), INHABITED_AUGMENTATION_BUILD_1.
--
-- The spec frames this as a TRANSFORM: "it takes any other archetype's plan
-- (default: 8.1 compound or 8.6 garrison) and damages it." rimplace has no
-- mechanism to load or merge a SECOND template's already-built plan into
-- this one - `require`/`dofile`/`load` are all sandbox-forbidden
-- (luaenv.py's _FORBIDDEN), and `ctx:ruin()` operates on THIS template's own
-- `self.plan`, not an external one. That is also exactly how every existing
-- `state="ruined"` branch already works (homestead.lua, garrison_tiny.lua,
-- road_warehouse.lua, trading_post.lua, moisture_farm_ruined.lua): the
-- template builds its OWN host structure with the ordinary prelude helpers,
-- then calls `ctx:ruin()` on it. battle_site.lua follows that same, only
-- proven, shape - a small garrison/compound-flavoured host built inline,
-- always ruined, always fight-dressed - rather than inventing new engine
-- plumbing under time pressure to satisfy a literal cross-template read of
-- the spec sentence.
--
-- `ctx:ruin(pct, attacker)` ALREADY EXISTS in luaenv.py (Ctx.ruin, "E4: the
-- ruin pass (spec 8.12)") - it was NOT missing, so prelude.lua/luaenv.py are
-- UNTOUCHED by this template. Its own docstring says plainly what it covers
-- and what it defers: steps (1) breach (2) attrition (3) roof-near-breach
-- (4) floor ash (5) furniture rolls (incl. its own `_RUIN_COUSIN` table:
-- Bed->AncientBed, Storage/Shelf_small->AncientShelf, Turret->
-- VFEPD_AncientBrokenTurret, Light->AncientLamp, Crate->AncientCrate,
-- Sandbag->SandbagRubble) are all handled there. Steps (6) the fight, (7)
-- after and (8) time are explicitly left to "whichever archetype pass calls
-- PAWN itself" - this file is that pass.
--
-- Verified real defNames (RimSage `search_defs`, this session's index -
-- caveat every sibling template's header already states: this index is the
-- minimal/prior-load mod set, not the full 599-mod ModsConfig.xml):
--   ChunkMechanoidSlag, SandbagRubble, Filth_MoldyUniform, Filth_BlastMark,
--   Filth_RubbleBuilding, Skullspike, Gun_Autopistol, MeleeWeapon_Knife,
--   PawnKindDef Pirate - all confirmed real ThingDefs/PawnKindDef this pass.
-- NOT indexed this session (VFEPD_* absent from the whole index, same as
-- garrison_tiny.lua's own header found - this session's dump predates that
-- mod being loaded) - substituted or omitted rather than guessed:
--   `VFEPD_FilthBones` - used directly anyway, as mining_site.lua already
--     does (sibling-template precedent, per this item's own dispatch
--     instructions: verify via RimSage OR fall back to a name already used
--     in a sibling template, noting the choice - this is that fallback).
--   `AB_Mech_RuinedTurret_Single` (spec's own droid-turret prop) - appears
--     NOWHERE else in this repo and RimSage returns nothing for it. Rather
--     than guess a defName, this template OMITS it and relies on the
--     structural TURRET placed below getting the SAME VFEPD_AncientBrokenTurret
--     cousin swap every other ruined TURRET already gets, for free, from
--     `ctx:ruin()`'s own `_RUIN_COUSIN` table - already-shipped behaviour,
--     not a new guess.
--
-- params:
--   faction    any Jawa_* / Empire / *Civil faction the palette knows
--              (default "Jawa_IndigenousTribes").
--   techLevel  "Neolithic" (default) | "Industrial"+ - Industrial adds a
--              GENERATOR (loot - it stays) and its battery cell converts
--              straight to ChunkSlagSteel (spec's own "power: conduits cut,
--              generator stays, battery is ChunkSlagSteel").
--   host       "garrison" (default) | "compound" - garrison adds the outer
--              SANDBAG+BARRICADE perimeter ring with a gate (8.6's own
--              vocabulary); compound is the plainer walled house with no
--              ring (8.1's shape). Either way the interior furniture/ruin/
--              fight/after/time passes are identical.
--   pct        fraction of remaining wall cells ctx:ruin() attrites, clamped
--              to the spec's own 0.20-0.40 (default 0.30).
--   attacker   nil | "mech" | "droid" | "hutt" | "tusken" - gates
--              ChunkMechanoidSlag (mech/droid) and Skullspike (hutt/tusken)
--              per spec 8.12 step 6/7.
--   crew       how many defenders came back to bury their own dead, 0-3
--              (default 2) - the GRAVE count.
--
-- Layout convention (this file's own, per prelude.lua's header: 0=north=+z,
-- 2=south=-z): the house sits toward the NORTH (high z) of the lot with its
-- door on the SOUTH wall (low z); the sandbag/gate line sits a few rows
-- south of that door, with a 2-row strip further south still (the lowest z)
-- left OUTSIDE the ring for the 30% of skeletons that "ran" - real bug this
-- pass's own sweep caught: a first draft put the sandbag ring at `lot.z2`
-- (north edge - the far side of the house from its own door, disconnected
-- from the gate/turret/fight-zone entirely) and put "outside the wall"
-- skeletons at `lot.z2 + 1/2`, off the canvas, which silently placed 0
-- pawns there (`ctx:pawn` needs `ctx:in_bounds` true - it does not itself
-- bounds-check). Fixed by putting the ring at `lot.z` (south, same side as
-- the door) and giving it a 2-row margin still inside the lot.
--
-- Designed for --rect 0,0,18,17.

function min_rect(params)
  return 18, 17
end

local function place_near(ctx, def, x, z, radius, role_tag, rot, within)
  rot = rot or 0
  for ring = 0, radius do
    local cells = {}
    for dz = -ring, ring do
      for dx = -ring, ring do
        if math.max(math.abs(dx), math.abs(dz)) == ring then cells[#cells + 1] = { x + dx, z + dz } end
      end
    end
    shuffle(cells)
    for _, c in ipairs(cells) do
      if (within == nil or in_rect(c[1], c[2], within))
         and ctx:can_place(def, c[1], c[2], rot) then
        ctx:place(def, c[1], c[2], rot, nil, role_tag)
        return true, c[1], c[2]
      end
    end
  end
  return false
end

local function filth(ctx, def, x, z)
  return ctx:place(def, x, z, 0, nil, "FILTH", true)
end

-- n items of `def` scattered inside rect r via place_near's spiral search
-- from a fresh random start each time (dead_caravan.lua/mining_site.lua's
-- own "clump" shape) - a plain scatter() can't take a raw defName.
local function clump(ctx, def, role_tag, r, n)
  local got = 0
  for _ = 1, n * 4 do
    if got >= n then break end
    local x, z = rng.int(r.x, r.x2), rng.int(r.z, r.z2)
    if place_near(ctx, def, x, z, 2, role_tag, 0, r) then got = got + 1 end
  end
  return got
end

function build(ctx)
  local p = params
  local lot = R(rect.x, rect.z, rect.w, rect.h)
  local host = p.host or "garrison"
  local tech = p.techLevel or "Neolithic"
  local industrial = (tech == "Industrial" or tech == "Spacer" or tech == "Ultra" or tech == "Archotech")
  local attacker = p.attacker
  local pct = math.max(0.20, math.min(0.40, tonumber(p.pct) or 0.30))
  local crew = math.max(0, math.min(3, tonumber(p.crew) or 2))

  -- ---------------------------------------------------------------------- --
  -- (0) THE HOST - a small walled dwelling toward the north of the lot,
  -- door on its south wall. Stands in for "an already-built 8.1/8.6 plan"
  -- (see header) using the same shell()/dress() vocabulary every archetype
  -- in this folder already builds with.
  -- ---------------------------------------------------------------------- --
  local hw, hh = 10, 8
  local hx, hz = lot.x + math.floor((lot.w - hw) / 2), lot.z2 - hh + 1
  local house = R(hx, hz, hw, hh)
  -- REAL BUG this pass's own sweep caught: the south door's default random
  -- offset (door_on's off-centre pick, house.x+2..house.x+7) can land at
  -- house.x+6/+7, which is exactly the column the armoury nook's own wall
  -- occupies one row further in - the door's interior threshold cell was
  -- THE NOOK'S WALL on ~30% of seeds (23/80 in a faction/tech/attacker/host
  -- sweep), sealing room r1 from its own front door (`aisle-blocked`, every
  -- surviving primary unreached, since the flood-fill never had anywhere to
  -- start). Forcing the door to the WEST end (house.x+2), well clear of the
  -- nook at house.x2-3..house.x2, removes the collision deterministically
  -- rather than narrowing the odds.
  local inr = shell(ctx, "House", house, { floor = "FLOOR", doors = { { "S", 2 } } })

  -- an armoury nook, 3x3 interior, partitioned off the house's own NE
  -- corner. door_on()'s centring formula degenerates to the CORNER cell for
  -- a width-3 room (its "at" range collapses to a single value = r.x2) -
  -- passing an explicit `at` (the true middle column) avoids that rather
  -- than relying on prelude.lua's own formula for a room this narrow.
  local nook = R(house.x2 - 3, house.z + 1, 3, 3)
  ctx:wall_rect(nook.x, nook.z, nook.w, nook.h)
  ctx:floor_rect(nook.x + 1, nook.z + 1, 1, 1, ctx:role("FLOOR"))
  door_on(ctx, nook, "S", 1)

  -- furniture, placed BEFORE ruin() so the furniture-roll pass has
  -- something real to damage/rubble/cousin-swap.
  along_wall(ctx, "BED", inr, "W", 2, { gap = 1 })
  hug(ctx, "STORAGE", inr, "N", { n = 1 })
  dress(ctx, inr, { { role = "TABLE", n = 1, where = "corner" } })
  dress(ctx, nook, { { role = "TOOL_CABINET", n = 1, where = "wall" },
                     { role = "STORAGE", n = 1, where = "wall" } })
  wall_lights(ctx, inr, 1)

  if industrial then
    hug(ctx, "GENERATOR", inr, "E", { n = 1 })
  end

  -- ---------------------------------------------------------------------- --
  -- the gate: SANDBAG+BARRICADE ring on "garrison" hosts (8.6's own
  -- vocabulary, has_role-gated exactly like garrison_tiny.lua so a
  -- faction/tech combination with no SANDBAG role simply contributes
  -- nothing rather than crashing), on the SAME side as the house door - two
  -- rows south of the lot's own south edge, so there is still room outside
  -- the ring for step (7)'s fleeing skeletons.
  -- ---------------------------------------------------------------------- --
  local gate_x = house.x + math.floor(house.w / 2)
  local ring_z = lot.z + 2
  if host == "garrison" and ctx:has_role("SANDBAG") then
    for x = lot.x, lot.x2 do
      if math.abs(x - gate_x) > 1 and not ctx:occupied(x, ring_z) then
        try_place(ctx, "SANDBAG", x, ring_z, 0)
      end
    end
    if ctx:has_role("BARRICADE") then
      place_near(ctx, ctx:role("BARRICADE"), gate_x - 2, ring_z, 1, "BARRICADE", 0, lot)
      place_near(ctx, ctx:role("BARRICADE"), gate_x + 2, ring_z, 1, "BARRICADE", 0, lot)
    end
  end
  -- the gun position: south of the door, between it and the ring, watching
  -- the same approach the ring/gate face (not the far side of the house).
  local turret_def = ctx:has_role("TURRET") and ctx:role("TURRET") or "Turret_MiniTurret"
  local turret_ok, turret_x, turret_z = place_near(ctx, turret_def, gate_x, house.z - 3, 2, "TURRET", 0, lot)

  -- ---------------------------------------------------------------------- --
  -- (1)-(5) breach, attrition, roof-near-breach, floor ash, furniture rolls.
  -- This is the WHOLE of ctx:ruin() - already built, already selftested.
  -- ---------------------------------------------------------------------- --
  local removed = ctx:ruin(pct, attacker)

  -- ---------------------------------------------------------------------- --
  -- (6) THE FIGHT - concentrated between the gate/ring and the house door,
  -- the one zone this template knows the coordinates of (ctx:ruin()'s own
  -- structural breach lands wherever its own RNG stream picked, elsewhere
  -- on the wall - two failure points on one plan is not a defect for a
  -- battle site).
  -- ---------------------------------------------------------------------- --
  local gate_zone = R(math.max(lot.x, gate_x - 3), ring_z, math.min(lot.w, 7), math.max(1, house.z - ring_z))
  local rubble_n = clump(ctx, "SandbagRubble", "SANDBAG", gate_zone, rng.int(2, 4))
  local barricade_n = 0
  do
    local bdef = ctx:role("BARRICADE") or "Barricade"
    for _ = 1, rng.int(2, 4) do
      local ok = place_near(ctx, bdef, gate_x + rng.int(-2, 2), ring_z + rng.int(0, 2), 1, "BARRICADE", 0, lot)
      if ok then barricade_n = barricade_n + 1 end
    end
  end
  local blood_n = clump(ctx, "Filth_Blood", "FILTH", gate_zone, rng.int(4, 8))
  local uniform_n = clump(ctx, "Filth_MoldyUniform", "FILTH", gate_zone, 2)
  local slag_n = 0
  if attacker == "mech" or attacker == "droid" then
    slag_n = clump(ctx, "ChunkMechanoidSlag", "SCRAP", gate_zone, rng.int(2, 5))
  end
  local weapon_n = 0
  for _ = 1, rng.int(0, 2) do
    local wdef = rng.chance(0.5) and "Gun_Autopistol" or "MeleeWeapon_Knife"
    if place_near(ctx, wdef, gate_x + rng.int(-3, 3), ring_z + rng.int(0, 3), 2, "WEAPON", 0, lot) then
      weapon_n = weapon_n + 1
    end
  end

  -- ---------------------------------------------------------------------- --
  -- (7) AFTER - graves dug by whoever came back, trophies on some readings,
  -- and E3 skeletons of whoever did not make it out: 70% at the breach/
  -- inside, 30% outside the ring (they ran) - the 2-row strip south of
  -- `ring_z` that stays inside the lot.
  -- ---------------------------------------------------------------------- --
  local yard = R(lot.x, ring_z + 1, lot.w, math.max(1, house.z - ring_z - 1))
  local graves_n = 0
  if ctx:has_role("GRAVE") then
    for _ = 1, crew do
      local gx, gz = rng.int(yard.x, yard.x2), rng.int(yard.z, yard.z2)
      if try_near(ctx, "GRAVE", gx, gz, rng.int(0, 3), 2, yard) then graves_n = graves_n + 1 end
    end
  end
  local skull_n = 0
  if attacker == "hutt" or attacker == "tusken" then
    for _ = 1, rng.int(1, 2) do
      if place_near(ctx, "Skullspike", gate_x + rng.int(-2, 2), ring_z, 2, "TROPHY", 0, lot) then
        skull_n = skull_n + 1
      end
    end
  end
  -- VFEPD_FilthBones: not indexed this session (see header) - used directly
  -- anyway, same sibling-template fallback mining_site.lua already relies on.
  clump(ctx, "VFEPD_FilthBones", "DECOR", gate_zone, rng.int(1, 2))
  local outside = R(lot.x, lot.z, lot.w, math.max(1, ring_z - lot.z))
  local skel_n = 0
  local skel_total = rng.int(2, 6)
  for _ = 1, skel_total do
    local inside = rng.chance(0.7)
    local sx, sz
    if inside then
      sx, sz = rng.int(gate_zone.x, gate_zone.x2), rng.int(gate_zone.z, gate_zone.z2)
    else
      sx, sz = rng.int(outside.x, outside.x2), rng.int(outside.z, outside.z2)
    end
    if ctx:in_bounds(sx, sz) and ctx:pawn("Pirate", sx, sz, "wild", "skeleton") then
      skel_n = skel_n + 1
    end
  end

  -- ---------------------------------------------------------------------- --
  -- (8) TIME - sand drifts through the gate, the yard path goes soft.
  -- ---------------------------------------------------------------------- --
  for dz = 0, 2 do
    for x = gate_x - 2, gate_x + 2 do
      local sx, sz = x, ring_z + dz
      if ctx:in_bounds(sx, sz) and rng.chance(0.6) and not ctx:occupied(sx, sz) then
        filth(ctx, "Filth_Sand", sx, sz)
      end
    end
  end
  floor_worn(ctx, R(yard.x, yard.z, yard.w, math.min(2, yard.h)), "SoftSand", "PackedDirt", 0.3)

  if industrial and ctx:has_role("GENERATOR") then
    -- the generator stays (loot); its battery cell is scrap.
    place_near(ctx, "ChunkSlagSteel", inr.x2 - 1, inr.z + 1, 2, "SCRAP", 0, inr)
  end

  note(string.format(
    "battle_site(host=%s, attacker=%s): %d wall cell(s) breached/attrited by "
    .. "ctx:ruin, gate fight: %d sandbag rubble, %d barricades, %d blood, "
    .. "%d moldy uniforms, %d mech slag, %d spent weapons, turret placed=%s; "
    .. "after: %d graves, %d skullspikes, %d/%d skeletons",
    host, tostring(attacker), removed, rubble_n, barricade_n, blood_n,
    uniform_n, slag_n, weapon_n, tostring(turret_ok), graves_n, skull_n,
    skel_n, skel_total))
end
