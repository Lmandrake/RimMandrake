"""Capture each staged pit full-frame at rootSize ROOT (this install floors at 8): python.exe capture_stepped_pits.py <out_dir> 6 close. Writes <TAG>_full_<pit>.png and <TAG>_meta.json (camera centre = pit centre, 2 x rootSize cells tall)."""
import sys, json, os, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
OUT = sys.argv[1]; ROOT = float(sys.argv[2]); TAG = sys.argv[3]; os.makedirs(OUT, exist_ok=True)
PITS = [("a_his_L_8m_with_4m_L", 150, 160, 3, 3), ("b_straight_step_2m_north_6m_south", 156, 160, 4, 4),
        ("c_staircase_1m_3m_6m", 163, 160, 4, 3), ("d1_deep_hole_6m_in_1m_pit", 150, 150, 5, 5),
        ("d2_1m_island_in_6m_pit", 158, 150, 5, 5), ("e_step_1m_3m_under_water_2p5m", 166, 150, 4, 4)]
def local(p):
    p = str(p or "")
    if os.name != "nt" and len(p) > 2 and p[1] == ":":
        return "/mnt/%s/%s" % (p[0].lower(), p[3:].replace("\\", "/"))
    return p
h, p, t = resolve_endpoint()
meta = {}
with RimBridge(h, p, t) as B:
    c = lambda name, **kw: B.call(name, kw, check=False)
    c("jawa/clear_ui", all=True)
    for name, x, z, w, hh in PITS:
        c("rimworld/set_camera_zoom", rootSize=ROOT)
        c("rimworld/jump_camera_to_cell", x=x + w // 2, z=z + hh // 2)
        time.sleep(1.5)
        cam = c("rimworld/get_camera_state")
        r = c("rimworld/take_screenshot", fileName="steppit_%s_%s" % (TAG, name), suppressMessage=True)
        time.sleep(1.0)
        cam2 = c("rimworld/get_camera_state")
        src = local(r.get("path"))
        dst = os.path.join(OUT, "%s_full_%s.png" % (TAG, name))
        for _ in range(10):
            if src and os.path.isfile(src): break
            time.sleep(0.5)
        if src and os.path.isfile(src): shutil.copyfile(src, dst)
        meta[name] = {"rect": [x, z, w, hh], "cam": cam, "cam2": cam2, "file": dst, "resp": {k: v for k, v in r.items() if k != "state"}}
        print(name, cam.get("rootSize"), cam.get("viewRect"), cam2.get("viewRect"), os.path.isfile(dst))
    c("rimworld/set_camera_zoom", rootSize=24)
json.dump(meta, open(os.path.join(OUT, "%s_meta.json" % TAG), "w"), indent=1, default=str)
