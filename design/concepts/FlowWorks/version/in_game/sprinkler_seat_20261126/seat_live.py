"""SPRINKLER_HEAD_FIX_FLOATS_OFF_CURVE A2/A3, a deterministic state read (python.exe, RM_REPO set, a cleared test map).
Per look L (Scrapper, Industrial, Modern, Futuristic) at bx = 100 + 10 i:
  elbow group: pipes (bx,130) (bx+1,130) (bx,131) (bx+1,129); head on (bx,130) [mask N|E, want (+d,+d)], faucet on (bx+1,130)
  [mask S|W, want (-d,-d)], d = 0.5 - 0.5/sqrt2 = 0.1464 (RM_PipeSeatMath, every look).
  A3 row: pipes (bx..bx+3,134) + (bx+1,135); heads on (bx,134) end, (bx+1,134) tee, (bx+2,134) straight, lone pipe (bx+6,134):
  want (0,0) each. Move: a pipe added at (bx,133) makes (bx,134) an elbow E|S -> want (+d,-d); removed -> (0,0) again.
  Restyle: the elbow pipe (bx,130) restyled to the next look -> its head still at (+d,+d).
Reads RM_PipeSeat.Offset(head) (the offset Print draws at). Prints rows (name, want, got, PASS/FAIL/UNMEASURED) and captures."""
import json, math, os, re, shutil, sys, time
sys.path.insert(0, os.path.join(os.environ["RM_REPO"], "src", "RimMandrake", "FlowWorks", "northstar"))
import owner_look_regressions as O
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
D = 0.5 - 0.5 / math.sqrt(2)
TOL = 0.006          # Vector3.ToString prints F2: 0.005, plus float noise
rows, notes = [], []
def build(ops):
    r = O.call("jawa/build_batch", ops=ops, faction="player", wipeExisting=False)
    if r.get("survived") != len(ops.split(";")):
        notes.append("build %s: %s" % (ops[:80], str(r.get("failed"))[:200]))
def at(defname, x, z):
    for t in O.call("jawa/list_things", rect="%d,%d,1,1" % (x, z), limit=20).get("things") or []:
        if t.get("def") == defname:
            return str(t.get("id"))
    return None
def style(defname, x, z, st):
    tid = at(defname, x, z)
    r = O.call("jawa/set_thing_props", thing=tid, style=st) if tid else {"success": False}
    if r.get("success") is False:
        notes.append("style %s at %d,%d: %s" % (st, x, z, str(r)[:160]))
def offset(tid):
    r = O.static("RimMandrake.FlowWorks.Sprinklers.RM_PipeSeat", "Offset", tid)
    m = re.match(r"\(\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+)\)", r)
    return (float(m.group(1)), float(m.group(3))) if m else r
def judge(name, tid, want):
    if not tid:
        rows.append((name, want, "no thing", "UNMEASURED")); return
    got = offset(tid)
    if not isinstance(got, tuple):
        rows.append((name, want, str(got)[:120], "UNMEASURED")); return
    ok = abs(got[0] - want[0]) <= TOL and abs(got[1] - want[1]) <= TOL
    rows.append((name, [round(v, 4) for v in want], got, "PASS" if ok else "FAIL"))
O.call("jawa/destroy_batch", rects="98,127,45,10", categories="Plant")
for i, L in enumerate(LOOKS):
    bx = 100 + 10 * i
    pipes = [(bx, 130), (bx + 1, 130), (bx, 131), (bx + 1, 129)] + [(bx + k, 134) for k in range(4)] + [(bx + 1, 135), (bx + 6, 134)]
    build(";".join("RM_UniversalPipe:%d,%d" % p for p in pipes))
    for p in pipes:
        style("RM_UniversalPipe", p[0], p[1], "RM_UniversalPipe_" + L)
    build(";".join(["RM_SprinklerHead:%d,130" % bx, "RM_PipeFaucet:%d,130" % (bx + 1)]
                   + ["RM_SprinklerHead:%d,134" % (bx + k) for k in (0, 1, 2, 6)]))
O.call("jawa/map_commit")
for i, L in enumerate(LOOKS):
    bx = 100 + 10 * i
    judge("A2 %s head on elbow N|E" % L, at("RM_SprinklerHead", bx, 130), (D, D))
    judge("A2 %s faucet on elbow S|W" % L, at("RM_PipeFaucet", bx + 1, 130), (-D, -D))
    for k, kind in ((0, "end"), (1, "tee"), (2, "straight"), (6, "lone")):
        judge("A3 %s head on %s" % (L, kind), at("RM_SprinklerHead", bx + k, 134), (0.0, 0.0))
for i, L in enumerate(LOOKS):          # move: add a neighbour, then remove it
    bx = 100 + 10 * i
    build("RM_UniversalPipe:%d,133" % bx); style("RM_UniversalPipe", bx, 133, "RM_UniversalPipe_" + L)
    judge("A3 %s end becomes elbow E|S when a pipe is added" % L, at("RM_SprinklerHead", bx, 134), (D, -D))
    O.call("jawa/destroy_batch", rects="%d,133,1,1" % bx, categories="Building")
    judge("A3 %s back to an end when that pipe is removed" % L, at("RM_SprinklerHead", bx, 134), (0.0, 0.0))
    nxt = LOOKS[(i + 1) % 4]
    style("RM_UniversalPipe", bx, 130, "RM_UniversalPipe_" + nxt)
    judge("A3 %s elbow restyled %s keeps the head on the bend" % (L, nxt), at("RM_SprinklerHead", bx, 130), (D, D))
    style("RM_UniversalPipe", bx, 130, "RM_UniversalPipe_" + L)
O.call("jawa/map_commit")
shots = []
for i, L in enumerate(LOOKS):
    bx = 100 + 10 * i
    for name, x, z, w, h in (("elbow_" + L, bx - 1, 128, 4, 5), ("row_" + L, bx - 1, 133, 9, 3)):
        fn = "seat_%d_%s" % (int(time.time()), name); asked = time.time()
        r = O.call("rimworld/screenshot_cell_rect", x=x, z=z, width=w, height=h, paddingCells=0, fileName=fn, suppressMessage=True, rootSize=6.0)
        src, size = str(r.get("path") or ""), -1
        for _ in range(40):
            now = os.path.getsize(src) if src and os.path.isfile(src) else -1
            if now > 0 and now == size: break
            size = now; time.sleep(0.4)
        if src and os.path.isfile(src) and os.path.getmtime(src) >= asked - 2:
            dst = os.path.join(OUT, name + ".png"); shutil.copyfile(src, dst); shots.append(dst)
        else:
            notes.append("no capture " + name)
tally = {}
for r in rows: tally[r[3]] = tally.get(r[3], 0) + 1
print(json.dumps({"tally": tally, "rows": rows, "notes": notes, "shots": shots}, indent=1))
