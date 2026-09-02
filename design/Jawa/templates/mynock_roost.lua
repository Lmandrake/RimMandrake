-- mynock_roost.lua - "The Mynock Roost" (structure_injection_roster.md
-- PROMISE #18, RimStarWars tier, Zizzik): a cave-mouth den where mynocks
-- have been gnawing power cable for a season. "power cables are food here" -
-- the roster's own line, matching Mynock's OWN in-stack description
-- ("digest various metals and components for nutritional value",
-- Races_Animal_SW.xml). NEW light per the roster - smallest footprint of
-- this batch, no walls/rooms, no invented "nest" ThingDef.
--
-- SUBSTITUTION NOTE (verified against the on-disk mod XML and vanilla
-- source, not guessed): no dedicated "mynock nest"/"roost comb" ThingDef
-- exists anywhere in the stack (checked mlie.starwarsanimalcollection's
-- own Defs tree). The roost reads through what mynocks leave behind, not an
-- invented prop:
--   PowerConduit (Core, Buildings_Power.xml, category Building, 1x1) -
--     chewed-through cable stubs, placed damaged/dead, not wired into any
--     live power network (this is scenery, not a functioning grid).
--   ChunkSlagSteel (Core) - gnawed metal debris, the same "junk scatter"
--     vocabulary podracer_wreck.lua already uses for mechanical wreckage.
--   Filth_AnimalFilth (Core, category Filth) - the den floor itself.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local conduits, chunks, filth = 0, 0, 0

  for x = rect.x, rect.x2 do
    for z = rect.z, rect.z2 do
      if not ctx:occupied(x, z) then
        -- elseif-chained, not three independent rolls, because only ONE
        -- thing can ever occupy a cell - each branch only gets evaluated
        -- when every prior one already missed. That COMPOUNDS the literal
        -- numbers below into lower actual per-cell rates (code-review
        -- finding, 2026-09-02: read as flat 10/20/40%, the real rates are
        -- 10% / 18% / 28.8% at these values) - editing an EARLIER branch's
        -- chance silently shifts every later one's actual density too, not
        -- just its own. Stated here so that surprise is on paper, not
        -- rediscovered by a future edit.
        if rng.chance(0.10) then
          ctx:place("PowerConduit", x, z)
          conduits = conduits + 1
        elseif rng.chance(0.20) then
          ctx:place("ChunkSlagSteel", x, z)
          chunks = chunks + 1
        elseif rng.chance(0.40) then
          ctx:place("Filth_AnimalFilth", x, z)
          filth = filth + 1
        end
      end
    end
  end

  if conduits == 0 and chunks == 0 then
    -- pathological tiny footprint - guarantee the one prop that actually
    -- carries the roster's "power cables are food here" read.
    local cx = rect.x + math.floor(rect.w / 2)
    local cz = rect.z + math.floor(rect.h / 2)
    ctx:place("PowerConduit", cx, cz)
    conduits = 1
  end

  note(string.format(
    "mynock roost: %d chewed conduit stubs, %d slag chunks, %d filth cells - cave-mouth den, no walls",
    conduits, chunks, filth))
end
