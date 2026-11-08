"""story1.py -- the owner's covered-pit-trap story (2026-11-04), played on an ordinary quicktest map on game A.

  python.exe ralph/live/story1.py stage   [--d 4] [--cover RM_PitCover_PlankLattice]
  python.exe ralph/live/story1.py raid    [--points 250] [--faction TribeRough]
  python.exe ralph/live/story1.py watch   [--ticks 20000] [--slice 120]
  python.exe ralph/live/story1.py look    <name>          one play-zoom shot of the passage + a pawn read

Layout (cells): a walled compound round the colonists with ONE doorway in its south wall at (GX, CZ0); a 3-wide passage
walled on both sides runs south from the doorway; a covered, spiked pit 3 x 2 lies across the passage. Shots go to the
game's Screenshots folder with the prefix s1_ and a time stamp (unique names: the tool writes asynchronously).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fwb  # noqa: E402

# the layout is placed round the colonists: SHIFT moves it (env FW_SHIFT="dx,dz", default 0,0 = the first map's spot)
_SX, _SZ = (int(v) for v in os.environ.get("FW_SHIFT", "0,0").split(","))
GX = 140 + _SX                # doorway x
CX0, CX1, CZ0, CZ1 = 133 + _SX, 147 + _SX, 132 + _SZ, 146 + _SZ   # compound walls
PZ0, PZ1 = 118 + _SZ, 131 + _SZ   # passage walls run z = PZ0..PZ1 at x = GX-2 and GX+2
PIT = [(x, z) for x in range(GX - 1, GX + 2) for z in (124 + _SZ, 125 + _SZ)]
PZ = 124 + _SZ
VIEW = (GX - 6, 119 + _SZ, 13, 12)  # the play-zoom frame: passage, pit and doorway
ROOT = float(os.environ.get("FW_ROOT", "20"))   # play zoom: root 20 ~23 px a cell on Steve (7.2 was closer than a player can zoom)
STATE = os.path.join(fwb.REPO, "Transient", "ralph_fw", "story1_state.json")
LOG = os.path.join(fwb.REPO, "Transient", "ralph_fw", "story1.log")


def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(s + "\n")


def load():
    try:
        return json.load(open(STATE))
    except Exception:  # noqa: BLE001
        return {}


def save(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as f:
        json.dump(st, f, indent=1)


def ops(defname, cells, rot=None):
    return ";".join("%s:%d,%d%s" % (defname, x, z, "" if rot is None else ",%d" % rot) for x, z in cells)


def shot(B, name, rect=VIEW, root=ROOT):
    # frame first and let the game draw a few frames: a capture straight after a camera move misses the pawns
    B.call("rimworld/screenshot_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=1,
           rootSize=root, doNotResetCamera=True, fileName="s1_frame_tmp")
    time.sleep(1.5)
    r = B.call("rimworld/screenshot_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=1,
               rootSize=root, doNotResetCamera=True, fileName="s1_%s_%s" % (name, time.strftime("%H%M%S"))) or {}
    log("SHOT", name, r.get("path") or r.get("message"))
    return r.get("path")


def pawns(B, faction):
    r = B.call("jawa/pawn_census", faction=faction, includeDead=True) or {}
    out = []
    for p in r.get("pawns") or []:
        if p.get("kindDef") in ("Cat", "Dog") or (faction == "player" and not p.get("isColonist")):
            continue
        out.append(p)
    return out


def brief(p):
    job = p.get("job") or p.get("curJob") or {}
    jd = job.get("def") if isinstance(job, dict) else job
    return "%s(%s) %d,%d%s%s job=%s" % (p.get("name"), p.get("kindDef"), p.get("x", -1), p.get("z", -1),
                                         " DOWN" if p.get("downed") else "", " DEAD" if p.get("dead") else "", jd)


def pit_read(B):
    r = B.call("jawa/flowworks_pit_report", x=PIT[0][0], z=PIT[0][1]) or {}
    ps = r.get("pawns") or r.get("occupants") or []
    return r, ps


def stage(B, a):
    st = load()
    cells_walls = []
    for x in range(CX0, CX1 + 1):
        cells_walls += [(x, CZ0), (x, CZ1)]
    for z in range(CZ0 + 1, CZ1):
        cells_walls += [(CX0, z), (CX1, z)]
    cells_walls = [c for c in cells_walls if c != (GX, CZ0)]
    for z in range(PZ0, PZ1 + 1):
        cells_walls += [(GX - 2, z), (GX + 2, z)]
    # a player's colonists would cut the plants under the walls and the pit: clear just those cells
    for c in cells_walls + PIT:
        B.call("jawa/clear_area", rect="%d,%d,1,1" % c, dryRun=False)
    r = B.call("jawa/build_batch", ops=ops("Wall", cells_walls), stuff="BlocksGranite", faction="player", readBack=2) or {}
    log("walls", {k: r.get(k) for k in ("success", "placed", "survived", "failed") if k in r})
    shot(B, "00_passage_undug")
    for c in PIT:
        B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=a.d, setFill=-1)
    B.step(5)
    ex = B.call("jawa/flowworks_excavation_rect", x=GX - 1, z=PZ, w=3, h=2, includeTerrain=True) or {}
    log("dug", [(c.get("x"), c.get("z"), c.get("d"), c.get("terrain")) for c in ex.get("cells") or ex.get("rows") or []])
    shot(B, "01_pit_open")
    r = B.call("jawa/build_batch", ops=ops("RM_Spikes", PIT), stuff="WoodLog", faction="player", readBack=1) or {}
    log("spikes", {k: r.get(k) for k in ("success", "placed", "survived", "failed", "message") if k in r})
    shot(B, "02_pit_spiked")
    r = B.call("jawa/build_batch", ops=ops(a.cover, PIT), stuff="WoodLog", faction="player", readBack=1) or {}
    log("cover", {k: r.get(k) for k in ("success", "placed", "survived", "failed", "message") if k in r})
    B.step(5)
    shot(B, "03_pit_covered")
    shot(B, "04_pit_covered_close", rect=(GX - 3, PZ - 2, 7, 6), root=4.0)
    # his story: "the defenders standing on the other side begin peppering them with arrows" -- three archers drafted in the
    # passage just north of the pit, the colony side
    r = B.call("jawa/spawn_pawn", kindDef="Tribal_Archer", x=GX, z=PZ + 4, faction="player", count=3) or {}
    aids = [p.get("id") for p in r.get("pawns") or [] if p.get("id")]
    for pid, dx in zip(aids, (-1, 0, 1)):
        o = B.call("jawa/order_pawn", pawnId=pid, x=GX + dx, z=PZ + 4, draft=True, waitTicks=120) or {}
        log("archer", pid, json.dumps(o, default=str)[:200])
    st.update(staged=True, d=a.d, cover=a.cover)
    save(st)


def raid(B, a):
    cols = pawns(B, "player")
    ids = ",".join(p["id"] for p in cols)
    spots = [(GX - 1, CZ0 + 3), (GX + 1, CZ0 + 3), (GX, CZ0 + 4), (GX - 2, CZ0 + 2), (GX + 2, CZ0 + 2)]
    for p, s in zip([c for c in cols if c.get("kindDef") != "Tribal_Archer"], spots):
        o = B.call("jawa/order_pawn", pawnId=p["id"], x=s[0], z=s[1], draft=True, waitTicks=0) or {}
        log("order", p.get("name"), s, json.dumps(o, default=str)[:160])
    log("colonists", [brief(p) for p in cols])
    kw = dict(incidentDef="RaidEnemy", points=a.points, forced=True, dryRun=False)
    if a.faction:
        kw["faction"] = a.faction
    r = B.call("jawa/fire_incident", **kw) or {}
    log("raid", json.dumps(r, default=str)[:1500])
    st = load()
    st["raid_tick"] = (B.call("rimworld/get_game_info") or {}).get("state", {}).get("tick")
    save(st)


def watch(B, a):
    t0 = time.time()
    done = 0
    k = 0
    near_seen = False
    while done < a.ticks:
        hs = pawns(B, "hostile")
        alive = [p for p in hs if not p.get("dead")]
        near = [p for p in alive if abs(p.get("x", 0) - GX) <= 14 and abs(p.get("z", 0) - PZ) <= 16]
        # real-time play, not step_game_ticks: a stepped tick runs no per-frame visuals, so pawns stay drawn at a stale spot
        step = a.slice if near else 600
        mult = {"Normal": 1, "Fast": 3, "Superfast": 6, "Ultrafast": 15}[a.speed]
        B.call("rimworld/play_for", durationMs=int(step * 1000 / (60 * mult)), speed=a.speed, forceRequestedSpeed=True)
        done += step
        hs = pawns(B, "hostile")
        rep, occ = pit_read(B)
        line = "t+%d hostiles=%d near=%d | %s | pit: %s" % (
            done, len([p for p in hs if not p.get("dead")]), len(near), "; ".join(brief(p) for p in hs)[:900],
            json.dumps(occ, default=str)[:600])
        log(line)
        if near or near_seen:
            near_seen = True
            k += 1
            if k % a.every == 0:
                shot(B, "w%03d" % k)
        if time.time() - t0 > a.wall:
            log("wall-clock budget spent")
            break
        if near_seen and not [p for p in hs if not p.get("dead") and not p.get("downed")
                              and abs(p.get("x", 0) - GX) <= 30 and abs(p.get("z", 0) - PZ) <= 30]:
            log("no hostile on its feet within 30 cells: stop")
            break


def look(B, a):
    shot(B, a.name)
    log("hostiles", "; ".join(brief(p) for p in pawns(B, "hostile")))
    log("colonists", "; ".join(brief(p) for p in pawns(B, "player")))
    rep, occ = pit_read(B)
    log("pit", json.dumps(rep, default=str)[:2500])


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(os.path.join(os.path.dirname(STATE), "story1.pid"), "w") as f:
        f.write(str(os.getpid()))
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("name", nargs="?", default="look")
    ap.add_argument("--d", type=int, default=4)
    ap.add_argument("--cover", default="RM_PitCover_WovenScrap")
    ap.add_argument("--points", type=float, default=250)
    ap.add_argument("--faction", default="TribeRough")
    ap.add_argument("--ticks", type=int, default=20000)
    ap.add_argument("--slice", type=int, default=120)
    ap.add_argument("--every", type=int, default=1)
    ap.add_argument("--speed", default="Fast")
    ap.add_argument("--wall", type=float, default=1500)
    a = ap.parse_args()
    B = fwb.FW()
    dict(stage=stage, raid=raid, watch=watch, look=look)[a.cmd](B, a)


if __name__ == "__main__":
    main()
