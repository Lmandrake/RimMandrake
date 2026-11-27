"""live_deck_art_picks.py -- the live bridge test of RIMMANDRAKE_INSTALL_JETTY_BRIDGE_PICKS_HEAVY_B_CHOSEN_TWO_PICKS_OPEN: build
each of the owner's seven picked jetties and bridges once over a dug pit (1, 2 and 4 squares where allowed; east/west and
north/south), read what each will draw (RM_SuspensionProofs.ProofDeckArt), walk a colonist across one bridge, and capture
every station zoomed plus the whole yard at default zoom. A person LOOKS at every capture; this script decides nothing.

Run from the repo root with the bridge on a game holding FlowWorks (tier `flowworks`) and a quicktest map up:
    eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"
    python3 src/RimMandrake/Utils/../FlowWorks/northstar/live_deck_art_picks.py [--origin X,Z] [--out DIR]
    ... --jetties     only the jetty yard: steel and heavy, each look, 2 squares east and 2 north (16 stations)
    ... --heavy-scrapper   only the Scrapper heavy bridge (RIMMANDRAKE_DRAW_SCRAPPER_JETTIES_HEAVY_BRIDGE_IN_HIS_PICKED_MANNER):
                      east-west 2 and 4 squares and north-south 4, a drafted colonist mid-span on each (bare, then in a
                      cowboy hat), captures on the deck middle and on each end (anchor + post)
    ... --heavy-scrapper --draw-order   also read how each colonist is drawn (jawa/pawn_render_nodes, close and default
                      zoom) and every section draw on its square and the square north (jawa/cell_draw_census, probeY = its
                      highest drawn node); --queue-experiment adds, on ew4, the cable material's queue set below then above
                      the colonist's, a close capture each, then given back (jawa/material_queue); --rope-sides decides
                      by state: on an east-west span the rope north of the deck lies below the colonist's lowest drawn
                      node and the near rope above his highest; on a north-south span both side ropes lie above him (as
                      before). Each vertex's height decides what covers him (the depth test; every section sub-mesh is
                      drawn before him, its bounds at y 0). Exit 1 unless every bridge reads PASS.
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


HEAVY_SCRAPPER_STRIP = "SuspensionBridge/Scrapper/RM_SuspensionDeck_Heavy_Strip"   # the installed pieces' texture folder
HAT = "Apparel_CowboyHat"       # a vanilla hat with a wide brim: the head's highest reach into a far-side hanger
# rootSize for the close captures: 5 gave 656 px over 5 cells = 131 px/cell on ArchSmall (2026-11-27, 2463x1310 window); the
# offline judge (verdict_heavy_bridge_Scrapper_B.md Q1/Q2) asked ~128 px/cell. set_camera_zoom clamps at 8 (~82 px/cell
# measured the same day); screenshot_cell_rect's rootSize does not.
CLOSE_ROOT = 5.0
CLOSE_CELLS = 5                 # a 5x5 cell clip centred on the subject: the pawn's square, or the anchor with its post


def close_snap(w, out, name, cell):
    """A CLOSE_CELLS square clip centred on cell at CLOSE_ROOT, copied to out/name.png. Returns the path or an
    UNMEASURED reason (never a silent None)."""
    import shutil
    h = CLOSE_CELLS // 2
    r = w.call("rimworld/screenshot_cell_rect", x=cell[0] - h, z=cell[1] - h, width=CLOSE_CELLS, height=CLOSE_CELLS,
               paddingCells=0, fileName="hscrap_%s_%d" % (name, int(time.time())), rootSize=CLOSE_ROOT) or {}
    src = r.get("path")
    for _ in range(12):
        if src and os.path.exists(src):
            break
        time.sleep(0.5)
    try:
        dst = os.path.join(out, name + ".png")
        shutil.copyfile(src, dst)
        time.sleep(1.0)       # take_screenshot names files by the second
        return dst
    except Exception as ex:  # noqa: BLE001
        return "UNMEASURED: close capture %s failed: %s (%s)" % (name, ex, str(r)[:160])


def plan_heavy_scrapper(ox, oz):
    """The Scrapper heavy bridge, east-west 2 and 4 squares (8 apart in z) and north-south 4 (12 east) -- pure.
    The ticket's two questions: (a) cables drawn over a colonist mid-span, (b) the rusty posts on the old anchor frames."""
    out = []
    for k, n in enumerate((2, 4)):
        x0, z = ox, oz + k * 8
        pit = [(x, z + dz) for x in range(x0 + 1, x0 + 1 + n) for dz in (-1, 0, 1)]
        out.append(("ew%d_heavy_Scrapper" % n, "bridge", "Scrapper", "heavy", (x0, z), (x0 + n + 1, z), pit,
                    (x0 - 1, z - 2, n + 4, 5)))
    x, z0 = ox + 12, oz
    out.append(("ns4_heavy_Scrapper", "bridge", "Scrapper", "heavy", (x, z0), (x, z0 + 5),
                [(x + dx, z) for z in range(z0 + 1, z0 + 5) for dx in (-1, 0, 1)], (x - 2, z0 - 1, 5, 8)))
    return out


def mid_cell(p, q):
    """The deck square a colonist stands on mid-span: the middle of the run, rounded toward p -- pure."""
    dx, dz = (q[0] > p[0]) - (q[0] < p[0]), (q[1] > p[1]) - (q[1] < p[1])
    k = (abs(q[0] - p[0]) + abs(q[1] - p[1])) // 2
    return (p[0] + dx * k, p[1] + dz * k)


def deckart_ok(txt):
    """(ok, why) for a DECKART reading of a Scrapper heavy bridge: the Scrapper heavy strip, complete=True -- pure."""
    t = txt or ""
    if not t.startswith("DECKART look=Scrapper"):
        return False, "not a Scrapper DECKART reading"
    if HEAVY_SCRAPPER_STRIP not in t:
        return False, "strip is not %s" % HEAVY_SCRAPPER_STRIP
    if " complete=True" not in t:
        return False, "complete is not True"
    return True, "Scrapper heavy strip, complete=True"


def heavy_scrapper_look(w, out, stations, readings):
    """Per bridge: a drafted colonist mid-span, captured bare and in a hat on the deck middle, then each end framed on its
    anchor and post. Returns [(bridge, capture name, path or UNMEASURED reason)]."""
    shots = []
    for name, kind, look, tier, p, q, pit, rect in stations:
        cell = mid_cell(p, q)
        r = w.call("jawa/spawn_pawn", kindDef="Colonist", faction="PlayerColony", x=cell[0], z=cell[1]) or {}
        rows = r.get("pawns") or []
        pid = rows[0].get("id") if rows and isinstance(rows[0], dict) else None
        if not r.get("spawnedCount") or not pid:
            shots.append((name, "mid", "UNMEASURED: spawn_pawn on %s refused: %s" % (cell, str(r)[:160])))
            continue
        d = w.call("jawa/set_draft", pawnId=pid, drafted=True) or {}
        readings[name]["pawn"] = dict(id=pid, cell=cell, drafted=d.get("success", d))
        shots.append((name, "mid_bare", close_snap(w, out, "%s_mid_bare" % name, cell)))
        g = w.call("jawa/pawn_gear", **{"pawn": pid, "action": "wear", "def": HAT}) or {}   # `def` is a Python keyword
        readings[name]["hat"] = dict(success=g.get("success"), gear=str(g.get("apparel") or g.get("gear") or "")[:300])
        shots.append((name, "mid_hat", close_snap(w, out, "%s_mid_hat" % name, cell)))
        for tag, e in (("endA", p), ("endB", q)):
            shots.append((name, tag, close_snap(w, out, "%s_%s" % (name, tag), e)))
    return shots


def _pawn_line(name, tag, n):
    """One printed line of a jawa/pawn_render_nodes reading -- pure."""
    if not n.get("success"):
        return "DRAWORDER %s pawn %s: UNMEASURED %s" % (name, tag, str(n)[:200])
    reqs = n.get("requests") or []
    qs = sorted({r.get("renderQueue") for r in reqs})
    top = max(reqs, key=lambda r: (r.get("drawn") or [0, -1])[1]) if reqs else {}
    return ("DRAWORDER %s pawn %s: path=%s root=%s frames=%s bodyY=%s nodesY=%s queues=%s top=%s/%s/%s q%s cached=%s" % (
        name, tag, n.get("drawPath"), n.get("cameraRootSize"), n.get("framesSinceDraw"), (n.get("bodyPos") or [0, None])[1],
        n.get("nodesY"), qs, top.get("node"), top.get("shader"), (top.get("drawn") or [0, None])[1], top.get("renderQueue"),
        n.get("cachedQuad")))


def _census_lines(name, tag, c):
    """The printed lines of a jawa/cell_draw_census reading -- pure."""
    if not c.get("success"):
        return ["DRAWORDER %s census %s: UNMEASURED %s" % (name, tag, str(c)[:200])]
    out = []
    for d in c.get("draws") or []:
        out.append("DRAWORDER %s census %s: %s %s id=%s %s q%s boundsY=%s vertY=%s squareY=%s vsProbe=%s straddles=%s drawn=%s" % (
            name, tag, d.get("layer"), d.get("material"), d.get("materialId"), d.get("shader"), d.get("renderQueue"),
            d.get("boundsY"), d.get("vertY"), d.get("squareY"), d.get("boundsVsProbe"), d.get("straddlesProbe"), d.get("drawn")))
    return out or ["DRAWORDER %s census %s: [] (no section draw on the square)" % (name, tag)]


CABLE_MATS = ("cable", "rail_timber", "rope")     # the material names a bridge's ropes print with (RM_DeckArtExtension.cable)


def is_cable(material):
    """Is a census draw's material a bridge rope's -- pure."""
    m = str(material or "").lower()
    return any(k in m for k in CABLE_MATS)


def census_cells(p, q, cell):
    """The squares a bridge's side ropes cross beside a colonist mid-span, as {tag: (x, z)} -- pure. East-west: his own square
    (the near rope, south of the deck, crosses his body there) and the square north (the far rope and its hangers). North-south:
    the squares east and west of him and the two north of those."""
    x, z = cell
    if p[1] == q[1]:
        return {"0,0": (x, z), "0,1": (x, z + 1)}
    return {"-1,0": (x - 1, z), "1,0": (x + 1, z), "-1,1": (x - 1, z + 1), "1,1": (x + 1, z + 1)}


def node_span(reading):
    """(lowest, highest) drawn height of a colonist from a jawa/pawn_render_nodes reading: the requests with a material when
    he is drawn node by node, the one quad when he is drawn as his cached atlas frame (the requests then hold the atlas
    render's spots near y 0, never drawn on the map: SteveDesktop 2026-11-27); None when nothing drawn was read -- pure."""
    if not (reading or {}).get("success"):
        return None
    path = reading.get("drawPath")
    if path == "cachedAtlas":
        ys = [(reading.get("cachedQuad") or {}).get("y")]
    elif path == "nodes":
        ys = [(r.get("drawn") or [0, None])[1] for r in reading.get("requests") or []
              if isinstance(r.get("renderQueue"), int) and r.get("renderQueue") >= 0]
    else:
        return None
    ys = [y for y in ys if isinstance(y, (int, float))]
    return (min(ys), max(ys)) if ys else None


def cable_ys(census):
    """[(min, max)] of the rope draws on a census square (squareY), drawn ones only -- pure. None when the census failed."""
    if not (census or {}).get("success"):
        return None
    out = []
    for d in census.get("draws") or []:
        sq = d.get("squareY") or {}
        if d.get("drawn") and is_cable(d.get("material")) and sq.get("n"):
            out.append((sq["min"], sq["max"]))
    return out


def rope_sides(ew, by_tag, spans):
    """("PASS"|"FAIL"|"UNMEASURED", why) -- pure. by_tag: {census tag: cable_ys}; spans: [node_span] of the colonist (each
    read zoom). East-west: every rope vertex on the square north of him ("0,1") lies below his lowest drawn node, and every
    one on his own square ("0,0") above his highest. North-south: every rope vertex beside him lies above his highest."""
    spans = [s for s in spans if s]
    if not spans:
        return "UNMEASURED", "no drawn node of the colonist was read"
    lo, hi = min(s[0] for s in spans), max(s[1] for s in spans)
    if any(v is None for v in by_tag.values()):
        return "UNMEASURED", "a census square could not be read: %s" % sorted(k for k, v in by_tag.items() if v is None)
    if ew:
        far, near = by_tag.get("0,1") or [], by_tag.get("0,0") or []
        if not far or not near:
            return "UNMEASURED", "no rope read on the %s square" % ("north" if not far else "colonist's")
        bad = []
        top = max(b for _, b in far)
        if top >= lo:
            bad.append("the rope north of the deck reaches y %.4f, not below his lowest node %.4f" % (top, lo))
        bottom = min(a for a, _ in near)
        if bottom <= hi:
            bad.append("the near rope reaches down to y %.4f, not above his highest node %.4f" % (bottom, hi))
        if bad:
            return "FAIL", "; ".join(bad)
        return "PASS", "north rope at most y %.4f < his nodes %.4f..%.4f < near rope from y %.4f" % (top, lo, hi, bottom)
    side = [s for v in by_tag.values() for s in v]
    if not side:
        return "UNMEASURED", "no rope read beside him"
    bottom = min(a for a, _ in side)
    if bottom <= hi:
        return "FAIL", "a side rope reaches down to y %.4f, not above his highest node %.4f" % (bottom, hi)
    return "PASS", "both side ropes from y %.4f, above his nodes %.4f..%.4f" % (bottom, lo, hi)


def draw_order(w, out, stations, readings, experiment):
    """RIMMANDRAKE_DRAW_SCRAPPER_JETTIES_HEAVY_BRIDGE_IN_HIS_PICKED_MANNER: the readings that say what decides whether a cable
    covers the colonist. Per bridge: how the colonist is drawn at the close and the default zoom, and every section draw on
    its square and the square north of it against its highest drawn node. With experiment, on ew4: the cable material's
    queue below, then above, the colonist's, a close capture each, then the shader's own queue again. Decides nothing."""
    for name, kind, look, tier, p, q, pit, rect in stations:
        pawn = readings.get(name, {}).get("pawn") or {}
        pid, cell = pawn.get("id"), pawn.get("cell")
        rec = readings.setdefault(name, {}).setdefault("draw_order", {})
        if not pid or not cell:
            w.say("DRAWORDER %s: UNMEASURED: no colonist on the deck" % name)
            continue
        for tag, root in (("close", 8.0), ("default", float(DEFAULT_ZOOM))):
            w.call("jawa/clear_ui", all=True)
            w.call("rimworld/jump_camera_to_cell", x=cell[0], z=cell[1])
            w.call("rimworld/set_camera_zoom", rootSize=root)
            time.sleep(1.5)
            n = w.call("jawa/pawn_render_nodes", pawnId=pid) or {}
            rec["pawn_" + tag] = n
            w.say(_pawn_line(name, tag, n))
        close = rec.get("pawn_close") or {}
        ys = [(r.get("drawn") or [0, None])[1] for r in close.get("requests") or []]
        ys = [y for y in ys if isinstance(y, (int, float))]
        probe = max(ys) if ys else -1.0
        rec["census"] = {}
        for tag, (cx, cz) in sorted(census_cells(p, q, cell).items()):
            c = w.call("jawa/cell_draw_census", x=cx, z=cz, probeY=probe) or {}
            rec["census"][tag] = c
            for ln in _census_lines(name, tag, c):
                w.say(ln)
        verdict, why = rope_sides(p[1] == q[1], {k: cable_ys(v) for k, v in rec["census"].items()},
                                  [node_span(rec.get("pawn_close")), node_span(rec.get("pawn_default"))])
        rec["rope_sides"] = dict(verdict=verdict, why=why)
        w.say("ROPESIDES %s: %s (%s)" % (name, verdict, why))
        if not experiment or not name.startswith("ew4"):
            continue
        # a null-material node (a status overlay) reads queue -1: only drawn nodes' queues count
        qs = [r.get("renderQueue") for r in close.get("requests") or [] if isinstance(r.get("renderQueue"), int) and r.get("renderQueue") >= 0]
        cables = sorted({d.get("materialId") for c in rec["census"].values() for d in (c or {}).get("draws") or []
                         if is_cable(d.get("material"))})
        if not qs or not cables:
            w.say("DRAWORDER %s experiment: UNMEASURED: pawn queues %s, cable materials %s" % (name, qs, cables))
            continue
        exp = rec.setdefault("experiment", [])
        for tag, queue in (("q_below", min(qs) - 1), ("q_above", max(qs) + 1), ("q_shader", -1)):
            for mid in cables:
                r = w.call("jawa/material_queue", materialId=mid, setQueue=queue) or {}
                exp.append(dict(step=tag, materialId=mid, setQueue=queue, reply=r))
                w.say("DRAWORDER %s experiment %s: material %s -> %s: %s" % (name, tag, mid, queue, str(r.get("materials") or r)[:240]))
            time.sleep(1.0)
            exp.append(dict(step=tag, shot=close_snap(w, out, "%s_mid_hat_%s" % (name, tag), cell)))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--origin", default=None)
    ap.add_argument("--out", default=os.path.join(C.REPO, "Transient", "deck_art_picks"))
    ap.add_argument("--no-build", action="store_true", help="the yard is already built: capture and read only")
    ap.add_argument("--jetties", action="store_true", help="build only the jetty yard: each tier in each look, east and north")
    ap.add_argument("--heavy-scrapper", action="store_true",
                    help="build only the Scrapper heavy bridge (EW 2 and 4, NS 4) with a colonist mid-span on each")
    ap.add_argument("--draw-order", action="store_true", help="with --heavy-scrapper: the draw-order readings of each colonist")
    ap.add_argument("--queue-experiment", action="store_true", help="with --draw-order: the cable queue experiment on ew4")
    ap.add_argument("--rope-sides", action="store_true", help="with --draw-order: exit 1 unless every bridge's ROPESIDES is PASS")
    a = ap.parse_args(argv)
    a.mock = False
    a.no_shots = False
    w = C.make_walk(a, a.out)
    sx, sz = C.map_size(w)
    ox, oz = map(int, a.origin.split(",")) if a.origin else (sx // 2 - 25, sz // 2 - 20)
    stations = plan_heavy_scrapper(ox, oz) if a.heavy_scrapper else plan_jetties(ox, oz) if a.jetties else plan(ox, oz)
    yard = (ox - 3, oz - 3, 22, 18) if a.heavy_scrapper else (ox - 3, oz - 3, 31, 31) if a.jetties else (ox - 3, oz - 3, 56, 40)
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
    if a.heavy_scrapper:
        bad = 0
        for name in [s_[0] for s_ in stations]:
            ok, why = deckart_ok(readings[name]["deckart"])
            readings[name]["deckart_check"] = dict(ok=ok, why=why)
            bad += not ok
            w.say("CHECK %s: %s (%s)" % (name, "OK" if ok else "BAD", why))
        w.say("CHECK heavy Scrapper DECKART: %d bad of %d read (limit 0)" % (bad, len(stations)))
        readings["_look"] = [list(t) for t in heavy_scrapper_look(w, a.out, stations, readings)]
        if a.draw_order:
            draw_order(w, a.out, stations, readings, a.queue_experiment)
        with open(os.path.join(a.out, "readings.json"), "w") as f:
            json.dump(readings, f, indent=1)
        w.say("WROTE %s" % os.path.join(a.out, "readings.json"))
        if a.draw_order and a.rope_sides:
            got = [(n, (readings.get(n, {}).get("rope_sides") or {}).get("verdict", "UNMEASURED")) for n in [s_[0] for s_ in stations]]
            bad = [g for g in got if g[1] != "PASS"]
            w.say("ROPESIDES: %d of %d PASS%s" % (len(got) - len(bad), len(got), "" if not bad else "; not PASS: %s" % bad))
            if bad:
                sys.exit(1)
        return
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
