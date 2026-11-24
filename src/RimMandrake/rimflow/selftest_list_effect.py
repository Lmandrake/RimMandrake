#!/usr/bin/env python3
"""selftest_list_effect.py - outcome checks on list items, and the tick that closes what already passes.

Item RIMMANDRAKE_BUILD_LIST_OUTCOME_CHECKS_SEVEN_DONE_NEVER_CLOSED; page design/specs/2026-11-22-list-outcome-checks/
boundary.md (each t_ function is one promise of it). Why: 7 of the 48 Conductor debts in the census of 2026-11-22 were
done and never closed.

Offline: a throwaway ledger (RIMFLOW_LEDGER / RIMFLOW_ITEMS), a throwaway check root and git repo, a throwaway control
store and pause file, a throwaway state dir. The real `cli.py` runs as a subprocess against the throwaway ledger.
Written before the code; seen failing on the base (list_effect.py absent, `file --effect` unknown).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CLI = os.path.join(HERE, "cli.py")
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"

FAILS = []
X = {}


def chk(fn, what):
    try:
        cond = fn()
    except Exception as e:  # noqa: BLE001
        cond, what = False, "%s (raised %s: %s)" % (what, type(e).__name__, str(e)[:300])
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def LE():
    import list_effect
    return list_effect


def page(name, text):
    p = os.path.join(X["root"], name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def cli(*args, seat="BENCH"):
    env = dict(os.environ)
    for k in ("CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "RM_ROLE_UNIT"):
        env.pop(k, None)
    env["RIMFLOW_SEAT"] = seat
    r = subprocess.run([sys.executable, CLI] + list(args), cwd=REPO, env=env, capture_output=True, text=True,
                       timeout=180, stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout + r.stderr


def events():
    import model as LM
    LM.EVENTS = os.environ["RIMFLOW_LEDGER"]
    return LM.read()


def world():
    import model as LM
    LM.EVENTS = os.environ["RIMFLOW_LEDGER"]
    LM.ITEMS = os.environ["RIMFLOW_ITEMS"]
    LM.CLOSED = os.path.join(LM.ITEMS, "closed")
    return LM.replay()


def file_item(iid, effect=None, extra=()):
    args = ["file", iid, "--for", "BENCH", "--title", "t " + iid, "--why", "selftest"]
    if effect:
        args += ["--effect", effect]
    return cli(*(args + list(extra)))


def no_hand(*_a, **_k):
    raise AssertionError("this beat must not close")


def calls():
    out = []

    def close(iid, text, why, publish):
        out.append((iid, text))
        return 0, "closed"
    return out, close


# ---- the promises -------------------------------------------------------------------------------------------------

def t_parse_reads_three_forms_and_never_raises():
    L = LE()
    chk(lambda: L.parse("path-has:a/b.md::x y") == {"kind": "path-has", "path": "a/b.md", "text": "x y"},
        "parse path-has gives its path and text")
    chk(lambda: L.parse("path-lacks:a.md::(open)")["kind"] == "path-lacks", "parse path-lacks")
    chk(lambda: L.parse("cmd:grep -q x a.md") == {"kind": "cmd", "cmd": "grep -q x a.md"}, "parse cmd gives the command")
    for bad in ("", None, "looks-done", "path-has:a.md", "path-has:a.md::", "path-has:/etc/passwd::x",
                "path-has:../x.md::y", "cmd:", "cmd:   ", 42):
        chk(lambda b=bad: L.parse(b)["kind"] == "unreadable" and bool(L.parse(b)["why"]),
            "parse %r is unreadable with a reason, no exception" % (bad,))


def t_holds_keeps_could_not_look_apart_from_fails():
    L = LE()
    r = X["root"]
    page("p.md", "alpha\nbeta (open question)\n")
    chk(lambda: L.holds("path-has:p.md::alpha", r) == "holds", "path-has holds when the text is there")
    chk(lambda: L.holds("path-has:p.md::gamma", r) == "fails", "path-has fails when it is not")
    chk(lambda: L.holds("path-has:none.md::x", r) == "fails", "path-has on a missing page fails")
    chk(lambda: L.holds("path-lacks:p.md::(open question)", r) == "fails", "path-lacks fails while the text is there")
    chk(lambda: L.holds("path-lacks:p.md::gamma", r) == "holds", "path-lacks holds when it is gone")
    chk(lambda: L.holds("path-lacks:none.md::x", r) == "unmeasured", "path-lacks on a missing page is unmeasured")
    os.makedirs(os.path.join(r, "adir"), exist_ok=True)
    chk(lambda: L.holds("path-has:adir::x", r) == "unmeasured", "a path that is a folder is unmeasured")
    chk(lambda: L.holds("cmd:true", r) == "holds" and L.holds("cmd:false", r) == "fails", "cmd: exit 0 holds, 1 fails")
    chk(lambda: L.holds("cmd:exit 2", r) == "unmeasured", "cmd: exit 2 is unmeasured, not fails")
    chk(lambda: L.holds("cmd:/no/such/program-xyz", r) == "unmeasured", "cmd: a program that cannot start is unmeasured")
    chk(lambda: L.run("cmd:sleep 5", r, timeout=0.5)[0] == "unmeasured", "cmd: past its deadline is unmeasured")
    chk(lambda: L.holds("cmd:test -f p.md", r) == "holds", "cmd: runs from the root it is given")
    chk(lambda: L.holds("nonsense", r) == "unmeasured", "an unreadable check is unmeasured")
    v, out = L.run("cmd:echo hello-out; exit 1", r)
    chk(lambda: v == "fails" and "hello-out" in out, "run returns the command's output beside its verdict")


def t_decide_closes_only_on_holds_and_leaves_an_item_with_no_check_alone():
    L = LE()
    chk(lambda: [L.decide({"state": "ready", "effect": "cmd:x"}, v) for v in ("holds", "fails", "unmeasured")]
        == ["close", "work", "blind"], "decide: holds close, fails work, unmeasured blind")
    chk(lambda: all(L.decide({"state": "doing", "effect": None}, v) == "no_effect" for v in ("holds", "fails")),
        "decide: no check is no_effect whatever the verdict")
    chk(lambda: all(L.decide({"state": s, "effect": "cmd:x"}, "holds") == "closed"
                    for s in ("done", "dropped", "superseded")), "decide: a closed item stays closed")


def _git(*a, env=None):
    e = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
             GIT_COMMITTER_EMAIL="t@t", **(env or {}))
    subprocess.run(["git", "-C", X["git"]] + list(a), check=True, capture_output=True, env=e, timeout=60)


def t_a_check_that_already_holds_is_refused_at_attach_unless_seen_failing_at_filing():
    L = LE()
    g = X["git"]
    os.makedirs(g, exist_ok=True)
    _git("init", "-q", "-b", "main")
    with open(os.path.join(g, "rules.md"), "w") as f:
        f.write("old text\n")
    _git("add", "rules.md")
    _git("commit", "-q", "-m", "one", env={"GIT_COMMITTER_DATE": "2026-11-01T00:00:00Z",
                                            "GIT_AUTHOR_DATE": "2026-11-01T00:00:00Z"})
    with open(os.path.join(g, "rules.md"), "w") as f:
        f.write("the plan runs to 2026-11-29\n")
    _git("commit", "-q", "-am", "two", env={"GIT_COMMITTER_DATE": "2026-11-10T00:00:00Z",
                                             "GIT_AUTHOR_DATE": "2026-11-10T00:00:00Z"})
    _git("update-ref", "refs/remotes/origin/main", "HEAD")
    import calendar
    t_between = float(calendar.timegm((2026, 11, 6, 0, 0, 0)))     # after commit one, before commit two
    t_after = float(calendar.timegm((2026, 11, 15, 0, 0, 0)))
    seen, why = L.attach_gate("path-has:rules.md::2026-11-29", g)
    chk(lambda: seen is None and "--holds-why" in why, "a check that holds now, new item, no reason: refused with its path")
    seen, why = L.attach_gate("path-has:rules.md::2026-12-25", g)
    chk(lambda: why is None and seen["verdict"] == "fails", "a check that fails now is accepted, red seen now")
    seen, why = L.attach_gate("path-has:rules.md::2026-11-29", g, filed_ts=t_between)
    chk(lambda: why is None and seen["verdict"] == "fails" and seen.get("rev"),
        "a path check that holds now and failed at the filing commit is accepted, red seen at that commit")
    seen, why = L.attach_gate("path-lacks:rules.md::old text", g, filed_ts=t_between)
    chk(lambda: why is None and seen.get("rev"), "path-lacks: the stale text was there at filing: accepted")
    seen, why = L.attach_gate("path-has:rules.md::2026-11-29", g, filed_ts=t_after)
    chk(lambda: seen is None and why, "a path check that held already at filing is refused (it cannot tell done)")
    seen, why = L.attach_gate("cmd:grep -q 2026-11-29 rules.md", g, filed_ts=t_between)
    chk(lambda: seen is None and "--holds-why" in why, "a cmd check that holds now is refused without a reason")
    seen, why = L.attach_gate("cmd:grep -q 2026-11-29 rules.md", g, filed_ts=t_between,
                              holds_why="the ruling was written into the page before the check existed")
    chk(lambda: why is None and seen["verdict"] == "holds" and seen["why"], "with a stated reason it is accepted, noted")
    for vac in ("cmd:true", "cmd: : ", "cmd:exit 0", "cmd:echo done", "cmd:/bin/true"):
        seen, why = L.attach_gate(vac, g, holds_why="because")
        chk(lambda s=seen, w=why: s is None and w, "a vacuous command %r is refused even with a reason" % vac)
    seen, why = L.attach_gate("looks-done", g)
    chk(lambda: seen is None and "path-has:" in why, "an unreadable check is refused, naming the forms")
    seen, why = L.attach_gate("cmd:/no/such/program-xyz", g)
    chk(lambda: seen is None and "unmeasured" in why, "a check that cannot run is refused with its cause")


def t_file_and_effect_record_the_check_and_its_red_reading():
    page("led/page.md", "nothing yet\n")
    rc, out = file_item("RIMMANDRAKE_TEST_LIST_EFFECT_FILED_WITH_A_CHECK", "path-has:led/page.md::DONE MARK")
    chk(lambda: rc == 0, "file --effect with a failing check files (rc %d: %s)" % (rc, out[-300:]))
    w = world()
    it = w.items.get("RIMMANDRAKE_TEST_LIST_EFFECT_FILED_WITH_A_CHECK")
    chk(lambda: it is not None and it.effect == "path-has:led/page.md::DONE MARK", "Item.effect replays the check")
    chk(lambda: it is not None and (it.effect_seen or {}).get("verdict") == "fails", "Item.effect_seen holds the red reading")
    n0 = len(events())
    rc, out = file_item("RIMMANDRAKE_TEST_LIST_EFFECT_ALWAYS_PASSING_CHECK", "cmd:true")
    chk(lambda: rc != 0 and len(events()) == n0, "file --effect cmd:true is refused and writes nothing (rc %d)" % rc)
    rc, out = file_item("RIMMANDRAKE_TEST_LIST_EFFECT_CHECK_GIVEN_LATER")
    rc, out = cli("effect", "RIMMANDRAKE_TEST_LIST_EFFECT_CHECK_GIVEN_LATER", "--check", "cmd:test -f led/absent.md",
                  "--why", "selftest")
    chk(lambda: rc == 0, "effect --check on an open item is recorded (rc %d: %s)" % (rc, out[-300:]))
    it = world().items.get("RIMMANDRAKE_TEST_LIST_EFFECT_CHECK_GIVEN_LATER")
    chk(lambda: it.effect == "cmd:test -f led/absent.md", "the later check replays")
    n0 = len(events())
    rc, out = cli("effect", "RIMMANDRAKE_TEST_LIST_EFFECT_CHECK_GIVEN_LATER", "--check", "cmd:test -f led/page.md",
                  "--why", "selftest")
    chk(lambda: rc != 0 and len(events()) == n0, "effect --check that holds with no reason is refused, nothing written")
    rc, out = cli("effect", "RIMMANDRAKE_TEST_LIST_EFFECT_CHECK_GIVEN_LATER", "--clear", "--why", "selftest")
    chk(lambda: rc == 0 and world().items["RIMMANDRAKE_TEST_LIST_EFFECT_CHECK_GIVEN_LATER"].effect is None,
        "effect --clear removes the check")


def t_the_tick_closes_a_passing_item_as_the_pipelines_act_with_the_output():
    L = LE()
    iid = "RIMMANDRAKE_TEST_LIST_EFFECT_TICK_CLOSES_IT"
    page("led/tick.md", "waiting\n")
    rc, out = file_item(iid, "path-has:led/tick.md::SHIPPED-MARK")
    chk(lambda: rc == 0, "filed the tick's item (%s)" % out[-200:])
    page("led/tick.md", "waiting\nSHIPPED-MARK on 2026-11-22\n")
    rd = L.tick(apply=True, publish=False, root=X["root"], fx={"pause": lambda now: None, "blocked": lambda iid: None})
    row = rd["items"].get(iid) or {}
    chk(lambda: row.get("decision") == "closed_by_check", "the beat closed it (row %s)" % row)
    cl = [e for e in events() if e.get("event") == "close" and e.get("id") == iid]
    chk(lambda: len(cl) == 1, "one close event on the ledger")
    e = cl[0] if cl else {}
    chk(lambda: "path-has:led/tick.md::SHIPPED-MARK" in str(e.get("noCode")), "the close names the check")
    chk(lambda: "SHIPPED-MARK on 2026-11-22" in str(e.get("noCode")), "the close carries the check's output")
    chk(lambda: str(e.get("role_unit") or "").startswith("rm-list-effect"), "the close carries the timer's unit")
    chk(lambda: not any(e.get(k) for k in ("ownerSaid", "byCard", "perRuling")), "the close is not his or the Conductor's")
    ev_path = row.get("evidence") or ""
    chk(lambda: os.path.isfile(ev_path) and "SHIPPED-MARK" in open(ev_path).read(), "the whole output is kept as evidence")
    chk(lambda: world().items[iid].state == "done", "the item replays done")


def t_the_tick_closes_nothing_on_fails_unmeasured_or_no_check():
    L = LE()
    page("led/n.md", "nothing\n")
    a, b, c = ("RIMMANDRAKE_TEST_LIST_EFFECT_STILL_FAILS", "RIMMANDRAKE_TEST_LIST_EFFECT_TURNS_UNMEASURED",
               "RIMMANDRAKE_TEST_LIST_EFFECT_NO_CHECK_ONLY_A_NOTE")
    file_item(a, "path-has:led/n.md::NEVER-THERE")
    page("led/b.sh", "exit 1\n")
    file_item(b, "cmd:sh led/b.sh")
    file_item(c)
    cli("note", c, "--text", "DONE: all finished, close me", "--why", "selftest")
    page("led/b.sh", "exit 3\n")       # b's check now cannot answer: exit 3 is outside 0/1
    got, close = calls()
    rd = L.tick(apply=True, publish=False, root=X["root"],
                fx={"pause": lambda now: None, "blocked": lambda iid: None, "close": close})
    chk(lambda: not got, "no close sent (sent %s)" % got)
    chk(lambda: rd["items"][a]["decision"] == "work", "a failing check reads work")
    chk(lambda: rd["items"][b]["decision"] == "blind", "an unmeasured check reads blind")
    chk(lambda: c not in rd["items"], "an item with no check is not looked at")
    chk(lambda: world().items[b].effect == "cmd:sh led/b.sh", "fixture sane: b carries its check")


def t_the_tick_obeys_pause_and_pipe_off():
    L = LE()
    import control as C
    import pipeline_pause as PP
    iid = "RIMMANDRAKE_TEST_LIST_EFFECT_PAUSED_PASSING"
    page("led/p2.md", "x\n")
    file_item(iid, "path-has:led/p2.md::PASS-NOW")
    page("led/p2.md", "PASS-NOW\n")
    got, close = calls()
    PP.pause(None, "selftest pause", "selftest")
    rd = L.tick(apply=True, publish=False, root=X["root"], fx={"close": close})
    chk(lambda: not got and rd["items"][iid]["decision"] == "pipeline_paused", "the pause closes nothing")
    PP.resume(None, "selftest", "selftest")
    for scope in ("all", "family:list_effect", "item:" + iid):
        C.switch(scope, True, "selftest off")
        rd = L.tick(apply=True, publish=False, root=X["root"], fx={"close": close})
        # `pipe off all` is also the pipeline's pause (pipeline_pause reads the control store): either name holds it
        chk(lambda: not got and rd["items"][iid]["decision"] in ("off", "pipeline_paused"),
            "pipe off %s closes nothing (%s, sent %s)"
            % (scope, rd["items"][iid], got))
        C.switch(scope, False, "selftest on")
    rd = L.tick(apply=True, publish=False, root=X["root"],
                fx={"close": close, "blocked": lambda i: (_ for _ in ()).throw(C.Unreadable("store gone"))})
    chk(lambda: not got and rd["items"][iid]["decision"] == "blind", "an unreadable control store closes nothing")
    rd = L.tick(apply=True, publish=False, root=X["root"], fx={"close": close})
    chk(lambda: len(got) == 1, "with everything on, the same beat closes it (sanity: the gates were what held it)")


def t_the_tick_launches_nothing_and_files_nothing():
    L = LE()
    iid = "RIMMANDRAKE_TEST_LIST_EFFECT_NO_FOLLOW_ON"
    page("led/f.md", "x\n")
    file_item(iid, "path-has:led/f.md::OK-NOW")
    page("led/f.md", "OK-NOW\n")
    n0 = len(events())
    L.tick(apply=True, publish=False, root=X["root"], fx={"pause": lambda now: None, "blocked": lambda i: None})
    new = events()[n0:]
    chk(lambda: bool(new) and {e.get("event") for e in new} == {"close"}, "the beat's only ledger writes are closes (%s)"
        % [e.get("event") for e in new])
    src = open(os.path.join(HERE, "list_effect.py"), encoding="utf-8").read()
    chk(lambda: "systemd-run" not in src and "detached_helper.py" not in src and '"spawn"' not in src,
        "list_effect.py names no launcher and no spawn")


def t_a_refused_close_is_not_sent_again_unchanged():
    L = LE()
    iid = "RIMMANDRAKE_TEST_LIST_EFFECT_CLOSE_REFUSED_ONCE"
    page("led/r.md", "x\n")
    file_item(iid, "path-has:led/r.md::READY")
    page("led/r.md", "READY\n")
    sent, needs = [], []

    def close(i, text, why, publish):
        sent.append(i)
        return 2, "close refused: still owes C1 L1"
    fx = {"pause": lambda now: None, "blocked": lambda i: None, "close": close, "need": lambda t, now: needs.append(t)}
    L.tick(apply=True, publish=False, root=X["root"], fx=fx)
    rd = L.tick(apply=True, publish=False, root=X["root"], fx=fx)
    chk(lambda: sent.count(iid) == 1, "the refused close is sent once over two beats (sent %d)" % sent.count(iid))
    chk(lambda: rd["items"][iid]["decision"] == "close_refused" and "owes C1" in rd["items"][iid]["why"],
        "the second beat reads close_refused with the refusal")
    chk(lambda: len([n for n in needs if iid in n]) == 1, "the Needs Conductor line is said once")
    cli("note", iid, "--text", "criterion C1 settled", "--why", "selftest")
    L.tick(apply=True, publish=False, root=X["root"], fx=fx)
    chk(lambda: sent.count(iid) == 2, "after the item changes, the close is sent again")


def t_a_close_of_an_item_already_done_is_not_a_refusal():
    import types
    L = LE()
    real = L.subprocess.run
    said = ("nothing to publish: this command wrote no ledger or prose path\nA_DONE_ITEM is already `%s`, and this would be "
            "a SECOND one. The first record stands")

    def fake(text, rc):
        L.subprocess.run = lambda *a, **k: types.SimpleNamespace(returncode=rc, stdout=text, stderr="")
        try:
            return L.close_item("A_DONE_ITEM", "t", "w", False)
        finally:
            L.subprocess.run = real
    rc, out = fake(said % "done", 1)
    chk(lambda: rc == 0 and "already" in out, "a close refused as already done is closed (the failure of 2026-11-23)")
    chk(lambda: fake(said % "dropped", 1)[0] == 1, "already dropped is not done: still refused")
    chk(lambda: fake(said.replace("A_DONE_ITEM", "B_OTHER") % "done", 1)[0] == 1, "another item's done word is not this item's")
    chk(lambda: fake("the close gate refused: a criterion is owed", 1)[0] == 1, "any other refusal stays a refusal")
    chk(lambda: fake("closed at abc", 0)[0] == 0, "a close that landed is a close")


def t_a_dry_beat_writes_nothing():
    L = LE()
    iid = "RIMMANDRAKE_TEST_LIST_EFFECT_DRY_BEAT"
    page("led/d.md", "x\n")
    file_item(iid, "path-has:led/d.md::YES")
    page("led/d.md", "YES\n")
    d = tempfile.mkdtemp(prefix="le_dry_")
    os.environ["RM_LIST_EFFECT_DIR"] = d
    n0 = len(events())
    rd = L.tick(apply=False, publish=False, root=X["root"], fx={"pause": lambda now: None, "blocked": lambda i: None})
    chk(lambda: rd["items"][iid]["decision"] == "would_close", "the dry beat says would_close")
    chk(lambda: len(events()) == n0 and not os.listdir(d), "the dry beat wrote no event and no state")
    os.environ["RM_LIST_EFFECT_DIR"] = X["state"]
    shutil.rmtree(d, ignore_errors=True)


def t_closed_reads_item_states_for_a_check():
    L = LE()
    a, b = "RIMMANDRAKE_TEST_LIST_EFFECT_CLOSED_HELPER_DONE", "RIMMANDRAKE_TEST_LIST_EFFECT_CLOSED_HELPER_OPEN"
    file_item(a)
    file_item(b)
    cli("drop", a, "--reason", "selftest", "--why", "selftest")
    chk(lambda: L.closed_main([a]) == 0, "closed: a dropped item reads closed (exit 0)")
    chk(lambda: L.closed_main([a, b]) == 1, "closed: one open item reads 1")
    chk(lambda: L.closed_main([a, "RIMMANDRAKE_TEST_LIST_EFFECT_NEVER_FILED_AT_ALL"]) == 1, "closed: a never-filed item reads 1")
    chk(lambda: L.closed_main([]) == 2, "closed: no ids is 2 (no answer), never 0")
    cli("claim", b, "--why", "selftest")
    chk(lambda: L.closed_main([b]) == 1 and L.closed_main([a, b], started=True) == 0,
        "closed --started: a claimed item passes only with --started")
    chk(lambda: L.closed_main(["RIMMANDRAKE_TEST_LIST_EFFECT_NEVER_FILED_AT_ALL"], started=True) == 1,
        "closed --started: a never-filed item still reads 1")
    saved = os.environ["RIMFLOW_LEDGER"]
    bad = os.path.join(X["root"], "torn.jsonl")
    with open(bad, "w") as f:
        f.write("{not json\n")
    os.environ["RIMFLOW_LEDGER"] = bad
    try:
        rc = L.closed_main([a])
    finally:
        os.environ["RIMFLOW_LEDGER"] = saved
    chk(lambda: rc != 0, "closed: an unreadable ledger never reads 0 (got %s)" % rc)


def t_both_ticks_keep_an_operational_item_open_until_its_live_promise_holds():
    import list_dispatch as LD

    missing, plain, declared, blind = ["RIMMANDRAKE_TEST_CHECK_CLOSE_" + s for s in
                                       ("LIVE_MISSING", "PLAIN_WORK", "UNIT_DECLARES", "GIT_UNREADABLE")]
    check = "path-has:check-close.txt::READY"
    directory = "src/RimMandrake/Utils/systemd"
    line = "unit=y.timer max_age=1h"
    for iid in (missing, plain, declared, blind):
        chk(lambda iid=iid: file_item(iid, check)[0] == 0, "filed fixture item " + iid)
    with patch.dict(X, root=X["git"]):
        for name, body, subject in ((directory + "/x.timer", "[Timer]\n", missing),
                                     ("plain.py", "# ordinary work\n", plain),
                                     (directory + "/y.timer", "# Live: " + line + "\n[Timer]\n", declared),
                                     (directory + "/other.timer", "[Timer]\n", plain + "_OTHER\n\n" + plain)):
            page(name, body)
            _git("add", name)
            _git("commit", "-qm", subject)
        _git("update-ref", "refs/remotes/origin/main", "HEAD")
        page(directory + "/local.timer", "[Timer]\n")
        _git("add", directory + "/local.timer")
        _git("commit", "-qm", plain)
    fake_bin = os.path.join(X["state"], "bin")
    os.mkdir(fake_bin)
    systemctl = os.path.join(fake_bin, "systemctl")
    with open(systemctl, "w", encoding="utf-8") as f:
        f.write('#!/bin/sh\ncase "$2" in\nis-enabled) echo enabled;;\nis-active) echo active;;\n'
                'show) date +%s;;\n*) exit 2;;\nesac\n')
    os.chmod(systemctl, 0o755)
    fx = {"pause": lambda now: None, "blocked": lambda iid: None, "need": no_hand}

    def dispatch():
        facts = {"items": {missing: {"state": "open", "effect": check, "verdict": "holds", "events": 1}}, "runs": {}}
        return LD.tick(LD.load_cfg(), apply=True, fx={"facts": lambda st: facts, "account": lambda: (True, ""),
            "close": lambda iid, text, why: LD.close(iid, text, why, publish=False)})["items"][missing]

    with patch.dict(os.environ, PATH=fake_bin + os.pathsep + os.environ["PATH"],
                    RM_LIST_DISPATCH_DIR=os.path.join(X["state"], "dispatch")):
        with patch.dict(os.environ):
            row = dispatch()
        chk(lambda: world().items[missing].open, "list_dispatch leaves the timer item open without a live line (got %s)"
            % row["decision"])
        page("check-close.txt", "READY\n")
        _git("update-ref", "-d", "refs/remotes/origin/main")
        rows = LE().tick(apply=True, publish=False, root=X["root"], fx=fx)["items"]
        chk(lambda: world().items[blind].open and "could not look" in rows[blind]["why"].lower(),
            "a failed origin/main read is could_not_look and closes nothing (got %s)" % rows[blind]["decision"])
        _git("update-ref", "refs/remotes/origin/main", "HEAD^")
        LE().tick(apply=True, publish=False, root=X["root"], fx=fx)
        chk(lambda: world().items[missing].open, "list_effect also leaves the timer item open without a live line")
        chk(lambda: world().items[plain].state == "done" and not world().items[plain].live,
            "a plain item closes without a promise even if a body, another id or a local commit touches a timer")
        chk(lambda: world().items[declared].live == line, "a holding live line from the item's committed timer is recorded")
        notes = [e["text"] for e in events() if e.get("id") == missing and e.get("event") == "note"]
        chk(lambda: len(notes) == 1 and directory + "/x.timer" in notes[0] and "rimflow close " + missing in notes[0]
            and "--live" in notes[0], "the two ticks write one note naming the timer and the command to pass")
        item_line = "unit=x.timer reading=%s max_age=1h" % os.path.join(X["root"], "timer-reading")
        with open(os.path.join(os.environ["RIMFLOW_ITEMS"], missing + ".md"), "w", encoding="utf-8") as f:
            f.write("## live\n" + item_line + "\n")
        rows = LE().tick(apply=True, publish=False, root=X["root"], fx=fx)["items"]
        chk(lambda: world().items[missing].open and "reading" in rows[missing]["why"],
            "a declared promise whose reading fails leaves the item open")
        page("timer-reading", "fresh\n")
        LE().tick(apply=True, publish=False, root=X["root"], fx=fx)
        chk(lambda: world().items[missing].state == "done" and world().items[missing].live == item_line,
            "the later tick records the item's own live line once it holds")


def main():
    top = tempfile.mkdtemp(prefix="selftest_list_effect_")
    X.update(root=os.path.join(top, "root"), git=os.path.join(top, "git"), state=os.path.join(top, "state"))
    os.makedirs(X["root"])
    os.makedirs(X["state"])
    keys = ("RIMFLOW_LEDGER", "RIMFLOW_ITEMS", "RIMFLOW_GITINDEX", "RIMFLOW_GIT_CWD", "RIMFLOW_PROBE", "RM_LIST_EFFECT_DIR",
            "RM_LIST_EFFECT_ROOT", "RM_CONTROL_DB", "RM_PIPELINE_PAUSE_FILE", "RM_DISPATCHER_STATE", "RM_ROLE_UNIT")
    saved = {k: os.environ.get(k) for k in keys}
    os.environ.update(RIMFLOW_LEDGER=os.path.join(top, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(top, "items"),
                      RIMFLOW_GITINDEX="off", RIMFLOW_GIT_CWD=X["git"], RIMFLOW_PROBE="no-reading", RM_LIST_EFFECT_DIR=X["state"],
                      RM_LIST_EFFECT_ROOT=X["root"], RM_CONTROL_DB=os.path.join(top, "control.db"),
                      RM_PIPELINE_PAUSE_FILE=os.path.join(top, "pause.json"),
                      RM_DISPATCHER_STATE=os.path.join(top, "dstate"))
    os.environ.pop("RM_ROLE_UNIT", None)
    os.makedirs(os.environ["RIMFLOW_ITEMS"])
    try:
        try:
            import control as C
            C.init(os.environ["RM_CONTROL_DB"])
        except Exception as e:  # noqa: BLE001
            print("     (control store init raised %s: %s)" % (type(e).__name__, e))
        for t in (t_parse_reads_three_forms_and_never_raises,
                  t_holds_keeps_could_not_look_apart_from_fails,
                  t_decide_closes_only_on_holds_and_leaves_an_item_with_no_check_alone,
                  t_a_check_that_already_holds_is_refused_at_attach_unless_seen_failing_at_filing,
                  t_file_and_effect_record_the_check_and_its_red_reading,
                  t_the_tick_closes_a_passing_item_as_the_pipelines_act_with_the_output,
                  t_the_tick_closes_nothing_on_fails_unmeasured_or_no_check,
                  t_the_tick_obeys_pause_and_pipe_off,
                  t_the_tick_launches_nothing_and_files_nothing,
                  t_a_refused_close_is_not_sent_again_unchanged,
                  t_a_close_of_an_item_already_done_is_not_a_refusal, t_a_dry_beat_writes_nothing,
                  t_closed_reads_item_states_for_a_check, t_both_ticks_keep_an_operational_item_open_until_its_live_promise_holds):
            try:
                t()
            except Exception as e:  # noqa: BLE001
                chk(lambda: False, "%s (raised %s: %s)" % (t.__name__, type(e).__name__, str(e)[:300]))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(top, ignore_errors=True)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
