#!/usr/bin/env python3
"""Proof for VEXXISS_VARIANT_WIRING_VET_REVIEW: RM_CauldronFauna.xml is reviewed CLEAN, the RM_Vexxiss
PawnKindDef carries the V_E alternate graphic at chance 0.5, and the def plus EVERY RM_Vexxiss texture
the def names is deployed byte-identical. Exits 1 on the first failed clause class (all failures printed).

Every check fails on its own; nothing is a loop whose status is only the last iteration's (the gen-1 hole).
--deployed-root / --repo-root let a mutation probe point the checks at a doctored copy.
"""
import argparse
import filecmp
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

REL_XML = "Defs/ThingDefs_Races/RM_CauldronFauna.xml"
TEX_DIR = "Textures/Things/Pawn/Animal/RM_Vexxiss"
BASE_TEX = "Things/Pawn/Animal/RM_Vexxiss/RM_Vexxiss"
ALT_TEX = "Things/Pawn/Animal/RM_Vexxiss/RM_VexxissV_E"
FACINGS = ("north", "south", "east")   # Graphic_Multi: west mirrors east
DEPLOYED = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/RimMandrake.Biomes/Biomes/Cauldron"

ap = argparse.ArgumentParser()
ap.add_argument("--repo-root", default="src/RimMandrake/Cauldron")
ap.add_argument("--deployed-root", default=DEPLOYED)
ap.add_argument("--skip-review", action="store_true", help="probe use only: skip the CLEAN check")
a = ap.parse_args()

fails = []
def need(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)

repo_xml = os.path.join(a.repo_root, REL_XML)
dep_xml = os.path.join(a.deployed_root, REL_XML)

# 1. review: code_review_status says CLEAN for the repo file
if not a.skip_review:
    r = subprocess.run([sys.executable, "src/RimMandrake/Utils/code_review_status.py", "check", repo_xml],
                       capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    need(r.returncode == 0 and "CLEAN" in out and "DIRTY" not in out, "review CLEAN: %s" % out.splitlines()[-1:] )

# 2. the wiring, parsed as XML elements
kind = None
try:
    root = ET.parse(repo_xml).getroot()
    kind = next((k for k in root.findall("PawnKindDef") if (k.findtext("defName") or "").strip() == "RM_Vexxiss"), None)
except (ET.ParseError, OSError) as e:
    need(False, "parse %s: %s" % (repo_xml, e))
need(kind is not None, "PawnKindDef RM_Vexxiss present")
tex_paths = set()
if kind is not None:
    ch = (kind.findtext("alternateGraphicChance") or "").strip()
    need(ch != "" and abs(float(ch) - 0.5) < 1e-9, "alternateGraphicChance == 0.5 (got %r)" % ch)
    alts = [(li.findtext("texPath") or "").strip() for li in kind.findall("alternateGraphics/li")]
    need(ALT_TEX in alts, "alternateGraphics names %s (got %s)" % (ALT_TEX, alts))
    bodies = [(t.text or "").strip() for t in kind.findall("lifeStages/li/bodyGraphicData/texPath")]
    need(BASE_TEX in bodies, "lifeStage bodyGraphicData names %s (got %s)" % (BASE_TEX, sorted(set(bodies))))
    tex_paths = set(alts) | set(bodies)

# 3. deploy: the def is byte-identical
need(os.path.isfile(dep_xml) and filecmp.cmp(repo_xml, dep_xml, shallow=False), "deployed def identical: %s" % dep_xml)

# 4. deploy: every facing of every texPath the def names exists in repo AND deployed, byte-identical
for tp in sorted(tex_paths | {BASE_TEX, ALT_TEX}):
    for f in FACINGS:
        rel = os.path.join("Textures", tp + "_%s.png" % f)
        src, dst = os.path.join(a.repo_root, rel), os.path.join(a.deployed_root, rel)
        need(os.path.isfile(src), "repo texture exists: %s" % rel)
        need(os.path.isfile(dst) and os.path.isfile(src) and filecmp.cmp(src, dst, shallow=False),
             "deployed texture identical: %s" % rel)

# 5. no repo PNG in the folder left undeployed or drifted (catches textures beyond the six named)
rdir = os.path.join(a.repo_root, TEX_DIR)
pngs = sorted(p for p in os.listdir(rdir) if p.endswith(".png")) if os.path.isdir(rdir) else []
need(len(pngs) >= 6, "repo RM_Vexxiss folder holds >= 6 PNGs (got %d)" % len(pngs))
for p in pngs:
    d = os.path.join(a.deployed_root, TEX_DIR, p)
    need(os.path.isfile(d) and filecmp.cmp(os.path.join(rdir, p), d, shallow=False), "folder PNG deployed identical: %s" % p)

print("RESULT %s (%d failures)" % ("PASS" if not fails else "FAIL", len(fails)))
sys.exit(1 if fails else 0)
