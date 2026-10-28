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


def D(meter, live, state=None, gate=True, plan=PLAN):
    st = dict(state or {})
    if gate:
        st["gate_passed"] = True
    return SP.decide(meter, live, NOW, plan, st, markers=st.get("_markers", {}))


def main():
    out = SP.decide({}, "system", NOW, PLAN, {}, markers={}, gate_seen=False)
    check(out["do"] == "passive", "gate unseen: passive (account_failover still owns the machine)")
    off = {"steven": R(90, 100)}  # steven 68 h after his reset: outside the 48 h window
    d = D({**off, "system": R(50, 100), "lukas": R(98, 120)}, "system")
    check(d["do"] == "normal" and d.get("to") is None, "system live with headroom, steven out of window: normal")
    d = D({**off, "system": R(2.5, 100), "lukas": R(98, 120)}, "system")
    check(d["do"] == "soft", "system at 2.5% (switch-away line 1 + 2): soft line")
    d = D({**off, "system": R(0.9, 100), "lukas": R(98, 120)}, "system")
    check(d["do"] == "switch" and d["to"] == "lukas", "system under 1%, lukas has headroom: switch to lukas")
    d = D({**off, "system": R(0.9, 100, age=20), "lukas": R(98, 120)}, "system")
    check(d["do"] != "switch" and d.get("poll"), "a 20-min-old reading at the line: poll first, never switch on it")
    d = D({**off, "system": R(0.5, 100), "lukas": R(1.9, 120)}, "lukas")
    check(d["do"] == "stop", "lukas is the last: at its 2% wait line -> hard stop")
    d = D({**off, "system": R(0.5, 100), "lukas": R(3.5, 120)}, "lukas")
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
    d = D({**off, "system": R(0.5, 100, src="ESTIMATE"), "lukas": R(98, 120)}, "system")
    check(d["do"] != "switch" and d.get("poll"), "an ESTIMATE of the live account never switches; it asks for a poll")
    d = D({"steven": R(10, 0.2), "system": R(0.5, 100), "lukas": R(40, 120)}, "lukas")
    check(d["do"] == "soft" and "steven" in d["why"], "steven resets in 12 min (lead 20): soft notice before the switch")
    d = D({**off, "system": R(0.5, 100), "lukas": R(100, 167.5)}, "lukas", state={"stopped": {"account": "lukas"}})
    check(d["do"] == "start", "hard-stopped on lukas, lukas's own reset: fleet-start, no switch")
    d = D({**off, "system": R(None, -0.1), "lukas": R(1.9, 120)}, "lukas")
    check(d.get("poll") and d["do"] != "stop", "system's reset just passed (no post-reset reading): poll before acting")
    mk = {SP.switch_key("system", "lukas", R(98, 120)): {"phase": "done"}}
    d = D({**off, "system": R(0.9, 100), "lukas": R(98, 120)}, "system", state={"_markers": mk})
    check(d["do"] == "hold", "a transition already done this week is never repeated")
    # use it or lose it: the soonest-expiring account with budget burns first (coordinator 2026-10-28 10:58)
    d = D({**off, "system": R(100, 167.9), "lukas": R(40, 3)}, "lukas")
    check(d["do"] == "normal", f"system just reset, lukas 40% expires in 3 h: stay on lukas (got {d['do']} {d.get('to')})")
    d = D({**off, "system": R(0.5, 0.2), "lukas": R(40, 3)}, "lukas")
    check(d["do"] == "normal", f"system's reset in 12 min will not pull the machine off lukas: no soft (got {d['do']})")
    d = D({"steven": R(100, 167.9), "system": R(100, 165), "lukas": R(30, 1.2)}, "lukas")
    check(d["do"] == "normal", f"steven just reset but lukas expires in 1.2 h: lukas first (got {d['do']} {d.get('to')})")
    d = D({"steven": R(100, 167), "system": R(98, 165), "lukas": R(0.9, 0.5)}, "lukas")
    check(d["do"] == "switch" and d["to"] == "steven", f"lukas spent: steven's window expires before system (got {d})")
    d = D({**off, "system": R(100, 165), "lukas": R(1.5, 3)}, "lukas")
    check(d["do"] == "soft", f"lukas at 1.5% with system to switch to: its line is 1 (soft, not stop) (got {d['do']})")
    d = D({**off, "system": R(1.5, 100), "lukas": R(1.8, 120)}, "lukas")
    check(d["do"] == "stop", f"no account with budget: pause at the 2% wait floor (got {d['do']})")
    mk = {SP.switch_key("system", "lukas", R(98, 120)): {"phase": "failed", "at": SP.iso(NOW - 60)}}
    d = D({**off, "system": R(0.9, 100), "lukas": R(98, 120)}, "system", state={"_markers": mk})
    check(d["do"] == "switch", f"a FAILED switch is retried next pass, never held (got {d['do']})")
    mk = {SP.switch_key("system", "lukas", R(98, 120)): {"phase": "pending", "at": SP.iso(NOW - 600)}}
    d = D({**off, "system": R(0.4, 100), "lukas": R(98, 120)}, "system", state={"_markers": mk})
    check(d["do"] == "stop", f"a pending switch that never landed while live is under its line: stop (got {d['do']})")
    d = D({**off, "system": R(0.9, 100), "lukas": R(98, 120)}, None)
    check(d["do"] == "skip", "live account unknown: skip")

    # the pool: every budget is due at its own expiry (use it or lose it), plus each account's next refill
    p = SP.pool({"steven": R(80, 168 - 8), "system": R(50, 100), "lukas": R(98, 120)}, NOW, PLAN, live="steven")
    # steven 28 by his window end (40 h); system 49 by 100 h; lukas (last to expire: wait line 2) 96 by 120 h
    by120 = sum(x["spend_pct"] for x in p["parts"] if x["by_h"] <= 120)
    check(abs(by120 - 173) < 0.01, f"this week's budgets: 28 + 49 + 96 = 173 due by lukas's reset, 120 h (got {by120})")
    # the refills (steven 48 by 208 h, system 99 by 268 h, lukas 98 by 288 h) make 418 by 288 h: 1.451 > 173/120
    check(abs(p["rate_pct_h"] - 418 / 288) < 0.01 and abs(p["deadline_h"] - 288) < 0.01 and abs(p["pct"] - 418) < 0.01,
          f"the binding deadline is the refills' 418% by 288 h (got {p['pct']} by {p['deadline_h']})")
    p = SP.pool({"steven": R(60, 168 - 46), "system": R(90, 100), "lukas": R(98, 120)}, NOW, PLAN, live="steven")
    check(abs(p["rate_pct_h"] - 4.0) < 0.01 and abs(p["deadline_h"] - 2) < 0.01,
          f"steven's 8% must go in the 2 h left of his window: 4%/h binds (got {p['rate_pct_h']})")
    p = SP.pool({"steven": R(22, 2), "system": R(100, 168), "lukas": R(7, 3)}, NOW, PLAN, live="system")
    check(abs(p["rate_pct_h"] - 2.0) < 0.01 and abs(p["deadline_h"] - 3) < 0.01,
          f"lukas's 6% expiring in 3 h binds at 2%/h (got {p['rate_pct_h']} by {p['deadline_h']})")
    sv = [x for x in p["parts"] if x["account"] == "steven"]
    check(len(sv) == 1 and abs(sv[0]["spend_pct"] - 48) < 0.01 and abs(sv[0]["by_h"] - 50) < 0.01,
          f"steven's coming window counts: 48% by 50 h (got {sv})")

    # one pass end to end, fake claude-account
    fake = TMP / "claude-account"
    calls = TMP / "calls.txt"
    fake.write_text("#!/usr/bin/env python3\nimport json,sys,os\nopen(%r,'a').write(' '.join(sys.argv[1:])+'\\n')\n"
                    "if 'status' in sys.argv: print(json.dumps({'machine':'testbox','live':os.environ.get('FAKE_LIVE'),"
                    "'armed':False}))\nelif os.environ.get('FAKE_FAIL') in sys.argv: sys.exit(3)\nelse: print(json.dumps({'ok':True}))\n" % str(calls))
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    os.environ["RM_CLAUDE_ACCOUNT"] = str(fake)
    os.environ["FAKE_LIVE"] = "system"
    SP.CA = str(fake)
    (TMP / "out").mkdir(exist_ok=True)
    SP.save_state({"gate_passed": True})
    meter = {**off, "system": R(0.9, 100), "lukas": R(98, 120)}
    rc = SP.check(dry=False, now=NOW, meter_fn=lambda: meter, poll_fn=lambda: None)
    seq = [ln.replace("--json ", "").split()[0] for ln in calls.read_text().splitlines() if ln.strip()]
    check(rc == 0 and seq[-3:] == ["arm", "use", "disarm"], f"switch pass: arm, use, disarm (got {seq})")
    mks = SP.read_markers()
    check(any(v.get("phase") == "done" for v in mks.values()), "the transition marker reads done")
    calls.write_text("")
    os.environ["FAKE_LIVE"] = "lukas"
    meter2 = {**off, "system": R(0.9, 100), "lukas": R(1.5, 120)}
    rc = SP.check(dry=False, now=NOW, meter_fn=lambda: meter2, poll_fn=lambda: None)
    seq = [ln.replace("--json ", "").split()[0] for ln in calls.read_text().splitlines() if ln.strip()]
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
    calls.write_text("")
    rc = SP.check(dry=True, now=NOW, meter_fn=lambda: meter, poll_fn=lambda: None)
    seq = [ln.replace("--json ", "").split()[0] for ln in calls.read_text().splitlines() if ln.strip()]
    check(all(s == "status" for s in seq), f"--dry-run calls nothing but status (got {seq})")
    print(f"{'FAILED ' + str(len(FAILS)) if FAILS else 'all passed'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
