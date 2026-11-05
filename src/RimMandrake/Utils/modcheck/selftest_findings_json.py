#!/usr/bin/env python3
"""Selftest for MODCHECK_FINDINGS_FIX_WRITTEN_AS_REPR: runner.write_sheet's results JSON must carry summary.findings as
{name, verdict, detail} dicts, never '<suite.Component object at 0x...>' (json.dumps(default=str) of the Component
objects runner.run appends). Offline: SHEET_DIR is a temp dir and report.render is stubbed; the in-memory summary
must still hold the Component objects file_findings reads."""
import json
import os
import shutil
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import runner  # noqa: E402
import suite  # noqa: E402

FAILS = []


def ok(cond, what, got=None):
    print(("PASS  " if cond else "FAIL  ") + what + ("" if cond or got is None else "   got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def main():
    tmp = tempfile.mkdtemp(prefix="selftest_findings_json_")
    try:
        runner.SHEET_DIR = tmp
        sys.modules["report"] = types.SimpleNamespace(render=lambda mod, summary: "<html></html>")
        gate_stub = types.SimpleNamespace(index_run=lambda *a: None, record_misses=lambda *a: [])
        sys.modules["gate"] = gate_stub
        c = suite.Component("hose_flow", "toggleHose", False)
        c.verdict, c.detail = "FAIL", "water did not move"
        summary = {"chains": [], "all_green": False, "findings": [c], "refused": ""}
        path = runner.write_sheet("ToyMod", summary)
        with open(path[:-5] + ".json", encoding="utf-8") as f:
            text = f.read()
        ok("object at 0x" not in text, "results JSON holds no '<... object at 0x' repr")
        got = json.loads(text)["summary"]["findings"]
        ok(got == [{"name": "hose_flow", "verdict": "FAIL", "detail": "water did not move"}],
           "summary.findings is a list of {name, verdict, detail}", got)
        ok(summary["findings"][0] is c, "in-memory summary still holds the Component (file_findings reads .name)")
        plain = runner.summary_for_json({"chains": [], "findings": []})
        ok(plain == {"chains": [], "findings": []}, "an empty findings list passes through unchanged", plain)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("RESULT: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
