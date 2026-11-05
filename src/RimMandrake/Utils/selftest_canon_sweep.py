#!/usr/bin/env python3
"""Selftest for canon_sweep.py (CANON_BUILD_SWEEP_WHEN_CANON_MOVES).

Drives every trigger on a throwaway git repo holding the REAL check_canon.py and canon.yml: the first full sweep, a
commit that adds a contradicting doc (changed docs only, one Conductor line), a quiet rerun (no second line), the fix,
a contradiction committed past the hooks that only a canon.yml change finds, the nightly backstop, a checker change,
a lost base sha, and an UNMEASURED checker that must not advance the state. The Conductor log is a temp file.

    python3 src/RimMandrake/Utils/selftest_canon_sweep.py
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import canon_sweep as S  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -- %s" % detail) if not ok and detail else ""))
    if not ok:
        FAILS.append(name)


def git(repo, *a):
    subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True,
                   capture_output=True, text=True)


def write(repo, rel, text):
    p = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


def commit(repo, msg, *rels):
    git(repo, "add", "--", *rels)
    git(repo, "commit", "-q", "-m", msg)


tmp = tempfile.mkdtemp(prefix="canon_sweep_")
try:
    repo, out = os.path.join(tmp, "repo"), os.path.join(tmp, "out")
    log = os.path.join(tmp, "conductor_log.md")
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "main")
    shutil.copy(os.path.join(REPO, S.CANON_REL), os.path.join(repo, "canon.tmp"))
    write(repo, S.CANON_REL, open(os.path.join(repo, "canon.tmp"), encoding="utf-8").read())
    os.remove(os.path.join(repo, "canon.tmp"))
    write(repo, S.CHECKER_REL, open(os.path.join(REPO, S.CHECKER_REL), encoding="utf-8").read())
    write(repo, "design/good.md", "The roster is 13 factions.\n")
    write(repo, "design/other.md", "Nothing numeric here.\n")
    commit(repo, "init", S.CANON_REL, S.CHECKER_REL, "design/good.md", "design/other.md")

    t0 = dt.datetime(2026, 11, 5, 12, 0, tzinfo=dt.timezone.utc)

    def go(hours, **kw):
        rc = S.run(repo, out, log, now=t0 + dt.timedelta(hours=hours), **kw)
        return rc, json.load(open(os.path.join(out, "latest.json"), encoding="utf-8"))

    def log_lines():
        return [l for l in open(log, encoding="utf-8").read().splitlines() if "CANON SWEEP" in l] \
            if os.path.exists(log) else []

    rc, L = go(0)
    check("first run is a full sweep", rc == 0 and L["reason"] == "first" and L["files_checked"] == 2, L)
    check("clean tree: no contradiction, nothing told", L["contradictions"] == 0 and not log_lines())

    write(repo, "design/bad.md", "There are 14 factions.\n")
    commit(repo, "bad doc", "design/bad.md")
    rc, L = go(1)
    check("a commit checks only its changed docs", rc == 0 and L["reason"] == "commits"
          and L["changed"] == ["design/bad.md"] and L["files_checked"] == 1, L)
    check("the contradiction is open and new", L["contradictions"] == 1 and len(L["new"]) == 1
          and L["open"][0]["key"] == "factions" and L["open"][0]["path"] == "design/bad.md", L["open"])
    ll = log_lines()
    check("the Conductor log got ONE line naming the doc", len(ll) == 1 and "design/bad.md:1" in ll[0]
          and "[factions]" in ll[0], ll)
    check("findings.md lists it", "design/bad.md:1" in open(os.path.join(out, "findings.md"), encoding="utf-8").read())

    rc, L = go(2)
    check("a quiet rerun checks nothing and keeps the finding open", L["reason"] == "commits"
          and L["files_checked"] == 0 and L["contradictions"] == 1 and not L["new"], L)
    check("a quiet rerun does not re-ring the Conductor", len(log_lines()) == 1)

    write(repo, "design/bad.md", "Blank line first.\n\nThere are 14 factions.\n")
    commit(repo, "move the line", "design/bad.md")
    rc, L = go(2.5)
    check("an edit that only moves the line does not re-ring", L["contradictions"] == 1 and not L["new"]
          and len(log_lines()) == 1, L)

    write(repo, "design/bad.md", "There are 13 factions.\n")
    commit(repo, "fix", "design/bad.md")
    rc, L = go(3)
    check("the fix clears the open set", L["contradictions"] == 0, L)

    # a contradiction that landed past every hook: put it in the tree and pretend the last run already saw this sha
    write(repo, "design/sneaky.md", "Eleven factions remain.\n")
    commit(repo, "landed past the hooks", "design/sneaky.md")
    st_p = os.path.join(out, "state.json")
    st = json.load(open(st_p, encoding="utf-8"))
    st["sha"] = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    json.dump(st, open(st_p, "w", encoding="utf-8"))
    rc, L = go(4)
    check("unchanged canon and no new commits: the sneaky doc is not seen yet", L["contradictions"] == 0
          and L["files_checked"] == 0, L)
    with open(os.path.join(repo, S.CANON_REL), "a", encoding="utf-8") as fh:
        fh.write("\n# canon moved\n")
    commit(repo, "canon moved", S.CANON_REL)
    rc, L = go(5)
    check("canon.yml moving triggers a FULL sweep", L["reason"] == "canon_moved" and L["changed"] is None
          and L["files_checked"] == 4, L)
    check("the full sweep finds the doc no commit check saw", [h["path"] for h in L["open"]] == ["design/sneaky.md"]
          and len(log_lines()) == 2 and "canon_moved" in log_lines()[-1], L["open"])

    rc, L = go(5 + S.NIGHTLY_H + 0.1)
    check("the nightly backstop runs a full sweep", L["reason"] == "nightly" and L["files_checked"] == 4, L)
    check("nightly keeps an already-told finding quiet", not L["new"] and len(log_lines()) == 2, L)

    with open(os.path.join(repo, S.CHECKER_REL), "a", encoding="utf-8") as fh:
        fh.write("\n# rules moved\n")
    commit(repo, "checker moved", S.CHECKER_REL)
    rc, L = go(26)
    check("a check_canon.py change triggers a FULL sweep", L["reason"] == "checker_moved" and L["changed"] is None, L)

    st = json.load(open(st_p, encoding="utf-8"))
    st["sha"] = "0" * 40
    json.dump(st, open(st_p, "w", encoding="utf-8"))
    rc, L = go(27)
    check("a base sha git cannot diff from is a FULL sweep", L["reason"] == "base_lost" and L["files_checked"] == 4, L)

    write(repo, "design/sneaky.md", "Thirteen factions.\n")
    commit(repo, "fix sneaky", "design/sneaky.md")
    go(28)
    write(repo, "design/sneaky.md", "There are 11 factions.\n")
    commit(repo, "regress", "design/sneaky.md")
    rc, L = go(29)
    check("a finding that cleared and came back rings again", len(L["new"]) == 1 and len(log_lines()) == 3, L)

    before = json.load(open(st_p, encoding="utf-8"))
    write(repo, S.CHECKER_REL, "import sys\nprint('no yaml', file=sys.stderr)\nsys.exit(2)\n")
    commit(repo, "blind checker", S.CHECKER_REL)
    rc, L = go(30)
    check("an UNMEASURED checker exits 2 and says so", rc == 2 and L["state"].startswith("UNMEASURED"), L)
    check("an UNMEASURED run does not advance the state", json.load(open(st_p, encoding="utf-8")) == before)

    write(repo, S.CHECKER_REL, "print('CONTRADICTS CANON — 1')\nprint('garbage')\nprint('\\n1 file(s) checked. "
          "1 contradiction(s), 0 advisory.')\nraise SystemExit(1)\n")
    commit(repo, "unparseable checker", S.CHECKER_REL)
    rc, L = go(31)
    check("output that disagrees with the checker's own total is UNMEASURED, not clean",
          rc == 2 and "parsed 0" in L["state"], L)

    rc = S.main(["show", "--out", out])
    check("show exits 2 on an UNMEASURED reading", rc == 2)

    try:
        S.tell_conductor(S.conductor_log_guard.LIVE, t0, "selftest", L.get("open") or [], out)
        refused = False
    except S.conductor_log_guard.TestWroteLiveLog:
        refused = True
    check("a test process cannot write the real Conductor log through the sweep", refused)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n%s: %d failure(s)" % ("RED" if FAILS else "GREEN", len(FAILS)))
sys.exit(1 if FAILS else 0)
