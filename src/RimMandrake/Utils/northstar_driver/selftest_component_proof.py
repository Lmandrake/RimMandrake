#!/usr/bin/env python3
"""component_proof.refusal: a driver run refused at preflight reads UNMEASURED (harness or dud), never the mod's FAIL.

WASTELAND_CONTAGION_PROBE_FIVE_LOOSE_ENDS gen 1: one stuck UNKNOWN-outcome bridge marker made five live clauses print
"FAIL: no component ..." and the round charged them as game failures. Offline; no bridge.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "rimflow")))
import component_proof as cp  # noqa: E402
import relentless_live as L  # noqa: E402

STUCK = ("dlc_status: refusing jawa/dlc_status: 1 earlier mutating call(s) have an UNKNOWN outcome "
         "(b7164851922b4797 jawa/safe_advance). A retry could apply it twice.\n  python rimbridge_client.py --reconcile")


def doc(refused, preflight, components=()):
    return {"mod": "Contagion", "refused": refused, "preflight": preflight, "components": list(components)}


def classify(d, tmp):
    js = os.path.join(tmp, "out.json")
    with open(js, "w") as f:
        json.dump(d, f)
    why = cp.refusal(js)
    log = os.path.join(tmp, "run.log")
    with open(log, "w") as f:
        f.write("$ python.exe cli.py run\nUNMEASURED: preflight refused, chain genome never ran: %s -> %s\n" % (why, js))
    return why, L.could_not_ask(log)


def main():
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        why, kind = classify(doc("site:dlc_status FAIL; dev_god_mode UNMEASURED", [
            {"name": "tool_census", "status": "PASS", "evidence": "ok"},
            {"name": "dev_god_mode", "status": "UNMEASURED", "evidence": "get_game_info has no 'devModeEnabled' field"},
            {"name": "site:dlc_status", "status": "FAIL", "evidence": STUCK}]), tmp)
        if not (kind and kind[0] == "harness"):
            fails.append("stuck marker refusal should read harness, got %r (%s)" % (kind, why))
        why, kind = classify(doc("dev_god_mode UNMEASURED", [
            {"name": "dev_god_mode", "status": "UNMEASURED", "evidence": "no field"}]), tmp)
        if not (kind and kind[0] == "dud"):
            fails.append("plain preflight refusal should read dud, got %r (%s)" % (kind, why))
        why, _ = classify(doc("", [], [{"chain": "genome", "name": "x", "verdict": "FAIL"}]), tmp)
        if why:
            fails.append("a run that did not refuse must give no refusal, got %r" % why)
    for f in fails:
        print("FAIL", f)
    print("selftest_component_proof: %s" % ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
