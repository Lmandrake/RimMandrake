"""L1 acceptance sweep, FOUNDRY 2026-10-10 (acc_20261009d tier, 68 mods). Run under python.exe from the repo root:
    python.exe src\\RimMandrake\\Utils\\scenes\\l1_sweep_20261010.py
Prints one 'CHECK <item>/<crit> <PASS|FAIL|UNMEASURED> detail' line per read. Pure reads: no spawns, no settings.
Every def read is paired with a sanity probe (known-present + known-absent) so a failed call cannot read as 'absent'.
"""
import sys, json, re, os, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from scenes import scenelib as S
S.quiet()

def j(x, n=300): return json.dumps(x, default=str)[:n]

def get(d, fields=None):
    kw = {"defs": d}
    if fields: kw["fields"] = fields
    return S.call("jawa/get_defs", **kw)

def present(d):
    r = get(d)
    if not (isinstance(r, dict) and r.get("success") is True): return "UNMEASURED " + j(r, 150)
    return "found" if r.get("foundCount") == 1 else "notFound"

def out(tag, verdict, detail=""):
    print("CHECK %-48s %-10s %s" % (tag, verdict, detail), flush=True)

# sanity probe: a def that must exist and one that must not
p1, p2 = present("ThingDef/Steel"), present("ThingDef/Nonexistent_Def_XYZ")
out("PROBE Steel/absent", "PASS" if (p1, p2) == ("found", "notFound") else "UNMEASURED", "%s/%s" % (p1, p2))
if (p1, p2) != ("found", "notFound"): sys.exit(2)

# SUMP_NOOTHELM_B_PLANT_1 A1
a, b = present("ThingDef/RM_Lanneth"), present("ThingDef/RM_RawLanneth")
r = get("RecipeDef/RSW_CookFruitOnAStick", "ingredients")
txt = j(r, 4000)
acc = "RM_RawLanneth" in txt
out("SUMP_NOOTHELM_B_PLANT_1/A1", "PASS" if (a, b) == ("found", "found") and acc else "FAIL",
    "Lanneth=%s RawLanneth=%s recipe_success=%s accepts_raw=%s" % (a, b, r.get("success") if isinstance(r, dict) else "?", acc))

# ZERSIUM_FORGE_BIOME_1 L4 (defs loaded)
zs = {d: present(d) for d in ("ThingDef/RSW_Zersium", "ThingDef/RSW_MineableZersium", "GenStepDef/RUT_ZersiumForgeLumps")}
out("ZERSIUM_FORGE_BIOME_1/L4", "PASS" if all(v == "found" for v in zs.values()) else "FAIL", j(zs))

# WEEPINGSTONES_CONDENSER_QUESTS_1 C6 campaign half only (free-list half needs a separate load)
slots = ["RimMandrake.WeepingStones.RM_FactionSlotDef/RM_FactionSlot_CondenserBuyer",
         "RimMandrake.WeepingStones.RM_FactionSlotDef/RM_FactionSlot_CondenserSettlers",
         "RimMandrake.WeepingStones.RM_FactionSlotDef/RM_FactionSlot_CondenserHunters"]
for s in slots:
    r = get(s, "preferredFactions")
    out("WEEPINGSTONES_CONDENSER_QUESTS_1/C6 " + s.split("_")[-1], "INFO", j(r, 400))

# EXCAVATION_WALL_ART_1 A2 (offline PNG existence + magenta)
try:
    from PIL import Image
    root = "src/RimMandrake/FlowWorks"
    res = {}
    for n in ("RM_Spikes", "RM_Ladder", "RM_LadderRaised"):
        fs = glob.glob(root + "/**/%s*.png" % n, recursive=True)
        bad = []
        for f in fs:
            im = Image.open(f).convert("RGBA"); px = im.getdata()
            mag = sum(1 for (r_, g_, b_, a_) in px if a_ > 0 and r_ > 240 and b_ > 240 and g_ < 20)
            if mag: bad.append((os.path.basename(f), mag))
        res[n] = (len(fs), bad)
    out("EXCAVATION_WALL_ART_1/A2", "PASS" if all(v[0] > 0 and not v[1] for v in res.values()) else "FAIL", j(res))
except Exception as e:
    out("EXCAVATION_WALL_ART_1/A2", "UNMEASURED", repr(e))

# LASSO_CHERRYPICKER_REMOVAL_1 A2
cfg = glob.glob(os.path.expandvars(r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_2944488802_*.xml"))
if not cfg: out("LASSO_CHERRYPICKER_REMOVAL_1/A2", "FAIL", "config file absent (absence is a FAIL)")
else:
    m = re.search(r"<LassoSpawnChance>([^<]*)<", open(cfg[0], encoding="utf-8", errors="replace").read())
    out("LASSO_CHERRYPICKER_REMOVAL_1/A2", "PASS" if m and float(m.group(1)) == 0 else "FAIL", "%s -> %s" % (cfg[0], m.group(1) if m else "element absent"))
