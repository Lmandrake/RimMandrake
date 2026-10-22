"""QUARRY FIND live check (FLOWWORKS_QUARRY_DIGGING_1 A5: "The canal-dig find roll (RM_DigDiscoveryProof force) drops a local
find on the lip, with first-find letter"; BENCH belt 2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/quarry_find_live.py [out.json] [--origin X,Z] [--fresh-map]

PROVE a colonist (Mining raised to 10, undrafted, every other colonist vanished) digs one plain RM_DigCanal notch at
      (5, 5) of a cleared plot after RM_DigDiscoveryProof.ProofReport("force"); the report is read before and after; the
      things on the 3x3 around the cell and the letters are read before and after the cut.
EXPECT depth 0 -> 1 (a real cut, the dig job's own path), Finds +1, a new item on a standable non-dug square within
      1 of the cell, a new letter.
LIES  a cut never made (no colonist dig) measures nothing -> UNMEASURED; an item that was already there is excluded by
      the before/after id diff.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
DPROOF = "RimMandrake.FlowWorks.RM_DigDiscoveryProof"
ITEM = "FLOWWORKS_QUARRY_DIGGING_1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,40")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "quarry_find_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "quarry_find_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-24s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:600]), flush=True)
        save()

    def step(n):
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}

    ox, oz = (int(v) for v in a.origin.split(","))
    c = (ox + 5, oz + 5)
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("QUARRY_FIND_DROPS_ON_LIP", "UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    rect = (ox, oz, 11, 11)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site_rows = []
    V.prepare_site(B, rect, site_rows, "quarry_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        row("QUARRY_FIND_DROPS_ON_LIP", "UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
        return 2
    for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []:
        if not p.get("dead") and p.get("isPlayer"):
            B.call("jawa/pawn_force_incapacitate", pawn=p.get("id"), action="vanish")
    # three diggers (belt live: a single random colonist sometimes never dug in 4000 ticks -- Mining disabled by backstory)
    r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=ox + 2, z=oz + 2, faction="player", count=3) or {}
    cids = [p_.get("id") for p_ in r.get("pawns") or [] if p_.get("id")]
    cid = cids[0] if cids else None
    for c_ in cids:
        B.call("jawa/set_pawn_skill", pawn=c_, skill="Mining", level=10, _answer=True)
        # SITE (belt live 2026-10-22): bridge-spawned colonists can come with the work type at priority 0 (job probe:
        # "priority 0, workActive False") -- they never dig. Set it on, and read the probe back into the result.
        B.call("jawa/set_work_priority", pawnId=c_, workType="Mining", priority=1)

    def things():
        lt = B.call("jawa/list_things", rect="%d,%d,3,3" % (c[0] - 1, c[1] - 1), limit=50) or {}
        return {t.get("id"): (t.get("def"), t.get("x"), t.get("z"), t.get("stackCount")) for t in lt.get("things") or []
                if not str(t.get("def") or "").startswith(("Filth", "Plant", "Human"))}

    def letters():
        lt = B.call("rimworld/list_letters") or {}
        return [str(x.get("label") or x.get("title") or x)[:80] for x in lt.get("letters") or []]

    def depth():
        return (B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=0, setFill=-1) or {}).get("depth")
    r0 = (B.call("jawa/static_call", type=DPROOF, method="ProofReport", args="force", _answer=True) or {}).get("result")
    t0, l0, d0 = things(), letters(), depth()
    des = B.call("jawa/designate_batch", action="add", designation="RM_DigCanal", rect="%d,%d,1,1" % c) or {}
    t, cut_at = 0, None
    while t < 4000:
        step(250)
        t += 250
        if depth() not in (None, d0):
            cut_at = t
            break
    step(10)
    r1 = (B.call("jawa/static_call", type=DPROOF, method="ProofReport", args="report", _answer=True) or {}).get("result")
    t1, l1, d1 = things(), letters(), depth()
    new = {k: v for k, v in t1.items() if k not in t0}
    new_letters = [x for x in l1 if x not in l0]
    det = {"armed": r0, "after": r1, "depth": [d0, d1], "cutAt": cut_at, "newThings": new, "newLetters": new_letters,
           "designate": str(des)[:200]}
    if cut_at is None:
        row("QUARRY_FIND_DROPS_ON_LIP", "UNMEASURED", "SITE", dict(det, why="no colonist cut the square in 4000 ticks"))
        return 2

    def finds(rep):
        try:
            return int(str(rep).split("finds ")[1].split()[0])
        except (IndexError, ValueError):
            return None
    f0, f1 = finds(r0), finds(r1)
    on_lip = [v for v in new.values() if (v[1], v[2]) != c]
    good = f0 is not None and f1 == f0 + 1 and bool(on_lip) and bool(new_letters)
    row("QUARRY_FIND_DROPS_ON_LIP", "PASS" if good else "FAIL", "MOD", det)
    for c_ in cids:
        B.call("jawa/pawn_force_incapacitate", pawn=c_, action="vanish", _answer=True)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
