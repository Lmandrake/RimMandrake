"""CLIMB live proof (PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP; design/RimMandrake/relative_depth_climb_design_2026-10-12.md
§8.6, the debug_process rule: the proof script is written with the build item and grows with each later item).

  python.exe src/RimMandrake/FlowWorks/northstar/climb_proof.py [out.json] [--origin X,Z] [--fresh-map]

Run from the repo root with python.exe; the bridge must be held. Exit 0 = every MEASURED row PASS (owed rows are UNMEASURED
and say why). NEVER RUN BY THE BUILD ITEM ITSELF: written offline 2026-10-13 while a live driver held the game.

Owner rulings this proves (2026-10-12, verbatim, design §10):
  Q1 "it should be relative height (the depth of the pit relative to its N, S, E, W, neighbors) so that gradual slopes
     never trap anyone."  ·  "Even a 2-deep trench could trap rat-sized creatures"
  Q2 "Human-sized pawns should climb two at a time (slow) or one a time (faster). Three or more traps."
  and the pond sentence: "Natural ponds and lakes when pumped dry would leave just such gradual terrain so no chance to
  fall in and get stuck."

Scenes (plot coords from --origin, default 120,120; 46 x 12 (SITE_W, SITE_H), cleared + read back by validation_core.prepare_site):
  A  dried-pond stand-in at (2..6, 2..6): a D 2 5x5 ring with a D 4 3x3 core (dug; a real drained pond reads the same once
     POND_BED step 2 routes the bed depth through RM_MapComponent_Excavation.ClimbDepthAt).
  B  sheer D 3 3x3 at (10..12, 2..4).
  C  sheer D 2 1x1 at (16, 3).
  D  sheer D 4 3x3 at (20..22, 2..4) with a lowered RM_Ladder at (20, 3) on its west wall.
Pawns: a Colonist with superdeepCapturesOwnFaction ON for the run (restored after; so the hole captures it like an enemy),
a wild Muffalo (body 2.4, K 3), a wild Rat (K 1). Every read is jawa/static_call RM_NorthstarProofs.ProofClimb:
  "CLIMB k=K held=b trapped=b cell=x,z | POCKET k=K comp=N pocket=b size=N depth=D gen=N built=N rebuilds=N".
No flyer, no flight check (standing rule).

Rows (MEASURED now): CLIMB_pond_person_free, CLIMB_pond_person_walks_out, CLIMB_D3_person_trapped,
CLIMB_D3_person_cannot_walk_out, CLIMB_D3_muffalo_free, CLIMB_D2_rat_trapped, CLIMB_ladder_prison_door,
CLIMB_rebuild_follows_fill, CLIMB_ramp_frees_and_retraps + CLIMB_ramp_walk_out (pit E: sheer D 4 3x3 at
(24..26, 2..4), a D 1 shelf at (27, 3), a ramp on (26, 3) pointing east, built and removed by ProofRamp),
CLIMB_mask_seals_cliff_edge (PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS: the person band's
connectivity byte on pit B's west lip has no east bit, the muffalo band's has), CLIMB_step_cost_slow_at_K (the same item's
step cost: ProofClimb "cost:" prices surface -> D 2 ring slow, ring -> ring 0, surface -> pit E's D 1 shelf one climb),
CLIMB_raider_never_crosses_ramped_moat (F: a 3x3 surface island at (31..33, 4..6) ringed by a sheer D 4 moat (30..34, 3..7),
ramped OUT on its east side: a ramp on (34, 5) pointing east to a D 1 shelf at (35, 5); one hostile Pirate on the island and
one on the moat floor at (30, 3), read through jawa/flowworks_pit_report's canReachMapEdge (the game's own
Reachability.CanReachMapEdge through RM_Patch_Reachability_SuperdeepMapEdge) and three ProofClimb band-2 components;
moat_verdict), CLIMB_hauler_fetches_ramped_floor (G: a sheer D 4 3x3 at (38..40, 2..4), a D 1 shelf at (41, 3); 10 Jade on
the floor's middle (39, 3), two squares from every lip; a Colonist with ONLY Hauling (priority 1, every other vanilla work
type 0) and a Jade-only 2x2 stockpile at (43, 8) left to its own AI: first 600 ticks with NO ramp (the floor must keep the
Jade), then a ramp on (40, 3) pointing east and up to 3000 ticks until the Jade lies in the stockpile; haul_verdict).
Site 46 x 12 (x 0..45).  OWED (always UNMEASURED, see OWED below): CLIMB_save_reload_pockets_identical (live_session B7).

ANTI-GUESSING NOTES
- The pocket grid rebuilds from the map tick at most once per 60 ticks after a depth write; every scene is dug, then the
  game is ticked 70 before any read, and each read records gen/built so a stale grid reads UNMEASURED, never FAIL/PASS.
- held/trapped are the mod's own predicate (RM_SuperdeepTrap.IsHeld / IsTrapped); a walk-out row is the pawn's POSITION after
  a drafted jawa/order_pawn, read from the order's own pawn row, with ticksElapsed > 0 or it is UNMEASURED.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

PROOF_TYPE = "RimMandrake.FlowWorks.RM_NorthstarProofs"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
SETTLE = 70          # > RM_PocketGrid.RebuildMinTicks
WAIT_OUT = 900

SITE_W, SITE_H = 46, 12
HAUL_SEALED_TICKS = 600
HAUL_BUDGET = 3000
HAUL_ITEM = "Jade"        # vanilla resource ThingDef: a Jade-only stockpile is never fed by anything else on the map
# vanilla WorkTypeDefs (Core + DLC; a missing or disabled one is refused by set_work_priority and simply skipped)
OTHER_WORK = ("Firefighter", "Patient", "Doctor", "PatientBedRest", "Childcare", "BasicWorker", "Warden", "Handling",
              "Cooking", "Hunting", "Construction", "Growing", "Mining", "PlantCutting", "Smithing", "Tailoring", "Art",
              "Crafting", "Cleaning", "Research", "DarkStudy")

OWED = {
    "CLIMB_save_reload_pockets_identical": "covered by live_session.py B7 (one save + one load; pockets compared, "
                                           "RELOAD_POCKETS_DIAGNOSE_KEPT_NO_RECEIPTS); the grid is derived, never scribed",
}


# ============================================================================ verdicts (pure; selftest_climb_proof.py)
def parse(txt):
    """ProofClimb's line -> dict (the CLIMB half and the POCKET half; same-named keys agree)."""
    kv = {}
    for tok in (txt or "").replace("|", " ").split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return kv


def fresh(kv):
    """The grid answered for the current generation (a stale grid is no evidence either way)."""
    return kv.get("gen") is not None and kv.get("gen") == kv.get("built")


def state_verdict(kv, want_held=None, want_trapped=None, want_pocket=None):
    if not kv or "held" not in kv:
        return "UNMEASURED", {"why": "ProofClimb gave no pawn line", "kv": kv}
    if not fresh(kv):
        return "UNMEASURED", {"why": "pocket grid stale (gen != built)", "kv": kv}
    got = {"held": kv.get("held") == "True", "trapped": kv.get("trapped") == "True", "pocket": kv.get("pocket") == "True"}
    want = {"held": want_held, "trapped": want_trapped, "pocket": want_pocket}
    bad = {k: (got[k], w) for k, w in want.items() if w is not None and got[k] != w}
    return ("FAIL" if bad else "PASS"), {"kv": kv, "mismatch": bad}


def mask_verdict(person, big):
    """CLIMB_mask_seals_cliff_edge from two ProofClimb mask reads -> status. East is bit 0x04 (Verse.CellConnection)."""
    try:
        bp, bb = int(person["bits"], 16), int(big["bits"], 16)
        van = int(person["vanilla"], 16)
    except (KeyError, ValueError, TypeError):
        return "UNMEASURED"
    if person.get("derived") != "True" or not van & 0x04:
        return "UNMEASURED"   # masks not derived yet, or vanilla itself has no east step there (a wall, the map edge)
    return "PASS" if (not bp & 0x04) and (bb & 0x04) else "FAIL"


def ramp_verdict(before, with_ramp, removed):
    """CLIMB_ramp_frees_and_retraps from three ProofClimb reads of one pit cell (person band): a pocket, then not, then again."""
    reads = (before, with_ramp, removed)
    if not all(r and fresh(r) and "pocket" in r for r in reads):
        return "UNMEASURED"
    want = ("True", "False", "True")
    return "PASS" if tuple(r["pocket"] for r in reads) == want else "FAIL"


def cost_verdict(slow, flat, normal):
    """CLIMB_step_cost_slow_at_K from three ProofClimb cost: reads by one person (K 2), design §8.2 / RM_PitTrapMath.StepCost:
    a step of exactly K costs climb x "Slow climb factor", a step along equal depth 0, a step under K one plain climb.
    UNMEASURED unless all three answered with the masks on (the StepCost route is the masked one)."""
    try:
        reads = [(int(r["cost"]), int(r["climb"]), float(r["factor"]), int(r["k"]), r["mask"]) for r in (slow, flat, normal)]
    except (KeyError, ValueError, TypeError):
        return "UNMEASURED"
    if any(m != "True" for *_x, m in reads) or reads[0][3] != 2:
        return "UNMEASURED"
    (sc, scl, f, _k, _m), (fc, _a, _b, _c, _d), (nc, ncl, _e, _g, _h) = reads
    return "PASS" if sc == int(round(scl * f)) and fc == 0 and nc == ncl and sc > nc else "FAIL"


def pit_pawn(report, pid):
    """The pawns[] row of jawa/flowworks_pit_report for pawn pid (ids compared without the Thing_ prefix), or None."""
    want = str(pid or "").replace("Thing_", "")
    for p in (report or {}).get("pawns") or []:
        if str(p.get("id") or "").replace("Thing_", "") == want:
            return p
    return None


def moat_verdict(island, moat, k_island, k_moat, k_out):
    """CLIMB_raider_never_crosses_ramped_moat (design §8.6) -> (status, why). island / moat = the pit_report pawn rows
    of a hostile on the moated island and one on the ramped moat floor; k_* = ProofClimb band-2 reads (island, moat,
    outer surface). The control first: the moat raider must reach the map edge up the ramp (else the instrument never
    said True and the island's False proves nothing: UNMEASURED). Then PASS = the island raider cannot reach the edge
    and the island is its own band component while moat and outside are one; FAIL = it can, or the grid joins it."""
    for name, r in (("island", island), ("moat", moat)):
        if not r or r.get("spawned") is not True or r.get("dead") or r.get("downed"):
            return "UNMEASURED", "%s raider not read (or dead/downed): %r" % (name, r)
    if moat.get("canReachMapEdge") is not True:
        return "UNMEASURED", "control: the moat-floor raider cannot reach the edge up the ramp (see CLIMB_ramp_* rows)"
    if island.get("canReachMapEdge") is True:
        return "FAIL", "the island raider reaches the map edge across the moat"
    reads = (k_island, k_moat, k_out)
    if not all(r and fresh(r) and "comp" in r for r in reads):
        return "UNMEASURED", "a stale or missing pocket-grid read"
    if k_island["comp"] == k_out["comp"]:
        return "FAIL", "the grid puts the island in the outside's component"
    if k_moat["comp"] != k_out["comp"]:
        return "UNMEASURED", "control: the grid does not join the ramped moat to the outside"
    return "PASS", ""


def in_rect(rect, xz):
    return not out_of(rect, xz)


def haul_verdict(sealed_items, final_items, pit_rect, pile_rect):
    """CLIMB_hauler_fetches_ramped_floor -> (status, why). *_items = jawa/list_things rows of the Jade (def/x/z/spawned).
    sealed_items: read after HAUL_SEALED_TICKS with NO ramp; final_items: after the ramp, at the end of the poll.
    UNMEASURED when the Jade was never seen on the pit floor; FAIL when it left a sheer D 4 floor with no ramp (the
    hauler got in where nobody can) or never reached the stockpile once the ramp stood; PASS = sealed, then fetched."""
    if not sealed_items:
        return "UNMEASURED", "the Jade was not read back after the sealed phase"
    if not any(in_rect(pit_rect, (t.get("x"), t.get("z"))) for t in sealed_items):
        return "FAIL", "the Jade left a sheer D 4 floor with no ramp"
    if any(in_rect(pile_rect, (t.get("x"), t.get("z"))) for t in final_items or []):
        return "PASS", ""
    return "FAIL", "the Jade never reached the stockpile with the ramp built"


def out_of(rect, xz):
    x0, z0, w, h = rect
    return not (x0 <= xz[0] < x0 + w and z0 <= xz[1] < z0 + h)


def dig_misses(digs):
    """[(cell, wanted, why)] for every excavation_drive whose reply does not say the cell now sits at the wanted depth.
    Deepen ADDS (LAW 1: depth only goes down), so a cell an earlier run dug and nobody reset reads deeper than asked; a
    refused drive leaves it shallow. Either way every row on that scene would judge the wrong pit: the run stops
    UNMEASURED/SITE instead of scoring a "free" row PASS on ground that was never dug."""
    bad = []
    for cell, want, r in digs:
        if not isinstance(r, dict) or r.get("success") is not True:
            bad.append((cell, want, "refused: %s" % str((r or {}).get("error") or r)[:80]))
        elif "depth" in r and r.get("depth") != want:
            bad.append((cell, want, "depth %s" % r.get("depth")))
    return bad


def reset_left(txt):
    """ProofResetRect's 'RESET cells=n levels=n rolled=n left=n' -> left (None when unread or refused)."""
    kv = parse(txt)
    try:
        return int(kv["left"]) if str(txt).startswith("RESET") else None
    except (KeyError, ValueError):
        return None


def walk_verdict(order_row, rect, want_out):
    """A drafted order to a cell outside rect: PASS when the pawn ends outside (want_out) / inside (not want_out)."""
    if not order_row or order_row.get("orderAccepted") is not True or not (order_row.get("ticksElapsed") or 0) > 0:
        return "UNMEASURED", {"why": "order not accepted or the game never ticked", "order": order_row}
    pos = order_row.get("position") or order_row.get("end") or order_row.get("cell")
    if isinstance(pos, dict):
        pos = (pos.get("x"), pos.get("z"))
    if not pos or pos[0] is None:
        return "UNMEASURED", {"why": "no end position in the order row", "order": order_row}
    ok = out_of(rect, pos) == want_out
    return ("PASS" if ok else "FAIL"), {"end": pos, "rect": rect, "wantOut": want_out}


# ============================================================================ live rows F and G
def _things(B, rect):
    r = B.call("jawa/list_things", defName=HAUL_ITEM, rect="%d,%d,%d,%d" % rect) or {}
    return [t for t in r.get("things") or [] if t.get("def") == HAUL_ITEM]


def haul_rows(B, P, row, spawn, climb, rect_G, rect_pile):
    x0, z0 = P(0, 0)
    site = (x0, z0, SITE_W, SITE_H)
    hauler = spawn("Colonist", P(39, 9), "player")
    prio = {w: (B.call("jawa/set_work_priority", pawnId=hauler, workType=w, priority=0) or {}).get("success")
            for w in OTHER_WORK} if hauler else {}
    hp = (B.call("jawa/set_work_priority", pawnId=hauler, workType="Hauling", priority=1) or {}) if hauler else {}
    zr = B.call("jawa/map_zones", action="createZone", zoneType="stockpile", rect="%d,%d,%d,%d" % rect_pile) or {}
    label = zr.get("created")
    ss = (B.call("jawa/storage_settings", target=label, disallowAll=True, allow=HAUL_ITEM) or {}) if label else {}
    sp = B.call("jawa/spawn_batch", ops="%s:%d,%d,10" % ((HAUL_ITEM,) + P(39, 3))) or {}
    setup = dict(hauler=hauler, hauling=hp.get("success"), zone=label, filter=ss.get("success"),
                 placed=sp.get("thingsPlaced"), othersOff=sum(1 for v in prio.values() if v))
    if not (hauler and hp.get("success") and label and ss.get("success") and sp.get("thingsPlaced")):
        row("CLIMB_hauler_fetches_ramped_floor", "UNMEASURED", "SITE", dict(why="haul scene not staged", **setup))
        return
    trail = []
    B.ticks(HAUL_SEALED_TICKS)
    sealed = _things(B, site)
    kv, _t = climb("pawn:%s" % hauler)
    trail.append(kv.get("cell"))
    tr = B.call("jawa/static_call", type=PROOF_TYPE, method="ProofRamp", args="%d,%d;1" % P(40, 3)) or {}
    final, waited = [], 0
    while waited < HAUL_BUDGET:
        B.ticks(250)
        waited += 250
        kv, _t = climb("pawn:%s" % hauler)
        trail.append(kv.get("cell"))
        final = _things(B, site)
        if any(in_rect(rect_pile, (t.get("x"), t.get("z"))) for t in final):
            break
    st, why = haul_verdict(sealed, final, rect_G, rect_pile)
    if st == "FAIL" and "ramp built" in why and "joins=True" not in str(tr.get("result")):
        st, why = "UNMEASURED", "the ramp did not join (%s): see CLIMB_ramp_* rows" % str(tr.get("result") or tr)[:80]
    row("CLIMB_hauler_fetches_ramped_floor", st, "MOD", dict(why=why, sealed=sealed, final=final, waited=waited,
                                                             ramp=tr, trail=trail[-14:], **setup))
    B.call("jawa/set_draft", pawnId=hauler, drafted=True)


def moat_row(B, P, row, spawn, climb, ramp):
    isl = spawn("Pirate", P(32, 5), "hostile")
    mo = spawn("Pirate", P(30, 3), "hostile")
    try:
        # no ticks: reachability needs none, and a hostile left a few ticks wanders off the cell pit_report reads; each
        # report is taken where ProofClimb says the pawn stands
        def report(pid, c):
            kv, _t = climb("pawn:%s" % pid) if pid else ({}, "")
            try:
                c = tuple(int(v) for v in kv["cell"].split(","))
            except (KeyError, ValueError):
                pass
            return B.call("jawa/flowworks_pit_report", x=c[0], z=c[1]) or {}
        ri = report(isl, P(32, 5))
        rm = report(mo, P(30, 3))
        ki, ti = climb("%d,%d;2" % P(32, 5))
        km, tm = climb("%d,%d;2" % P(30, 3))
        ko, to = climb("%d,%d;2" % P(37, 10))
        st, why = moat_verdict(pit_pawn(ri, isl), pit_pawn(rm, mo), ki, km, ko)
        row("CLIMB_raider_never_crosses_ramped_moat", st, "MOD",
            dict(why=why, island=pit_pawn(ri, isl), moat=pit_pawn(rm, mo), txt=[ti, tm, to], ramp=ramp))
    finally:
        for pid in (isl, mo):
            if pid:
                B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")


# ============================================================================ live run
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="120,120")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH           # noqa: E402  (bridge-side imports only on a live run)
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "climb_proof_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "climb_proof.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "detail": det})
        print("%-40s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def climb(arg):
        r = B.call("jawa/static_call", type=PROOF_TYPE, method="ProofClimb", args=arg) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return parse(txt) if r.get("success") is True and not txt.startswith("REFUSED") else {}, txt

    def sget(f):
        return (B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f) or {}).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))

    digs = []

    def dig(c, n):
        r = B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=-1) or {}
        digs.append((tuple(c), n, r))
        return r

    def spawn(kind, c, faction):
        r = B.call("jawa/spawn_pawn", kindDef=kind, x=c[0], z=c[1], faction=faction, count=1) or {}
        return ((r.get("pawns") or [{}])[0]).get("id")

    def order(pid, c):
        o = B.call("jawa/order_pawn", pawnId=pid, x=c[0], z=c[1], waitTicks=WAIT_OUT, draft=True) or {}
        for p in o.get("pawns") or []:
            if p.get("id") == pid:
                return dict(p, ticksElapsed=o.get("ticksElapsed"))
        return {}

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)                        # noqa: E731
    rect_A, rect_B, rect_C, rect_D = (ox + 2, oz + 2, 5, 5), (ox + 10, oz + 2, 3, 3), (ox + 16, oz + 3, 1, 1), (ox + 20, oz + 2, 3, 3)
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    rect_G, rect_pile = (ox + 38, oz + 2, 3, 3), (ox + 43, oz + 8, 2, 2)
    ok, _ = V._wait_playing(B, leave_s=0)
    # HARNESS (BENCH belt 2026-10-22): d03ca752f4 put this calm BEFORE `ok` was assigned -> UnboundLocalError at start
    if ok:
        res["site_calm"] = V.site_calm(B)   # TESTENV_PREFLIGHT_HARDEN_TRISPIKE_AT_ARM: map-gen hostiles/hives stop safe_advance at arm
    FIELDS = ("superdeepCapturesOwnFaction", "pitRelativeClimbEnabled", "ladderPrisonDoorEnabled")
    before = {f: sget(f) for f in FIELDS}
    res["settings_before"] = before
    try:
        # old digs first: prepare_site paints Soil but never fills a dug cell back in, and Deepen ADDS, so a reused map
        # (live_session B3 runs this without --fresh-map) doubled every depth below
        rr = B.call("jawa/static_call", type=PROOF_TYPE, method="ProofResetRect", args="%d;%d;%d;%d" % (ox, oz, SITE_W, SITE_H)) or {}
        left = reset_left(str(rr.get("result") or "")) if rr.get("success") is True else None
        if not ok or left != 0 or not V.prepare_site(B, (ox, oz, SITE_W, SITE_H), rows, "CLIMB_site_ready"):
            row("CLIMB_site", "UNMEASURED", "SITE", {"why": "site not ready / not playing / old digs not reset",
                                                     "reset": str(rr.get("result") or rr.get("error") or rr)[:160]})
            return 2
        sset("pitRelativeClimbEnabled", True)
        sset("superdeepCapturesOwnFaction", True)
        sset("ladderPrisonDoorEnabled", True)
        for x in range(5):
            for z in range(5):
                dig(P(2 + x, 2 + z), 4 if (1 <= x <= 3 and 1 <= z <= 3) else 2)
        for x in range(3):
            for z in range(3):
                dig(P(10 + x, 2 + z), 3)
                dig(P(20 + x, 2 + z), 4)
                dig(P(24 + x, 2 + z), 4)
                dig(P(38 + x, 2 + z), 4)
        dig(P(16, 3), 2)
        dig(P(27, 3), 1)
        for x in range(5):                 # F: the moat ring around a 3x3 island
            for z in range(5):
                if not (1 <= x <= 3 and 1 <= z <= 3):
                    dig(P(30 + x, 3 + z), 4)
        dig(P(35, 5), 1)
        dig(P(41, 3), 1)
        lad = B.call("jawa/spawn_batch", ops="RM_Ladder:%d,%d" % P(20, 3)) or {}   # a wall cell: a ladder joins its cell to a SHALLOWER cardinal neighbour (design §8.4)
        bad = dig_misses(digs)
        if bad:
            row("CLIMB_site_dug", "UNMEASURED", "SITE", {"why": "%d drive(s) missed their depth: every scene would judge the "
                                                         "wrong pit" % len(bad), "misses": bad[:8]})
            return 2
        B.ticks(SETTLE)
        # A: the dried pond
        col_a = spawn("Colonist", P(4, 4), "player")
        B.ticks(2)
        kv, txt = climb("pawn:%s" % col_a)
        st, det = state_verdict(kv, want_held=False, want_trapped=False, want_pocket=False)
        row("CLIMB_pond_person_free", st, "MOD", dict(det, txt=txt))
        st, det = walk_verdict(order(col_a, P(4, 9)), rect_A, want_out=True)
        row("CLIMB_pond_person_walks_out", st, "MOD", det)
        # B: sheer D 3
        col_b = spawn("Colonist", P(11, 3), "player")
        muff = spawn("Muffalo", P(10, 2), "none")
        B.ticks(2)
        kv, txt = climb("pawn:%s" % col_b)
        st, det = state_verdict(kv, want_held=True, want_trapped=True, want_pocket=True)
        row("CLIMB_D3_person_trapped", st, "MOD", dict(det, txt=txt))
        st, det = walk_verdict(order(col_b, P(11, 9)), rect_B, want_out=False)
        row("CLIMB_D3_person_cannot_walk_out", st, "MOD", det)
        kv, txt = climb("pawn:%s" % muff)
        st, det = state_verdict(kv, want_held=False, want_pocket=False)
        row("CLIMB_D3_muffalo_free", st, "MOD", dict(det, txt=txt))
        # C: sheer D 2, a rat
        rat = spawn("Rat", P(16, 3), "none")
        B.ticks(2)
        kv, txt = climb("pawn:%s" % rat)
        st, det = state_verdict(kv, want_held=True, want_trapped=True, want_pocket=True)
        row("CLIMB_D2_rat_trapped", st, "MOD", dict(det, txt=txt))
        # D: the ladder is a prison door: our colonist is free, a wild rat is not
        col_d = spawn("Colonist", P(20, 2), "player")
        rat_d = spawn("Rat", P(22, 4), "none")
        B.ticks(2)
        kc, tc = climb("pawn:%s" % col_d)
        kr, tr = climb("pawn:%s" % rat_d)
        s1, d1 = state_verdict(kc, want_trapped=False, want_pocket=True)
        s2, d2 = state_verdict(kr, want_trapped=True, want_pocket=True)
        st = "PASS" if (s1, s2) == ("PASS", "PASS") else ("UNMEASURED" if "UNMEASURED" in (s1, s2) else "FAIL")
        if not lad.get("thingsPlaced"):          # no ladder on the wall: a trapped colonist is the scene, not the mod
            st = "UNMEASURED"
        row("CLIMB_ladder_prison_door", st, "MOD" if st != "UNMEASURED" or lad.get("thingsPlaced") else "SITE",
            {"colonist": d1, "rat": d2, "txt": [tc, tr], "ladder": {k: lad.get(k) for k in ("success", "thingsPlaced", "failed")}})
        # the cliff masks (PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS): on pit B's west lip (D 0 beside D 3) a person's A* has no
        # east step and a muffalo's does
        km, tm = climb("mask:%d,%d;2" % P(9, 3))
        kb, tb = climb("mask:%d,%d;3" % P(9, 3))
        row("CLIMB_mask_seals_cliff_edge", mask_verdict(km, kb), "MOD", {"person": tm, "muffalo": tb})
        # E: a ramp frees a sheer D 4 pit and removing it re-seals (PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS)
        col_e = spawn("Colonist", P(25, 3), "player")
        B.ticks(SETTLE)
        k0, t0 = climb("%d,%d;2" % P(25, 3))
        tr = B.call("jawa/static_call", type=PROOF_TYPE, method="ProofRamp", args="%d,%d;1" % P(26, 3)) or {}
        trF = B.call("jawa/static_call", type=PROOF_TYPE, method="ProofRamp", args="%d,%d;1" % P(34, 5)) or {}   # F's ramp
        B.ticks(SETTLE)
        k1, t1 = climb("%d,%d;2" % P(25, 3))
        st, det = walk_verdict(order(col_e, P(25, 9)), (ox + 24, oz + 2, 3, 3), want_out=True)
        if st == "FAIL" and "joins=True" not in str(tr.get("result")):
            st, det = "UNMEASURED", dict(det, why="the ramp did not join (%s)" % str(tr.get("result") or tr)[:80])
        row("CLIMB_ramp_walk_out", st, "MOD", dict(det, ramp=tr))
        tr2 = B.call("jawa/static_call", type=PROOF_TYPE, method="ProofRamp", args="%d,%d;off" % P(26, 3)) or {}
        B.ticks(SETTLE)
        k2, t2 = climb("%d,%d;2" % P(25, 3))
        row("CLIMB_ramp_frees_and_retraps", ramp_verdict(k0, k1, k2), "MOD", {"txt": [t0, t1, t2], "ramp": [tr, tr2]})
        # walking speed (§8.2, priced by RM_Patch_PitStepCost with the masks on): the person who walked out of A climbs
        # surface -> D 2 ring (s = K = 2: slow), walks ring -> ring (0) and steps surface -> pit E's D 1 shelf (s 1: plain)
        cs, ts = climb("cost:%d,%d;%d,%d;%s" % (P(1, 4) + P(2, 4) + (col_a,)))
        cf, tf = climb("cost:%d,%d;%d,%d;%s" % (P(2, 3) + P(2, 4) + (col_a,)))
        cn, tn = climb("cost:%d,%d;%d,%d;%s" % (P(28, 3) + P(27, 3) + (col_a,)))
        row("CLIMB_step_cost_slow_at_K", cost_verdict(cs, cf, cn), "MOD", {"txt": [ts, tf, tn]})
        # the grid follows a fill: raise B's middle-east wall cell from D 3 to D 1 -> 3 -> 1 -> 0 is a stair for a person
        f1 = B.call("jawa/flowworks_excavation_drive", x=P(12, 3)[0], z=P(12, 3)[1], deepenLevels=0, setFill=-1, fillInLevels=2) or {}
        B.ticks(SETTLE)
        kv, txt = climb("%d,%d;2" % P(11, 3))
        if f1.get("success") is not True:     # a refused fill leaves the pocket: that is the drive, not the grid
            row("CLIMB_rebuild_follows_fill", "UNMEASURED", "SITE", {"why": "fill drive refused", "fill": f1})
        elif not kv or not fresh(kv):
            row("CLIMB_rebuild_follows_fill", "UNMEASURED", "MOD", {"why": "no fresh read", "txt": txt, "fill": f1})
        else:
            row("CLIMB_rebuild_follows_fill", "PASS" if kv.get("pocket") == "False" else "FAIL", "MOD",
                {"kv": kv, "fill": f1})
        # G: a hauler fetches from a ramped pit floor (design §8.6), by its own AI
        haul_rows(B, P, row, spawn, climb, rect_G, rect_pile)
        # F: a raider never crosses a ramped moat over its wall (design §8.6); hostiles last, vanished at once
        moat_row(B, P, row, spawn, climb, trF)
        for rid, why in OWED.items():
            row(rid, "UNMEASURED", "OWED", {"why": why})
    finally:
        for f, v in before.items():
            if v is not None:
                sset(f, v)
        res["settings_restored"] = {f: sget(f) for f in FIELDS}
        save()
    measured = [r for r in rows if r["class"] != "OWED" and r["id"] != "CLIMB_site_ready"]
    return 0 if measured and all(r["status"] == "PASS" for r in measured) else 1


if __name__ == "__main__":
    sys.exit(main())
