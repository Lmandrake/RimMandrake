"""river_scenes_walk.py -- RUNBOOK: python.exe src/RimMandrake/FlowWorks/northstar/river_scenes_walk.py all --prep   (~12-15 min live; bridge held; --prep founds a river map first via river_site.py, ~3-5 min of that)
   no --prep: the current Playing map must already be a river site.   one scene: ... go R3   |   just the map: ... prep
   offline proof of the script itself: python3 src/RimMandrake/FlowWorks/northstar/river_scenes_walk.py all --mock   (seconds, no game)

RIVER_SCENES_BUILD_WALKTHROUGH_WITH_CAPTIONS. The FlowWorks rivers extension (extensions_rivers.py is a pass/fail suite) as scenes
he can WATCH, in the water_scenes_walk.py style: each scene is staged on the river site map, the clock advances in small governed
steps with a pause, a screenshot is taken at each milestone, and every picture is saved with a caption panel beside it: WHAT YOU ARE
LOOKING AT, WHAT TO CHECK, PASS IF, FAILS IF, WHAT THE GAME MEASURED. Scenes:
  R1 surface current   a throwaway colonist stands in moving water and is carried; the mod's own grid and ProofShove are read
  R2 ford crossing     ford stones across the shallows: a colonist on them is not carried, a control colonist in open water is
  R3 wash-off-map      colonists on moving water at a map edge are swept off; the book rises; they walk home
  R4 bank weir         a weir on the bank edge (placed live, rotation read back) + the mod's place/pool/join proofs
  R5 sluice box        a sluice box on the shallows + the mod's placer proof (wash draws the shared stock; setting off washes nothing)
Words: MATCHES (the game did what the caption says), DIFFERS, UNMEASURED (could not be asked or not staged: reason printed),
CRASHED (a traceback was kept). Nothing here is a verdict: the owner judges. Output: Transient/fw_scenes/live/rivers/ (index.html,
<scene>_<moment>_panel.png, <scene>_rows.json, log, tracebacks). A crash in a scene is printed in full, kept in
<scene>_traceback_<stamp>.txt, recorded as a CRASHED row, and the walk goes on. Staged colonists are always removed afterwards.
The clock runs through water_scenes_walk.Walk.ticks (feeds colonists, resumes one GovernorStop). Throwaway colonists on moving water
take the shipped river bruise by design: it is DECLARED to the clock gate (as the swept chain does), never switched off.
"""
import argparse
import contextlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import fw_walk_common as C  # noqa: E402

REPO = C.REPO
for _p in (os.path.join(C.UTILS, "modcheck"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

OUT_LIVE = os.path.join(REPO, "Transient", "fw_scenes", "live", "rivers")
OUT_MOCK = os.path.join(REPO, "Transient", "fw_scenes", "mock", "rivers")
NORTHSTAR = os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "northstar")
RIVERS = "RimMandrake.FlowWorks.Rivers."
PROOF, WORKS = RIVERS + "RM_RiverWorksProof", RIVERS + "RM_RiverWorksProofWorks"
PLACER = "RimMandrake.FlowWorks.Quarry.RM_PlacerProof"
STEP_TICKS = 60            # one scan of the current is 250 ticks; a carried pawn steps every ~60: small steps so the eye follows
WATCH_STEPS = 6
SWEPT_CHUNK, SWEPT_MAX = 250, 1500   # extensions_rivers.SWEPT_WAIT_CHUNK / SWEPT_WAIT_MAX
ORDER = ["R1", "R2", "R3", "R4", "R5"]

SCENES = {
    "R1": dict(title="R1. The river carries whoever stands in it",
               legend="A throwaway colonist (drafted, so it stays put by choice) is placed in moving river water. Blue-green flowing water with lanes: fast lanes in the middle, slower edge lanes.",
               check=["Over the six steps the colonist should drift DOWNSTREAM, along the water, a few squares.",
                      "The mod's own grid should say the map has a current with a fast lane."],
               passif="Moved at least 3 squares along the river; the grid reports current > 0 and a fast lane; the fast-lane shove test moves a colonist 3 squares.",
               fails="The colonist stands still in the middle of moving water."),
    "R2": dict(title="R2. Ford stones: a safe crossing",
               legend="A line of 4 flat-stone squares laid over the shallow water (a ford). One colonist stands ON the middle stone; a control colonist stands in open shallow water a few squares away.",
               check=["The colonist on the stones should NOT move at all.",
                      "The control colonist in open water SHOULD drift (this proves the current was running)."],
               passif="Ford colonist unmoved, control moved, and the mod's ford shove test reads MOVED 0.",
               fails="The ford colonist is carried away, or the control does not move (then the test shows nothing)."),
    "R3": dict(title="R3. Swept off the map edge, then walks home",
               legend="Colonists stand on moving river water at the map edge where the river leaves. The game keeps a book of who was washed away (pending); after the current carries one off, they are walked home.",
               check=["Within about 1500 ticks at least one colonist should vanish off the edge (the book's pending count rises).",
                      "Then they return: pending drops back to 0 and the washed-away colonist is on the map again."],
               passif="pending rose, returned to 0, and a washed-away colonist is back on the map.",
               fails="Nobody is carried off in 1500 ticks, or the book empties but nobody is back."),
    "R4": dict(title="R4. A bank weir holds the river back",
               legend="A weir (a short wall) standing on the bank edge facing the water. The mod's own proofs build and remove their own weirs; the picture is a weir placed by this script, its rotation read back from the game.",
               check=["The weir stands on the bank edge, facing the river.",
                      "The proofs: it may only be placed on a bank edge (not dry land, not open water), it arrests and calms the water upstream (pool), and two weirs join into one continuous wall."],
               passif="Place test edge=True dry=False wet=False; pool arrested and dropped > 0; joined wall run=2 with the pool gap 0.",
               fails="A weir accepted on dry land or in open water, no pool behind it, or a gap draining the joined wall."),
    "R5": dict(title="R5. A sluice box washes the river's gravel",
               legend="A sluice box (a 1x2 trough) standing in the shallows. The mod's placer proof builds its own box and washes the shared mineral stock.",
               check=["The box stands in shallow water, rotation as read.",
                      "A wash must draw what comes out FROM the shared stock, and with the setting off nothing may be washed."],
               passif="poolCount > 0; got > 0; the stock fell by what came out; sluice=off with the setting off.",
               fails="Nothing washed, stock unchanged, or the box washes with its setting off."),
}


def status(ok):
    return "UNMEASURED" if ok is None else ("MATCHES" if ok else "DIFFERS")


def kv(line):
    return dict(p.split("=", 1) for p in str(line).split() if "=" in p)


# ---------------------------------------------------------------- helpers (pure where possible)
def displacement(a, b):
    if a is None or b is None:
        return None
    return abs(b[0] - a[0]) + abs(b[1] - a[1])


def nearest_moving(terr, size, away_from=(), min_d=4, margin=14, kind=None):
    """The Moving-water cell nearest the map centre (and >= min_d, Chebyshev, from every cell in away_from), or None."""
    w, h = size
    best = None
    for (x, z), t in terr.items():
        if not C.is_moving(t) or (kind and t != kind) or not (margin <= x < w - margin and margin <= z < h - margin):
            continue
        if any(max(abs(x - a[0]), abs(z - a[1])) < min_d for a in away_from):
            continue
        d = ((x - w / 2.0) ** 2 + (z - h / 2.0) ** 2, x, z)
        if best is None or d < best:
            best = d
    return None if best is None else (best[1], best[2])


def shallow_pair(terr, size, margin=14):
    """(cell, rot) of a 1x2 sluice box: two WaterMovingShallow cells in a line, nearest the map centre; None if none."""
    w, h = size
    best = None
    for (x, z), t in terr.items():
        if t != "WaterMovingShallow" or not (margin <= x < w - margin and margin <= z < h - margin):
            continue
        for r, (dx, dz) in ((0, (0, 1)), (1, (1, 0))):
            if terr.get((x + dx, z + dz)) == "WaterMovingShallow":
                d = ((x - w / 2.0) ** 2 + (z - h / 2.0) ** 2, x, z, r)
                if best is None or d < best:
                    best = d
    return None if best is None else ((best[1], best[2]), best[3])


def _num(pid):
    """A pawn id as the HoseProbe reports it. LIVE 2026-10-17: jawa/spawn_pawn answers "Human54153" while the HoseProbe's
    colonists list says 54153, so a plain == never matched (R1/R2 read every position as None, R3 saw nobody come home)."""
    d = "".join(ch for ch in str(pid) if ch.isdigit())
    return int(d) if d else pid


def pawn_pos(w, pid):
    for c in w.hp("colonists").get("pawns") or []:
        if _num(c.get("id")) == _num(pid):
            return C.thing_cell(c)
    return None


def stage_colonist(w, cell):
    r = w.call("jawa/spawn_pawn", kindDef="Colonist", x=cell[0], z=cell[1], faction="player", count=1) or {}
    pid = ((r.get("pawns") or [{}])[0] or {}).get("id")
    if pid:
        w.call("jawa/set_draft", pawnId=pid, drafted=True)
    return pid


def vanish(w, ids):
    for pid in ids:
        w.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")


@contextlib.contextmanager
def bruise_declared(ids):
    """The river bruises the pawn it carries by design (owner card 2): declared to the clock gate, never switched off."""
    try:
        import clockgate
        import testenv_guards as TG
        cm = clockgate.expected_disturbance("river bruise on staged throwaways (FlowWorks hazard, owner card 2)", TG.expected_hurt(ids, "Bruise"))
    except Exception:  # noqa: BLE001 - offline / no modcheck: nothing to declare to
        cm = contextlib.nullcontext()
    with cm:
        yield


def row(w, sid, eid, ok, text):
    w.say("  %-7s %-10s %s" % (eid, status(ok), text))
    w.rows.append(dict(id=eid, scene=sid, status=status(ok), game=text))
    return (status(ok), "%s: %s" % (eid, text))


def proof(w, typ, method, arg="-"):
    r = w.call("jawa/static_call", type=typ, method=method, args=arg or "-") or {}
    txt = str(r.get("result") or r.get("message") or r.get("error") or "")
    return (r.get("success") is not False and not txt.startswith(("REFUSED", "UNMEASURED"))), txt


def view_rect(cells, size, w_=44, h_=26):
    return C.centroid_rect(cells, w_, h_, size)


def moving_near(terr, c, r=14):
    return [k for k, t in terr.items() if C.is_moving(t) and abs(k[0] - c[0]) <= r and abs(k[1] - c[1]) <= r]


def shot(w, shots, sid, tag, moment, rect):
    png = C.snap(w, "%s_%s" % (sid, tag), rect)
    w.say("         screenshot: %s" % (png or "none"))
    if png:
        shots.append((png, tag, moment))


# ---------------------------------------------------------------- scenes
def scene_R1(w, env):
    size, terr = env["size"], env["terr"]
    shots, rd = [], []
    cell = nearest_moving(terr, size)
    if not cell:
        return shots, [row(w, "R1", "R1.a", None, "no moving water on the map")]
    rect = view_rect(moving_near(terr, cell), size)
    ok, g = proof(w, PROOF, "ProofGrid")
    k = kv(g)
    cur, fast, edge = int(k.get("current", 0) or 0), int(k.get("fast", 0) or 0), int(k.get("edge", 0) or 0)
    rd.append(row(w, "R1", "R1.a", (cur > 0 and fast + edge > 0) if ok else None,
                  "mod grid: current=%d fast=%d edge=%d%s" % (cur, fast, edge, "" if ok else " (proof refused: %s)" % g[:100])))
    pid = stage_colonist(w, cell)
    if not pid:
        rd.append(row(w, "R1", "R1.b", None, "no throwaway colonist spawned at %s" % (cell,)))
        return shots, rd
    try:
        w.say("  colonist %s staged at %s in %s" % (pid, cell, terr.get(cell)))
        p0 = pawn_pos(w, pid)
        shot(w, shots, "R1", "p00", "Step 0: the colonist has just been placed in the water", rect)
        trail = [p0]
        with bruise_declared([pid]):
            for step in range(1, WATCH_STEPS + 1):
                w.ticks(STEP_TICKS)
                trail.append(pawn_pos(w, pid))
                w.say("  step %d (+%d ticks): colonist at %s" % (step, STEP_TICKS, trail[-1]))
                time.sleep(w.args.pace)
        shot(w, shots, "R1", "p%02d" % WATCH_STEPS, "Step %d: where the current has carried the colonist" % WATCH_STEPS, rect)
        d = displacement(p0, trail[-1])
        rd.append(row(w, "R1", "R1.b", None if d is None else d >= 3, "moved %s squares: %s" % (d, trail)))
        ok2, s = proof(w, PROOF, "ProofShove", "fast;3")
        rd.append(row(w, "R1", "R1.c", (s.startswith("MOVED") and int(s.split()[1]) >= 3) if ok2 else None, "fast-lane shove test: %s" % s[:100]))
    finally:
        vanish(w, [pid])
    return shots, rd


def scene_R2(w, env):
    size, terr = env["size"], env["terr"]
    from objects_sheet import ford_line, FORD
    shots, rd = [], []
    line = ford_line(terr, size)
    if not line:
        return shots, [row(w, "R2", "R2.a", None, "no straight 4-cell run of WaterMovingShallow on this river to lay a ford on")]
    w.call("jawa/set_terrain_batch", ops=";".join("%s:%d,%d,1,1" % (FORD, c[0], c[1]) for c in line))
    after = C.read_terrain(w, size)
    got = [(after or {}).get(c) for c in line]
    rd.append(row(w, "R2", "R2.a", None if after is None else all(g == FORD for g in got), "ford stones read back at %s: %s" % (line, got)))
    mid_c = line[len(line) // 2]
    ctrl_c = nearest_moving(after or terr, size, away_from=line, min_d=5)
    rect = view_rect(line + ([ctrl_c] if ctrl_c else []), size, 34, 20)
    a = stage_colonist(w, mid_c)
    b = stage_colonist(w, ctrl_c) if ctrl_c else None
    try:
        a0, b0 = pawn_pos(w, a), pawn_pos(w, b) if b else None
        w.say("  ford colonist %s on %s; control %s at %s" % (a, mid_c, b, ctrl_c))
        shot(w, shots, "R2", "p00", "Step 0: one colonist on the stones, a control colonist in open shallows", rect)
        with bruise_declared([x for x in (a, b) if x]):
            for step in range(1, WATCH_STEPS + 1):
                w.ticks(STEP_TICKS)
                w.say("  step %d: ford colonist %s, control %s" % (step, pawn_pos(w, a), pawn_pos(w, b) if b else None))
                time.sleep(w.args.pace)
        shot(w, shots, "R2", "p%02d" % WATCH_STEPS, "Step %d: the ford colonist should be where it started" % WATCH_STEPS, rect)
        da, db = displacement(a0, pawn_pos(w, a)), (displacement(b0, pawn_pos(w, b)) if b else None)
        rd.append(row(w, "R2", "R2.b", None if (da is None or db is None or db < 1) else (da == 0),   # an unread ford colonist is UNMEASURED, not "moved"
                      
                      "ford colonist moved %s; control moved %s%s" % (da, db, "" if (db or 0) >= 1 else " (control did not drift: the current is not shown running, so the ford reading is UNMEASURED)")))
        ok2, s = proof(w, PROOF, "ProofShove", "ford;3")
        rd.append(row(w, "R2", "R2.c", s.startswith("MOVED 0") if ok2 else None, "ford shove test: %s" % s[:100]))
    finally:
        vanish(w, [x for x in (a, b) if x])
    return shots, rd


def scene_R3(w, env):
    import extensions_rivers as RIV
    size, terr = env["size"], env["terr"]
    shots, rd = [], []
    edges = RIV.moving_edges(terr, size)
    if len(edges) < RIV.MIN_RIVER_EDGES:
        return shots, [row(w, "R3", "R3.a", None, "SITE: no downstream edge: moving water reaches only %s (run river_site.py)" % (edges,))]
    cells = RIV.edge_river_cells(terr, size, cap=6)
    if not cells:
        return shots, [row(w, "R3", "R3.a", None, "no moving river water on any map edge")]
    ok, before = proof(w, PROOF, "ProofSwept", "read")
    p0 = int(kv(before).get("pending", -1)) if ok else -1
    if p0 < 0:
        return shots, [row(w, "R3", "R3.a", None, "the swept book gave no pending count: %s" % before[:100])]
    staged = []
    try:
        for c in cells:
            pid = stage_colonist(w, c)
            if pid:
                staged.append(pid)
        if not staged:
            return shots, [row(w, "R3", "R3.a", None, "no colonist spawned on the %d edge river cells" % len(cells))]
        fac0 = {}
        for i in staged:
            pg = ((w.call("jawa/pawn_get", pawn=i) or {}).get("pawns") or [{}])[0]
            fac0[i] = pg.get("faction")
        w.say("  staged factions (game read): %s" % fac0)
        rect = view_rect(cells[:2], size, 40, 26)
        w.say("  %d colonists staged on edge river cells %s; pending %d" % (len(staged), cells, p0))
        shot(w, shots, "R3", "p00", "Start: colonists standing in the moving water at the map edge", rect)
        waited, now, reads_ok = 0, p0, 0   # reads_ok: if every follow-up book read was refused, R3.a is UNMEASURED, not "nobody swept"
        with bruise_declared(staged):
            while waited < SWEPT_MAX and now <= p0:
                w.ticks(SWEPT_CHUNK)
                waited += SWEPT_CHUNK
                ok, txt = proof(w, PROOF, "ProofSwept", "read")
                now = int(kv(txt).get("pending", now)) if ok else now
                reads_ok += 1 if ok else 0
                w.say("  after %d ticks: pending %d, still on map: %d of %d" % (waited, now, len([1 for c in (w.hp("colonists").get("pawns") or []) if _num(c.get("id")) in {_num(i) for i in staged}]), len(staged)))
                time.sleep(w.args.pace)
        shot(w, shots, "R3", "swept", "After %d ticks: whoever the current carried off the edge is gone" % waited, rect)
        rd.append(row(w, "R3", "R3.a", (now > p0) if reads_ok else None, "pending %d -> %d after %d ticks (%d colonists staged)" % (p0, now, waited, len(staged))))
        roster = w.hp("colonists").get("pawns") or []
        gone = {i for i in staged if _num(i) not in {_num(c.get("id")) for c in roster}}
        if not roster:
            gone = None   # the roster read came back empty: cannot tell "washed away" from "unread"
        ok, ret = proof(w, PROOF, "ProofSwept", "return")
        rd.append(row(w, "R3", "R3.b", ret.startswith("SWEPT pending=0") if ok else None, "walk-home call: %s" % ret[:100]))
        back = {i for i in (gone or ()) if _num(i) in {_num(c.get("id")) for c in (w.hp("colonists").get("pawns") or [])}}
        # LIVE 2026-10-17: the HoseProbe lists only THIS map's colonists; a returned pawn may walk home to another loaded map.
        # Ask the game where each washed-away pawn is now (jawa/pawn_get searches every map and the world).
        for i in sorted(gone or ()):
            pg = ((w.call("jawa/pawn_get", pawn=i) or {}).get("pawns") or [{}])[0]
            w.say("  after return, %s: faction %s (staged as %s), position %s" % (i, pg.get("faction"), fac0.get(i), pg.get("position")))
        rd.append(row(w, "R3", "R3.c", None if not gone else bool(back), "washed away %s; back on the map after return: %s" % (sorted(gone or ()), sorted(back))))
        shot(w, shots, "R3", "home", "After the walk home: the washed-away colonists are back", rect)
        rd.append(row(w, "R3", "R3.d", None, "the 'Swept away' / 'Back from the river' letters are not read by this walk (the river suite's swept chain reads them)"))
    finally:
        vanish(w, staged)
    return shots, rd


def scene_R4(w, env):
    size, terr = env["size"], env["terr"]
    shots, rd = [], []
    ok, s = proof(w, WORKS, "ProofWeirPlace")
    k = kv(s)
    rd.append(row(w, "R4", "R4.a", (k.get("edge") == "True" and k.get("dry") == "False" and k.get("wet") == "False") if ok else None, "place test: %s" % s[:100]))
    ok, s = proof(w, WORKS, "ProofWeirPool")
    k = kv(s)
    rd.append(row(w, "R4", "R4.b", (k.get("arrestedWet") == "True" and int(k.get("dropped", 0) or 0) > 0) if ok else None, "pool test: %s" % s[:110]))
    ok, s = proof(w, WORKS, "ProofWeirJoin")
    k = kv(s)
    if not ok:
        rd.append(row(w, "R4", "R4.c", None, "join test: %s" % s[:110]))
    elif int(k.get("poolSingle", 0) or 0) <= 0:
        rd.append(row(w, "R4", "R4.c", None, "the first weir pooled nothing, so joining cannot be compared: %s" % s[:100]))
    else:
        rd.append(row(w, "R4", "R4.c", (k.get("placeOk") == "True" and k.get("run") == "2" and k.get("headIsBank") == "True" and k.get("joint") == "True"
                                         and int(k.get("poolJoined", 0)) >= int(k.get("poolSingle", 0)) and int(k.get("poolGap", -1)) == 0), "join test: %s" % s[:130]))
    picks = C.spread(C.bank_cells(terr, size), 1)
    if not picks:
        rd.append(row(w, "R4", "R4.d", None, "no bank-edge cell to place a visible weir on"))
        return shots, rd
    (c, r) = picks[0]
    rect = view_rect([c], size, 36, 22)
    shot(w, shots, "R4", "before", "Before: the bank, no weir", rect)
    res = C.place(w, "RM_BankWeir", c, rot=r)
    w.ticks(250)
    w.ticks(250)
    rd.append(row(w, "R4", "R4.d", None if (not res["survived"] or res["rot_read"] is None) else res["rot_read"] == r,
                  "weir at %s: asked %s, game reads %s%s" % (c, C.rot_text(r), C.rot_text(res["rot_read"]), "; " + res["note"] if res["note"] else "")))
    shot(w, shots, "R4", "after", "After 2 pulses: the weir on the bank edge; look at the water behind it", rect)
    w.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (c[0] - 1, c[1] - 1, 3, 4), categories="Building")
    w.say("  weir removed again (destroy_batch around %s)" % (c,))
    return shots, rd


def scene_R5(w, env):
    size, terr = env["size"], env["terr"]
    shots, rd = [], []
    ok, s = proof(w, PLACER, "ProofReport", "selfcheck")
    k = kv(s)
    if not ok:
        rd.append(row(w, "R5", "R5.a", None, "placer proof: %s" % s[:110]))
    elif int(k.get("poolCount", 0) or 0) <= 0:
        rd.append(row(w, "R5", "R5.a", None, "the site's rock holds no placer mineral, so its river carries nothing: %s" % s[:100]))
    else:
        good = (int(k.get("got", 0) or 0) > 0 and k.get("drawMatches") == "True" and k.get("inPool") == "True")
        rd.append(row(w, "R5", "R5.a", good, "wash: %s" % s[:130]))
        rd.append(row(w, "R5", "R5.b", k.get("off") == "sluice=off", "setting off: off=%s" % k.get("off")))
    sp = shallow_pair(terr, size)
    if not sp:
        rd.append(row(w, "R5", "R5.c", None, "no 2-cell run of shallow moving water for a sluice box"))
        return shots, rd
    c, r = sp
    rect = view_rect([c], size, 34, 20)
    shot(w, shots, "R5", "before", "Before: the shallows", rect)
    res = C.place(w, "RM_SluiceBox", c, rot=r)
    w.ticks(250)
    rd.append(row(w, "R5", "R5.c", None if (not res["survived"] or res["rot_read"] is None) else res["rot_read"] == r,
                  "sluice box at %s: asked %s, game reads %s%s" % (c, C.rot_text(r), C.rot_text(res["rot_read"]), "; " + res["note"] if res["note"] else "")))
    shot(w, shots, "R5", "after", "After: the sluice box standing in the shallows", rect)
    w.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (c[0] - 1, c[1] - 1, 3, 4), categories="Building")
    return shots, rd


RUN = {"R1": scene_R1, "R2": scene_R2, "R3": scene_R3, "R4": scene_R4, "R5": scene_R5}


# ---------------------------------------------------------------- caption panels
def panel(src, dst, sid, moment, readings):
    """Screenshot + a 1000 px caption panel to its right, same layout as annotate_water_scenes.py."""
    from PIL import Image, ImageDraw
    sc = SCENES[sid]
    im = Image.open(src).convert("RGB")
    W, PW, pad = 1600, 1000, 30
    im = im.resize((W, max(1, round(im.height * W / im.width))), Image.LANCZOS)
    fh, fb, ft = C._font(34, True), C._font(25), C._font(25, True)
    blocks = [("t", sc["title"]), ("m", moment), ("h", "WHAT YOU ARE LOOKING AT"), ("p", sc["legend"]), ("h", "WHAT TO CHECK")]
    blocks += [("p", "- " + c) for c in sc["check"]]
    blocks += [("h", "PASS IF"), ("p", sc["passif"]), ("h", "FAILS IF"), ("p", sc["fails"]), ("h", "WHAT THE GAME MEASURED")]
    blocks += [("p", "- %s %s" % (s, t)) for s, t in readings] or [("p", "- (nothing measured)")]
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lay, y = [], pad
    for k, t in blocks:
        f = {"t": fh, "h": ft}.get(k, fb)
        ls = C._wrap(tmp, t, f, PW - 2 * pad)
        if k == "h":
            y += 14
        lay.append((k, ls, f, y))
        y += (f.size + 8) * len(ls) + (4 if k != "h" else 2)
    cv = Image.new("RGB", (W + PW, max(im.height, y + pad)), (250, 247, 240))
    cv.paste(im, (0, 0))
    d = ImageDraw.Draw(cv)
    col = {"t": (30, 30, 30), "m": (0, 70, 140), "h": (90, 60, 20), "p": (25, 25, 25)}
    for k, ls, f, y0 in lay:
        for i, l in enumerate(ls):
            d.text((W + pad, y0 + i * (f.size + 8)), l, font=f, fill=col[k])
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    cv.save(dst)
    return dst


# ---------------------------------------------------------------- orchestration
def prep_site(w, a):
    """Make the current map a river site: river_site.py (its own bridge session), exit 0 = ready."""
    if a.mock:
        w.say("river_site.py skipped (--mock)")
        return True
    w.call("rimworld/pause_game", pause=True)
    w.say("founding a river site (river_site.py; a few minutes) ...")
    exe = "python.exe" if os.name == "posix" and os.path.exists("/mnt/c") else sys.executable
    rc = subprocess.call([exe, os.path.join(NORTHSTAR, "river_site.py")], timeout=1500)
    w.say("river_site.py exit %s (0 = ready; 2 = no tile qualified; 3 = site problems printed above)" % rc)
    return rc == 0


def env_for(w):
    size = C.map_size(w)
    terr = C.read_terrain(w, size)
    if not terr:
        return None, "terrain unreadable"
    if not any(C.is_moving(t) for t in terr.values()):
        return None, "this map has no moving river water (use --prep or run river_site.py first)"
    return dict(size=size, terr=terr), None


def do_scene(w, sid, env, out_dir, a):
    w.say("=" * 100)
    w.say(SCENES[sid]["title"])
    w.rows, w.log_lines = [], w.log_lines
    shots, rd, panels = [], [], []
    try:
        if getattr(a, "mock_fail", None) == sid:
            raise RuntimeError("injected by --mock-fail %s" % sid)
        shots, rd = RUN[sid](w, env)
    except Exception:  # noqa: BLE001 - print it, keep it, go on
        tbp, last = C.keep_traceback(w, out_dir, sid)
        rd = list(rd) + [("CRASHED", "%s.crash: %s" % (sid, last))]
        w.rows.append(dict(id=sid + ".crash", scene=sid, status="CRASHED", game=last, traceback=tbp))
    for png, tag, moment in shots:
        dst = os.path.join(out_dir, "%s_%s_panel.png" % (sid, tag))
        try:
            panel(png, dst, sid, moment, rd)
            panels.append((os.path.basename(dst), moment))
        except Exception:  # noqa: BLE001
            C.keep_traceback(w, out_dir, sid + "_panel")
    with open(os.path.join(out_dir, "%s_rows.json" % sid), "w", encoding="utf-8") as f:
        json.dump(w.rows, f, indent=1)
    sc = SCENES[sid]
    return dict(id=sid, title=sc["title"], looking_at=sc["legend"], check=sc["check"], passif=sc["passif"], fails=sc["fails"],
                images=panels, readings=rd)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["prep", "go", "all"])
    ap.add_argument("scene", nargs="?")
    ap.add_argument("--prep", action="store_true", help="all/go: found a river site first (river_site.py)")
    ap.add_argument("--pace", type=float, default=1.0, help="wall seconds between clock steps")
    ap.add_argument("--no-shots", action="store_true")
    ap.add_argument("--mock", action="store_true", help="offline fake game; proves this script's own paths only")
    ap.add_argument("--mock-fail", default=None, help="with --mock: raise inside this scene id to prove a crash is kept and the walk goes on")
    ap.add_argument("--fresh-map", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--reset-index", action="store_true", help="start index.html afresh (default: it accumulates every scene run)")
    a = ap.parse_args(argv)
    if a.mock:
        a.pace = 0.0
    out_dir = OUT_MOCK if a.mock else OUT_LIVE
    mf = a.mock_fail
    w = C.make_walk(a, out_dir)
    a.mock_fail = mf
    rc = 0
    try:
        if not a.mock:
            st = (w.call("rimworld/get_ui_state") or {}).get("programState")
            if st != "Playing":
                w.say("No Playing game (state %s): start a quicktest map, then rerun with --prep." % st)
                return 2
            w.call("rimworld/pause_game", pause=True)
            w.call("rimworld/set_god_mode", enabled=True)
        if a.verb == "prep" or a.prep:
            if not prep_site(w, a):
                return 3 if a.verb == "prep" else 3
            if a.verb == "prep":
                return 0
        env, why = env_for(w)
        if not env:
            w.say("NOT A RIVER SITE: %s" % why)
            return 2
        sids = ORDER if a.verb == "all" else [(a.scene or "").upper()]
        if any(s not in RUN for s in sids):
            ap.error("scene must be one of %s" % ORDER)
        groups = []
        for sid in sids:
            groups.append(do_scene(w, sid, env, out_dir, a))
            if any(s == "CRASHED" for s, _ in groups[-1]["readings"]):
                rc = 1
        idx = C.write_index(os.path.join(out_dir, "index.html"), "FlowWorks river scenes: what to evaluate",
                            "Each scene has caption panels (what you look at, what to check, pass/fail, what the game measured). "
                            "Tick your answer under each scene; 'Copy my answers as JSON' puts them on the clipboard. Every scene you have run stays on the "
                            "page; the newest run of a scene replaces its older one.", groups, accumulate=not a.reset_index)
        with open(os.path.join(out_dir, "log_%s.txt" % time.strftime("%Y%m%dT%H%M%S")), "w", encoding="utf-8") as f:
            f.write("\n".join(w.log_lines) + "\n")
        w.say("index: %s" % idx)
    except Exception:  # noqa: BLE001 - the harness itself: never a bare 'Traceback' line
        C.keep_traceback(w, out_dir, "walk")
        rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
