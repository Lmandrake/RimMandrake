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
    check("tank-bridge row FAILS when the net probe measures nothing (it used to pass on an empty read)",
          st0.get("NS_tank_does_not_bridge_pipe_runs") == "FAIL", st0.get("NS_tank_does_not_bridge_pipe_runs"))
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
            check("a failing H0_probe_channel turns every MX_ hose scene FAIL (none PASS on a dead probe)",
                  len(mrows) == len(scenes) and set(mrows.values()) == {"FAIL"}, mrows)
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
    print("selftest_proof_hose: %s (%d failing)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
