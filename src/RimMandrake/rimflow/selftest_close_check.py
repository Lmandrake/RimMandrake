#!/usr/bin/env python3
"""Selftest of close_check.py: one test for each promise of design/specs/2026-11-23-close-check/boundary.md. A throwaway
git repo and a fake ledger; no network, no real ledger write."""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("RM_CLOSE_CHECK_SRC") or HERE)       # the mutation run points at a copy
sys.path.append(HERE)
import close_check as CC  # noqa: E402

FAILS = []
X = {}
NOW = 1795500000.0      # 2026-11-24T06:00:00Z


def chk(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def git(*a):
    r = subprocess.run(["git", "-C", X["repo"], "-c", "user.name=t", "-c", "user.email=t@t"] + list(a),
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def commit(msg, *paths):
    for p in paths:
        f = os.path.join(X["repo"], p)
        os.makedirs(os.path.dirname(f), exist_ok=True)
        with open(f, "a") as fh:
            fh.write(msg + "\n")
        git("add", "--", p)
    git("commit", "-q", "-m", msg)
    return git("rev-parse", "HEAD")


def close(iid, sha=None, t=NOW - 3600, **kw):
    e = {"event": "close", "id": iid, "seat": "BENCH", "ts": iso(t)}
    if sha is not None:
        e["sha"] = sha
    e.update(kw)
    return e


def check(events, states=None, since=0.0):
    ids = {e["id"] for e in events if e.get("event") == "close"}
    st = dict({i: "done" for i in ids}, **(states or {}))
    return CC.check(events, st, since, NOW, CC.Commits(X["repo"]))


def flags(res, iid):
    return sorted(f for r in res["substance"] + res["form"] if r["item"] == iid for f in r["flags"])


def t_a_code_close_whose_sha_is_not_on_main_is_substance():
    res = check([close("GOOD", X["good"]), close("SHORT", X["good"][:10]), close("GONE", "deadbeef" * 5),
                 close("LIT", "HEAD"), close("NONE"), close("EMPTY", " "), close("TINY", X["good"][:4])])
    chk(flags(res, "GOOD") == [] and flags(res, "SHORT") == [], "a sha on main is clean, full or as a prefix")
    chk(flags(res, "GONE") == ["sha_not_on_main"], "a sha no commit on main has")
    chk(flags(res, "LIT") == ["sha_missing"] and flags(res, "NONE") == ["sha_missing"] and
        flags(res, "EMPTY") == ["sha_missing"], "HEAD, no sha and a blank sha are missing")
    chk(flags(res, "TINY") == ["sha_not_on_main"], "4 characters name no commit")
    chk({r["item"] for r in res["substance"]} == {"GONE", "LIT", "NONE", "EMPTY", "TINY"} and not res["form"],
        "these are substance, never form")
    chk(res["closes"] == 7 and res["code"] == 7, "the counts are the closes it looked at")


def t_a_code_close_that_touches_only_the_ledger_is_substance():
    res = check([close("L", X["ledger"]), close("M", X["mixed"])])
    chk(flags(res, "L") == ["sha_only_ledger"] and res["substance"][0]["item"] == "L", "a ledger-only commit is no work")
    chk(flags(res, "M") == [], "one other path makes it clean")


def t_a_no_code_close_is_counted_and_its_sha_is_not_checked():
    res = check([close("N", "deadbeef" * 5, noCode="told him at 5:57 PM"), close("N2", X["ledger"], noCode="x")])
    chk(res["substance"] == [] and res["no_code"] == 2 and res["code"] == 0, "no sha finding on a no-code close")


def t_missing_evidence_and_missing_named_source_are_form():
    here = os.path.join(X["top"], "proof.txt")
    with open(here, "w") as f:
        f.write("x")
    v = {"event": "verify", "seat": "BENCH", "ts": iso(NOW - 4000), "result": "pass"}
    evs = [close("EV", X["good"]), dict(v, id="EV", evidence="/home/nobody_here/gone.txt"),
           close("EVOK", X["good"]), dict(v, id="EVOK", evidence=here),
           close("TRANS", X["good"]), dict(v, id="TRANS", evidence="/home/x/Transient/a.txt"),
           close("SRC", X["good"], why="built src/never.py"),
           close("SRCOK", X["good"], why="built src/a.py"),
           close("NAMED_ITEM", X["good"], why="built src/other.py")]
    res = check(evs)
    chk(flags(res, "EV") == ["evidence_gone"] and flags(res, "EVOK") == [], "a gone evidence file, and one that is there")
    chk(flags(res, "TRANS") == [], "a Transient path is not on this disk by design")
    chk(flags(res, "SRC") == ["named_source_not_in_commits"] and flags(res, "SRCOK") == [], "named source in the commit or not")
    chk(flags(res, "NAMED_ITEM") == [], "named source in another commit that names the item")
    chk(res["substance"] == [], "form is never substance")


def t_only_the_newest_close_of_an_item_that_is_done_is_checked():
    bad = "deadbeef" * 5
    res = check([close("REOPENED", bad), close("DROPPED", bad), close("TWICE", bad, t=NOW - 9000),
                 close("TWICE", X["good"], t=NOW - 60), close("LATER_BAD", X["good"], t=NOW - 9000),
                 close("LATER_BAD", bad, t=NOW - 60)], {"REOPENED": "ready", "DROPPED": "dropped"})
    chk({r["item"] for r in res["substance"]} == {"LATER_BAD"}, "only a done item's newest close")
    chk(res["closes"] == 2, "skipped items are not counted as checked")


def t_the_window_starts_before_the_last_reading_and_never_after_it():
    chk(CC.window_start(None) == CC._epoch(CC.START), "no reading: START")
    old = NOW - 400 * 86400
    chk(CC.window_start({"until": iso(old)}) == old - CC.OVERLAP_S, "an old reading is never clamped")
    bad = "deadbeef" * 5
    res = check([close("IN", bad, t=1000.0), close("OUT", bad, t=999.0)], since=1000.0)
    chk({r["item"] for r in res["substance"]} == {"IN"}, "the window's edge")


def _run(events, argv, fail=0, git_dir=None):
    calls = []

    def reopen(iid, sha, flags, reading):
        calls.append((iid, sha, tuple(flags)))
        return fail, "refused: " + "x" * 600 + " repair the same item (reopen refused)" if fail else "ok"
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        rc = CC.main(argv, fx={"events": lambda: events, "reopen": reopen, "now": NOW, "repo": git_dir or X["repo"],
                               "states": lambda evs: {e["id"]: "done" for e in evs if e.get("event") == "close"},
                               "unearned": lambda evs, since: {"unearned": 1, "of": 4}})
    return rc, calls, out.getvalue()


def t_substance_reopens_the_same_item_once_and_a_dry_run_writes_nothing():
    p = os.path.join(X["top"], "r1.json")
    evs = [close("BAD", "deadbeef" * 5), close("GOOD", X["good"]), close("FORM", X["good"], why="built src/never.py")]
    rc, calls, _ = _run(evs, ["run", "--reading", p])
    chk(rc == 0 and calls == [] and not os.path.exists(p), "dry: no reopen, no reading")
    rc, calls, _ = _run(evs, ["run", "--apply", "--reading", p])
    d = json.load(open(p))
    chk(rc == 0 and calls == [("BAD", "deadbeef" * 5, ("sha_not_on_main",))], "one fail run, on the substance item only")
    chk(d["reopened"] == ["BAD"] and d["closes"] == 3 and d["generated"] == iso(NOW) and d["until"] == iso(NOW)
        and d["unearned"] == {"unearned": 1, "of": 4} and [r["item"] for r in d["form"]] == ["FORM"], "the reading says it")


def t_an_unreadable_source_is_unmeasured_and_writes_no_reading():
    p = os.path.join(X["top"], "r2.json")
    with open(p, "w") as f:
        f.write('{"until": "2026-11-20T00:00:00Z", "generated": "2026-11-20T00:00:00Z"}')
    before = open(p).read()
    rc, calls, out = _run([], ["run", "--apply", "--reading", p])
    chk(rc == 2 and "UNMEASURED" in out and open(p).read() == before, "an empty ledger")
    rc, calls, out = _run([close("G", X["good"])], ["run", "--apply", "--reading", p], git_dir=X["top"] + "/nowhere")
    chk(rc == 2 and "UNMEASURED" in out and calls == [] and open(p).read() == before, "a git that cannot answer")
    try:
        CC.Commits(X["repo"]).files(["0" * 40])
        chk(False, "a commit git does not have is refused")
    except CC.Unmeasured as e:
        chk("git log exit" in str(e), "a commit git does not have is refused by name, never an empty file list")
    with open(p, "w") as f:
        f.write("{torn")
    rc, calls, out = _run([close("G", X["good"])], ["run", "--apply", "--reading", p])
    chk(rc == 2 and "UNMEASURED" in out and open(p).read() == "{torn", "a torn old reading is said, never a fresh start")


def t_fresh_says_stale_missing_and_unreadable_apart():
    p = os.path.join(X["top"], "r3.json")
    say = lambda: _run([], ["fresh", "--reading", p])
    rc, _, out = say()
    chk(rc == 2 and "no reading" in out, "missing")
    for text, want, word in (("{torn", 2, "unreadable"),
                             (json.dumps({"generated": iso(NOW + 4000)}), 2, "after now"),
                             (json.dumps({"generated": iso(NOW - CC.MAX_AGE_S - 60)}), 1, "stale"),
                             (json.dumps({"generated": "2026-11-01T21:01:30Z"}), 1, "stale"),
                             (json.dumps({"generated": iso(NOW - 3600)}), 0, "fresh")):
        with open(p, "w") as f:
            f.write(text)
        rc, _, out = say()
        chk(rc == want and word in out, "%s -> %d (%d, %s)" % (word, want, rc, out.strip()))


def t_a_run_whose_reopen_failed_says_so():
    p = os.path.join(X["top"], "r4.json")
    rc, calls, out = _run([close("BAD", "deadbeef" * 5)], ["run", "--apply", "--reading", p], fail=3)
    d = json.load(open(p))
    chk(rc == 1 and d["reopened"] == [] and d["reopen_failed"][0]["item"] == "BAD" and "refused" in d["reopen_failed"][0]["why"],
        "a refused fail run is named and the run exits 1")
    chk(d["reopen_failed"][0]["why"] == "exit 3: refused: " + "x" * 600 + " repair the same item (reopen refused)",
        "the reopen reading keeps the whole refusal")


def main():
    X["top"] = tempfile.mkdtemp(prefix="selftest_close_check_")
    X["repo"] = os.path.join(X["top"], "repo")
    os.makedirs(X["repo"])
    try:
        git("init", "-q", "-b", "main")
        X["good"] = commit("first", "src/a.py")
        X["ledger"] = commit("ledger", "infrastructure/state/ledger/events/BENCH.jsonl")
        X["mixed"] = commit("mixed", "infrastructure/state/ledger/events/BENCH.jsonl", "src/b.py")
        commit("NAMED_ITEM: the other half", "src/other.py")
        for t in (t_a_code_close_whose_sha_is_not_on_main_is_substance,
                  t_a_code_close_that_touches_only_the_ledger_is_substance,
                  t_a_no_code_close_is_counted_and_its_sha_is_not_checked,
                  t_missing_evidence_and_missing_named_source_are_form,
                  t_only_the_newest_close_of_an_item_that_is_done_is_checked,
                  t_the_window_starts_before_the_last_reading_and_never_after_it,
                  t_substance_reopens_the_same_item_once_and_a_dry_run_writes_nothing,
                  t_an_unreadable_source_is_unmeasured_and_writes_no_reading,
                  t_fresh_says_stale_missing_and_unreadable_apart,
                  t_a_run_whose_reopen_failed_says_so):
            print("-- " + t.__name__[2:])
            try:
                t()
            except Exception as e:  # noqa: BLE001
                chk(False, "%s (raised %s: %s)" % (t.__name__, type(e).__name__, e))
    finally:
        shutil.rmtree(X["top"], ignore_errors=True)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
