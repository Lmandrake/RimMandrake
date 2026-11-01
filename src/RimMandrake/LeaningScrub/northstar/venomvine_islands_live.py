"""venomvine_islands_live.py -- VENOMVINE_BUILD_SCRUB_GROWS_TEETH live check on a REAL Leaning Scrub map (python.exe).

Two modes, both on the CURRENT map (the RM_TestSite_leaningscrub_v2 site: a real mapgen Scrub map with the islands the
shipped genstep laid; ProofIslands is NOT run here, it re-lays islands and belongs on a disposable map):

  check   (b) perf + pathing with the islands. Read-only except colonist walks and a short unpaused window.
          Rows: scrub.census, scrub.share, scrub.islands, scrub.rooms, scrub.clearance, scrub.path.<dir>,
          scrub.perf.creep_tick, scrub.perf.recount, scrub.perf.tps. Prints one PASS/FAIL/UNMEASURED table.
  stage   (c) numbered review stations: one per venomvine form present (the tall renders are provisional; the OWNER
          judges them, this script never does), a review label + an in-save sign book each, colonists drafted at the
          start, then a keeper save (refuses to overwrite) via modcheck/reviewmap.save_keeper.

Counted defs come from the RM_LeaningScrub BiomeDef's RM_VenomvineIslandsExtension (read from the XML, never guessed).
Evidence JSON goes to --out (default D:\\ClaudeWork\\rimmandrake\\venomvine_live).

  python.exe src/RimMandrake/LeaningScrub/northstar/venomvine_islands_live.py check | tr -d '\\r'
  python.exe src/RimMandrake/LeaningScrub/northstar/venomvine_islands_live.py stage --save RM_REVIEW_venomvine_tallrenders_20261101
"""
import argparse
import json
import math
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
UTILS = os.path.join(os.path.dirname(MOD), "Utils")
sys.path.insert(0, UTILS)
sys.path.insert(0, os.path.join(UTILS, "modcheck"))
import reviewmap  # noqa: E402

BIOME_XML = os.path.join(MOD, "Defs", "BiomeDefs", "RM_LeaningScrub_Biome.xml")
PROOF = "RimMandrake.LeaningScrub.RM_VenomvineIslandsUtil"
SHARE_TARGET = 0.15            # Settings default venomvineIslandShare (owner Q1: islands at about 15%)
CLEARANCE = 30.0               # Settings default venomvineStartClearance
CREEP_MS_PER_TICK_BAR = 0.02   # creep comp budget on a 250x250 map (sweep every 15000 ticks; should be ~0)
RECOUNT_MS_BAR = 100.0         # one full-map open-cell recount (bridge round trip included), once per sweep
TPS_RATIO_BAR = 0.80           # ticks / expected over the unpaused window at the speed we set


def counted_defs():
    x = open(BIOME_XML, encoding="utf-8").read()
    m = re.search(r'RM_VenomvineIslandsExtension">(.*?)</li>\s*</modExtensions>', x, re.S)
    if not m:
        raise SystemExit("no RM_VenomvineIslandsExtension in " + BIOME_XML)
    body = m.group(1)
    thicket = re.search(r"<thicketDef>(\w+)</thicketDef>", body).group(1)
    crown = re.search(r"<crownDef>(\w+)</crownDef>", body).group(1)
    forms = re.findall(r"<li>(\w+)</li>", re.search(r"<countedForms>(.*?)</countedForms>", body, re.S).group(1))
    rooms = re.findall(r"<form>(\w+)</form><role>(\w+)</role>", body)
    return thicket, crown, forms, rooms


def row(rows, rid, status, cls, data):
    rows.append(dict(id=rid, status=status, cls=cls if status != "PASS" else "", data=data))


def table(rows):
    w = max(len(r["id"]) for r in rows)
    for r in rows:
        print("%-*s  %-10s %-8s %s" % (w, r["id"], r["status"], r["cls"], json.dumps(r["data"])[:220]))
    n = {s: sum(1 for r in rows if r["status"] == s) for s in ("PASS", "FAIL", "UNMEASURED")}
    print("TOTAL", n)


ISLAND_MIN = 20   # cells: a component this big is an island; the biome's wildPlants also seed venomvine everywhere


def components(cells):
    """8-connected components of a set of (x,z) -> list of (size, centre, cellset), largest first."""
    seen, out = set(), []
    for c in cells:
        if c in seen:
            continue
        stack, mem = [c], set([c])
        seen.add(c)
        while stack:
            x, z = stack.pop()
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    q = (x + dx, z + dz)
                    if q in cells and q not in seen:
                        seen.add(q)
                        mem.add(q)
                        stack.append(q)
        n = len(mem)
        out.append((n, (sum(m[0] for m in mem) // n, sum(m[1] for m in mem) // n), mem))
    out.sort(key=lambda t: -t[0])
    return out


def census(B, defs):
    r = B.call("jawa/list_things", defName=",".join(defs), limit=30000)
    if r.get("success") is not True:
        return None, r
    return r, None


def colonists(B):
    r = B.call("rimworld/list_colonists", currentMapOnly=True)
    out = []
    for c in r.get("colonists", []) or []:
        if c.get("spawned") and not c.get("dead") and not c.get("downed"):
            out.append((c["pawnId"].replace("Thing_", ""), c["position"]["x"], c["position"]["z"]))
    return out


def check(B, out, rows, ev):
    thicket, crown, forms, rooms = counted_defs()
    defs = [thicket, crown] + forms + [f for f, _ in rooms]
    gi = B.call("rimworld/get_game_info")
    mi = B.call("jawa/map_info")
    ev["map"] = dict(biome=mi.get("mapBiome"), size=[mi.get("sizeX"), mi.get("sizeZ")], tick=gi.get("ticksGame"))
    if mi.get("mapBiome") != "RM_LeaningScrub":
        row(rows, "scrub.map", "UNMEASURED", "SITE", ev["map"])
        return rows, ev
    cols = colonists(B)
    ev["colonists"] = cols
    if not cols:
        row(rows, "scrub.map", "UNMEASURED", "SITE", "no free colonist")
        return rows, ev
    # the clearance is judged around the MAP START (the site's colonists start at the centre; after a walk they are
    # elsewhere, so their positions are not the start)
    sx, sz = mi.get("sizeX", 250) // 2, mi.get("sizeZ", 250) // 2
    ev["start"] = [sx, sz]

    lt, err = census(B, defs)
    if lt is None:
        row(rows, "scrub.census", "UNMEASURED", "HARNESS", err)
        return rows, ev
    things = lt.get("things", [])
    per = lt.get("perDef", {})
    ev["perDef"] = per
    complete = lt.get("isCompleteList") is True
    row(rows, "scrub.census", "PASS" if per.get(thicket, 0) > 0 and complete else ("UNMEASURED" if not complete else "FAIL"),
        "HARNESS" if not complete else "MOD", dict(matched=lt.get("countMatched"), complete=complete, scanned=lt.get("scanned")))

    t0 = time.time()
    oc = B.call("jawa/static_call", type=PROOF, method="CountOpen", args="current")
    recount_ms = (time.time() - t0) * 1000.0
    open_n = None
    try:
        open_n = int(str(oc.get("result", oc.get("value"))).strip())
    except Exception:  # noqa: BLE001
        pass
    ev["countOpen"] = dict(raw={k: oc.get(k) for k in ("success", "result", "value", "message")}, ms=recount_ms,
                           opMs=(oc.get("operation") or {}).get("DurationMs"))
    vine_n = len(things)
    if not open_n:
        row(rows, "scrub.share", "UNMEASURED", "HARNESS", ev["countOpen"])
    else:
        share = vine_n / float(open_n)
        ok = 0.5 * SHARE_TARGET <= share <= 1.6 * SHARE_TARGET
        row(rows, "scrub.share", "PASS" if ok else "FAIL", "MOD",
            dict(vine=vine_n, open=open_n, share=round(share, 4), bar="%.3f..%.3f" % (0.5 * SHARE_TARGET, 1.6 * SHARE_TARGET)))

    # NOTE the biome's wildPlants seed venomvine (thicket 0.15 + every form) all over the map, so share/rooms/clearance
    # judge the ISLANDS (8-connected components >= ISLAND_MIN cells), and the all-vine share is reported beside it.
    cells = set((t["x"], t["z"]) for t in things)
    comps = components(cells)
    big = [c for c in comps if c[0] >= ISLAND_MIN]
    island_cells = set().union(*[c[2] for c in big]) if big else set()
    ev["islands"] = [dict(cells=n, centre=c) for n, c, _m in big[:60]]
    row(rows, "scrub.islands", "PASS" if len(big) >= 3 else "FAIL", "MOD",
        dict(islands=len(big), minCells=ISLAND_MIN, largest=big[0][0] if big else 0, islandCells=len(island_cells),
             islandShare=round(len(island_cells) / float(open_n), 4) if open_n else None, components=len(comps)))

    room_defs = set(f for f, _ in rooms)
    by_cell = {}
    for t in things:
        by_cell.setdefault((t["x"], t["z"]), set()).add(t["def"])
    with_room, forms_in = 0, set()
    for _n, _c, mem in big:
        here = set()
        for c in mem:
            here |= by_cell.get(c, set()) & room_defs
        forms_in |= here
        with_room += 1 if here else 0
    ok = big and with_room >= 0.5 * len(big) and len(forms_in) >= 3
    row(rows, "scrub.rooms", "PASS" if ok else "FAIL", "MOD",
        dict(islands=len(big), withRoom=with_room, roomFormsInIslands=len(forms_in), of=len(room_defs),
             absent=sorted(room_defs - forms_in)))

    # The genstep keeps islands out of a CLEARANCE disc round MapGenerator.PlayerStartSpot, which is not saved; the
    # loaded site only shows where prep put the colonists (the centre). So: find the largest island-free disc whose
    # centre is within 40 cells of the map centre. Can fail: no such disc of 0.9 x CLEARANCE means islands crowd the
    # whole middle of the map.
    best, best_r = None, -1.0
    ic = list(island_cells)
    for x in range(sx - 40, sx + 41, 2):
        for z in range(sz - 40, sz + 41, 2):
            r = min(math.hypot(a_ - x, b_ - z) for a_, b_ in ic) if ic else 999.0
            if r > best_r:
                best, best_r = (x, z), r
    row(rows, "scrub.clearance", "PASS" if best_r >= 0.9 * CLEARANCE else "FAIL", "MOD",
        dict(freeDiscCentre=best, freeDiscRadius=round(best_r, 1), bar=round(0.9 * CLEARANCE, 1), searchedWithin=40,
             note="start spot is not saved; disc search stands in for it"))
    ev["things"] = [(t["def"], t["x"], t["z"], t["id"]) for t in things]

    # ---- pathing: walk one colonist to each far quadrant, past/through island country, and read where it ended
    sx_, sz_ = mi.get("sizeX", 250), mi.get("sizeZ", 250)
    targets = dict(north=(sx, sz_ - 12), south=(sx, 12), east=(sx_ - 12, sz), west=(12, sz))
    B.call("rimworld/set_time_speed", speed="Superfast")
    # every walk starts at the start: first bring everyone back (a previous run leaves them at the edges).
    # Everyone stays DRAFTED for the whole block: an undrafted colonist wanders into the vine between walks,
    # and then a venom dose cannot be charged to the ordered walk (run4, 2026-11-01: Rotary idled to (112,193)).
    home = B.call("jawa/order_pawn", pawnId="colonists", x=sx, z=sz, waitTicks=2500, undraftAfter=False)
    ev["path_home"] = {k: home.get(k) for k in home if k not in ("operation", "state")}
    cols = colonists(B)
    for i, (name, (tx, tz)) in enumerate(targets.items()):
        pid, px, pz = cols[i % len(cols)]
        if i >= len(cols):     # a reused colonist: back to the start first
            B.call("jawa/order_pawn", pawnId=pid, x=sx, z=sz, waitTicks=2500, undraftAfter=False)
            px, pz = sx, sz
        rr = B.call("jawa/order_pawn", pawnId=pid, x=tx, z=tz, waitTicks=2500, undraftAfter=False)
        ev["path_" + name] = {k: rr.get(k) for k in rr if k not in ("operation", "state")}
        hurt = [(c.get("name"), "dead" if c.get("dead") else "downed")
                for c in (B.call("rimworld/list_colonists", currentMapOnly=True).get("colonists") or [])
                if c.get("dead") or c.get("downed")]
        ev.setdefault("hurt_after", {})[name] = dict(walker=pid, hurt=hurt)   # which walk the harm followed
        res = (rr.get("results") or rr.get("pawns") or [rr])
        res = res[0] if isinstance(res, list) and res else res
        can = res.get("canReach") if isinstance(res, dict) else None
        end = (res.get("endPosition") or res.get("end") or res.get("position")) if isinstance(res, dict) else None
        ex, ez = reviewmap.pawn_xz(dict(position=end)) if end else (None, None)
        if can is None:
            row(rows, "scrub.path." + name, "UNMEASURED", "HARNESS", str(ev["path_" + name])[:300])
            continue
        st = res.get("start") if isinstance(res, dict) else None
        if isinstance(st, dict):
            px, pz = st.get("x", px), st.get("z", pz)
        d0 = math.hypot(tx - px, tz - pz)
        dl = math.hypot(tx - ex, tz - ez) if ex is not None else None
        ok = can is True and dl is not None and dl <= 2 and d0 >= 60
        row(rows, "scrub.path." + name, "PASS" if ok else ("FAIL" if can is False else "UNMEASURED"),
            "MOD" if can is False else "HARNESS",
            dict(target=[tx, tz], canReach=can, start=[px, pz], end=[ex, ez], left=round(dl, 1) if dl is not None else None,
                 walked=round(d0), ticks=rr.get("ticksElapsed"), arrived=res.get("arrived")))
    B.call("rimworld/pause_game", pause=True)
    # a walk that downs or kills a colonist is the pathing answer on this map (venomvine is a contact-venom plant)
    after = B.call("rimworld/list_colonists", currentMapOnly=True).get("colonists", []) or []
    lost = [(c["pawnId"], c.get("name"), "dead" if c.get("dead") else "downed") for c in after if c.get("dead") or c.get("downed")]
    deaths = [x.get("label") for x in (B.call("rimworld/list_letters").get("letters") or []) if "Death" in str(x.get("letterDef"))]
    ev["colony_after_walks"] = dict(lost=lost, deathLetters=deaths)
    row(rows, "scrub.path.colony_survives", "PASS" if not lost and not deaths else "FAIL", "MOD",
        dict(downedOrDead=lost, deathLetters=deaths, perWalk=ev.get("hurt_after")))

    # ---- perf: map comp timing over an unpaused window, the TPS record over it, and the recount cost
    B.call("rimworld/set_time_speed", speed="Superfast")
    mt = B.call("jawa/map_comp_timing", ticks=1200, maxSeconds=90, top=40)
    tps = B.call("jawa/tps_report", last=6)
    tp = B.call("jawa/time_perf")
    B.call("rimworld/pause_game", pause=True)
    gi2 = B.call("rimworld/get_game_info")
    ev["comp_timing"] = {k: mt.get(k) for k in mt if k not in ("operation", "state")}
    ev["tps"] = {k: tps.get(k) for k in tps if k not in ("operation", "state")}
    ev["time_perf"] = {k: tp.get(k) for k in tp if k not in ("operation", "state")}
    ev["paused_after"] = (gi2.get("state") or {}).get("paused")
    comps_t = mt.get("components") or mt.get("top") or []
    creep = [c for c in comps_t if "VenomvineCreep" in json.dumps(c)]
    if mt.get("success") is not True or not comps_t:
        row(rows, "scrub.perf.creep_tick", "UNMEASURED", "HARNESS", str(ev["comp_timing"])[:300])
    else:
        c = creep[0] if creep else {}
        mspt = c.get("msPerTick", c.get("msPerElapsedTick"))
        if not creep:
            # absent from a top-40 list that has entries: below the smallest listed (sanity: the list is non-empty)
            row(rows, "scrub.perf.creep_tick", "PASS", "", dict(listed=len(comps_t), creep="below top-40",
                                                                 elapsed=mt.get("elapsedTicks")))
        else:
            ok = mspt is not None and float(mspt) <= CREEP_MS_PER_TICK_BAR
            row(rows, "scrub.perf.creep_tick", "PASS" if ok else "FAIL", "MOD",
                dict(msPerTick=mspt, bar=CREEP_MS_PER_TICK_BAR, entry=c))
    if open_n:
        op_ms = ev["countOpen"]["opMs"]
        ms = float(op_ms) if op_ms is not None else recount_ms
        row(rows, "scrub.perf.recount", "PASS" if ms <= RECOUNT_MS_BAR else "FAIL", "MOD",
            dict(ms=round(ms, 1), bar=RECOUNT_MS_BAR, everyTicks=15000))
    wins = []
    for line in tps.get("samplesJsonl") or []:
        try:
            wins.append(json.loads(line) if isinstance(line, str) else line)
        except ValueError:
            pass
    unp = [w for w in wins if isinstance(w, dict) and w.get("state") == "run" and w.get("ratio") is not None]
    if not unp:
        row(rows, "scrub.perf.tps", "UNMEASURED", "HARNESS", str(ev["tps"])[:300])
    else:
        best = max(float(w["ratio"]) for w in unp)
        row(rows, "scrub.perf.tps", "PASS" if best >= TPS_RATIO_BAR else "FAIL", "MOD",
            dict(bestRatio=round(best, 3), bar=TPS_RATIO_BAR, windows=len(unp), pausedAfter=ev["paused_after"]))
    return rows, ev


FORM_NOTE = {}


def load_site(B, name, budget_s=300):
    try:
        B.call("rimworld/load_game", saveName=name, ignoreModCompatibility=True)
    except Exception:  # noqa: BLE001 - polled below, never resent
        pass
    t0 = time.time()
    while time.time() - t0 < budget_s:
        time.sleep(5)
        try:
            st = (B.call("rimworld/get_game_info").get("state") or {}).get("programState")
            if st == "Playing" and B.call("jawa/map_info").get("tile") is not None:
                time.sleep(40)     # the game is drivable ~40 s after it first answers: hold mutations
                return round(time.time() - t0, 1), B
        except Exception:  # noqa: BLE001 - a timeout poisons the socket: reopen, keep polling
            B = reviewmap.LiveBridge()
    return None, B


def stage(B, out, save, rows, ev, load=""):
    thicket, crown, forms, rooms = counted_defs()
    defs = [thicket, crown] + forms + [f for f, _ in rooms]
    mi = B.call("jawa/map_info")
    if mi.get("mapBiome") != "RM_LeaningScrub":
        row(rows, "stage.map", "UNMEASURED", "SITE", mi.get("mapBiome"))
        return rows, ev
    cols = colonists(B)
    sx = sum(c[1] for c in cols) // max(1, len(cols))
    sz = sum(c[2] for c in cols) // max(1, len(cols))
    lt, err = census(B, defs)
    if lt is None:
        row(rows, "stage.census", "UNMEASURED", "HARNESS", err)
        return rows, ev
    things = lt["things"]
    # one station per form present: the instance nearest the start (shortest walk for the owner); stations must sit
    # >= 9 cells apart so their labels do not overlap
    picks = []
    for d in defs:
        cand = sorted((t for t in things if t["def"] == d), key=lambda t: (t["x"] - sx) ** 2 + (t["z"] - sz) ** 2)
        for t in cand:
            if all((t["x"] - p["x"]) ** 2 + (t["z"] - p["z"]) ** 2 >= 81 for p in picks):
                picks.append(t)
                break
    picks.sort(key=lambda t: math.atan2(t["z"] - sz, t["x"] - sx))      # a loop around the start
    labels, books, stations = [], [], []
    role = dict(rooms)
    for i, t in enumerate(picks, 1):
        key = "%02d" % i
        kind = "thicket (island body)" if t["def"] == thicket else "crown" if t["def"] == crown else \
            "counted form" if t["def"] in forms else "room form (%s)" % role.get(t["def"], "?")
        look = "the %s at the sign: tall render installed provisionally" % t["label"]
        do = "zoom in on it; compare with its neighbours"
        decide = "keep or reject this render (rejects come out)"
        labels.append(reviewmap.label_line(t["x"], t["z"] + 2, "%s %s" % (key, t["label"]),
                                           reviewmap.sign_sub(kind, look, do, decide), tag="venomvine"))
        bx, bz = t["x"] + 1, t["z"]
        books.append(reviewmap.sign_book(bx, bz, key, t["label"], kind, look, do, decide,
                                         more="def %s at (%d,%d)" % (t["def"], t["x"], t["z"])))
        stations.append(dict(key=key, defName=t["def"], label=t["label"], x=t["x"], z=t["z"], id=t["id"]))
    ev["stations"] = stations
    B.call("jawa/review_label", action="clear", tag="venomvine")
    lr = B.call("jawa/review_label", action="add", ops="\n".join(labels), tag="venomvine")
    sr = reviewmap.place_signs(B, books)
    ev["labels"] = {k: lr.get(k) for k in lr if k not in ("operation", "state")}
    ev["signs"] = {k: sr.get(k) for k in sr if k not in ("operation", "state")}
    placed = len(sr.get("placed") or [])
    row(rows, "stage.stations", "PASS" if len(stations) >= len(defs) - 2 and lr.get("success") is True else "FAIL",
        "HARNESS", dict(stations=len(stations), forms=len(defs), labelOk=lr.get("success")))
    row(rows, "stage.signs", "PASS" if placed == len(books) else "FAIL", "HARNESS",
        dict(placed=placed, wanted=len(books), refused=sr.get("refused")))
    for c in cols:
        B.call("jawa/set_draft", pawnId=c[0], drafted=True)
    B.call("rimworld/pause_game", pause=True)
    B.call("jawa/clear_ui", all=True)
    if save:
        k = reviewmap.save_keeper(B, save, saves=reviewmap.SAVES, signs=labels)
        ev["keeper"] = k
        row(rows, "stage.keeper", "PASS" if k.get("ok") else "FAIL", "HARNESS",
            dict(name=save, new=k.get("new"), changed=k.get("changed"), gone=k.get("gone"), refused=k.get("refused")))
    return rows, ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("check", "stage"))
    ap.add_argument("--save", default="")
    ap.add_argument("--load", default="", help="load this save first (e.g. RM_TestSite_leaningscrub_v2)")
    ap.add_argument("--out", default=r"D:\ClaudeWork\rimmandrake\venomvine_live")
    a = ap.parse_args()
    B = reviewmap.LiveBridge()
    rows, ev = [], {}
    try:
        if a.load:   # the check walks colonists into venom and the stage mutates: both want a fresh site
            ev["load_s"], B = load_site(B, a.load)
            if ev["load_s"] is None:
                row(rows, a.mode + ".load", "UNMEASURED", "HARNESS", "no Playing map after load_game " + a.load)
        if not rows:
            check(B, a.out, rows, ev) if a.mode == "check" else stage(B, a.out, a.save, rows, ev)
    except Exception as e:  # noqa: BLE001  -- a crash is a HARNESS row, and the evidence so far is still written
        import traceback
        rows.append(dict(id="harness.crash", status="UNMEASURED", cls="HARNESS", data=traceback.format_exc()[-600:]))
        B.call("rimworld/pause_game", pause=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "%s_%s.json" % (a.mode, stamp))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dict(mode=a.mode, rows=rows, evidence=ev), f, indent=1)
    table(rows)
    print("EVIDENCE", path)


if __name__ == "__main__":
    main()
