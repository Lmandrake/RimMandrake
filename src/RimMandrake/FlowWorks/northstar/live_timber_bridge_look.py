"""live_timber_bridge_look.py -- the live look of RIMMANDRAKE_REDRAW_TIMBER_BRIDGE_FROM_HIS_THREE_PHOTOS: build timber ("plank")
suspension bridges over a dug pit -- the unstyled look 4 squares east/west railings off and on, north/south railed, 2 wide
railed, and each of the four looks railed (ProofLook ...;timber) -- read what each square and each end draws
(RM_SuspensionProofs.ProofDeckArt: drawn=, ends=), stand a colonist on two of them, and capture every station zoomed plus
the yard at default zoom. An art judge LOOKS at the captures against his photos 13, 14 and 15
(D:\\ClaudeWork\\rimmandrake\\showings\\FLOWWORKS_WALK3_20261125\\); the readings decide only that the new art is the art drawn:
every deck square a Timber_Strip piece (lane pieces _top/_bottom on the 2-wide one), every end a Timber_Abutment (never its
bollard picture: "No ropes tied to the ground for the wood bridge"), the deck complete, railed squares when on.

Run from the repo root with the bridge on a game holding FlowWorks and a map up:
    eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"
    python3 src/RimMandrake/FlowWorks/northstar/live_timber_bridge_look.py [--origin X,Z] [--out DIR]
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
STRIP = "RM_SuspensionDeck_Timber_Strip"
ABUT = "RM_SuspensionDeck_Timber_Abutment"
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")


def plan(ox, oz):
    """[(name, a, b, rails, pit cells, rect, look)] -- pure. a/b: the drag ends (the anchors); look None: ProofBuild timber."""
    out = []
    for k, rails in enumerate((False, True)):
        z = oz + k * 6
        pit = [(x, z + dz) for x in range(ox + 1, ox + 5) for dz in (-1, 0, 1)]
        out.append(("ew4_rails_%s" % ("on" if rails else "off"), (ox, z), (ox + 5, z), rails, pit, (ox - 1, z - 2, 8, 5), None))
    x = ox + 12
    pit = [(x + dx, z) for z in range(oz + 1, oz + 5) for dx in (-1, 0, 1)]
    out.append(("ns4_rails_on", (x, oz), (x, oz + 5), True, pit, (x - 2, oz - 1, 5, 8), None))
    z = oz + 12
    pit = [(xx, z + dz) for xx in range(ox + 1, ox + 5) for dz in (-1, 0, 1, 2)]
    out.append(("ew4_wide2_rails_on", (ox, z), (ox + 5, z + 1), True, pit, (ox - 1, z - 2, 8, 6), None))
    for k, look in enumerate(LOOKS):
        z = oz + 18 + k * 6
        pit = [(xx, z + dz) for xx in range(ox + 1, ox + 5) for dz in (-1, 0, 1)]
        out.append(("ew4_%s_rails_on" % look, (ox, z), (ox + 5, z), True, pit, (ox - 1, z - 2, 8, 5), look))
    return out


def judge_reading(name, txt, rails, rails_txt, width=1):
    """What the readings can decide: the timber art is what the game draws, on every square and both ends."""
    bad = []
    t = txt or ""
    drawn = t.split(" drawn=")[-1].split(" ")[0] if " drawn=" in t else ""
    ends = t.split(" ends=")[-1].split(" ")[0] if " ends=" in t else ""
    if "complete=True" not in t:
        bad.append("deck not complete")
    lanes = drawn.split("|") if drawn else []
    if len(lanes) != width:
        bad.append("drawn reads %d lanes, not %d" % (len(lanes), width))
    for li, row in enumerate(lanes):
        sq = row.split(",")
        want = "" if width == 1 else ("_top" if li == 0 else "_bottom" if li == width - 1 else "_open")
        for s in sq:
            if not s.startswith(STRIP) or not s.endswith(want) or (want == "" and s.endswith(("_top", "_bottom", "_open"))):
                bad.append("lane %d draws %s (want %s*%s)" % (li, s, STRIP, want))
    es = ends.split(",") if ends else []
    if len(es) != 2 * width or any(not e.startswith(ABUT) for e in es):
        bad.append("ends draw %s (want %d x %s): an anchor draws its bollards and ropes" % (es, 2 * width, ABUT))
    if rails and "railed=0" in (rails_txt or "railed=0"):
        bad.append("railings on but no railed square")
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--origin", default=None)
    ap.add_argument("--out", default=os.path.join(C.REPO, "Transient", "timber_bridge_look"))
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
    yard = (ox - 3, oz - 3, 22, 46)
    readings, faults = {}, {}
    if not a.no_build:
        w.clear_site(yard)
        for s in stations:
            for c in s[4]:
                w.dig(c, DEPTH)
        for name, p, q, rails, pit, rect, look in stations:
            if look:
                ok, txt = w.proof(SUSP, "ProofLook", "%s;%d,%d;%d,%d;timber" % ((look,) + p + q))
                w.say("LOOK %s: %s %s" % (name, ok, txt[:300]))
                readings.setdefault(name, {})["build"] = txt
                readings[name]["rails"] = "railed by ProofLook"
                continue
            ok, txt = w.proof(SUSP, "ProofBuild", "%d,%d;%d,%d;timber;god" % (p + q))
            w.say("BUILD %s: %s %s" % (name, ok, txt[:200]))
            readings.setdefault(name, {})["build"] = txt
            if rails:
                ok, txt = w.proof(SUSP, "ProofRails", "%d,%d;on" % (p[0] + (q[0] > p[0]), p[1] + (q[1] > p[1])))
                w.say("RAILS %s: %s %s" % (name, ok, txt[:200]))
                readings[name]["rails"] = txt
    for name, p, q, rails, pit, rect, look in stations:
        ok, txt = w.proof(SUSP, "ProofDeckArt", "%d,%d" % p)
        w.say("READ %s: %s" % (name, txt))
        readings.setdefault(name, {})["deckart"] = txt
        readings[name]["shot"] = C.snap(w, name, rect)
        bad = judge_reading(name, txt, rails, readings[name].get("rails"), width=1 + abs(q[1] - p[1]) if q[0] != p[0] else 1)
        if bad:
            faults[name] = bad
    x, z, wd, ht = yard
    w.call("jawa/clear_ui", all=True)
    w.call("rimworld/jump_camera_to_cell", x=x + wd // 2, z=z + ht // 2)
    w.call("rimworld/set_camera_zoom", rootSize=DEFAULT_ZOOM)
    time.sleep(1.5)
    r = w.call("jawa/take_screenshot", fileName="timberbridge_yard_%d" % int(time.time())) or {}
    readings["_yard_default"] = r.get("filePath")
    shots = []
    for s in stations:
        if s[0] not in ("ew4_rails_on", "ew4_wide2_rails_on"):
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
    w.say("TIMBER_BRIDGE_LOOK %s: %d stations, %d with faults %s (captures for the art judge in %s)"
          % (verdict, len(stations), len(faults), faults or "", a.out))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
