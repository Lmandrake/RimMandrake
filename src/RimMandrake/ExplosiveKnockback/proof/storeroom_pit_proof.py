"""Live proof: a bomb in a storeroom beside a pit throws goods AND people into the pit (owner's flagship sentence,
2026-11-12: "Just put a bomb into a storeroom with people in it beside a pit. Shows some items falling into the pit
and some people as well.").

Scene: the saved EK sitting Station 1 (25 x Shell_HighExplosive, blast radius 6.0, at the room's middle; the open
east side 5 cells from the bomb is a FlowWorks superdeep pit; five drafted colonists in flak; sturdy and fragile goods).

Three arms, each reloading the save:
  A  defaults (thrown goods take 25% blast damage, wall impact 10/cell)  -> >=K stacks and >=1 colonist in pit cells,
     0 goods stacks destroyed, 0 colonists dead, goods hitting a wall are journalled
  B  thrownGoodsBlastDamagePercent=100 (vanilla damage)                    -> >=1 fragile stack destroyed, nothing spared
  C  enabled=False (knockback off)                                         -> no goods stack and no colonist thrown

--storage (RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED, owner ruling 2026-11-11 "(1) but the closed containers may
themselves get shoved a bit"; 2026-11-12 "Anything that draws its contents is open"): a scene of two open shelves and
one container that hides its contents (default LWM's Deep Storage weapons locker, lwm.deepstorage on the list, holding
weapons its filter accepts). The proof never tags a def closed; RM_KnockbackProof.IsClosed must read CLOSED for it by the
shipped rule, else the arm fails. The 2026-11-12 save EK_SITTING_STATION1_STORAGE_20261112 holds a Hopper, which is OPEN:
it must be restaged with a hiding container before this arm can pass.
Two arms, each reloading the save; every row can fail alone:
  SA  defaults                 -> SA_OPEN_SHELF_THROWN    every good on a shelf moved
                                  SA_CLOSED_GOODS_STAY    no good in the container thrown (at its start or carried)
                                  SA_CONTAINER_RULE       one "container" line; thrown = off its cell, not pit/pawn,
                                                          the goods with it; jolt = unmoved
                                  SA_NO_IN_STORAGE_SKIP   no "in_storage" skip line (the old rule is off)
  SC  enabled=False            -> SC_OFF_SHELF_GOODS_NOT_THROWN, SC_OFF_CONTAINER_STILL, SC_OFF_NO_CONTAINER_LINE

Usage (python.exe from WSL, bridge held):
  storeroom_pit_proof.py [--save NAME] [--site x,z,w,h] [--pit x,z,w,h] [--k 3] [--out evidence.json]
  storeroom_pit_proof.py --storage [--save EK_SITTING_STATION1_STORAGE_20261112] [--shelves x,z;x,z] [--container x,z]
Prints one PASS/FAIL/UNMEASURED table. Exit 0 only if every row passes."""
import argparse, collections, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "FlowWorks", "northstar"))
import proof_hose as PH  # noqa: E402

KP = "RimMandrake.ExplosiveKnockback.RM_KnockbackProof"
ap = argparse.ArgumentParser()
ap.add_argument("--save", default=None, help="default EK_SITTING_STATION1_STOREROOM_PIT_20261112 (--storage: _STORAGE_)")
ap.add_argument("--storage", action="store_true", help="run the open-shelf / closed-container arms instead")
ap.add_argument("--shelves", default="120,122;120,126", help="shelf anchor cells (stage_station1_v2 storage layout)")
ap.add_argument("--container", default="122,126", help="the container's cell")
ap.add_argument("--container-def", default="LWM_WeaponsLocker", help="a building def that hides its contents (closed by the shipped rule, never tagged)")
ap.add_argument("--site", default="114,117,22,15", help="census rect x,z,w,h around the room and pit")
ap.add_argument("--pit", default="128,122,4,5", help="pit cells x,z,w,h")
ap.add_argument("--k", type=int, default=3, help="min goods stacks that must end in pit cells (arm A)")
ap.add_argument("--ticks", type=int, default=300)
ap.add_argument("--out", default=None)
a = ap.parse_args()
a.save = a.save or ("EK_SITTING_STATION1_STORAGE_20261112" if a.storage else "EK_SITTING_STATION1_STOREROOM_PIT_20261112")
B = PH.PB()
sys.path.insert(0, os.path.join(HERE, ".."))
from proof_build_gate import require_proof_build  # noqa: E402
px, pz, pw, ph = (int(v) for v in a.pit.split(","))
rows, ev = [], {"save": a.save}


def c(tool, **kw):
    try:
        return B.call(tool, **kw) or {}
    except Exception as e:  # noqa: BLE001
        return {"success": False, "exc": repr(e)[:300]}


def row(rid, ok, det):
    st = ok if isinstance(ok, str) else ("PASS" if ok else "FAIL")
    rows.append((rid, st, det))


def in_pit(x, z):
    return x is not None and z is not None and px <= x < px + pw and pz <= z < pz + ph


def census():
    """Haulable things (goods, shells, corpses) in the site; never buildings."""
    return c("jawa/list_things", rect=a.site, group="HaulableEver", limit=2000).get("things") or []


def pawns_in_site():
    x, z, w, h = (int(v) for v in a.site.split(","))
    return {p["id"]: p for p in c("jawa/list_pawns", limit=400).get("pawns") or []
            if x <= (p.get("x") or -1) < x + w and z <= (p.get("z") or -1) < z + h}


def load():
    c("rimworld/load_game", saveName=a.save)
    PH.V._wait_playing(B, leave_s=3)
    c("rimworld/set_time_speed", speed=0)


def arm(name, settings):
    load()
    c("jawa/static_call", type=KP, method="Settings", args="reset")
    for kv in settings:
        r = str(c("jawa/static_call", type=KP, method="Settings", args=kv).get("result"))
        if not r.startswith("SET"):
            row(name + "_SETTING", False, "%s -> %s" % (kv, r[:120]))
    things = census()
    shells = [t for t in things if str(t.get("def")).startswith("Shell_")]
    if not shells:
        row(name + "_BOMB", False, "no Shell_ thing in %s" % a.site)
        return None
    bomb = shells[0]
    bx, bz = bomb["x"], bomb["z"]
    near = lambda t: math.hypot(t["x"] - bx, t["z"] - bz) <= 6.0
    goods = {t["id"]: t for t in things if t is not bomb and near(t)}
    pawns = {i: p for i, p in pawns_in_site().items() if near(p)}
    c("jawa/static_call", type=KP, method="Clear", args="x")
    c("jawa/damage", thingId=bomb["id"], damageDef="Crush", amount=float(bomb.get("hitPoints") or 60) + 40.0)
    # one step of the same ticks (it was a.ticks//25 calls of 25 with nothing read between): the client sends it through
    # tickburst_step.advance, many ticks per frame (speed_20261112; RM_STEP_PATH=slow is one tick per frame)
    c("rimworld/step_game_ticks", ticks=max(1, a.ticks // 25) * 25, pauseFirst=True, timeoutMs=120000)
    after = {t["id"]: t for t in census()}
    lp2 = pawns_in_site()
    g = collections.Counter()
    for tid, t in goods.items():
        n = after.get(tid)
        # a stack counts as in_pit only if it MOVED there (staging can leave dropped clothes on pit cells)
        g["destroyed" if n is None else "still" if (n["x"], n["z"]) == (t["x"], t["z"]) else
          "in_pit" if in_pit(n["x"], n["z"]) else "moved"] += 1
    p = collections.Counter()
    for pid, t in pawns.items():
        n = lp2.get(pid)
        if n is None or n.get("dead"):
            p["dead"] += 1
            continue
        p["still" if (n.get("x"), n.get("z")) == (t["x"], t["z"]) else
          "in_pit" if in_pit(n.get("x"), n.get("z")) else "moved"] += 1
    jl = (c("jawa/static_call", type=KP, method="Journal", args="400").get("result") or "").splitlines()
    j = collections.Counter(json.loads(x).get("type") for x in jl if x.startswith("{"))
    res = {"bomb": [bx, bz, bomb.get("stackCount")], "goods_n": len(goods), "pawns_n": len(pawns),
           "goods": dict(g), "pawns": dict(p), "journal": dict(j)}
    ev[name] = res
    row(name + "_START", len(pawns) >= 5 and len(goods) >= 12,
        "bomb %s x%s; %d colonists, %d goods stacks within r6" % ((bx, bz), bomb.get("stackCount"), len(pawns), len(goods)))
    return res


def buildings(rect):
    return c("jawa/list_things", rect=rect, group="BuildingArtificial", limit=400).get("things") or []


def storage_arm(name, settings):
    """One reload: check the container def is closed by the shipped rule, apply settings, fire the bomb, and return before/after of the shelf
    goods, the container goods and the container itself, plus the journal lines."""
    load()
    c("jawa/static_call", type=KP, method="Settings", args="reset")
    cs = str(c("jawa/static_call", type=KP, method="IsClosed", args=a.container_def).get("result"))
    if not cs.startswith("CLOSED"):
        row(name + "_CONTAINER_CLOSED", False, cs[:120])
        return None
    for kv in settings:
        r = str(c("jawa/static_call", type=KP, method="Settings", args=kv).get("result"))
        if not r.startswith("SET"):
            row(name + "_SETTING", False, "%s -> %s" % (kv, r[:120]))
    cx, cz = (int(v) for v in a.container.split(","))
    shelf_cells = set()
    for sxz in a.shelves.split(";"):
        sx, sz = (int(v) for v in sxz.split(","))
        shelf_cells |= {(sx - 1, sz), (sx, sz), (sx + 1, sz)}  # a 2x1 shelf covers its anchor and one side
    cont = [b for b in buildings("%d,%d,1,1" % (cx, cz)) if b.get("def") == a.container_def]
    things = census()
    shells = [t for t in things if str(t.get("def")).startswith("Shell_")]
    if not cont or not shells:
        row(name + "_START", False, "container %s at %s: %d; bombs %d" % (a.container_def, a.container, len(cont), len(shells)))
        return None
    on_shelf = {t["id"]: t for t in things if (t["x"], t["z"]) in shelf_cells}
    in_cont = {t["id"]: t for t in things if (t["x"], t["z"]) == (cx, cz)}
    row(name + "_START", len(on_shelf) >= 2 and len(in_cont) >= 1,
        "%d goods on shelves %s, %d in %s" % (len(on_shelf), sorted(shelf_cells), len(in_cont), a.container_def))
    bomb = shells[0]
    c("jawa/static_call", type=KP, method="Clear", args="x")
    c("jawa/damage", thingId=bomb["id"], damageDef="Crush", amount=float(bomb.get("hitPoints") or 60) + 40.0)
    # one step of the same ticks (it was a.ticks//25 calls of 25 with nothing read between): the client sends it through
    # tickburst_step.advance, many ticks per frame (speed_20261112; RM_STEP_PATH=slow is one tick per frame)
    c("rimworld/step_game_ticks", ticks=max(1, a.ticks // 25) * 25, pauseFirst=True, timeoutMs=120000)
    after = {t["id"]: t for t in census()}
    x, z, w, h = (int(v) for v in a.site.split(","))
    cont2 = [b for b in buildings(a.site) if b.get("def") == a.container_def and b.get("id") == cont[0].get("id")]
    jl = [json.loads(l) for l in (c("jawa/static_call", type=KP, method="Journal", args="400").get("result") or "").splitlines()
          if l.startswith("{")]
    res = {"container": [cx, cz], "container_after": [cont2[0]["x"], cont2[0]["z"]] if cont2 else None,
           "shelf": {i: [t["x"], t["z"], (after.get(i) or {}).get("x"), (after.get(i) or {}).get("z")] for i, t in on_shelf.items()},
           "held": {i: [t["x"], t["z"], (after.get(i) or {}).get("x"), (after.get(i) or {}).get("z")] for i, t in in_cont.items()},
           "pawn_cells": [[p.get("x"), p.get("z")] for p in pawns_in_site().values()],
           "container_lines": [j for j in jl if j.get("type") == "container"],
           "skips": collections.Counter(j.get("reason") for j in jl if j.get("type") == "skip"),
           "journal": collections.Counter(j.get("type") for j in jl)}
    ev[name] = res
    return res


def moved(v):
    return v[2] is not None and (v[2], v[3]) != (v[0], v[1])


# release DLL (no RM_KnockbackProof): exit 3 PROOF BUILD REQUIRED before any load, never a table of FAILs
require_proof_build(c("jawa/static_call", type=KP, method="Names", args="x"))
if a.storage:
    S = storage_arm("SA", [])
    if S:
        sh = S["shelf"].values()
        row("SA_OPEN_SHELF_THROWN", bool(sh) and all(moved(v) for v in sh),
            "%d/%d shelf goods moved (destroyed counts as not moved)" % (sum(moved(v) for v in sh), len(S["shelf"])))
        end = tuple(S["container_after"] or ())
        stay = [v for v in S["held"].values() if v[2] is not None and (v[2], v[3]) in {(v[0], v[1]), end}]
        row("SA_CLOSED_GOODS_STAY", bool(S["held"]) and len(stay) == len(S["held"]) and S["skips"].get("closed_container", 0) >= 1,
            "%d/%d container goods at start or carried; closed_container skips %d" % (
                len(stay), len(S["held"]), S["skips"].get("closed_container", 0)))
        # fails alone when the blast destroys the container (a staging defect, not the rule): the 25-shell storeroom
        # destroyed every Hopper (RIMMANDRAKE_STAGE_KNOCKBACK_CONTAINER_SURVIVES_BLAST); Station 5 uses 3 shells
        row("SA_CONTAINER_SURVIVES", S["container_after"] is not None, "container %s -> %s" % (S["container"], S["container_after"]))
        cl = S["container_lines"]
        ok, det = False, "lines %s" % cl
        if len(cl) == 1 and S["container_after"]:
            l = cl[0]
            to, frm = tuple(l.get("to") or ()), tuple(l.get("from") or ())
            if l.get("action") == "thrown":
                # owner 2026-11-12: thrown whole (RIMMANDRAKE_THROW_CLOSED_CRATES_WHOLE_CONTENTS_RIDE_SAFE); it lands on its
                # planned cell or, if that filled meanwhile, the nearest free one, never in a pit or on a pawn, goods with it
                ok = (bool(end) and end != frm and not in_pit(*end) and list(end) not in S["pawn_cells"]
                      and all((v[2], v[3]) == end for v in S["held"].values() if v[2] is not None))
            elif l.get("action") == "jolt":
                ok = end == frm == tuple(S["container"])
            det = "%s %s->%s after %s mass %s" % (l.get("action"), frm, to, end, l.get("mass"))
        row("SA_CONTAINER_RULE", ok, det)
        row("SA_NO_IN_STORAGE_SKIP", S["skips"].get("in_storage", 0) == 0, str(dict(S["skips"])))
    S = storage_arm("SC", ["enabled=False"])
    if S:
        # a shelf the blast destroys drops leavings that vanilla GenSpawn may nudge a stack one cell aside, so "still" is
        # wrong (RIMMANDRAKE_STAGE_KNOCKBACK_CONTAINER_SURVIVES_BLAST): off means no item_move line and no stack >1 cell away
        far = [i for i, v in S["shelf"].items() if v[2] is not None and max(abs(v[2] - v[0]), abs(v[3] - v[1])) > 1]
        row("SC_OFF_SHELF_GOODS_NOT_THROWN", S["journal"].get("item_move", 0) == 0 and not far,
            "item_move %d; >1 cell %s; %s" % (S["journal"].get("item_move", 0), far, str(S["shelf"])[:120]))
        row("SC_OFF_CONTAINER_STILL", S["container_after"] == S["container"], "%s -> %s" % (S["container"], S["container_after"]))
        row("SC_OFF_NO_CONTAINER_LINE", not S["container_lines"], str(dict(S["journal"])))
    A = Bm = C = None
else:
    A = arm("A", [])
if A:
    row("A_GOODS_IN_PIT", A["goods"].get("in_pit", 0) >= a.k, "%s (need >=%d in pit)" % (A["goods"], a.k))
    row("A_PAWN_IN_PIT", A["pawns"].get("in_pit", 0) >= 1, str(A["pawns"]))
    row("A_NO_GOODS_DESTROYED", A["goods"].get("destroyed", 0) == 0, str(A["goods"]))
    row("A_NO_COLONIST_DEAD", A["pawns"].get("dead", 0) == 0, str(A["pawns"]))
    row("A_SPARED_JOURNALLED", A["journal"].get("spared", 0) >= 1, str(A["journal"]))
    row("A_WALL_IMPACT_JOURNALLED", A["journal"].get("goods_impact", 0) >= 1, str(A["journal"]))
Bm = None if a.storage else arm("B", ["thrownGoodsBlastDamagePercent=100"])
if Bm:
    row("B_VANILLA_DESTROYS_FRAGILE", Bm["goods"].get("destroyed", 0) >= 1, str(Bm["goods"]))
    row("B_NOTHING_SPARED", Bm["journal"].get("spared", 0) == 0, str(Bm["journal"]))
C = None if a.storage else arm("C", ["enabled=False"])
if C:
    row("C_OFF_NO_GOODS_THROWN", C["goods"].get("moved", 0) + C["goods"].get("in_pit", 0) == 0, str(C["goods"]))
    row("C_OFF_NO_PAWN_IN_PIT", C["pawns"].get("in_pit", 0) == 0, str(C["pawns"]))
    row("C_OFF_JOURNAL_EMPTY", sum(C["journal"].values()) == 0, str(C["journal"]))
load()  # leave the scene as saved, defaults restored
c("jawa/static_call", type=KP, method="Settings", args="reset")
out = a.out or os.path.join(os.environ.get("RM_SCRATCH", r"D:\ClaudeWork\rimmandrake"), "ek_proof",
                            "storeroom_pit_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump({"rows": rows, **ev}, f, indent=1, default=str)
print("%-28s %-10s %s" % ("ROW", "STATUS", "DETAIL"))
for rid, st, det in rows:
    print("%-28s %-10s %s" % (rid, st, str(det)[:160]))
print("evidence:", out)
sys.exit(0 if rows and all(r[1] == "PASS" for r in rows) else 1)
