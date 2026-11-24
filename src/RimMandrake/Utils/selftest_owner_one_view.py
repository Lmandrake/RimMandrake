#!/usr/bin/env python3
"""selftest_owner_one_view.py: the promises of design/specs/2026-11-23-owner-one-view/boundary.md.

    python3 src/RimMandrake/Utils/selftest_owner_one_view.py

Fixtures only: a temp state directory, a temp transcript, fake items and run records. No ledger, no network. Before
no_home.py and owner_queue.one_view existed every test was RED: no count, no shared view.
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rimflow"))
TMP = tempfile.mkdtemp(prefix="selftest_owner_one_view_")
os.environ["RM_OWNER_VIEW_DIR"] = TMP
try:
    import no_home as NH  # noqa: E402
except ImportError:
    NH = None
import owner_queue as OQ  # noqa: E402
import probe_his_words as P  # noqa: E402

NOW = 1_800_000_000.0
H = 3600.0
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def need():
    assert NH is not None, "no no_home.py: no count of needs not filed anywhere"
    assert hasattr(OQ, "one_view"), "owner_queue has no one_view"


def boom():
    raise OSError("cannot read")


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def t_count_sums_the_readable_sources():
    need()
    r = NH.count({"a": lambda: ["m1", "m2"], "b": boom, "c": lambda: ["r1"]})
    assert r["no_home"] == 3 and r["by_source"] == {"a": 2, "c": 1} and r["unmeasured"] == ["b"], r
    many = NH.count({"a": lambda: ["x%d" % i for i in range(20)]})
    assert many["no_home"] == 20 and len(many["names"]["a"]) == NH.NAMES_SHOWN, many


def t_no_readable_source_is_none_never_zero():
    need()
    assert NH.count({})["no_home"] is None and NH.count({"a": boom})["no_home"] is None
    assert NH.count({"a": lambda: None})["unmeasured"] == ["a"]        # no answer is not an empty answer
    z = NH.count({"a": lambda: []})
    assert z["no_home"] == 0 and z["by_source"] == {"a": 0} and z["unmeasured"] == []


def t_an_unanswered_card_is_a_need():
    need()
    assert NH.unanswered_cards(["c1", "c2", "c3", "c1"], {"c2"}) == ["c1", "c3"]
    assert NH.unanswered_cards([], set()) == []
    d = tempfile.mkdtemp(prefix="cards_", dir=TMP)
    f = os.path.join(d, "s.jsonl")

    def ask(cid, t, q):
        return {"type": "assistant", "timestamp": iso(t), "message": {"content": [
            {"type": "tool_use", "name": "AskUserQuestion", "id": cid, "input": {"questions": [{"question": q}]}}]}}

    def res(cid, t, err=False):
        return {"type": "user", "timestamp": iso(t), "message": {"content": [
            {"type": "tool_result", "tool_use_id": cid, "is_error": err, "content": "x"}]}}
    rows = [ask("a", NOW - 5 * H, "answered?"), res("a", NOW - 5 * H + 10),
            ask("r", NOW - 4 * H, "refused by a hook?"), res("r", NOW - 4 * H + 1, err=True),
            ask("old", NOW - 9 * 86400, "outside the window"),
            ask("live", NOW - 60, "on screen now")]
    with open(f, "w") as fh:
        fh.write("\n".join(json.dumps(x) for x in rows) + "\n")
    c = P.cards(iso(NOW - 3 * 86400), iso(NOW), files=[f])
    assert c["asked"] == ["a", "r", "live"] and c["answered"] == {"a"} and c["on_screen"] == {"live"}, c
    left = NH.unanswered_cards([x for x in c["asked"] if x not in c["on_screen"]], c["answered"])
    assert left == ["r"], left


def t_an_ended_run_with_no_later_act_is_a_need():
    need()
    items = {"OPEN": {"state": "ready", "effect": None}, "LANE": {"state": "ready", "effect": "cmd:false"},
             "DONE": {"state": "done", "effect": None}, "ACTED": {"state": "ready", "effect": None},
             "LIVE": {"state": "doing", "effect": None}, "OLD": {"state": "ready", "effect": None},
             "WAITED": {"state": "doing", "effect": None, "wait_until": iso(NOW + 86400)},
             "BLOCKED": {"state": "ready", "effect": None, "blocked": True},
             "LEFT": {"state": "doing", "effect": None}, "STAGE": {"state": "doing", "effect": None}}
    recs = [{"unit": "u1", "item": "OPEN", "ended": NOW - 2 * H, "status": "finished"},
            {"unit": "u0", "item": "OPEN", "ended": NOW - 9 * H, "status": "finished"},
            {"unit": "u2", "item": "LANE", "ended": NOW - 2 * H, "status": "finished"},
            {"unit": "u3", "item": "DONE", "ended": NOW - 2 * H, "status": "finished"},
            {"unit": "u4", "item": "ACTED", "ended": NOW - 2 * H, "status": "finished"},
            {"unit": "u5", "item": "LIVE", "ended": NOW - 5 * H, "status": "finished"},
            {"unit": "u6", "item": "LIVE", "at": NOW - H, "status": "running", "live_state": "running"},
            {"unit": "u7", "item": "OLD", "ended": NOW - NH.WINDOW_S - H, "status": "finished"},
            {"unit": "u8", "item": "WAITED", "at": NOW - 3 * H, "ended": NOW - 2 * H, "status": "finished"},
            {"unit": "u9", "item": "BLOCKED", "at": NOW - 3 * H, "ended": NOW - 2 * H, "status": "finished"},
            {"unit": "u10", "item": "LEFT", "at": NOW - 3 * H, "ended": NOW - 2 * H, "status": "finished"},
            {"unit": "u11", "item": "STAGE", "at": NOW - 3 * H, "ended": NOW - 2 * H, "status": "finished",
             "env": {"RM_CONTROL_MOD": "GimmeSomeSlack", "RM_CONTROL_STAGE": "offline_build"}}]
    evs = [{"id": "ACTED", "event": "note", "ts": iso(NOW - H), "text": "read it, next is X"},
           {"id": "OPEN", "event": "note", "ts": iso(NOW - H), "text": "DETACHED run u1 ended success (exited 0)"},
           {"id": "OPEN", "event": "note", "ts": iso(NOW - H), "why": "detached run ended", "text": "x"},
           {"id": "LEFT", "event": "note", "ts": iso(NOW - 2.5 * H), "text": "LEFT OPEN: step two is the census rows"}]
    # a run that put a wait or a block on its item, or left a LEFT OPEN: note, gave its end a home
    got = NH.ended_runs(recs, items, NH.last_act(evs), NOW, left_open=NH.left_open_notes(evs))
    assert got == ["u1 on OPEN"], got


def t_the_reading_is_shared_and_cached():
    need()
    path = os.path.join(TMP, "nh_cache.json")
    calls = []
    real = NH.sources
    NH.sources = lambda *a, **k: calls.append(1) or {"a": lambda: ["x"]}
    try:
        r1 = NH.reading(None, None, None, NOW, path=path)
        r2 = NH.reading(None, None, None, NOW + NH.TTL_S - 1, path=path)
        r3 = NH.reading(None, None, None, NOW + NH.TTL_S + 1, path=path)
    finally:
        NH.sources = real
    assert len(calls) == 2 and r1["at"] == NOW and r2["at"] == NOW and r3["at"] == NOW + NH.TTL_S + 1, (calls, r1, r2, r3)
    assert NH.last(NOW + 10, 60, path=path) is None and NH.last(NOW + NH.TTL_S + 2, 60, path=path)["no_home"] == 1
    v = os.path.join(TMP, "v.json")
    assert OQ.write_view([{"item": "A", "q": "q"}], [], r1, NOW, path=v) is None
    assert OQ.read_view(NOW + 1, path=v)["his"] == [{"item": "A", "q": "q"}]
    assert OQ.read_view(NOW + OQ.VIEW_FRESH_S + 1, path=v) is None


HOME = {"no_home": 3, "by_source": {"typed words": 2, "ended runs": 1}, "unmeasured": ["words typed elsewhere"]}


def t_a_test_never_writes_the_shared_files():
    need()
    real_dir, real_state = os.environ.pop("RM_OWNER_VIEW_DIR"), None
    try:
        import doorbell
        real_state = doorbell.state_dir
        fake_real = tempfile.mkdtemp(prefix="real_state_", dir=TMP)
        doorbell.state_dir = lambda: fake_real          # stands in for the real state dir: never touched here
        said = OQ.write_view([{"item": "A", "q": "q"}], [], None, NOW)
        assert said and "test" in said and not os.path.exists(os.path.join(fake_real, "owner_view", "view.json")), said
        calls = []
        real_sources = NH.sources
        NH.sources = lambda *a, **k: calls.append(1) or {"a": lambda: ["x"]}
        try:
            r = NH.reading(None, None, None, NOW, fresh=True)
        finally:
            NH.sources = real_sources
        assert r["no_home"] == 1 and "test" in r.get("write_failed", ""), r
        assert not os.path.exists(os.path.join(fake_real, "owner_view", "no_home.json"))
    finally:
        os.environ["RM_OWNER_VIEW_DIR"] = real_dir
        if real_state:
            doorbell.state_dir = real_state


def t_one_view_shows_his_ours_and_the_count():
    need()
    his = [{"item": "X_ONE", "q": "Pick the <bridge> art"}]
    ours = [{"item": "X_TWO", "q": "Write the ruling", "age": "2d"}]
    md = OQ.one_view(his, ours, HOME)
    assert "Pick the <bridge> art (`X_ONE`)" in md and "Write the ruling (`X_TWO`), 2d" in md, md
    assert "not filed anywhere: 3 (typed words 2, ended runs 1; UNMEASURED: words typed elsewhere)" in md, md
    unm = OQ.one_view(his, ours, {"no_home": None, "by_source": {}, "unmeasured": ["typed words"]})
    assert "not filed anywhere: UNMEASURED" in unm and "not filed anywhere: 0" not in unm
    assert "not filed anywhere: UNMEASURED (no reading yet)" in OQ.one_view(his, ours, None)
    assert "not filed anywhere: 0" in OQ.one_view([], [], {"no_home": 0, "by_source": {"a": 0}, "unmeasured": []})
    h = OQ.one_view(his, ours, HOME, fmt="html")
    assert "\n" not in h and "&lt;bridge&gt;" in h and "<bridge>" not in h and "NEEDS YOU, 1" in h, h
    assert "X_TWO (2d)" in h and "not filed anywhere: 3" in h
    assert "Nothing waits on you." in OQ.one_view([], [], HOME)
    rows = OQ.ours({"answered": [{"item": "B", "q": "b"}, {"item": "A", "q": "a"}]},
                   {"A": type("I", (), {"created_at": iso(NOW - 5 * 86400)})(),
                    "B": type("I", (), {"created_at": iso(NOW - 86400 * 2)})()}, NOW)
    assert [r["item"] for r in rows] == ["A", "B"] and rows[0]["age"] == "5d", rows


def t_not_his_before_its_turn():
    need()
    from types import SimpleNamespace as NS

    def row(**kw):
        return NS(**dict({"id": "A", "open": True, "needs": "owner", "title": "t", "blocked": False, "blocked_kind": None,
                          "blocked_on": None, "blocked_also": (), "wait_until": None, "history": [], "state": "proposed"}, **kw))
    for x, his in ((row(wait_until=iso(NOW + 86400)), False), (row(wait_until=iso(NOW - 60)), True), (row(), True),
                   (row(wait_until="soon"), True), (row(blocked=True, blocked_on="P"), False),
                   (row(blocked=True, blocked_on="GONE"), True)):
        n = OQ.needs_you({"A": x, "P": row(id="P", needs="offline")}, {}, {}, evs=[], now=NOW)
        assert ([r["item"] for r in n["lines"]] == ["A"]) is his and ([r["item"] for r in n["later"]] == ["A"]) is not his, x
        assert OQ.needs_you({"A": x}, {}, {}, evs=[], turns={"A": "turn"}, now=NOW)["count"] == 1, "a Designer turn is his"


def t_both_pages_build_from_one_view():
    need()
    for p in ("running_now.py", "maturation_now.py"):
        with open(os.path.join(HERE, p), encoding="utf-8") as f:
            assert "one_view(" in f.read(), p
    import maturation_now as M
    d = {"view": {"his": [{"item": "X_ONE", "q": "Pick it"}], "ours": [], "home": HOME},
         "needs": {"journal": ["Gimme Some Slack: question 4, poles"], "mandrake": [], "conductor": [], "pipeline": []}}
    md = "\n".join(M.view_block(d, "md"))
    assert md.startswith("## Needs Mandrake (1)") and "Pick it (`X_ONE`)" in md and "not filed anywhere: 3" in md, md
    assert "Open questions in mod journals" in md and "question 4" in md
    assert "\n" not in M.view_block(d, "html")
    assert M.view_block({"needs": {}}, "md") is None


def t_each_limit_names_its_danger():
    need()
    for mod, names in ((NH, ("WINDOW_S", "TTL_S", "NAMES_SHOWN")), (OQ, ("VIEW_FRESH_S",))):
        with open(mod.__file__, encoding="utf-8") as f:
            src = f.read()
        for n in names:
            m = re.search(r"((?:#.*\n)+)%s = " % n, src)
            assert m and "Danger" in m.group(1) and "Evidence" in m.group(1), "%s has no danger and evidence" % n


def t_the_live_promise_follows_the_shared_view_file():
    import doorbell
    import live_line

    iid = "RIMMANDRAKE_BUILD_ONE_OWNER_VIEW_NO_HOME_COUNT_BESIDE"
    path = os.path.join(REPO, "infrastructure/state/items/closed", iid + ".md")
    with open(path, encoding="utf-8") as f:
        match = re.search(r"^## live\n(\S[^\n]*)", f.read(), re.M)
    assert match, "the owner-view item has no live line"
    line = match[1]
    p = live_line.parse(line)
    assert p["unit"] == "rm-maturation-page.timer" and p["max_age_s"] == OQ.VIEW_FRESH_S, p
    assert live_line.local_path(p["reading"]) == os.path.join(doorbell.DEFAULT_STATE, "owner_view", "view.json"), p
    path = OQ.view_path()
    assert OQ.write_view([], [], HOME, NOW) is None
    os.utime(path, (NOW, NOW))

    def systemctl(argv, **kw):
        assert argv[-1] == p["unit"], argv
        return subprocess.CompletedProcess(argv, 0, {"is-enabled": "enabled", "is-active": "active"}[argv[2]], "")

    line = line.replace(p["reading"], path)
    assert live_line.check(line, now=NOW + 60, runner=systemctl) is None
    assert "old" in live_line.check(line, now=NOW + OQ.VIEW_FRESH_S + 1, runner=systemctl)


def main():
    tests = [t_count_sums_the_readable_sources, t_no_readable_source_is_none_never_zero, t_an_unanswered_card_is_a_need,
             t_an_ended_run_with_no_later_act_is_a_need, t_the_reading_is_shared_and_cached,
             t_a_test_never_writes_the_shared_files,
             t_one_view_shows_his_ours_and_the_count, t_not_his_before_its_turn, t_both_pages_build_from_one_view,
             t_the_live_promise_follows_the_shared_view_file, t_each_limit_names_its_danger]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, str(e)[:400]))
    print("FAILED %d of %d" % (failed, len(tests)) if failed else "ALL PASS (%d)" % len(tests))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
