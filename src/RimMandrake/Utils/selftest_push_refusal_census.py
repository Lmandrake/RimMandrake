#!/usr/bin/env python3
"""Selftest for push_refusal_census.py: fixture transcripts with known refusals give known counts.

Guards the traps met while building it (PUSH_REFUSALS_MEASURE_BEFORE_BUYING_GITLAB, 2026-11-06): a grep of
publish.py's SOURCE prints "origin kept moving" and 'REFUSED: %s' mid-line and was counted as 8 give-ups; and
publish.py's "push failed (...); retrying" retries are not non-fast-forward rejections but cost time all the same.
"""
import datetime as dt
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import push_refusal_census as P  # noqa: E402

FAILS = []
RM = "/home/mandrake/rm/relentless/clones/SOME_ITEM"
T0 = dt.datetime(2026, 11, 3, 18, 0, tzinfo=dt.timezone.utc)


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def pair(uid, cmd, out, start_s, dur_s, cwd=RM):
    t0 = (T0 + dt.timedelta(seconds=start_s)).isoformat().replace("+00:00", "Z")
    t1 = (T0 + dt.timedelta(seconds=start_s + dur_s)).isoformat().replace("+00:00", "Z")
    use = {"type": "assistant", "cwd": cwd, "timestamp": t0, "message": {"content": [
        {"type": "tool_use", "id": uid, "name": "Bash", "input": {"command": cmd}}]}}
    res = {"type": "user", "cwd": cwd, "timestamp": t1, "message": {"content": [
        {"type": "tool_result", "tool_use_id": uid, "content": [{"type": "text", "text": out}]}]}}
    return [json.dumps(use), json.dumps(res)]


def main():
    lines = []
    lines += pair("clean1", "./publish -m 'X: a' a.py", "PUBLISHED abcdef1234", 0, 10)
    lines += pair("clean2", "./publish -m 'X: b' b.py", "PUBLISHED abcdef1235", 100, 8)
    lines += pair("clean3", "./publish -m 'X: c' c.py", "PUBLISHED abcdef1236", 200, 9)
    lines += pair("moved2", "./publish -m 'X: d' d.py",
                  "origin moved (attempt 1); rebasing and retrying\norigin moved (attempt 2); rebasing and retrying\n"
                  "PUBLISHED abcdef1237", 300, 30)
    lines += pair("gaveup", "./publish -m 'X: e' e.py",
                  "".join("origin moved (attempt %d); rebasing and retrying\n" % i for i in range(1, 9)) +
                  "REFUSED: origin kept moving: 8 non-fast-forward rejections in a row", 400, 60)
    lines += pair("srcgrep", "grep -n 'kept moving\\|REFUSED' src/RimMandrake/Utils/publish.py",
                  '566:    raise Refuse("origin kept moving: %d non-fast-forward rejections in a row" % MAX_TRIES)\n'
                  '609:        print("REFUSED: %s" % e, file=sys.stderr)', 500, 1)
    lines += pair("pusherr", "./publish -m 'X: f' f.py",
                  "push failed (error: failed to push some refs to 'github.com:x/y.git'); retrying\n"
                  "PUBLISHED abcdef1238", 600, 12)
    lines += pair("conflict", "./publish -m 'X: g' g.py",
                  "REFUSED: replaying 1234567 onto origin/main stopped on a conflict in: a.jsonl. Your commit is "
                  "intact", 700, 5)
    lines += pair("landsh", "sh src/RimMandrake/Utils/land.sh -m m p",
                  "land.sh: origin moved during the push; rebuilding on the new tip (try 2)\nPUBLISHED abcdef1239",
                  800, 11)
    lines += pair("raw", "git push origin main",
                  " ! [rejected]        main -> main (fetch first)\nerror: failed to push some refs to 'x'", 900, 2)
    lines += pair("noop", "./publish", "REFUSED: nothing to publish: HEAD is already on origin/main", 1000, 3)
    lines += pair("test", "python3 src/RimMandrake/Utils/run_selftests.py --only selftest_publish",
                  "origin moved (attempt 1); rebasing and retrying\nPUBLISHED abcdef1240", 1100, 4)
    lines += pair("elsewhere", "./publish -m x y", "origin moved (attempt 1); rebasing and retrying\nPUBLISHED 1234567",
                  1200, 20, cwd="/home/mandrake/dev/Lodestar")
    lines += pair("old", "./publish -m x y", "origin moved (attempt 1); rebasing and retrying\nPUBLISHED 1234567",
                  -30 * 86400, 20)
    lines += pair("pubtest", "./publish -m 'X: t' src/RimMandrake/Utils/selftest_foo.py",
                  "origin moved (attempt 1); rebasing and retrying\nPUBLISHED abcdef1241", 1300, 15)
    lines += pair("bare", "./publish -m 'X: h' h.py", "push failed\nPUBLISHED abcdef1242", 1400, 11)
    lines += pair("submit", "./publish --submit -m 'X: i' i.py",
                  "REFUSED: refs/submit/x already holds a submission this one does not contain — not forcing", 1500, 4)
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "proj", "s1", "subagents"))
        a = os.path.join(d, "proj", "s1.jsonl")
        with open(a, "w") as f:
            f.write("\n".join(lines) + "\n")
        b = os.path.join(d, "proj", "s1", "subagents", "agent-1.jsonl")   # a resumed copy: same ids, once
        with open(b, "w") as f:
            f.write("\n".join(lines[:4]) + "\n")
        since, until = T0 - dt.timedelta(days=7), T0 + dt.timedelta(days=1)
        rows = P.scan([a, b], since, until)
        by = {r["id"]: r for r in rows}
        check(set(by) == {"clean1", "clean2", "clean3", "moved2", "gaveup", "pusherr", "conflict", "landsh", "raw",
                          "noop", "pubtest", "bare", "submit"}, "kept exactly the RimMandrake landing calls in the window: %s" % sorted(by))
        check("srcgrep" not in by, "a grep of publish.py's source is no landing and no give-up")
        check(by["moved2"]["rejections"] == 2 and by["moved2"]["outcome"] == "landed", "two rejections, then landed")
        check(by["gaveup"]["gaveup"] and by["gaveup"]["rejections"] == 8, "gave up after 8 rejections")
        check(by["pusherr"]["retried_errors"] == 1 and by["pusherr"]["rejections"] == 0,
              "a push-error retry is counted apart from non-fast-forward")
        check(by["conflict"]["outcome"] == "origin: rebase conflict", "rebase conflict classified")
        check(by["landsh"]["rejections"] == 1, "land.sh retry line counted")
        check(by["raw"]["rejections"] == 1 and by["raw"]["outcome"] == "origin: raw git push rejected",
              "raw git push rejection counted")
        check(by["noop"]["outcome"].startswith("no-op") and not by["noop"]["rejections"], "nothing-to-publish is no refusal")
        check(by["pubtest"]["rejections"] == 1, "publishing a selftest FILE is a landing, not a test run")
        check(by["bare"]["retried_errors"] == 1, "a bare 'push failed' retry is counted")
        check(by["submit"]["outcome"].startswith("origin: submit") and by["submit"]["rejections"] == 1,
              "a submit-ref refusal is an origin refusal")
        check(by["clean1"]["writer"] == "relentless worker", "writer from cwd: %s" % by["clean1"]["writer"])
        base, n = P.lost(rows)
        check(n == 3 and base == 9.0, "median clean landing is 9.0 s over 3 (got %s over %d)" % (base, n))
        check(by["moved2"]["lost"] == 21.0 and by["gaveup"]["lost"] == 60.0 and by["pusherr"]["lost"] == 3.0
              and by["bare"]["lost"] == 2.0,
              "time lost: excess over the median, whole call when it gave up")
        rep = P.report(rows, since, until, 2, base, n, [], None)
        check("(8 days)" in rep, "header names the real window length")
        for sec in ("## Time lost", "## Per day", "## Per writer", "## Outcomes"):
            check(sec in rep, "report has %s" % sec)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
