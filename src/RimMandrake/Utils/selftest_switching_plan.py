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
    d = D({**off, "system": R(0.9, 100), "lukas": R(98, 120)}, None)
    check(d["do"] == "skip", "live account unknown: skip")

    # the pool
    p = SP.pool({"steven": R(80, 168 - 8), "system": R(50, 100), "lukas": R(98, 120)}, NOW, PLAN, live="steven")
    # steven: 28 by 40 h; system 49 + lukas 96 by system's reset (100 h)
    check(abs(p["pct"] - 173) < 0.01, f"pool = 28 + 49 + 96 = 173 (got {p['pct']})")
    check(abs(p["rate_pct_h"] - 1.73) < 0.01 and abs(p["deadline_h"] - 100) < 0.01,
          f"required rate 173/100 h binds at system's reset (got {p['rate_pct_h']} over {p['deadline_h']})")
    p = SP.pool({"steven": R(60, 168 - 46), "system": R(90, 100), "lukas": R(98, 120)}, NOW, PLAN, live="steven")
    check(abs(p["rate_pct_h"] - 4.0) < 0.01 and abs(p["deadline_h"] - 2) < 0.01,
          f"steven's 8% must go in the 2 h left of his window: 4%/h binds (got {p['rate_pct_h']})")
    p = SP.pool({"steven": R(22, 2), "system": R(100, 168), "lukas": R(7, 3)}, NOW, PLAN, live="system")
    # steven's next window opens in 2 h: 48 by 50 h; system 99 + lukas (refills before system's reset) 98 by 168 h
    check(abs(p["pct"] - (48 + 99 + 98)) < 0.01, f"steven's coming window and lukas's refill count (got {p['pct']})")

    # one pass end to end, fake claude-account
    fake = TMP / "claude-account"
    calls = TMP / "calls.txt"
    fake.write_text("#!/usr/bin/env python3\nimport json,sys,os\nopen(%r,'a').write(' '.join(sys.argv[1:])+'\\n')\n"
                    "if 'status' in sys.argv: print(json.dumps({'machine':'testbox','live':os.environ.get('FAKE_LIVE'),"
                    "'armed':False}))\nelse: print(json.dumps({'ok':True}))\n" % str(calls))
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
    rc = SP.check(dry=True, now=NOW, meter_fn=lambda: meter, poll_fn=lambda: None)
    seq = [ln.replace("--json ", "").split()[0] for ln in calls.read_text().splitlines() if ln.strip()]
    check(all(s == "status" for s in seq), f"--dry-run calls nothing but status (got {seq})")
    print(f"{'FAILED ' + str(len(FAILS)) if FAILS else 'all passed'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
