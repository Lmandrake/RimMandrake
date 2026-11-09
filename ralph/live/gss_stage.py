#!/usr/bin/env python3
"""GSS sitting stager: load a played GSS colony, make it quiet, and put the camera on the spot the owner must judge.

Run from the ralph clone root with the Windows python (it is what reaches the bridge), like the loop's p12_look.py:

    cd /home/mandrake/rm/scratch/BENCH/ralph_gss
    python.exe -B D:\\ClaudeWork\\rimmandrake\\gss_sitting\\gss_stage.py status
    python.exe -B D:\\ClaudeWork\\rimmandrake\\gss_sitting\\gss_stage.py load Modern          # load, quiet, bends count, camera on the lamp
    python.exe -B D:\\ClaudeWork\\rimmandrake\\gss_sitting\\gss_stage.py spot Modern heap     # lamp | heap | mast | strips | span
    python.exe -B D:\\ClaudeWork\\rimmandrake\\gss_sitting\\gss_stage.py bends Modern         # the measured half, no load
    python.exe -B D:\\ClaudeWork\\rimmandrake\\gss_sitting\\gss_stage.py restore              # raids back as found

HARD RULES (lesson 20261108T171957Z): this script NEVER calls rimworld/set_time_speed and never steps ticks; the owner
runs the clock. It only READS the clock, and says PAUSED or RUNNING. It never takes a screenshot unless --shot, and never
hides his UI. Raids off is applied after every load (threatScale 0, allowBigThreats false, incident queue cleared) and the
prior values are saved to PRIOR for `restore`.
Never use it for a flyer. It stages no pawns, spawns nothing, builds nothing: the four colonies are saved play-throughs.
"""
import json
import os
import sys
import time

REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "northstar_matrix"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import run_live as RL  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PRIOR = os.path.join(HERE, "prior_difficulty.json")
EVID = os.path.join(HERE, "evidence")
SAVE_SRC = os.path.join(HERE, "saves")
SAVES_DIR = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves")

# ralph/live/ba_state.json on Steve, 2026-11-07 17:11: each colony's origin; a site cell (x, z) is world (ox + x, oz + z)
ORIGIN = {"Modern": (140, 100), "Scrapper": (65, 80), "Industrial": (40, 60), "Futuristic": (90, 160)}
# the sites' own cells (x, z, w, h). The camera root is max(h, w*9/16)/2, the same play zoom the loop's shots used.
SPOTS = {
    "lamp": (-2, 8, 14, 8),      # the two bedrooms: standing lamps, beds, (Modern) the power strips; RATCHET bar item 2 (lamp lead hook)
    "heap": (38, -11, 24, 12),   # the dense conduit block at (42..46, -9..-5): RATCHET item 4 (the heap), the p15e/p18 frame
    "mast": (33, -1, 14, 9),     # first mast (39, 2): pole box, wall plate, junction box below; RATCHET item 3 (mast foot)
    "strips": (13, 0, 13, 11),   # the rec room: Modern strip hooks at sockets, judged by the eye not the count
    "span": (36, -6, 40, 18),    # the overhead span between the masts (not a bar; for the cut look)
}
ORDER = ["lamp", "heap", "mast"]
LOOKS = ["Modern", "Scrapper", "Industrial", "Futuristic"]


def ok(r):
    return isinstance(r, dict) and r.get("success") is not False


def clock(B):
    t1 = B.call("jawa/map_info").get("ticksGame")
    time.sleep(1.5)
    t2 = B.call("jawa/map_info").get("ticksGame")
    return t1, t2, ("PAUSED" if t1 is not None and t1 == t2 else "RUNNING")


def cell(look, spot):
    ox, oz = ORIGIN[look]
    x, z, w, h = SPOTS[spot]
    return ox + x + w / 2.0, oz + z + h / 2.0, max(h, w * 9.0 / 16.0) / 2.0


def go(B, look, spot, shot=False):
    cx, cz, root = cell(look, spot)
    r1 = B.call("rimworld/jump_camera_to_cell", x=int(round(cx)), z=int(round(cz)))
    r2 = B.call("rimworld/set_camera_zoom", rootSize=root)
    time.sleep(1.0)
    cam = B.call("rimworld/get_camera_state")
    print("CAMERA %s %s: cell (%d,%d) root %.1f jump=%s zoom=%s settled=%s" % (look, spot, round(cx), round(cz), root, ok(r1), ok(r2), cam.get("rootSize")))
    if shot:
        os.makedirs(EVID, exist_ok=True)
        x, z, w, h = SPOTS[spot]
        ox, oz = ORIGIN[look]
        B.call("jawa/clear_ui", all=True)
        res = B.call("rimworld/screenshot_cell_rect", x=x + ox, z=z + oz, width=w, height=h, paddingCells=0,
                     fileName="gss_sitting_%s_%s" % (look, spot), rootSize=root)
        print("SHOT", res.get("filePath") or res.get("path"))


def bends(B, look=None):
    b = B.probe("bends")
    t = b.get("tally") or {}
    print("BENDS %s world=%s strands=%s bends=%s UNFORCED=%s why=%s" % (look, b.get("world"), t.get("strands"), t.get("bends"), t.get("unforced"), json.dumps(t.get("why"))[:200]))
    os.makedirs(EVID, exist_ok=True)
    json.dump(b, open(os.path.join(EVID, "bends_%s_%s.json" % (look, time.strftime("%H%M%S"))), "w"))
    return t.get("unforced")


def tune_values(r):
    # jawa/difficulty_tune nests its values under "before"/"after" (top level holds only success, difficultyDef, state)
    return (r or {}).get("after") or (r or {}).get("before") or {}


def quiet(B):
    prior = tune_values(B.call("jawa/difficulty_tune"))
    keep = {k: prior.get(k) for k in ("threatScale", "allowBigThreats")}
    if any(v is None for v in keep.values()):
        print("RAIDS UNMEASURED: difficulty_tune gave no prior values; PRIOR not written, raids-off still applied")
    elif not os.path.exists(PRIOR):
        json.dump(keep, open(PRIOR, "w"))
    B.call("jawa/difficulty_tune", threatScale=0, allowBigThreats=False)
    after = tune_values(B.call("jawa/difficulty_tune"))
    q = B.call("jawa/incident_queue_clear")
    print("RAIDS threatScale %s->%s allowBigThreats %s->%s queue cleared %s" % (keep["threatScale"], after.get("threatScale"), keep["allowBigThreats"], after.get("allowBigThreats"), q.get("clearedCount")))
    try:
        rows = B.call("jawa/list_pawns", limit=500).get("pawns") or []
        hostile = [p for p in rows if p.get("hostile") and not p.get("dead")]
        print("HOSTILES standing: %d of %d pawns (read only; none touched)" % (len(hostile), len(rows)))
    except Exception as e:
        print("HOSTILES UNMEASURED:", repr(e)[:120])


def load(B, look, shot=False):
    src = os.path.join(SAVE_SRC, "gss_ba_%s.rws" % look)
    dst = os.path.join(SAVES_DIR, "gss_ba_%s.rws" % look)
    if not os.path.exists(dst) and os.path.exists(src):
        import shutil
        shutil.copyfile(src, dst)
        print("COPIED save into the Saves folder:", dst)
    r = B.call("rimworld/load_game_ready", saveName="gss_ba_%s" % look, timeoutMs=240000)
    print("LOAD", look, json.dumps(r)[:140])
    from await_lifecycle import await_lifecycle
    lc = await_lifecycle(B.call, "map_ready", 240, poll_s=0.5)
    print("MAP_READY", lc.ok, lc.reason)
    if not lc.ok:
        print("STOP: not ready; a dialog may be open (python.exe ralph/live/close_dialogs.py clears it)")
        return 2
    time.sleep(8)                                  # the cord lay is frame-sliced after a load; let it finish before anyone looks
    census = B.probe("census")
    print("CENSUS pending=%s strands=%s" % (census.get("pending"), census.get("strands")))
    quiet(B)
    t1, t2, state = clock(B)
    print("CLOCK ticksGame %s -> %s %s%s" % (t1, t2, state, "  (owner: pause it yourself; this script never touches speed)" if state == "RUNNING" else ""))
    bends(B, look)
    go(B, look, ORDER[0], shot)
    return 0


def restore():
    if not os.path.exists(PRIOR):
        print("no prior difficulty saved; nothing to restore")
        return 1
    keep = {k: v for k, v in json.load(open(PRIOR)).items() if v is not None}
    B = RL.LiveBridge()
    B.call("jawa/difficulty_tune", **keep)
    if not keep:
        print("prior file holds no values; nothing restored (PRIOR kept)")
        return 1
    now = tune_values(B.call("jawa/difficulty_tune"))
    print("restored", keep, "now", {k: now.get(k) for k in keep})
    os.unlink(PRIOR)
    return 0


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    shot = "--shot" in sys.argv
    if not a:
        print(__doc__)
        return 64
    if a[0] == "restore":
        return restore()
    B = RL.LiveBridge()
    if a[0] == "status":
        try:
            print("GAME", json.dumps(B.call("rimworld/get_game_info"))[:300])
        except Exception as e:
            print("GAME UNMEASURED:", repr(e)[:120])
        mi = B.call("jawa/map_info")
        print("MAP", mi.get("mapId"), mi.get("sizeX"), mi.get("sizeZ"), "ticksGame", mi.get("ticksGame"))
        print("CLOCK", clock(B))
        print("GSS probe census", json.dumps(B.probe("census", wait_s=8))[:240])
        return 0
    look = a[1] if len(a) > 1 else None
    if look not in ORIGIN:
        print("look must be one of", LOOKS)
        return 64
    if a[0] == "load":
        return load(B, look, shot)
    if a[0] == "spot":
        go(B, look, a[2] if len(a) > 2 else "lamp", shot)
        return 0
    if a[0] == "bends":
        bends(B, look)
        return 0
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main())
