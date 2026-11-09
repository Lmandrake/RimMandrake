#!/usr/bin/env python3
"""gravship_scene.py -- does a span strung on a gravship stay up through the flight, and do its cords come with it? (sc_gravship,
keepWiresOnGravship; a live launch on a scratch quicktest, the origin map is destroyed.)

    python.exe src/RimMandrake/GimmeSomeSlack/northstar/gravship_scene.py on|off [--shot NAME]

Flies bridgetools/prove_gravship.py's own ship (its recipe knows every engine gate), with two masts, a floor run and a lamp staged on
the pad, and one mast left on the ground strung to the ship. Reads, after landing: the aboard span up (on) or taken down (off), the
ground span gone either way, the cords laid on the new map within the new map's nets. Exit 0/1/2: PASS/FAIL/UNMEASURED.
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PROVE = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "prove_gravship.py")
sys.path.insert(0, os.path.join(HERE, "..", "northstar_matrix"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.dirname(PROVE))
SHOTS = r"D:\ClaudeWork\rimmandrake\ralph_gss\shots"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("on", "off"))
    ap.add_argument("--shot", default=None)
    a = ap.parse_args()
    src = open(PROVE, encoding="utf-8").read()
    head, rest = src.split("# -- 5. launch", 1)
    g = {"__file__": PROVE, "__name__": "prove_gravship_scene"}
    exec(compile(head, PROVE, "exec"), g)                    # authors the ship, refuels, walks the colonists aboard
    import run_live as RL
    B = RL.LiveBridge()
    X, Z = g["X"], g["Z"]
    st = {"B": B}   # the bridge in use: the land step makes a new one
    try:
        B.call("rimworld/set_god_mode", enabled=True)
        B.ap("set:keepWiresOnGravship=%s" % ("True" if a.mode == "on" else "False"))
        B.ap("set:autoLink=False")
        aboard = [(X + 3, Z + 17), (X + 16, Z + 17)]
        ground = (X + 3, Z + 24)
        for c in aboard + [ground]:
            B.ap("place:RM_AerialMast:Industrial:%d,%d:god" % c)
        for x in range(X + 4, X + 11):
            B.ap("cplace:PowerConduit:Industrial:%d,%d:god" % (x, Z + 16))
        B.ap("cprocess")
        B.call("jawa/build_batch", ops="StandingLamp:%d,%d" % (X + 12, Z + 15), faction="player", wipeExisting=False)
        B.ticks(3)
        apos = {(q["x"], q["z"]): q["id"] for q in B.ap("census").get("anchors") or []}
        ids = [apos.get(c) for c in aboard + [ground]]
        if None in ids:
            print("UNMEASURED: masts did not build: %s %s" % (ids, sorted(apos)))
            return 2
        print("links", B.ap("link:%d,%d" % (ids[0], ids[1])).get("verdict"), B.ap("link:%d,%d" % (ids[0], ids[2])).get("verdict"))
        B.call("rimworld/set_god_mode", enabled=False)
        B.ticks(2)
        before = B.ap("census")
        g["call"]("rimworld/step_game_ticks", ticks=60)
        tail = "# -- 5. launch" + rest.split("# -- 6. land", 1)[0] + "# -- 6. land" + rest.split("# -- 6. land", 1)[1].split("for part in", 1)[0]
        exec(compile(tail, PROVE, "exec"), g)                    # launch, travel, land
        B = st["B"] = RL.LiveBridge()
        B.ticks(30)
        B.probe("rebuild")
        after = B.ap("census")
        anchors = after.get("anchors") or []
        links = [(q["id"], l.get("other"), l.get("state")) for q in anchors for l in q.get("links") or []]
        up_aboard = any(i in ids[:2] and o in ids[:2] and st == "Up" for i, o, st in links)
        to_ground = any(ids[2] in (i, o) for i, o, st in links)
        gr = B.probe("census")
        lay = {k: gr.get(k) for k in ("cordEdges", "cordsAcrossNets", "verticesInUnwalkable", "conduitCells")}
        # a failed census reads as no anchors and zero counters: measured only when both censuses answered and both spans
        # were up before the launch (Codex review 2026-11-09)
        measured = bool(after.get("success")) and bool(gr.get("success")) and before.get("spansUp") == 2 and len(anchors) >= 2
        if not measured:
            print("UNMEASURED: census failed or the spans were not up before launch: %s" % json.dumps(
                {"before": before.get("spansUp"), "after": after.get("success"), "graph": gr.get("success"), "anchors": len(anchors)}))
            return 2
        ok = (up_aboard == (a.mode == "on")) and not to_ground and (gr.get("cordsAcrossNets") or 0) == 0 and (gr.get("verticesInUnwalkable") or 0) == 0
        if a.mode == "on":
            ok = ok and (gr.get("conduitCells") or 0) >= 7 and (gr.get("cordEdges") or 0) >= 1
        print(json.dumps({"mode": a.mode, "before": {"spansUp": before.get("spansUp")}, "after": {"spansUp": after.get("spansUp"), "spansCut": after.get("spansCut")},
                          "aboardSpanUp": up_aboard, "groundLinkKept": to_ground, "cords": lay, "verdict": "PASS" if ok else "FAIL"}))
        if a.shot:
            q = next((p for p in anchors if p["id"] == ids[0]), None)
            if q:
                res = B.call("rimworld/screenshot_cell_rect", x=q["x"] - 4, z=q["z"] - 6, width=24, height=14, paddingCells=1, fileName=a.shot)
                src_ = res.get("filePath") or res.get("path") or res.get("savedPath")
                for _ in range(30):
                    if src_ and os.path.exists(src_) and os.path.getsize(src_) > 0:
                        break
                    time.sleep(0.5)
                time.sleep(1)
                if src_ and os.path.exists(src_):
                    shutil.copyfile(src_, os.path.join(SHOTS, a.shot + ".png"))
                    print(os.path.join(SHOTS, a.shot + ".png"))
        return 0 if ok else 1
    finally:   # every exit, the early UNMEASURED return and exceptions too, puts the settings back (Codex review 2026-11-09)
        for f in (lambda: st["B"].call("rimworld/set_god_mode", enabled=False),
                  lambda: st["B"].ap("set:keepWiresOnGravship=True"), lambda: st["B"].ap("set:autoLink=True")):
            try:
                f()
            except Exception as e:   # noqa: BLE001  (restore what can be restored)
                print("restore failed: %s" % e)


if __name__ == "__main__":
    sys.exit(main())
