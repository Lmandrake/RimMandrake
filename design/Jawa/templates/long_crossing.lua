-- long_crossing.lua - "The Long Crossing" (structure_injection_roster.md,
-- deep-desert band, extends #4 The Podracer Wreck's family but a DIFFERENT
-- story - a droid-crewed ground crawler, not a racing pod): deep_desert.md
-- §4's campaign-defining fact is that a droid carries no water, so nothing
-- under the sand will spend a strike on it - a Jawa clan that fields droids
-- can cross ground nothing alive can cross. This crawler was exploiting
-- exactly that when its ENGINE failed, not its hull - nothing hunted it,
-- nothing burned it, nothing rotted it. It just stopped, and has been
-- sitting inert and unmolested by anything alive ever since. What emptied
-- it was years of Jawa and Deep Desert Tribe scavengers walking off with
-- everything that unbolted. Small promise site, no walls/rooms - a debris
-- field a caravan reaches on foot, matching podracer_wreck.lua's idiom.
--
-- SUBSTITUTION NOTE (verified against the live def dump, not guessed): no
-- "sandcrawler"/"ground crawler"/"skimmer" ThingDef exists anywhere in the
-- mod stack. AncientPodCar (the Podracer Wreck's own centerpiece) is a
-- FLYING pod and was rejected on purpose to keep the two sites visually
-- distinct. The closest real match for a stranded GROUND vehicle is
-- AncientIndustrialTruck ("An industrial truck, heavily rusted and
-- abandoned. The engine is beyond repair." - vanilla Ancient/Shipping set),
-- size (2,4), Flammability 0 (the biome's hard ban on fire content is
-- satisfied by construction, not by luck), killedLeavings ChunkSlagSteel x3.
-- Its own flavour text already says "the engine is beyond repair" - the
-- mechanical breakdown this site is built around - so the site needed no
-- invented damage-cause text of its own.
--
-- Scattered debris reuses ChunkSlagSteel (the standard scrap-chunk ThingDef,
-- also this hull's own killedLeavings type - not invented dressing), kept
-- SPARSE: most of what could be carried off already was, over "anywhere
-- from a handful of years to a century" per the brief.
--
-- Sand accretion: ctx:floor paints SoftSand (verified TerrainDef, vanilla)
-- on the leeward side, thinning with distance - the dune building up
-- against a fixed obstacle that deep_desert.md §9 calls out as one of the
-- map's few permanent, hard-edged shade shapes.
--
-- The shade-ecosystem hint (deep_desert.md §8: "where debris falls it makes
-- shade, and shade makes a small living biome right beside it... these are
-- the treasured sites of the deep desert"): ONE Iguana (vanilla PawnKindDef,
-- desert-neutral, no campaign baggage) spawned via ctx:pawn in the
-- state="dessicated" (engine's spelling, not "desiccated") state, sitting
-- in the sand patch in the hull's shadow. Not a population, not a food web -
-- deep_desert.md §4 is explicit that nothing rots here, it desiccates, so a
-- single sun-dried lizard that wandered into the one patch of permanent
-- shade for hundreds of tiles and never found enough there to leave again
-- IS the "just beginning to form" beat, not a shortcut around it. No living
-- plant/animal was used, and nothing green: both would cross deep_desert.md
-- §6's hard bans (no green in the open, no abundant shade/structure) for a
-- site whose entire point is that shade here is rare and this is the whole
-- of it.
--
-- Footprint exclusion for the hull uses the same generous hand-padded box
-- podracer_wreck.lua does (comment there: "the lint's defsize-aware
-- footprint check caught a collision at the manual bounds, so this errs
-- generous rather than guess the exact anchor convention") - rot is left at
-- 0 (the engine default) rather than rotated, so no rotation-origin-shift
-- math is needed on top of that same uncertainty.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)

  -- ---- the hull, stalled mid-crossing ------------------------------------
  local hull = "AncientIndustrialTruck"
  local hull_w, hull_h = 2, 4
  local hx = cx - 1
  local hz = cz - 2
  if hx < rect.x then hx = rect.x end
  if hz < rect.z then hz = rect.z end
  if hx + hull_w - 1 > rect.x2 then hx = rect.x2 - hull_w + 1 end
  if hz + hull_h - 1 > rect.z2 then hz = rect.z2 - hull_h + 1 end
  ctx:place(hull, hx, hz)

  local function in_hull(x, z)
    return x >= hx - 1 and x < hx + hull_w + 1 and z >= hz - 1 and z < hz + hull_h + 1
  end

  -- ---- leeward sand accretion: one direction, tapering with distance ----
  -- The wind is fixed campaign-wide (deep_desert.md §9's yardang grain);
  -- this template just needs ONE consistent side, so it picks the map's own
  -- +x edge as "downwind" rather than guess a numeric wind-angle constant
  -- nothing in the ctx API exposes. A reviewer who knows the real bearing
  -- can flip this later without touching anything else in the file.
  local drift_cells = 0
  local trailing_x = hx + hull_w  -- the hull's downwind edge
  for x = rect.x, rect.x2 do
    for z = rect.z, rect.z2 do
      if not in_hull(x, z) then
        local d = x - trailing_x
        if d >= 0 then
          local chance = math.max(0, 0.65 - d * 0.12)
          if rng.chance(chance) then
            ctx:floor(x, z, "SoftSand")
            drift_cells = drift_cells + 1
          end
        end
      end
    end
  end

  -- ---- scattered stripped debris: sparse, not a field --------------------
  -- Decades of scavengers already carried off everything that unbolted, so
  -- this reads as leftovers too small or too broken to be worth a trip, not
  -- a supply field like the Podracer Wreck's denser scatter.
  local scattered = 0
  for x = rect.x, rect.x2 do
    for z = rect.z, rect.z2 do
      if not in_hull(x, z) and not ctx:occupied(x, z) then
        local d = math.abs(x - cx) + math.abs(z - cz)
        local chance = math.max(0.0, 0.10 - d * 0.008)
        if rng.chance(chance) then
          ctx:place("ChunkSlagSteel", x, z)
          scattered = scattered + 1
        end
      end
    end
  end

  -- ---- the one tenant the shade has attracted so far ---------------------
  -- Placed just past the hull's padded footprint on its leeward side, inside
  -- the sand patch - it is here BECAUSE of the shade, and it is alone
  -- because the shade is new.
  local tx = hx + hull_w + 1
  local tz = hz + 1
  if tx > rect.x2 then tx = rect.x2 end
  if tz > rect.z2 then tz = rect.z2 end
  ctx:pawn("Iguana", tx, tz, "wild", "dessicated")

  note(string.format(
    "the long crossing: 1 stalled AncientIndustrialTruck (engine failure, "
    .. "never touched by anything alive), %d ChunkSlagSteel leftovers too "
    .. "small to have been worth carrying off, %d SoftSand cells drifted "
    .. "against its leeward side, 1 dessicated Iguana - the shade's first "
    .. "and so-far only tenant", scattered, drift_cells))
end
