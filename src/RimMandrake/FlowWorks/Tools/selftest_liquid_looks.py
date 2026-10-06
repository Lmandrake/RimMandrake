#!/usr/bin/env python3
"""selftest_liquid_looks.py -- FLOWWORKS_LIQUID_LOOKS_1: the per-liquid look table is complete and shipped.

Pins, offline:
  1. every field a look row uses is a real public field of RM_LiquidSurfaceLook (a misspelt XML field would be a
     load error that discards the whole LiquidDef);
  2. every liquid that reaches a terrain has a look: each LIQUID_DEF_ROWS row with a terrainSuite or canalFluid,
     and each canal FluidDef in Defs/Canals/FluidDefs (through its row or FLUID_SURFACE_LOOKS);
  3. no two looks are the same surface (shader + texture + tint), so each liquid can be told apart;
  4. the water family draws no overlay and no custom wake (owner: "make the water just look like Shallow water");
  5. the generated registry and fluid-look patch match the table byte-for-byte (edit the table, never the XML).
"""
import importlib.util
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD = HERE.parent
fails = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


spec = importlib.util.spec_from_file_location("gls", HERE / "generate_liquid_suite.py")
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)

# 1 field names
cs = (MOD / "Source" / "RM_LiquidSurface.cs").read_text(encoding="utf-8")
body = cs[cs.index("public class RM_LiquidSurfaceLook"):cs.index("public class RM_LiquidSurface :")]
fields = set(re.findall(r"public\s+(?:float|bool|string|Color)\s+([^;=]+?)\s*(?:=|;)", body))
names = set()
for decl in re.findall(r"public\s+(?:float|bool|string|Color)\s+([^;]+);", body):
    for part in decl.split(","):
        names.add(part.split("=")[0].strip())
all_looks = dict(G.SURFACE_LOOKS)
all_looks.update(G.FLUID_SURFACE_LOOKS)
unknown = sorted({f for look in all_looks.values() for f in look} - names)
check(not unknown, "every look field is a C# field (unknown: %s)" % unknown)
check(set(G._LOOK_FIELDS) <= names, "emitter field list is all C# fields (%s)" % sorted(set(G._LOOK_FIELDS) - names))
check(all(f in G._LOOK_FIELDS for look in all_looks.values() for f in look), "emitter writes every field a row sets")

# 2 coverage
missing = [k for k, r in G.LIQUID_DEF_ROWS.items()
           if (r.get("terrainSuite") or r.get("canalFluid")) and k not in G.SURFACE_LOOKS]
check(not missing, "every row that reaches a terrain has a look (missing: %s)" % missing)
canal = set()
for p in (MOD / "Defs" / "Canals" / "FluidDefs").glob("*.xml"):
    canal |= set(re.findall(r"<defName>(RM_Fluid_\w+)</defName>", p.read_text(encoding="utf-8")))
by_row = {r.get("canalFluid"): k for k, r in G.LIQUID_DEF_ROWS.items() if r.get("canalFluid")}
uncovered = sorted(f for f in canal if f not in G.FLUID_SURFACE_LOOKS and by_row.get(f) not in G.SURFACE_LOOKS)
check(len(canal) >= 8, "sanity: found the canal fluids (%d)" % len(canal))
check(not uncovered, "every canal fluid has a look (uncovered: %s)" % uncovered)

# 3 distinct (rows that ADOPT vanilla terrains -- fresh/salt -- are vanilla water and exempt)
seen = {}
for k, look in all_looks.items():
    if k in ("freshwater", "saltwater"):
        continue
    key = (look.get("shader", "Water"), look.get("texture"), look.get("tint"), look.get("fleck"), look.get("sheen"))
    seen.setdefault(key, []).append(k)
dups = [v for v in seen.values() if len(v) > 1]
check(not dups, "no two liquids share one surface (dups: %s)" % dups)

# 4 water family
for k in ("freshwater", "saltwater", "brine", "toxic", "boiling", "icy"):
    look = G.SURFACE_LOOKS[k]
    check(not look.get("overlay") and not look.get("wake") and look.get("shader", "Water") == "Water",
          "%s is vanilla water: no overlay, no custom wake" % k)
for k in ("slime_red",):
    check(G.SURFACE_LOOKS[k].get("shader") == "Flow" and G.SURFACE_LOOKS[k].get("splashes") is False,
          "%s is a thick liquid: flow shader, no splash" % k)

# tar is deliberately water-shader + wading splash since 2026-10-06 (owner), not a thick liquid
check(G.SURFACE_LOOKS["tar"].get("shader", "Water") == "Water" and G.SURFACE_LOOKS["tar"].get("wake") == 0.0,
      "tar uses the water shader with a near-black tint (owner 2026-10-06)")

# 5 generated output in sync
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    G.build_liquiddef_registry(td)
    G.build_fluid_looks_patch(td)
    for gen, shipped in (("RM_LiquidDefRegistry.xml", MOD / "Defs" / "LiquidTypes" / "LiquidDefs"),
                         ("RM_FluidSurfaceLooks.xml", MOD / "Patches" / "LiquidTypes")):
        same = (td / gen).read_bytes() == (shipped / gen).read_bytes()
        check(same, "%s matches the table (regenerate: python3 Tools/generate_liquid_suite.py)" % gen)
pit = (MOD / "Defs" / "Canals" / "FluidDefs" / "FlowWorks_PitFluids.xml").read_text(encoding="utf-8")
check("<surfaceLook>" not in pit, "no hand-written surfaceLook left in FlowWorks_PitFluids.xml (the patch carries it)")

print("%d FAIL" % len(fails) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
