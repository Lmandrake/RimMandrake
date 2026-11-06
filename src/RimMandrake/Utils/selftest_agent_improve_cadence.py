#!/usr/bin/env python3
"""Selftest for agent_improve_cadence.py (design 4.3): which checks are due at each level, run_pass triggering and
recording them, a revert verdict publishing a revert version and no_signal publishing none, every refusal
leaving the tree as it was, and the narrow count on the packet and the owner's digest page. Agents and publishing are
stubs, in a temp git repo; the real repo, ledger and models are never touched."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import agent_improve as A  # noqa: E402
import agent_improve_cadence as C  # noqa: E402
import agent_improve_general as G  # noqa: E402
import delegated_digest as D  # noqa: E402

sys.path.insert(0, os.path.dirname(HERE))
from contracts import blind as BL  # noqa: E402

fails = []


def check(name, cond, detail=""):
    if not cond:
        fails.append(name)
        print("FAIL: %s %s" % (name, str(detail)[:500]))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def sh(cwd, *args):
    return subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, check=True).stdout


DAY = 86400
NOW = A.epoch("2026-11-20T06:40:00Z")
GOOD = "---\nname: foo\n---\n# Foo\n\n- Read the def.\n"
BAD = GOOD + "- A line the check dislikes.\n"
AT = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")   # noqa: E731


def rec(t, n, **kw):
    return dict({"target": t, "version": n, "tag": "agent/%s/v%d" % (t, n), "diff": "", "generalization": []}, **kw)


def entry(verdict, t=NOW - DAY):
    return {"at": AT(t), "verdict": verdict}


with tempfile.TemporaryDirectory() as tmp:
    repo = os.path.join(tmp, "repo")
    A.REPO, A.ROLES, A.SKILLS = repo, os.path.join(repo, "src/RimMandrake/rimflow/roles"), os.path.join(repo, "skills")
    for name in ("foo", "bar", "baz", "qux"):
        write(os.path.join(repo, "skills", name, "SKILL.md"), GOOD)
    A.run_checks = lambda res, r: []

    # ---- the cadence
    cd = os.path.join(tmp, "cad")

    def due(recs, level, now=NOW):
        shutil.rmtree(cd, ignore_errors=True)
        os.makedirs(cd)
        for r in recs:
            write(os.path.join(cd, "%s_v%d.json" % (r["target"], r["version"])), json.dumps(r))
        return [(d["target"], d["version"], d["why"]) for d in C.due_checks(level, now, cd)]

    check("L0: nothing, the design's cost bound", due([rec("foo", 5), rec("bar", 1)], 0) == [])
    fresh = [rec("foo", n, generalization=[entry("general")] if n == 6 else []) for n in (4, 5, 6)]
    check("L1: the fifth change unchecked is due, the fourth is not, a newest checked yesterday is not",
          due([rec("foo", n) for n in (1, 2, 3)] + fresh, 1) == [("foo", 5, "every fifth change")], due(fresh, 1))
    check("a revert is not a change for the fifth count", [d[:2] for d in due(
        [rec("foo", n, generalization=[entry("general")] if n == 7 else []) for n in (1, 2, 3, 4, 6, 7)]
        + [rec("foo", 5, revert_of=4)], 1)] == [("foo", 6)], "v6 is the fifth change")
    check("L2: the fifth-change rule is L1's (L2 gates before apply)", due([rec("foo", n) for n in (1, 2, 3)] + fresh, 2) == [])
    check("weekly is per target: a new version a day after a check of the last one waits", due(
        [rec("foo", 1, generalization=[entry("general")]), rec("foo", 2)], 1) == [])
    check("weekly: newest never checked", due([rec("foo", 1)], 1) == [("foo", 1, "weekly, newest version")])
    check("weekly: older versions are not its business", due([rec("foo", 1), rec("foo", 2,
          generalization=[entry("general")])], 2) == [])
    wk = [rec("foo", 1, generalization=[entry("narrow", NOW - 7 * DAY + 3600)])]   # later clock, same UTC-day gap
    check("weekly: seven UTC days on is due, whatever the minutes", due(wk, 1) == [("foo", 1, "weekly, newest version")])
    wk6 = [rec("foo", 1, generalization=[entry("narrow", NOW - 6 * DAY)])]
    check("weekly: six days on is not", due(wk6, 2) == [])
    un = [rec("foo", 1, generalization=[entry("unmeasured")])]
    check("an unmeasured entry is no check", due(un, 1) == [("foo", 1, "weekly, newest version")])
    check("a revert version is never checked", due([rec("foo", 1, reverted_by=2), rec("foo", 2, revert_of=1)], 2) == [])
    check("a reverted fifth change is not due", due([rec("foo", 5, reverted_by=6), rec("foo", 6, revert_of=5)], 1) == [])
    check("a target no longer editable is skipped", due([rec("gone", 1)], 1) == [])
    mix = [rec("foo", 1, generalization=[entry("general", NOW - 9 * DAY)]), rec("bar", 1),
           rec("baz", 1, generalization=[entry("general", NOW - 30 * DAY)]), rec("qux", 1)]
    order = due(mix, 1)
    check("longest since an attempt first, never-tried before all", {o[0] for o in order[:2]} == {"bar", "qux"}
          and [o[0] for o in order[2:]] == ["baz", "foo"], order)
    tried = [rec("foo", 1, generalization=[entry("unmeasured", NOW - 3 * DAY)]), rec("bar", 1)]
    check("an unmeasured attempt stays due but goes behind one never tried", [o[0] for o in due(tried, 1)] == ["bar", "foo"])
    four = [rec(x, 1) for x in ("foo", "bar", "baz", "qux")]
    firsts = {tuple(o[0] for o in due(four, 1, NOW + k * DAY)[:3]) for k in range(12)}
    check("ties rotate daily, so a check that always crashes never holds a slot for good", len(firsts) > 1
          and all(any(x in f for f in firsts) for x in ("foo", "bar", "baz", "qux")), firsts)

    # ---- a real repo for the run
    changes = os.path.join(repo, "infrastructure/state/agent_improve/changes")
    gdir = os.path.join(repo, "infrastructure/state/agent_improve/general")
    TP = os.path.join(repo, "skills/foo/SKILL.md")
    DIFF = ("--- a/skills/foo/SKILL.md\n+++ b/skills/foo/SKILL.md\n@@ -4,3 +4,4 @@\n # Foo\n \n - Read the def.\n"
            "+- A line the check dislikes.\n")
    published = []

    def rewind():
        """A new repo holding one change, foo v1, whose text the check dislikes (every case starts from this)."""
        shutil.rmtree(repo, ignore_errors=True)
        for name in ("foo", "bar", "baz", "qux"):
            write(os.path.join(repo, "skills", name, "SKILL.md"), GOOD)
        write(TP, BAD)
        write(os.path.join(changes, "foo_v1.json"), json.dumps(rec(
            "foo", 1, diff=DIFF, day="2026-11-01", source_kinds=["REPAIR"], recheck="x", recheck_result="pass"), indent=1))
        sh(repo, "git", "init", "-q")
        sh(repo, "git", "add", "-A")
        sh(repo, "git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base")
        sh(repo, "git", "tag", "agent/foo/v1")
        published.clear()

    rewind()

    def fake_publish(msg, paths, r):
        published.append((msg, paths))
        sh(r, "git", "add", "--", *paths)
        sh(r, "git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", msg, "--", *paths)
        return True, sh(r, "git", "rev-parse", "HEAD").strip()

    def stub_check(verdict, calls=None):
        def go(t, version, repo=None, changes_dir=None, general_dir=None, now=None):
            if calls is not None:
                calls.append((t, version))
            r = {"at": AT(NOW), "seed": len(os.listdir(general_dir)) if os.path.isdir(general_dir) else 0, "verdict": verdict,
                 "keep": G.KEEP[verdict], "held_out": {"win": 0, "loss": 3, "tie": 0, "error": 0},
                 "source": {"win": 0, "loss": 0, "tie": 0, "error": 0}, "pairs": []}
            return r, G.record(r, t, int(version[1:]), changes_dir, general_dir, repo, {"old": "a", "new": "b"})
        return go

    def run(verdict, publish=fake_publish, level=1, now=NOW, cv=None):
        return C.run_due("2026-11-19", level, repo, changes, cv or stub_check(verdict), publish, now)

    def reread():
        return json.load(open(os.path.join(changes, "foo_v1.json"), encoding="utf-8"))

    def clean():
        return sh(repo, "git", "status", "--porcelain", "--", "skills", "infrastructure") == ""

    # ---- the verdicts against the revert
    check("the rule this reads has the noise floor", "no_signal" in G.VERDICTS and G.KEEP["no_signal"] is None)
    for v in ("general", "narrow", "unmeasured", "no_signal"):
        r = run(v)
        check("%s publishes no revert" % v, "revert" not in r[0] and open(TP).read() == BAD, r)
        rewind()
    calls = []
    r = run("overfit", cv=stub_check("overfit", calls))
    check("a revert verdict publishes a revert version", r[0]["revert"] == "published" and "agent/foo/v2" in r[0]["revert_detail"], r)
    check("the check is told the version", calls == [("foo", "v1")], calls)
    check("the target's text is restored", open(TP).read() == GOOD)
    tagged = sh(repo, "git", "show", "agent/foo/v2:skills/foo/SKILL.md")
    check("the new tag holds the restored text, v1 still holds the old", tagged == GOOD
          and sh(repo, "git", "show", "agent/foo/v1:skills/foo/SKILL.md") == BAD)
    r2 = json.load(open(os.path.join(changes, "foo_v2.json"), encoding="utf-8"))
    check("the revert's record", r2["revert_of"] == 1 and r2["version"] == 2 and r2["revert_verdict"] == "overfit"
          and r2["revert_evidence"].startswith("infrastructure/state/agent_improve/general/")
          and r2["source_kinds"] == ["REPAIR"] and "-- A line the check dislikes" in r2["diff"], r2)
    check("the old record points at it, its verdict entry kept", reread()["reverted_by"] == 2
          and reread()["generalization"][-1]["verdict"] == "overfit")
    check("the revert commit carries the digest's Delegated line", "Delegated: technical — agent improvement foo revert"
          in sh(repo, "git", "log", "-1", "--format=%B"))
    check("tree clean after", clean(), sh(repo, "git", "status", "--porcelain"))
    check("nothing due after a revert (no ping-pong)", C.due_checks(1, NOW + 30 * DAY, changes) == [])
    rewind()
    # ---- refusals leave the tree as it was
    stale = dict(reread(), diff=DIFF.replace("A line the check dislikes", "A line that was never there"))
    write(os.path.join(changes, "foo_v1.json"), json.dumps(stale, indent=1))
    sh(repo, "git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qam", "edit")
    r = run("overfit")
    check("a diff that no longer reverse-applies is refused and said", r[0]["revert"] == "refused"
          and "reverse-apply" in r[0]["revert_detail"] and open(TP).read() == BAD and clean(), r)
    rewind()
    A.run_checks = lambda res, rp: ["validate_skills exit 1"]
    r = run("overfit")
    check("failing checks put the text back", r[0]["revert"] == "refused" and "validate_skills" in r[0]["revert_detail"]
          and open(TP).read() == BAD and clean(), r)
    A.run_checks = lambda res, rp: []
    rewind()

    def pub_refuses_revert(msg, paths, r):
        if "revert" in msg.split("\n")[0]:
            return False, "refused"
        return fake_publish(msg, paths, r)
    r = run("overfit", publish=pub_refuses_revert)
    check("a refused revert publish puts everything back", r[0]["revert"] == "refused" and open(TP).read() == BAD
          and not os.path.exists(os.path.join(changes, "foo_v2.json")) and "reverted_by" not in reread() and clean(),
          (r, sh(repo, "git", "status", "--porcelain")))
    rewind()

    # a revert record that cannot be written: everything back, reported
    write(os.path.join(changes, "foo_v2.json"), "not json, so last_change skips it and v2 collides")
    sh(repo, "git", "add", "--", os.path.join(changes, "foo_v2.json"))
    sh(repo, "git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "unreadable record")
    r = run("overfit")
    check("a colliding revert record is refused and the tree put back", r[0]["revert"] == "refused"
          and "preparing" in r[0]["revert_detail"] and open(TP).read() == BAD and "reverted_by" not in reread() and clean()
          and "not json" in open(os.path.join(changes, "foo_v2.json")).read(), (r, sh(repo, "git", "status", "--porcelain")))
    rewind()

    def pub_refuses(msg, paths, r):
        return False, "refused"
    r = run("overfit", publish=pub_refuses)
    check("a refused check publish: unrecorded, no revert", not r[0]["published"] and "revert" not in r[0]
          and not reread()["generalization"] and clean() and not (os.path.isdir(gdir) and os.listdir(gdir)), r)
    check("and it stays due", [d["version"] for d in C.due_checks(1, NOW, changes)] == [1])
    rewind()

    def crash(*a, **k):
        raise OSError("claude: not found")
    r = run("overfit", cv=crash)
    check("a crashed check is no verdict and stays due", r[0]["verdict"] is None and "crashed" in r[0]["detail"]
          and [d["version"] for d in C.due_checks(1, NOW, changes)] == [1] and clean(), r)
    write(os.path.join(changes, "foo_v1.json"), json.dumps(reread(), indent=2))
    r = run("overfit")
    check("an uncommitted change record is left alone", r[0]["verdict"] is None and "uncommitted" in r[0]["detail"], r)
    rewind()

    for name in ("bar", "baz", "qux"):
        write(os.path.join(changes, "%s_v1.json" % name), json.dumps(rec(name, 1)))
    write(os.path.join(changes, "bar_v1.json"), json.dumps(rec("bar", 1)))
    sh(repo, "git", "add", "--", os.path.join(changes, "bar_v1.json"))
    sh(repo, "git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "bar")
    was_rev = A.git

    def bad_git(*a, **k):
        raise RuntimeError("git went away")
    A.git = bad_git
    rows = C.run_due("d", 2, repo, changes, crash, fake_publish, NOW)
    A.git = was_rev
    check("a git failure on one target is a row, never the pass's crash", rows and all(
        "crashed" in x["detail"] for x in rows), rows)
    check("four due, MAX_CHECKS run", len(C.due_checks(2, NOW, changes)) == 4 and C.MAX_CHECKS == 3
          and len(C.run_due("d", 2, repo, changes, crash, fake_publish, NOW)) == 3)
    rewind()

    # ---- run_pass triggers and reports it
    src = {"lessons": os.path.join(tmp, "nolessons"), "store": os.path.join(tmp, "nostore"),
           "ops_alarms": os.path.join(tmp, "none.json"), "owner": os.path.join(tmp, "none.jsonl")}
    out = os.path.join(tmp, "out")
    os.makedirs(out, exist_ok=True)
    sp = os.path.join(out, "state.json")
    write(sp, json.dumps({"level": 1}))
    seen = []

    def cad(**k):
        seen.append(k)
        return C.run_due(check_version=stub_check("narrow"), **k)
    delegated = os.path.join(repo, "infrastructure/state/delegated")
    kw = dict(out=out, repo=repo, src=src, state_path=sp, changes_dir=changes, delegated_dir=delegated,
              publish=fake_publish, force=True)
    s = A.run_pass("2026-11-19", apply=False, cadence=cad, **kw)
    check("a dry run triggers nothing", not seen and s["checks"] == [], s)
    s = A.run_pass("2026-11-19", apply=True, cadence=cad, **kw)
    check("run_pass triggers the due check with its level", seen and seen[0]["level"] == 1 and seen[0]["day"] == "2026-11-19", seen)
    check("and records it", reread()["generalization"][-1]["verdict"] == "narrow" and s["checks"][0]["published"], s)
    check("and reports it, with the narrow count, on the packet", "foo v1 (weekly, newest version): narrow"
          in open(os.path.join(out, "2026-11-19", "packet.md")).read()
          and "Narrow changes per target: foo 1" in open(os.path.join(out, "2026-11-19", "packet.md")).read())
    check("the summary carries the count", s["narrow"] == {"foo": 1}, s["narrow"])
    write(sp, json.dumps({"level": 0}))
    seen.clear()
    s = A.run_pass("2026-11-19", apply=True, cadence=lambda **k: C.run_due(check_version=crash, **k), **kw)
    check("L0 runs no check through the default step", s["checks"] == [], s)
    write(sp, json.dumps({"level": 1}))
    seen.clear()
    s = A.run_pass("2026-11-19", apply=True, only={"foo"}, cadence=cad, **kw)
    check("a --target hand run triggers no check", not seen and s["checks"] == [], s)
    write(sp, json.dumps({"level": 0}))
    called = []
    was, C.run_due = C.run_due, lambda **k: called.append(k) or []
    write(sp, json.dumps({"level": 2}))
    A.run_pass("2026-11-19", apply=True, **kw)
    C.run_due = was
    check("the default step is run_due, not opt-in", len(called) == 1 and called[0]["level"] == 2, called)
    rewind()

    # gather at L1: a change's unread recheck holds its target to a recheck-only pass; a revert's does not
    ldir = os.path.join(tmp, "lessons")
    for i, (hh, kind) in enumerate((("08", "REPAIR"), ("09", "AUDIT"), ("10", "REPAIR"))):
        write(os.path.join(ldir, "20261119T%s0000Z-BENCH-x%d.md" % (hh, i)),
              "# WIDGET_%s_SHAPE guessed a defName %d\n\nhome: foo\n" % (kind, i))
    gsrc = dict(src, lessons=ldir)
    write(os.path.join(changes, "foo_v2.json"), json.dumps(rec("foo", 2, recheck="y", recheck_result=None)))
    pk = A.gather("2026-11-19", gsrc, A.LEVELS[1], changes)
    check("control: an ordinary change's unread recheck holds the target", "foo" in pk["held"], pk["held"])
    write(os.path.join(changes, "foo_v2.json"), json.dumps(rec("foo", 2, revert_of=1, recheck="y", recheck_result=None)))
    pk = A.gather("2026-11-19", gsrc, A.LEVELS[1], changes)
    check("a revert's recheck does not", "foo" not in pk["held"] and [e["target"] for e in pk["targets"]] == ["foo"]
          and not pk["targets"][0]["recheck_only"], pk["held"])
    rewind()

    # ---- the narrow count
    nd = os.path.join(tmp, "narrow")
    N = lambda t, n, *vs, **kw: write(os.path.join(nd, "%s_v%d.json" % (t, n)), json.dumps(rec(   # noqa: E731
        t, n, generalization=[{"verdict": v} for v in vs], **kw)))
    N("rimworld-modding", 1, "narrow")
    N("rimworld-modding", 2, "narrow", "unmeasured")                # the latest MEASURED verdict decides
    N("rimworld-modding", 3, "narrow", "general")                   # moved on
    N("rimworld-modding", 4, "narrow", reverted_by=5)               # undone
    N("using-rimflow", 1, "general")
    N("designer", 1)
    counts = D.narrow_counts(nd)
    check("narrow counts by target", counts == {"rimworld-modding": 2, "using-rimflow": 0, "designer": 0}, counts)
    check("a missing folder is UNMEASURED, not zero", D.narrow_counts(os.path.join(tmp, "nowhere")) is None)
    write(os.path.join(nd, "broken_v1.json"), "not json")
    check("an unreadable record is UNMEASURED, not a lower count", D.narrow_counts(nd) is None)
    check("packet line: UNMEASURED and none", "UNMEASURED" in C.narrow_line(None) and C.narrow_line({"a": 0}).endswith("none"))
    os.remove(os.path.join(nd, "broken_v1.json"))

    # the owner's page, through the real allowlist renderer (the real repo's targets name the domain)
    def page(narrow):
        cut = dt.datetime(2026, 11, 20, tzinfo=dt.timezone.utc)
        reads = {s: D._read() for s in D.SOURCES}
        return D.build("2026-11-20", None, cut, reads, asks=[], narrow=narrow)[0]
    t = page(counts)
    check("the digest lists the target and its count", "| rimworld-modding | 2 |" in t, t)
    check("a target at zero is not listed", "using-rimflow" not in t and "designer" not in t)
    t = page({"swordfish-nine": 3, "rimworld-modding": 1})
    check("a target outside the domain is withheld and counted, never named", "swordfish" not in t
          and "| rimworld-modding | 1 |" in t and "per target; reverted ones not counted. Withheld: 1." in t, t)
    t = page(None)
    check("unread records read UNMEASURED on the page", "## Narrow agent changes UNMEASURED" in t, t)
    check("no narrow change says None", "None." in page({"rimworld-modding": 0}))
    # the whole path: main reads the folder it is given and the written page shows it
    ledger, ddir = os.path.join(tmp, "ledger.jsonl"), os.path.join(tmp, "digest")
    write(ledger, "")
    rc = D.main(["--dry-run", "--ledger", ledger, "--cut", "2026-11-20T00:00:00Z", "--date", "2026-11-20",
                 "--out-dir", ddir, "--state", os.path.join(tmp, "dstate.json"), "--changes", nd,
                 "--errors", os.path.join(tmp, "derrors.log")])
    written = [os.path.join(ddir, n) for n in os.listdir(ddir) if n.endswith(".md")] if os.path.isdir(ddir) else []
    check("digest main puts the count on the page", rc == 0 and written
          and "| rimworld-modding | 2 |" in open(written[0], encoding="utf-8").read(), (rc, written))
    check("the domain holds the real targets", {"relentless", "rimworld-modding", "designer"}
          <= set(BL._agent_target_domain()), BL._agent_target_domain()[:5])

print("selftest_agent_improve_cadence: %s" % ("FAIL %d" % len(fails) if fails else "PASS"))
sys.exit(1 if fails else 0)
