"""live_deck_art_picks.py -- the live bridge test of RIMMANDRAKE_INSTALL_JETTY_BRIDGE_PICKS_HEAVY_B_CHOSEN_TWO_PICKS_OPEN: build
each of the owner's seven picked jetties and bridges once over a dug pit (1, 2 and 4 squares where allowed; east/west and
north/south), read what each will draw (RM_SuspensionProofs.ProofDeckArt), walk a colonist across one bridge, and capture
every station zoomed plus the whole yard at default zoom. A person LOOKS at every capture; this script decides nothing.

Run from the repo root with the bridge on a game holding FlowWorks (tier `flowworks`) and a quicktest map up:
    eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"
    python3 src/RimMandrake/Utils/../FlowWorks/northstar/live_deck_art_picks.py [--origin X,Z] [--out DIR]
    ... --jetties     only the jetty yard: steel and heavy, each look, 2 squares east and 2 north (16 stations)
Writes DIR/<station>.png, DIR/yard_default.png, DIR/walk_*.png and DIR/readings.json (default Transient/deck_art_picks).
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
DEFAULT_ZOOM = 24       # CameraDriver's starting rootSize


def plan(ox, oz):
    """[(name, kind, look, tier, a, b, pit cells, rect)] -- pure. kind: bridge|jetty; a/b: drag ends."""
    out = []
    # east/west bridges, 4 deck squares: five picks, one row each 6 apart
    looks = [("Scrapper", "steel"), ("Industrial", "steel"), ("Modern", "steel"), ("Futuristic", "steel"), ("Industrial", "heavy")]
    for k, (look, tier) in enumerate(looks):
        x0, z = ox, oz + k * 6
        pit = [(x, z + dz) for x in range(x0 + 1, x0 + 5) for dz in (-1, 0, 1)]
        out.append(("ew4_%s_%s" % (tier, look), "bridge", look, tier, (x0, z), (x0 + 5, z), pit, (x0 - 1, z - 2, 8, 5)))
    # east/west 1 and 2 squares, steel Industrial and heavy Industrial
    for k, tier in enumerate(("steel", "heavy")):
        for j, n in enumerate((1, 2)):
            x0, z = ox + 10 + j * 7, oz + k * 6
            pit = [(x, z + dz) for x in range(x0 + 1, x0 + 1 + n) for dz in (-1, 0, 1)]
            out.append(("ew%d_%s_Industrial" % (n, tier), "bridge", "Industrial", tier, (x0, z), (x0 + n + 1, z), pit,
                        (x0 - 1, z - 2, n + 4, 5)))
    # north/south bridges, 4 deck squares
    for k, (look, tier) in enumerate(looks):
        x, z0 = ox + 26 + k * 5, oz
        pit = [(x + dx, z) for z in range(z0 + 1, z0 + 5) for dx in (-1, 0, 1)]
        out.append(("ns4_%s_%s" % (tier, look), "bridge", look, tier, (x, z0), (x, z0 + 5), pit, (x - 2, z0 - 1, 5, 8)))
    # jetties (Industrial, his picks): 2 east, 1 west, 2 north, 1 south, steel and heavy
    for k, tier in enumerate(("steel", "heavy")):
        zb = oz + 14 + k * 12
        xb = ox + 10
        out.append(("jetty_%s_E2" % tier, "jetty", "Industrial", tier, (xb, zb), (xb + 2, zb),
                    [(x, zb + dz) for x in range(xb + 1, xb + 4) for dz in (-1, 0, 1)], (xb - 1, zb - 2, 6, 5)))
        out.append(("jetty_%s_W1" % tier, "jetty", "Industrial", tier, (xb + 10, zb), (xb + 9, zb),
                    [(x, zb + dz) for x in range(xb + 7, xb + 10) for dz in (-1, 0, 1)], (xb + 6, zb - 2, 6, 5)))
        xn = ox + 26 + k * 10
        zn = oz + 12
        out.append(("jetty_%s_N2" % tier, "jetty", "Industrial", tier, (xn, zn), (xn, zn + 2),
                    [(xn + dx, z) for z in range(zn + 1, zn + 4) for dx in (-1, 0, 1)], (xn - 2, zn - 1, 5, 6)))
        out.append(("jetty_%s_S1" % tier, "jetty", "Industrial", tier, (xn + 5, zn + 4), (xn + 5, zn + 3),
                    [(xn + 5 + dx, z) for z in range(zn + 1, zn + 4) for dx in (-1, 0, 1)], (xn + 3, zn, 5, 6)))
    # the DEFAULT look (Scrapper): what a player who never picks a look builds -- the heavy bridge and both jetties
    zd = oz + 32
    out.append(("ew4_heavy_Scrapper_default", "bridge", "Scrapper", "heavy", (ox, zd), (ox + 5, zd),
                [(x, zd + dz) for x in range(ox + 1, ox + 5) for dz in (-1, 0, 1)], (ox - 1, zd - 2, 8, 5)))
    for k, tier in enumerate(("steel", "heavy")):
        xb = ox + 10 + k * 10
        out.append(("jetty_%s_E2_Scrapper_default" % tier, "jetty", "Scrapper", tier, (xb, zd), (xb + 2, zd),
                    [(x, zd + dz) for x in range(xb + 1, xb + 4) for dz in (-1, 0, 1)], (xb - 1, zd - 2, 6, 5)))
    return out


LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")


def plan_jetties(ox, oz):
    """RIMMANDRAKE_JOIN_JETTY_SQUARES_SEAMLESS_STILL_TWO_BLOCKS: each jetty tier in each of the four looks, 2 squares
    reaching east and 2 squares reaching north, one look per column (7 apart), one tier and direction per row -- pure.
    His walk 2026-11-25: stations 78/79 "still look like two blocks stuck together rather than a seamless whole"."""
    out = []
    for r, (tier, way) in enumerate((("steel", "E"), ("heavy", "E"), ("steel", "N"), ("heavy", "N"))):
        for c, look in enumerate(LOOKS):
            x, z = ox + c * 7, oz + r * 7
            if way == "E":
                pit = [(px, z + dz) for px in range(x + 1, x + 4) for dz in (-1, 0, 1)]
                out.append(("jetty_%s_E2_%s" % (tier, look), "jetty", look, tier, (x, z), (x + 2, z), pit, (x - 1, z - 2, 6, 5)))
            else:
                pit = [(x + dx, pz) for pz in range(z + 1, z + 4) for dx in (-1, 0, 1)]
                out.append(("jetty_%s_N2_%s" % (tier, look), "jetty", look, tier, (x, z), (x, z + 2), pit, (x - 2, z - 1, 5, 6)))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--origin", default=None)
    ap.add_argument("--out", default=os.path.join(C.REPO, "Transient", "deck_art_picks"))
    ap.add_argument("--no-build", action="store_true", help="the yard is already built: capture and read only")
    ap.add_argument("--jetties", action="store_true", help="build only the jetty yard: each tier in each look, east and north")
    a = ap.parse_args(argv)
    a.mock = False
    a.no_shots = False
    w = C.make_walk(a, a.out)
    sx, sz = C.map_size(w)
    ox, oz = map(int, a.origin.split(",")) if a.origin else (sx // 2 - 25, sz // 2 - 20)
    stations = plan_jetties(ox, oz) if a.jetties else plan(ox, oz)
    yard = (ox - 3, oz - 3, 31, 31) if a.jetties else (ox - 3, oz - 3, 56, 40)
    readings = {}
    if not a.no_build:
        w.clear_site(yard)
        for name, kind, look, tier, p, q, pit, rect in stations:
            for c in pit:
                w.dig(c, DEPTH)
        for name, kind, look, tier, p, q, pit, rect in stations:
            if kind == "bridge":
                ok, txt = w.proof(SUSP, "ProofLook", "%s;%d,%d;%d,%d%s" % (look, p[0], p[1], q[0], q[1], ";heavy" if tier == "heavy" else ""))
            else:
                ok, txt = w.proof(SUSP, "ProofJetty", "%d,%d;%d,%d;%s;god;%s" % (p + q + (tier, look)))
            w.say("BUILD %s: %s %s" % (name, ok, txt[:200]))
            readings.setdefault(name, {})["build"] = txt
    for name, kind, look, tier, p, q, pit, rect in stations:
        ok, txt = w.proof(SUSP, "ProofDeckArt", "%d,%d" % p)
        w.say("READ %s: %s" % (name, txt))
        readings.setdefault(name, {})["deckart"] = txt
        readings[name]["shot"] = C.snap(w, name, rect)
    # the whole yard at the default zoom
    x, z, wd, ht = yard
    w.call("jawa/clear_ui", all=True)
    w.call("rimworld/jump_camera_to_cell", x=x + wd // 2, z=z + ht // 2)
    w.call("rimworld/set_camera_zoom", rootSize=DEFAULT_ZOOM)
    time.sleep(1.5)
    r = w.call("jawa/take_screenshot", fileName="deckart_yard_%d" % int(time.time())) or {}
    readings["_yard_default"] = r.get("filePath")
    # a colonist STANDS on a deck square of each kind, so a capture shows whether the cables draw over a pawn.
    # HARNESS (2026-11-22, RIMMANDRAKE_DEPLOY_THIN_OUTLINE_ULLAI_INSTALLED_BUT_NO_GAME_HAS_IT): the old walk ordered a map
    # colonist across ew4_steel_Industrial and took 0 shots in 60 x 15 ticks (the pawn never reached the deck), so the
    # cable-over-pawn look went undecided. jawa/spawn_pawn on the deck square is deterministic.
    on_deck = {"ew4_steel_Industrial": 2, "ew4_heavy_Industrial": 2, "ns4_steel_Industrial": 2, "jetty_steel_E2": 1,
               "jetty_heavy_E2_Scrapper": 1, "jetty_heavy_N2_Scrapper": 1}
    shots = []
    for s in stations:
        if s[0] not in on_deck:
            continue
        p, q, k = s[4], s[5], on_deck[s[0]]
        dx, dz = (q[0] > p[0]) - (q[0] < p[0]), (q[1] > p[1]) - (q[1] < p[1])
        cell = (p[0] + dx * k, p[1] + dz * k)
        r = w.call("jawa/spawn_pawn", kindDef="Colonist", faction="PlayerColony", x=cell[0], z=cell[1]) or {}
        if not r.get("spawnedCount"):
            shots.append((s[0], "UNMEASURED: spawn_pawn on %s refused: %s" % (cell, str(r)[:160])))
            continue
        shots.append((s[0], C.snap(w, "pawn_on_" + s[0], s[7])))
    readings["_walk"] = dict(on_deck=shots)
    with open(os.path.join(a.out, "readings.json"), "w") as f:
        json.dump(readings, f, indent=1)
    w.say("WROTE %s" % os.path.join(a.out, "readings.json"))


if __name__ == "__main__":
    main()
