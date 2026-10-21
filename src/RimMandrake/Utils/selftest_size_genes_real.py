#!/usr/bin/env python3
"""Selftest: every RSW_BodySizeGene_* is REAL size, in the shipped XML and in the generator that writes it.

Owner, 2026-08-22: "I'd like it to affect carrying capacity, food, melee, etc. just as you say. Let's use this
stuff right." 7707a6aca's regeneration silently put SM_Cosmetic_BodySizeOffset back on all five
(SIZE_GENES_RECONCILE_LOST_IN_REGEN). This fails if that happens again:
  1. src/RimStarWars/StarWarsRaces/Defs/GeneDefs/SW_Genes.xml: each RSW_BodySizeGene_* carries SM_BodySizeOffset,
     no SM_Cosmetic_BodySizeOffset, and the offset / biostatMet in gen_races_mod.SIZE_GENES_REAL;
  2. gen_races_mod.make_size_genes_real turns a donor-shaped cosmetic gene real (so a regeneration cannot revert);
  3. nothing is at or over Big and Small's 1.99 BS_Giant threshold (giant weapons are a separate decision);
  4. sanity probe: the checker flags a cosmetic gene, so a pass is not a blind instrument.
Offline; parses source only.
"""
import ast
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GENES = os.path.join(REPO, "src/RimStarWars/StarWarsRaces/Defs/GeneDefs/SW_Genes.xml")
GEN = os.path.join(HERE, "gen_races_mod.py")
PREFIX = "RSW_BodySizeGene_"
GIANT = 1.99

fails = 0


def check(ok, what, detail=None):
    global fails
    print(("PASS " if ok else "FAIL ") + what + ("" if ok or detail is None else "  -> %r" % (detail,)))
    if not ok:
        fails += 1


def generator_table():
    """SIZE_GENES_REAL and make_size_genes_real from gen_races_mod.py, without importing the generator
    (its import reads the def dump and the workshop)."""
    tree = ast.parse(open(GEN, encoding="utf-8").read())
    table = fn = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "SIZE_GENES_REAL" for t in node.targets):
            table = ast.literal_eval(node.value)
        if isinstance(node, ast.FunctionDef) and node.name == "make_size_genes_real":
            fn = node
    ns = {"ET": ET, "sys": sys, "DEF_PREFIX": "RSW_", "SIZE_GENES_REAL": table}
    if fn is not None:
        exec(compile(ast.Module(body=[fn], type_ignores=[]), GEN, "exec"), ns)
    return table, ns.get("make_size_genes_real")


def problems(genes_root, table):
    out = []
    seen = set()
    for g in genes_root.iter("GeneDef"):
        name = g.findtext("defName") or ""
        if not name.startswith(PREFIX):
            continue
        suf = name[len(PREFIX):]
        seen.add(suf)
        if g.find(".//SM_Cosmetic_BodySizeOffset") is not None:
            out.append((name, "cosmetic"))
        off = g.findtext("statOffsets/SM_BodySizeOffset")
        if off is None:
            out.append((name, "no SM_BodySizeOffset"))
            continue
        if suf not in table:
            out.append((name, "no SIZE_GENES_REAL row"))
            continue
        want_off, want_met, _ = table[suf]
        if abs(float(off) - want_off) > 1e-9:
            out.append((name, "offset %s != %s" % (off, want_off)))
        if (g.findtext("biostatMet") or "").strip() != str(want_met):
            out.append((name, "biostatMet %s != %s" % (g.findtext("biostatMet"), want_met)))
        if 1 + float(off) >= GIANT:
            out.append((name, "size %.2f reaches the BS_Giant threshold" % (1 + float(off))))
    for suf in set(table) - seen:
        out.append((PREFIX + suf, "in SIZE_GENES_REAL but not shipped"))
    return out


table, make_real = generator_table()
check(isinstance(table, dict) and len(table) >= 5, "gen_races_mod.SIZE_GENES_REAL is a table of size genes", table)
check(callable(make_real), "gen_races_mod.make_size_genes_real exists")

root = ET.parse(GENES).getroot()
n = sum(1 for g in root.iter("GeneDef") if (g.findtext("defName") or "").startswith(PREFIX))
check(n >= 5, "SW_Genes.xml ships the RSW_BodySizeGene_* family (found %d)" % n, n)
bad = problems(root, table)
check(not bad, "every shipped RSW_BodySizeGene_* is REAL size, matching the generator's table", bad)
check(max(1 + v[0] for v in table.values()) < GIANT, "largest size gene stays under the 1.99 giant-weapon threshold")

# Sanity probe: a cosmetic gene (the donor's shape, what 7707a6aca shipped) is flagged.
probe = ET.fromstring("<Defs><GeneDef><defName>RSW_BodySizeGene_big</defName><biostatMet>-1</biostatMet>"
                      "<statOffsets><SM_Cosmetic_BodySizeOffset>0.2</SM_Cosmetic_BodySizeOffset></statOffsets>"
                      "</GeneDef></Defs>")
check(any(p[0] == "RSW_BodySizeGene_big" for p in problems(probe, table)),
      "sanity: the checker flags a cosmetic RSW_BodySizeGene_big")

# The generator turns the donor shape real, so a regeneration cannot revert it.
if callable(make_real):
    donor = ET.fromstring("<GeneDef><defName>RSW_BodySizeGene_small</defName><description>shorter-than-normal"
                          "</description><biostatMet>1</biostatMet><statOffsets><SM_Cosmetic_BodySizeOffset>-0.2"
                          "</SM_Cosmetic_BodySizeOffset></statOffsets></GeneDef>")
    make_real({"GeneDef": [donor]})
    check(not problems(ET.fromstring("<Defs>" + ET.tostring(donor, encoding="unicode") + "</Defs>"),
                       {"small": table["small"]}),
          "make_size_genes_real turns the donor's cosmetic _small into real -0.2 / metabolism +3",
          ET.tostring(donor, encoding="unicode"))

print("OK: 0 failure(s)" if not fails else "FAILED: %d failure(s)" % fails)
sys.exit(1 if fails else 0)
