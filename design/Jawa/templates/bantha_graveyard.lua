-- bantha_graveyard.lua - MIN_RECT: none - scatter-only with a center
-- fallback, safe at any rect >=1x1 (see dead_beacon.lua's own header for
-- why this line exists at all).
-- "The Bantha Graveyard" (structure_injection_roster.md
-- PROMISE #15, RimStarWars tier, Oomo): a herd's old bone-ground - horns and
-- hide left behind over many seasons, not a single kill site. "ivory and
-- calm; herds return in season - hunt or shepherd" - the roster's own line
-- reads pastoral, not predatory (unlike krayt_graveyard.lua's single-owner
-- crescent), so this is a loose, scattered field rather than a tight ring
-- around one central skull. Promise structure, no walls/rooms.
--
-- Real defNames verified directly against the on-disk mod XML (this
-- session's defs.sqlite capture is scoped to ResearchProjectDef only, so
-- `rimplace verify` legitimately reports UNMEASURED for ThingDefs right
-- now - same discipline as oasis_shrine.lua/rakatan_trace.lua):
--   BanthaHorn (mlie.starwarsanimalcollection, Items_Resource_swanimal_
--     Items.xml, ParentName="ResourceVerbBase", category Item, stackLimit
--     10) - the "ivory-scatter icon" prop; no dedicated ivory ThingDef is
--     reachable (ProcessIvoryBantha's own <Ivory> product is gated
--     MayRequire="LegendaryMinuteman.SimpleIvory", confirmed NOT active on
--     this mod list - 0 hits in the live ModsConfig.xml), so the raw horn
--     trophy itself is the real, unconditional substitute. Same krayt_
--     graveyard.lua discipline: reuse what exists rather than invent.
--   Leather_Bantha (same mod, ParentName="LeatherBase", category Item) -
--     hide left with the bones, standard leather stack shape.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local horns, hides = 0, 0

  -- ---- loose scatter across the whole footprint --------------------------
  -- no center-of-menace like Krayt's single owner skull - a grazing ground
  -- accumulates bones unevenly over years, thinning toward the footprint
  -- edge so it still reads as a discrete site rather than carpeting the map.
  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)
  local max_r = math.max(1, math.min(math.floor(rect.w / 2), math.floor(rect.h / 2)))

  for x = rect.x, rect.x2 do
    for z = rect.z, rect.z2 do
      if not ctx:occupied(x, z) then
        local d = math.max(math.abs(x - cx), math.abs(z - cz))
        local chance = math.max(0.03, 0.22 - (d / max_r) * 0.16)
        if rng.chance(chance) then
          if rng.chance(0.6) then
            ctx:place("BanthaHorn", x, z)
            horns = horns + 1
          else
            ctx:place("Leather_Bantha", x, z)
            hides = hides + 1
          end
        end
      end
    end
  end

  if horns == 0 and hides == 0 then
    -- pathological tiny footprint - guarantee at least one bone at center
    -- so the site never renders as literally empty ground.
    ctx:place("BanthaHorn", cx, cz)
    horns = 1
  end

  note(string.format(
    "bantha graveyard: %d horns, %d hide stacks scattered across the footprint, no center-of-menace",
    horns, hides))
end
