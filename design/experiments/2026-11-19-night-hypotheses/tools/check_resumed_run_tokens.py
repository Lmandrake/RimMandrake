#!/usr/bin/env python3
"""Acceptance check for RIMMANDRAKE_COUNT_RESUMED_RUN_TOKENS_ONCE_SESSION_TOTAL_LOGGED. Read-only.

A run that resumes a claude session gets a result JSON whose modelUsage is the WHOLE session so far. This check
reads the detached run records, groups runs by session, and asserts that each resumed run's recorded `tokens` is
its own part: no more than (this result's session total) - (the largest session total an earlier run of the same
session reported), with 2% + 2,000 slack.

    check_resumed_run_tokens.py <repo_root> <detached_records_dir> [--since <ISO time or epoch seconds, compared with the record's 'ended'>]
        [--until <same>]

It also prints one SUMS line over the window: the recorded tokens of every run, and the same with each resumed run
counted at its own part (the corrected sum).

Exit 0  PASS: at least one resumed run was checked and every one holds its own part only.
Exit 1  FAIL: at least one resumed run's recorded tokens include an earlier run's.
Exit 3  COULD NOT LOOK: the folder or the price table is unreadable.
Exit 4  EMPTY: no resumed run with a readable record and result in the window (not a pass).
"""
import glob, json, os, sys
from datetime import datetime


def when(s):
    if isinstance(s, (int, float)) and not isinstance(s, bool):
        return float(s)                 # a run record's `ended` is epoch seconds
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def main(a):
    if len(a) < 3:
        print(__doc__)
        return 2
    repo, folder = a[1], a[2]
    raw = a[a.index("--since") + 1] if "--since" in a else 0
    since = when(float(raw) if str(raw).replace(".", "", 1).isdigit() else raw)
    raw_u = a[a.index("--until") + 1] if "--until" in a else "9999999999999"
    until = when(float(raw_u) if str(raw_u).replace(".", "", 1).isdigit() else raw_u)
    if since is None or until is None:
        print("VERDICT COULD-NOT-LOOK: --since %r / --until %r is not a time" % (raw, raw_u))
        return 3
    try:
        sys.path.insert(0, os.path.join(repo, "src", "RimMandrake", "rimflow"))
        import role_launch as RL
        recs = [p for p in glob.glob(os.path.join(folder, "*.json")) if not p.endswith(".out.json")]
        if not os.path.isdir(folder):
            raise OSError("not a folder: %s" % folder)
    except Exception as e:
        print("VERDICT COULD-NOT-LOOK: %r" % (e,))
        return 3
    by, unread = {}, 0
    for p in recs:
        try:
            rec = json.load(open(p))
            res = json.load(open(rec["out"]))
            sid, total = res["session_id"], RL.run_tokens(res, rec.get("model"))
            end = when(rec.get("ended"))
        except Exception:
            unread += 1
            continue
        if total is None or end is None or not isinstance(rec.get("tokens"), int):
            unread += 1
            continue
        by.setdefault(sid, []).append((end, rec["tokens"], total, bool(rec.get("resume_session")), rec.get("unit")))
    checked, bad, logged, fixed = 0, [], 0, 0
    for sid, runs in by.items():
        runs.sort()
        prev = 0
        for end, tokens, total, resumed, unit in runs:
            inside = since <= end < until
            logged += tokens if inside else 0
            fixed += (min(tokens, total - prev) if resumed and prev else tokens) if inside else 0
            if resumed and prev and inside:
                checked += 1
                own = total - prev
                if tokens > own * 1.02 + 2000:
                    bad.append((unit, tokens, own))
            prev = max(prev, total)
    print("SUMS recorded %d weighted tokens; each resumed run at its own part %d; over-count %d "
          "(runs with a readable record and result only)" % (logged, fixed, logged - fixed))
    if bad:
        for unit, tokens, own in bad[:40]:
            print("  FAIL %s recorded %d, own part %d" % (unit, tokens, own))
        print("VERDICT FAIL: %d of %d resumed runs record more than their own part; overstated by %d weighted tokens "
              "(%d records unreadable or without a result)" % (len(bad), checked, sum(t - o for _, t, o in bad), unread))
        return 1
    if not checked:
        print("VERDICT EMPTY: no resumed run with an earlier run of its session in the window "
              "(%d records unreadable or without a result)" % unread)
        return 4
    print("VERDICT PASS: %d resumed runs, each records its own part only (%d records unreadable or without a result)"
          % (checked, unread))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
