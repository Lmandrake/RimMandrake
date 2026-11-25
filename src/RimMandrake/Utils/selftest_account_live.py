#!/usr/bin/env python3
"""selftest_account_live.py - the promises of design/specs/2026-11-22-live-account/boundary.md, one t_ per promise.

Hermetic: every case feeds a recorded or fixture (rc, stdout) through account_live.read(run=...); no case runs the
real switcher or ssh. Cases: fixtures/account_live_cases.json (built by the page folder's build_fixtures.py).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import account_live as AL  # noqa: E402

TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CASES = {c["name"]: c for c in json.load(open(os.path.join(HERE, "fixtures", "account_live_cases.json")))["cases"]}
FAILS = []


def check(ok, what, got=None):
    print("%s  %s%s" % ("ok  " if ok else "FAIL", what, "" if ok else "  got %r" % (got,)))
    if not ok:
        FAILS.append(what)


def world(c):
    def run(argv, timeout):
        if c["raises"] == "timeout":
            raise subprocess.TimeoutExpired(argv[0], timeout)
        if c["raises"] == "notfound":
            raise FileNotFoundError(argv[0])
        if c["raises"] == "oserror":
            raise PermissionError(argv[0])
        return c["rc"], c["out"]
    return run


def ans(name):
    return AL.read(run=world(CASES[name]))


def t_a_clean_status_names_its_account():
    rec = [c for c in CASES.values() if c["source"].startswith("recorded")]
    check(len(rec) >= 3, "the fixture holds recorded status outputs (%d)" % len(rec), len(rec))
    for c in rec:
        a = AL.read(run=world(c))
        check(a.kind == "value" and AL.name_of(a) == c["want"]["live"], "recorded %s names %s" % (c["name"],
              c["want"]["live"]), (a.kind, AL.name_of(a)))
    a = ans("no-ok-key")
    check(AL.name_of(a) == "system" and AL.status_of(a).get("machine") == "testbox",
          "a status with no ok key names its account and keeps its whole object", a)


def t_text_around_the_json_is_tolerated():
    for n in ("warning-line-before", "login-banner-before-and-note-after", "acceptance-fake", "long-padding-before"):
        c = CASES[n]
        check(AL.name_of(ans(n)) == c["want"]["live"], "%s reads %s" % (n, c["want"]["live"]), ans(n))


def t_a_cut_status_is_failed_not_a_name():
    for n in ("cut-at-1000-chars", "cut-at-2000-chars-of-a-long-status", "garbage", "json-list", "empty-stdout"):
        a = ans(n)
        check(a.kind == "failed" and AL.name_of(a) is None, "%s reads failed" % n, a)


def t_a_non_zero_exit_is_failed():
    for n in ("rc3-with-a-live-name", "refused-rc1"):
        a = ans(n)
        check(a.kind == "failed" and "exited" in a.cause, "%s reads failed, naming the exit code" % n, a)


def t_not_ok_is_failed():
    a = ans("not-ok-rc0")
    check(a.kind == "failed" and "not ok" in a.cause and AL.name_of(a) is None, "ok=false reads failed", a)


def t_no_live_account_is_empty():
    for n in ("live-empty-string", "live-null", "live-not-a-string"):
        a = ans(n)
        check(a.kind == "empty" and AL.name_of(a) is None and AL.status_of(a) == {}, "%s reads empty" % n, a)


def t_a_missing_or_hung_switcher_could_not_look():
    for n, word in (("timeout", "timed out after"), ("not-found", "not found"), ("permission-denied", "could not run")):
        a = ans(n)
        check(a.kind == "could_not_look" and word in a.cause, "%s reads could_not_look (%s)" % (n, word), a)
    os.environ["RM_CLAUDE_ACCOUNT"] = os.path.join(TOP, "no-such-claude-account")
    try:
        a = AL.read()
    finally:
        os.environ.pop("RM_CLAUDE_ACCOUNT")
    check(a.kind == "could_not_look" and "not found" in a.cause, "a real missing switcher (the seam) reads not found", a)


def t_every_blind_answer_names_its_cause():
    for n, c in CASES.items():
        a = AL.read(run=world(c))
        w = AL.why_of(a)
        check(a.kind == c["want"]["kind"], "%s reads %s" % (n, c["want"]["kind"]), a.kind)
        check((w is None) == (a.kind == "value") and (w is None or w.strip()), "%s: why is None only on a name" % n, w)


def t_a_remote_machine_is_read_over_ssh():
    seen = []

    def run(argv, timeout):
        seen.append(argv)
        return 0, CASES["stevedesktop-real-over-ssh"]["out"]
    a = AL.read(target="stevedesktop", run=run)
    argv = seen[0]
    check(argv[0] == "ssh" and "BatchMode=yes" in argv and argv[-2] == "stevedesktop"
          and argv[-1].startswith("bash -lc ") and "claude-account --json status" in argv[-1],
          "the remote read is ssh BatchMode through a login shell", argv)
    check(AL.name_of(a) == "system" and AL.status_of(a).get("machine") == "stevedesktop",
          "the remote answer goes through the same parse", a)
    a = AL.read(target="stevedesktop", run=lambda argv, t: (0, "Last login: today {x}\n" + CASES["acceptance-fake"]["out"]))
    check(AL.name_of(a) == "lukas", "a login banner on the remote does not hide the account", a)


def t_every_reader_uses_the_one_home():
    # the argv form, or the command as a quoted shell string (ssh); docstrings in backticks do not match
    r = subprocess.run(["git", "-C", TOP, "grep", "-n", "-E", r'"--json", "status"|"claude-account (--json )?status', "--",
                        "src/RimMandrake/*.py", "src/RimMandrake/**/*.py"], capture_output=True, text=True)
    rows = [ln for ln in r.stdout.splitlines() if not ln.startswith("src/RimMandrake/Utils/account_live.py:")
            and "/selftest_" not in ln]
    check(r.returncode in (0, 1) and not rows, "no file outside account_live.py runs claude-account status", rows)
    for f in ("slot_allocator.py", "switching_plan.py", "account_handover.py", "account_usage.py"):
        src = open(os.path.join(HERE, f)).read()
        check("account_live" in src and "AL.read(" in src, "%s reads the live account through account_live" % f)


def main():
    for t in (t_a_clean_status_names_its_account, t_text_around_the_json_is_tolerated,
              t_a_cut_status_is_failed_not_a_name, t_a_non_zero_exit_is_failed, t_not_ok_is_failed,
              t_no_live_account_is_empty, t_a_missing_or_hung_switcher_could_not_look,
              t_every_blind_answer_names_its_cause, t_a_remote_machine_is_read_over_ssh,
              t_every_reader_uses_the_one_home):
        t()
    print("selftest_account_live: %s" % ("FAILED %d" % len(FAILS) if FAILS else "OK"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
