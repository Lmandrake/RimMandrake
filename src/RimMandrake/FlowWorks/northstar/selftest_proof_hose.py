#!/usr/bin/env python3
"""Offline selftest of the hose live driver (proof_hose.py) and the FlowWorks manifest contract (hose port step 8, design FINAL
§3.10 G5.5). No game, no bridge: a fake bridge answers every call.

Proves: (1) declared_rows() = DECLARED_ROWS + the nine MX_H0* hose scenes, no duplicate, PP1/PP2 declared; (2) the walk's
manifest (northstar/manifest.py) is v2's rows UNION the hose rows, and the walk's checkout names it; (3) a full run on the fake
bridge emits EXACTLY the declared ids (declared = emitted), writes a live certifiable result, and the hose matrix scenes and
the pre-port rows come back UNMEASURED (never absent) when GSS / the pre-port saves are not there; (4) a partial run (--only)
is mode partial, never certifiable; (5) FlowWorks/validation.py's hose_live_rows reads only a live, certifiable result at the
current mod hash (stale, partial and non-certifiable results are refused), and a row the result lacks is UNMEASURED
("missing"); (6) every id in validation.py's HOSE_ROW_SHOWS live set is declared here; (7) the save-hygiene row SL2 refuses an
old hose class name in the saved blob (the shared XML-aware helper).
"""
import argparse
import importlib.util
import io
import contextlib
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
RM = os.path.dirname(MOD)
for _p in (HERE, MOD, os.path.join(RM, "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else str(detail)[:300]))
    if not cond:
        FAILS.append(name)


class FakeBridge(object):
    """Answers every bridge call; saves write a small .rws holding a FlowWorks hose blob into a temp Saves dir. <hoses>
    replaces the census's hoses (review S7: a Dropped-only census)."""

    def __init__(self, saves, blob, hoses=None):
        self.saves, self.blob, self.calls, self.tick = saves, blob, [], 0
        self.hoses = hoses

    def call(self, tool, **kw):
        self.calls.append(tool)
        if tool == "rimworld/save_game":
            with open(os.path.join(self.saves, kw["saveName"] + ".rws"), "wb") as f:
                f.write(self.blob)
        if tool == "rimworld/get_ui_state":
            return {"programState": "Playing"}
        if tool == "jawa/running_mods":
            return {"success": True, "packageIds": ["mandrake.rm.flowworks"]}
        return {"success": True}

    def probe(self, cmd, wait_s=20.0):
        return {}

    def probe_of(self, t, cmd, wait_s=20.0, poll_s=0.3):
        return {}

    def hp(self, cmd, wait_s=20.0):
        if cmd == "census":
            return {"success": True, "tick": self.tick,
                    "hoses": self.hoses or [{"reel": [1, 1], "state": "Flat", "carry": "Laid", "far": [9, 9]}]}
        if cmd == "colonists":
            return {"success": True, "pawns": []}
        return {"success": True}

    def ticks(self, n):
        self.tick += n
        return {"success": True}


class NetFakeBridge(FakeBridge):
    """Answers the pump-net probe with the tank at the far end of the last hose laid (scene 5's own tank5), so the
    tank-bridge row has something real to read."""

    def __init__(self, *a, **kw):
        FakeBridge.__init__(self, *a, **kw)
        self.last_end = None

    def hp(self, cmd, wait_s=20.0):
        if cmd.startswith("lay:"):
            x0, z0, x1, z1 = (int(v) for v in cmd[4:].split(","))
            self.last_end = [x1 + 1, z1]
        if cmd.startswith("net:"):
            return {"success": True, "tanks": [{"tank": self.last_end}] if self.last_end else []}
        return FakeBridge.hp(self, cmd, wait_s)


def _mk_noload(saves, blob, hoses):
    class NoLoad(FakeBridge):
        def call(self, tool, **kw):
            if tool == "rimworld/load_game":
                return {"success": False, "message": "no such save"}
            return FakeBridge.call(self, tool, **kw)
    return NoLoad(saves, blob, hoses)


def run_fake(args_only=None, gss=False, hoses=None, bridge_cls=None):
    import validation_core as V
    import proof_hose as PH
    import validation_hose as VH
    import validation_style_hose as VSH
    saves = tempfile.mkdtemp(prefix="ph_saves_")
    V.SAVES = saves
    blob = b'<curDriver Class="RimMandrake.FlowWorks.Hose.Jobs.JobDriver_CarryHoseEnd"/> rmHoseState RM_HoseReel_Scrapper'
    B = (bridge_cls or FakeBridge)(saves, blob, hoses)
    # the moved block scripts report their declared rows (their live logic is not under test here)
    for name, fn in (("hose", "run_live"), ("maze", "run_maze"), ("relay", "run_relay"), ("carry", "run_carry")):
        ids = PH.DECLARED_ROWS[name]
        setattr(VH, fn, (lambda ids: lambda ns: {"rows": [{"id": i, "status": "PASS", "class": "MOD", "detail": {}} for i in ids]})(ids))
    VSH.run_live = lambda ns: {"rows": [{"id": i, "status": "PASS", "class": "MOD", "detail": {}} for i in PH.DECLARED_ROWS["style_hose"]]}
    V._wait_saved = lambda name, budget_s=60: True
    a = argparse.Namespace(only=args_only, no_fresh_map=True, skip_offline=False, save_name="RM_ph_selftest", preport_save=None, out=None)
    P = PH.Proof(a, bridge=B)
    P.gss_active = gss
    P.out_path = os.path.join(saves, "result.json")
    with contextlib.redirect_stdout(io.StringIO()):
        orig_pre = P.preflight

        def pre():
            orig_pre()
            P.gss_active = gss
        P.preflight = pre
        try:
            P.run()
        finally:
            P.checkpoint(final=True)
    return P, json.load(open(P.out_path, encoding="utf-8"))


def _zoo_bridge():
    """PROOF_HOSE_SWEEP_FIX_ATE_THE_ZOO: a walkthrough save holding a colonist, a staged wild muffalo, a prisoner and a
    player husky; a stray wild boar walks in after the first roster read. pawn_force_incapacitate vanish removes an id."""
    class ZooFake(NetFakeBridge):
        def __init__(self, *a, **kw):
            NetFakeBridge.__init__(self, *a, **kw)
            self.roster = [{"id": 1, "isPlayer": True, "intelligence": "Humanlike", "faction": "PlayerColony"},
                           {"id": 50, "isPlayer": False, "intelligence": "Animal", "faction": None},
                           {"id": 51, "isPlayer": False, "intelligence": "Humanlike", "faction": "Pirate", "prisoner": True},
                           {"id": 52, "isPlayer": True, "intelligence": "Animal", "faction": "PlayerColony"}]
            self.reads, self.vanished, self.bulk = 0, [], 0

        def call(self, tool, **kw):
            if tool == "jawa/list_pawns":
                self.reads += 1
                if self.reads == 2:
                    self.roster.append({"id": 60, "isPlayer": False, "intelligence": "Animal", "faction": None})
                return {"success": True, "pawns": [dict(r) for r in self.roster]}
            if tool == "jawa/pawn_force_incapacitate":
                self.vanished.append(kw.get("pawn"))
                self.roster = [r for r in self.roster if r["id"] != kw.get("pawn")]
                return {"success": True}
            if tool == "jawa/destroy_bulk":
                self.bulk += 1
                if not kw.get("dryRun", True):
                    self.roster = [r for r in self.roster if r["isPlayer"] and r["intelligence"] == "Humanlike"]
                return {"success": True, "matchedCount": 0}
            return NetFakeBridge.call(self, tool, **kw)
    return ZooFake


def zoo_checks():
    import validation_core as V
    Zoo = _zoo_bridge()
    holder = {}

    def mk(*a, **kw):
        holder["B"] = Zoo(*a, **kw)
        return holder["B"]
    with contextlib.redirect_stdout(io.StringIO()):
        _, res = run_fake(bridge_cls=mk)
    B = holder["B"]
    ids = sorted(r["id"] for r in B.roster)
    check("zoo: --no-fresh-map never calls destroy_bulk on a save that holds non-colonists", B.bulk == 0, B.bulk)
    check("zoo: the staged muffalo, prisoner and player husky survive every sweep", ids[:4] == [1, 50, 51, 52], ids)
    check("zoo: the stray that walked in after the snapshot is vanished, and only it", B.vanished == [60] and 60 not in ids,
          (B.vanished, ids))
    check("zoo: the result records the kept snapshot", sorted((res.get("kept_pawns") or {}).get("kept") or []) == [50, 51, 52],
          res.get("kept_pawns"))
    # nothing kept (a fresh map): the old bulk route; an unreadable snapshot: nothing removed at all
    V.keep_pawns_reset()
    fb = Zoo(tempfile.mkdtemp(), b"")
    check("zoo: nothing kept -> destroy_bulk route", V.sweep_non_colonists(fb)["route"] == "destroy_bulk" and fb.bulk == 1)

    class Blind(FakeBridge):
        def call(self, tool, **kw):
            if tool == "jawa/list_pawns":
                return {"success": False, "message": "no"}
            if tool == "jawa/destroy_bulk":
                raise AssertionError("bulk on a blind snapshot")
            return FakeBridge.call(self, tool, **kw)
    bl = Blind(tempfile.mkdtemp(), b"")
    kp = V.keep_pawns_on_map(bl)
    sw = V.sweep_non_colonists(bl)
    check("zoo: an unreadable snapshot refuses every sweep (removes nothing)", "error" in kp and sw["route"].startswith("refused"), sw)
    V.keep_pawns_reset()
    zoo_start_checks(Zoo)


def vh_reel_facing_checks(VH):
    """VALIDATION_HOSE_REELS_FIX_STILL_WEST: validation_hose stages each reel facing its hose's end (3fa1dc487d's pattern)."""
    import validation_core as V
    src = open(VH.__file__, encoding="utf-8").read()
    check("VH: no reel is staged with reel_west / reel_west_ops", "reel_west" not in src)
    face = {k: "NESW"[V.reel_facing(k, t)] for k, t in VH.RELAY_TARGET.items()}
    check("VH: relays A and B face East (their next reel), C faces West (A, the refused ring)",
          [face[VH.RA], face[VH.RB], face[VH.RC]] == ["E", "E", "W"], face)
    check("VH: the hose and carry reels face East, at their ends", V.reel_facing(VH.R1, VH.F1) == 1 and V.reel_facing(VH.R2, VH.F2) == 1
          and V.reel_facing(VH.CREEL, VH.CTARGET) == 1)
    check("VH: the relay row checks the brass inlet only on the relay's facing side",
          "brass = inward == [1, 0] and V.reel_facing(dst, RELAY_TARGET[dst]) == 3" in src)


def zoo_start_checks(Zoo):
    """PROOF_SWEEPS_FIX_OTHER_ZOOS_STILL_OPEN: validation_core.sweep_at_start, the opening sweep validation_v2
    (--current-map), liquid_checks, raid_trench_proof and water_scenes_walk share."""
    import validation_core as V
    V.keep_pawns_reset()
    z = Zoo(tempfile.mkdtemp(), b"")
    s1 = V.sweep_at_start(z, made_map=False)        # read 1: snapshot {50,51,52}; read 2 (the sweep): the boar 60 walks in
    ids = sorted(r["id"] for r in z.roster)
    check("start: a map we did not make keeps its zoo and bulk is never called", z.bulk == 0 and ids == [1, 50, 51, 52], (z.bulk, ids))
    check("start: the stray that arrived after the snapshot is vanished", z.vanished == [60], (z.vanished, s1))
    z.roster.append({"id": 61, "isPlayer": False, "intelligence": "Animal", "faction": None})
    V.sweep_at_start(z, made_map=False)             # the next scene of the same run: the first snapshot stands
    check("start: a second call does not re-snapshot (a stray from scene 1 is still swept)", 61 in z.vanished
          and sorted(V.KEEP_PAWNS) == [50, 51, 52], (z.vanished, sorted(V.KEEP_PAWNS)))
    # QUIET_SITE_FIX_JAILBREAK_BY_VANISHING: quiet_site's hostiles_removed (helpers.kill_hostiles) spares the kept prisoner
    import helpers as MH
    z.roster.append({"id": 62, "isPlayer": False, "intelligence": "Humanlike", "faction": "Pirate", "hostile": True})
    z.roster[2]["hostile"] = True
    z.vanished = []
    MH.kill_hostiles(z)
    MH.kill_wildlife(z)
    MH.clear_strangers(z)
    check("start: kill_hostiles / kill_wildlife / clear_strangers never vanish a kept prisoner or animal",
          not set(z.vanished) & {50, 51, 52} and 62 in z.vanished and 51 in [r["id"] for r in z.roster], (z.vanished, sorted(MH.KEEP_PAWNS)))
    check("start: the helpers' keep set is the snapshot (shared with validation_core)", sorted(MH.KEEP_PAWNS) == [50, 51, 52])
    fresh = Zoo(tempfile.mkdtemp(), b"")
    s3 = V.sweep_at_start(fresh, made_map=True)
    check("start: a map the run made resets the keep set and takes the bulk route", s3["route"] == "destroy_bulk"
          and fresh.bulk == 1 and not V.KEEP_PAWNS and not MH.KEEP_PAWNS, (s3, sorted(V.KEEP_PAWNS)))
    V.keep_pawns_reset()
    # can-fail: no proof script on the item's list sweeps non-colonists around the keep set any more
    for f in ("validation_v2.py", "liquid_checks.py", "raid_trench_proof.py", "water_scenes_walk.py"):
        src = open(os.path.join(HERE, f), encoding="utf-8").read()
        check("start: %s has no direct destroy_bulk nonColonists" % f,
              'call("jawa/destroy_bulk", filter="nonColonists"' not in src)


def main():
    import proof_hose as PH
    dr = PH.declared_rows()
    mx = [r for r in dr if r.startswith("MX_H0")]
    check("declared_rows: DECLARED_ROWS + 9 hose matrix scenes, no duplicate", len(mx) == 9 and len(dr) == len(set(dr))
          and all(r in dr for ids in PH.DECLARED_ROWS.values() for r in ids), (len(mx), len(dr)))
    check("declared_rows: the pre-port rows and the real-flow bars are declared",
          "PP1_preport_midcarry_save_loads" in dr and "NS_tank_feeds_hose" in dr and "RL6_debug_flow_propagates" in dr
          and "RL6_flow_passes_through" not in dr)
    import manifest as MF
    import validation_v2 as V2
    with contextlib.redirect_stdout(io.StringIO()):
        man, v2 = MF.declared_rows(), V2.declared_rows()
    check("manifest = v2 UNION hose rows, no duplicate", set(man) == set(v2) | set(dr) and len(man) == len(set(man)), (len(man), len(v2), len(dr)))
    walk = open(os.path.join(os.path.dirname(os.path.dirname(RM)), "design", "validation_walks", "RimMandrake", "FlowWorks.md"), encoding="utf-8").read()
    check("the FlowWorks walk's checkout is the manifest", "\ncheckout: src/RimMandrake/FlowWorks/northstar/manifest.py" in walk)

    P, res = run_fake()
    st0 = {r["id"]: r["status"] for r in res["rows"]}
    check("tank-bridge row is UNMEASURED (never PASS, never a mod FAIL) when the net probe never sees the pump's own tank",
          st0.get("NS_tank_does_not_bridge_pipe_runs") == "UNMEASURED", st0.get("NS_tank_does_not_bridge_pipe_runs"))
    with contextlib.redirect_stdout(io.StringIO()):
        _, res_net = run_fake(bridge_cls=NetFakeBridge)
    stn = {r["id"]: r for r in res_net["rows"]}
    tb = stn.get("NS_tank_does_not_bridge_pipe_runs") or {}
    check("tank-bridge row PASSES once the probe sees the pump's own tank and not the second run's",
          tb.get("status") == "PASS" and (tb.get("detail") or {}).get("probeSawPumpTank") is True, tb)
    emitted = [r["id"] for r in res["rows"]]
    declared = [r for r in dr]
    missing = [r for r in declared if r not in emitted]
    extra = [r for r in emitted if r not in declared and not r.startswith("RF_site")]
    check("a full fake run emits exactly the declared ids (declared = emitted)", not missing and not extra, (missing[:6], extra[:6]))
    check("a full run is mode live and certifiable", res["mode"] == "live" and res["certifiable"] is True, (res["mode"], res.get("certifiable")))
    st = {r["id"]: r["status"] for r in res["rows"]}
    check("hose matrix scenes without GSS: UNMEASURED, never absent", all(st.get(m) == "UNMEASURED" for m in mx), [st.get(m) for m in mx][:3])
    check("pre-port rows without --preport-save: UNMEASURED", st.get("PP1_preport_midcarry_save_loads") == "UNMEASURED"
          and st.get("PP2_preport_midretract_save_loads") == "UNMEASURED")
    check("SL2 refuses a saved hose job driver when no colonist was on a hose job at the save", st.get("SL2_save_names_no_class_of_ours") == "FAIL")

    # review S7: SL4 is GSS's old staged check again -- a save holding only a DROPPED hose (no colonist to stage the CARRYING
    # half) is UNMEASURED with the staging recorded, never PASS (the post-port SL4 passed it on "every carried hose survived")
    import validation_hose as VH0
    dropped = [{"reel": list(VH0.CREEL), "state": "Flat", "carry": "Dropped", "far": [9, 9], "trail": {"count": 3, "last": [5, 5]}}]
    P3, res3 = run_fake(hoses=dropped)
    sl4 = next(r for r in res3["rows"] if r["id"] == "SL4_carry_states_survive")
    check("SL4 with only a Dropped hose and no colonist to stage: UNMEASURED, staging recorded (reel1/reel2)",
          sl4["status"] == "UNMEASURED" and (sl4["detail"].get("staging") or {}).get("error") == "no colonist"
          and "dropped(CR4a)" in sl4["detail"] and "carrying(CR4b)" in sl4["detail"], (sl4["status"], str(sl4["detail"])[:200]))
    # HW1 (HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS): every laid hose's census wallCross must read 0
    wv = PH.walls_verdict
    laid = lambda i, **kw: dict({"id": i, "reel": [i, 1], "laid": True, "layOk": True, "wallCross": 0, "wallCrossAt": None}, **kw)
    check("walls_verdict: every laid hose wallCross 0 -> PASS", wv({"hoses": [laid(1), laid(2)]})[0] == "PASS")
    w_bad = wv({"hoses": [laid(1), laid(2, wallCross=7, wallCrossAt=[22, 40])]})
    check("walls_verdict: one hose crossing -> FAIL MOD naming it", w_bad[0] == "FAIL" and w_bad[1] == "MOD"
          and w_bad[2]["crossing"][0]["id"] == 2 and w_bad[2]["crossing"][0]["at"] == [22, 40], w_bad)
    check("walls_verdict: no laid hose -> UNMEASURED SITE (stored reels ignored)",
          wv({"hoses": [laid(1, laid=False, wallCross=5)]})[:2] == ("UNMEASURED", "SITE"))
    check("walls_verdict: census without wallCross (old DLL) -> UNMEASURED HARNESS, never PASS",
          wv({"hoses": [{"id": 1, "laid": True, "layOk": True}]})[:2] == ("UNMEASURED", "HARNESS"))
    check("walls_verdict: a census that did not answer -> UNMEASURED HARNESS, not SITE",
          wv({"success": False, "error": "timeout"})[:2] == ("UNMEASURED", "HARNESS") and wv(None)[:2] == ("UNMEASURED", "HARNESS"))
    hw1 = next((r for r in res["rows"] if r["id"] == "HW1_no_laid_hose_crosses_a_wall"), None)
    check("a full fake run emits HW1 (the fake census has no wallCross: UNMEASURED)", hw1 is not None and hw1["status"] == "UNMEASURED", hw1)
    v = PH.sl4_verdict
    ok_carry = {"reel1_staged": {"carry": "Dropped"}, "reel2_staged": {"carry": "Carrying"}, "p1": 1, "p2": 2}
    d1 = {"carry": "Dropped", "far": [1, 1], "trailCount": 3, "trailLast": [2, 2], "pending": "Deploy", "pendingAt": [9, 9]}
    c2a = {"carry": "Carrying", "trailCount": 4, "pending": "Deploy"}
    check("sl4_verdict: both halves staged and round-tripped -> PASS", v(ok_carry, d1, dict(d1), c2a, dict(c2a), {}, {}) == "PASS")
    check("sl4_verdict: the Carrying hose comes back Stored -> FAIL",
          v(ok_carry, d1, dict(d1), c2a, dict(c2a, carry="Stored"), {}, {}) == "FAIL")
    check("sl4_verdict: the Dropped hose's trail changed over the load -> FAIL",
          v(ok_carry, d1, dict(d1, trailCount=2), c2a, dict(c2a), {}, {}) == "FAIL")
    check("sl4_verdict: one colonist (Carrying half not staged) -> UNMEASURED, never PASS",
          v(dict(ok_carry, reel2_staged={"error": "only one free colonist"}), d1, dict(d1), {}, {}, {}, {}) == "UNMEASURED")
    # review 2026-10-20: a staging that read no hose at the reel (carry None) or the wrong state measured the site, not the mod
    check("sl4_verdict: reel 1 staged with no hose read (carry None) -> UNMEASURED, never FAIL",
          v(dict(ok_carry, reel1_staged={"carry": None}), d1, {}, c2a, dict(c2a), {}, {}) == "UNMEASURED")
    check("sl4_verdict: reel 2 staged Dropped instead of Carrying -> UNMEASURED",
          v(dict(ok_carry, reel2_staged={"carry": "Dropped"}), d1, dict(d1), c2a, dict(c2a), {}, {}) == "UNMEASURED")

    class NoHoseBridge(FakeBridge):
        def hp(self, cmd, wait_s=20.0):
            if cmd == "census":
                return {"success": True, "tick": self.tick, "hoses": []}
            return FakeBridge.hp(self, cmd, wait_s)
    with contextlib.redirect_stdout(io.StringIO()):
        _, resnh = run_fake(bridge_cls=NoHoseBridge)
    stnh = {r["id"]: r["status"] for r in resnh["rows"]}
    check("SL2/SL3 with no hose on the map at the save are UNMEASURED (site), not a MOD FAIL",
          stnh.get("SL2_save_names_no_class_of_ours") == "UNMEASURED" and stnh.get("SL3_hoses_and_reel_styles_survive") == "UNMEASURED", stnh)
    # H0_probe_channel (review S7): a failing matrix probe channel turns every hose scene row FAIL (ids stay declared)
    import types
    spec = PH.hose_matrix_spec()
    if spec is None:
        check("H0_probe_channel surfacing (UNMEASURED: GSS northstar_matrix not on disk)", True)
    else:
        fake = types.ModuleType("run_live")
        fake.LiveBridge = lambda: None
        scenes = {sc["id"]: {"status": "PASS"} for sc in spec["scenes"]}
        fake.run = lambda a, b, mock=False: {"scenes": scenes, "rows": [{"id": "H0_probe_channel", "status": "FAIL", "detail": {"success": False}}]}
        saved = sys.modules.get("run_live")
        fake.load_catalog = saved.load_catalog       # the scene catalog stays GSS's real one; only the live run is faked
        sys.modules["run_live"] = fake
        try:
            Pm = PH.Proof(argparse.Namespace(only=None, no_fresh_map=True, skip_offline=False, save_name=None, preport_save=None, out=None),
                          bridge=FakeBridge(tempfile.mkdtemp(), b""))
            Pm.gss_active = True
            with contextlib.redirect_stdout(io.StringIO()):
                Pm.matrix_hose()
            mrows = {r["id"]: r["status"] for r in Pm.rows}
            check("a failing H0_probe_channel turns every MX_ hose scene UNMEASURED (none PASS on a dead probe, none a mod FAIL)",
                  len(mrows) == len(scenes) and set(mrows.values()) == {"UNMEASURED"}, mrows)
            fake.run = lambda a, b, mock=False: {"scenes": scenes, "rows": [{"id": "H0_probe_channel", "status": "PASS"}]}
            Pm.rows = []
            with contextlib.redirect_stdout(io.StringIO()):
                Pm.matrix_hose()
            check("can-fail: a passing H0_probe_channel leaves the scenes as measured (PASS)",
                  {r["status"] for r in Pm.rows} == {"PASS"}, [r["status"] for r in Pm.rows][:3])
        finally:
            if saved is not None:
                sys.modules["run_live"] = saved
            else:
                sys.modules.pop("run_live", None)

    # HOSE_REALFLOW_DIAGNOSE_SHORT_POUR_DRY_TANK: a pump level is conserved in tank + the route's hoses (a hose fills from its
    # first level, rev 2 §3.7 L8); live run 6 read tank 8,899 + hose 1,101 = one level as a FAIL. Can-fail both ways.
    import proof_hose as PHm
    saved_tank, saved_held = PHm._tank, PHm._held
    try:
        for name, tank_gain, hose_gain, want in (("tank 8899 + hose 1101 is one level", 8899, 1101, True),
                                                 ("tank 8899 with an empty hose is short", 8899, 0, False),
                                                 ("a hose that took the whole level while the tank gained 0 is short", 0, 10000, False)):
            fb = FakeBridge(tempfile.mkdtemp(), b"")
            PHm._tank = lambda B, c, g=tank_gain, fb=fb: {"units": g if fb.tick >= 100 else 0}
            PHm._held = lambda B, reels, g=hose_gain, fb=fb: g if fb.tick >= 100 else 0
            _, w = PHm._moved(fb, (0, 0), 0, [(1, 1)], 0)
            check("realflow _moved: " + name, (w <= PHm.RF_CYCLE) == want, w)
    finally:
        PHm._tank, PHm._held = saved_tank, saved_held

    # code review 2026-10-19: a short build_batch makes a FAIL row UNMEASURED SITE; a "dropped hose moved nothing" row on a scene that
    # could not move liquid anyway (tank unread / pump never powered) is UNMEASURED, and PASSes only with a live tank and powered pump
    class ScenFake(FakeBridge):
        short = False
        tank_units = None
        powered = None

        def call(self, tool, **kw):
            r = FakeBridge.call(self, tool, **kw)
            if tool == "jawa/build_batch" and self.short:
                return {"success": True, "survived": 0, "failed": [{"op": "x"}]}
            return r

        def hp(self, cmd, wait_s=20.0):
            if cmd.startswith("tank:"):
                return {"success": True, "units": self.tank_units} if self.tank_units is not None else {"success": False}
            if cmd.startswith("pump:"):
                return {"success": True, "powered": self.powered}
            if cmd.startswith("settrail:"):
                return {"success": True, "carry": "Dropped"}
            return FakeBridge.hp(self, cmd, wait_s)

    def rf_rows(**kw):
        fb = ScenFake(tempfile.mkdtemp(), b"")
        for k, v in kw.items():
            setattr(fb, k, v)
        with contextlib.redirect_stdout(io.StringIO()):
            rr = PHm._rf(fb)["rows"]
        return {r["id"]: r for r in rr}
    r0 = rf_rows(tank_units=500, powered=True)
    check("dropped-hose row PASSes with a live tank and a powered pump (can pass)", r0["NS_hose_dropped_carries_nothing"]["status"] == "PASS",
          r0["NS_hose_dropped_carries_nothing"])
    r1 = rf_rows(tank_units=None, powered=True)
    check("dropped-hose row on an unread tank is UNMEASURED, not a vacuous PASS", r1["NS_hose_dropped_carries_nothing"]["status"] == "UNMEASURED")
    r2 = rf_rows(tank_units=500, powered=None)
    check("dropped-hose row with a pump that never powered is UNMEASURED, not a vacuous PASS", r2["NS_hose_dropped_carries_nothing"]["status"] == "UNMEASURED")
    rp = rf_rows(tank_units=500, powered=None)
    check("a FAIL row over a pump that never powered reads UNMEASURED (SITE), not a MOD FAIL",
          rp["NS_hose_carries_real_units"]["status"] == "UNMEASURED" and rp["NS_hose_carries_real_units"]["class"] == "SITE", rp["NS_hose_carries_real_units"])
    r3 = rf_rows(tank_units=500, powered=True, short=True)
    check("a FAIL row over a short build_batch reads UNMEASURED (SITE), not a MOD FAIL",
          r3["NS_hose_carries_real_units"]["status"] == "UNMEASURED" and r3["NS_hose_carries_real_units"]["class"] == "SITE", r3["NS_hose_carries_real_units"])
    r4 = rf_rows(tank_units=500, powered=True)
    check("can-fail: with a full build the same row is a measured FAIL (MOD), nothing moved",
          r4["NS_hose_carries_real_units"]["status"] == "FAIL" and r4["NS_hose_carries_real_units"]["class"] == "MOD", r4["NS_hose_carries_real_units"])

    # review 2026-10-20 (round 3): a SITE/harness fault reads UNMEASURED, a genuine mod fault still reads FAIL
    class SiteFake(ScenFake):
        lay_ok = True
        destroy_ok = True
        load_ok = True

        def call(self, tool, **kw):
            if tool == "jawa/destroy_batch":
                if kw.get("categories") == "Building" and not self.destroy_ok:     # the scenes' own destroys, not the site prep's
                    return {"success": False, "message": "no"}
                return {"success": True, "destroyed": 1}
            if tool == "rimworld/load_game" and not self.load_ok:
                return {"success": False, "message": "no such save"}
            return ScenFake.call(self, tool, **kw)

        def hp(self, cmd, wait_s=20.0):
            if cmd.startswith("lay:") and not self.lay_ok:
                return {"success": False, "error": "no room for the straight lead-out"}
            return ScenFake.hp(self, cmd, wait_s)

    def sf_rows(**kw):
        fb = SiteFake(tempfile.mkdtemp(), b"")
        for k, v in kw.items():
            setattr(fb, k, v)
        with contextlib.redirect_stdout(io.StringIO()):
            rr = PHm._rf(fb)["rows"]
        return {r["id"]: r for r in rr}
    rl = sf_rows(tank_units=500, powered=True, lay_ok=False)
    for rid in ("NS_hose_carries_real_units", "NS_hose_plumps_only_from_powered_pump", "NS_hose_far_end_pump", "NS_relay_chain_carries",
                "NS_pipe_and_hose_one_net", "NS_tank_feeds_hose", "NS_hose_port_removed_discovered"):
        check("a hose that was never laid reads UNMEASURED (SITE), not a mod FAIL: " + rid, rl[rid]["status"] == "UNMEASURED", rl[rid])
    rok = sf_rows(tank_units=500, powered=True)
    check("can-fail: a laid hose whose battery cut worked but never went Plump is a measured FAIL",
          rok["NS_hose_plumps_only_from_powered_pump"]["status"] == "FAIL", rok["NS_hose_plumps_only_from_powered_pump"])
    rnd = sf_rows(tank_units=500, powered=True, destroy_ok=False)
    check("a battery / far tank that destroy_batch never removed reads UNMEASURED, not FAIL",
          rnd["NS_hose_plumps_only_from_powered_pump"]["status"] == "UNMEASURED"
          and rnd["NS_hose_port_removed_discovered"]["status"] == "UNMEASURED", (rnd["NS_hose_plumps_only_from_powered_pump"]["status"],
                                                                                  rnd["NS_hose_port_removed_discovered"]["status"]))
    rpb = sf_rows(tank_units=None, powered=True)
    check("a tank probe that never answers makes the bar UNMEASURED, not a mod FAIL", rpb["NS_hose_carries_real_units"]["status"] == "UNMEASURED",
          rpb["NS_hose_carries_real_units"])
    rf0 = sf_rows(tank_units=500, powered=True)
    check("can-fail: a live tank, a powered pump and a laid hose that moves nothing is still FAIL",
          rf0["NS_hose_carries_real_units"]["status"] == "FAIL", rf0["NS_hose_carries_real_units"])
    # a refused load leaves the old map Playing: SL3/SL4 must not compare it with itself and PASS
    with contextlib.redirect_stdout(io.StringIO()):
        _, resld = run_fake(bridge_cls=lambda saves, blob, hoses=None: _mk_noload(saves, blob, hoses))
    stl = {r["id"]: r["status"] for r in resld["rows"]}
    check("a refused load_game makes SL3 and SL4 UNMEASURED (declared ids still emitted)",
          stl.get("SL3_hoses_and_reel_styles_survive") == "UNMEASURED" and stl.get("SL4_carry_states_survive") == "UNMEASURED", stl)

    P2, res2 = run_fake(args_only=["realflow"])
    check("a partial run (--only) is mode partial and never certifiable", res2["mode"] == "partial" and res2["certifiable"] is False)

    # validation.py's reader: only a live certifiable result at the current hash counts; a missing row is UNMEASURED
    spec = importlib.util.spec_from_file_location("fw_validation_ph", os.path.join(MOD, "validation.py"))
    vm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vm)
    check("every hose live row validation.py claims is declared by proof_hose", not [r for r in vm.HOSE_LIVE_IDS if r not in dr],
          [r for r in vm.HOSE_LIVE_IDS if r not in dr])
    tmp = tempfile.mkdtemp(prefix="ph_ns_")
    vm.NS = tmp
    good = {"mode": "live", "certifiable": True, "mod_hash": "H1", "rows": [{"id": "NS_hose_carries_real_units", "status": "PASS", "class": "MOD"}]}
    for name, d in (("proof_hose_20261011T000001.json", dict(good, mod_hash="OLD")),            # stale
                    ("proof_hose_20261011T000002.json", dict(good, mode="partial")),           # partial
                    ("proof_hose_20261011T000003.json", dict(good, certifiable=False))):       # not certifiable
        json.dump(d, open(os.path.join(tmp, name), "w"))
    check("stale, partial and non-certifiable results are refused", vm.latest_hose_result("H1") is None)
    json.dump(good, open(os.path.join(tmp, "proof_hose_20261011T000004.json"), "w"))
    found = vm.latest_hose_result("H1")
    check("a live certifiable result at the current hash is read", found is not None and found[1]["rows"][0]["status"] == "PASS")

    # SL2's helper refuses an old hose class in the blob
    import validation_hose as VH
    check("SL2 helper refuses an old GSS hose class", bool(VH.save_class_hits(b'<li Class="RimMandrake.GimmeSomeSlack.Hose.CompHoseReel"/>')["offending"]))
    zoo_checks()
    # PROOF_REELS_FIX_STILL_STAGED_WEST: scene reels face their tank (East); NS_hose_ends_on_ports reads the nozzle on that side
    sc = PH.Scene(None, 0)
    check("reels: scene 0's reel is built facing East toward its tank, footprint kept",
          PH.V.reel_toward(sc.reel, sc.end) == "RM_HoseReel:%d,%d,1" % (sc.reel[0], sc.reel[1] + 1))
    check("reels: nozzle side cells by facing (E = the footprint's east column, W = its west column)",
          PH._nozzle_side(10, 20, 1) == (11, 12, 20, 22) and PH._nozzle_side(10, 20, 3) == (10, 11, 20, 22))
    vh_reel_facing_checks(VH)
    print("selftest_proof_hose: %s (%d failing)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
