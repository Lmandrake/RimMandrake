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

Usage (python.exe from WSL, bridge held):
  storeroom_pit_proof.py [--save NAME] [--site x,z,w,h] [--pit x,z,w,h] [--k 3] [--out evidence.json]
Prints one PASS/FAIL/UNMEASURED table. Exit 0 only if every row passes."""
import argparse, collections, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "FlowWorks", "northstar"))
import proof_hose as PH  # noqa: E402

KP = "RimMandrake.ExplosiveKnockback.RM_KnockbackProof"
ap = argparse.ArgumentParser()
ap.add_argument("--save", default="EK_SITTING_STATION1_STOREROOM_PIT_20261112")
ap.add_argument("--site", default="114,117,22,15", help="census rect x,z,w,h around the room and pit")
ap.add_argument("--pit", default="128,122,4,5", help="pit cells x,z,w,h")
ap.add_argument("--k", type=int, default=3, help="min goods stacks that must end in pit cells (arm A)")
ap.add_argument("--ticks", type=int, default=300)
ap.add_argument("--out", default=None)
a = ap.parse_args()
B = PH.PB()
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
    for _ in range(max(1, a.ticks // 25)):
        c("rimworld/step_game_ticks", ticks=25, pauseFirst=True, timeoutMs=60000)
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


A = arm("A", [])
if A:
    row("A_GOODS_IN_PIT", A["goods"].get("in_pit", 0) >= a.k, "%s (need >=%d in pit)" % (A["goods"], a.k))
    row("A_PAWN_IN_PIT", A["pawns"].get("in_pit", 0) >= 1, str(A["pawns"]))
    row("A_NO_GOODS_DESTROYED", A["goods"].get("destroyed", 0) == 0, str(A["goods"]))
    row("A_NO_COLONIST_DEAD", A["pawns"].get("dead", 0) == 0, str(A["pawns"]))
    row("A_SPARED_JOURNALLED", A["journal"].get("spared", 0) >= 1, str(A["journal"]))
    row("A_WALL_IMPACT_JOURNALLED", A["journal"].get("goods_impact", 0) >= 1, str(A["journal"]))
Bm = arm("B", ["thrownGoodsBlastDamagePercent=100"])
if Bm:
    row("B_VANILLA_DESTROYS_FRAGILE", Bm["goods"].get("destroyed", 0) >= 1, str(Bm["goods"]))
    row("B_NOTHING_SPARED", Bm["journal"].get("spared", 0) == 0, str(Bm["journal"]))
C = arm("C", ["enabled=False"])
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
