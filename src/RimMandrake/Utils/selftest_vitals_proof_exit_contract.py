#!/usr/bin/env python3
"""prove_vitals_governor.py keeps its own exit contract when a case cannot look.

The script's last lines promise: exit 1 = a row FAILED; 3 = no row failed but a row could not look (UNMEASURED);
and it writes every row it measured to its proof JSON. A case that cannot look (each cause that the page names) must therefore end the run with exit 3 and keep the rows already measured,
never exit 1 (which `rimflow` effect checks and `work_bundle.py` read as "fails") with no JSON at all.

The proof runs offline against a fake bridge (stub `rimbridge_client`, `rmpaths`, `await_lifecycle`; `time.sleep` a
no-op). The real governor module is imported.

    python3 src/RimMandrake/Utils/selftest_vitals_proof_exit_contract.py
"""
import glob
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PROOF = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "prove_vitals_governor.py")
FAILS = []

BOOT = r'''
import sys, types, time, runpy, json
out_dir, quiet_after, survived, proof = sys.argv[1], json.loads(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
fake = json.loads(sys.argv[5])   # the one thing this run's bridge cannot do: no_map, no_far_cell, events_cut, no_arm
time.sleep = lambda s: None
rp = types.ModuleType("rmpaths")
rp.rm_path = rp.rm_str = rp.rm_win = lambda *a: out_dir
sys.modules["rmpaths"] = rp
al = types.ModuleType("await_lifecycle")
class _LC:
    def __init__(self, ok): self.ok, self.reason = ok, "" if ok else "map_ready not reached (fake)"
    def __bool__(self): return self.ok
al.await_lifecycle = lambda call, phase, s: _LC(not (phase == "map_ready" and fake.get("no_map")))
sys.modules["await_lifecycle"] = al
quiet = iter(quiet_after)
COLS = [{"id": "Human1", "def": "Human", "x": 10, "z": 10}, {"id": "Human2", "def": "Human", "x": 11, "z": 10}]
def answer(t, p):
    if t == "jawa/quiet_site":
        return {"success": True, "threatsAfter": next(quiet)}
    if t == "jawa/list_pawns":
        if p.get("faction") == "player": return {"pawns": COLS}
        return {"pawns": [] if fake.get("no_far_cell") else [{"id": "Deer5", "x": 50, "z": 50}]}
    if t == "jawa/vitals":
        a = p.get("action")
        if a == "arm": return {"armed": not fake.get("no_arm")}
        if a == "events": return {"truncated": bool(fake.get("events_cut")), "triggers": [{"kind": "threat_structure", "subject": "Wall", "seq": 1,
                                                "detail": "new hostile structure Wall (Mechanoid)"}]}
        return {"threats": 1}
    if t == "jawa/build_batch":
        return {"survived": survived}
    return {"success": True}   # so jawa/time_clock gives no ticksGame: every clock read is blind
class RimBridge:
    def __init__(self, **k): pass
    def connect(self): pass
    def call(self, t, p): return answer(t, p or {})
rb = types.ModuleType("rimbridge_client")
rb.RimBridge = RimBridge
rb.resolve_endpoint = lambda: ("127.0.0.1", 0, "x")
sys.modules["rimbridge_client"] = rb
sys.argv = [proof] + sys.argv[6:]
runpy.run_path(proof, run_name="__main__")
'''


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def run(quiet_after, cases, survived=1, **fake):
    """-> (rc, rows of the proof JSON or None, output) for one offline run of the proof. `quiet_after`: the
    threatsAfter that each jawa/quiet_site answers, in order; `survived`: what jawa/build_batch answers; `fake`: the
    bridge's one blind spot (BOOT's `fake`)."""
    d = tempfile.mkdtemp(prefix="vitals_proof_")
    r = subprocess.run([sys.executable, "-c", BOOT, d, json.dumps(quiet_after), str(survived), PROOF,
                        json.dumps(fake)] + cases,
                       capture_output=True, text=True, timeout=120)   # hang guard: the offline run takes about 1 s
    files = glob.glob(os.path.join(d, "proof_*.json"))
    rows = json.load(open(files[0])) if files else None
    return r.returncode, rows, (r.stdout + r.stderr)[-600:]


CLUSTER = "hostile_structure_threat_detected_without_hostile_pawn_count"


def t_every_row_pass_exits_0():
    rc, rows, out = run([0], ["cluster"])
    ok(rc == 0 and bool(rows) and rows.get(CLUSTER, {}).get("result") == "PASS",
       "every row PASS: the cluster row on a cleared map reads PASS and exits 0 (rc %s; %s)" % (rc, out))


def t_a_failed_row_exits_1():
    rc, rows, out = run([0], ["cluster"], survived=0)
    ok(rc == 1 and bool(rows) and rows.get(CLUSTER, {}).get("result") == "FAIL",
       "a FAILED row (our wall did not survive): exit 1, the row in the JSON (rc %s; %s)" % (rc, out))


BLIND = "run_stopped_could_not_look"
# each cause the page names -> (the run that meets it, a word its recorded cause must hold)
CAUSES = {
    "threats not cleared": (dict(quiet_after=[1], cases=["cluster"]), "not cleared"),
    "no map after start": (dict(quiet_after=[0], cases=["cluster"], no_map=True), "no map"),
    "no far standable cell": (dict(quiet_after=[0], cases=["cluster"], no_far_cell=True), "far standable"),
    "no clock read": (dict(quiet_after=[0], cases=["raid"]), "ticksGame"),
    "vitals events incomplete": (dict(quiet_after=[0], cases=["cluster"], events_cut=True), "incomplete"),
    "monitor will not arm": (dict(quiet_after=[0], cases=["cluster"], no_arm=True), "would not arm"),
}


def t_a_case_that_cannot_look_exits_3():
    for what, (kw, word) in CAUSES.items():
        rc, rows, out = run(**kw)
        ok(rc == 3, "%s: exit 3 (UNMEASURED), not 1 (FAILED) (rc %s; %s)" % (what, rc, out))
        ok(bool(rows) and rows.get(BLIND, {}).get("result") == "UNMEASURED" and word in rows[BLIND].get("cause", ""),
           "%s: the proof JSON holds the UNMEASURED row %s with its cause (%s)" % (what, BLIND, rows))
    # "unless a row measured before it reads FAIL": a FAIL measured first still exits 1, beside the stop's row
    rc, rows, out = run([0, 1], ["cluster", "death"], survived=0)
    ok(rc == 1 and bool(rows) and rows.get(CLUSTER, {}).get("result") == "FAIL" and BLIND in rows,
       "a FAILED row, then a case that cannot look: exit 1, both rows in the JSON (rc %s; %s)" % (rc, rows))


def t_a_case_that_cannot_look_keeps_the_measured_rows():
    rc, rows, out = run([0, 1], ["cluster", "death"])
    ok(rc == 3, "a later case that cannot look: exit 3 (rc %s; %s)" % (rc, out))
    ok(bool(rows) and rows.get(CLUSTER, {}).get("result") == "PASS",
       "a later case that cannot look keeps the rows already measured in the JSON (%s)" % rows)


def main():
    t_every_row_pass_exits_0()
    t_a_failed_row_exits_1()
    t_a_case_that_cannot_look_exits_3()
    t_a_case_that_cannot_look_keeps_the_measured_rows()
    print("SELFTEST %s -- %d failed" % ("FAILED" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
