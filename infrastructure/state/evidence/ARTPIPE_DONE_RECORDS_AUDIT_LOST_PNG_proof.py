#!/usr/bin/env python3
"""Proof for ARTPIPE_DONE_RECORDS_AUDIT_LOST_PNG: every one of the 31 done/failed twins whose _artsrc PNG was lost
has exactly one recorded decision, and the record's claims that git can check hold.

Checks (offline, git only): 31 jobs, decisions in {installed, superseded, purged, requeue}, counts 20/8/2/1; every
`installed` job names a src texture whose bytes at the audit commit hash to the recorded sha; the one `requeue` job's
gate fix commit is an ancestor of HEAD. Exit 0 = holds, 1 = does not."""
import hashlib, json, subprocess, sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
REC = Path(__file__).with_name("ARTPIPE_DONE_RECORDS_AUDIT_LOST_PNG.json")
WANT = {"installed": 20, "superseded": 8, "purged": 2, "requeue": 1}


def git(*a, text=True):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=text)


def main() -> int:
    rec = json.loads(REC.read_text())
    jobs, errs = rec["jobs"], []
    got = Counter(j["decision"] for j in jobs.values())
    if len(jobs) != 31 or dict(got) != WANT:
        errs.append(f"decisions {dict(got)} over {len(jobs)} jobs, want {WANT} over 31")
    for k, j in jobs.items():
        if not j.get("why"):
            errs.append(f"{k}: no reason")
        if j["decision"] != "installed":
            continue
        paths = [(v["sha"], r) for v in j["variants"] for r in v["repo_at_audit"]]
        if not paths:
            errs.append(f"{k}: installed but names no src texture")
        for sha, r in paths:
            b = git("show", f"{rec['audit_commit']}:{r}", text=False)
            if b.returncode or hashlib.sha256(b.stdout).hexdigest() != sha:
                errs.append(f"{k}: {r} at {rec['audit_commit'][:12]} is not sha {sha[:12]}")
    if git("merge-base", "--is-ancestor", rec["gate_fix_commit"], "HEAD").returncode:
        errs.append(f"gate fix {rec['gate_fix_commit'][:12]} is not an ancestor of HEAD")
    for e in errs:
        print("FAIL", e)
    print(f"{'FAIL' if errs else 'PASS'}: {len(jobs)} jobs {dict(got)}; {len(errs)} problem(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
