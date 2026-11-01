"""selftest_apply_blanket_ruling.py -- a blanket ruling never flattens a sitting, whatever stamp the sitting left.

The guard used to allow-list three sitting stamps; decisions_v2 --accept-looks stamps "decisions_v2 --accept-looks
(owner's words)" over per-row owner picks and was let through (wave 76). Runs the CLI on temp files: every sitting
stamp (and a bare writeCount) refuses and leaves the file untouched; an unstamped pre-fill and a previous blanket
ruling are replaced; --over-sitting still overrides."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "apply_blanket_ruling.py")
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def run(tmp, doc, *extra):
    sheet, dec = os.path.join(tmp, "s.html"), os.path.join(tmp, "d.json")
    with open(sheet, "w", encoding="utf-8") as fh:
        fh.write('<script id="ITEMS" type="application/json">[{"id": "r1"}, {"id": "r2"}]</script>')
    raw = json.dumps(doc)
    with open(dec, "w", encoding="utf-8") as fh:
        fh.write(raw)
    p = subprocess.run([sys.executable, TOOL, "--decisions", dec, "--sheet", sheet, "--decision", "replace",
                        "--said", "replace everything", "--apply", *extra], capture_output=True, text=True)
    with open(dec, encoding="utf-8") as fh:
        after = fh.read()
    return p.returncode, after != raw, json.loads(after), p.stderr


def main():
    sat = {"decisions": {"r1": {"decision": "keep", "by": "owner"}}}
    with tempfile.TemporaryDirectory() as tmp:
        for stamp in ("review-sheet-sidecar", "review-sheet-page", "artifact-db-merge",
                      "decisions_v2 --accept-looks (owner's words)", "some-future-sitting-route"):
            rc, changed, _, _ = run(tmp, dict(sat, savedBy=stamp))
            check("refuses over a sitting stamped %r" % stamp, rc != 0 and not changed, (rc, changed))
        rc, changed, _, err = run(tmp, dict(sat, writeCount=3))
        check("refuses over a writeCount with no stamp, naming the writeCount (not 'None')",
              rc != 0 and not changed and "3 time(s)" in err and "None" not in err, (rc, changed, err))
        rc, changed, d, _ = run(tmp, {"decisions": {"r1": {"decision": "keep"}}})
        check("replaces an unstamped pre-fill on every sheet row",
              rc == 0 and changed and sorted(d["decisions"]) == ["r1", "r2"] and d["savedBy"] == "owner-blanket-ruling",
              (rc, d.get("savedBy")))
        rc, changed, d, _ = run(tmp, dict(sat, savedBy="owner-blanket-ruling", writeCount=5))
        check("replaces a previous blanket ruling", rc == 0 and changed, rc)
        rc, changed, d, _ = run(tmp, dict(sat, savedBy="decisions_v2 --accept-looks (owner's words)"), "--over-sitting")
        check("--over-sitting still overrides", rc == 0 and changed, rc)
    print("RESULT", "FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
