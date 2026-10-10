"""SUMP_NOOTHELM_B_PLANT_1 A1 retry (FOUNDRY 2026-10-10). Reads the recipe's fixedIngredientFilter + defaultIngredientFilter, not 'ingredients'.
Run: python.exe src\\RimMandrake\\Utils\\scenes\\l1_lanneth_recipe_20261010.py   Sanity probe: RawBerries must appear, a nonsense def must not."""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from scenes import scenelib as S
S.quiet()
def get(d, f=None):
    kw = {"defs": d}
    if f: kw["fields"] = f
    return S.call("jawa/get_defs", **kw)
for f in ("fixedIngredientFilter", "defaultIngredientFilter"):
    r = get("RecipeDef/RSW_CookFruitOnAStick", f)
    t = json.dumps(r, default=str)
    print("FIELD", f, "success=%s" % (r.get("success") if isinstance(r, dict) else "?"), "len=%d" % len(t),
          "RawBerries=%s RawLanneth=%s NoSuch=%s" % ("RawBerries" in t, "RM_RawLanneth" in t, "RM_NoSuchXYZ" in t), flush=True)
    print(t[:900], flush=True)
for d in ("ThingDef/RM_Lanneth", "ThingDef/RM_RawLanneth"):
    r = get(d); print(d, r.get("success"), r.get("foundCount"), flush=True)
