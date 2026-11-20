#!/usr/bin/env python3
"""selftest_gravship_scene_exit.py -- gravship_scene.py writes a verdict whatever stops it (RIMMANDRAKE_GUARD_SLACK_GRAVSHIP_SCENE_EXIT_WRITES_NO_ROW).

Visit 2 (2026-11-19): prove_gravship's staging refused ("at least one colonist aboard before launch") with sys.exit(1);
SystemExit is not an Exception, so main()'s handler missed it, `rc` was unbound in `finally`, and the run wrote no row.
A staging refusal is "could not ask": UNMEASURED/HARNESS, never FAIL/MOD and never silence. Offline, no bridge.
    python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gravship_scene_exit.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gravship_scene as G  # noqa: E402

fails = []


def run(raise_with, mode="off"):
    out = os.path.join(tempfile.mkdtemp(), "r.json")
    sys.argv = ["gravship_scene.py", mode, "--out", out]

    def fake(a, det):
        if isinstance(raise_with, BaseException):
            raise raise_with
        return raise_with
    G.scene = fake
    rc = "raised"
    try:
        rc = G.main()
    except BaseException as e:  # noqa: BLE001
        rc = "raised %s" % type(e).__name__
    row = json.load(open(out))["rows"][0] if os.path.exists(out) else None
    return rc, row


for name, given, want_status, want_class in (
        ("staging refusal sys.exit(1)", SystemExit(1), "UNMEASURED", "HARNESS"),
        ("crash", RuntimeError("boom"), "UNMEASURED", "HARNESS"),
        ("pass", 0, "PASS", "MOD"),
        ("fail", 1, "FAIL", "MOD"),
        ("unmeasured", 2, "UNMEASURED", "HARNESS")):
    rc, row = run(given)
    if row is None:
        fails.append("%s: no row written (rc %r)" % (name, rc))
    elif (row["status"], row["class"]) != (want_status, want_class):
        fails.append("%s: %s/%s, want %s/%s" % (name, row["status"], row["class"], want_status, want_class))
    elif name.startswith("staging") and "staging" not in json.dumps(row["detail"]):
        fails.append("%s: the row does not say the staging refused: %s" % (name, row["detail"]))
print("\n".join(fails) if fails else "PASS (5 cases)")
sys.exit(1 if fails else 0)
