-- dead_beacon.lua - MIN_RECT: 5x5 (below this, ctx:refuse fires, tested and
-- correct - see design/Jawa/worldbuilding/structure_injection_roster.md's
-- own TILE_STRUCTURE_REVIEW_SAVE_1 finding: nothing else records this, so
-- whoever exports/wires this template must respect this number by hand).
-- "The Dead Beacon" (structure_injection_roster.md
-- PROMISE #14, RimUtinni tier, Ishko vs Sh'kaar): a small lamp-room, cold
-- and unpowered. "light the dark and see what answers" - "relighting it is
-- a CHOICE" per the roster's own line: this template deliberately does NOT
-- wire the lamp to power (no battery/generator/conduit placed) - it stays
-- dark until a FUTURE player action (running their own power to it) lights
-- it, which is the mechanical shape "a choice" actually has in RimWorld's
-- own vocabulary. No verticality in this engine, so "tower" reads as a
-- small single-room lamp-house rather than a literal multi-story structure -
-- same 2D abstraction hunting_lodge.lua/toll_gap.lua already accepted for
-- "lodge"/"toll house".
--
-- Real defNames verified against vanilla source (RimSage-indexed):
--   StandingLamp (Core, category Building) - the beacon lamp itself,
--     placed but never wired to a power source, so it is genuinely COLD,
--     not just re-skinned as dark.
--   Wall / Door (Core) - the lamp-room shell, same shipped precedent
--     rakatan_trace.lua/toll_gap.lua already use.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local W, H = 5, 5
  if rect.w < W or rect.h < H then
    ctx:refuse("footprint", string.format(
      "%dx%d cannot hold a %dx%d lamp-room", rect.w, rect.h, W, H))
    return
  end

  local x, z = rect.x, rect.z

  -- ---- the lamp-room shell ----------------------------------------------
  ctx:room("Storeroom", x, z, W, H, true)
  ctx:wall_rect(x, z, W, H)
  ctx:door(x + math.floor(W / 2), z)

  -- ---- the cold beacon, centered, unwired --------------------------------
  local cx = x + math.floor(W / 2)
  local cz = z + math.floor(H / 2)
  ctx:place("StandingLamp", cx, cz)

  note("dead beacon: one lamp-room, StandingLamp centered and deliberately unwired - stays dark until a future player choice powers it")
end
