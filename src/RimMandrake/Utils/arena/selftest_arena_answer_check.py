#!/usr/bin/env python3
"""selftest_arena_answer_check: the plain answer-store check (arena_answer_check.py) passes on the real sandbox and
FAILS when the sandbox stops masking /home and /mnt (proof the instrument can see a readable store).
G1-G7 (ARENA_ANSWER_CHECK_FIX_STALE_ROWS_UNGATED): freeze refuses with no record, a stale one (census after the
check), a FAIL/VOID row or an unmeasured judge-hidden row, and opens on a current passing record."""
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_answer_check as AC  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def gate_cases():
    tmp = Path(tempfile.mkdtemp(prefix="selftest_answer_gate_"))
    old = os.environ.get("ARENA_ROOT")
    os.environ["ARENA_ROOT"] = str(tmp)
    try:
        import arena_tasks as AT
        p = AT.paths()
        p["tasks"].mkdir(parents=True)
        p["judge"].mkdir(parents=True)
        (p["tasks"] / "T1.json").write_text('{"id": "T1"}')
        (p["judge"] / "T1.json").write_text('{"task": "T1"}')

        def rows(**over):
            out = [{"store": s, "what": w, "path": x, "result": over.get(w, "PASS")} for s, w, x in AC.targets()]
            return out

        hid = [r for r in rows() if r["what"] == "judge hidden checks"]
        check(len(hid) == 1 and hid[0]["path"] == str(p["judge"] / "T1.json"),
              "G7 the judge-hidden row reads the census's judge dir (%s)" % (hid[0]["path"] if hid else None))
        g = AC.gate(p)
        check(g and "no answer check" in g[0], "G1 no record -> refuse (%s)" % g[:1])
        AC.record(rows(), True, p)
        check(AC.gate(p) == [], "G2 current passing record -> gate open (%s)" % AC.gate(p))
        AC.record(rows(**{"freeze authority": "UNMEASURED"}), True, p)
        check(AC.gate(p) == [], "G4 an UNMEASURED row other than judge-hidden does not refuse")
        AC.record(rows(**{"judge hidden checks": "UNMEASURED"}), True, p)
        check(any("judge hidden checks" in x for x in AC.gate(p)), "G4 judge-hidden UNMEASURED -> refuse")
        AC.record(rows(**{"ledger shards": "FAIL"}), True, p)
        check(any("FAIL" in x for x in AC.gate(p)), "G5 a FAIL row -> refuse")
        AC.record(rows(), False, p)
        check(any("VOID" in x for x in AC.gate(p)), "G5 control unreadable -> refuse")
        AC.record(rows(), True, p)
        (p["judge"] / "T1.json").write_text('{"task": "T1", "changed": 1}')     # a census after the check
        check(any("STALE" in x for x in AC.gate(p)), "G3 census after the check -> STALE, refuse")
        AC.record(rows(), True, p)
        sb = tmp / "fake_sandbox.py"
        sb.write_text("x = 1\n")
        old_files = AC.SANDBOX_FILES
        AC.SANDBOX_FILES = old_files + (str(sb),)
        try:
            check(any("sandbox code" in x for x in AC.gate(p)), "G8 sandbox file set changed -> STALE")
            AC.record(rows(), True, p)
            check(AC.gate(p) == [], "G8 sanity: re-recorded -> open")
            sb.write_text("x = 2\n")                 # sandbox code edited after the check
            check(any("STALE" in x and "sandbox code" in x for x in AC.gate(p)), "G8 sandbox code edited -> STALE, refuse")
        finally:
            AC.SANDBOX_FILES = old_files
        (p["judge"] / "T1.json").write_text('{"task": "T1", "changed": 2}')
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = AT.main(["freeze"])
        check(rc == 1 and "answer check is not current" in buf.getvalue() and not p["freeze"].exists(),
              "G6 `arena_tasks.py freeze` refuses on the stale record, nothing frozen (rc %s)" % rc)
        AC.record(rows(), True, p)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                AT.main(["freeze"])
            except BaseException:                    # noqa: BLE001 - the fake task is refused later; only the gate matters
                pass
        check("answer check is not current" not in buf.getvalue(), "G6 sanity: a current record passes the gate")
        doc = json.loads(AC.record_path(p).read_text())
        check(doc["schema"] == AC.SCHEMA and doc["fingerprint"] == AC.fingerprint(p), "record carries its fingerprint")
    finally:
        if old is None:
            os.environ.pop("ARENA_ROOT", None)
        else:
            os.environ["ARENA_ROOT"] = old
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    gate_cases()
    rows, ctl = AC.run()
    check(ctl, "control file in the arm scratch is readable inside the sandbox")
    bad = [r["what"] for r in rows if r["result"] in ("FAIL", "VOID")]
    check(not bad, "no answer store readable from inside the arm sandbox (%s)" % bad)
    must = {"arena harness event token", "live clone foundry"}
    measured = {r["what"] for r in rows if r["result"] == "PASS"}
    check(must <= measured, "token and live clone are measured, not skipped (%s)" % sorted(must - measured))
    rows, ctl = AC.run(_drop=("/home", "/mnt"))
    leaked = {r["what"] for r in rows if r["result"] == "FAIL"}
    check(ctl and must <= leaked, "mutation: /home and /mnt unmasked -> the check FAILS on them (%s)" % sorted(leaked))
    check("D:\\ mirror" in leaked or not Path("/mnt/d/Luke/dev/RimMandrake/CLAUDE.md").exists(),
          "mutation: the D:\\ mirror row turns FAIL too")
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
