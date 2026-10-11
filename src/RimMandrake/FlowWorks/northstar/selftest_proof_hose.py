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
    """Answers every bridge call; saves write a small .rws holding a FlowWorks hose blob into a temp Saves dir."""

    def __init__(self, saves, blob):
        self.saves, self.blob, self.calls, self.tick = saves, blob, [], 0

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
            return {"success": True, "tick": self.tick, "hoses": [{"reel": [1, 1], "state": "Flat", "carry": "Laid", "far": [9, 9]}]}
        if cmd == "colonists":
            return {"success": True, "pawns": []}
        return {"success": True}

    def ticks(self, n):
        self.tick += n
        return {"success": True}


def run_fake(args_only=None, gss=False):
    import validation_core as V
    import proof_hose as PH
    import validation_hose as VH
    import validation_style_hose as VSH
    saves = tempfile.mkdtemp(prefix="ph_saves_")
    V.SAVES = saves
    blob = b'<curDriver Class="RimMandrake.FlowWorks.Hose.Jobs.JobDriver_CarryHoseEnd"/> rmHoseState RM_HoseReel_Scrapper'
    B = FakeBridge(saves, blob)
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
