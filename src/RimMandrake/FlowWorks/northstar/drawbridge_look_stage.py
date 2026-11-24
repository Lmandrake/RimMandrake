"""drawbridge_look_stage.py -- the owner's drawbridge look (RIMMANDRAKE_PRUNE_FLOWWORKS_DRAWBRIDGE_TO_HIS_NOV_THIRD_RULINGS): one
review map, one grid over material, direction, width and length, each LOWERED cell beside its RAISED twin, plus a row over the
four looks. Every bridge is laid by the mod's own one-drag button (ProofOneDrag, god mode); a raised cell is set raised and held
(ProofDevSet). Walls stand beside the gates. Hostiles killed, clear weather, paused.

  python.exe northstar/drawbridge_look_stage.py --dry-run               the plan and the grid key; no bridge
  python.exe northstar/drawbridge_look_stage.py --faults                three live checks of the merged faults, on their own plots
  python.exe northstar/drawbridge_look_stage.py --out DIR [--save NAME] stage, shoot every cell, save
A bridge must be held and a map must be Playing (--fresh-map starts a quicktest map).
Minimum Force: the leaf is set to its hold, not worked there by a colonist; the scene shows the picture and nothing about the job.
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "Utils")))
DP = "RimMandrake.FlowWorks.Pits.RM_DrawbridgeProofs"
SP = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
F = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
CASES = {"timber": [(1, 4), (2, 4), (3, 4), (4, 4), (1, 1), (2, 2)], "steel": [(1, 4), (2, 4), (3, 4), (4, 4), (1, 1), (2, 8)]}
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
DEEP = 8


def grid():
    """[{row, col, name, mat, dir, w, L, up, look, box (x,z,w,h), start, end, trench, walls}] relative to the site's corner (pure)."""
    out = []
    z = 2
    rows = [("%s %s" % (m, d), m, d, [(w, L, None) for (w, L) in CASES[m]]) for m in ("timber", "steel") for d in "SNEW"]
    rows += [("looks %s" % m, m, d, [(2, 3, k) for k in LOOKS]) for m, d in (("timber", "E"), ("steel", "S"))]
    for name, m, d, cases in rows:
        x = 2
        tall = 0
        for k, (w, L, look) in enumerate(cases):
            for up in (False, True):
                horiz = d in "EW"
                # along: gate square, hinge anchor, leaf L, far anchor; margins 2 behind the gate, 2 past the far anchor
                alen, across = L + 3 + 4, w + 5
                bw, bh = (alen, across + 2) if horiz else (across, alen)
                fx, fz = F[d]
                sx, sz = fz, -fx                          # record side for a drag running d: lanes step clockwise
                # hinge anchor lane-0 cell
                if d == "N":
                    h = (x + 2, z + 3)
                elif d == "S":
                    h = (x + 2 + w, z + bh - 4)
                    h = (x + 2 + (w - 1) + 1, z + bh - 4)
                elif d == "E":
                    h = (x + 3, z + 2 + (w - 1) + 1)
                else:
                    h = (x + bw - 4, z + 2)
                lane = lambda i, j: (h[0] + sx * j + fx * i, h[1] + sz * j + fz * i)   # noqa: E731
                start, end = lane(0, 0), lane(L + 1, w - 1)
                trench = [lane(i, j) for i in range(1, L + 1) for j in range(-2, w + 2)]
                walls = [lane(-1, j) for j in (-2, -1, w, w + 1)]
                out.append({"row": name, "col": k, "mat": m, "dir": d, "w": w, "L": L, "up": up, "look": look, "box": (x, z, bw, bh),
                            "start": start, "end": end, "deck": lane(1, 0), "trench": trench, "walls": walls,
                            "name": "%s %s w%d L%d%s %s" % (m, d, w, L, " " + look if look else "", "RAISED" if up else "lowered")})
                x += bw + (0 if not up else 1)
                tall = max(tall, bh)
        z += tall + 1
    return out


def extent(cells):
    return max(c["box"][0] + c["box"][2] for c in cells) + 2, max(c["box"][1] + c["box"][3] for c in cells) + 2


def problems(cells):
    """Cells whose squares leave their box or meet another cell's squares (pure)."""
    bad, used = [], {}
    for c in cells:
        x, z, w, h = c["box"]
        for q in c["trench"] + c["walls"] + [c["start"], c["end"]]:
            if not (x <= q[0] < x + w and z <= q[1] < z + h):
                bad.append("%s: %s leaves its box %s" % (c["name"], q, c["box"]))
            if used.setdefault(q, c["name"]) != c["name"] and q in c["trench"]:
                bad.append("%s meets %s at %s" % (c["name"], used[q], q))
    return bad


def stations(cells):
    """[(row, col)] in grid order: station n is the n-th pair, its lowered cell on the left and its raised twin on the right (pure)."""
    out = []
    for c in cells:
        if (c["row"], c["col"]) not in out:
            out.append((c["row"], c["col"]))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--faults", action="store_true")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--origin", default="6,6")
    ap.add_argument("--out", default=None)
    ap.add_argument("--save", default=None)
    ap.add_argument("--shots-only", action="store_true", help="the scene already stands: only shoot (and save)")
    a = ap.parse_args()
    a.no_shots = False
    cells = grid()
    W, H = extent(cells)
    print("grid %d cells, %dx%d" % (len(cells), W, H))
    bad = problems(cells)
    for b in bad[:8]:
        print("LAYOUT:", b)
    if a.dry_run or bad:
        for n, (r, k) in enumerate(stations(cells), 1):
            print("%2d  %s" % (n, [c["name"] for c in cells if c["row"] == r and c["col"] == k][0].replace(" lowered", "")))
        return 1 if bad else 0
    import water_scenes_walk as m
    w = m.Walk(a)
    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda c: "%d,%d" % (ox + c[0], oz + c[1])      # noqa: E731
    fails = []

    def need(ok, what, got):
        if not ok:
            fails.append("%s: %s" % (what, str(got)[:200]))
            print("FAULT", fails[-1], flush=True)
        return ok

    if a.fresh_map:
        w.call("rimworld/go_to_main_menu")
        r = w.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
        print("map:", str(r)[:150])
    need(w.V._wait_playing(w.B, leave_s=0)[0], "a map is Playing", "the wait timed out")
    w.call("rimworld/pause_game")
    w.call("rimworld/set_god_mode", enabled=True)
    proof = lambda meth, arg, ty=DP: w.proof(ty, meth, arg)[1]      # noqa: E731
    if a.faults:
        return faults(w, proof, ox, oz, need, fails)
    if not a.shots_only:
        calm = w.V.site_calm(w.B)        # no storyteller, no wild spawns, no stranger: a fight or a meteor broke bridges on the first pass
        need(calm.get("ok"), "the world is calm", calm)
        w.call("jawa/kill_hostiles")
        w.call("jawa/weather_set", weather="Clear", lockWeather=True)
        for _ in range(12):              # to midday BEFORE anything is built
            tk = w.call("jawa/time_clock") or {}
            if tk.get("ticksAbs") is None or 10 <= (tk["ticksAbs"] % 60000) / 2500.0 <= 13:
                break
            w.call("rimworld/step_game_ticks", ticks=2000, pauseFirst=True, timeoutMs=120000)
        print("site:", w.clear_site((ox, oz, W, H)), flush=True)
        for c in cells:
            for q in c["trench"]:
                w.call("jawa/flowworks_excavation_drive", x=ox + q[0], z=oz + q[1], deepenLevels=DEEP, setBodyWaterM=-1)
            w.call("jawa/spawn_batch", ops=";".join("Wall:" + P(q) for q in c["walls"]), stuff="BlocksGranite")
            arg = "%s;%s;%s" % (P(c["start"]), P(c["end"]), c["mat"]) + (";" + c["look"] if c["look"] else "")
            t = proof("ProofOneDrag", arg)
            need("ok=True" in t and "linked=1" in t and "gates=%d" % c["w"] in t, c["name"] + " laid by one drag", t)
            if c["mat"] == "steel":
                need("powered=True" in proof("ProofWinchPower", P(c["deck"]) + ";on"), c["name"] + " powered", "")
            if c["up"]:
                t = proof("ProofDevSet", P(c["deck"]) + ";raise;instant")
                need("DEVSET" in t, c["name"] + " raised", t)
            print("laid", c["name"], flush=True)
        for c in cells:
            t = proof("ProofLeaf", P(c["deck"]))
            kv = dict(x.split("=", 1) for x in t.split() if "=" in x)
            need((kv.get("progress") == kv.get("full")) == c["up"] and (kv.get("progress") == "0") != c["up"], c["name"] + " reads its state", t)
        w.call("jawa/kill_hostiles")
        w.call("rimworld/step_game_ticks", ticks=120, pauseFirst=True, timeoutMs=120000)
        import owner_review_stage as R
        ops = []
        for n, (r, k) in enumerate(stations(cells), 1):
            two = [c for c in cells if c["row"] == r and c["col"] == k]
            x0, x1 = two[0]["box"][0], two[1]["box"][0] + two[1]["box"][2]
            ops.append(R.label_op(ox + (x0 + x1) // 2, oz + two[0]["box"][1] + two[0]["box"][3], "%d" % n, two[0]["name"].replace(" lowered", "")))
        w.call("jawa/review_label", action="clear", tag="drawbridge_look")
        need((w.call("jawa/review_label", action="add", ops="\n".join(ops), tag="drawbridge_look") or {}).get("success") is not False, "labels", "")
        for c in cells:      # the state after the clock moved: nothing lowered itself
            t = proof("ProofLeaf", P(c["deck"]))
            kv = dict(x.split("=", 1) for x in t.split() if "=" in x)
            need((kv.get("progress") == "0") != c["up"], c["name"] + " kept its state while the clock moved", t)
    # a giant plant rooted outside the site leans over its edge rows: the margin is cleared too
    need((w.call("jawa/destroy_batch", rects=";".join("%d,%d,%d,%d" % r for r in ((max(ox - 24, 1), max(oz - 24, 1), W + 48, 24),
         (max(ox - 24, 1), oz + H, W + 48, 12), (max(ox - 24, 1), oz, min(24, ox - 1), H), (ox + W, oz, 24, H))), categories="Plant") or {}).get("success") is not False,
         "the margin's plants cleared", "")
    import fw_walk_common as C
    out = a.out
    os.makedirs(out, exist_ok=True)
    shots = []

    def snap(name, rect):
        png = C.snap(w, name, rect)
        if need(png, "picture " + name, png):
            dst = os.path.join(out, name + ".png")
            shutil.copyfile(png, dst)
            shots.append(dst)

    rows = []
    for c in cells:
        if c["row"] not in rows:
            rows.append(c["row"])
    for r in rows:
        for k in sorted({c["col"] for c in cells if c["row"] == r}):
            two = [c for c in cells if c["row"] == r and c["col"] == k]
            x0, z0 = min(c["box"][0] for c in two), min(c["box"][1] for c in two)
            x1, z1 = max(c["box"][0] + c["box"][2] for c in two), max(c["box"][1] + c["box"][3] for c in two)
            snap("cell_%s_%d_w%d_L%d" % (r.replace(" ", "_"), k, two[0]["w"], two[0]["L"]), (ox + x0, oz + z0, x1 - x0, z1 - z0))
    snap("overview", (ox, oz, W, H))
    if a.save:
        w.frame((ox, oz, W, H))
        w.call("rimworld/pause_game")
        r = w.call("rimworld/save_game", saveName=a.save) or {}
        print("SAVE", json.dumps(r)[:300])
    print("SHOTS %d in %s; faults %d" % (len(shots), out, len(fails)))
    return 1 if fails else 0


def faults(w, proof, ox, oz, need, fails):
    """DRAWBRIDGE_LOWER_FIX_LIFTS_OCCUPANTS_BENEATH, TIMBER_WINCH_FIX_POWERS_STEEL_BRIDGE, DRAWBRIDGE_BUTTON_FIX_CLICK_SEEMS_DEAD, live."""
    X, Z = ox + 20, oz + 20
    w.call("jawa/kill_hostiles")
    print("site:", w.clear_site((X - 2, Z - 2, 40, 30)), flush=True)

    def dig(z, n):
        for i in range(1, n + 1):
            w.call("jawa/flowworks_excavation_drive", x=X + i, z=z, deepenLevels=DEEP, setBodyWaterM=-1)

    def leaf(z):
        t = proof("ProofLeaf", "%d,%d" % (X + 1, z))
        return dict(k.split("=", 1) for k in t.split() if "=" in k), t

    res = {}
    # 1 beneath: raised leaf, a colonist in the hole under it, lowered: still under
    dig(Z, 4)
    print(proof("ProofOneDrag", "%d,%d;%d,%d;timber" % (X, Z, X + 5, Z)))
    proof("ProofDevSet", "%d,%d;raise;instant" % (X + 1, Z))
    r = w.call("jawa/spawn_pawn", kindDef="Colonist", x=X + 2, z=Z, faction="player", count=1) or {}
    pid = ((r.get("pawns") or [{}])[0]).get("id")
    num = "".join(ch for ch in str(pid) if ch.isdigit())
    before = proof("ProofBand", num, SP)
    proof("ProofDevSet", "%d,%d;lower;instant" % (X + 1, Z))
    after = proof("ProofBand", num, SP)
    res["LOWER_KEEPS_BENEATH"] = (need("under=True" in after and "onDeck=False" in after, "lowered over a colonist in the hole", before + " -> " + after), before, after)
    # 2 a timber winch beside a steel hinge takes no leaf
    z2 = Z + 8
    dig(z2, 4)
    print(proof("ProofMakeDrawbridge", "%d,%d;%d,%d;steel;A" % (X, z2, X + 5, z2)))
    w.call("jawa/build_batch", ops="RM_DrawbridgeWinch_Timber:%d,%d" % (X, z2 - 1), faction="player")
    there = [q.get("def") for q in (w.call("jawa/list_things", rect="%d,%d,1,1" % (X, z2 - 1), limit=9) or {}).get("things") or []]
    need("RM_DrawbridgeWinch_Timber" in there, "the timber winch stands beside the steel hinge", there)
    kv, t = leaf(z2)
    res["TIMBER_WINCH_NO_STEEL"] = (need(kv.get("winch") == "False", "a timber winch beside a steel hinge", t), t)
    w.call("jawa/build_batch", ops="RM_DrawbridgeWinch_Steel:%d,%d" % (X, z2 + 1), faction="player")
    kv, t = leaf(z2)
    res["STEEL_WINCH_LINKS"] = (need(kv.get("winch") == "True", "can-fail: a steel winch does link", t), t)
    # 3 the order shows itself: the selected winch's readout names the order
    proof("ProofOrder", "%d,%d;raise" % (X + 1, Z))
    info = w.call("jawa/list_things", rect="%d,%d,%d,%d" % (X, Z - 1, 1, 3), limit=20, includeInspect=True) or {}
    texts = [str(i.get("inspect") or i.get("inspectString") or "") for i in info.get("things") or []]
    hit = [s for s in texts if "Raise ordered" in s]
    line = w.call("jawa/static_call", type="RimMandrake.FlowWorks.Pits.RM_DrawbridgeProofs", method="ProofOrderLine", args="%d,%d" % (X + 1, Z)) or {}
    txt = str(line.get("result") or line)
    res["ORDER_SHOWS"] = (need("Raise ordered" in txt, "the readout names the order", txt), txt, hit[:1])
    w.call("rimworld/step_game_ticks", ticks=60, pauseFirst=True, timeoutMs=60000)
    txt = str((w.call("jawa/static_call", type="RimMandrake.FlowWorks.Pits.RM_DrawbridgeProofs", method="ProofOrderLine", args="%d,%d" % (X + 1, Z)) or {}).get("result"))
    res["ORDER_NAMES_WORKER"] = (need("winch" in txt, "the readout names its worker", txt), txt)
    for k, v in res.items():
        print("%-22s %s %s" % (k, "PASS" if v[0] else "FAIL", v[1:]))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
