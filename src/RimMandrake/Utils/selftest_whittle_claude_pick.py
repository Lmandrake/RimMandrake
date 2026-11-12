#!/usr/bin/env python3
"""Offline selftest of the deterministic pick in infrastructure/whittle_claude/wc.py (the gate that runs before any model
call of a Claude Whittle round), and of the bookkeeping beside it.

    python3 src/RimMandrake/Utils/selftest_whittle_claude_pick.py

Cases: gate() on a ghost (no ledger item; no items file on origin/main), a closed item, one claimed by another loop, one
owned by another seat, needs=owner, a lane mismatch both ways, blocked, Test Pilot routed, 3 non-pass runs, a recent
round, a thin item (eligible, ranked last) and an eligible one; an unreadable claims table refuses a claim instead of
being read as empty; the account switcher's notice (stop, none, absent, unreadable); a killed whittle run still has its
spend read from the transcript, ending where the wrapup began.
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

TMP = Path(tempfile.mkdtemp(prefix="wc_pick_"))
os.environ["WC_HOME"] = str(TMP / "home")
os.environ["RM_SWITCH_PLAN_DIR"] = str(TMP / "plan")
os.environ.pop("WC_REMOTE", None)
os.environ.pop("WC_DIR", None)

p = Path(__file__).resolve().parents[3] / "infrastructure/whittle_claude/wc.py"
spec = importlib.util.spec_from_file_location("wc_pick", p)
wc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wc)

FAILS = []


def check(name, cond, got=""):
    print("%s %s%s" % ("ok  " if cond else "FAIL", name, "" if cond else "  got: %r" % (got,)))
    if not cond:
        FAILS.append(name)


def item(id_="RM_TEST_ITEM_ONE", **kw):
    d = dict(id=id_, open=True, state="ready", owner="BENCH", needs="offline", blocked=False, blocked_reason=None,
             runs=[], criteria=["a"], title="t", history=[])
    d.update(kw)
    return SimpleNamespace(**d)


LIVE = {"RM_TEST_ITEM_ONE", "FW_TEST_ITEM", "RM_TEST_THIN"}
import re  # noqa: E402

FW = [re.compile(r"^FW_")]


def ctx(**kw):
    d = dict(pats=FW, claims={}, origin=set(LIVE), recent={}, live=lambda i: i in LIVE)
    d.update(kw)
    return wc.Ctx(**d)


W = "CLAUDE_TEST_OFFLINE1"
CASES = [
    ("ghost: no ledger item", None, "offline", ctx(), False, "ghost"),
    ("ghost: no items file on origin", item(), "offline", ctx(origin=set()), False, "ghost"),
    ("ghost: no items file here", item(), "offline", ctx(live=lambda i: False), False, "ghost"),
    ("closed", item(open=False, state="closed"), "offline", ctx(), False, "closed"),
    ("claimed by another loop", item(), "offline", ctx(claims={"RM_TEST_ITEM_ONE": {"worker": "CLAUDE_X", "at": "t"}}),
     False, "claimed by CLAUDE_X"),
    ("our own claim passes", item(), "offline", ctx(claims={"RM_TEST_ITEM_ONE": {"worker": W, "at": "t"}}), True,
     "eligible"),
    ("owned by another seat", item(owner="CONDUCTOR"), "offline", ctx(), False, "owned by seat CONDUCTOR"),
    ("needs=owner", item(needs="owner"), "offline", ctx(), False, "needs=owner"),
    ("needs=owner on fwlive", item("FW_TEST_ITEM", needs="owner"), "fwlive", ctx(), False, "needs=owner"),
    ("offline lane refuses bridge", item(needs="bridge"), "offline", ctx(), False, "lane"),
    ("fwlive refuses a non-FW id", item(), "fwlive", ctx(), False, "lane"),
    ("fwlive takes FW bridge", item("FW_TEST_ITEM", needs="bridge", state="built"), "fwlive", ctx(), True, "eligible"),
    ("blocked", item(blocked=True, blocked_reason="waits on X"), "offline", ctx(), False, "blocked"),
    ("Test Pilot routed", item(), "offline", ctx(pilot=lambda v: {"kind": "pilot", "why": "routed"}), False,
     "Test Pilot"),
    ("3 non-pass runs", item(runs=[SimpleNamespace(result="fail")] * 3), "offline", ctx(), False, "non-pass"),
    ("a pass breaks the run", item(runs=[SimpleNamespace(result="fail")] * 2 + [SimpleNamespace(result="pass")]),
     "offline", ctx(), True, "eligible"),
    ("recent round", item(), "offline", ctx(recent={"RM_TEST_ITEM_ONE": "failed 2h ago"}), False, "recent round"),
    ("thin", item("RM_TEST_THIN"), "offline", ctx(missing=lambda v: ["Acceptance"]), True, "thin"),
    ("eligible", item(), "offline", ctx(), True, "eligible"),
]
for name, v, lane, c, want_ok, want_word in CASES:
    ok, reason, rank = wc.gate(v, W, lane, c)
    check("gate %s" % name, ok == want_ok and want_word in reason, (ok, reason))
_, _, r_thin = wc.gate(item("RM_TEST_THIN"), W, "offline", ctx(missing=lambda v: ["Acceptance"]))
_, _, r_ok = wc.gate(item(), W, "offline", ctx())
check("thin ranks after eligible", r_thin is not None and r_ok is not None and r_thin >= r_ok + 10, (r_thin, r_ok))
_, _, r_built = wc.gate(item("FW_TEST_ITEM", needs="bridge", state="built"), W, "fwlive", ctx())
_, _, r_off = wc.gate(item("FW_TEST_ITEM", needs="offline"), W, "fwlive", ctx())
check("fwlive ranks built live work first", r_built < r_off, (r_built, r_off))

# claims table: absent is empty, unreadable is None and a claim is refused (never overwritten as empty)
home = Path(os.environ["WC_HOME"])
home.mkdir(parents=True, exist_ok=True)
check("absent claims table reads empty", wc.read_table() == {}, wc.read_table())
(home / "claims.json").write_text('{"RM_A": {"worker": "CLAUDE_X"', encoding="utf-8")
check("corrupt claims table reads None", wc.read_table() is None, wc.read_table())
rc = wc.claim(SimpleNamespace(worker=W, id="RM_TEST_ITEM_ONE"))
check("claim refused on a corrupt table", rc == 4, rc)
check("corrupt table left as it was", (home / "claims.json").read_text(encoding="utf-8").startswith('{"RM_A"'))
(home / "claims.json").write_text("{}", encoding="utf-8")
rc = wc.claim(SimpleNamespace(worker=W, id="RM_TEST_ITEM_ONE"))
check("claim on a good table", rc == 0 and W == wc.read_table().get("RM_TEST_ITEM_ONE", {}).get("worker"), rc)
check("claim writes the .bak", (home / "claims.json.bak").exists())

# the account switcher's notice: absent = no stop, none = no stop, stop = stop, unreadable = fail safe
plan = Path(os.environ["RM_SWITCH_PLAN_DIR"])
wc.NOTICE = plan / "notice.json"
check("no notice: no stop", wc.notice_state()[0] == 1 and wc.stop_reason() is None, wc.notice_state())
plan.mkdir(parents=True, exist_ok=True)
wc.NOTICE.write_text(json.dumps({"state": "none"}), encoding="utf-8")
check("state none: no stop", wc.notice_state()[0] == 1 and wc.stop_reason() is None, wc.notice_state())
wc.NOTICE.write_text(json.dumps({"state": "stop", "since": "S", "reset_at": "R"}), encoding="utf-8")
rc, text = wc.notice_state()
check("state stop: stop", rc == 0 and "S" in text and "R" in text and wc.stop_reason(), (rc, text))
wc.NOTICE.write_text("{not json", encoding="utf-8")
check("unreadable notice: fail safe", wc.notice_state()[0] == 2 and "fail safe" in (wc.stop_reason() or ""),
      wc.notice_state())
wc.NOTICE.write_text("[1]", encoding="utf-8")
check("non-object notice: fail safe", wc.notice_state()[0] == 2, wc.notice_state())

# spend of a round whose whittle run was killed: setup and wrapup from their result lines, whittle from the transcript
rd = TMP / "rounds/1"
rd.mkdir(parents=True)
clone = TMP / "clone"
proj = TMP / "fakehome/.claude/projects" / re.sub(r"[^A-Za-z0-9]", "-", str(clone))
proj.mkdir(parents=True)
os.environ["HOME"] = str(TMP / "fakehome")
now = time.time()


def result(path, i, o, cw, cr, cost, sid):
    path.write_text(json.dumps({"type": "result", "session_id": sid, "num_turns": 1, "modelUsage": {"claude-sonnet": {
        "inputTokens": i, "outputTokens": o, "cacheCreationInputTokens": cw, "cacheReadInputTokens": cr,
        "costUSD": cost}}}) + "\n", encoding="utf-8")


result(rd / "setup.json", 10, 20, 0, 1000, 0.01, "s-setup")
(rd / "whittle.1.t0").write_text(str(now - 100), encoding="utf-8")
(rd / "whittle.1.log").write_text("", encoding="utf-8")
(rd / "whittle.1.out").write_text("", encoding="utf-8")
os.utime(rd / "whittle.1.out", (now - 100, now - 100))   # created when the run began, never written: killed


def msg(t, mid, i, cr):
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t)) + "Z"
    return json.dumps({"type": "assistant", "sessionId": "s-whittle", "timestamp": stamp, "message": {
        "id": mid, "model": "claude-opus-x", "usage": {"input_tokens": i, "output_tokens": 0,
                                                       "cache_creation_input_tokens": 0, "cache_read_input_tokens": cr}}})


(proj / "w.jsonl").write_text("\n".join([msg(now - 90, "m1", 100, 10000), msg(now - 80, "m2", 100, 10000),
                                         msg(now - 80, "m2", 100, 10000),          # the same message twice: one
                                         msg(now - 10, "m3", 999999, 0)]) + "\n",  # after the wrapup began: not ours
                              encoding="utf-8")
(rd / "wrapup.json.err").write_text("", encoding="utf-8")
os.utime(rd / "wrapup.json.err", (now - 50, now - 50))
result(rd / "wrapup.json", 5, 5, 0, 0, 0.001, "s-wrapup")
os.utime(rd / "wrapup.json", (now - 5, now - 5))
s = wc.spend_of(rd, clone)
check("killed whittle spend from the transcript", s["whittle"]["raw"] == 20200 and s["whittle"]["turns"] == 2,
      s["whittle"])
check("whittle weighted reads cache at 0.1", s["whittle"]["weighted"] == 2200, s["whittle"]["weighted"])
check("whittle priced", abs(s["whittle"]["cost_usd"] - wc.priced("opus", 200, 0, 0, 20000)) < 1e-6, s["whittle"])
check("setup from its result line", s["setup"]["raw"] == 1030 and s["setup"]["cost_usd"] == 0.01, s["setup"])
check("total sums the phases", s["total"]["raw"] == 1030 + 20200 + 10, s["total"]["raw"])

shutil.rmtree(TMP, ignore_errors=True)
print("%d failed" % len(FAILS) if FAILS else "all ok")
sys.exit(1 if FAILS else 0)
