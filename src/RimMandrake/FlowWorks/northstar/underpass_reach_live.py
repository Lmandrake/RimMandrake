"""UNDERPASS_REACH_VERIFY_WALK_UNDER_FOR_REAL live rows: reachability (CanReach, RelativeVeto) and A* agree in game under and
beside a built suspension deck -- the live row owed by UNDERPASS_REACH_FIX_DECK_VIEW_SAYS_NO (a01c76fe25), whose offline half is
FlowWorks SelfTest UnderpassReachChecks.

  python.exe src/RimMandrake/FlowWorks/northstar/underpass_reach_live.py A1|A2 [--origin X,Z] [--out result.json]

Exit 0 = the clause holds, 1 = it does not (MOD), 2 = UNMEASURED (no game, site not prepared, a staging that did not take).
Every read is RM_SuspensionProofs.ProofReach "pawnId;x,z" -> "REACH veto= reach= reachPawnless= found= cells= onDeck= under=
view= agree=" (production RelativeVeto, Reachability.CanReach with the pawn's TraverseParms and pawnless, FindPathNow).

A1  plot = origin. A 4 m trench (1..8, 0) (8 notches), a 2-wide steel suspension bridge over it (4,-1)-(5,1), built at once (god).
    A colonist on the trench floor at (1,0), asked for (8,0): the only way is along the floor under the deck.
    EXPECT veto=False reach=True reachPawnless=True found=True under>=1 view=floor agree=True.
A2  plot = origin + (0, 12). A stepped pit z = 0..3: west ledge x=1 and east ledge x=4 at 4 m (8 notches), core x=2..3 at 7 m
    (14); a sunken steel bridge (1,1)-(4,1) at ledge height. A colonist on the west ledge (1,3), asked for the east ledge (4,3):
    the core is a 3 m drop a person cannot climb back, so the only way is ACROSS the sunken deck.
    EXPECT veto=False reach=True reachPawnless=True found=True onDeck>=2 view=deck agree=True.
CONTROL (each clause; the instrument can see a NO): the same pawn asked for undug surface beside its plot (A1 (0,3), A2 (0,3)),
    up a 4 m wall with no ladder. EXPECT veto=True reach=False found=False agree=True. A control that reads reach=True means the
    read cannot tell a veto from a pass: UNMEASURED, never PASS.
LIES  A pawn the spawn put somewhere else (not on the plot's floor/ledge) is SITE; a bridge that did not stand is SITE.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
ITEM = "UNDERPASS_REACH_VERIFY_WALK_UNDER_FOR_REAL"
SPROOF = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
DEEP, CORE = 8, 14            # notches: 4 m ledge / trench floor, 7 m core

# (dx, dz) relative to the clause's plot
SCENES = {
    "A1": {"plot": (0, 0),
           "digs": [((x, 0), DEEP) for x in range(1, 9)],
           "bridge": ((4, -1), (5, 1)),
           "pawn": (1, 0), "dest": (8, 0), "control": (0, 3),
           "want_view": "floor", "count": "under"},
    "A2": {"plot": (0, 12),
           "digs": [((x, z), DEEP if x in (1, 4) else CORE) for z in range(0, 4) for x in (1, 2, 3, 4)],
           "bridge": ((1, 1), (4, 1)),
           "pawn": (1, 3), "dest": (4, 3), "control": (0, 3),
           "want_view": "deck", "count": "onDeck"},
}
NEED = {"under": 1, "onDeck": 2}


def parse(txt):
    kv = {}
    for tok in str(txt).split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return kv


def num(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return -1


def verdict(clause, kv, ctl):
    """(status, why) for one clause from its ProofReach read `kv` and its control read `ctl`. Pure: the selftest sweeps it."""
    s = SCENES[clause]
    if not kv or not ctl:
        return "UNMEASURED", "a ProofReach read is missing"
    if not (ctl.get("veto") == "True" and ctl.get("reach") == "False" and ctl.get("found") == "False"):
        return "UNMEASURED", "control: the read did not see a veto up a 4 m wall (%s)" % ctl
    bad = []
    for k, want in (("veto", "False"), ("reach", "True"), ("reachPawnless", "True"), ("found", "True"), ("agree", "True"),
                    ("view", s["want_view"])):
        if kv.get(k) != want:
            bad.append("%s=%s (want %s)" % (k, kv.get(k), want))
    if num(kv.get(s["count"])) < NEED[s["count"]]:
        bad.append("%s=%s (want >= %d)" % (s["count"], kv.get(s["count"]), NEED[s["count"]]))
    if ctl.get("agree") != "True":
        bad.append("control agree=%s" % ctl.get("agree"))
    return ("FAIL", "; ".join(bad)) if bad else ("PASS", "reach and A* agree")


def pid_num(pid):
    return re.sub(r"^(?:Thing_)?[A-Za-z]+_?(\d+)$", r"\1", str(pid))


def run(clause, B, origin, live=True):
    """Stage `clause` and read it. Returns (status, detail)."""
    s = SCENES[clause]
    ox, oz = origin[0] + s["plot"][0], origin[1] + s["plot"][1]
    P = lambda c: (ox + c[0], oz + c[1])     # noqa: E731
    xz = lambda c: "%d,%d" % P(c)            # noqa: E731
    det = {"clause": clause, "plot": [ox, oz]}

    def static(method, arg):
        r = B.call("jawa/static_call", type=SPROOF, method=method, args=arg, _answer=True) or {}
        return str(r.get("result") or r.get("message") or r.get("error") or "")

    if live:
        import validation_core as V  # noqa: E402  (bridge-side only)
        ok, _ = V._wait_playing(B, leave_s=0)
        if not ok:
            return "UNMEASURED", dict(det, why="no game in Playing")
        B.call("jawa/kill_hostiles")
        rect = (ox - 1, oz - 2, 12, 8)
        B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
        site_rows = []
        V.prepare_site(B, rect, site_rows, "underpass_reach_%s" % clause)
        bad = [r for r in site_rows if r.get("status") not in (None, "PASS")]
        if bad:
            return "UNMEASURED", dict(det, why="site not prepared", site=bad[:2])
    for c, n in s["digs"]:
        x, z = P(c)
        B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=n, setFill=-1)
    a, b = s["bridge"]
    det["build"] = static("ProofBuild", "%s;%s;steel;god" % (xz(a), xz(b)))
    if "ok=True" not in det["build"]:
        return "UNMEASURED", dict(det, why="the bridge did not build")
    x, z = P(s["pawn"])
    r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=x, z=z, faction="player", count=1) or {}
    pawn = ((r.get("pawns") or [{}])[0]).get("id")
    if not pawn:
        return "UNMEASURED", dict(det, why="no colonist spawned", spawn=r)
    pn = pid_num(pawn)
    try:
        det["band"] = static("ProofBand", pn)
        at = [p for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or [] if str(p.get("id")) == str(pawn)]
        if not at or (at[0].get("x"), at[0].get("z")) != (x, z) or "onDeck=False" not in det["band"]:
            return "UNMEASURED", dict(det, why="the colonist is not on the plot's floor/ledge", at=at[:1])
        det["read"] = static("ProofReach", "%s;%s" % (pn, xz(s["dest"])))
        det["control"] = static("ProofReach", "%s;%s" % (pn, xz(s["control"])))
        st, why = verdict(clause, parse(det["read"]) if det["read"].startswith("REACH") else {},
                          parse(det["control"]) if det["control"].startswith("REACH") else {})
        return st, dict(det, why=why)
    finally:
        B.call("jawa/pawn_force_incapacitate", pawn=pawn, action="vanish", _answer=True)


def main(argv=None, bridge=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("clause", choices=sorted(SCENES))
    ap.add_argument("--origin", default="60,60")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    live = bridge is None
    if live:
        import proof_hose as PH  # noqa: E402
        bridge = PH.PB()
    origin = tuple(int(v) for v in a.origin.split(","))
    st, det = run(a.clause, bridge, origin, live=live)
    res = {"script": "underpass_reach_live.py", "item": ITEM, "clause": a.clause, "status": st, "detail": det,
           "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    print("%s %s %s" % (a.clause, st, json.dumps(det, default=str)[:900]), flush=True)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
    return {"PASS": 0, "FAIL": 1}.get(st, 2)


if __name__ == "__main__":
    sys.exit(main())
