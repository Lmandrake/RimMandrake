#!/usr/bin/env python3
"""selftest for switching_plan.py (ACCOUNTS_PLAN_BUILD_STANDARD_SWITCHING): the pure decision, the pool, and one
end-to-end pass against a fake claude-account. Scratch dirs only; never touches the real switcher or meter.

    python3 src/RimMandrake/Utils/selftest_switching_plan.py
"""
import json
import os
import stat
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp(prefix="selftest_switching_plan_"))
os.environ["RM_SWITCH_PLAN_DIR"] = str(TMP / "out")
sys.path.insert(0, str(HERE))
import switching_plan as SP  # noqa: E402

FAILS = []
NOW = 1_800_000_000.0
PLAN = SP.load_plan()


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def R(left, h, src="MEASURED", age=1.0, stale=False):
    """A read_now record: left % of the week, h hours to the weekly reset."""
    rs = NOW + h * 3600
    return {"source": src, "week_pct_left": left, "week_pct_used": None if left is None else 100 - left,
            "hours_to_week_reset": h if h is None or h > 0 else None, "week_resets_at": SP.iso(rs),
            "stale": stale, "age_min": age}


def D(meter, live, state=None, gate=True, plan=PLAN, polled=False):
    st = dict(state or {})
    if gate:
        st["gate_passed"] = True
    return SP.decide(meter, live, NOW, plan, st, markers=st.get("_markers", {}), polled=polled)


def main():
    out = SP.decide({}, "system", NOW, PLAN, {}, markers={}, gate_seen=False)
    check(out["do"] == "passive", "gate unseen: passive (account_failover still owns the machine)")
    off = {"steven": R(90, 100)}  # steven 68 h after his reset: outside the 48 h window
    d = D({**off, "system": R(50, 100), "lukas": R(98, 120)}, "system")
    check(d["do"] == "normal" and d.get("to") is None, "system live with headroom, steven out of window: normal")
    d = D({**off, "system": R(1.5, 100), "lukas": R(98, 120)}, "system")
    check(d["do"] == "soft", "system at 1.5% (switch-away line 0 + 2): soft line")
    d = D({**off, "system": R(0, 100), "lukas": R(98, 120)}, "system")
    check(d["do"] == "switch" and d["to"] == "lukas", "system at 0%, lukas has headroom: switch to lukas")
    d = D({**off, "system": R(0.9, 100, age=20), "lukas": R(98, 120)}, "system")
    check(d["do"] != "switch" and d.get("poll"), "a 20-min-old reading at the line: poll first, never switch on it")
    d = D({**off, "system": R(0.5, 100), "lukas": R(1.9, 120)}, "lukas")
    check(d["do"] == "stop", "lukas is the last: at its 2% wait line -> hard stop")
    d = D({**off, "system": R(0, 100), "lukas": R(3.5, 120)}, "lukas")
    check(d["do"] == "soft", "lukas at 3.5% (wait line 2 + 2): soft line")
    d = D({**off, "system": R(0.5, 100), "lukas": R(1.5, 120)}, "system")
    check(d["do"] == "stop", "system live and lukas spent: system becomes the wait account (2%), at 0.5% -> stop")
    d = D({"steven": R(100, 167.9), "system": R(40, 100), "lukas": R(98, 120)}, "system")
    check(d["do"] == "switch" and d["to"] == "steven", "steven's reset: switch to steven from system")
    d = D({"steven": R(53, 150), "system": R(40, 100), "lukas": R(98, 120)}, "steven")
    check(d["do"] == "soft", "steven at 53% (leave 52 + 2): soft")
    d = D({"steven": R(51.9, 150), "system": R(40, 100), "lukas": R(98, 120)}, "steven")
    check(d["do"] == "switch" and d["to"] == "system", "steven at its 52% line: switch to system")
    d = D({"steven": R(80, 110), "system": R(40, 100), "lukas": R(98, 120)}, "steven")
    check(d["do"] == "switch" and d["to"] == "system", "steven live outside its window: switch off him")
    d = D({"steven": R(90, 110), "system": R(0.5, 100), "lukas": R(0.5, 120)}, "system")
    check(d["do"] == "stop" and d.get("to") is None, "nothing eligible but steven out of window: stop, never steven")
    d = D({**off, "system": R(3, 100, src="ESTIMATE"), "lukas": R(98, 120)}, "system")
    check(d["do"] != "switch" and d.get("poll"), "an ESTIMATE of the live account never switches; it asks for a poll")
    d = D({"steven": R(10, 0.2), "system": R(0, 100), "lukas": R(40, 120)}, "lukas")
    check(d["do"] == "soft" and "steven" in d["why"], "steven resets in 12 min (lead 20): soft notice before the switch")
    d = D({**off, "system": R(0, 100), "lukas": R(100, 167.5)}, "lukas", state={"stopped": {"account": "lukas"}})
    check(d["do"] == "start", "hard-stopped on lukas, lukas's own reset: fleet-start, no switch")
    d = D({**off, "system": R(None, -0.1), "lukas": R(1.9, 120)}, "lukas")
    check(d.get("poll") and d["do"] != "stop", "system's reset just passed (no post-reset reading): poll before acting")
    mk = {SP.switch_key("system", "lukas", R(98, 3)): {"phase": "done"}}
    d = D({**off, "system": R(40, 100), "lukas": R(98, 3)}, "system", state={"_markers": mk})
    check(d["do"] == "hold", "a transition already done this week is never repeated (a human moved back)")
    # owner 2026-10-28 11:2x (relayed): switch away at 0%, wait on 2%; blind meter = 0%
    check(PLAN["floors"]["switch_away_pct_left"] == 0 and PLAN["floors"]["wait_pct_left"] == 2
          and PLAN["floors"]["blind_zero_pct"] == 1, f"floors are 0 / 2, blind at 1 (got {PLAN['floors']})")
    d = D({**off, "system": R(0.5, 100), "lukas": R(98, 120)}, "system")
    check(d["do"] == "soft", f"0.5% on an account we switch away from at 0%: soft, keep burning (got {d['do']})")
    d = D({**off, "system": R(0, 100), "lukas": R(98, 120)}, "system")
    check(d["do"] == "switch" and d["to"] == "lukas", f"0% reached: switch (got {d})")
    d = D({**off, "system": R(0.8, 100, src="ESTIMATE", age=30), "lukas": R(98, 120)}, "system")
    check(d["do"] == "switch" and d["to"] == "lukas" and d["pct_left"] == 0,
          f"blind meter on a last-MEASURED 0.8%: counts as 0%, switch without waiting on a poll (got {d})")
    d = D({**off, "system": R(0.8, 100, stale=True), "lukas": R(98, 120)}, "system")
    check(d["do"] == "switch" and d["to"] == "lukas", f"a stale 0.8% reading is blind too: switch (got {d['do']})")
    d = D({**off, "system": R(0.8, 100, src="ESTIMATE", age=30), "lukas": R(1, 120)}, "system")
    check(d["do"] == "stop", f"blind 0% and no account with budget: stop, no poll (got {d['do']})")
    d = D({**off, "system": R(5, 100, src="ESTIMATE", age=30), "lukas": R(98, 120)}, "system")
    check(d["do"] == "poll", f"a blind reading last MEASURED at 5% is not 0%: poll (got {d['do']})")
    d = D({**off, "system": R(0.8, -0.1, src="ESTIMATE", age=30), "lukas": R(98, 120)}, "system")
    check(d["do"] == "poll", f"a blind reading from before a passed reset is not 0%: poll (got {d['do']})")
    pb = SP.pool({**off, "system": R(0.8, 100, src="ESTIMATE"), "lukas": R(50, 120)}, NOW, PLAN)
    check([x["spend_pct"] for x in pb["parts"] if x["account"] == "system"][0] == 0,
          f"the pool spends nothing more of a blind 0% account (got {pb['parts']})")
    # GPT review round 10 (2026-10-28 12:00)
    d = D({"steven": R(70, -49, src="ESTIMATE"), "system": R(0, 100), "lukas": R(0, 120)}, "steven", polled=True)
    check(d["do"] == "stop", f"steven live 49 h past a reset his reading predates: out of window, stop (got {d['do']})")
    # GPT review round 9 (2026-10-28 11:55)
    d = D({"steven": R(60, 120 + 5 / 60), "system": R(40, 100), "lukas": R(98, 130)}, "system")
    check(d["do"] == "normal", f"steven with 5 min of window left is no switch target (a slow use lands outside) (got {d['do']} {d['to']})")
    d = D({"steven": R(60, 120 + 5 / 60), "system": R(40, 100), "lukas": R(98, 130)}, "steven")
    check(d["do"] == "switch" and d["to"] == "system", f"live steven in the last minutes of his window switches away (got {d['do']})")
    d = D({"steven": R(60, 120 + 20 / 60), "system": R(40, 100), "lukas": R(98, 130)}, "system")
    check(d["do"] == "switch" and d["to"] == "steven", f"steven with 20 min left is still the soonest target (got {d['do']})")
    # GPT review round 8 (2026-10-28 11:50)
    st8 = {"stopped": {"account": "system"}}
    d = D({**off, "system": R(0.5, 100, src="ESTIMATE")}, "system", state=st8)
    check(d["do"] == "poll", f"stopped with lukas unread (no record): poll for it (got {d['do']})")
    d = D({**off, "system": R(0.5, 100, src="ESTIMATE"), "lukas": R(None, 120, src="UNMEASURED")}, "system", state=st8)
    check(d["do"] == "poll", f"stopped with lukas at an unknown %: poll for it (got {d['do']})")
    # GPT review round 5 (2026-10-28 11:37)
    mv = {"steven": R(80, 144), "system": R(60, 12, age=20), "lukas": R(0, 120)}
    d = D(mv, "lukas", polled=True)
    check(d["do"] == "switch" and d["to"] == "steven",
          f"spent, preferred target unconfirmed, a confirmed fallback exists: switch to it, never stop (got {d['do']} {d['to']})")
    d = D(mv, "system", polled=True)
    check(d["do"] != "switch" or d["to"] != "steven", f"the fallback is only for a spent live account (got {d['do']} {d['to']})")
    # GPT review round 4 (2026-10-28 11:32)
    d = D({**off, "system": R(2, 24), "lukas": R(100, 160)}, "system", state={"stopped": {"account": "system"}})
    check(d["do"] == "switch" and d["to"] == "lukas",
          f"hard-stopped in the soft zone and lukas refilled: switch to lukas, never sit stopped (got {d['do']} {d['to']})")
    d = D({**off, "system": R(2, 24), "lukas": R(1, 160)}, "system", state={"stopped": {"account": "system"}})
    check(d["do"] == "stopped", f"hard-stopped and nothing else has budget: stay stopped (got {d['do']})")
    sv = SP.SERVICE
    tmo = int(sv.split("TimeoutStartSec=")[1].split("s")[0])
    check(tmo >= 120 + 420 + 120 + 3 * 600, f"the unit outlives a full pass (status, poll, status, arm, use, disarm): {tmo}")
    # GPT review round 3 (2026-10-28 12:10)
    mk = {SP.switch_key("steven", "system", R(70, 100)): {"phase": "failed", "at": SP.iso(NOW - 300)}}
    sv = {"steven": R(51, 150), "system": R(70, 100), "lukas": R(0, 120)}
    d = D(sv, "steven", state={"_markers": mk})
    check(d["do"] == "stop", f"a failed switch with live under its line: hard stop first (got {d['do']})")
    d = D(sv, "steven", state={"_markers": mk, "stopped": {"account": "steven"}})
    check(d["do"] == "switch" and d["to"] == "system", f"stopped after a failed switch: retry the switch (got {d['do']})")
    d = D({"steven": R(80, 110), "system": R(0, 100), "lukas": R(1, 120)}, "steven")
    check(d["do"] == "stop", f"steven live past his window with no account to go to: stop (got {d['do']})")
    d = D({**off, "system": R(2, 100), "lukas": R(50, 120, stale=True)}, "system")
    check(d["do"] == "poll", f"no target but an unread account may have budget: poll before stopping (got {d['do']})")
    d = D({**off, "system": R(2, 100), "lukas": R(50, 120, stale=True)}, "system", polled=True)
    check(d["do"] == "stop", f"still unread after the poll: stop (got {d['do']})")
    # GPT review round 2 (2026-10-28 11:58)
    mk = {SP.switch_key("system", "lukas", R(50, 48)): {"phase": "done", "from": "system", "to": "lukas",
                                                        "under": True, "at": SP.iso(NOW - 600)}}
    d = D({**off, "system": R(1, 24), "lukas": R(50, 48)}, "lukas", state={"_markers": mk})
    check(d["do"] == "normal", f"an account left at its line is no target again before its reset: no flap (got {d})")
    d = D({**off, "system": R(1, 24, src="ESTIMATE", age=30), "lukas": R(50, 48)}, "system", state={"_markers": mk})
    check(d["do"] == "switch" and d["to"] == "lukas",
          f"back on an empty account after a done switch: switch again, never stop with lukas at 50% (got {d})")
    d = D({**off, "system": R(2, 24, src="ESTIMATE", age=30), "lukas": R(50, 48)}, "system", polled=True)
    check(d["do"] == "switch" and d["to"] == "lukas", f"blind after a poll near its line: switch, never hold (got {d})")
    d = D({**off, "system": R(50, 24, src="ESTIMATE", age=30), "lukas": R(50, 48)}, "system", polled=True)
    check(d["do"] == "hold", f"blind after a poll far from its line: hold (got {d['do']})")
    d = D({**off, "system": R(1, 24, age=120), "lukas": R(50, 48)}, "system",
          state={"stopped": {"account": "system"}}, polled=True)
    check(d["do"] != "start", f"no fleet-start on an unconfirmed reading (got {d['do']})")
    d = D({**off, "system": R(0, 100), "lukas": R(3, 120)}, "lukas", state={"stopped": {"account": "lukas"}})
    check(d["do"] == "stopped", f"no fleet-start into the soft zone (lukas 3%, wait line 2) (got {d['do']})")
    d = D({"steven": R(90, -0.02), "system": R(1, 24, src="ESTIMATE", age=30), "lukas": R(50, 48)}, "system")
    check(d["do"] == "switch" and d["to"] == "lukas", f"blind 0% live: an unrelated reset never delays the switch (got {d})")
    # GPT review 2026-10-28 findings, as tests
    mk = {SP.switch_key("system", "lukas", R(98, 120)): {"phase": "done"}}
    d = D({**off, "system": R(0, 100), "lukas": R(98, 120)}, "system", state={"_markers": mk})
    check(d["do"] == "switch" and d["to"] == "lukas",
          f"a done marker never disables the floor: live under its line switches again (got {d['do']})")
    d = D({**off, "system": R(0, 100, age=20), "lukas": R(98, 120)}, "system", polled=True)
    check(d["do"] == "switch" and d["to"] == "lukas",
          f"live under its line on an old reading (an upper bound), target fresh: switch, never hold (got {d['do']})")
    d = D({"steven": R(None, -0.1, src="UNMEASURED"), "system": R(0, 100), "lukas": R(98, 120)}, "system",
          polled=True)
    check(d["do"] == "switch" and d["to"] == "lukas", f"an unrelated account's unread reset never blocks a switch (got {d})")
    d = D({**off, "system": R(1.9, -0.01), "lukas": R(0.5, 120)}, "system")
    check(d["do"] == "poll", f"live's own reset just passed: poll before acting (got {d['do']})")
    d = D({**off, "system": R(1.9, -0.01), "lukas": R(0.5, 120)}, "system", polled=True)
    check(d["do"] not in ("stop", "switch"), f"a pre-reset reading of live never stops it (got {d['do']})")
    d = D({**off, "system": R(40, 100), "lukas": R(50, 3, age=40)}, "system")
    check(d["do"] == "poll", f"a 40-min-old reading of the target: poll before switching (got {d['do']})")
    d = D({**off, "system": R(40, 100), "lukas": R(50, 3, age=40)}, "system", polled=True)
    check(d["do"] != "switch", f"no switch onto a target read 40 min ago, even after a poll (got {d['do']})")
    # use it or lose it: the soonest-expiring account with budget burns first (coordinator 2026-10-28 10:58)
    d = D({**off, "system": R(100, 167.9), "lukas": R(40, 3)}, "lukas")
    check(d["do"] == "normal", f"system just reset, lukas 40% expires in 3 h: stay on lukas (got {d['do']} {d.get('to')})")
    d = D({**off, "system": R(0, 0.2), "lukas": R(40, 3)}, "lukas")
    check(d["do"] == "normal", f"system's reset in 12 min will not pull the machine off lukas: no soft (got {d['do']})")
    d = D({"steven": R(100, 167.9), "system": R(100, 165), "lukas": R(30, 1.2)}, "lukas")
    check(d["do"] == "normal", f"steven just reset but lukas expires in 1.2 h: lukas first (got {d['do']} {d.get('to')})")
    d = D({"steven": R(100, 167), "system": R(98, 165), "lukas": R(0, 0.5)}, "lukas")
    check(d["do"] == "switch" and d["to"] == "steven", f"lukas spent: steven's window expires before system (got {d})")
    d = D({**off, "system": R(100, 165), "lukas": R(1.5, 3)}, "lukas")
    check(d["do"] == "soft", f"lukas at 1.5% with system to switch to: its line is 0 (soft, not stop) (got {d['do']})")
    d = D({**off, "system": R(1.5, 100), "lukas": R(1.8, 120)}, "lukas")
    check(d["do"] == "stop", f"no account with budget: pause at the 2% wait floor (got {d['do']})")
    mk = {SP.switch_key("system", "lukas", R(98, 120)): {"phase": "failed", "at": SP.iso(NOW - 60)}}
    d = D({**off, "system": R(0, 100), "lukas": R(98, 120)}, "system",
          state={"_markers": mk, "stopped": {"account": "system"}})
    check(d["do"] == "switch", f"a FAILED switch is retried from the stopped fleet, never held (got {d['do']})")
    mk = {SP.switch_key("system", "lukas", R(98, 120)): {"phase": "pending", "at": SP.iso(NOW - 600)}}
    d = D({**off, "system": R(0, 100), "lukas": R(98, 120)}, "system", state={"_markers": mk})
    check(d["do"] == "stop", f"a pending switch that never landed while live is under its line: stop (got {d['do']})")
    d = D({**off, "system": R(0.9, 100), "lukas": R(98, 120)}, None)
    check(d["do"] == "skip", "live account unknown: skip")

    # the pool: every budget is due at its own expiry (use it or lose it), plus each account's next refill
    p = SP.pool({"steven": R(80, 168 - 8), "system": R(50, 100), "lukas": R(98, 120)}, NOW, PLAN, live="steven")
    # steven 28 by his window end (40 h); system 50 by 100 h (switch-away 0); lukas (last to expire: wait line 2) 96 by 120 h
    by120 = sum(x["spend_pct"] for x in p["parts"] if x["by_h"] <= 120)
    check(abs(by120 - 174) < 0.01, f"this week's budgets: 28 + 50 + 96 = 174 due by lukas's reset, 120 h (got {by120})")
    # the refills (steven 48 by 208 h, system 100 by 268 h, lukas 98 by 288 h) make 420 by 288 h: 1.458 > 174/120
    check(abs(p["rate_pct_h"] - 420 / 288) < 0.01 and abs(p["deadline_h"] - 288) < 0.01 and abs(p["pct"] - 420) < 0.01,
          f"the binding deadline is the refills' 420% by 288 h (got {p['pct']} by {p['deadline_h']})")
    p = SP.pool({"steven": R(60, 168 - 46), "system": R(90, 100), "lukas": R(98, 120)}, NOW, PLAN, live="steven")
    check(abs(p["rate_pct_h"] - 4.0) < 0.01 and abs(p["deadline_h"] - 2) < 0.01,
          f"steven's 8% must go in the 2 h left of his window: 4%/h binds (got {p['rate_pct_h']})")
    p = SP.pool({"steven": R(22, 2), "system": R(100, 168), "lukas": R(6, 3)}, NOW, PLAN, live="system")
    check(abs(p["rate_pct_h"] - 2.0) < 0.01 and abs(p["deadline_h"] - 3) < 0.01,
          f"lukas's 6% expiring in 3 h binds at 2%/h (got {p['rate_pct_h']} by {p['deadline_h']})")
    p9 = SP.pool({"steven": R(22, 2), "system": R(40, 168), "lukas": R(40, 167)}, NOW, PLAN)
    sv9 = sorted(x["by_h"] for x in p9["parts"] if x["account"] == "steven")
    check(sv9 == [50.0, 218.0], f"steven's two windows inside the horizon both count (got {sv9})")
    sv = [x for x in p["parts"] if x["account"] == "steven"]
    check(len(sv) == 2 and abs(sv[0]["spend_pct"] - 48) < 0.01 and abs(sv[0]["by_h"] - 50) < 0.01,
          f"steven's coming window counts: 48% by 50 h (got {sv})")

    # one pass end to end, fake claude-account
    fake = TMP / "claude-account"
    calls = TMP / "calls.txt"
    fake.write_text("#!/usr/bin/env python3\nimport json,sys,os\nopen(%r,'a').write(' '.join(sys.argv[1:])+'\\n')\n"
                    "lf=os.environ.get('FAKE_LIVE_FILE')\n"
                    "if 'use' in sys.argv and lf and os.environ.get('FAKE_FAIL') != 'use': open(lf,'w').write(sys.argv[sys.argv.index('use')+1])\n"
                    "live=open(lf).read() if lf and os.path.exists(lf) else os.environ.get('FAKE_LIVE')\n"
                    "if 'status' in sys.argv: print(json.dumps({'machine':'testbox','live':live,"
                    "'armed':False}))\nelif os.environ.get('FAKE_FAIL') in sys.argv: sys.exit(3)\nelse: print(json.dumps({'ok':True}))\n" % str(calls))
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    os.environ["RM_CLAUDE_ACCOUNT"] = str(fake)
    os.environ["FAKE_LIVE"] = "system"
    os.environ["FAKE_LIVE_FILE"] = str(TMP / "live.txt")
    SP.CA = str(fake)
    (TMP / "out").mkdir(exist_ok=True)
    SP.save_state({"gate_passed": True})
    meter = {**off, "system": R(0, 100), "lukas": R(98, 120)}
    rc = SP.check(dry=False, now=NOW, meter_fn=lambda: meter, poll_fn=lambda: None)
    seq = [ln.replace("--json ", "").split()[0] for ln in calls.read_text().splitlines() if ln.strip()]
    seq = [x for x in seq if x != "status"]  # the post-arm re-check reads status too
    check(rc == 0 and seq[-3:] == ["arm", "use", "disarm"], f"switch pass: arm, use, disarm (got {seq})")
    check("use lukas --confirm testbox" in calls.read_text(), "the switch names the target and confirms the machine")
    check(SP.switcher_status().get("live") == "lukas", "after the pass the switcher reads lukas live")
    (TMP / "live.txt").unlink()
    mks = SP.read_markers()
    check(any(v.get("phase") == "done" for v in mks.values()), "the transition marker reads done")
    calls.write_text("")
    os.environ["FAKE_LIVE"] = "lukas"
    meter2 = {**off, "system": R(0, 100), "lukas": R(1.5, 120)}
    rc = SP.check(dry=False, now=NOW, meter_fn=lambda: meter2, poll_fn=lambda: None)
    seq = [ln.replace("--json ", "").split()[0] for ln in calls.read_text().splitlines() if ln.strip()]
    seq = [x for x in seq if x != "status"]
    check(seq[-3:] == ["arm", "fleet-stop", "disarm"], f"hard stop pass: arm, fleet-stop, disarm (got {seq})")
    n = json.loads((TMP / "out" / "notice.json").read_text())
    check(n.get("state") == "stop", "the notice says stop")
    calls.write_text("")
    SP.check(dry=False, now=NOW + 60, meter_fn=lambda: meter2, poll_fn=lambda: None)
    seq = [ln.replace("--json ", "").split()[0] for ln in calls.read_text().splitlines() if ln.strip()]
    check("fleet-stop" not in seq, "the hard stop happens once per account-week")
    calls.write_text("")
    st = SP.load_state(); st.pop("stopped", None); SP.save_state(st)
    for k in list(SP.read_markers()):
        (TMP / "out" / "markers" / (k + ".json")).unlink()
    os.environ["FAKE_FAIL"] = "fleet-stop"
    SP.check(dry=False, now=NOW + 120, meter_fn=lambda: meter2, poll_fn=lambda: None)
    os.environ.pop("FAKE_FAIL")
    check(not SP.load_state().get("stopped"), "a fleet-stop that failed leaves no 'stopped' record: the next pass retries")
    # a crash inside fleet-stop leaves no 'stopped' record (it would suppress every later stop)
    real = SP.armed_call
    def boom(st, argv, still=None):
        raise RuntimeError("killed mid-call")
    SP.armed_call = boom
    try:
        SP.check(dry=False, now=NOW + 180, meter_fn=lambda: meter2, poll_fn=lambda: None)
    except RuntimeError:
        pass
    SP.armed_call = real
    check(not SP.load_state().get("stopped"), "a crash during fleet-stop leaves no 'stopped' record")
    # the soft notice goes out BEFORE the slow poll; time moves on during the poll
    seen, clock = {}, [1000.0]
    SP.clock = lambda: clock[0]
    os.environ["FAKE_LIVE"] = "lukas"
    m7 = {**off, "system": R(0.5, 100), "lukas": R(3.9, 120, age=7)}
    (TMP / "out" / "notice.json").unlink(missing_ok=True)
    st = SP.load_state(); st.pop("last_poll", None); SP.save_state(st)
    def poll7():
        seen["n"] = SP.read_json(TMP / "out" / "notice.json", {}).get("state")
    SP.check(dry=False, now=NOW + 240, meter_fn=lambda: m7, poll_fn=poll7)
    check(seen.get("n") == "soft", f"the soft brake is published before the poll starts (saw {seen.get('n')})")
    os.environ["FAKE_LIVE"] = "system"
    calls.write_text("")
    m5a = {"steven": R(55, 120.05, age=20), "system": R(40, 100), "lukas": R(98, 120)}
    m5b = {"steven": R(55, 120.05), "system": R(40, 100), "lukas": R(98, 120)}
    cur = [m5a]
    def poll5():
        clock[0] += 420
        cur[0] = m5b
    st = SP.load_state(); st.pop("last_poll", None); SP.save_state(st)
    SP.check(dry=False, now=NOW, meter_fn=lambda: cur[0], poll_fn=poll5)
    check("use steven" not in calls.read_text(), "a 7-min poll that ends past steven's window never switches to him")
    calls.write_text("")
    m5c = {"steven": R(55, 120.02), "system": R(40, 100), "lukas": R(98, 120)}
    def slow_meter():
        clock[0] += 120  # a slow status/meter read with no poll at all
        return m5c
    SP.check(dry=False, now=NOW, meter_fn=slow_meter, poll_fn=lambda: None)
    check("use steven" not in calls.read_text(), "a slow status read that ends past steven's window never switches to him")
    calls.write_text("")
    real_run = SP.run
    def slow_arm(argv, *a, **k):
        if argv[1:2] == ["arm"]:
            clock[0] += 900  # arming took 15 min: steven's window closed meanwhile
        return real_run(argv, *a, **k)
    SP.run = slow_arm
    st = SP.load_state(); st.pop("last_poll", None); SP.save_state(st)
    m6 = {"steven": R(80, 120.2), "system": R(40, 100), "lukas": R(0, 120)}
    SP.check(dry=False, now=NOW, meter_fn=lambda: m6, poll_fn=lambda: None)
    SP.run = real_run
    check("use steven" not in calls.read_text() and "arm" in calls.read_text(),
          "a decision that lapses while arming (steven's window closed) is skipped, not executed")
    mk6 = SP.read_markers()
    check(any(v.get("phase") == "lapsed" for v in mk6.values()), "the skipped switch is marked lapsed, not failed")
    # the re-check re-reads the meter: a target spent while arming is not switched onto
    lf = TMP / "live.txt"
    live_before = lf.read_text() if lf.exists() else None
    calls.write_text("")
    for k in list(SP.read_markers()):
        (TMP / "out" / "markers" / f"{k}.json").unlink(missing_ok=True)
    (TMP / "live.txt").write_text("lukas")
    cur7 = [{**off, "system": R(3, 100, age=0), "lukas": R(0, 120)}]
    def arm_spends(argv, *a, **k):
        if argv[1:2] == ["arm"]:
            cur7[0] = {**off, "system": R(1, 100, age=0), "lukas": R(0, 120)}
        return real_run(argv, *a, **k)
    SP.run = arm_spends
    SP.check(dry=False, now=NOW, meter_fn=lambda: cur7[0], poll_fn=lambda: None)
    SP.run = real_run
    check("use system" not in calls.read_text() and "arm" in calls.read_text(),
          "a target spent below its reserve while arming is not switched onto")
    # exhaustion first seen on the re-check (the departing account went blind at <=1%) latches into the done marker
    calls.write_text("")
    for k in list(SP.read_markers()):
        (TMP / "out" / "markers" / f"{k}.json").unlink(missing_ok=True)
    (TMP / "live.txt").write_text("system")
    st = SP.load_state(); st.pop("stopped", None); st.pop("last_poll", None); SP.save_state(st)
    cur11 = [{"steven": R(60, 132), "system": R(0.5, 24), "lukas": R(30, 48)}]
    def arm_blinds(argv, *a, **k):
        if argv[1:2] == ["arm"]:
            cur11[0] = {"steven": R(60, 132), "system": R(0.5, 24, src="ESTIMATE"), "lukas": R(30, 48)}
        return real_run(argv, *a, **k)
    SP.run = arm_blinds
    SP.check(dry=False, now=NOW, meter_fn=lambda: cur11[0], poll_fn=lambda: None)
    SP.run = real_run
    mk11 = [v for v in SP.read_markers().values() if v.get("to") == "steven"]
    check("use steven" in calls.read_text() and mk11 and mk11[0].get("phase") == "done" and mk11[0].get("under") is True,
          "a switch whose re-check finds the departing account exhausted records under=True in its done marker")
    # a stop that lapses while arming (lukas reset meanwhile) is skipped
    calls.write_text("")
    st = SP.load_state(); st.pop("stopped", None); SP.save_state(st)
    cur8 = [{**off, "system": R(0, 100), "lukas": R(2, 120)}]
    def arm_resets(argv, *a, **k):
        if argv[1:2] == ["arm"]:
            cur8[0] = {**off, "system": R(0, 100), "lukas": R(100, 288)}
        return real_run(argv, *a, **k)
    SP.run = arm_resets
    SP.check(dry=False, now=NOW, meter_fn=lambda: cur8[0], poll_fn=lambda: None)
    SP.run = real_run
    check("fleet-stop" not in calls.read_text() and "arm" in calls.read_text() and not SP.load_state().get("stopped"),
          "a stop that no longer holds after arming is skipped and leaves no 'stopped' record")
    # a human switch while arming: the engine does not switch again
    calls.write_text("")
    (TMP / "live.txt").write_text("lukas")
    for k in list(SP.read_markers()):
        (TMP / "out" / "markers" / f"{k}.json").unlink(missing_ok=True)
    cur10 = {**off, "system": R(50, 100), "lukas": R(60, 120)}
    def arm_human(argv, *a, **k):
        if argv[1:2] == ["arm"]:
            (TMP / "live.txt").write_text("system")
        return real_run(argv, *a, **k)
    SP.run = arm_human
    SP.check(dry=False, now=NOW, meter_fn=lambda: cur10, poll_fn=lambda: None)
    SP.run = real_run
    check("use system" not in calls.read_text() and "arm" in calls.read_text(),
          "a live account changed by a human while arming: no second switch")
    (TMP / "live.txt").write_text("lukas")
    # a hold on a pending switch near the line still publishes the soft brake
    (TMP / "out" / "notice.json").unlink(missing_ok=True)
    cur11 = {**off, "system": R(50, 30), "lukas": R(1, 60)}
    kk = SP.switch_key("lukas", "system", cur11["system"])
    SP.write_marker(kk, {"phase": "pending", "at": SP.iso(NOW - 60), "from": "lukas", "to": "system"})
    SP.check(dry=False, now=NOW, meter_fn=lambda: cur11, poll_fn=lambda: None)
    (TMP / "out" / "markers" / f"{kk}.json").unlink(missing_ok=True)
    check(SP.read_json(TMP / "out" / "notice.json", {}).get("state") == "soft",
          "a hold on a pending switch at 1% still publishes the soft brake")
    # HOLD written while arming brakes the act
    calls.write_text("")
    st = SP.load_state(); st.pop("stopped", None); SP.save_state(st)
    cur9 = {**off, "system": R(0, 100), "lukas": R(2, 120)}
    def arm_hold(argv, *a, **k):
        if argv[1:2] == ["arm"]:
            (TMP / "out" / "HOLD").write_text("x")
        return real_run(argv, *a, **k)
    SP.run = arm_hold
    SP.check(dry=False, now=NOW, meter_fn=lambda: cur9, poll_fn=lambda: None)
    SP.run = real_run
    (TMP / "out" / "HOLD").unlink(missing_ok=True)
    check("fleet-stop" not in calls.read_text() and "arm" in calls.read_text(),
          "HOLD written while arming brakes the act")
    if live_before is None:
        lf.unlink(missing_ok=True)
    else:
        lf.write_text(live_before)
    SP.clock = time.time
    # a second concurrent pass stands down
    import fcntl
    with open(TMP / "out" / "check.lock", "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        calls.write_text("")
        rc = SP.check(dry=False, now=NOW, meter_fn=lambda: meter, poll_fn=lambda: None)
        check(rc == 0 and calls.read_text() == "", "a pass that finds another running does nothing")
    # HOLD created while the poll runs brakes this pass too
    calls.write_text("")
    os.environ["FAKE_LIVE"] = "system"
    cur = [{**off, "system": R(40, 100), "lukas": R(50, 3, age=40)}]
    def poll_hold():
        (TMP / "out" / "HOLD").write_text("x")
        cur[0] = {**off, "system": R(40, 100), "lukas": R(50, 3)}
    st = SP.load_state(); st.pop("last_poll", None); SP.save_state(st)
    SP.check(dry=False, now=NOW + 300, meter_fn=lambda: cur[0], poll_fn=poll_hold)
    (TMP / "out" / "HOLD").unlink()
    check("use" not in calls.read_text(), "a HOLD written during the poll stops the pass from acting")
    # a stop the pass already sees is acted on at once, never deferred behind a slow poll
    calls.write_text("")
    (TMP / "live.txt").write_text("steven")
    st = SP.load_state(); st.pop("last_poll", None); st.pop("stopped", None); SP.save_state(st)
    polls = []
    SP.check(dry=False, now=NOW + 360, meter_fn=lambda: {"steven": R(51, 150), "system": R(70, 100, age=7),
                                                          "lukas": R(0, 120)}, poll_fn=lambda: polls.append(1))
    check("fleet-stop" in calls.read_text() and not polls, f"a pre-poll stop acts before any poll (polls={polls})")
    calls.write_text("")
    st = SP.load_state(); st.pop("last_poll", None); st.pop("stopped", None); SP.save_state(st)
    polls = []
    SP.check(dry=False, now=NOW + 420, meter_fn=lambda: {"steven": R(52, 150, age=7), "system": R(100, 100),
                                                          "lukas": R(0, 120)}, poll_fn=lambda: polls.append(1))
    check("use system" in calls.read_text() and not polls,
          f"a confirmed switch off a spent account acts before any poll (polls={polls})")
    st = SP.load_state(); st.pop("stopped", None); SP.save_state(st)
    calls.write_text("")
    rc = SP.check(dry=True, now=NOW, meter_fn=lambda: meter, poll_fn=lambda: None)
    seq = [ln.replace("--json ", "").split()[0] for ln in calls.read_text().splitlines() if ln.strip()]
    check(all(s == "status" for s in seq), f"--dry-run calls nothing but status (got {seq})")
    print(f"{'FAILED ' + str(len(FAILS)) if FAILS else 'all passed'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
