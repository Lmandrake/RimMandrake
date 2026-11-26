"""live_rope_bridge_look.py -- the live look of RIMMANDRAKE_REDRAW_ROPE_BRIDGE_AS_ROPES_AND_SPARSE_SLATS: build rope suspension
bridges over a dug pit (4 squares east/west and north/south, railings off and on; one 1-square bridge), read what each
draws (RM_SuspensionProofs.ProofDeckArt and ProofRails), stand a colonist on two of them, and capture every station zoomed
plus the yard at default zoom. A person or an art judge LOOKS at the captures against his reference photo
(D:\\ClaudeWork\\rimmandrake\\showings\\FLOWWORKS_WALK3_20261125\\12.png); the readings decide only that the new art is the
art drawn (strip=...Rope_Strip, pieces root/mid/tip or solo, complete=True, railed squares when on).

Run from the repo root with the bridge on a game holding FlowWorks and a map up:
    eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"
    python3 src/RimMandrake/FlowWorks/northstar/live_rope_bridge_look.py [--origin X,Z] [--out DIR]
Writes DIR/<station>.png, DIR/yard_default.png, DIR/pawn_on_*.png and DIR/readings.json (verdict line last).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fw_walk_common as C  # noqa: E402

SUSP = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
DEPTH = 8
DEFAULT_ZOOM = 24
STRIP = "RM_SuspensionDeck_Rope_Strip"


def plan(ox, oz):
    """[(name, a, b, rails, pit cells, rect)] -- pure. a/b: the drag ends (the anchors)."""
    out = []
    for k, rails in enumerate((False, True)):
        z = oz + k * 6
        pit = [(x, z + dz) for x in range(ox + 1, ox + 5) for dz in (-1, 0, 1)]
        out.append(("ew4_rails_%s" % ("on" if rails else "off"), (ox, z), (ox + 5, z), rails, pit, (ox - 1, z - 2, 8, 5)))
    for k, rails in enumerate((False, True)):
        x = ox + 12 + k * 6
        pit = [(x + dx, z) for z in range(oz + 1, oz + 5) for dx in (-1, 0, 1)]
        out.append(("ns4_rails_%s" % ("on" if rails else "off"), (x, oz), (x, oz + 5), rails, pit, (x - 2, oz - 1, 5, 8)))
    z = oz + 12
    out.append(("ew1_rails_off", (ox, z), (ox + 2, z), False, [(ox + 1, z + dz) for dz in (-1, 0, 1)], (ox - 1, z - 2, 5, 5)))
    return out


def judge_reading(name, txt, rails, rails_txt):
    """What the readings can decide: the rope art is what the game draws."""
    bad = []
    if STRIP not in (txt or ""):
        bad.append("strip is not the rope strip")
    if "complete=True" not in (txt or ""):
        bad.append("deck not complete (no hand ropes drawn)")
    if "old" in (txt or "").split("pieces=")[-1].split(" ")[0].split(","):
        bad.append("a square draws the old art")
    if rails and "railed=0" in (rails_txt or "railed=0"):
        bad.append("railings on but no railed square")
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--origin", default=None)
    ap.add_argument("--out", default=os.path.join(C.REPO, "Transient", "rope_bridge_look"))
    ap.add_argument("--no-build", action="store_true")
    a = ap.parse_args(argv)
    a.mock = False
    a.no_shots = False
    w = C.make_walk(a, a.out)
    if (w.call("rimworld/get_ui_state") or {}).get("programState") != "Playing":
        w.say("no game in progress: starting a quicktest map")
        try:
            r = w.call("rimworld/start_debug_game_ready", timeoutMs=900000, readiness="mapData", pauseIfNeeded=True)
            w.say("quicktest: %s" % str(r)[:300])
        except Exception as e:  # noqa: BLE001 -- seen 2026-11-25: the call outlived the client's 600 s deadline while the map was up
            w.say("quicktest call ended: %s" % str(e)[:200])
        for _ in range(120):   # hang guard: a quicktest map took ~90 s; 10 min is far above it
            try:
                if (w.call("rimworld/get_ui_state") or {}).get("programState") == "Playing":
                    break
            except Exception:  # noqa: BLE001
                pass
            time.sleep(5)
    sx, sz = C.map_size(w)
    ox, oz = map(int, a.origin.split(",")) if a.origin else (sx // 2 - 12, sz // 2 - 10)
    stations = plan(ox, oz)
    yard = (ox - 3, oz - 3, 30, 20)
    readings, faults = {}, {}
    if not a.no_build:
        w.clear_site(yard)
        for s in stations:
            for c in s[4]:
                w.dig(c, DEPTH)
        for name, p, q, rails, pit, rect in stations:
            ok, txt = w.proof(SUSP, "ProofBuild", "%d,%d;%d,%d;rope;god" % (p + q))
            w.say("BUILD %s: %s %s" % (name, ok, txt[:200]))
            readings.setdefault(name, {})["build"] = txt
            if rails:
                ok, txt = w.proof(SUSP, "ProofRails", "%d,%d;on" % (p[0] + (q[0] > p[0]), p[1] + (q[1] > p[1])))
                w.say("RAILS %s: %s %s" % (name, ok, txt[:200]))
                readings[name]["rails"] = txt
    for name, p, q, rails, pit, rect in stations:
        ok, txt = w.proof(SUSP, "ProofDeckArt", "%d,%d" % p)
        w.say("READ %s: %s" % (name, txt))
        readings.setdefault(name, {})["deckart"] = txt
        readings[name]["shot"] = C.snap(w, name, rect)
        bad = judge_reading(name, txt, rails, readings[name].get("rails"))
        if bad:
            faults[name] = bad
    x, z, wd, ht = yard
    w.call("jawa/clear_ui", all=True)
    w.call("rimworld/jump_camera_to_cell", x=x + wd // 2, z=z + ht // 2)
    w.call("rimworld/set_camera_zoom", rootSize=DEFAULT_ZOOM)
    time.sleep(1.5)
    r = w.call("jawa/take_screenshot", fileName="ropebridge_yard_%d" % int(time.time())) or {}
    readings["_yard_default"] = r.get("filePath")
    shots = []
    for s in stations:
        if s[0] not in ("ew4_rails_on", "ns4_rails_off"):
            continue
        p, q = s[1], s[2]
        dx, dz = (q[0] > p[0]) - (q[0] < p[0]), (q[1] > p[1]) - (q[1] < p[1])
        cell = (p[0] + dx * 2, p[1] + dz * 2)
        r = w.call("jawa/spawn_pawn", kindDef="Colonist", faction="PlayerColony", x=cell[0], z=cell[1]) or {}
        if not r.get("spawnedCount"):
            shots.append((s[0], "UNMEASURED: spawn_pawn on %s refused: %s" % (cell, str(r)[:160])))
            continue
        shots.append((s[0], C.snap(w, "pawn_on_" + s[0], s[5])))
    readings["_walk"] = dict(on_deck=shots)
    verdict = "PASS" if not faults else "FAIL"
    readings["_verdict"] = dict(verdict=verdict, faults=faults, stations=len(stations))
    with open(os.path.join(a.out, "readings.json"), "w") as f:
        json.dump(readings, f, indent=1)
    w.say("ROPE_BRIDGE_LOOK %s: %d stations, %d with faults %s (captures for the art judge in %s)"
          % (verdict, len(stations), len(faults), faults or "", a.out))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
