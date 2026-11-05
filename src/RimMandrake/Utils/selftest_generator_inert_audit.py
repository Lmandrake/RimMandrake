#!/usr/bin/env python3
"""selftest_generator_inert_audit.py -- the IL walker, the creation-only classifier and the A2 save judge, on synthetic input.

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
# A2: the canonical save's own header is the record of a load without the INERT mods (judge_a2)
J = g.judge_a2
base = ["ludeon.rimworld"] + ["filler.%d" % k for k in range(30)] + list(g.ALIEN_WORLDS)
check(J(base, g.EXPECT_TILES, {})[0] == g.PASS, "both AW ids, no INERT mod, whole planet: PASS")
check(J(base + ["oblitus.mylittleplanet"], g.EXPECT_TILES, {})[0] == g.FAIL, "a save listing My Little Planet: FAIL")
check(J(base + ["boots.sensiblefactions"], g.EXPECT_TILES, {})[0] == g.FAIL, "a save listing Sensible Factions: FAIL")
check(J(base[:-1], g.EXPECT_TILES, {})[0] == g.FAIL, "a save lacking Tidally Locked: FAIL")
check(J(base, 10242, {})[0] == g.FAIL and J(base, None, {})[0] == g.FAIL, "a wrong or unread tile count: FAIL")
check(J(base, g.EXPECT_TILES, {"oblitus.mylittleplanet": ["MyLittlePlanet.X"]})[0] == g.FAIL, "an INERT type named: FAIL")
check(J(base, g.EXPECT_TILES, {"jaeger972.factionterritories": ["FactionTerritories.X"]})[0] == g.PASS,
      "an ACTIVE mod's types decide nothing for A2")
check(J(list(g.ALIEN_WORLDS), g.EXPECT_TILES, {})[0] == g.FAIL, "a near-empty modIds read is BLIND: FAIL")

# surface_tiles decodes raw-DEFLATE ushorts and takes the FIRST layer (the surface; the orbit layer follows)
import base64, tempfile, zlib  # noqa: E401,E402


def deflate(n):
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    return base64.b64encode(c.compress(b"\1\0" * n) + c.flush()).decode()


with tempfile.NamedTemporaryFile("w", suffix=".rws", delete=False) as fh:
    fh.write("<grid><layers><li><tileBiomeDeflate>%s</tileBiomeDeflate></li><li><tileBiomeDeflate>%s"
             "</tileBiomeDeflate></li></layers></grid>" % (deflate(21872), deflate(2432)))
check(g.surface_tiles(fh.name) == 21872, "surface layer tiles %r" % g.surface_tiles(fh.name))
with open(fh.name, "w") as fh2:
    fh2.write("<grid/>")
check(g.surface_tiles(fh.name) is None, "no tile array reads None")
os.unlink(fh.name)

print("selftest_generator_inert_audit: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
