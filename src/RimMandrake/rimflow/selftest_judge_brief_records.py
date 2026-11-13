#!/usr/bin/env python3
"""selftest_judge_brief_records.py - the agent-launched judge briefs emit refusal records the contract accepts
(RIMMANDRAKE_EMIT_REFUSAL_RECORDS_FROM_JUDGE_BRIEFS, T4). art_judge_brief.md and scene_look_judge_brief.md are read by a
judge agent a window launches, so their launcher is the window running `refusal_contract.py submit`: this test runs that
command on each brief's own `contract` example (it must be well formed, or the brief teaches every judge to be refused)
and on a broken copy of it (it must be refused, exit 1). No model, no network; the contract store is a temp dir."""
import copy
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import refusal_contract as RC  # noqa: E402

BRIEFS = {"art_judge_brief": ("design/RimMandrake/art_judge_brief.md",
                              {"C1": "North is the creature's rear (no face, no eyes)",
                               "D1": "the sprite fills its canvas at the def's drawSize"}),
          "scene_look_judge_brief": ("design/RimMandrake/scene_look_judge_brief.md",
                                     {"B2": "the west reel sits on the rim, cover-line above the water",
                                      "B3": "the east reel is drawn whole above the water surface"})}
FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def example(text):
    """-> the brief's ```json block that holds a `contract`, parsed."""
    for block in re.findall(r"```json\n(.*?)```", text, re.S):
        try:
            obj = json.loads(block)
        except ValueError:
            continue
        if isinstance(obj, dict) and "contract" in obj:
            return obj
    return None


def submit(root, name, obj, given):
    vf, gf = os.path.join(root, name + ".json"), os.path.join(root, name + ".given.json")
    with open(vf, "w") as f:
        json.dump(obj, f)
    with open(gf, "w") as f:
        json.dump(given, f)
    env = dict(os.environ, RM_REFUSAL_DIR=os.path.join(root, "store"), RM_OPS_WATCH_DIR=os.path.join(root, "ops"),
               RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
    p = subprocess.run([sys.executable, os.path.join(HERE, "refusal_contract.py"), "submit", vf, "--given", gf],
                       capture_output=True, text=True, env=env, timeout=60)
    return p.returncode, p.stdout + p.stderr


def main():
    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, "ops"))
        for fam, (rel, crit) in BRIEFS.items():
            text = open(os.path.join(REPO, rel), encoding="utf-8").read()
            check("%s names every record field and the submit command" % fam,
                  all(f in text for f in RC.FIELDS) and "refusal_contract.py submit" in text)
            ex = example(text)
            check("%s carries a contract example" % fam, ex is not None)
            if ex is None:
                continue
            c = ex["contract"]
            check("%s's example is family %s" % (fam, fam), c.get("family") == fam, c.get("family"))
            refs = sorted({e for r in c["refusals"] + c["passed"] for e in r["evidence"]})
            given = {"inputs": refs, "criteria": crit}
            good = copy.deepcopy(ex)
            for r in good["contract"]["refusals"]:   # the example holds a placeholder hash; the window computes it
                r["criterion_hash"] = RC.criterion_hash(crit[r["clause"]])
            rc, out = submit(root, fam + "_good", good, given)
            check("%s: the brief's own example is accepted by refusal_contract.py submit" % fam, rc == 0, out[-600:])
            bad = copy.deepcopy(good)
            bad["contract"]["refusals"][0].update(would_pass="does not pass",
                                                  smallest_fix={"what": "needs more work", "attainable": "yes",
                                                                "cost": "edit"})
            rc, out = submit(root, fam + "_bad", bad, given)
            check("%s: a refusal with no path to pass is refused (exit 1, named)" % fam,
                  rc == 1 and "would_pass says nothing checkable" in out, out[-600:])
            nofix = copy.deepcopy(good)
            del nofix["contract"]["refusals"][0]["criterion_verdict"]
            rc, out = submit(root, fam + "_nocrit", nofix, given)
            check("%s: a refusal that does not judge its criterion is refused" % fam,
                  rc == 1 and "criterion_verdict is missing" in out, out[-600:])
    print("selftest_judge_brief_records: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
