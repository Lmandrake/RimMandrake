#!/usr/bin/env python3
"""Proof for ARTPIPE_DONE_RECORDS_AUDIT_LOST_PNG: every one of the 31 done/failed twins whose _artsrc PNG was lost
has exactly one recorded decision, and the record's claims about the tree at HEAD hold.

Reads only the working tree (no git: the blind checker's export has no .git). Checks: 31 jobs, one decision each from
{installed, installed_then_refit, superseded, purged, requeue}, counts 6/14/8/2/1, every job with a reason;
`installed`: every path the job went to holds bytes hashing to the job's sha now; `installed_then_refit`: every path
holds the recorded sha_at_head, any path that differs from the job's sha names the refit commit, and at least one does;
the `requeue` job's gate fix (HAR alienRace/graphicPaths reading) is present in regen_eligibility.py.
Exit 0 = holds, 1 = does not."""
import hashlib, json, sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
REC = Path(__file__).with_name("ARTPIPE_DONE_RECORDS_AUDIT_LOST_PNG.json")
WANT = {"installed": 6, "installed_then_refit": 14, "superseded": 8, "purged": 2, "requeue": 1}
GATE = REPO / "src/RimMandrake/Utils/art/regen_eligibility.py"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "MISSING"


def main() -> int:
    rec = json.loads(REC.read_text())
    jobs, errs = rec["jobs"], []
    got = Counter(j["decision"] for j in jobs.values())
    if len(jobs) != 31 or dict(got) != WANT:
        errs.append(f"decisions {dict(got)} over {len(jobs)} jobs, want {WANT} over 31")
    for k, j in jobs.items():
        if not j.get("why"):
            errs.append(f"{k}: no reason")
        if j["decision"] not in ("installed", "installed_then_refit"):
            continue
        rows = [(v["sha"], e) for v in j["variants"] for e in v.get("repo_at_head", [])]
        if not rows:
            errs.append(f"{k}: {j['decision']} but names no src texture")
        refits = 0
        for job_sha, e in rows:
            now = sha(REPO / e["path"])
            if j["decision"] == "installed":
                if now != job_sha:
                    errs.append(f"{k}: {e['path']} at HEAD is {now[:12]}, not job sha {job_sha[:12]}")
                continue
            if now != e["sha_at_head"]:
                errs.append(f"{k}: {e['path']} at HEAD is {now[:12]}, record says {e['sha_at_head'][:12]}")
            if now != job_sha:
                refits += 1
                if not e.get("refit_commit"):
                    errs.append(f"{k}: {e['path']} differs from the job sha but names no refit commit")
        if j["decision"] == "installed_then_refit" and not refits:
            errs.append(f"{k}: installed_then_refit but every path still holds the job sha")
    if "alienRace/graphicPaths" not in (GATE.read_text() if GATE.is_file() else ""):
        errs.append(f"gate fix (HAR graphicPaths) absent from {GATE.relative_to(REPO)}")
    for e in errs:
        print("FAIL", e)
    print(f"{'FAIL' if errs else 'PASS'}: {len(jobs)} jobs {dict(got)}; {len(errs)} problem(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
