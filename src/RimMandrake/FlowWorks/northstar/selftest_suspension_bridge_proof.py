"""The suspension bridge functional script runs every path offline (suspension_bridge_proof.py --mock, FakeBridge): each
section's rows are written and every mock verdict is PASS except rows marked owed. Can-fail: a FakeBridge answering a
refusal for the length row makes it FAIL. Proves the SCRIPT, never the game (live rows stay owed to FOUNDRY).

    python3 src/RimMandrake/FlowWorks/northstar/selftest_suspension_bridge_proof.py
"""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import suspension_bridge_proof as SBP  # noqa: E402


def run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = SBP.main(argv)
    return rc, buf.getvalue()


def main():
    fails = []
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "mock.json")
        rc, txt = run(["--mock", out])
        rows = json.load(open(out, encoding="utf-8"))["rows"]
        if rc != 0:
            fails.append("mock run exit %s: %s" % (rc, txt.strip().splitlines()[-1]))
        ids = [r["id"] for r in rows]
        for sec in SBP.SECTIONS:
            if not any(("== section %s" % sec) in line for line in txt.splitlines()):
                fails.append("section %s never ran" % sec)
        if any(r["status"] != "SKIP" for r in rows):
            fails.append("a mock row claimed a live verdict")
        if len(ids) != len(set(ids)):
            fails.append("duplicate row ids")
        # can-fail: a refusal where the build must pass turns the first row's mock verdict to FAIL
        orig = SBP.FakeBridge.static
        SBP.FakeBridge.static = lambda self, m, a: ("BUILD ok=False anchors=0 decks=0 blueprints=0 reason=x" if m == "ProofBuild"
                                                    else orig(self, m, a))
        try:
            rc2, _ = run(["--mock", os.path.join(d, "bad.json"), "--only", "posts"])
        finally:
            SBP.FakeBridge.static = orig
        if rc2 == 0:
            fails.append("can-fail BROKEN: a refused build still passed the mock")
    for f in fails:
        print("FAIL " + f)
    print("suspension bridge proof mock: %d rows, %d sections, %s" % (len(ids), len(SBP.SECTIONS), "ok" if not fails else "FAIL"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
