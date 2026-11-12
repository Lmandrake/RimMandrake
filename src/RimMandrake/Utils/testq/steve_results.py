#!/usr/bin/env python3
"""steve_results.py - tally testq jobs into a markdown table with NO model. Reads testq's own files only.

  python3 steve_results.py [--since 2026-11-12T14:00:00Z] [--out PATH]

Columns: job, item, selector, state, PASS/FAIL/UNMEASURED (worst row wins; INVALID/REFUSED runs read UNMEASURED),
evidence path. Jobs are read from testq/{running,pending,done,quarantined,cancelled}/ under the testq data root.
"""
import argparse, json, os, glob

ROOT = "/mnt/d/ClaudeWork/rimmandrake/testq"
OUT = "/mnt/d/ClaudeWork/rimmandrake/conductor/steve_testq_20261112/results.md"


def verdict(res):
    if not res:
        return "-"
    rows = [r.get("verdict") for r in res.get("rows") or []]
    c = res.get("counts") or {}
    if res.get("outcome") not in (None, "DONE") or not rows and not c:
        return "UNMEASURED (%s %s)" % (res.get("outcome"), res.get("cause") or "")
    if "FAIL" in rows or c.get("FAIL"):
        return "FAIL"
    if "UNMEASURED" in rows or c.get("UNMEASURED"):
        return "UNMEASURED"
    return "PASS" if (rows or c) else "UNMEASURED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-11-12T14:00:00Z")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    lines = ["# SteveDesktop testq results (refreshed from testq files, no model)", "",
             "| job | item | selector | state | verdict | evidence |", "|---|---|---|---|---|---|"]
    n = 0
    for state in ("running", "pending", "done", "quarantined", "cancelled"):
        for f in sorted(glob.glob(os.path.join(ROOT, state, "*.json"))):
            try:
                d = json.load(open(f))
            except Exception:
                continue
            job = d.get("job") or d
            if (job.get("submitted") or "") < a.since:
                continue
            res = d.get("result")
            ev = ""
            if res:
                arts = [x.get("path") for x in res.get("artifacts") or []]
                ev = "; ".join(arts[:3]) or ("/mnt/d/RimTest/testq/attempts/%s" % res.get("attempt"))
                bad = [r for r in res.get("rows") or [] if r.get("verdict") in ("FAIL", "UNMEASURED")]
                if bad:
                    ev += " | " + "; ".join("%s/%s: %s" % (r.get("chain"), r.get("row"), str(r.get("detail"))[:90]) for r in bad[:3])
            sel = job.get("selector") or {}
            s = ",".join("%s=%s" % (k, v if not isinstance(v, list) else "+".join(map(str, v))) for k, v in sel.items())
            lines.append("| %s | %s | %s | %s | %s | %s |" % (job.get("id"), job.get("item") or job.get("mod"), s[:60], state,
                                                              verdict(res) if state == "done" else "-", ev))
            n += 1
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write("\n".join(lines) + "\n")
    print("%d jobs -> %s" % (n, a.out))


if __name__ == "__main__":
    main()
