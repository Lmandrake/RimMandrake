"""Selftest for Cuisine/validation.py vce_sealer_problems (VCE_CANFISH_FIX_RESKIN_SKIPS_BILL): the shipped ration-sealer
patch passes; a patch without the VCE_CanFish relabel fails; VCE_CanFish moved into the main Sequence fails."""
import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))  # validation.py imports modcheck
spec = importlib.util.spec_from_file_location("cuisine_validation", os.path.join(HERE, "validation.py"))
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

FAILS = []


def check(name, ok, detail=""):
    print("%-5s %s %s" % ("ok" if ok else "FAIL", name, "" if ok else detail))
    if not ok:
        FAILS.append(name)


shipped = open(v.VCE_SEALER_PATCH, encoding="utf-8").read()


def run(text):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "patch.xml")
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return v.vce_sealer_problems(p)


check("the shipped patch passes", v.vce_sealer_problems() == [], v.vce_sealer_problems())
cut = shipped.split("<!-- VCE_CANFISH_FIX_RESKIN_SKIPS_BILL")[0] + "</Patch>\n"
check("planted defect: no VCE_CanFish relabel fails", any("Conditional" in p for p in run(cut)), run(cut))
moved = shipped.replace('<xpath>Defs/RecipeDef[defName="VCE_CanEggs"]/label</xpath>',
                        '<xpath>Defs/RecipeDef[defName="VCE_CanFish"]/label</xpath>', 1)
check("planted defect: VCE_CanFish inside the main Sequence fails", any("main Sequence" in p for p in run(moved)), run(moved))
nojob = shipped.replace('<xpath>Defs/RecipeDef[defName="VCE_CanFish"]/jobString</xpath>',
                        '<xpath>Defs/RecipeDef[defName="VCE_CanFishX"]/jobString</xpath>', 1)
check("planted defect: a missing VCE_CanFish jobString fails", any("jobString" in p for p in run(nojob)), run(nojob))
check("sanity probe: a patch with no main Sequence is refused, not passed",
      any(p.startswith("sanity") for p in run("<Patch></Patch>")), run("<Patch></Patch>"))

print("all ok" if not FAILS else "FAILED: %s" % FAILS)
sys.exit(1 if FAILS else 0)
