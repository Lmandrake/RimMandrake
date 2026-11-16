#!/usr/bin/env python3
"""selftest_seat_restart_held.py — a held restart unsticks itself, and a held or refused one is seen
(RIMMANDRAKE_PUBLISH_HELD_RESTART_LEDGER_LINE_SILENT_TWO_HOURS).

2026-11-15: the Conductor said HANDOFF READY at 21:23Z; the Dispatcher held the restart for 2 h 17 min (a helper, then
"ledger shard unpublished" for 30 min while other processes in the clone kept appending, then the bridge lock), and
its hourly "held" alarm never reached the Conductor log. Earlier, a stranded clone read its shard as unpushed for ever.
Every case runs on throwaway git repos and simulated windows in a temp dir; the live ledger is never touched.
  dirty shard only       the restart publishes the shard itself and is granted; the Dispatcher no longer holds on it
  append mid-publish     a line appended between the publish and the re-check is published too: still granted
  non-ledger blocks      a publish that fails with a non-ledger dirty file -> refused, naming the file and the fix;
                         the hold reaches the Conductor log (fixture log); a non-ledger local commit is never pushed
  held past the bound    a handoff held past held_tell_s alarms once, with the fixed id, into the Conductor log
  clean                  granted, no commit, the publisher never runs
  stranded clone         shard lines origin already holds under another commit hash read as published
  next turn              a refused or held restart is printed on the window's next prompt (conductor_goodbye.py)
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_seat_restart as B  # noqa: E402  (sets RM_DISPATCHER_STATE etc. to its temp dir)

D, SR, T0 = B.D, B.SR, B.T0
TMP = tempfile.mkdtemp(prefix="selftest_seat_restart_held_")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SHARD = "infrastructure/state/ledger/events/BENCH.jsonl"
FAILS = []
for k in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
    os.environ[k] = "selftest"
for k in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
    os.environ[k] = "selftest@example.invalid"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def git(cwd, *a):
    return subprocess.run(["git", "-c", "commit.gpgsign=false"] + list(a), cwd=cwd, capture_output=True, text=True)


def fixture(name):
    """-> (origin, clone): a bare origin and a clone on main holding the BENCH shard and other.txt, all pushed."""
    root = os.path.join(TMP, name)
    origin, clone = os.path.join(root, "o.git"), os.path.join(root, "c")
    os.makedirs(root)
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", origin], capture_output=True)
    subprocess.run(["git", "clone", "-q", origin, clone], capture_output=True)
    git(clone, "checkout", "-q", "-B", "main")
    os.makedirs(os.path.join(clone, os.path.dirname(SHARD)))
    append(clone, {"n": 0})
    with open(os.path.join(clone, "other.txt"), "w") as f:
        f.write("one\n")
    git(clone, "add", "--", SHARD, "other.txt")
    git(clone, "commit", "-q", "-m", "init")
    git(clone, "push", "-q", "origin", "HEAD:main")
    git(clone, "branch", "-q", "-u", "origin/main")
    git(clone, "fetch", "-q", "origin")
    return origin, clone


def append(clone, ev):
    with open(os.path.join(clone, SHARD), "a", encoding="utf-8") as f:
        f.write(json.dumps(ev) + "\n")


def on_origin(clone):
    git(clone, "fetch", "-q", "origin")
    return git(clone, "show", "origin/main:" + SHARD).stdout


def commits(clone):
    return int(git(clone, "rev-list", "--count", "HEAD").stdout.strip() or 0)


def shard_reader(text):
    return lambda seat: text


def held_obs(**kw):
    o = B.obs(**kw)
    o["seat_restart"]["shard"] = shard_reader(kw.pop("_shard", None))
    return o


# ---------------------------------------------------------------------------------------------------------------------

def test_dirty_shard_only_is_published_and_granted():
    _, clone = fixture("dirty")
    append(clone, {"n": 1, "why": "the window's last note"})
    why = SR.publish_owed_shard("BENCH", clone)
    check(why is None, "a dirty shard alone is published by the restart itself (%s)" % why)
    check('"n": 1' in on_origin(clone), "the uncommitted line is on origin afterwards")
    check(SR.unpublished_shard("BENCH", clone) is None, "and the shard reads published")
    # the Dispatcher: a shard-only hold no longer holds the restart; the kill's re-check publishes
    st = B.fresh()
    o = B.obs(request=B.req())
    o["seat_restart"]["shard"] = shard_reader("%s has uncommitted lines" % SHARD)
    a = B.to_claim(B.sched(), st, o)
    check("restart_kill" in B.dos(a), "a restart held only by unpublished shard lines goes to the kill (%s)" % B.dos(a))


def test_append_between_publish_and_recheck_still_granted():
    _, clone = fixture("race")
    append(clone, {"n": 1})
    calls = []

    def publish():
        why = SR.publish_shard("BENCH", clone)
        if not calls:                     # the 3:39 PM quick check: another process appends right after the publish
            append(clone, {"n": 2, "by": "a peer in the same clone"})
        calls.append(why)
        return why
    why = SR.publish_owed_shard("BENCH", clone, publish=publish)
    check(why is None, "a line appended between publish and re-check is still granted (%s)" % why)
    o = on_origin(clone)
    check('"n": 1' in o and '"n": 2' in o, "both lines are on origin (%d publish runs)" % len(calls))


def test_non_ledger_dirt_blocking_publish_is_refused_and_logged():
    _, clone = fixture("blocked")
    append(clone, {"n": 1})
    with open(os.path.join(clone, "other.txt"), "a") as f:
        f.write("a stray uncommitted edit\n")

    def failing():                        # publish.py's own refusal when a dirty file blocks the landing
        return "./publish rc 1: Blocking uncommitted paths: other.txt"
    why = SR.publish_owed_shard("BENCH", clone, publish=failing)
    check(bool(why) and "other.txt" in why, "the refusal names the non-ledger file (%s)" % why)
    check(bool(why) and "smallest fix" in why.lower(), "the refusal names the smallest fix")
    check('"n": 1' not in on_origin(clone), "nothing claimed published that is not")
    # the kill's re-check records the refusal; the Dispatcher holds on it and says so in the Conductor log
    sch, st = B.sched(), B.fresh()
    o = B.obs(request=B.req())
    o["seat_restart"]["shard"] = shard_reader("%s has uncommitted lines" % SHARD)
    B.run(sch, st, o, T0 + 1)
    rs = st["seat_restart"]["FOUNDRY"]
    SR.note_shard_refused(rs, why, T0 + 100)
    a = B.run(sch, st, o, T0 + SR.DEFAULTS["grace_s"] + 5)
    check("restart_kill" not in B.dos(a), "a refused auto-publish holds the restart (%s)" % B.dos(a))
    first = [x for x in a if x.get("do") == "alarm" and x.get("kind") == "restart:FOUNDRY:held_first"]
    check(first and first[0].get("conductor_log") and "other.txt" in (first[0].get("why") or ""),
          "the first hold is a Conductor-log line naming the file (%s)" % first)
    log = os.path.join(TMP, "conductor_log.md")
    if first:
        D.conductor_log(dict(sch, no_handoff={"conductor_log": log}), first[0], T0 + 130)
    body = open(log).read() if os.path.exists(log) else ""
    check("RAISE FIRST" in body and "other.txt" in body, "the fixture Conductor log holds the line, RAISE FIRST style")
    # a non-ledger local commit is never published by the restart
    _, clone2 = fixture("foreign_commit")
    with open(os.path.join(clone2, "other.txt"), "a") as f:
        f.write("committed, never landed\n")
    git(clone2, "commit", "-q", "-m", "work in progress", "--", "other.txt")
    append(clone2, {"n": 1})
    ran = []
    why = SR.publish_owed_shard("BENCH", clone2, publish=lambda: ran.append(1))
    check(bool(why) and "other.txt" in why and not ran,
          "a non-ledger commit not on origin refuses and is never pushed (%s)" % why)


def test_held_past_bound_alarms_once_with_fixed_id():
    sch, st = B.sched(), B.fresh()
    r = dict(B.req(), ticket="HANDOFF", handoff=True)
    o = B.obs(request=r, bridge={"state": "MEASURED", "holders": ["FOUNDRY"]})
    B.run(sch, st, o, T0 + 1)
    a1 = B.run(sch, st, o, T0 + SR.DEFAULTS["grace_s"] + 5)
    bound = SR.DEFAULTS["held_tell_s"]
    check(bound <= 900, "the bound after a HANDOFF READY is short (%s s)" % bound)
    early = [x for x in a1 if x.get("kind") == "restart:FOUNDRY:held"]
    check(not early, "no bound alarm before the bound")
    a2 = B.run(sch, st, o, T0 + bound + 10)
    al = [x for x in a2 if x.get("do") == "alarm" and x.get("kind") == "restart:FOUNDRY:held"]
    check(len(al) == 1 and al[0].get("conductor_log") and al[0].get("raise_first"),
          "held past the bound -> one alarm, fixed id, into the Conductor log (%s)" % al)
    check(al and "bridge" in al[0]["why"] and "release" in al[0]["why"], "it names what holds and the fix")
    a3 = B.run(sch, st, o, T0 + bound + 300)
    check(not [x for x in a3 if x.get("kind") == "restart:FOUNDRY:held"], "and fires once, not every tick")


def test_clean_is_granted_with_no_commit():
    _, clone = fixture("clean")
    before, ran = commits(clone), []
    why = SR.publish_owed_shard("BENCH", clone, publish=lambda: ran.append(1))
    check(why is None and not ran and commits(clone) == before, "clean -> granted, no publish, no commit")


def test_stranded_clone_reads_published():
    origin, clone = fixture("stranded")
    peer = os.path.join(TMP, "stranded", "peer")
    subprocess.run(["git", "clone", "-q", origin, peer], capture_output=True)
    append(clone, {"n": 1})
    git(clone, "commit", "-q", "-m", "ledger: local", "--", SHARD)
    append(peer, {"n": 1})            # the same line landed under another hash (a replay that left the branch behind)
    git(peer, "commit", "-q", "-m", "ledger: replayed", "--", SHARD)
    git(peer, "push", "-q", "origin", "HEAD:main")
    git(clone, "fetch", "-q", "origin")
    why = SR.unpublished_shard("BENCH", clone)
    check(why is None, "shard lines origin already holds under another hash read as published (%s)" % why)
    append(clone, {"n": 2})
    why = SR.unpublished_shard("BENCH", clone)
    check(bool(why) and "uncommitted" in why, "a line origin lacks still reads unpublished (%s)" % why)


def test_refused_or_held_reaches_the_next_turn():
    SR._write_json(SR.refused_path("BENCH"), {"seat": "BENCH", "session_id": "sid-c", "why": "shard blocked by x.txt",
                                              "n": 4, "ts": T0})
    txt = SR.restart_notice("BENCH", "sid-c", now=T0 + 60) or ""
    check("REFUSED" in txt and "x.txt" in txt, "a refused handoff is printed for its window (%s)" % txt[:120])
    check(SR.restart_notice("BENCH", "sid-other", now=T0 + 60) is None, "another window is not told")
    os.remove(SR.refused_path("BENCH"))
    sp = os.path.join(os.environ["RM_DISPATCHER_STATE"], "state.json")
    os.makedirs(os.path.dirname(sp), exist_ok=True)
    with open(sp, "w") as f:
        json.dump({"seat_restart": {"BENCH": {"state": "pending", "session_id": "sid-c", "ts": T0, "handoff": True,
                                              "held_since": T0, "held_why": "bridge/driver lock held by BENCH"}}}, f)
    txt = SR.restart_notice("BENCH", "sid-c", now=T0 + 900) or ""
    check("HELD" in txt and "bridge" in txt, "a held restart is printed for its window (%s)" % txt[:120])
    hook = os.path.join(REPO, ".claude", "hooks", "conductor_goodbye.py")
    r = subprocess.run([sys.executable, hook], input=json.dumps({"prompt": "how is it going", "session_id": "sid-c"}),
                       capture_output=True, text=True, env=dict(os.environ, AGENT_SEAT="BENCH"))
    check("HELD" in r.stdout and "bridge" in r.stdout, "the UserPromptSubmit hook prints it on his next prompt (%r)"
          % r.stdout[:160])
    r = subprocess.run([sys.executable, hook], input=json.dumps({"prompt": "how is it going", "session_id": "sid-x"}),
                       capture_output=True, text=True, env=dict(os.environ, AGENT_SEAT="BENCH"))
    check(r.stdout.strip() == "", "and prints nothing for another window")
    os.remove(sp)


def main():
    SR.UNFILED = lambda t: None
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                check(False, "%s raised %s: %s" % (name, type(e).__name__, e))
    print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
