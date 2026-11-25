#!/usr/bin/env python3
"""selftest_quiet_scan.py: quiet_scan.py over fake facts and a temp git repo. Nothing is launched; no model.
Page design/specs/2026-11-24-quiet-scan/boundary.md: one test per promise, of its name. Exit 0 all pass, 1 any fail."""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import traceback
from unittest import mock

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
GIT = QS.git
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


def printed(argv):
    """-> (exit code, what main printed)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = QS.main(argv)
    return rc, out.getvalue().strip()


def own_state(st=None):
    """A fresh state directory for one block; the shared one comes back after it."""
    d = tempfile.mkdtemp(dir=TMP)
    if st is not None:
        json.dump(st, open(os.path.join(d, "state.json"), "w"))
    return mock.patch.dict(os.environ, {"RM_QUIET_SCAN_DIR": d})


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
    # gather asks git for origin/main now, and says so when git cannot answer
    for dead in ("fetch", "log"):
        def g(r, *a):
            if a[0] == dead:
                raise QS.Blind("git %s failed" % dead)
            return "" if a[0] == "fetch" else GIT(r, *a)
        with mock.patch.object(QS, "git", g), mock.patch.object(QS, "_flags", dict), \
                mock.patch.object(QS, "_records", dict), mock.patch.object(QS, "_holds", dict):
            f = QS.gather(CFG, {}, t, root)
        assert "git %s failed" % dead in (f["blind"] or ""), "git %s could not answer and gather is not blind: %s" % (dead, f["blind"])
    # a commit landed on origin/main that this clone's HEAD does not hold; an old-dated commit on top hides nothing under it
    git(root, "checkout", "-q", "-b", "landed")
    for days, n in ((2, "edge8.cs"), (40, "About/About.xml")):
        open(os.path.join(root, p, n), "a").write("z\n")
        when = "%d +0000" % (t - days * DAY)
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", n, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
    git(root, "checkout", "-q", "main")
    ch = QS.changed_since(root, 7, t)
    eq((p + "edge8.cs" in ch, p + "About/About.xml" in ch), (True, False), "origin/main, not HEAD; past an old-dated commit")


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
    old, e8 = "src/RimMandrake/M/old.cs", "src/RimMandrake/M/edge8.cs"
    h = QS.sha256(os.path.join(root, old))
    f = QS.gather_files(root, 7, t, readers={"flags": dict, "records": lambda: {e8: {"hash": "0" * 64}}, "holds": dict})
    eq(QS.candidates(f)[:2], [old, e8], "an out-of-date record, gathered, comes after a file never read")
    for ent, want in (({"hash": h, "status": "clean"}, set([old])), ({"hash": h}, set([old])),
                      ({"hash": h, "status": "dirty"}, set()), ({"hash": "0" * 64}, set())):
        f = QS.gather_files(root, 7, t, readers={"flags": lambda: {}, "records": lambda: {old: ent}, "holds": lambda: {}})
        eq(f["clean"], want, "a record %s" % ent)
        assert (old in QS.candidates(f)) == (not want), ent
    f = QS.gather_files(root, 7, t, readers={"flags": lambda: {e8: {}}, "records": lambda: {}, "holds": lambda: {"M": "held"}})
    eq((f["flagged"], f["held"]), (set([e8]), {"M": "held"}), "flags and holds reach the facts")
    # the three default readers are the tools' own
    import code_review_status as CRS
    import mod_owner_hold as MOH
    with mock.patch.object(CRS, "flags", lambda: {"f": 1}), mock.patch.object(CRS, "load", lambda: {"r": {}}), \
            mock.patch.object(MOH, "load", lambda: {"X": {"mod": "X", "date": "d", "said": "s"}}):
        eq((QS._flags(), QS._records(), list(QS._holds())), ({"f": 1}, {"r": {}}, ["X"]), "default readers")


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
    eq(f["picked"], {}, "a file whose picks all ended is not behind the others when it is owed a new read")
    # the run's own two words, through main: the pick is recorded, the same file until it ends, the end's refusal is its exit
    c = p
    with own_state({"run": {"unit": "m1"}}), mock.patch.object(QS, "REPO", root), \
            mock.patch.object(QS, "landed_cfg", lambda r: CFG), \
            mock.patch.object(QS, "gather", lambda cfg, st_, now, root=None: facts(files=files_facts(tracked=[c, q]))):
        eq(printed(["next", "--run", "m1"]), (0, "READ " + q), "next")
        eq([(x["run"], x["path"]) for x in QS.picks()], [("m1", q)], "the pick is recorded")
        eq(printed(["next", "--run", "m1"]), (0, "READ " + q), "a file with no outcome is given again, never a second one")
        eq(len(QS.picks()), 1, "and picked once")
        rc, text = printed(["end", q, "--run", "m1", "--outcome", "noted"])
        assert rc == 2 and "--reason" in text, "a refused end exits 2: %s %s" % (rc, text)
        eq(printed(["end", q, "--run", "m1", "--outcome", "noted", "--reason", "x"])[0], 0, "end")
        eq([e["path"] for e in QS.ends()], [q], "the end is recorded")
        eq(printed(["next", "--run", "m1"]), (0, "READ " + c), "then the next file")

        def dark(*a, **k):
            raise QS.Blind("fetch failed")
        with mock.patch.object(QS, "end", dark):
            eq(printed(["end", c, "--run", "m1", "--outcome", "clean"])[0], 3, "could not look is not ended")
    # look_at, for real: a record line and the file's bytes are landed only when origin/main holds them
    rec = os.path.join(root, QS.REC)
    os.makedirs(rec + "/flags")
    import code_review_status as CRS
    with mock.patch.object(CRS, "ROOT", root), mock.patch.object(CRS, "REC_DIR", rec), \
            mock.patch.object(QS, "git", lambda r, *a: "" if a[0] == "fetch" else GIT(r, *a)):
        git(root, "checkout", "-q", "--", p)
        eq(QS.look_at(root, p), {"record": "DIRTY", "flag": False, "landed": True}, "no record")
        line = json.dumps({"path": p, "sha256": QS.sha256(os.path.join(root, p)), "verdict": "clean", "seat": "T",
                           "ts": "2026-11-24T00:00:00Z", "sha": "x", "date": "2026-11-24", "cleanCount": 1})
        open(os.path.join(rec, "T.jsonl"), "w").write(line + "\n")
        eq(QS.look_at(root, p), {"record": "CLEAN", "flag": False, "landed": False}, "an unlanded record")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "rec")
        eq(QS.look_at(root, p)["landed"], False, "a commit that is not on origin/main")
        git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
        eq(QS.look_at(root, p), {"record": "CLEAN", "flag": False, "landed": True}, "landed")
        open(os.path.join(rec, "flags", "T.jsonl"), "w").write(json.dumps(
            {"event": "flag", "path": p, "seat": "T", "sha256": "x", "ts": "2026-11-24T00:00:00Z", "why": "w"}) + "\n")
        eq(QS.look_at(root, p), {"record": "CLEAN", "flag": True, "landed": False}, "an unlanded flag")
        open(os.path.join(root, p), "a").write("fix\n")
        git(root, "add", QS.REC)
        git(root, "commit", "-q", "-m", "flag")
        git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
        eq(QS.look_at(root, p)["landed"], False, "a fix that is not on origin/main")


def t_a_system_death_releases_the_file():
    root, t = repo()
    import detached_helper as DH
    fin = {"unit": "r", "status": "finished", "result": "success (exited 0)", "clone": "/c", "seat": "BENCH", "at": NOW}
    for rec, live, want in ((None, "dead", {}), (fin, "running", {"r": {"live": True}}),
                            (fin, "launching", {"r": {"live": True}})):
        with mock.patch.object(DH, "read_record", lambda u: rec), mock.patch.object(DH, "live_status", lambda r: live):
            eq(QS._run("r"), want, "%s %s" % (rec, live))
    for res, counts in (("success (exited 0)", True), ("killed (signal TERM)", False), ("timeout (killed KILL)", False)):
        with mock.patch.object(DH, "read_record", lambda u: dict(fin, result=res)), \
                mock.patch.object(DH, "live_status", lambda r: "finished"):
            r = QS._run("r")["r"]
            eq((r["live"], r["counts"]), (False, counts), res)
    eq(QS._run(None), {}, "no run")
    p = "src/RimMandrake/M/old.cs"
    n = len(QS.ends())
    QS.record_pick("u3", p, root, NOW)
    s = {"run": {"unit": "u3"}}
    QS.harvest(s, {"u3": {"live": False, "counts": False, "result": "killed"}}, NOW)
    eq(len(QS.ends()), n, "nothing noted")
    f = QS.gather_files(root, 7, t, readers={"flags": lambda: {}, "records": lambda: {}, "holds": lambda: {}})
    eq(f["picked"], {p: 1}, "a released pick is counted")
    assert not s.get("stopped"), s
    eq(QS.decide(CFG, s, facts(), NOW + 60)["decision"], "system_wait", "waits")
    eq(QS.decide(CFG, s, facts(), NOW + 3601)["decision"], "launch", "then goes")
    with own_state({"run": {"unit": "u3"}}):        # tick waits its setting after a run that did not count
        fx = {"facts": lambda cfg, st, now: facts(runs={"u3": {"live": False, "counts": False, "result": "killed"}}),
              "account": lambda: (True, ""), "launch": lambda cfg: (0, "", "u3c")}
        eq(QS.tick(CFG, True, fx, NOW)["decision"], "system_wait", "tick after a killed run")
        eq(QS._state()["wait_until"], NOW + CFG["system_wait_s"], "system_wait_s")
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
    for d in ("live", "launch", "launched", "launch_wait", "launch_retry", "slots_full", "ready", "repairing", "settling"):
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
    import detached_helper as DH
    recs = [{"unit": "a", "status": "running"}, {"unit": "b", "status": "running"}, {"unit": "c", "status": "finished"}]
    with mock.patch.object(DH, "all_records", lambda: recs), \
            mock.patch.object(DH, "live_status", lambda r: "dead" if r["unit"] == "b" else "running"):
        eq([r["unit"] for r in QS._live_records()], ["a"], "the live runs")
    eq(QS.decide(CFG, {}, facts(blind="the reading is stale"), NOW)["decision"], "blind", "tick, stale reading")
    w = QS.next_word(CFG, {"run": {"unit": "u"}}, facts(busy="Pyrelands is live"), "u", [], NOW)
    eq(w[0], "YIELD", "next")
    eq(QS.next_word(CFG, {"run": {"unit": "u"}}, facts(blind="x"), "u", [], NOW)[0], "YIELD", "next, blind")
    eq(QS.next_word(CFG, {"run": {"unit": "u"}}, facts(), "u", [], NOW), ("READ", "src/RimMandrake/ModA/Src/c.cs"), "idle")


def t_the_gates_launch_nothing():
    D = lambda cfg=CFG, st=None, account=(True, ""), **kw: QS.decide(cfg, st or {}, facts(**kw), NOW, account)
    eq(D()["decision"], "launch", "the green case")
    # gather, for real: each gate's own answer reaches the facts, and one that cannot be read is blind
    import control as C
    import detached_helper as DH
    import maturation_dispatch as MD
    import pipeline_pause as PP
    import scratch_clone as SC
    root, t = repo()
    rdir = tempfile.mkdtemp(dir=TMP)

    def boom(*a, **k):
        raise RuntimeError("unreadable")

    def got(reading_at=t, recs=(), **over):
        json.dump({"at": reading_at, "mods": {}}, open(os.path.join(rdir, "reading.json"), "w"))
        p = {"blocked": lambda spec: None, "blocks": lambda mod, now: None, "pool": lambda dest: None, "run": lambda u: {}}
        p.update(over)
        files = {}

        def gf(r, days, now):
            files["days"] = days
            return files_facts()
        with mock.patch.object(C, "blocked", p["blocked"]), mock.patch.object(PP, "blocks", p["blocks"]), \
                mock.patch.object(SC, "pool_admit", p["pool"]), mock.patch.object(DH, "all_records", lambda: list(recs)), \
                mock.patch.object(DH, "pool_root", lambda: TMP), mock.patch.object(QS, "_run", p["run"]), \
                mock.patch.object(DH, "live_status", lambda r: "running"), mock.patch.object(QS, "gather_files", gf), \
                mock.patch.object(QS, "git", lambda r, *a: ""), \
                mock.patch.dict(os.environ, {"RM_MATURATION_DISPATCH_DIR": rdir}):
            f = QS.gather(CFG, {"run": {"unit": "u"}}, t, root)
        eq(files["days"], 7, "quiet_days")
        return f
    f = got()
    eq((f["off"], f["paused"], f["pool"], f["busy"], f["blind"]), (None,) * 5, "all green")
    eq(got(blocked=lambda s: "off" if s["family"] == "quiet_scan" else None)["off"], "off", "pipe off family:quiet_scan")
    eq(got(blocked=lambda s: "off" if s["family"] == "detached" else None)["off"], "off", "pipe off family:detached")
    eq(got(blocks=lambda mod, now: "paused")["paused"], "paused", "the pause")
    eq(got(pool=lambda dest: "full")["pool"], "full", "the pool")
    eq(got(run=lambda u: {u: {"live": True}})["runs"], {"u": {"live": True}}, "the run")
    assert got(recs=[{"unit": "x", "status": "running", "env": {"RM_CONTROL_MOD": "M"}}])["busy"], "a live mod run"
    assert got(reading_at=t - 601)["blind"], "a stale reading"
    for k in ("blocked", "blocks", "pool", "run"):
        assert got(**{k: boom})["blind"], "%s unreadable" % k
    with mock.patch.object(DH, "drain_refusal", lambda now: "draining"):
        eq(QS.account_gate(), (False, "draining"), "the account drain")
    with mock.patch.object(DH, "drain_refusal", lambda now: None), mock.patch.object(MD, "account_gate", lambda: (False, "HOLD")):
        eq(QS.account_gate(), (False, "HOLD"), "the account pick")
    eq(D(cfg=dict(CFG, enabled=False))["decision"], "disabled", "")
    eq(D(off="OFF by pipe")["decision"], "off", "")
    eq(D(paused="pause all")["decision"], "pipeline_paused", "")
    eq(D(account=(False, "draining"))["decision"], "account_hold", "")
    eq(D(pool="pool full")["decision"], "pool_full", "")
    eq(D(st={"run": {"unit": "u"}}, runs={"u": {"live": True}})["decision"], "live", "")
    eq(D(files=files_facts(tracked=[]))["decision"], "none_left", "")
    # tick asks the account and hands --hand to the decision and to the run it launches
    def ticked(hand=None, account=(True, ""), **kw):
        sent = []
        with own_state():
            fx = {"facts": lambda cfg, st_, now: facts(**kw), "account": lambda: account,
                  "launch": lambda cfg: sent.append(1) or (0, "", "u")}
            return QS.tick(CFG, True, fx, NOW, hand)["decision"], len(sent), (QS._state().get("run") or {}).get("hand")
    eq(ticked(account=(False, "HOLD")), ("account_hold", 0, None), "tick under an account hold")
    eq(ticked(busy="b"), ("yields", 0, None), "tick beside a mod step")
    eq(ticked(hand="why", busy="b"), ("launched", 1, "why"), "tick --hand beside a mod step")
    eq(ticked(), ("launched", 1, None), "tick")
    # the settings that `next` obeys are origin/main's, not those of the run's own clone, which was taken before it started
    cfg = os.path.join(root, QS.CFG_REL)
    os.makedirs(os.path.dirname(cfg))
    json.dump(dict(CFG, enabled=False), open(cfg, "w"))
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "off")
    git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
    json.dump(CFG, open(cfg, "w"))
    with own_state({"run": {"unit": "u"}}), mock.patch.object(QS, "REPO", root), mock.patch.object(QS, "load_cfg", lambda: CFG), \
            mock.patch.object(QS, "gather", lambda cfg_, st_, now, root=None: facts(
                files=files_facts(tracked=["src/RimMandrake/M/old.cs"]))):
        rc, text = printed(["next", "--run", "u"])
        assert text.startswith("YIELD") and "enabled" in text, "disabled on origin/main mid-run: %s" % text
        git(root, "update-ref", "refs/remotes/origin/main", "HEAD~1")
        rc, text = printed(["next", "--run", "u"])
        assert text.startswith("YIELD"), "settings that cannot be read: %s" % text
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
    # a run that asked and was told to yield is no fault, and the next launch waits
    s = {"run": {"unit": "u5"}}
    QS.record_answer("u5", "YIELD", "a mod step", NOW)
    QS.harvest(s, {"u5": {"live": False, "counts": True, "result": "success (0)"}}, NOW)
    assert not s.get("stopped"), s
    eq(QS.decide(CFG, s, facts(), NOW + 60)["decision"], "system_wait", "a run that was told to yield is not sent again at once")
    # a run that never asked read nothing: it stops the scan
    s = {"run": {"unit": "u6"}}
    QS.harvest(s, {"u6": {"live": False, "counts": True, "result": "success (0)"}}, NOW)
    assert s.get("stopped") and "u6" in s["stopped"], s
    # tick itself harvests the ended run, before it decides
    d = tempfile.mkdtemp(dir=TMP)
    os.environ["RM_QUIET_SCAN_DIR"] = d
    try:
        json.dump({"run": {"unit": "u7"}}, open(os.path.join(d, "state.json"), "w"))
        fx = {"facts": lambda cfg, st, now: facts(runs={"u7": {"live": False, "counts": True, "result": "success (0)"}}),
              "account": lambda: (True, ""), "launch": lambda cfg: (0, "", "u8"), "need": lambda text, now: told.append(text)}
        del told[:]
        eq(QS.tick(CFG, True, fx, NOW)["decision"], "stopped", "tick")
        eq(QS.tick(CFG, True, fx, NOW + 600)["decision"], "stopped", "tick again")
        eq(len(told), 1, "tick says it to the Conductor, once")
        eq(printed(["clear", "--why", "fixed"])[0], 0, "clear")
        eq(QS.tick(CFG, False, fx, NOW + 1200)["decision"], "would_launch", "`clear` starts the scan again")
        # the run's own two words, through main: the answer is recorded, the file is picked once, then ended
        st = {"run": {"unit": "u9"}}
        json.dump(st, open(os.path.join(d, "state.json"), "w"))
        with mock.patch.object(QS, "gather", lambda cfg, st_, now, root=None: facts(busy="a mod step")):
            eq(QS.main(["next", "--run", "u9"]), 0, "next")
        eq([a["word"] for a in QS.answers() if a["run"] == "u9"], ["YIELD"], "next records its answer")
    finally:
        os.environ["RM_QUIET_SCAN_DIR"] = os.path.join(TMP, "state")


def t_the_run_is_sonnet_and_knows_the_method():
    argv = QS.launch_argv(CFG, "/b.md")
    eq(argv[argv.index("--model") + 1], "sonnet", "model")
    assert "--max-budget-usd" not in argv
    calls = []

    def run(argv, **kw):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, "DETACHED rm-x\n  item\n", "")
    with mock.patch.object(QS.subprocess, "run", run):
        eq(QS.launch(CFG)[::2], (0, "rm-x"), "the unit launch read")
    with mock.patch.object(QS.subprocess, "run", lambda argv, **kw: subprocess.CompletedProcess(argv, 3, "DETACHED rm-x\n", "")):
        eq(QS.launch(CFG)[2], None, "a refused launch has no unit")
    eq(calls, [QS.launch_argv(CFG, QS.ROLE)], "the launch sends the sonnet argv with the role file as its brief")
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
    import re as _re   # the argument's name moved (owed -> said); the guard on the wake must not
    assert _re.search(r"wake_conductor\([^\n]*\) if run_wakes\(rec, \w+\)", src), "finish asks run_wakes"
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
        calls = []
        with mock.patch.object(QS, "tick", lambda cfg, apply, **kw: calls.append((apply, kw["hand"])) or r):
            for argv in (["tick"], ["tick", "--apply"], ["tick", "--apply", "--hand", "why"]):
                printed(argv)
        eq(calls, [(False, None), (True, None), (True, "why")], "the command line acts only with --apply")
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
