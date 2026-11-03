#!/usr/bin/env python3
"""RAIL_WALK live proof: the guardrail's walked-step door has a live control (RAIL_WALK_PROVE_NOBODY_WALKS_OFF_ANYWAY,
FALL_GUARDRAILS_BUILD_REAL_OBJECT A3).

  python.exe src/RimMandrake/FlowWorks/northstar/rail_walk_live.py [out.json] [--origin X,Z] [--fresh-map]

Why a hook: the A3 run of 2026-10-18 ordered a Pirate at a 7 m pit's centre and it never stepped off the UNRAILED lip either
(with the cliff masks on, A* and the per-move floor refuse every walked step past a pawn's climb), so "the railed one did not
fall" proved nothing about the rail. RM_FallRails.ProofWalkedStep asks the REAL per-move floor (the Harmony prefix on
Pawn_PathFollower.TryEnterNextPathCell) which door refuses the step, then, with "force", makes the step the floor refused,
marked WALKED, so the descent detector judges a stale walked arrival on its next pass.

Scene (plot from --origin, default 120,200; 9 x 9 cleared + read back): a 7 m pit x = 2..6, z = 2..6 (14 notches);
RM_PitGuardrail (steel) on the west lip (1, 3); the west lip (1, 5) left bare. One hostile Pirate per lip, stepping east.
EXPECT  W1 railed lip: rail=True, door=rail, prefixPass=False (the rail door refuses first)
        W2 unrailed lip: rail=False, door=floor, prefixPass=False (nobody walks off anyway: the floor holds it)
        W3 railed, forced walked step: expect=putback; 3 ticks later the Pirate is on the lip, no new descent
        W4 unrailed, forced walked step (the control): expect=fell; 3 ticks later a new descent and the Pirate in the pit
LIES    a W3 pass with a W4 that does not fall would be the old A3 again (no control): W4 must FALL for W3 to mean anything.
Exit 0 = every row PASS; 1 = a row FAIL; 2 = UNMEASURED (no game, site, harness).
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
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
RAILS = "RimMandrake.FlowWorks.RM_FallRails"
ITEM = "RAIL_WALK_PROVE_NOBODY_WALKS_OFF_ANYWAY"


def parse_kv(s):
    """'WALK rail=True door=rail ...' -> {'rail': 'True', 'door': 'rail', ...}."""
    return dict(re.findall(r"(\w+)=(\S+)", s or ""))


def judge_floor(kv, railed):
    """W1/W2: which door refuses the walked step, railed vs unrailed."""
    if not kv:
        return False
    want_door = "rail" if railed else "floor"
    return kv.get("rail") == str(railed) and kv.get("door") == want_door and kv.get("prefixPass") == "False"


def judge_forced(kv, before, after, lip, railed):
    """W3/W4: the detector's verdict on a forced walked arrival. before/after: ProofTrap key/values."""
    if not kv or not before or not after:
        return False
    try:
        d0, d1 = int(before.get("descents")), int(after.get("descents"))
    except (TypeError, ValueError):
        return False
    on_lip = after.get("pos") == "%d,%d" % lip
    if railed:
        return kv.get("expect") == "putback" and on_lip and d1 == d0
    return kv.get("expect") == "fell" and not on_lip and d1 == d0 + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="120,200")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "rail_walk_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "rail_walk_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-22s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:700]), flush=True)
        save()

    def call(ty, m, arg):
        r = B.call("jawa/static_call", type=ty, method=m, args=arg, _answer=True) or {}
        return str(r.get("result") or r.get("message") or "")

    def ticks(n):
        return (B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=60000) or {}).get("success") is not False

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)  # noqa: E731
    xz = lambda c: "%d,%d" % c  # noqa: E731
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("W0_site", "UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    rect = (ox, oz, 9, 9)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site_rows = []
    V.prepare_site(B, rect, site_rows, "rail_walk_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        row("W0_site", "UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
        return 2
    for x in range(2, 7):
        for z in range(2, 7):
            c = P(x, z)
            B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=14, setFill=-1)
    railed_lip, bare_lip = P(1, 3), P(1, 5)
    railed_drop, bare_drop = P(2, 3), P(2, 5)
    B.call("jawa/build_batch", ops="RM_PitGuardrail:%s" % xz(railed_lip), stuff="Steel", faction="player", wipeExisting=False)
    ticks(5)
    pre = {}
    lt = B.call("jawa/list_things", defName="RM_PitGuardrail", rect="%d,%d,1,1" % railed_lip, limit=2, _answer=True) or {}
    pre["guardrail"] = str(lt)[:200]

    def spawn(c):
        r = B.call("jawa/spawn_pawn", kindDef="Pirate", x=c[0], z=c[1], faction="hostile", count=1) or {}
        return ((r.get("pawns") or [{}])[0]).get("id")

    pr, pb = spawn(railed_lip), spawn(bare_lip)
    if not pr or not pb:
        row("W0_site", "UNMEASURED", "HARNESS", dict(pre, why="a Pirate did not spawn", railed=pr, bare=pb))
        return 2
    ticks(2)
    # W1 / W2: the real per-move floor's verdict, no step taken
    w1 = call(RAILS, "ProofWalkedStep", "%s;%s;%s" % (pr, xz(railed_lip), xz(railed_drop)))
    w2 = call(RAILS, "ProofWalkedStep", "%s;%s;%s" % (pb, xz(bare_lip), xz(bare_drop)))
    for rid, s, railed in (("W1_railed_door", w1, True), ("W2_unrailed_floor", w2, False)):
        kv = parse_kv(s)
        if not s.startswith("WALK"):
            row(rid, "UNMEASURED", "HARNESS", dict(pre, answer=s))
        else:
            row(rid, "PASS" if judge_floor(kv, railed) else "FAIL", "MOD", dict(pre, answer=s))
    # W3 then W4: a forced walked step each, judged by the detector on its next pass
    for rid, pid, lip, drop, railed in (("W3_railed_putback", pr, railed_lip, railed_drop, True),
                                        ("W4_unrailed_falls", pb, bare_lip, bare_drop, False)):
        before = parse_kv(call(NSP, "ProofTrap", str(pid)))
        s = call(RAILS, "ProofWalkedStep", "%s;%s;%s;force" % (pid, xz(lip), xz(drop)))
        ticks(3)
        after = parse_kv(call(NSP, "ProofTrap", str(pid)))
        det = {"answer": s, "before": before, "after": after}
        if not s.startswith("WALK") or not before or not after:
            row(rid, "UNMEASURED", "HARNESS", det)
        else:
            row(rid, "PASS" if judge_forced(parse_kv(s), before, after, lip, railed) else "FAIL", "MOD", det)
    for pid in (pr, pb):
        B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    st = [r["status"] for r in rows]
    if "FAIL" in st:
        return 1
    return 0 if st and all(s == "PASS" for s in st) and len(st) == 4 else 2


if __name__ == "__main__":
    sys.exit(main())
