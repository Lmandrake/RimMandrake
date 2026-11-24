#!/usr/bin/env python3
"""selftest_quiet_scan.py: quiet_scan.py over fake facts and a temp git repo. Nothing is launched; no model.
Page design/specs/2026-11-24-quiet-scan/boundary.md: one test per promise, of its name. Exit 0 all pass, 1 any fail."""
import json
import os
import subprocess
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_quiet_scan_")
os.environ["RM_QUIET_SCAN_DIR"] = os.path.join(TMP, "state")
sys.path.insert(0, HERE)
try:
    import quiet_scan as QS
except ImportError as e:
    print("FAIL quiet_scan.py cannot be imported: %s" % e)
    sys.exit(1)

FAILS = []
NOW = 1_800_000_000.0
DAY = 86400


def eq(got, want, what=""):
    if got != want:
        raise AssertionError("%s: got %r, want %r" % (what, got, want))


CFG = {"enabled": True, "seat": "BENCH", "quiet_days": 7, "files_per_run": 2, "reading_max_age_s": 600,
       "system_wait_s": 3600, "sonnet_cap_usd": 5}


def files_facts(**kw):
    f = {"tracked": ["src/RimMandrake/Utils/a.py", "src/RimMandrake/ModA/Defs/d.xml", "src/RimMandrake/ModA/Src/c.cs",
                     "src/RimUtinni/ModB/Src/b.cs"],
         "mods": {"src/RimMandrake/ModA": "ModA", "src/RimUtinni/ModB": "ModB"}, "changed": set(), "clean": set(),
         "recorded": set(), "flagged": set(), "ended": set(), "held": {}}
    f.update(kw)
    return f


def facts(**kw):
    f = {"files": files_facts(), "busy": None, "off": None, "paused": None, "pool": None, "runs": {}, "blind": None}
    f.update(kw)
    return f


def git(root, *a, **env):
    e = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", **env)
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t"] + list(a), cwd=root, env=e, check=True,
                          capture_output=True, text=True).stdout


def repo():
    """A repo with an old commit (30 days) of src/T/Old/*.cs and a fresh one that touches new.cs."""
    root = tempfile.mkdtemp(dir=TMP)
    git(root, "init", "-q", "-b", "main")
    d = os.path.join(root, "src/RimMandrake/M")
    os.makedirs(os.path.join(d, "About"))
    for n in ("About/About.xml", "old.cs", "new.cs", "edge6.cs", "edge8.cs"):
        open(os.path.join(d, n), "w").write("x\n")
    import time
    t = time.time()

    def commit(days, msg):
        when = "%d +0000" % (t - days * DAY)
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", msg, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    commit(30, "old")
    for days, n in ((8, "edge8.cs"), (6, "edge6.cs"), (1, "new.cs")):
        open(os.path.join(d, n), "w").write("y%s\n" % n)
        commit(days, n)
    git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
    return root, t


def t_a_file_changed_in_the_last_seven_days_is_never_picked():
    root, t = repo()
    ch = QS.changed_since(root, 7, t)
    p = "src/RimMandrake/M/"
    eq((p + "new.cs" in ch, p + "edge6.cs" in ch, p + "edge8.cs" in ch, p + "old.cs" in ch), (True, True, False, False), "git")
    f = files_facts(changed={"src/RimMandrake/ModA/Src/c.cs"})
    assert "src/RimMandrake/ModA/Src/c.cs" not in QS.candidates(f)
    # could not look is never "nothing changed"
    for broken in (tempfile.mkdtemp(dir=TMP), os.path.join(TMP, "absent")):
        try:
            QS.changed_since(broken, 7, t)
        except QS.Blind:
            pass
        else:
            raise AssertionError("no repo read as no changes: %s" % broken)
    shallow = os.path.join(TMP, "shallow")
    subprocess.run(["git", "clone", "-q", "--depth", "1", "file://" + root, shallow], check=True, capture_output=True)
    try:
        QS.changed_since(shallow, 7, t)
    except QS.Blind:
        pass
    else:
        raise AssertionError("a shallow clone read as a full history")
    d = QS.decide(CFG, {}, facts(files=None, blind="git log failed"), NOW)
    eq(d["decision"], "blind", "tick when git cannot answer")


def t_mod_content_first():
    eq(QS.candidates(files_facts()), ["src/RimMandrake/ModA/Src/c.cs", "src/RimUtinni/ModB/Src/b.cs",
                                      "src/RimMandrake/ModA/Defs/d.xml", "src/RimMandrake/Utils/a.py"], "order")
    t_ = ["src/RimMandrake/ModA/Source/SelfTest/Program.cs", "src/RimMandrake/ModA/Source/AFuzz/AFuzz.cs",
          "src/RimMandrake/ModA/selftest_x.py", "src/RimMandrake/ModA/Source/Contest.cs"]
    eq(QS.candidates(files_facts(tracked=t_))[0], t_[3], "a test program inside a mod is not mod content")
    eq(QS.candidates(files_facts(tracked=t_ + ["src/RimMandrake/ModA/Defs/d.xml"]))[:2], [t_[3], "src/RimMandrake/ModA/Defs/d.xml"],
       "the mod's XML before its test programs")
    eq(QS.candidates(files_facts(recorded={"src/RimMandrake/ModA/Src/c.cs"}))[:2],
       ["src/RimUtinni/ModB/Src/b.cs", "src/RimMandrake/ModA/Src/c.cs"], "never read before out of date")
    root, t = repo()
    eq(QS.mod_dirs(root, ["src/RimMandrake/M/About/About.xml", "src/RimMandrake/Utils/x.py"]), {"src/RimMandrake/M": "M"}, "mods")


def t_a_file_that_needs_no_read_is_not_picked():
    c = "src/RimMandrake/ModA/Src/c.cs"
    for k in ("clean", "flagged", "ended"):
        assert c not in QS.candidates(files_facts(**{k: {c}})), k
    got = QS.candidates(files_facts(held={"ModA": "HELD BY OWNER"}))
    eq(got, ["src/RimUtinni/ModB/Src/b.cs", "src/RimMandrake/Utils/a.py"], "a held mod")

    def boom():
        raise RuntimeError("store unreadable")
    root, t = repo()
    for k in ("flags", "holds", "records"):
        try:
            QS.gather_files(root, 7, t, readers={k: boom})
        except QS.Blind:
            continue
        raise AssertionError("unreadable %s read as none" % k)
    f = QS.gather_files(root, 7, t, readers={"flags": lambda: {}, "records": lambda: {}, "holds": lambda: {}})
    eq(QS.candidates(f), ["src/RimMandrake/M/edge8.cs", "src/RimMandrake/M/old.cs", "src/RimMandrake/M/About/About.xml"],
       "the live gather over a real repo")


def t_a_picked_file_ends_clean_flagged_or_with_a_noted_reason():
    root, t = repo()
    p = "src/RimMandrake/M/old.cs"
    QS.record_pick("u1", p, root, NOW)
    st = {"record": "DIRTY", "flag": False, "landed": True}

    def look(root_, path):
        return dict(st)
    rc, said = QS.end(p, "u1", "clean", None, root, NOW, look=look)
    assert rc == 2 and "mark-clean" in said, (rc, said)
    st["record"] = "CLEAN"
    st["landed"] = False
    rc, said = QS.end(p, "u1", "clean", None, root, NOW, look=look)
    assert rc == 2 and "./publish" in said, (rc, said)
    rc, said = QS.end(p, "u1", "flagged", None, root, NOW, look=look)
    assert rc == 2 and "is not FLAGGED" in said, (rc, said)
    rc, said = QS.end(p, "u1", "noted", "  ", root, NOW, look=look)
    assert rc == 2 and "--reason" in said, (rc, said)
    rc, said = QS.end(p, "u1", "gone", None, root, NOW, look=look)
    assert rc == 2, said
    rc, said = QS.end("src/RimMandrake/M/new.cs", "u1", "noted", "x", root, NOW, look=look)
    assert rc == 2 and "picked" in said, "a file nobody picked cannot end: %s" % said
    eq(QS.ends(), [], "a refusal records nothing")
    st["landed"] = True
    eq(QS.end(p, "u1", "clean", None, root, NOW, look=look)[0], 0, "clean")
    e = QS.ends()[-1]
    eq((e["path"], e["outcome"], e["run"]), (p, "clean", "u1"), "row")
    assert e["sha256"] == QS.sha256(os.path.join(root, p))
    # what a run left with no outcome is noted with that run's end
    q = "src/RimMandrake/M/edge8.cs"
    QS.record_pick("u2", q, root, NOW)
    QS.record_pick("u2", p, root, NOW)
    QS.end(p, "u2", "noted", "unreachable", root, NOW, look=look)
    s = {"run": {"unit": "u2"}}
    QS.harvest(s, {"u2": {"live": False, "counts": True, "result": "success (0)"}}, NOW)
    e = QS.ends()[-1]
    eq((e["path"], e["outcome"]), (q, "noted"), "harvest")
    assert "u2" in e["reason"] and "success" in e["reason"], e
    f = QS.gather_files(root, 7, t, readers={"flags": lambda: {}, "records": lambda: {}, "holds": lambda: {}})
    assert p not in QS.candidates(f) and q not in QS.candidates(f), "an ended file is not picked again on the same bytes"
    open(os.path.join(root, p), "a").write("z\n")
    f = QS.gather_files(root, 7, t, readers={"flags": lambda: {}, "records": lambda: {}, "holds": lambda: {}})
    assert p in QS.candidates(f), "new bytes are a new file to read"


def t_a_system_death_releases_the_file():
    root, t = repo()
    p = "src/RimMandrake/M/old.cs"
    n = len(QS.ends())
    QS.record_pick("u3", p, root, NOW)
    s = {"run": {"unit": "u3"}}
    QS.harvest(s, {"u3": {"live": False, "counts": False, "result": "killed"}}, NOW)
    eq(len(QS.ends()), n, "nothing noted")
    assert not s.get("stopped"), s
    eq(QS.decide(CFG, s, facts(), NOW + 60)["decision"], "system_wait", "waits")
    eq(QS.decide(CFG, s, facts(), NOW + 3601)["decision"], "launch", "then goes")
    eq(QS.candidates(files_facts(picked={"src/RimMandrake/ModA/Src/c.cs": 1}))[-1], "src/RimMandrake/ModA/Src/c.cs",
       "a released file goes behind the files picked fewer times")
    s = {"run": {"unit": "u3b"}}
    QS.harvest(s, {}, NOW)          # no record of the run: could not look, nothing harvested
    eq((s.get("run"), len(QS.ends())), ({"unit": "u3b"}, n), "a run that cannot be seen stays")
    eq(QS.decide(CFG, s, facts(), NOW)["decision"], "blind", "and launches nothing")


def t_the_job_yields_to_a_live_mod_step():
    def rd(decision, live=(), age=10):
        return {"at": NOW - age, "mods": {"Pyrelands": {"decision": decision, "live": list(live)},
                                          "Held": {"decision": "owner_hold", "live": []}}}
    for d in ("live", "launch", "launched", "launch_wait", "launch_retry", "slots_full", "ready", "repairing"):
        assert QS.mod_step(rd(d), [], NOW, 600)[0], d
    for d in ("owner", "stopped", "ceiling", "owner_hold", "upstream_wait"):
        eq(QS.mod_step(rd(d), [], NOW, 600), (None, None), d)
    assert QS.mod_step(rd("owner", live=["rm-x"]), [], NOW, 600)[0], "a live unit under another decision"
    recs = [{"unit": "rm-detached-a", "env": {"RM_CONTROL_MOD": "Pyrelands"}}]
    assert QS.mod_step(rd("owner"), recs, NOW, 600)[0], "a live run the tick has not seen"
    eq(QS.mod_step(rd("owner"), [{"unit": "x", "env": {"RM_CONTROL_MOD": "none"}}, {"unit": "y", "env": None}], NOW, 600),
       (None, None), "a run on no mod")
    for bad in (None, {}, {"at": NOW - 601, "mods": {}}, {"at": NOW, "mods": None}, rd("owner", age=700)):
        busy, blind = QS.mod_step(bad, [], NOW, 600)
        assert blind and not busy, bad
    eq(QS.decide(CFG, {}, facts(busy="Pyrelands is live"), NOW)["decision"], "yields", "tick")
    eq(QS.decide(CFG, {}, facts(blind="the reading is stale"), NOW)["decision"], "blind", "tick, stale reading")
    w = QS.next_word(CFG, {"run": {"unit": "u"}}, facts(busy="Pyrelands is live"), "u", [], NOW)
    eq(w[0], "YIELD", "next")
    eq(QS.next_word(CFG, {"run": {"unit": "u"}}, facts(blind="x"), "u", [], NOW)[0], "YIELD", "next, blind")
    eq(QS.next_word(CFG, {"run": {"unit": "u"}}, facts(), "u", [], NOW), ("READ", "src/RimMandrake/ModA/Src/c.cs"), "idle")


def t_the_gates_launch_nothing():
    D = lambda cfg=CFG, st=None, account=(True, ""), **kw: QS.decide(cfg, st or {}, facts(**kw), NOW, account)
    eq(D()["decision"], "launch", "the green case")
    eq(D(cfg=dict(CFG, enabled=False))["decision"], "disabled", "")
    eq(D(off="OFF by pipe")["decision"], "off", "")
    eq(D(paused="pause all")["decision"], "pipeline_paused", "")
    eq(D(account=(False, "draining"))["decision"], "account_hold", "")
    eq(D(pool="pool full")["decision"], "pool_full", "")
    eq(D(st={"run": {"unit": "u"}}, runs={"u": {"live": True}})["decision"], "live", "")
    eq(D(files=files_facts(tracked=[]))["decision"], "none_left", "")
    # --hand skips the mod step and nothing else
    eq(QS.decide(CFG, {}, facts(busy="b"), NOW, hand="why")["decision"], "launch", "hand")
    for kw in ({"off": "x"}, {"paused": "x"}, {"pool": "x"}, {"blind": "x"}):
        assert QS.decide(CFG, {}, facts(**kw), NOW, hand="why")["decision"] != "launch", kw
    st = {"run": {"unit": "u"}}
    for kw in ({"off": "x"}, {"paused": "x"}):
        eq(QS.next_word(CFG, st, facts(**kw), "u", [], NOW)[0], "YIELD", str(kw))
    eq(QS.next_word(dict(CFG, enabled=False), st, facts(), "u", [], NOW)[0], "YIELD", "disabled")
    eq(QS.next_word(CFG, st, facts(), "u", ["a", "b"], NOW)[0], "DONE", "files_per_run")
    eq(QS.next_word(CFG, st, facts(), "other", [], NOW)[0], "YIELD", "a run that is not the scan's")
    h = {"run": {"unit": "u", "hand": "why"}}
    eq(QS.next_word(CFG, h, facts(busy="b"), "u", [], NOW)[0], "READ", "hand's one file")
    eq(QS.next_word(CFG, h, facts(busy="b"), "u", ["a"], NOW)[0], "DONE", "hand reads one file")


def t_a_run_that_ends_no_file_stops_the_scan():
    root, t = repo()
    QS.record_pick("u4", "src/RimMandrake/M/old.cs", root, NOW)
    s = {"run": {"unit": "u4"}}
    QS.harvest(s, {"u4": {"live": False, "counts": True, "result": "success (0)"}}, NOW)
    assert s.get("stopped") and "u4" in s["stopped"], s
    d = QS.decide(CFG, s, facts(), NOW)
    eq(d["decision"], "stopped", "")
    assert d.get("need"), d
    told = []
    QS.say_need(d, s, NOW, need=lambda text, now: told.append(text))
    d = QS.decide(CFG, s, facts(), NOW)
    QS.say_need(d, s, NOW, need=lambda text, now: told.append(text))
    eq(len(told), 1, "said once")
    QS.clear(s, "fixed the brief", NOW)
    eq(QS.decide(CFG, s, facts(), NOW)["decision"], "launch", "cleared")
    # a run that yielded before it picked any file ended nothing and is no fault
    s = {"run": {"unit": "u5"}}
    QS.harvest(s, {"u5": {"live": False, "counts": True, "result": "success (0)"}}, NOW)
    assert not s.get("stopped"), s


def t_the_run_is_sonnet_and_knows_the_method():
    argv = QS.launch_argv(CFG, "/b.md")
    eq(argv[argv.index("--model") + 1], "sonnet", "model")
    assert "--max-budget-usd" not in argv
    b = QS.brief_text()
    for s in ("roles/code_review.md", "fresh reader", "quiet_scan.py next", "quiet_scan.py end", "mark-clean", "flag",
              "polish.md", "Do not claim", "concrete case"):
        assert s in b, s
    assert "{" + "unit}" not in b
    import re
    assert not re.search(r"\$\d|budget|weighted", b), "no spend in a brief"


def t_a_scan_run_does_not_wake_the_conductor():
    import detached_helper as DH
    eq([DH.run_wakes({"next_act_owner": "quiet_scan"}), DH.run_wakes({"next_act_owner": "quiet_scan"}, "owed"),
        DH.run_wakes({"next_act_owner": "list_dispatch"}), DH.run_wakes({})], [False, True, True, True], "wakes")
    src = open(os.path.join(HERE, "detached_helper.py"), encoding="utf-8").read()
    assert "if run_wakes(rec, owed)" in src, "finish asks run_wakes"
    argv = QS.launch_argv(CFG, "/b.md")
    eq(argv[argv.index("--next-act-owner") + 1], "quiet_scan", "the launch says whose run it is")


def t_a_dry_tick_writes_nothing():
    d = tempfile.mkdtemp(dir=TMP)
    os.environ["RM_QUIET_SCAN_DIR"] = os.path.join(d, "s")
    try:
        launched = []
        fx = {"facts": lambda cfg, st, now: facts(), "account": lambda: (True, ""),
              "launch": lambda cfg: launched.append(1) or (0, "DETACHED u", "u")}
        r = QS.tick(CFG, False, fx, NOW)
        eq((r["decision"], launched, os.path.exists(os.path.join(d, "s"))), ("would_launch", [], False), "dry")
        r = QS.tick(CFG, True, fx, NOW)
        eq((r["decision"], launched), ("launched", [1]), "apply")
        st = json.load(open(os.path.join(d, "s", "state.json")))
        eq(st["run"]["unit"], "u", "state")
        assert json.load(open(os.path.join(d, "s", "reading.json")))["at"] == NOW
        fx["facts"] = lambda cfg, st, now: facts()
        fx["launch"] = lambda cfg: (2, "refused: x", None)
        st["run"] = None
        json.dump(st, open(os.path.join(d, "s", "state.json"), "w"))
        r = QS.tick(CFG, True, fx, NOW + 5)
        eq(r["decision"], "launch_failed", "a refused launch")
        eq(QS.tick(CFG, False, fx, NOW + 60)["decision"], "system_wait", "is not sent again at once")
    finally:
        os.environ["RM_QUIET_SCAN_DIR"] = os.path.join(TMP, "state")


def t_each_limit_names_its_danger():
    c = QS.load_cfg()
    nums = [k for k, v in c.items() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    assert len(nums) >= 4, nums
    for k in nums:
        assert len(c.get("_%s_doc" % k, "")) > 40, k
    eq(c["quiet_days"], 7, "his card: 7 days or more")


def main():
    tests = [t_a_file_changed_in_the_last_seven_days_is_never_picked,
             t_mod_content_first,
             t_a_file_that_needs_no_read_is_not_picked,
             t_a_picked_file_ends_clean_flagged_or_with_a_noted_reason,
             t_a_system_death_releases_the_file,
             t_the_job_yields_to_a_live_mod_step,
             t_the_gates_launch_nothing,
             t_a_run_that_ends_no_file_stops_the_scan,
             t_the_run_is_sonnet_and_knows_the_method,
             t_a_scan_run_does_not_wake_the_conductor,
             t_a_dry_tick_writes_nothing,
             t_each_limit_names_its_danger]
    for fn in tests:
        name = fn.__name__[2:]
        try:
            fn()
            print("PASS " + name)
        except Exception as e:  # noqa: BLE001
            FAILS.append(name)
            print("FAIL %s: %s" % (name, e))
            if not isinstance(e, AssertionError):
                traceback.print_exc()
    print("%d/%d" % (len(tests) - len(FAILS), len(tests)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
