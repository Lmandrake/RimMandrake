import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
def j(x, n=400): return json.dumps(x, default=str)[:n]
def field(d, f):
    r = S.call("jawa/get_defs", defs=d, fields=f, limit=2, deep=True)
    rows = r.get("defs") or []
    return (rows[0].get("fields") or {}).get(f) if rows else ("UNREAD " + j(r, 200))
def exists(d):
    r = S.call("jawa/get_defs", defs=d)
    return "found" if r.get("success") and r.get("foundCount") == 1 else ("notFound" if r.get("success") is not False else "UNMEASURED " + j(r, 150))
# SHIP_ALLOY_FORGE_1 L5
print("ALLOY forge prereq", field("ThingDef/VFEFactory_AutomatedAlloyForge", "researchPrerequisites"))
print("ALLOY plasteel prereq", field("PipeSystem.ProcessDef/VFEFactory_AlloyPlasteel", "researchPrerequisites"))
for d in ("ResearchProjectDef/RM_WM_AlloyForgeRestoration", "ResearchProjectDef/RM_WM_PlasteelAlloying",
          "ThingDef/RSW_Durasteel", "PipeSystem.ProcessDef/RSW_AlloyDurasteel", "ThingDef/RSW_Zersium"):
    print("ALLOY", d, exists(d))
print("ALLOY forge processes", j(field("ThingDef/VFEFactory_AutomatedAlloyForge", "comps"), 600))
# MATERIAL_MERGES_CLEANUP_1 L2/L4/L7: removed defs absent, survivors present
removed = ["RM_RotWeakChitin", "RM_RotMediumChitin", "RSW_WeakChitin", "RSW_FragileChitin", "RSW_MediumChitin",
           "RSW_ToxiChitin", "RSW_GrayChitin", "RSW_CrystalChitin", "RUT_Hardwood", "ChunkSlagPlasteel_GT", "RUT_TibannaGas"]
surv = ["RM_WeakChitin", "RM_MediumChitin", "RM_GrayChitin", "RM_CrystalChitin", "RM_FragileChitin", "RM_ToxiChitin",
        "RM_GreatboleHardwood", "RM_RawSalt", "KotORChunk_plasteel", "KOTOR_Tibanna"]
for d in removed: print("MERGE removed", d, exists("ThingDef/" + d))
for d in surv: print("MERGE survivor", d, exists("ThingDef/" + d))
for d in ("ThingDef/Mynock", "ThingDef/Nonexistent_Def_XYZ"): print("PROBE", d, exists(d))
