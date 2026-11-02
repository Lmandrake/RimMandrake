#!/usr/bin/env python3
"""selftest_checkout_identity -- validation_v2 and proof_all record a run identity the report can prove.

VALIDATION_V2_IDENTITY_WIRE_READS_ZERO: both scripts wrote neither `run_identity` nor `situational`, so
required_checks_report counted 0 proven. No game here: validation_v2 runs its own --mock tier, proof_all runs main()
with its blocks stubbed, and the fingerprint is stubbed at mod_fingerprint (its own logic: selftest_run_identity).
Both scripts also run on their DEFAULT wiring, the one a real live run takes: run_live with mock=False and no `identity`
argument, proof_all with its own _RI. The bug this item names lives in that default, so nothing above mod_fingerprint is faked.
"""
import argparse
import contextlib
import copy
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
RM = os.path.dirname(UTILS)
for _p in (UTILS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import required_checks_report as R  # noqa: E402
import run_identity as RI  # noqa: E402

FAILS = []
DLL = "d" * 64
CUR = "c" * 64


def check(name, cond, detail=""):
    print("%s %s" % ("ok  " if cond else "FAIL", name))
    if not cond:
        FAILS.append("%s %s" % (name, str(detail)[:300]))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def fake_fp(calls, state="in-sync", moved=False):
    def fp(mod, dm=None, mods_dir=None):
        calls.append(mod)
        h = "h%d" % len(calls) if moved else "h"
        return {"mod": mod, "state": state, "src_hash": h, "deployed_hash": h, "src_dirty": False}
    return fp


def clean_window(tool, **kw):
    return {"success": False, "message": "No open window's type name contains it"}


class Game(object):
    def __init__(self, dialog_open=False, broken=False):
        self.dialog_open, self.broken = dialog_open, broken

    def call(self, tool, **kw):
        if self.broken:
            raise OSError("bridge gone")
        if self.dialog_open and tool == "jawa/window_list_close":
            return {"success": True, "closedCount": 1}
        return clean_window(tool)


def mock_bridge(V2):
    """The --mock game, answering the dialog sweep (only a run with an identity makes it)."""
    b = V2.MockBridge([])
    inner = b.call
    b.call = lambda tool, **kw: clean_window(tool) if tool == "jawa/window_list_close" else inner(tool, **kw)
    return b


def identity_shape(res, mod, n_calls, calls, tag):
    ri = res.get("run_identity") or {}
    check("%s: deploy_start for %s" % (tag, mod), (ri.get("deploy_start") or {}).get("mod") == mod, ri)
    check("%s: deploy_end for %s" % (tag, mod), (ri.get("deploy_end") or {}).get("mod") == mod, ri)
    check("%s: two fingerprints, start and end" % tag, calls == [mod] * n_calls, calls)
    check("%s: a repo identity is recorded" % tag, (ri.get("git") or {}).get("source") in ("git", "mirror"), ri)


def proven(res, mod, tmp, tag):
    """How many of `res`'s rows the real report counts proven, as a live result of the current code."""
    r = copy.deepcopy(res)
    r.update(mode="live", mod=mod, mod_hash=CUR, env={"assembly_sha256": DLL}, started="2026-10-05T08:00:00")
    d = os.path.join(tmp, tag, "northstar")
    os.makedirs(d)
    with open(os.path.join(d, "proof_all_x.json"), "w", encoding="utf-8") as f:
        json.dump(r, f, default=str)
    ids = sorted({x["id"] for x in r["rows"]})
    checks = [{"id": "checkout/" + i, "source": "checkout_row", "owner": False, "required": True, "checkout_row": i} for i in ids]
    row = {"script": None, "checks": checks,
           "checkout": {"script": os.path.join(tmp, tag, "proof_all.py"), "rows": len(checks), "error": None}}
    rec = os.path.join(tmp, tag, "records")
    os.makedirs(rec)
    rep, _runs = R.build_report({"mods": {mod: row}}, rec, os.path.join(tmp, "none.jsonl"),
                                checkout_ident=lambda m, w: (CUR, [("x.dll", DLL, DLL)]))
    return rep[0]["head"], len(ids)


def main():
    tmp = tempfile.mkdtemp(prefix="selftest_checkout_identity_")
    real_fp = RI.mod_fingerprint
    try:
        # ---- validation_v2
        V2 = load("_cv2", os.path.join(RM, "FlowWorks", "northstar", "validation_v2.py"))
        a = argparse.Namespace(mock=True, fault=[], progress=None, site_save=None, fresh_map=True, current_map=False,
                               max_job_ticks=4000, reset_settings=False)
        with contextlib.redirect_stdout(io.StringIO()):
            res0 = V2.run_live(copy.copy(a))
        check("v2 --mock default: no identity (a mock tests no deployed code)", res0["run_identity"] is None, res0["run_identity"])
        # the default wiring of a real live run: mock=False and no `identity`, so run_identity_module() supplies the module
        calls0 = []
        RI.mod_fingerprint = fake_fp(calls0)
        with contextlib.redirect_stdout(io.StringIO()):
            live = V2.run_live(argparse.Namespace(**dict(vars(a), mock=False)), B=mock_bridge(V2))
        check("v2 default: the live branch ran", live["mode"] == "live", live["mode"])
        identity_shape(live, "FlowWorks", 2, calls0, "v2 default")
        check("v2 default: situational recorded", isinstance(live.get("situational"), dict), live.get("situational"))
        calls = []
        RI.mod_fingerprint = fake_fp(calls)
        with contextlib.redirect_stdout(io.StringIO()):
            res = V2.run_live(copy.copy(a), B=mock_bridge(V2), identity=RI)
        identity_shape(res, "FlowWorks", 2, calls, "v2")
        check("v2: situational recorded", isinstance(res.get("situational"), dict), res.get("situational"))
        check("v2: result stays JSON", json.loads(json.dumps(res))["run_identity"]["job"] == "validation_v2")
        head, n = proven(res, "FlowWorks", tmp, "v2ok")
        check("v2: the report counts it proven (not 0)", head["proven"] > 0, head)
        no_ri = dict(res, run_identity=None)
        check("v2 CONTROL: without run_identity 0 proven", proven(no_ri, "FlowWorks", tmp, "v2none")[0]["proven"] == 0)
        no_sit = dict(res, situational=None)
        check("v2 CONTROL: without situational 0 proven", proven(no_sit, "FlowWorks", tmp, "v2nosit")[0]["proven"] == 0)
        calls2 = []
        RI.mod_fingerprint = fake_fp(calls2, moved=True)
        with contextlib.redirect_stdout(io.StringIO()):
            moved = V2.run_live(copy.copy(a), B=mock_bridge(V2), identity=RI)
        check("v2: redeployed mid-run is not proven", proven(moved, "FlowWorks", tmp, "v2moved")[0]["proven"] == 0)
        calls3 = []
        RI.mod_fingerprint = fake_fp(calls3, state="drift")
        with contextlib.redirect_stdout(io.StringIO()):
            drift = V2.run_live(copy.copy(a), B=mock_bridge(V2), identity=RI)
        check("v2: a drifted deploy is not proven", proven(drift, "FlowWorks", tmp, "v2drift")[0]["proven"] == 0)

        # ---- proof_all, through main()
        PA = load("_cpa", os.path.join(RM, "GimmeSomeSlack", "northstar", "proof_all.py"))
        game = Game()

        class P(PA.Proof):
            def __init__(self, args):
                self.args, self.rows, self.t0 = args, [], 0
                self.blocks = {}
                self.B = game
                self.res = {"mod": PA.V.MOD, "script": "proof_all.py", "mode": "live", "rows": self.rows, "blocks": self.blocks}

            def block(self, name, fn):
                self.res["env"] = {"running": ["x"]}
                self.res["site_save"] = {"verified": True}
                self.rows.append({"id": "P1_x", "status": "PASS", "class": "MOD", "detail": "", "block": "preflight"})

            def want(self, name):
                return False

            def restore(self):
                pass

        PA.Proof = P                   # PA._RI stays the real one: its import is the wiring under test
        out = os.path.join(tmp, "proof_all_r.json")
        calls4 = []
        RI.mod_fingerprint = fake_fp(calls4)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = PA.main(["--live", "--skip-offline", "--allow-red", "x", "--out", out])
        check("proof_all main ran", rc == 0, rc)
        pa = json.load(open(out, encoding="utf-8"))
        identity_shape(pa, PA.V.MOD, 2, calls4, "proof_all")
        check("proof_all: no identity error swallowed", "run_identity_error" not in pa, pa.get("run_identity_error"))
        check("proof_all: situational bland + companion", pa.get("situational", {}).get("bland") is True and
              pa["situational"].get("companion") is True, pa.get("situational"))
        check("proof_all: the report counts it proven", proven(pa, PA.V.MOD, tmp, "paok")[0]["proven"] > 0)

        # a run that raises still gets its end fingerprint
        calls5 = []
        RI.mod_fingerprint = fake_fp(calls5)
        P.block = lambda self, name, fn: (_ for _ in ()).throw(RuntimeError("boom"))
        out2 = os.path.join(tmp, "proof_all_raised.json")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                PA.main(["--live", "--skip-offline", "--out", out2])
        except RuntimeError:
            pass
        raised = json.load(open(out2, encoding="utf-8"))
        identity_shape(raised, PA.V.MOD, 2, calls5, "proof_all raised")

        # ---- run_situational's honesty
        check("situational: a dialog left open is a modal surprise",
              "modal" in json.dumps(RI.run_situational(Game(dialog_open=True).call, True, True)["surprises"]))
        check("situational: a failed sweep is unknown, not clean", RI.run_situational(Game(broken=True).call, True, True) is None)

        # ---- the names resolve in the real deploy tool: a wrong mod name would fingerprint as `unknown` for ever
        RI.mod_fingerprint = real_fp
        import deploy_custom_mods as dm
        dirs = dm.mod_dirs()
        check("FlowWorks and GimmeSomeSlack are deploy mod names", "FlowWorks" in dirs and PA.V.MOD in dirs, sorted(dirs)[:5])

        # ---- a narrow live result must not crowd out the checkout
        narrow = {"mod": "Synth", "script": "sprinkler_live.py", "mode": "live", "started": "2026-10-06T08:00:00",
                  "mod_hash": CUR, "env": {"assembly_sha256": DLL},
                  "rows": [{"id": "sprinkler.x", "status": "PASS", "class": "MOD", "detail": ""}]}
        wide = dict(pa, mod="Synth", mod_hash=CUR, env={"assembly_sha256": DLL}, started="2026-10-05T08:00:00", mode="live")
        wide["run_identity"] = json.loads(json.dumps(pa["run_identity"]).replace(PA.V.MOD, "Synth"))
        d = os.path.join(tmp, "Synth", "northstar")
        os.makedirs(d)
        json.dump(narrow, open(os.path.join(d, "sprinkler_live_result_1.json"), "w"))
        json.dump(wide, open(os.path.join(d, "x_result_1.json"), "w"))
        row = {"script": None, "checks": [{"id": "checkout/P1_x", "source": "checkout_row", "owner": False, "required": True,
                                           "checkout_row": "P1_x"}],
               "checkout": {"script": os.path.join(tmp, "Synth", "proof_all.py"), "rows": 1, "error": None}}
        rec = os.path.join(tmp, "synthrec")
        os.makedirs(rec)
        rep, _ = R.build_report({"mods": {"Synth": row}}, rec, os.path.join(tmp, "none.jsonl"),
                                checkout_ident=lambda m, w: (CUR, [("x.dll", DLL, DLL)]))
        check("a newer narrow result does not stand in for the checkout", rep[0]["head"]["proven"] == 1, rep[0]["head"])
    finally:
        RI.mod_fingerprint = real_fp
        shutil.rmtree(tmp, ignore_errors=True)
    if FAILS:
        print("\nFAILED: %s" % FAILS)
        return 1
    print("\nOK: selftest_checkout_identity")
    return 0


if __name__ == "__main__":
    sys.exit(main())
