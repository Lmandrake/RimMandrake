#!/usr/bin/env python3
"""Gimme Some Slack 0.1.1: one live look that the style button's three reaches do what the menu says
(RIMMANDRAKE_WIDEN_SLACK_STYLE_BUTTON_REACH_ITEM_RUN_OR_WHOLE_MAP; design/RimMandrake/messyconduit_style_per_build_design.md
section 2.5). Every repaint goes through the call the menu option makes (RestyleOne / RestyleRun / RestyleAll /
RestyleLampRun, via ConduitStyleProbe); only the click is skipped. Reads are stored styles and cord-piece looks (cstyles),
plus captures for a look by eye.

Scene (on a quicktest map, the validation_style SITE2 rect): run A, 8 Industrial conduit cells with a floor lamp hooked;
run B, 8 Modern orange cells with a lamp; run H, 5 conduit cells of a hostile faction (no style).

  R1 the reach menu names three reaches with their counts (A: 8 pieces, 1 lamp; map: the player's 16 pieces, 2 lamps)
  R2 This item: one A cell -> Futuristic; only that cell changes; its cord piece prints Futuristic; the lamp keeps Industrial
  R3 built onto the mixed run: a cell beside the Futuristic cell takes Futuristic, a cell at A's far end takes Industrial
  R4 All connected (A -> Modern blue): every A cell Modern blue, A's lamp follows (it wore a look the run drew), B untouched
  R5 All on map (player, Futuristic): A, B and both lamps Futuristic; the hostile run H stays unstyled
  R6 All on map in god mode (Industrial): H too
  R7 a lamp's All connected (B's lamp, Scrapper): B and that lamp Scrapper, A untouched

    eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"
    python3 src/RimMandrake/GimmeSomeSlack/live_probes/style_reach_live.py --out <json> --shots <dir>
Exit 0 all PASS, 1 any FAIL, 2 could not run (probe channel dead / site not ready).
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import validation as V  # noqa: E402
import validation_style as VS  # noqa: E402

X0, Z0 = VS.SITE2[0], VS.SITE2[1]
SITE = VS.SITE2
A = [(X0 + 2 + i, Z0 + 2) for i in range(8)]
B_ = [(X0 + 2 + i, Z0 + 7) for i in range(8)]
H = [(X0 + 16 + i, Z0 + 2) for i in range(5)]
LAMP_A = (X0 + 5, Z0 + 3)
LAMP_B = (X0 + 5, Z0 + 8)
NEAR_F = (A[3][0], Z0 + 1)        # touches only A[3] (the cell made Futuristic)
FAR_END = (A[-1][0] + 1, Z0 + 2)  # touches only A[-1] (Industrial)


def cst(B):
    B.ap("cprocess")
    B.ticks(2)
    return B.ap("cstyles:%d,%d,%d,%d" % SITE)


def mem(st):
    return {(m["x"], m["z"]): m for m in st.get("members") or []}


def lamps(st):
    return {(l["x"], l["z"]): l for l in st.get("lamps") or []}


def raw(st, c):
    return (mem(st).get(c) or {}).get("rawStyle")


def piece_look(st, c):
    for p in st.get("pieces") or []:
        if tuple(p["owner"]) == c and p.get("strands"):
            return p.get("look")
    return None


def shot(B, name, out, log):
    r = B.call("rimworld/screenshot_cell_rect", x=SITE[0], z=SITE[1], width=24, height=11, paddingCells=1,
               fileName=name, suppressMessage=True)
    src = r.get("path") or r.get("filePath")
    dst = None
    if src and os.path.exists(src):
        os.makedirs(out, exist_ok=True)
        dst = os.path.join(out, name + os.path.splitext(src)[1])
        shutil.copyfile(src, dst)
    log.append({"shot": name, "src": src, "dst": dst, "ok": r.get("success")})
    return dst


def row(rows, rid, ok, detail):
    rows.append({"id": rid, "status": "PASS" if ok else "FAIL", "detail": detail})
    print("%s %s" % (rows[-1]["status"], rid), flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--shots", required=True)
    a = ap.parse_args(argv)
    B = VS._A()
    rows, log = [], []
    res = {"script": "style_reach_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "log": log}
    if not B.ap("defaults").get("success"):
        print("COULD NOT RUN: aerial probe channel dead")
        return 2
    B.ap("cclearpicks")
    if not VS.prepare_site(B, SITE, [], "site"):
        print("COULD NOT RUN: site not ready")
        return 2
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % SITE, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % SITE)
    B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % SITE)
    V.reveal(B, SITE)
    V.frame_fit(B, (SITE[0], SITE[1], 24, 11))
    B.ticks(2)
    built = [B.ap("cline:PowerConduit:Industrial:%d,%d:%d,%d:god" % (A[0] + A[-1])),
             B.ap("cline:PowerConduit:Modern_Orange:%d,%d:%d,%d:god" % (B_[0] + B_[-1])),
             B.ap("cplace:StandingLamp:Industrial:%d,%d:god" % LAMP_A),
             B.ap("cplace:StandingLamp:Modern:%d,%d:god" % LAMP_B),
             B.call("jawa/build_batch", ops=";".join("PowerConduit:%d,%d,0" % c for c in H), faction="hostile", wipeExisting=False)]
    st = cst(B)
    ok0 = all(x.get("success") for x in built) and all(raw(st, c) == "PowerConduit_Industrial" for c in A) and \
        all(raw(st, c) == "PowerConduit_Modern_Orange" for c in B_) and all(c in mem(st) and raw(st, c) is None for c in H) and \
        (lamps(st).get(LAMP_A) or {}).get("look") == "Industrial"
    row(rows, "R0_scene", ok0, {"errors": [x.get("error") for x in built if not x.get("success")], "H": [raw(st, c) for c in H],
                                "lampA": lamps(st).get(LAMP_A), "lampB": lamps(st).get(LAMP_B)})
    if not ok0:
        res["aborted"] = "scene not built"
        json.dump(res, open(a.out, "w"), indent=1, default=str)
        return 1
    shot(B, "reach0_scene", a.shots, log)

    r = B.ap("creach:%d,%d:open" % A[0])
    labels = r.get("reaches") or []
    time.sleep(0.5)
    shot(B, "reach1_menu_open", a.shots, log)
    B.ap("cclosemenus")
    ok1 = len(labels) == 3 and labels[0].startswith("This item") and labels[1] == "All connected: 8 pieces, 1 lamps" and \
        labels[2].startswith("All on map: 16 pieces, 2 lamps")
    row(rows, "R1_reach_menu_counts", ok1, {"labels": labels})

    r2 = B.ap("crestyleone:%d,%d:Futuristic" % A[3])
    st = cst(B)
    others = [raw(st, c) for c in A if c != A[3]]
    ok2 = raw(st, A[3]) == "PowerConduit_Futuristic" and all(o == "PowerConduit_Industrial" for o in others) and \
        piece_look(st, A[3]) == "Futuristic" and (lamps(st).get(LAMP_A) or {}).get("look") == "Industrial"
    row(rows, "R2_this_item_only", ok2, {"call": r2, "cell": raw(st, A[3]), "piece": piece_look(st, A[3]), "others": others,
                                         "lampA": (lamps(st).get(LAMP_A) or {}).get("look")})
    shot(B, "reach2_this_item", a.shots, log)

    p1 = B.ap("cplace:PowerConduit:Scrapper:%d,%d:god" % NEAR_F)
    p2 = B.ap("cplace:PowerConduit:Scrapper:%d,%d:god" % FAR_END)
    st = cst(B)
    ok3 = raw(st, NEAR_F) == "PowerConduit_Futuristic" and raw(st, FAR_END) == "PowerConduit_Industrial" and raw(st, A[3]) == "PowerConduit_Futuristic"
    row(rows, "R3_new_piece_takes_touched_look", ok3, {"nearF": raw(st, NEAR_F), "farEnd": raw(st, FAR_END), "place": [p1.get("success"), p2.get("success")],
                                                       "message": st.get("lastMessage")})

    r4 = B.ap("crestyle:%d,%d:Modern_Blue" % A[0])
    st = cst(B)
    runA = A + [NEAR_F, FAR_END]
    ok4 = all(raw(st, c) == "PowerConduit_Modern_Blue" for c in runA) and all(raw(st, c) == "PowerConduit_Modern_Orange" for c in B_) and \
        (lamps(st).get(LAMP_A) or {}).get("look") == "Modern"
    row(rows, "R4_all_connected", ok4, {"call": r4, "A": [raw(st, c) for c in runA], "lampA": (lamps(st).get(LAMP_A) or {}).get("look")})
    shot(B, "reach3_all_connected", a.shots, log)

    r5 = B.ap("crestyleall:Futuristic:player")
    st = cst(B)
    ok5 = all(raw(st, c) == "PowerConduit_Futuristic" for c in runA + B_) and all(raw(st, c) is None for c in H) and \
        all((lamps(st).get(l) or {}).get("look") == "Futuristic" for l in (LAMP_A, LAMP_B))
    row(rows, "R5_all_on_map_player_only", ok5, {"call": r5, "H": [raw(st, c) for c in H], "lamps": [lamps(st).get(l) for l in (LAMP_A, LAMP_B)]})
    shot(B, "reach4_all_on_map", a.shots, log)

    r6 = B.ap("crestyleall:Industrial:god")
    st = cst(B)
    ok6 = all(raw(st, c) == "PowerConduit_Industrial" for c in runA + B_ + H)
    row(rows, "R6_all_on_map_god_every_faction", ok6, {"call": r6, "H": [raw(st, c) for c in H]})

    r7 = B.ap("clamprun:%d,%d:Scrapper" % LAMP_B)
    st = cst(B)
    ok7 = all(raw(st, c) == "PowerConduit_Scrapper" for c in B_) and all(raw(st, c) == "PowerConduit_Industrial" for c in runA) and \
        (lamps(st).get(LAMP_B) or {}).get("look") == "Scrapper"
    row(rows, "R7_lamp_all_connected", ok7, {"call": r7, "B": [raw(st, c) for c in B_], "lampB": (lamps(st).get(LAMP_B) or {}).get("look")})
    shot(B, "reach5_lamp_run", a.shots, log)

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    fails = [r["id"] for r in rows if r["status"] != "PASS"]
    print("style reach live: %d rows, %d FAIL %s -> %s" % (len(rows), len(fails), fails, a.out))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
