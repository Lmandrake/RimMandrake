#!/usr/bin/env python3
"""selftest_saves_prune.py — pins saves_prune.py's delete gate on a scratch Saves folder (never the real one).

  1. a cited save is KEEP and an uncited old debug save is PRUNE (citation search stubbed: one hit);
  2. --apply deletes the PRUNE row only, never the cited one or a CANONICAL_* save;
  3. a citation search that fails to run (exit 128) makes --apply REFUSE (rc 2) and delete nothing —
     before 2026-10-26 a blind search read as "cited nowhere" and every cited save became PRUNE.
"""
import io
import os
import subprocess
import sys
import tempfile
import time
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import saves_prune as sp  # noqa: E402

CITED, UNCITED, CANON = "RM_SelftestCitedSave.rws", "zz_selftest_uncited_debug.rws", "CANONICAL_SELFTEST_X.rws"


def fake_run(hit: bool, rc: int):
    def run(cmd, **kw):
        out = ""
        if hit and cmd[0] == "git":
            out = "design/x.md:%s\n" % CITED[:-4]
        return subprocess.CompletedProcess(cmd, rc, stdout=out, stderr="fatal: stub" if rc > 1 else "")
    return run


def go(folder: Path, run, argv):
    sp.CITE_ERRORS.clear()
    sp.subprocess.run = run
    os.environ["SAVES_PRUNE_DIR"] = str(folder)
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = sp.main(argv)
    return rc, buf.getvalue(), sorted(os.listdir(folder))


def main() -> int:
    real = subprocess.run
    fails = []
    try:
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            old = time.time() - 10 * 86400
            for n in (CITED, UNCITED, CANON):
                (d / n).write_bytes(b"x")
                os.utime(d / n, (old, old))
            rc, out, _ = go(d, fake_run(True, 0), [])
            if "KEEP" not in next((l for l in out.splitlines() if CITED in l), "") or \
                    "PRUNE" not in next((l for l in out.splitlines() if UNCITED in l), ""):
                fails.append("dry run verdicts wrong:\n" + out)
            rc, out, left = go(d, fake_run(False, 128), ["--apply"])
            if rc != 2 or "REFUSED" not in out or left != sorted([CITED, UNCITED, CANON]):
                fails.append("blind search did not refuse --apply (rc=%s, left=%s)" % (rc, left))
            rc, out, left = go(d, fake_run(True, 0), ["--apply"])
            if rc != 0 or left != sorted([CITED, CANON]):
                fails.append("--apply deleted the wrong set (rc=%s, left=%s)" % (rc, left))
    finally:
        sp.subprocess.run = real
    for f in fails:
        print("FAIL:", f)
    print("selftest_saves_prune: %s" % ("FAIL" if fails else "OK (3/3)"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
