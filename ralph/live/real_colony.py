#!/usr/bin/env python3
"""A real player's colony, not one this loop built: copy one of Steve's own saves to gss_real_<tag> (the original is never loaded or
written), load the copy on the small list, dump its cord world for the lab, and shoot every 20x11-cell tile that holds conduit, at play zoom.

    python.exe ralph/live/real_colony.py "The Omega Team" omega [--max-tiles 24] [--shot-tag p15r] [--no-load]

Prints the tiles it shot (map cells) so they can be shot again after a change. Unique names: the shot writer is asynchronous.
"""
import argparse, json, os, shutil, sys, time
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "northstar_matrix"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(REPO, "ralph", "live"))
import run_live as RL  # noqa: E402
from await_lifecycle import await_lifecycle  # noqa: E402

SAVES = os.path.join(os.environ.get("RM_GAME_USERDATA", ""), "Saves")
SHOTS = r"D:\ClaudeWork\rimmandrake\ralph_gss\shots"
WORLDS = r"D:\ClaudeWork\rimmandrake\ralph_gss\worlds"
TW, TH = 20, 11


def tiles_over(cells, maxn):
    """Tiles of TW x TH cells on a grid, ranked by how much conduit they hold."""
    count = {}
    for x, z in cells:
        k = (x // TW, z // TH)
        count[k] = count.get(k, 0) + 1
    ranked = sorted(count.items(), key=lambda kv: -kv[1])
    return [(i * TW, j * TH, n) for (i, j), n in ranked if n >= 3][:maxn]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("tag")
    ap.add_argument("--max-tiles", type=int, default=24)
    ap.add_argument("--shot-tag", default="p15r")
    ap.add_argument("--no-load", action="store_true", help="the copy is already loaded")
    ap.add_argument("--tiles", default="", help="x,z;x,z... tile corners to shoot instead of ranking")
    a = ap.parse_args()
    name = "gss_real_%s" % a.tag
    dst = os.path.join(SAVES, name + ".rws")
    if not os.path.exists(dst):
        shutil.copyfile(os.path.join(SAVES, a.src + ".rws"), dst)
        print("copied", a.src, "->", name)
    B = RL.LiveBridge()
    if not a.no_load:
        t0 = time.time()
        r = B.call("rimworld/load_game_ready", saveName=name, timeoutMs=600000)
        print("load", json.dumps(r)[:200])
        if r.get("success") is False:
            print("LOAD REFUSED: nothing shot (the map on screen is some other save)")
            return 1
        lc = await_lifecycle(B.call, "map_ready", 600, poll_s=1.0)
        print("map_ready", lc.ok, lc.reason, "%.0fs" % (time.time() - t0))
        time.sleep(10)
    B.call("rimworld/set_time_speed", speed=0)
    r = B.probe("worlddump:real_%s" % a.tag)
    print("worlddump", json.dumps(r)[:200])
    src = os.path.join(os.environ.get("RM_GAME_USERDATA", ""), "GssWorlds", "real_%s.json" % a.tag)
    for _ in range(40):
        if os.path.exists(src):
            break
        time.sleep(0.5)
    os.makedirs(WORLDS, exist_ok=True)
    W = None
    if os.path.exists(src):
        shutil.copyfile(src, os.path.join(WORLDS, "real_%s.json" % a.tag))
        W = json.load(open(src))
        print("world", W["w"], W["h"], "conduit", len(W["conduit"]), "machines", len(W["machines"]))
    if a.tiles:
        tiles = [tuple(int(v) for v in t.split(",")) + (0,) for t in a.tiles.split(";") if t]
    else:
        tiles = tiles_over([tuple(c) for c in W["conduit"]], a.max_tiles) if W else []
    out = []
    for x, z, n in tiles:
        nm = "%s_%s_x%dz%d" % (a.shot_tag, a.tag, x, z)
        B.call("jawa/clear_ui", all=True)
        root = max(TH, TW * 9.0 / 16.0) / 2.0
        res = B.call("rimworld/screenshot_cell_rect", x=x, z=z, width=TW, height=TH, paddingCells=0, fileName=nm, rootSize=root)
        p = res.get("filePath") or res.get("path") or res.get("savedPath")
        for _ in range(40):
            if p and os.path.exists(p) and os.path.getsize(p) > 0:
                break
            time.sleep(0.5)
        time.sleep(1.0)
        if p and os.path.exists(p):
            shutil.copyfile(p, os.path.join(SHOTS, nm + ".png"))
            out.append((nm, x, z, n))
        else:
            print("SHOT FAILED", nm, json.dumps(res)[:200])
    print("tiles", json.dumps(out))


if __name__ == "__main__":
    main()
