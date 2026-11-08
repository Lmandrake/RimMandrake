"""bars3.py -- the depth contrast sheet: one ordinary view, every hole occupied, shot in each pit look (pitLookMode 0/1/2).

  python.exe ralph/live/bars3.py stage <ox> <oz>       dig + occupy (run once, on a fresh map at a morning hour)
  python.exe ralph/live/bars3.py shoot <ox> <oz> <tag> shoot every look at root 20 and 11 (names b3_<tag>_<look>_<view>)

Row A (z = oz .. oz+1): 2x2 holes, one undug gap between, depths 0 (undug), 0.5, 1, 1.5, 2, 4, 8 m (D 0,1,2,3,4,8,16),
  x = ox + 3k; a drafted colonist on each hole's north-west square and one on the undug square.
Row B (z = oz+4 .. oz+5): the same depths, empty (pit_depth_ladder_legible).
Row C (z = oz+8 .. oz+12): one 6 x 5 pit 2 m deep with a colonist on its middle square near the south lip and one
  against the north wall (x = ox .. ox+5); beside it a 3 x 3 pit 4 m, empty (x = ox+9 ..).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fwb  # noqa: E402

DEPTHS = (0, 1, 2, 3, 4, 8, 16)
T = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
LOOKS = {0: dict(pitLookMode="0", pitSinkPerLevel="0.3", pitLipOcclusion="0.85"),
         1: dict(pitLookMode="1", pitSinkPerLevel="0.3", pitLipOcclusion="1"),
         2: dict(pitLookMode="2", pitSinkPerLevel="0.08", pitLipOcclusion="0.85")}
LOG = os.path.join(fwb.OUT, "bars3.log")


def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True)
    os.makedirs(fwb.OUT, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(s + "\n")


def dig(B, cells, d):
    for c in cells:
        B.call("jawa/clear_area", rect="%d,%d,1,1" % c, dryRun=False)
        if d:
            B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=d, setFill=-1)


def put(B, cell):
    r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=cell[0], z=cell[1], faction="player", count=1) or {}
    ids = [p.get("id") for p in r.get("pawns") or [] if p.get("id")]
    for pid in ids:
        o = B.call("jawa/order_pawn", pawnId=pid, x=cell[0], z=cell[1], draft=True, waitTicks=30) or {}
        log("put", pid, cell, json.dumps(o, default=str)[:160])
    return ids


def stage(B, ox, oz):
    ids = []
    for k, d in enumerate(DEPTHS):
        a = [(ox + 3 * k + i, oz + j) for i in range(2) for j in range(2)]
        b = [(ox + 3 * k + i, oz + 4 + j) for i in range(2) for j in range(2)]
        dig(B, a, d)
        dig(B, b, d)
    big = [(ox + i, oz + 8 + j) for i in range(6) for j in range(5)]
    dig(B, big, 4)
    side = [(ox + 9 + i, oz + 9 + j) for i in range(3) for j in range(3)]
    dig(B, side, 8)
    B.step(5)
    for k, d in enumerate(DEPTHS):
        ids += put(B, (ox + 3 * k, oz + 1))      # the hole's north-west square
    ids += put(B, (ox + 2, oz + 8))               # big pit, by the near (south) lip
    ids += put(B, (ox + 4, oz + 12))              # big pit, against the far (north) wall
    B.call("rimworld/play_for", durationMs=1500, speed="Normal")
    cen = B.call("jawa/pawn_census", ids=",".join(ids)) or {}
    log("pawns", [(p.get("name"), p.get("x"), p.get("z"), p.get("drafted")) for p in cen.get("pawns") or []])
    ex = B.call("jawa/flowworks_excavation_rect", x=ox, z=oz, w=21, h=1, onlyNonZero=True) or {}
    log("depths", [(c.get("x"), c.get("d")) for c in ex.get("cells") or ex.get("rows") or []])
    B.call("jawa/set_fog", action="unfog", rect="%d,%d,30,20" % (ox - 4, oz - 4))


def shot(B, name, rect, root):
    B.call("jawa/clear_ui", all=True)
    B.call("rimworld/screenshot_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=0,
           rootSize=root, doNotResetCamera=True, fileName="b3_frame_tmp")
    time.sleep(1.2)
    r = B.call("rimworld/screenshot_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=0,
               rootSize=root, doNotResetCamera=True, fileName="%s_%s" % (name, time.strftime("%H%M%S"))) or {}
    log("SHOT", name, r.get("path") or r.get("message"))


def set_look(B, look):
    for f, v in LOOKS[look].items():
        r = B.call("jawa/mod_settings_field", typeName=T, action="set", field=f, value=v) or {}
        log(f, r.get("valueBefore"), "->", r.get("valueAfter"))
    r = B.call("jawa/static_call", type="RimMandrake.FlowWorks.SectionLayer_RMExcavationWalls", method="RedrawAll", args="") or {}
    log("redraw", str(r.get("result") or r.get("message") or r.get("error"))[:120])
    B.call("rimworld/play_for", durationMs=500, speed="Normal")


def shoot(B, ox, oz, tag, looks):
    for look in looks:
        set_look(B, look)
        n = "b3_%s_L%d" % (tag, look)
        shot(B, n + "_occ_r20", (ox - 1, oz - 1, 22, 4), 20)
        shot(B, n + "_empty_r20", (ox - 1, oz + 3, 22, 4), 20)
        shot(B, n + "_big_r20", (ox - 1, oz + 7, 14, 7), 20)
        shot(B, n + "_occ_r11", (ox - 1, oz - 1, 22, 4), 11)
        shot(B, n + "_big_r11", (ox - 1, oz + 7, 14, 7), 11)
    set_look(B, 1)   # leave the default look on


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    B = fwb.FW()
    cmd, ox, oz = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    if cmd == "stage":
        stage(B, ox, oz)
    else:
        looks = [int(v) for v in sys.argv[5].split(",")] if len(sys.argv) > 5 else [0, 1, 2]
        shoot(B, ox, oz, sys.argv[4], looks)


if __name__ == "__main__":
    main()
