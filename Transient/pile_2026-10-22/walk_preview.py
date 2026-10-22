"""Walk preview: for every stop in walk_tonight.json run its goto, then capture each view into walk_preview/.
python.exe Transient/pile_2026-10-22/walk_preview.py [--only 1,6] [--zoom 12]"""
import sys, os, json, shutil, subprocess, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import validation_core as V
ap = argparse.ArgumentParser()
ap.add_argument("--only", default="")
ap.add_argument("--zoom", type=float, default=12)
a = ap.parse_args()
only = {int(x) for x in a.only.split(",") if x}
W = json.load(open(os.path.join(HERE, "walk_tonight.json")))
c1 = json.load(open(os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "northstar", "review", "scenarios", "map_r_placed.json")))
c1o = c1["c1"]["origin"]
OUT = os.path.join(HERE, "walk_preview")
B = V.Bridge()


def goto(cmd):
    out = []
    for part in cmd.split(";"):
        args = part.strip().replace("python.exe ", "").split()
        p = subprocess.run([sys.executable] + args, cwd=REPO, capture_output=True, text=True, timeout=300)
        out += (p.stdout + p.stderr).strip().splitlines()[-1:]
    return out


def shot(name, rect):
    B.call("jawa/clear_ui", all=True)
    need = max((rect[3] + 2) / 2.0, (rect[2] + 2) / 2.0 / (16.0 / 9.0)) + 1.5
    B.call("rimworld/set_camera_zoom", rootSize=max(a.zoom, need))
    r = B.call("rimworld/screenshot_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=1,
               fileName=name, suppressMessage=True)
    src = r.get("path") or r.get("filePath")
    if src:
        wsl = src.replace("\\", "/")
        if wsl[1:3] == ":/":
            wsl = "/mnt/" + wsl[0].lower() + wsl[2:]
        dst = os.path.join(OUT, name + ".png")
        try:
            shutil.copyfile(src, dst)
        except OSError:
            dst = src
        print("  shot", name, rect, "->", dst)
    else:
        print("  SHOT FAILED", name, json.dumps(r)[:200])


for s in W["stops"]:
    if only and s["n"] not in only:
        continue
    print("stop", s["n"], s["id"], goto(s["goto"]))
    B.call("rimworld/pause_game", pause=True)
    for i, v in enumerate(s["views"]):
        name = "stop%02d_%s_v%d" % (s["n"], s["id"], i + 1)
        if "goto" in v:
            print("  view goto", goto(v["goto"]))
            cam = B.call("rimworld/get_camera_state")
            B.call("jawa/clear_ui", all=True)
            r = B.call("rimworld/take_screenshot", fileName=name)
            src = r.get("path") or r.get("filePath")
            if src:
                try:
                    shutil.copyfile(src, os.path.join(OUT, name + ".png"))
                except OSError:
                    pass
            print("  shot(goto)", name, src or json.dumps(r)[:200])
            continue
        if "frame" in v:
            g = v["frame"]["args"]
            rect = (g["x"], g["z"], g["width"], g["height"])
        else:
            fx, fz, fw, fh = v["frame_rel"]
            rect = (c1o[0] + fx, c1o[1] + fz, fw, fh)
        shot(name, rect)
    if not s["views"]:
        B.call("jawa/clear_ui", all=True)
        nm = "stop%02d_%s" % (s["n"], s["id"])
        r = B.call("rimworld/take_screenshot", fileName=nm)
        src = r.get("path") or r.get("filePath")
        if src:
            try:
                shutil.copyfile(src, os.path.join(OUT, nm + ".png"))
            except OSError:
                pass
        print("  shot(goto)", src or json.dumps(r)[:200])
