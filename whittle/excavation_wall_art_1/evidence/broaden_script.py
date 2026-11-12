"""EXCAVATION_WALL_ART_1 broaden experiments (GPT's list, 2026-11-12). python.exe broaden.py <repo> <out>"""
import json
import os
import shutil
import sys
import time

REPO, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import validation_core as V  # noqa: E402

B = V.Bridge()
LOG = []
SPIKES = "architect-designator:structure:build-rm-spikes"


def call(tool, **kw):
    try:
        return B.call(tool, **kw) or {}
    except Exception as ex:  # noqa: BLE001
        return {"success": False, "error": str(ex)}


def log(k, v):
    LOG.append({k: v})
    print(k, json.dumps(v)[:300])
    sys.stdout.flush()


def drive(x, z, deepen=0, fill=-1):
    return call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=deepen, setFill=fill, fillInLevels=0)


def look(x, z):
    r = call("jawa/static_call", type="RimMandrake.FlowWorks.RM_WaterLookProofs", method="ProofWaterLook", args="%d,%d" % (x, z))
    t = str(r.get("result") or r)
    return {k: t.split(k + "=")[1].split()[0] for k in ("hollow", "waterM", "terrain") if k + "=" in t}


def cam(x, z, root=11.0):
    call("jawa/clear_ui", all=True)
    call("rimworld/jump_camera_to_cell", x=x, z=z)
    call("rimworld/set_camera_zoom", rootSize=root)


def snap(name):
    time.sleep(1.5)
    r = call("jawa/take_screenshot", fileName="ewab_%s_%d" % (name, int(time.time())))
    src = r.get("filePath")
    for _ in range(12):
        if src and os.path.exists(src):
            break
        time.sleep(0.5)
    shutil.copyfile(src, os.path.join(OUT, name + ".png"))
    log("shot", name)


def spikes(x, z, w, h):
    call("rimworld/set_god_mode", enabled=True)
    r = call("rimworld/apply_architect_designator", designatorId=SPIKES, x=x, z=z, width=w, height=h)
    call("rimworld/set_god_mode", enabled=False)
    log("spikes_%d_%d" % (x, z), {"accepted": r.get("acceptedCellCount"), "rejected": [(c.get("x"), c.get("z"), c.get("reason", "")[:70]) for c in (r.get("rejectedCells") or [])]})


# E1: a pit changed under a camera that never moves (stale SectionLayer?)
cam(97, 127)
for i in range(3):
    for j in range(3):
        drive(96 + i, 126 + j, deepen=1)
snap("e1_a_D1")
for i in range(3):
    for j in range(3):
        drive(96 + i, 126 + j, deepen=3)
log("e1_after_deepen", look(97, 127))
snap("e1_b_deepened_to_D4_same_camera")
for i in range(3):
    for j in range(3):
        drive(96 + i, 126 + j, fill=2)
log("e1_after_fill", look(97, 127))
snap("e1_c_filled_1m_same_camera")
for i in range(3):
    for j in range(3):
        drive(96 + i, 126 + j, fill=0)
log("e1_after_drain", look(97, 127))
snap("e1_d_drained_same_camera")

# E2: staircases. N-S: 3 wide, depth grows to the SOUTH (z 137 D1 .. z 134 D4); E-W: depth grows EAST.
for k, d in enumerate((1, 2, 3, 4)):
    for i in range(3):
        drive(104 + i, 137 - k, deepen=d)
    for j in range(3):
        drive(112 + k, 133 + j, deepen=d)
# and the reverse N-S (depth grows NORTH), the case where the faces sit on each step's north wall
for k, d in enumerate((1, 2, 3, 4)):
    for i in range(3):
        drive(120 + i, 134 + k, deepen=d)
log("e2_looks", {"ns_south_deeper": [look(105, 137 - k) for k in range(4)], "ew": [look(112 + k, 134) for k in range(4)],
                 "ns_north_deeper": [look(121, 134 + k) for k in range(4)]})
cam(113, 135, 12.0)
snap("e2_staircases")

# E3: spikes in a single-cell D4 hole and a 1x3 N-S D4 trench and a 3x1 E-W trench
drive(128, 135, deepen=4)
for j in range(3):
    drive(132, 134 + j, deepen=4)
for i in range(3):
    drive(136 + i, 135, deepen=4)
spikes(128, 135, 1, 1)
spikes(132, 134, 1, 3)
spikes(136, 135, 3, 1)
cam(133, 135, 11.0)
snap("e3_spikes_single_and_trenches")

# E4: spike fade - the scene's spiked D4 (116..118, 112..114) at 0.5 m, then drained
for i in range(3):
    for j in range(3):
        drive(116 + i, 112 + j, fill=1)
log("e4_fill_0_5m", look(117, 113))
cam(117, 113, 11.0)
snap("e4_spikes_under_half_metre")
for i in range(3):
    for j in range(3):
        drive(116 + i, 112 + j, fill=0)
log("e4_drained", look(117, 113))
snap("e4_spikes_drained_again")

with open(os.path.join(OUT, "broaden_%s.json" % time.strftime("%Y%m%dT%H%M%S")), "w") as f:
    json.dump(LOG, f, indent=1)
