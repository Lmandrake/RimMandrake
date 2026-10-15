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

Scenes (plot coords from --origin, default 120,120; 30 x 12, cleared + read back by validation_core.prepare_site):
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
connectivity byte on pit B's west lip has no east bit, the muffalo band's has).  OWED (always UNMEASURED, see OWED below): CLIMB_raider_never_crosses_ramped_moat, CLIMB_hauler_fetches_ramped_floor,
CLIMB_save_reload_pockets_identical.

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

OWED = {
    "CLIMB_raider_never_crosses_ramped_moat": "needs ramps (§8.4); the masks are in (§8.5 step 2)",
    "CLIMB_hauler_fetches_ramped_floor": "needs ramps (§8.4)",
    "CLIMB_save_reload_pockets_identical": "needs a save + reload cycle on the bridge; the grid is derived, never scribed",
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


def out_of(rect, xz):
    x0, z0, w, h = rect
    return not (x0 <= xz[0] < x0 + w and z0 <= xz[1] < z0 + h)


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
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))

    def dig(c, n):
        return B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=-1) or {}

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
    ok, _ = V._wait_playing(B, leave_s=0)
    FIELDS = ("superdeepCapturesOwnFaction", "pitRelativeClimbEnabled", "ladderPrisonDoorEnabled")
    before = {f: sget(f) for f in FIELDS}
    res["settings_before"] = before
    try:
        if not ok or not V.prepare_site(B, (ox, oz, 30, 12), rows, "CLIMB_site_ready"):
            row("CLIMB_site", "UNMEASURED", "SITE", {"why": "site not ready / not playing"})
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
        dig(P(16, 3), 2)
        dig(P(27, 3), 1)
        B.call("jawa/spawn_batch", ops="RM_Ladder:%d,%d" % P(20, 3))   # a wall cell: a ladder joins its cell to a SHALLOWER cardinal neighbour (design §8.4)
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
        row("CLIMB_ladder_prison_door", st, "MOD", {"colonist": d1, "rat": d2, "txt": [tc, tr]})
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
        B.ticks(SETTLE)
        k1, t1 = climb("%d,%d;2" % P(25, 3))
        st, det = walk_verdict(order(col_e, P(25, 9)), (ox + 24, oz + 2, 3, 3), want_out=True)
        row("CLIMB_ramp_walk_out", st, "MOD", dict(det, ramp=tr))
        tr2 = B.call("jawa/static_call", type=PROOF_TYPE, method="ProofRamp", args="%d,%d;off" % P(26, 3)) or {}
        B.ticks(SETTLE)
        k2, t2 = climb("%d,%d;2" % P(25, 3))
        row("CLIMB_ramp_frees_and_retraps", ramp_verdict(k0, k1, k2), "MOD", {"txt": [t0, t1, t2], "ramp": [tr, tr2]})
        # the grid follows a fill: raise B's middle-east wall cell from D 3 to D 1 -> 3 -> 1 -> 0 is a stair for a person
        f1 = B.call("jawa/flowworks_excavation_drive", x=P(12, 3)[0], z=P(12, 3)[1], deepenLevels=0, setFill=-1, fillInLevels=2) or {}
        B.ticks(SETTLE)
        kv, txt = climb("%d,%d;2" % P(11, 3))
        if not kv or not fresh(kv):
            row("CLIMB_rebuild_follows_fill", "UNMEASURED", "MOD", {"why": "no fresh read", "txt": txt, "fill": f1})
        else:
            row("CLIMB_rebuild_follows_fill", "PASS" if kv.get("pocket") == "False" else "FAIL", "MOD",
                {"kv": kv, "fill": f1})
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
