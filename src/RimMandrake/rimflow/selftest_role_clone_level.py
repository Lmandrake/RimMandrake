#!/usr/bin/env python3
"""selftest_role_clone_level.py — a stranded commit in a role clone never kills the role silently
(RIMMANDRAKE_LAND_STRANDED_ROLE_COMMIT_OPERATIONS_DEAD_FOUR_HOURS). One check per promise of
design/specs/2026-11-19-role-clone-level/boundary.md, same names. Offline: real git on a temp bare origin and its
clones (land.sh pushes to that file remote only), fake launch runners, no systemd.
"""
import os
import shlex
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="rcl_")
os.environ["RM_ROLE_CLONE_ROOT"] = os.path.join(TMP, "roles")          # read by role_clones at import
for k, v in (("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@t"), ("GIT_COMMITTER_NAME", "t"),
             ("GIT_COMMITTER_EMAIL", "t@t")):
    os.environ[k] = v
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))

SHARD = "infrastructure/state/ledger/events/BENCH.jsonl"
FAILS = []
N = [0]


def check(cond, name, said=""):
    print(("PASS " if cond else "FAIL ") + name + (" (%s)" % said if said else ""))
    if not cond:
        FAILS.append(name)


def git(repo, *a, check_rc=True):
    r = subprocess.run(["git", "-C", repo] + list(a), capture_output=True, text=True)
    if check_rc and r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr))
    return r.stdout.strip()


def fixture(name="Operations"):
    """-> (clone, peer, origin): a bare origin, a role clone ROOT/<name> and a peer clone that moves origin."""
    N[0] += 1
    base = os.path.join(TMP, "f%d" % N[0])
    origin, seed = os.path.join(base, "origin.git"), os.path.join(base, "seed")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", origin], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", seed], check=True)
    os.makedirs(os.path.join(seed, os.path.dirname(SHARD)))
    with open(os.path.join(seed, ".gitattributes"), "w") as f:
        f.write("infrastructure/state/ledger/events/*.jsonl merge=union\n")
    with open(os.path.join(seed, SHARD), "w") as f:
        f.write('{"n":0}\n')
    with open(os.path.join(seed, "code.txt"), "w") as f:
        f.write("one\n")
    git(seed, "add", "--", ".gitattributes", SHARD, "code.txt")
    git(seed, "commit", "-q", "-m", "seed")
    git(seed, "remote", "add", "origin", origin)
    git(seed, "push", "-q", "origin", "main")
    clone = os.path.join(os.environ["RM_ROLE_CLONE_ROOT"], name)
    if os.path.exists(clone):
        subprocess.run(["rm", "-rf", clone], check=True)
    os.makedirs(os.path.dirname(clone), exist_ok=True)
    subprocess.run(["git", "clone", "-q", origin, clone], check=True)
    peer = os.path.join(base, "peer")
    subprocess.run(["git", "clone", "-q", origin, peer], check=True)
    return clone, peer, origin


def commit(repo, path, line, msg):
    with open(os.path.join(repo, path), "a") as f:
        f.write(line + "\n")
    git(repo, "add", "--", path)
    git(repo, "commit", "-q", "-m", msg, "--", path)
    return git(repo, "rev-parse", "HEAD")


def origin_file(origin, path):
    return git(origin, "show", "main:" + path, check_rc=False)


def level_after(clone):
    git(clone, "fetch", "-q", "origin")
    return git(clone, "rev-parse", "HEAD") == git(clone, "rev-parse", "origin/main")


def mods():
    import role_clones as RC
    import role_launch as RL
    return RC, RL

def t_a_level_clone_launches_without_a_fetch():
    RC, RL = mods()
    level = getattr(RC, "level", None)
    clone, peer, origin = fixture()
    git(clone, "remote", "set-url", "origin", os.path.join(TMP, "no-such-remote.git"))
    got = level(clone) if level else {}
    check(got.get("state") == "level", "a-level-clone-launches-without-a-fetch", got.get("state"))


def t_a_stranded_ledger_commit_is_landed_and_the_clone_levelled():
    RC, RL = mods()
    level = getattr(RC, "level", None)
    clone, peer, origin = fixture()
    mine = commit(clone, SHARD, '{"n":"mine"}', "ledger: ops note")
    commit(peer, SHARD, '{"n":"peer"}', "ledger: peer note")
    git(peer, "push", "-q", "origin", "main")
    got = level(clone) if level else {}
    body = origin_file(origin, SHARD)
    check(got.get("state") == "landed" and len(got.get("landed") or []) == 1 and '"mine"' in body and '"peer"' in body
          and level_after(clone), "a-stranded-ledger-commit-is-landed-and-the-clone-levelled",
          "%s landed=%s" % (got.get("state"), got.get("landed")))


def t_a_stranded_code_commit_refuses_with_the_exact_fix():
    RC, RL = mods()
    level = getattr(RC, "level", None)
    clone, peer, origin = fixture()
    before = git(origin, "rev-parse", "main")
    code = commit(clone, "code.txt", "two", "code change")
    got = level(clone) if level else {}
    untouched = git(origin, "rev-parse", "main") == before
    fix = got.get("fix") or ""
    ran = subprocess.run(["sh", "-c", fix], capture_output=True, text=True) if fix else None
    check(got.get("state") == "stranded" and untouched and code[:10] in fix and ran is not None and ran.returncode == 0
          and "two" in origin_file(origin, "code.txt") and level_after(clone),
          "a-stranded-code-commit-refuses-with-the-exact-fix",
          "%s untouched=%s fix rc=%s" % (got.get("state"), untouched, ran and ran.returncode))


def t_a_stranded_code_commit_fix_holds_when_origin_moved_the_same_files():
    """RIMMANDRAKE_TRACE_DESIGNER_ROLE_CLONE_VANISHED_OPERATIONS_FAILS (2026-11-21): the Operations run's fix commit
    (fedb182ffd: maturation_autonomy.py + its BENCH shard) was stranded; origin then changed both files. The printed
    fix landed it (80f584b4cc) but its seat_sync refused, "NOT on origin/main": landed_twin cannot prove a twin whose
    file origin changed since, so every Operations launch stayed refused STRANDED."""
    RC, RL = mods()
    level = getattr(RC, "level", None)
    clone, peer, origin = fixture()
    with open(os.path.join(peer, "long.txt"), "w") as f:
        f.write("".join("line %d\n" % i for i in range(30)))
    git(peer, "add", "--", "long.txt")
    git(peer, "commit", "-q", "-m", "long file", "--", "long.txt")
    git(peer, "push", "-q", "origin", "main")
    git(clone, "pull", "-q", "--ff-only", "origin", "main")
    with open(os.path.join(clone, "long.txt"), "w") as f:
        f.write("".join("line %d%s\n" % (i, " MINE" if i == 25 else "") for i in range(30)))
    with open(os.path.join(clone, SHARD), "a") as f:
        f.write('{"n":"mine"}\n')
    git(clone, "commit", "-q", "-m", "code fix and its ledger line", "--", "long.txt", SHARD)
    code = git(clone, "rev-parse", "HEAD")
    git(peer, "pull", "-q", "--ff-only", "origin", "main")
    with open(os.path.join(peer, "long.txt"), "w") as f:
        f.write("".join("line %d%s\n" % (i, " THEIRS" if i == 2 else "") for i in range(30)))
    with open(os.path.join(peer, SHARD), "a") as f:
        f.write('{"n":"peer"}\n')
    git(peer, "commit", "-q", "-m", "origin moves the same files", "--", "long.txt", SHARD)
    git(peer, "push", "-q", "origin", "main")
    got = level(clone) if level else {}
    fix = got.get("fix") or ""
    ran = subprocess.run(["sh", "-c", fix], capture_output=True, text=True) if fix else None
    body = origin_file(origin, "long.txt")
    check(got.get("state") == "stranded" and code[:10] in fix and ran is not None and ran.returncode == 0
          and "MINE" in body and "THEIRS" in body and level_after(clone),
          "a-stranded-code-commit-refuses-with-the-exact-fix",
          "origin moved the same files: %s fix rc=%s %s" % (got.get("state"), ran and ran.returncode,
                                                             ((ran.stderr if ran else "") or "").strip()[-200:]))


def _role(RC, name="Designer"):
    return {"name": name, "seat": "BENCH", "clone": RC.clone_of(name), "model": "opus", "run_max_s": 1000}


def t_a_missing_clone_is_made_in_its_own_unit_and_the_launch_waits():
    """RIMMANDRAKE_TRACE_DESIGNER_ROLE_CLONE_VANISHED_OPERATIONS_FAILS: the clones of the six disabled roles were removed
    by hand 2026-11-18; the Pyrelands chain ran the Designer by run-now, refused "role clone ... is missing" every beat
    08:02Z-09:41Z 2026-11-21. A clone takes 26-153 s (measured 2026-11-18), past any beat: its own unit makes it."""
    RC, RL = mods()
    r = _role(RC)
    calls = []

    def started(argv, **kw):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, "", "")

    def already(argv, **kw):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 1, "", "Failed to start transient service unit: Unit %s.service was "
                                           "already loaded or has a fragment file." % RC.maker_unit("Designer"))

    def nobus(argv, **kw):
        return subprocess.CompletedProcess(argv, 1, "", "Failed to connect to bus")
    ok, out, _ = RL.launch(r, "u1", "m", TMP, "/bin/claude", runner=started)
    maker = calls[0] if len(calls) == 1 else []
    first = (not ok and out.startswith(RC.MAKING) and maker[:1] == ["systemd-run"] and RC.maker_unit("Designer") in maker
             and maker[-2:] == ["ensure", "Designer"])
    calls.clear()
    ok2, out2, _ = RL.launch(r, "u2", "m", TMP, "/bin/claude", runner=already)
    with open(RC.maker_log("Designer"), "w") as f:
        f.write("OK earlier\nFAILED scratch_clone failed (exit 1): disk full\n")
    calls.clear()
    ok3, out3, _ = RL.launch(r, "u3", "m", TMP, "/bin/claude", runner=started)
    os.remove(RC.maker_log("Designer"))
    ok4, out4, _ = RL.launch(r, "u4", "m", TMP, "/bin/claude", runner=nobus)
    os.makedirs(RC.clone_of("Designer"))
    calls.clear()
    ok5, out5, _ = RL.launch(r, "u5", "m", TMP, "/bin/claude", runner=started)
    no_unit5 = not calls
    os.rmdir(RC.clone_of("Designer"))
    check(first and not ok2 and out2.startswith(RC.MAKING) and not ok3 and not out3.startswith(RC.MAKING)
          and "disk full" in out3 and len(calls) == 0 and not ok4 and "bus" in out4 and not out4.startswith(RC.MAKING)
          and not ok5 and no_unit5 and "not a git clone" in out5,
          "a-missing-clone-is-made-in-its-own-unit-and-the-launch-waits",
          "made: %s | running: %s | last FAILED: %s | no bus: %s | not a clone: %s" % (
              out[:60], out2[:40], out3[:60], out4[:60], out5[:60]))


def t_a_clone_is_made_under_a_hidden_name_and_renamed():
    RC, RL = mods()
    import shutil
    seen = []

    def fake_scratch(argv, env=None, **kw):
        dest = os.path.join(env["RM_SCRATCH_ROOT"], env["RM_SEAT"], argv[argv.index("--name") + 1])
        seen.append((dest, os.path.exists(RC.clone_of("DesignerCodex"))))
        os.makedirs(os.path.join(dest, ".git"))
        return subprocess.CompletedProcess(argv, 0, dest + "\n", "")

    def half(argv, env=None, **kw):
        os.makedirs(os.path.join(env["RM_SCRATCH_ROOT"], env["RM_SEAT"], argv[argv.index("--name") + 1], ".git"))
        return subprocess.CompletedProcess(argv, 1, "", "fetch failed")
    ok, said = RC.ensure("DesignerCodex", runner=fake_scratch)
    made = (ok and os.path.isdir(os.path.join(RC.clone_of("DesignerCodex"), ".git")) and len(seen) == 1
            and not RC.is_role_clone(seen[0][0]) and not seen[0][1] and not os.path.exists(seen[0][0]))
    shutil.rmtree(RC.clone_of("DesignerCodex"))
    os.makedirs(os.path.join(RC.part_of("DesignerCodex"), ".git"))      # a make killed half-way
    ok2, said2 = RC.ensure("DesignerCodex", runner=half)
    check(made and not ok2 and not os.path.exists(RC.clone_of("DesignerCodex")) and not os.path.exists(RC.part_of("DesignerCodex")),
          "a-clone-is-made-under-a-hidden-name-and-renamed", "%s | %s | %s" % (seen, said, said2))


def t_the_launch_takes_the_prep_done_before_its_run_record():
    RC, RL = mods()
    r = _role(RC, "Producer")
    os.makedirs(os.path.join(RC.clone_of("Producer"), ".git"), exist_ok=True)
    lv = []
    ok_runner = lambda argv, **kw: subprocess.CompletedProcess(argv, 0, "", "")   # noqa: E731
    RL.launch(dict(r, _prepared={"refused": None, "lv": None}), "u6", "m", TMP, "/bin/claude", runner=ok_runner,
              level=lambda c: lv.append(c) or {"state": "level"})
    p = RL.prepare_clone(r, runner=ok_runner, level=lambda c: {"state": "stranded", "why": "1 commit", "fix": "F"})
    ok, out, _ = RL.launch(dict(r, _prepared=p), "u7", "m", TMP, "/bin/claude", runner=ok_runner)
    check(not lv and p["refused"].startswith(RC.STRANDED) and not ok and out == p["refused"],
          "the-launch-takes-the-prep-done-before-its-run-record", "levelled again: %s; prep %s" % (lv, p))


def t_a_mixed_strand_lands_the_ledger_and_refuses_the_rest():
    RC, RL = mods()
    level = getattr(RC, "level", None)
    clone, peer, origin = fixture()
    led = commit(clone, SHARD, '{"n":"mixed"}', "ledger: mixed")
    code = commit(clone, "code.txt", "three", "code change")
    got = level(clone) if level else {}
    fix = got.get("fix") or ""
    check(got.get("state") == "stranded" and len(got.get("landed") or []) == 1 and '"mixed"' in origin_file(origin, SHARD)
          and code[:10] in fix and led[:10] not in fix and "three" not in origin_file(origin, "code.txt"),
          "a-mixed-strand-lands-the-ledger-and-refuses-the-rest", "%s landed=%s" % (got.get("state"), got.get("landed")))


def _twin_fixture():
    """-> (clone, peer, origin, mine): the clone holds a ledger commit whose twin (a cherry-pick) is on origin, and
    origin moved on past it: ahead 1, behind 3, nothing unlanded. RIMMANDRAKE_TRACE_DESIGNER_TWIN_COMMIT_LAND_SAID_LEVEL
    (2026-11-21): the Designer clone sat 3 h at ahead 1 / behind 82 like this while every land unit said `level`."""
    clone, peer, origin = fixture("DesignerTwin")
    mine = commit(clone, SHARD, '{"n":"twin"}', "ledger: BENCH role run (role clone Designer)")
    with open(os.path.join(peer, "peer.txt"), "w") as f:        # origin moves first, so the twin is its own commit
        f.write("peer\n")
    git(peer, "add", "--", "peer.txt")
    git(peer, "commit", "-q", "-m", "origin moved first", "--", "peer.txt")
    git(peer, "fetch", "-q", clone, "main")
    git(peer, "cherry-pick", mine)
    assert git(peer, "rev-parse", "HEAD") != mine
    commit(peer, "code.txt", "origin moved on", "a later commit on origin")
    git(peer, "push", "-q", "origin", "main")
    return clone, peer, origin, mine


def t_a_twin_only_clone_is_moved_never_read_level_while_ahead():
    RC, RL = mods()
    clone, peer, origin, mine = _twin_fixture()
    got = RC.level(clone)
    ahead = git(clone, "rev-list", "refs/remotes/origin/main..HEAD")
    check(got.get("state") in ("level", "landed") and not ahead and level_after(clone)
          and git(origin, "rev-list", "--count", "main") == "4",
          "a-twin-only-clone-is-moved-never-read-level-while-ahead",
          "state=%s ahead=%s" % (got.get("state"), len(ahead.split())))
    # the land unit (ExecStopPost) on the same shape: ok, and the clone is level after it
    clone, peer, origin, mine = _twin_fixture()
    res = RC.land(clone, "BENCH", tidy=lambda c, settle_min: "nothing to land", leveller=RC.level)
    check(res["ok"] and not git(clone, "rev-list", "refs/remotes/origin/main..HEAD") and level_after(clone),
          "a-twin-only-clone-is-moved-never-read-level-while-ahead", "land: ok=%s level=%s" % (res["ok"], res["level"]))


def t_a_twin_held_by_dirt_is_stranded_with_its_fix():
    RC, RL = mods()
    clone, peer, origin, mine = _twin_fixture()
    with open(os.path.join(clone, "code.txt"), "w") as f:      # a real overlap with origin's later code.txt
        f.write("one\nMY UNCOMMITTED EDIT\n")
    got = RC.level(clone)
    fix = got.get("fix") or ""
    still_ahead = bool(git(clone, "rev-list", "refs/remotes/origin/main..HEAD"))
    res = RC.land(clone, "BENCH", tidy=lambda c, settle_min: "nothing to land", leveller=RC.level)
    check(got.get("state") == "stranded" and still_ahead and "seat_sync.py" in fix and mine[:12] in fix
          and "code.txt" in (got.get("why") or "") and not res["ok"] and "seat_sync.py" in (res.get("why") or ""),
          "a-twin-held-by-dirt-is-stranded-with-its-fix",
          "state=%s why=%s fix=%s land ok=%s" % (got.get("state"), (got.get("why") or "")[:160], fix[-120:], res["ok"]))


def t_could_not_look_is_unmeasured_not_level():
    RC, RL = mods()
    level = getattr(RC, "level", None)
    clone, peer, origin = fixture()
    commit(clone, SHARD, '{"n":"blind"}', "ledger: blind")
    git(clone, "remote", "set-url", "origin", os.path.join(TMP, "no-such-remote.git"))
    try:
        got = level(clone) if level else {}
        raised = None
    except Exception as e:  # noqa: BLE001 - the promise is that it does not raise
        got, raised = {}, e
    check(raised is None and got.get("state") == "UNMEASURED" and got.get("why"),
          "could-not-look-is-unmeasured-not-level", "%s %s" % (got.get("state"), raised or got.get("why")))


def t_the_launch_refuses_a_stranded_clone_before_systemd_run():
    RC, RL = mods()
    level = getattr(RC, "level", None)
    clone, peer, origin = fixture()
    role = {"name": "Operations", "seat": "BENCH", "clone": clone, "model": "opus", "run_max_s": 1000}
    called, asked = [], []
    stranded = {"state": "stranded", "landed": [], "left": [{"sha": "abc1234", "subject": "x", "paths": ["code.txt"]}],
                "fix": "LAND_REPO=%s sh land.sh abc1234 code.txt" % clone, "why": "1 commit not ledger-only"}
    try:
        ok, out, _ = RL.launch(role, "u1", "m", TMP, "/bin/claude", runner=lambda *a, **k: called.append(a),
                               level=lambda c: (asked.append(c), stranded)[1])
        ok2, out2, _ = RL.launch(dict(role, pin_refused="pin test"), "u2", "m", TMP, "/bin/claude",
                                 runner=lambda *a, **k: called.append(a),
                                 level=lambda c: {"state": "landed", "landed": ["abc"], "left": [], "fix": None})
        err = None
    except TypeError as e:          # the base commit's launch takes no level=
        ok = ok2 = True
        out = out2 = ""
        err = e
    check(err is None and not ok and not called and out.startswith("STRANDED:") and "NOT RUNNING" in out
          and "Operations" in out and stranded["fix"] in out and asked == [clone]
          and out2.startswith("REFUSED by control: pin test"),
          "the-launch-refuses-a-stranded-clone-before-systemd-run", err or out[:120])


def t_the_stop_post_land_lands_a_committed_shard():
    RC, RL = mods()
    level = getattr(RC, "level", None)
    clone, peer, origin = fixture()
    commit(clone, SHARD, '{"n":"committed"}', "ledger: committed, never published")
    res = RC.land(clone, "BENCH", tidy=lambda c, settle_min: "nothing to land")
    landed_ok = res["ok"] and '"committed"' in origin_file(origin, SHARD) and level_after(clone)
    commit(clone, "code.txt", "four", "code change")
    res2 = RC.land(clone, "BENCH", tidy=lambda c, settle_min: "nothing to land")
    check(landed_ok and not res2["ok"] and "land.sh" in (res2.get("why") or ""),
          "the-stop-post-land-lands-a-committed-shard", "first ok=%s second why=%s" % (res["ok"], (res2.get("why") or "")[:80]))


def t_a_stranded_launch_raises_one_not_running_alarm():
    RC, RL = mods()
    level = getattr(RC, "level", None)
    import dispatcher as D
    act = getattr(D, "launch_failed_action", None)
    a = {"role": "Operations", "unit": "u1", "ticket": "T1"}
    if act:
        one = act(a, "STRANDED: role Operations is NOT RUNNING: ... To pass: X", True, "now")
        two = act(dict(a, unit="u2"), "STRANDED: role Operations is NOT RUNNING: ... To pass: X", True, "now")
        other = act(a, "systemd-run exit 1: no", True, "now")
        good = (one["kind"] == two["kind"] == "role:Operations:not_running" and one.get("conductor_log")
                and "NOT RUNNING" in (one.get("raise_first") or "") and "To pass: X" in one["why"]
                and other["kind"] == "role:Operations:launch_failed" and not other.get("conductor_log"))
    else:
        good = False
    check(good, "a-stranded-launch-raises-one-not-running-alarm")


def main():
    t_a_level_clone_launches_without_a_fetch()
    t_a_stranded_ledger_commit_is_landed_and_the_clone_levelled()
    t_a_stranded_code_commit_refuses_with_the_exact_fix()
    t_a_stranded_code_commit_fix_holds_when_origin_moved_the_same_files()
    t_a_mixed_strand_lands_the_ledger_and_refuses_the_rest()
    t_a_twin_only_clone_is_moved_never_read_level_while_ahead()
    t_a_twin_held_by_dirt_is_stranded_with_its_fix()
    t_could_not_look_is_unmeasured_not_level()
    t_the_launch_refuses_a_stranded_clone_before_systemd_run()
    t_the_stop_post_land_lands_a_committed_shard()
    t_a_stranded_launch_raises_one_not_running_alarm()
    t_a_missing_clone_is_made_in_its_own_unit_and_the_launch_waits()
    t_a_clone_is_made_under_a_hidden_name_and_renamed()
    t_the_launch_takes_the_prep_done_before_its_run_record()
    print("%d check(s) failed" % len(FAILS) if FAILS else "all checks passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        subprocess.run(["rm", "-rf", TMP])
