"""Harness for the 2026-10-02 live pass 2 (python.exe only): extend validation.py's scene with an X node and a
run into natural rock, then frame + screenshot named views. State proof lives in validation.py, not here.

    python.exe Transient/messy_conduit_live_20261002/live2.py extend
    python.exe Transient/messy_conduit_live_20261002/live2.py shot <cx> <cz> <rootSize> <name>
    python.exe Transient/messy_conduit_live_20261002/live2.py census          # print a short census
    python.exe Transient/messy_conduit_live_20261002/live2.py probe <cmd>
    python.exe Transient/messy_conduit_live_20261002/live2.py call <tool> '<json>'
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "MessyConduit"))
import validation as V  # noqa: E402

X0, Z0 = V.X0, V.Z0
XNODE = (X0 + 5, Z0 + 3)                                   # on the main run, battery side of the gap
NORTH = [(X0 + 5, Z0 + 4), (X0 + 5, Z0 + 5), (X0 + 5, Z0 + 6)]
LAMP2 = (X0 + 5, Z0 + 7)
SOUTH = [(X0 + 5, Z0 + 2), (X0 + 5, Z0 + 1), (X0 + 5, Z0 + 0), (X0 + 5, Z0 - 1)]
ROCK = (X0 + 4, Z0 - 3, 3, 3)                              # x,z,w,h natural rock block; SOUTH's last cell ends inside it


def short(c):
    keep = ("ticksGame", "conduitCells", "cordEdges", "hiddenEdges", "strands", "nodeTypes", "decals", "layerVerts",
            "geometryHash", "fellBack", "verticesInUnwalkable", "cordsAcrossNets", "spawnedConduitTexture", "layerVisible")
    return {k: c.get(k) for k in keep}


def main():
    B = V.Bridge()
    cmd = sys.argv[1]
    if cmd == "extend":
        B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (X0 + 3, Z0 - 4, 5, 3), categories="All")
        B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % (X0 + 3, Z0 - 4, 5, 3))
        B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % (X0 + 1, Z0 - 5, 9, 15))
        B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % (X0 + 1, Z0 - 5, 9, 15))
        r1 = B.call("jawa/build_batch", ops=V.ops("PowerConduit", NORTH + SOUTH), faction="player", wipeExisting=False)
        r2 = B.call("jawa/build_batch", ops="StandingLamp:%d,%d" % LAMP2, faction="player")
        rx, rz, rw, rh = ROCK
        rock = [(x, z) for x in range(rx, rx + rw) for z in range(rz, rz + rh)]
        r3 = B.call("jawa/build_batch", ops=V.ops("Granite", rock), wipeExisting=False)
        B.call("jawa/map_commit")
        B.ticks(2)
        ci = B.call("rimworld/get_cells_info", x=X0 + 5, z=Z0 - 1, width=1, height=1)
        print(json.dumps({"conduit": (r1.get("survived"), r1.get("failed")), "lamp": (r2.get("survived"), r2.get("failed")),
                          "rock": (r3.get("survived"), r3.get("failed"))})[:900])
        print(json.dumps(ci)[:900])
        B.call("rimworld/frame_cell_rect", x=V.SITE[0], z=V.SITE[1] - 4, width=V.SITE[2], height=V.SITE[3] + 4, paddingCells=1)
        time.sleep(1.0)
        B.probe("poll")
        c = B.probe("census")
        print(json.dumps(short(c)))
        print(json.dumps([e for e in c.get("ends") or []])[:1500])
    elif cmd == "census":
        c = B.probe("census")
        print(json.dumps(short(c)))
    elif cmd == "probe":
        print(json.dumps(B.probe(sys.argv[2]))[:3000])
    elif cmd == "logs":
        lg = B.call("rimbridge/list_logs", limit=int(sys.argv[2]) if len(sys.argv) > 2 else 40, minimumLevel="warning")
        for e in lg.get("logs") or []:
            print(e.get("Sequence"), e.get("Level"), str(e.get("Message"))[:400].replace("\n", " | "))
    elif cmd == "call":
        print(json.dumps(B.call(sys.argv[2], **json.loads(sys.argv[3])))[:3000])
    elif cmd == "shot":
        x, z, root, name = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
        B.call("jawa/clear_ui", all=True)
        B.call("rimworld/set_camera_zoom", rootSize=root)
        time.sleep(1.0)
        B.call("rimworld/jump_camera_to_cell", x=x, z=z)
        time.sleep(2.5)
        print(json.dumps(B.call("rimworld/get_camera_state"))[:300])
        print(json.dumps(B.call("jawa/take_screenshot", fileName=name))[:600])


if __name__ == "__main__":
    main()
