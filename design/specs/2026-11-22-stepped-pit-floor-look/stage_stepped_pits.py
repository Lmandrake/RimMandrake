"""Stage six stepped pits on the current map (cleared rect x146-175, z146-167) and read their depths back. From WSL: eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"; python3 src/RimMandrake/rimflow/game_lock.py run ArchSmall --for "<why>" -- python.exe design/specs/2026-11-22-stepped-pit-floor-look/stage_stepped_pits.py Transient/steppit/cap"""
import sys, json, os, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
AREA = (146, 146, 30, 22)  # x, z, w, h cleared
# depth in notches (0.5 m). (name, x0, z0, rows north-first)
def grid(rows): return rows
PITS = [
    ("a_his_L_8m_with_4m_L", 150, 160, [[8, 8, 16], [8, 16, 16], [16, 16, 16]], None),
    ("b_straight_step_2m_north_6m_south", 156, 160, [[4]*4, [4]*4, [12]*4, [12]*4], None),
    ("c_staircase_1m_3m_6m", 163, 160, [[2]*4, [6]*4, [12]*4], None),
    ("d1_deep_hole_6m_in_1m_pit", 150, 150, [[2]*5, [2]*5, [2, 2, 12, 2, 2], [2]*5, [2]*5], None),
    ("d2_1m_island_in_6m_pit", 158, 150, [[12]*5, [12]*5, [12, 12, 2, 12, 12], [12]*5, [12]*5], None),
    ("e_step_1m_3m_under_water_2p5m", 166, 150, [[2]*4, [2]*4, [6]*4, [6]*4], 2.5),
]

def local(p):
    p = str(p or "")
    if os.name != "nt" and len(p) > 2 and p[1] == ":":
        return "/mnt/%s/%s" % (p[0].lower(), p[3:].replace("\\", "/"))
    return p

h, p, t = resolve_endpoint()
log = {"pits": {}, "captures": {}}
with RimBridge(h, p, t) as B:
    c = lambda name, **kw: B.call(name, kw, check=False)
    x, z, w, hh = AREA
    rr = "%d,%d,%d,%d" % AREA
    # clear any old dig, then the area
    ex = c("jawa/flowworks_excavation_rect", x=x, z=z, w=w, h=hh, onlyNonZero=True, includeTerrain=False)
    for cell in ex.get("rows") or []:
        if cell.get("isExcavated"):
            c("jawa/flowworks_excavation_drive", x=cell["x"], z=cell["z"], deepenLevels=0, setBodyWaterM=0.0, fillInLevels=int(cell.get("d") or 0))
    pawns = (c("jawa/list_pawns", rect=rr, limit=200).get("pawns") or [])
    log["pawns_in_area"] = [(q.get("label"), q.get("faction")) for q in pawns]
    print("destroy", str(c("jawa/destroy_batch", rects=rr, categories="All"))[:200])
    print("terrain", str(c("jawa/set_terrain_batch", ops="Soil:" + rr))[:200])
    c("jawa/set_fog", action="unfog", rect=rr)
    c("jawa/set_roof_batch", ops="None:" + rr)
    c("jawa/weather_set", weather="Clear", lockWeather=True)
    # noon light
    clk = c("jawa/time_clock")
    print("clock", str(clk)[:300])
    for name, x0, z0, rows, water in PITS:
        n = len(rows)
        for ri, row in enumerate(rows):
            for ci, d in enumerate(row):
                cx, cz = x0 + ci, z0 + (n - 1 - ri)
                r = c("jawa/flowworks_excavation_drive", x=cx, z=cz, deepenLevels=d, setBodyWaterM=-1)
                if not r.get("success", True):
                    print("DRIVE FAIL", name, cx, cz, str(r)[:200])
        if water is not None:
            r = c("jawa/flowworks_excavation_drive", x=x0, z=z0, deepenLevels=0, setBodyWaterM=water)
            print("water", name, str(r)[:300])
        # read back
        rb = c("jawa/flowworks_excavation_rect", x=x0, z=z0, w=len(rows[0]), h=n, onlyNonZero=False, includeTerrain=True)
        got = {(q["x"], q["z"]): q for q in rb.get("rows") or []}
        back = [[got.get((x0 + ci, z0 + (n - 1 - ri)), {}).get("d") for ci in range(len(rows[0]))] for ri in range(n)]
        log["pits"][name] = {"want": rows, "readback_d": back, "sample": list(got.values())[:1]}
        print(name, "want", rows, "got", back)
    json.dump(log, open(os.path.join(OUT, "stage_log.json"), "w"), indent=1, default=str)
