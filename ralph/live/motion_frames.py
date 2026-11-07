#!/usr/bin/env python3
"""A frame sequence of cut ends, so someone can see where the spark sits as the end writhes.

    python.exe ralph/live/motion_frames.py TAG [--look Modern] [--frames 10] [--cells 3.2]

Takes consecutive tight screenshots round one live floor end and one live fallen wire end, reading the end's position from the probe
beside each frame. The whip runs on real time, so this works paused and each frame is a later moment. Unique names: the writer is asynchronous.
"""
import argparse, json, os, shutil, sys, time
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "northstar_matrix"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import run_live as RL  # noqa: E402

OUT = r"D:\ClaudeWork\rimmandrake\ralph_gss\shots"


def grab(B, name, cx, cz, cells):
    res = B.call("rimworld/screenshot_cell_rect", x=int(cx - cells), z=int(cz - cells * 0.7), width=int(cells * 2), height=int(cells * 1.4),
                 paddingCells=0, fileName=name, rootSize=cells * 0.75)
    return res.get("filePath") or res.get("path") or res.get("savedPath")


def settle(paths):
    for src, name in paths:
        for _ in range(40):
            if src and os.path.exists(src) and os.path.getsize(src) > 0:
                break
            time.sleep(0.25)
        time.sleep(0.2)
        if src and os.path.exists(src):
            shutil.copyfile(src, os.path.join(OUT, name + ".png"))


def park(B, cx, cz, cells):
    """Leave the camera on the end: a shot puts the camera back afterwards, and off screen no whip is drawn, so the probe would read the laid tip."""
    B.call("rimworld/jump_camera_to_cell", x=int(cx), z=int(cz))
    B.call("rimworld/set_camera_zoom", rootSize=cells * 0.75)
    time.sleep(0.4)


def sequence(B, tag, label, read, cx, cz, n, cells):
    rows, paths = [], []
    park(B, cx, cz, cells)
    t0 = time.time()
    for i in range(n):
        name = "%s_%s_%02d" % (tag, label, i)
        rows.append({"frame": i, "t": round(time.time() - t0, 2), "tip": read()})
        paths.append((grab(B, name, cx, cz, cells), name))
    settle(paths)
    print(label, json.dumps(rows))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tag")
    ap.add_argument("--frames", type=int, default=10)
    ap.add_argument("--cells", type=float, default=3.2)
    a = ap.parse_args()
    B = RL.LiveBridge()
    B.call("jawa/clear_ui", all=True)
    m = B.probe("motion")
    tips = m.get("sparkTips") or []
    print("whipDraws", m.get("whipDraws"), "liveFloorEnds", m.get("liveFloorEnds"), "tips", len(tips))
    if tips:
        lx, lz = tips[0]["laid"]

        def read_floor():
            for q in B.probe("motion").get("sparkTips") or []:
                if abs(q["laid"][0] - lx) < 0.01 and abs(q["laid"][1] - lz) < 0.01:
                    return q["now"]
            return None
        # the camera must be on it first, or the whip is not drawn and the probe reads the laid tip
        grab(B, "%s_floor_warm" % a.tag, lx, lz, a.cells)
        time.sleep(0.5)
        sequence(B, a.tag, "floor", read_floor, lx, lz, a.frames, a.cells)
    c = B.ap("census")
    for an in c.get("anchors") or []:
        if an.get("fallenLive") is not True:
            continue
        for f in an.get("fallen") or []:
            ends = f.get("wireEnds") or []
            if not ends:
                continue
            ex, ez = ends[0]["laid"]
            aid = an["id"]

            def read_wire():
                for q in B.ap("census").get("anchors") or []:
                    if q.get("id") == aid:
                        return [w["now"] for w in q["fallen"][0]["wireEnds"]]
                return None
            grab(B, "%s_wire_warm" % a.tag, ex, ez, a.cells)
            time.sleep(0.5)
            print("wire ends laid", json.dumps(ends))
            sequence(B, a.tag, "wire", read_wire, ex, ez, a.frames, a.cells)
            return 0
    print("no live fallen wire on this map")
    return 0


if __name__ == "__main__":
    sys.exit(main())
