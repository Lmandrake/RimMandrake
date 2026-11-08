"""bars2_common.py -- shared helpers for the pass-2 north-star bar staging on game A (ralph/live/bars2_*.py).

Shots go to the game's Screenshots folder as b2_<name>_<HHMMSS>.png (fetch: ralph/live/getshots.sh b2_ <dir>).
Every helper prints what it did; nothing here judges a bar (the owner judges by the picture).
"""
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fwb  # noqa: E402

ROOT = 7.2
LOG = os.path.join(fwb.REPO, "Transient", "ralph_fw", "bars2.log")
HPROBE = "RimMandrake.FlowWorks.Hose.HoseProbe"
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
SUSP = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
TRENCH = "RimMandrake.FlowWorks.RM_TrenchCover"
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
PARITY = "RimMandrake.FlowWorks.RM_LadderParity"
GATES = "RimMandrake.FlowWorks.RM_FlowDoorRules"


def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(s + "\n")


def j(o, n=600):
    return json.dumps(o, default=str)[:n]


def bridge():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    return fwb.FW()


ZOOMS = [float(z) for z in os.environ.get("B2_ZOOMS", "11,20").split(",")]


def shot(B, name, rect, root=None):
    """Frame once, let the game draw ~1.5 s, then capture under a unique name. root=None: one shot per ZOOMS entry
    (player zooms, rootSize 11 and 20), named b2_<name>_r<zoom>_<HHMMSS>; an explicit root is an extra close-up."""
    roots = ZOOMS if root is None else [root]
    path = None
    for rs in roots:
        kw = dict(x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=1, rootSize=rs, doNotResetCamera=True)
        B.call("rimworld/screenshot_cell_rect", fileName="b2_frame_tmp", **kw)
        time.sleep(1.5)
        r = B.call("rimworld/screenshot_cell_rect", fileName="b2_%s_r%g_%s" % (name, rs, time.strftime("%H%M%S")), **kw) or {}
        log("SHOT", name, "r%g" % rs, r.get("path") or r.get("message"))
        path = r.get("path") or path
    return path


def num(pid):
    m = re.search(r"(\d+)$", str(pid))
    return int(m.group(1)) if m else None


def clear(B, cells):
    for c in cells:
        B.call("jawa/clear_area", rect="%d,%d,1,1" % tuple(c), dryRun=False)


def dig(B, cells, d, fill=-1):
    """Bring each square to depth d notches (idempotent: excavation_drive's deepenLevels ADDS levels, so only the
    difference is dug; a square already deeper is logged, not filled). Each square is cleared first (clear_area removes
    pawns and things standing on it)."""
    out = []
    cells = [tuple(c) for c in cells]
    xs, zs = [c[0] for c in cells], [c[1] for c in cells]
    cur = depths(B, min(xs), min(zs), max(xs) - min(xs) + 1, max(zs) - min(zs) + 1) if cells else {}
    deeper = []
    for c in cells:
        B.call("jawa/clear_area", rect="%d,%d,1,1" % c, dryRun=False)
        have = cur.get(c) or 0
        if have > d:
            deeper.append((c, have))
        if d - have > 0:
            r = B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=d - have, setFill=fill) or {}
            out.append(r.get("success"))
    if deeper:
        log("DIG WARNING already deeper than", d, deeper[:6])
    return out


def square(x0, z0, w, h):
    return [(x0 + i, z0 + k) for i in range(w) for k in range(h)]


def depths(B, x, z, w, h):
    ex = B.call("jawa/flowworks_excavation_rect", x=x, z=z, w=w, h=h, onlyNonZero=True, includeTerrain=False) or {}
    return {(c.get("x"), c.get("z")): c.get("d") for c in ex.get("cells") or ex.get("rows") or []}


def spawn(B, cell, kind="Colonist", faction="player", draft=True):
    r = B.call("jawa/spawn_pawn", kindDef=kind, x=cell[0], z=cell[1], faction=faction, count=1) or {}
    pid = ((r.get("pawns") or [{}])[0]).get("id")
    if pid and draft and faction == "player":
        B.call("rimworld/set_draft", pawnId=pid, drafted=True)
    log("spawn", kind, faction, cell, "->", pid)
    return pid


def build(B, op, stuff=None):
    kw = dict(ops=op, faction="player")
    if stuff:
        kw["stuff"] = stuff
    r = B.call("jawa/build_batch", **kw) or {}
    log("build", op, stuff, j({k: r.get(k) for k in ("success", "placed", "survived", "failed", "message") if k in r}, 300))
    return r


def things(B, defname, rect):
    r = B.call("jawa/list_things", defName=defname, rect="%d,%d,%d,%d" % tuple(rect), limit=50) or {}
    return r.get("things") or r.get("rows") or []


def proof(B, typ, method, arg):
    r = B.call("jawa/static_call", type=typ, method=method, args=arg) or {}
    txt = str(r.get("result") or r.get("message") or r.get("error") or "")
    log("proof", typ.split(".")[-1] + "." + method, arg, "->", txt[:400])
    return txt


def hp(B, cmd):
    r = B.probe_of(HPROBE, cmd) or {}
    return r


def census(B, ids):
    r = B.call("jawa/pawn_census", ids=",".join(str(i) for i in ids if i)) or {}
    return r.get("pawns") or []


def where(B, ids):
    return [(p.get("id"), p.get("x"), p.get("z"), "DOWN" if p.get("downed") else "", "DEAD" if p.get("dead") else "")
            for p in census(B, ids)]


def hediffs(B, pid):
    r = B.call("jawa/list_pawns", includeHealth=True) or {}
    for p in r.get("pawns") or []:
        if p.get("id") == pid or str(p.get("thingId")) == str(pid):
            return [(h.get("def") or h.get("defName") or h.get("label"), h.get("part"), h.get("severity"))
                    for h in ((p.get("health") or {}).get("hediffs") or [])]
    return None


def play(B, ms, speed="Normal"):
    B.call("rimworld/play_for", durationMs=int(ms), speed=speed, forceRequestedSpeed=True)


def tick(B):
    return ((B.call("rimworld/get_game_info") or {}).get("state") or {}).get("tick")


def gizmos(B, thing_id):
    B.call("rimworld/clear_selection")
    B.call("jawa/select_things", ids=str(thing_id), action="select")
    gz = (B.call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
    return gz


def press(B, thing_id, label_part):
    gz = gizmos(B, thing_id)
    labels = [g.get("label") for g in gz]
    g = next((q for q in gz if label_part.lower() in str(q.get("label", "")).lower()), None)
    ok = None
    if g is not None:
        ok = (B.call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id")) or {}).get("success")
    log("press", thing_id, repr(label_part), "->", ok, "| gizmos:", labels)
    B.call("rimworld/clear_selection")
    return ok, labels
