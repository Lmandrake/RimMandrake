#!/usr/bin/env python3
"""Def-side proof for ROT_REGEN_SHEET_FINISH_SIX_OPTIONS_SERVED: all six picked options are LIVE in the defs.

Owner picks: angelmoth A/B/C all live, donor dropped (card 2026-10-15); redsong a/b/c all live (2026-10-18).
Parses the XML (never greps it). Exit 0 when every clause holds, 1 with the failing clauses otherwise.

  python3 infrastructure/state/evidence/ROT_REGEN_SHEET_FINISH_SIX_OPTIONS_SERVED_proof.py [--root <repo>]
"""
import os
import sys
import xml.etree.ElementTree as ET

ROOT = sys.argv[sys.argv.index("--root") + 1] if "--root" in sys.argv else \
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MOD = os.path.join(ROOT, "src/RimMandrake/TheRot")
TEX = os.path.join(MOD, "Textures")
MOTH_XML = os.path.join(MOD, "Defs/Fauna/RM_Dustveil.xml")
FLORA_XML = os.path.join(MOD, "Defs/ThingDefs_Plants/RM_RotSporeKit_Flora.xml")
MOTH_A = "RotSpecies/AngelMoth/AngelMoth"
MOTH_ALTS = {"RotSpecies/AngelMoth/AngelMoth_B", "RotSpecies/AngelMoth/AngelMoth_C"}
CAP_DIR = "RotSporeKit/Things/Plant/CrimsonCap"
CAP_PICKS = ("CrimsonCap_a.png", "CrimsonCap_b.png", "CrimsonCap_c.png")

fails = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


def one_def(path, tag, name):
    hits = [d for d in ET.parse(path).getroot().iter(tag) if (d.findtext("defName") or "").strip() == name]
    check(len(hits) == 1, "%s %s defined exactly once in %s (found %d)" % (tag, name, os.path.basename(path), len(hits)))
    return hits[0] if hits else None


# --- angel moth (RM_Dustveil): option A base, B and C as alternates, no donor art -----------------
kind = one_def(MOTH_XML, "PawnKindDef", "RM_Dustveil")
if kind is not None:
    bodies = [(b.findtext("texPath") or "").strip() for b in kind.findall("lifeStages/li/bodyGraphicData")]
    check(bool(bodies) and all(t == MOTH_A for t in bodies),
          "every life stage's base texPath is option A %s (got %s)" % (MOTH_A, bodies))
    alts = [(li.findtext("texPath") or "").strip() for li in kind.findall("alternateGraphics/li")]
    check(sorted(alts) == sorted(MOTH_ALTS), "alternateGraphics are exactly options B and C (got %s)" % alts)
    try:
        chance = float(kind.findtext("alternateGraphicChance") or "0")
    except ValueError:
        chance = 0.0
    # A shows with 1-chance, B and C with chance/2 each: every option must actually appear.
    check(0.0 < chance < 1.0, "alternateGraphicChance strictly between 0 and 1, so A, B and C all appear (got %s)" % chance)
    alltex = [(e.text or "").strip() for e in kind.iter("texPath")]
    for d in ET.parse(MOTH_XML).getroot().iter("ThingDef"):
        if (d.findtext("defName") or "").strip() == "RM_Dustveil":
            alltex += [(e.text or "").strip() for e in d.iter("texPath")]
    donor = [t for t in alltex if not t.startswith("RotSpecies/AngelMoth/")]
    check(not donor, "no non-option (donor) texPath on RM_Dustveil (got %s)" % donor)
    for t in [MOTH_A] + sorted(MOTH_ALTS):
        for f in ("east", "north", "south"):
            check(os.path.isfile(os.path.join(TEX, "%s_%s.png" % (t, f))), "texture %s_%s.png exists" % (t, f))

# --- redsong (RM_CrimsonCap): Graphic_Random over the folder holding a/b/c -------------------------
cap = one_def(FLORA_XML, "ThingDef", "RM_CrimsonCap")
if cap is not None:
    gd = cap.find("graphicData")
    check(gd is not None and (gd.findtext("graphicClass") or "").strip() == "Graphic_Random",
          "RM_CrimsonCap graphicClass is Graphic_Random")
    check(gd is not None and (gd.findtext("texPath") or "").strip() == CAP_DIR,
          "RM_CrimsonCap texPath is the folder %s" % CAP_DIR)
    for f in CAP_PICKS:
        check(os.path.isfile(os.path.join(TEX, CAP_DIR, f)), "picked texture %s/%s in the Random pool" % (CAP_DIR, f))

print("RESULT %s (%d failing)" % ("PASS" if not fails else "FAIL", len(fails)))
sys.exit(1 if fails else 0)
