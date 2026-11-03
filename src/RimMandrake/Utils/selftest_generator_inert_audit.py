#!/usr/bin/env python3
"""selftest_generator_inert_audit.py -- the IL walker and the creation-only classifier, on synthetic input.

No DLL, save or game is read: the walker must step every operand width exactly, or every token after a
mis-stepped opcode is garbage and the audit silently loses (or invents) a Harmony target.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generator_inert_audit as g  # noqa: E402

FAILS = []


def check(cond, what):
    if not cond:
        FAILS.append(what)
        print("FAIL", what)


def tok(t):
    return struct.pack("<I", t)


# ldc.i8 (8) ; ldarg.s (1) ; switch 2 targets ; FE0C ldloc (2) ; ldtoken TypeRef 1 ; ldstr ; call ; ret
code = (b"\x21" + b"\0" * 8 + b"\x0e\x01" + b"\x45" + struct.pack("<I", 2) + b"\0" * 8 + b"\xfe\x0c\x01\x00"
        + b"\xd0" + tok(0x01000001) + b"\x72" + tok(0x70000005) + b"\x28" + tok(0x0A000003) + b"\x2a")
ins = list(g.il_instructions(code))
ops = [op for op, _t in ins]
check(ops == [0x21, 0x0E, 0x45, 0xFE0C, 0xD0, 0x72, 0x28, 0x2A], "opcode stream %r" % ops)
check(ins[4][1] == 0x01000001 and ins[5][1] == 0x70000005 and ins[6][1] == 0x0A000003, "tokens %r" % ins[4:7])
check(ins[0][1] is None and ins[1][1] is None, "8- and 1-byte operands carry no token")

# every 4-byte single-byte opcode steps 4, every short branch 1
for op in sorted(g._OP4):
    check(g._operand_size(op, b"\0" * 8, 0) == 4, "op %02x is 4 bytes" % op)
for op in range(0x2B, 0x38):
    check(g._operand_size(op, b"\0", 0) == 1, "short branch %02x is 1 byte" % op)
check(g._operand_size(0x2A, b"", 0) == 0, "ret has no operand")
check(g._operand_size_fe(0x06) == 4 and g._operand_size_fe(0x0C) == 2 and g._operand_size_fe(0x1D) == 0,
      "FE prefix widths")


def creation(t):
    return any(p.search(t) for p in g.CREATION_ONLY)


for t in ("RimWorld.Page_CreateWorldParams.DoWindowContents", "RimWorld.Planet.WorldGenerator.GenerateWorld",
          "RimWorld.Planet.WorldGenStep_Terrain.GenerateTileFor", "RimWorld.BiomeWorker_SeaIce.GetScore"):
    check(creation(t), "%s is creation-only" % t)
for t in ("RimWorld.GenCelestial.CelestialSunGlow", "RimWorld.Planet.World.ExposeData",
          "RimWorld.GenStep_ScatterGeysers.CalculateFinalCount",   # map generation runs during play
          "RimWorld.Planet.WorldGenerator.GenerateWorldX", "UNRESOLVED(Foo)"):
    check(not creation(t), "%s is runtime" % t)

check(set(g.EXPECTED) == set(g.MODS), "every audited mod has an expectation")
check(set(p for p, v in g.EXPECTED.items() if v == "INERT") == set(g.INERT_LOG_NEEDLES),
      "every INERT mod has Player.log needles")

# the live clause: a game that is not the clause's game is UNMEASURED (the round restages it), never a FAIL
# (2026-11-03: A2 ran on a list holding My Little Planet and was recorded FAIL)
W = "Ash'karr"
J = g.judge
check(J("game_loaded", W, W, g.EXPECT_TILES, [], 900)[0] == g.PASS, "canonical planet, clean, right tiles: PASS")
check(J("game_loaded", W, W, 10242, [], 900)[0] == g.FAIL, "canonical planet at the wrong tile count: FAIL")
check(J("game_loaded", W, W, g.EXPECT_TILES, ["ErrorWhileLoadingGame"], 900)[0] == g.FAIL, "load errors: FAIL")
check(J("main_menu", None, W, None, [], 900)[0] == g.UNMEASURED, "no map: UNMEASURED")
check(J("game_loaded", "Other", W, g.EXPECT_TILES, [], 900)[0] == g.UNMEASURED, "another save: UNMEASURED")
check(J("game_loaded", W, None, g.EXPECT_TILES, [], 900)[0] == g.UNMEASURED, "unread save name: UNMEASURED")
check(J("game_loaded", W, W, g.EXPECT_TILES, [], 10)[0] == g.UNMEASURED, "a stub log: UNMEASURED")
check(g.reply({"content": [{"text": '{"status": "game_loaded"}'}]}) == {"status": "game_loaded"}, "an envelope opens")
check(g.reply({"status": "x"}) == {"status": "x"} and g.reply(None) == {} and g.reply({"content": [{"text": "no"}]}) == {},
      "a plain reply passes, a None or bad envelope is empty")
import live_def_check as ldc  # noqa: E402
inert = [p for p, v in g.EXPECTED.items() if v == "INERT"]
both = set(g.ALIEN_WORLDS)
check(ldc.condition(list(g.ALIEN_WORLDS), inert, both | {"oblitus.mylittleplanet"}, {})[0] == g.UNMEASURED,
      "a running load holding My Little Planet: UNMEASURED")
check(ldc.condition(list(g.ALIEN_WORLDS), inert, {"7f.alienworlds"}, {})[0] == g.UNMEASURED,
      "a running load lacking Tidally Locked: UNMEASURED")
check(ldc.condition(list(g.ALIEN_WORLDS), inert, None, {})[0] == g.UNMEASURED, "an unread running load: UNMEASURED")
check(ldc.condition(list(g.ALIEN_WORLDS), inert, both | {"ludeon.rimworld"}, {})[0] is None, "the right load: met")

print("selftest_generator_inert_audit: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
