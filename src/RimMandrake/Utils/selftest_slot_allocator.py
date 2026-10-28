#!/usr/bin/env python3
"""selftest for slot_allocator.py (SLOT_ALLOCATOR_BUILD_RULES_FILE).

Pure rules first (decide() on hand-built inputs: every mode line, the budget fit and its per-seat split, the 13:05
hand baseline, presence, the 5-hour brake, hysteresis, the owner's word, the lent-account rule for steven), then the instruments on fixture files (running-helper count from
subagent transcripts, owner presence from a main transcript, the account meter and the streams record), then the CLI's
one line. No real transcript, meter or ledger is read: every path is a fixture under a temp dir.

    python3 src/RimMandrake/Utils/selftest_slot_allocator.py
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import slot_allocator as SA  # noqa: E402

FAILS = []
H = 3600.0
NOW = 1793050000.0


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  {detail}"))
    if not cond:
        FAILS.append(name)


def inp(**kw):
    base = {"seat": "BENCH", "account": "system", "source": "MEASURED", "week_pct_left": 40.0, "week_pct_used": 60.0,
            "hours_to_week_reset": 48.0, "week_resets_at": "2026-10-28T13:00-07:00", "session_pct_used": 18.0,
            "A1": 80, "D1": 32, "owner_window_min": None, "owner_card_min": None, "helpers_running": 2,
            "rate_pct_per_h": None, "mean_helpers": None, "override": None, "spare": []}
    base.update(kw)
    return base


R = SA.load_rules()


def d(state=None, **kw):
    return SA.decide(inp(**kw), state or {}, R, NOW)




# ---- token dial and the total
seats = lambda r: (r["seats"]["BENCH"], r["seats"]["FOUNDRY"])  # noqa: E731
r = d()
check("P from the meter: 40% left, 2.0 d -> 1.40", abs(r["inputs"]["P"] - 1.4) < 0.01, r["inputs"].get("P"))
check("P 1.40, no burn rate measured -> CRUISE step 6 total: BENCH 5, FOUNDRY 1",
      r["token_mode"] == "CRUISE" and seats(r) == (5, 1) and "no burn rate" in r["why"], (r["token_mode"], r["seats"], r["why"]))
check("no fixed cap of 5 anywhere", "cap 5" not in r["why"] and r["n_total"] == 6, r["why"])
r = d(rate_pct_per_h=1.2, mean_helpers=6.0)
check("13:05 hand baseline: 1.2%/h with 6 helpers, 40% over 48 h -> 4 total: BENCH 3, FOUNDRY 1",
      seats(r) == (3, 1) and "projected" in r["why"] and "69% of the rate" in r["why"], (r["seats"], r["why"]))
r = d(rate_pct_per_h=1.2, mean_helpers=6.0, rate_src="meter slope, 5 readings over 2.0 h")
check("why names where the rate came from", "meter slope" in r["why"], r["why"])
r = d({"token_mode": "CRUISE", "since": NOW - 5 * H, "total": 2}, rate_pct_per_h=1.2, mean_helpers=6.0)
check("the fit rises at most one per check: 2 -> 3, not 4", r["n_total"] == 3 and "raised one step" in r["why"], (r["n_total"], r["why"]))
r = d({"token_mode": "CRUISE", "since": NOW - 5 * H, "total": 8}, rate_pct_per_h=1.2, mean_helpers=6.0)
check("the fit falls at once: 8 -> 4", r["n_total"] == 4, r["n_total"])
r = d(rate_pct_per_h=0.5, mean_helpers=10.0)
check("a fit over the mode's ceiling stops at CRUISE 6", r["n_total"] == 6 and "ceiling 6" in r["why"], (r["n_total"], r["why"]))
r = d(rate_pct_per_h=1.2, mean_helpers=0.2)
check("too few helpers on average to fit a rate -> CRUISE step instead", r["n_total"] == 6 and "no burn rate" in r["why"], r["why"])
r = d(week_pct_left=10.0, week_pct_used=90.0, rate_pct_per_h=1.2, mean_helpers=6.0)
check("P 0.29 -> ALMOST_OUT, total 1: BENCH 1, FOUNDRY 0", r["token_mode"] == "ALMOST_OUT" and seats(r) == (1, 0), (r["token_mode"], r["seats"]))
r = d(week_pct_left=1.0, week_pct_used=99.0)
check("99% used -> DARK, 0 everywhere", r["token_mode"] == "DARK" and seats(r) == (0, 0), (r["token_mode"], r["seats"]))
r = d(week_pct_left=40.0, hours_to_week_reset=70.0)
check("CRUISE steps down with P when no rate: 0.96 -> 3 total (BENCH 3, FOUNDRY 0)", seats(r) == (3, 0), (r["inputs"]["P"], r["seats"]))
r = d(week_pct_left=40.0, hours_to_week_reset=115.0)
check("CRUISE steps down with P when no rate: 0.58 -> 2", r["n_total"] == 2, (r["inputs"]["P"], r["n_total"]))
# ---- hysteresis
st = {"token_mode": "CRUISE", "since": NOW - 5 * H, "pending": {"to": "BURN", "since": NOW - 2.5 * H}}
r = d(st, week_pct_left=80.0, hours_to_week_reset=40.0)
check("P 3.5 under 48 h, held 2 h -> BURN, ceiling 10", r["token_mode"] == "BURN" and r["n_total"] == 10, (r["token_mode"], r["n_total"]))
r = d({"token_mode": "CRUISE", "since": NOW - 5 * H}, week_pct_left=80.0, hours_to_week_reset=40.0)
check("BURN line just crossed (not held 2 h) -> still CRUISE", r["token_mode"] == "CRUISE"
      and r["state"]["pending"]["to"] == "BURN", r["state"])
ao = {"token_mode": "ALMOST_OUT", "since": NOW - 5 * H, "reset_at": "2026-10-28T13:00-07:00"}
r = d(ao, week_pct_left=20.0)
check("ALMOST_OUT holds at P 0.58 (leave line is 0.8)", r["token_mode"] == "ALMOST_OUT" and r["n_total"] == 1, r["token_mode"])
r = d(ao, week_pct_left=30.0)
check("ALMOST_OUT holds when P 0.88 is not yet held 2 h", r["token_mode"] == "ALMOST_OUT", r["token_mode"])
r = d(dict(ao, pending={"to": "CRUISE", "since": NOW - 2.5 * H}), week_pct_left=30.0)
check("ALMOST_OUT leaves after P > 0.8 held 2 h", r["token_mode"] == "CRUISE", r["token_mode"])
r = d(ao, week_pct_left=100.0, week_pct_used=0.0, hours_to_week_reset=167.0, week_resets_at="2026-11-04T13:00-07:00")
check("a weekly reset ends ALMOST_OUT at once", r["token_mode"] == "CRUISE", r["token_mode"])
r = d({"token_mode": "CRUISE", "since": NOW - 10 * 60}, week_pct_left=10.0, week_pct_used=90.0)
check("stepping DOWN to ALMOST_OUT ignores the 60 min minimum", r["token_mode"] == "ALMOST_OUT", r["token_mode"])
bu = {"token_mode": "BURN", "since": NOW - 3 * H}
r = d(bu, week_pct_left=40.0)
check("BURN holds at P 1.4 (leave line 1.2)", r["token_mode"] == "BURN", r["token_mode"])
r = d(bu, week_pct_left=30.0)
check("BURN under P 1.2 -> SWEEP, ceiling 3", r["token_mode"] == "SWEEP" and r["n_total"] == 3, (r["token_mode"], r["n_total"]))
r = d({"token_mode": "SWEEP", "since": NOW - 13 * H})
check("SWEEP ends after 12 h", r["token_mode"] == "CRUISE", r["token_mode"])
r = d(session_pct_used=95.0)
check("session window 95% used -> 0 everywhere whatever the mode", seats(r) == (0, 0) and "5-hour" in r["why"], (r["seats"], r["why"]))
r = d(source="UNMEASURED", week_pct_left=None, week_pct_used=None, hours_to_week_reset=None)
check("UNMEASURED meter, no history -> total 2, says blind", r["n_total"] == 2 and "UNMEASURED" in r["why"], (r["n_total"], r["why"]))
r = d({"token_mode": "ALMOST_OUT", "since": NOW - H, "total": 1}, source="UNMEASURED", week_pct_left=None, hours_to_week_reset=None)
check("UNMEASURED meter holds the previous mode and total", r["token_mode"] == "ALMOST_OUT" and r["n_total"] == 1, r["token_mode"])
r = d({"token_mode": "CRUISE", "since": NOW - 5 * H}, source="ESTIMATE", week_pct_left=80.0, hours_to_week_reset=40.0)
check("an ESTIMATE never enters BURN", r["token_mode"] == "CRUISE" and not r["state"].get("pending"), r["state"])
# ---- presence and queues
r = d(owner_window_min=4.0)
check("owner wrote 4 min ago -> BENCH presence, and NO lower N for it", r["presence"] == "BENCH" and seats(r) == (5, 1), (r["presence"], r["seats"]))
r = d(owner_window_min=45.0)
check("45 min since a window message -> PHONE, no BENCH cap", r["presence"] == "PHONE" and seats(r) == (5, 1), (r["presence"], r["seats"]))
r = d(owner_card_min=10.0)
check("a card 10 min ago -> PHONE", r["presence"] == "PHONE", r["presence"])
r = d(owner_window_min=70.0, owner_card_min=90.0)
check("no message and no card for 60 min -> AFK", r["presence"] == "AFK", r["presence"])
check("D1 32 -> PAYDOWN", d()["queue_mode"] == "PAYDOWN")
r = d(A1=10, D1=2)
check("A1 10, D1 2 -> CLEAR", r["queue_mode"] == "CLEAR", r["queue_mode"])
r = d({"queue_mode": "PAYDOWN"}, A1=70, D1=2)
check("PAYDOWN holds until A1 under 60", r["queue_mode"] == "PAYDOWN", r["queue_mode"])
r = d(A1=None, D1=None)
check("unmeasured queues fire nothing", r["queue_mode"] == "UNMEASURED", r["queue_mode"])
# ---- his word
ov = lambda **k: dict({"ownerSaid": "go to seven", "until": SA.iso_local(NOW + H)}, **k)  # noqa: E731
r = d(override=ov(n=7))
check("owner's word N 7 sets BENCH 7", r["seats"]["BENCH"] == 7 and "go to seven" in r["why"], (r["seats"], r["why"]))
r = d(override=ov(seats={"FOUNDRY": 2}))
check("owner's word per seat: FOUNDRY 2, BENCH as computed", seats(r) == (5, 2), r["seats"])
r = d(override=ov(n=7, until=SA.iso_local(NOW - 60)))
check("an expired owner word is ignored", seats(r) == (5, 1), r["seats"])
r = d(override=ov(mode="ALMOST_OUT"))
check("owner names ALMOST_OUT -> BENCH 1, FOUNDRY 0", seats(r) == (1, 0) and r["mode"].startswith("ALMOST_OUT"), (r["mode"], r["seats"]))
r = d(override=ov(n=7), session_pct_used=95.0)
check("the 5-hour brake binds even over the owner's word", seats(r) == (0, 0), r["seats"])
# ---- lent account: steven (owner 13:10). The REAL rules file carries his numbers as data.
pol = R["lent_accounts"]["steven"]
check("rules data: steven floor 10%, at most 50% used by us, off-limits through his 10-28 reset",
      pol["floor_pct_left"] == 10 and pol["max_used_by_us_pct"] == 50
      and SA.epoch(pol["off_limits_through"]) == SA.epoch("2026-10-28T15:00:00-07:00"), pol)
stv = lambda left, h: {"account": "steven", "pct_left": left, "pct_used": 100.0 - left, "hours_to_reset": h,  # noqa: E731
                       "resets_at": SA.iso_local(NOW + h * H), "source": "ESTIMATE"}
r = d(spare=[stv(31.0, 49.9)])
check("this week steven is off-limits: no spare line for him (today: 31% left)", "steven" not in r["why"], r["why"])
ok, why = SA.check_plan(stv(31.0, 49.9), 1.0, R, NOW)
check("this week any draw on steven is refused, even 1%", not ok and "off-limits" in why, why)
R2 = json.loads(json.dumps(R))
R2["lent_accounts"]["steven"]["off_limits_through"] = None
cp = lambda left, h, draw: SA.check_plan(stv(left, h), draw, R2, NOW)[0]  # noqa: E731
check("fresh reset (150 h to go), 80% left: up to 30% more is allowed (50% used cap)", cp(80, 150, 30) and not cp(80, 150, 31))
check("10 h after reset with 20% used: allowed up to 50% used", cp(80, 158, 30) and not cp(80, 158, 31))
check("edge: exactly 48 h after reset still in the window, just past it is 0", cp(80, 120, 30) and not cp(80, 119.9, 1))
check("60 h after reset (108 h to go), 20% used: 0", not cp(80, 108, 1))
check("30 h before reset, 20% used: 0 (end-of-week drawdown withdrawn)", not cp(80, 30, 1))
check("near his reset (10 h), 31% left: 0, not down to the floor", not cp(31, 10, 1))
check("fresh reset at 55% left: only 5% more (45% already used)", cp(55, 150, 5) and not cp(55, 150, 10))
check("fresh reset at 31% left (69% used): nothing", not cp(31, 150, 1))
bad = []
for left in range(0, 101, 3):
    for h in (1, 10, 23, 24, 25, 60, 119, 120, 150, 167):
        for draw in range(1, 101, 2):
            if cp(left, h, draw) and (left - draw < 10 or h < 120 or (100 - left) + draw > 50):
                bad.append((left, h, draw))
check("no accepted plan takes steven under 10%, over 50% used, or outside the 48 h after reset (sweep)", not bad, bad[:5])
r = SA.decide(inp(spare=[stv(80.0, 150.0)]), {}, R2, NOW)
check("a lent account is recommended only when the rule allows, naming the share", "steven may lend 30%" in r["why"]
      and "fresh reset" in r["why"] and "never automatic" in r["why"], r["why"])
r = d(spare=[{"account": "lukas", "pct_left": 7.0, "pct_used": 93.0, "hours_to_reset": 51.0},
             {"account": "other", "pct_left": 40.0, "pct_used": 60.0, "hours_to_reset": 51.0}])
check("an owned spare is named over 10% left only", "other has 40% unused" in r["why"] and "lukas" not in r["why"], r["why"])
p = subprocess.run([sys.executable, str(HERE / "slot_allocator.py"), "plan", "--help"], capture_output=True, text=True, timeout=60)
check("CLI has a plan check for a lent account", p.returncode == 0 and "--draw" in p.stdout, p.stderr[-300:])

# ---- line
ln = SA.line(d())
check("one line: mode, N per seat, why", ln.startswith("CRUISE") and " N=5 BENCH, FOUNDRY 1 " in ln and "P 1.40" in ln
      and "\n" not in ln, ln)

# ---- instruments on fixtures
tmp = Path(tempfile.mkdtemp(prefix="slotalloc_"))
proj = tmp / "projects" / "-home-mandrake-rm-bench"
sub = proj / "sess1" / "subagents"
sub.mkdir(parents=True)
real_now = time.time()


def tx(name, recs, age):
    p = sub / f"agent-{name}.jsonl"
    p.write_text("".join(json.dumps(x) + "\n" for x in recs))
    os.utime(p, (real_now - age, real_now - age))
    return p


A = lambda stop, mid=None: {"type": "assistant", "timestamp": SA.iso_z(real_now - 3500),  # noqa: E731
                           "message": {"role": "assistant", "id": mid, "stop_reason": stop, "content": [{"type": "text", "text": "x"}]}}
U = {"type": "user", "timestamp": SA.iso_z(real_now - 3600), "message": {"role": "user", "content": "go on"}}
tx("working", [U, A("tool_use")], 30)
tx("between_calls", [U, A("tool_use"), {"type": "api-request"}], 400)
tx("done_old", [U, A("end_turn")], 400)
tx("done_just_now", [U, A("end_turn")], 20)
tx("ended_with_tool", [U, dict(A("end_turn"), message={"role": "assistant", "stop_reason": "end_turn", "content": [{"type": "tool_use"}]})], 20)
tx("ended_then_noise", [U, A("end_turn"), {"type": "api-request"}, {"type": "api-request-blob", "message": {"role": "assistant", "content": [{"type": "tool_use"}]}}], 20)
tx("resumed", [U, A("end_turn"), U], 60)
tx("dead_silent", [U, A("tool_use")], 2000)
tx("unparsable", [U], 50)
(sub / "agent-working.meta.json").write_text("{}")
run = SA.running_helpers([proj], real_now, R)
ids = sorted(x["id"] for x in run)
check("running helpers: a clean end_turn is finished AT ONCE; ambiguous endings still run",
      ids == ["between_calls", "ended_with_tool", "resumed", "unparsable", "working"], ids)
for extra in ("ended_with_tool", "ended_then_noise"):  # keep the mean-helpers fixture below as it was
    (sub / f"agent-{extra}.jsonl").unlink()

# ---- overage and payback
OV = {"ownerSaid": "go to 8", "until": SA.iso_local(NOW + 5 * H), "seats": {"BENCH": 8}}
r = d({"token_mode": "CRUISE", "since": NOW - 5 * H, "overage_t": NOW - H}, helpers_running={"BENCH": 8, "FOUNDRY": 1}, override=OV)
check("overage: 8 BENCH running over a computed 5 for 1 h under his word -> 3 helper-h owed, no payback while it holds",
      abs(r["overage"]["owed_h"] - 3.0) < 1e-6 and not r["overage"]["paying"] and seats(r)[0] == 8, (r["overage"], r["seats"]))
r2 = d(r["state"], helpers_running={"BENCH": 5, "FOUNDRY": 1}, owner_window_min=300.0)
check("overage: no lower N applies just because he is present (window 4 min, no debt -> BENCH 5)",
      seats(d(owner_window_min=4.0)) == (5, 1))
st = dict(r["state"], overage_t=NOW - 0.25 * H)
r2 = d(st, helpers_running={"BENCH": 5, "FOUNDRY": 1}, owner_window_min=300.0, hours_to_week_reset=26.0)
check("payback: word lapsed, he is away -> N lowered by ceil(owed / (hours to reset - margin)) = ceil(3/20) = 1: BENCH 4",
      r2["overage"]["paying"] and r2["overage"]["cut"] == 1 and seats(r2)[0] == 4 and "lowered by 1" in r2["why"], (r2["overage"], r2["seats"]))
check("payback: the deadline is before the reset", r2["overage"]["deadline_h"] < 26.0, r2["overage"])
r3 = d(st, helpers_running={"BENCH": 5, "FOUNDRY": 1}, owner_window_min=300.0, hours_to_week_reset=8.0)
check("payback: near the reset N is cut harder (ceil(3/2) = 2: BENCH 3)", seats(r3)[0] == 3 and r3["overage"]["cut"] == 2, (r3["overage"], r3["seats"]))
st9 = dict(r["state"], overage_h=40.0, overage_t=NOW)
r4 = d(st9, helpers_running={"BENCH": 1, "FOUNDRY": 0}, owner_window_min=300.0, hours_to_week_reset=8.0)
check("payback: never below N=1 for BENCH, and says the rest is forgiven at the reset",
      seats(r4)[0] >= 1 and "forgiven at the reset" in r4["overage"]["plan"], (r4["overage"], r4["seats"]))
r5 = d(dict(r["state"], overage_t=NOW - H), helpers_running={"BENCH": 2, "FOUNDRY": 0}, owner_window_min=300.0)
check("payback: unused helper-hours are credited and the debt falls (3 owed, 3 under for 1 h -> 0)",
      r5["overage"]["owed_h"] == 0 and r5["overage"]["credited_h"] == 3.0, r5["overage"])
r6 = d(dict(r["state"], overage_t=NOW - H), helpers_running={"BENCH": 5, "FOUNDRY": 1}, owner_window_min=3.0)
check("payback waits while he is in a window", not r6["overage"]["paying"] and seats(r6)[0] == 5 and r6["overage"]["owed_h"] == 3.0, (r6["overage"], r6["seats"]))
r7 = d(dict(r["state"], reset_at="2026-10-26T01:00-07:00", overage_t=NOW), helpers_running={"BENCH": 5, "FOUNDRY": 1}, owner_window_min=300.0)
check("a weekly reset forgives the remaining debt", r7["overage"]["owed_h"] == 0 and r7["overage"]["forgiven_h"] == 3.0, r7["overage"])
check("interactive work above N is recorded without any override",
      abs(d({"overage_t": NOW - 0.5 * H}, helpers_running={"BENCH": 7, "FOUNDRY": 1}, owner_window_min=2.0)["overage"]["owed_h"] - 1.0) < 1e-6)

# presence from a main transcript
mainp = proj / "sess1.jsonl"
recs = [{"type": "user", "timestamp": SA.iso_z(real_now - 50 * 60), "origin": {"kind": "human"},
         "message": {"role": "user", "content": "please build it"}},
        {"type": "user", "timestamp": SA.iso_z(real_now - 5 * 60), "origin": {"kind": "task-notification"},
         "message": {"role": "user", "content": "<task-notification>done</task-notification>"}},
        {"type": "user", "timestamp": SA.iso_z(real_now - 4 * 60),
         "message": {"role": "user", "content": [{"type": "tool_result", "content": "x"}]}},
        {"type": "assistant", "timestamp": SA.iso_z(real_now - 60), "message": {"role": "assistant", "content": "ok"}}]
mainp.write_text("x" * 100 + "\n" + "".join(json.dumps(x) + "\n" for x in recs))
t = SA.owner_last_window([proj], real_now)
check("owner presence: last human message, not a notification or tool result",
      t is not None and abs((real_now - t) / 60 - 50) < 0.2, t)
ts = SA.owner_window_times([proj], real_now, 3 * H)
check("S8b: owner_window_times lists his typed messages only (one, 50 min ago)",
      len(ts) == 1 and abs((real_now - ts[0]) / 60 - 50) < 0.2, ts)
mh = SA.mean_helpers([proj], real_now, 3 * H)
check("mean helpers over 3 h from first record to last write (about 2.1)", 1.9 < mh < 2.3, mh)
fp = tmp / "projects" / "-home-mandrake-rm-foundry"
fp.mkdir()
(fp / "s2.jsonl").write_text("".join(json.dumps(A("tool_use", m)) + "\n" for m in ("m1", "m2", "m2", "m3")))
old = dict(A("tool_use", "m0"), timestamp=SA.iso_z(real_now - 4 * H))
(fp / "s3.jsonl").write_text(json.dumps(old) + "\n" + json.dumps(A("end_turn", "m4")) + "\n")
n = SA.messages_in_window(tmp / "projects", real_now, 3 * H)
check("messages in the window: distinct ids, older ones dropped (4)", n == 4, n)

# full gather from fixture meter + streams + ledger
au = tmp / "au"
au.mkdir()
iso = SA.iso_local
(au / "latest.json").write_text(json.dumps({"schema": 1, "updated": iso(real_now), "accounts": {
    "system": {"account": "system", "machine": "testhost", "source": "MEASURED", "ts": iso(real_now),
               "measured_at": iso(real_now - 60), "week_pct_used": 60.0, "week_resets_at": iso(real_now + 48 * H),
               "session_pct_used": 18.0, "session_resets_at": iso(real_now + 3 * H)},
    "other": {"account": "other", "machine": "elsewhere", "source": "MEASURED", "ts": iso(real_now),
              "measured_at": iso(real_now - 60), "week_pct_used": 93.0, "week_resets_at": iso(real_now + 51 * H)}}}))
(au / "series.jsonl").write_text("")
os.environ["RM_ACCOUNT_USAGE_DIR"] = str(au)
srs = [{"ts": iso(real_now - k * 1800), "account": "system", "source": "MEASURED", "measured_at": iso(real_now - k * 1800),
        "week_pct_used": 60.0 - k * 0.5, "week_resets_at": iso(real_now + 48 * H)} for k in (4, 3, 2, 1, 0)]
(au / "series.jsonl").write_text("".join(json.dumps(x) + "\n" for x in srs))
rate, npts, span = SA.slope("system", iso(real_now + 48 * H), real_now, R)
check("slope from account_usage's series: 5 readings over 2 h, 1.0%/h", rate is not None and abs(rate - 1.0) < 0.01
      and npts == 5, (rate, npts, span))
rate, npts, span = SA.slope("system", iso(real_now + 48 * H), real_now, dict(R, fit=dict(R["fit"], slope_min_points=6)))
check("too few readings -> no slope (fallback to messages)", rate is None, rate)
(au / "series.jsonl").write_text(json.dumps(srs[-1]) + "\n")
streams = tmp / "streams"
streams.mkdir()
(streams / "series.jsonl").write_text(json.dumps({"t": real_now - 300, "measures": {
    "A1": {"v": 80, "m": "MEASURED"}, "D1": {"v": 32, "m": "MEASURED"}}}) + "\n")
owner = tmp / "OWNER.jsonl"
owner.write_text(json.dumps({"seat": "OWNER", "event": "note", "byCard": "Q -> A", "ts": SA.iso_z(real_now - 20 * 60)}) + "\n")
env = dict(os.environ, RM_OPS_WATCH_DIR=str(tmp / "ops_watch"), RM_ACCOUNT_USAGE_DIR=str(au), RM_STREAMS_DIR=str(streams), RM_SLOT_PROJECTS=str(tmp / "projects"),
           RM_SLOT_OWNER_LEDGER=str(owner), RM_SLOT_MACHINE="testhost", AGENT_SEAT="BENCH")
cli = [sys.executable, str(HERE / "slot_allocator.py")]
p = subprocess.run(cli + ["now", "--json"], env=env, capture_output=True, text=True, timeout=60)
try:
    j = json.loads(p.stdout)
except ValueError:
    j = {}
check("CLI now --json runs", p.returncode == 0 and j, p.stderr[-400:])
ji = j.get("inputs") or {}
check("burn account auto = this machine's live login (system, not the 93% one)", ji.get("account") == "system", ji)
check("gather reads A1/D1 from the streams record", ji.get("A1") == 80 and ji.get("D1") == 32, ji)
check("gather counts the fixture's 4 running helpers on BENCH, 0 on FOUNDRY",
      ji.get("helpers_running") == {"BENCH": 4, "FOUNDRY": 0}, ji.get("helpers_running"))
check("one meter reading -> rate from this machine's message count", "4 messages" in (ji.get("rate_src") or ""), ji.get("rate_src"))
check("presence: window 50 min, card 20 min -> PHONE", j.get("presence") == "PHONE", (j.get("presence"), ji))
p = subprocess.run(cli + ["now"], env=env, capture_output=True, text=True, timeout=60)
out = p.stdout.strip()
check("CLI now prints exactly one line naming mode and N", p.returncode == 0 and len(out.splitlines()) == 1
      and out.startswith("CRUISE") and "N=5 BENCH, FOUNDRY 1" in out, out)
p = subprocess.run(cli + ["now", "--write"], env=env, capture_output=True, text=True, timeout=60)
al = json.loads((streams / "allocation.json").read_text()) if (streams / "allocation.json").exists() else {}
check("--write records allocation.json with mode, N per seat and state", al.get("seats") == {"BENCH": 5, "FOUNDRY": 1}
      and al.get("state", {}).get("token_mode") == "CRUISE",
      al)
p = subprocess.run(cli + ["set", "--n", "2", "--owner-said", "two for now"], env=env, capture_output=True, text=True, timeout=60)
p2 = subprocess.run(cli + ["now"], env=env, capture_output=True, text=True, timeout=60)
check("set --owner-said takes effect", p.returncode == 0 and "N=2" in p2.stdout and "two for now" in p2.stdout, p.stderr + p2.stdout)
p = subprocess.run(cli + ["set", "--n", "2"], env=env, capture_output=True, text=True, timeout=60)
check("set without the owner's words is refused", p.returncode != 0, p.stdout)
subprocess.run(cli + ["clear"], env=env, capture_output=True, text=True, timeout=60)
p2 = subprocess.run(cli + ["now"], env=env, capture_output=True, text=True, timeout=60)
check("clear drops the owner's word", "N=5 BENCH" in p2.stdout, p2.stdout)

check("CLI: no ops status -> the decision says so and changes nothing", "no ops watch status" in p2.stdout, p2.stdout)

# ---- the ops watch feed (ops_watch.py status.json, V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE)
OPS_OK = {"ok": True, "age_min": 5, "root_free_gb": 450.0, "codex_runway": 3.0, "steve_state": "RUNNING",
          "steve_unowned_stall_min": 0.0, "steve_invalid_streak": 0, "alarms_open": []}
ops = lambda **k: dict(OPS_OK, **k)  # noqa: E731
base_seats = seats(d())
r = d(ops=ops())
check("ops all OK changes no seat", seats(r) == base_seats and r["ops"] == {"disk": "OK", "codex": "OK", "steve_lane": "OK"},
      (seats(r), r["ops"]))
r = d(ops=ops(root_free_gb=150.0))
check("disk under the DISK_LOW line caps the total at disk_brake_total", r["n_total"] == R["ops"]["disk_brake_total"]
      and r["ops"]["disk"] == "BRAKE" and "disk brake" in r["why"], (r["n_total"], r["why"]))
r = d(ops=ops(root_free_gb=150.0), override=ov(n=7))
check("his word stands over the disk brake (BENCH 7) and says so", r["seats"]["BENCH"] == 7
      and "his word stands over the disk brake" in r["why"], (r["seats"], r["why"]))
r = d(ops=ops(root_free_gb=None))
check("an UNMEASURED disk brakes nothing (never read as 0 GB)", seats(r) == base_seats and r["ops"]["disk"] == "UNMEASURED",
      (seats(r), r["ops"]))
r = d(ops=ops(codex_runway=0.6))
check("Codex runway 0.6 -> CONSERVE advice, seats unchanged", r["ops"]["codex"] == "CONSERVE" and seats(r) == base_seats
      and "Codex runway 0.60" in r["why"], (r["ops"], r["why"]))
r = d(ops=ops(steve_unowned_stall_min=45.0))
check("Steve stalled 45 min unowned -> STALLED advice", r["ops"]["steve_lane"] == "STALLED" and "Steve lane STALLED" in r["why"],
      r["ops"])
r = d(ops=ops(steve_invalid_streak=3))
check("3 INVALID in a row -> INVALID_STREAK advice", r["ops"]["steve_lane"] == "INVALID_STREAK", r["ops"])
r = d(ops={"ok": False, "why": "ops watch status is 90 min old (rm-ops-watch.timer stopped?)"})
check("a stale ops status is ignored and named", seats(r) == base_seats and "90 min old" in r["why"]
      and r["ops"]["disk"] == "UNMEASURED", r["why"])
r = d(ops=ops(root_free_gb=150.0), session_pct_used=95.0)
check("the session brake still zeroes everything under a disk brake", r["n_total"] == 0, r["seats"])
od = tmp / "ops_watch_unit"
od.mkdir(parents=True, exist_ok=True)
os.environ["RM_OPS_WATCH_DIR"] = str(od)
(od / "status.json").write_text(json.dumps({"t": NOW - 600, "points": {
    "disk.root_free_gb": {"v": 100.0, "m": "MEASURED"}, "codex.runway": {"v": 0.5, "m": "ESTIMATE"},
    "steve.unowned_stall_min": {"v": None, "m": "UNMEASURED"}, "steve.invalid_streak": {"v": 4, "m": "MEASURED"}},
    "alarms": {"DISK_LOW:disk.root_free_gb": {"state": "OPEN"}, "X:y": {"state": "CLEARED"}}}))
oi = SA.ops_inputs(NOW, R)
check("ops_inputs reads MEASURED points, Codex ESTIMATE, drops UNMEASURED, lists open alarms",
      oi["ok"] and oi["root_free_gb"] == 100.0 and oi["codex_runway"] == 0.5 and oi["steve_unowned_stall_min"] is None
      and oi["steve_invalid_streak"] == 4 and oi["alarms_open"] == ["DISK_LOW:disk.root_free_gb"], oi)
oi = SA.ops_inputs(NOW + 3 * H, R)
check("ops_inputs: a status 3 h old is not ok", not oi["ok"] and "old" in oi["why"], oi)
(od / "status.json").write_text(json.dumps({"t": NOW - 600, "points": {
    "disk.root_free_gb": {"v": 50.0, "m": "ESTIMATE"}, "codex.runway": {"v": 0.4, "m": "ESTIMATE"},
    "steve.unowned_stall_min": {"v": 90, "m": "ESTIMATE"}, "steve.invalid_streak": {"v": 9, "m": "ESTIMATE"}}}))
oi = SA.ops_inputs(NOW, R)
check("ops_inputs: ESTIMATE disk and Steve readings are dropped; a Codex ESTIMATE counts",
      oi["ok"] and oi["root_free_gb"] is None and oi["steve_unowned_stall_min"] is None
      and oi["steve_invalid_streak"] is None and oi["codex_runway"] == 0.4, oi)
r = d(ops=oi)
check("an ESTIMATE low disk applies no brake", r["ops"]["disk"] == "UNMEASURED" and seats(r) == base_seats, r["ops"])
(od / "status.json").write_text(json.dumps({"t": NOW - 600, "points": {
    "disk.root_free_gb": {"v": "150", "m": "MEASURED"}, "codex.runway": {"v": None, "m": "MEASURED"},
    "steve.invalid_streak": {"v": float("inf"), "m": "MEASURED"}, "steve.state": {"v": 3, "m": "MEASURED"},
    "steve.unowned_stall_min": [1]}, "alarms": {"a": "OPEN"}}))
oi = SA.ops_inputs(NOW, R)
check("ops_inputs: malformed values (string GB, Infinity, a list point, a non-dict alarm) are ignored, not a crash",
      oi["ok"] and oi["root_free_gb"] is None and oi["steve_invalid_streak"] is None and oi["steve_state"] is None
      and oi["steve_unowned_stall_min"] is None and oi["alarms_open"] == [], oi)
r = d(ops=oi)
check("decide() survives a malformed ops status", r["ops"]["disk"] == "UNMEASURED", r["ops"])
for bad_t in ("NaN", "Infinity", None, True):
    (od / "status.json").write_text(json.dumps({"t": float(bad_t) if isinstance(bad_t, str) else bad_t, "points": {
        "disk.root_free_gb": {"v": 100.0, "m": "MEASURED"}}}))
    oi = SA.ops_inputs(NOW, R)
    check(f"ops_inputs: status time {bad_t!r} is not fresh", not oi["ok"], oi)

(od / "status.json").write_text('{"t": 1' + '0' * 400 + ', "points": {}}')
oi = SA.ops_inputs(NOW, R)
check("ops_inputs: a status time too big for a float is not fresh, not a crash", not oi["ok"], oi)
(od / "status.json").write_text(json.dumps({"t": NOW + 3600, "points": {"disk.root_free_gb": {"v": 1.0, "m": "MEASURED"}}}))
oi = SA.ops_inputs(NOW, R)
check("ops_inputs: a status stamped an hour in the future is not fresh", not oi["ok"] and "future" in oi["why"], oi)

# ---- GPT round K (2026-10-27): tightening fixes
r = d({"token_mode": "BURN", "since": NOW - 3 * H}, week_pct_left=2.0, week_pct_used=90.0)
check("BURN with P under the ALMOST_OUT line goes straight to ALMOST_OUT, not SWEEP",
      r["token_mode"] == "ALMOST_OUT", (r["token_mode"], r["inputs"]["P"]))
r = d(session_pct_used=95.0, source="STALE")
check("a STALE 5-hour reading brakes nothing (it may predate the reset)",
      r["n_total"] > 0 and "not braking" in r["why"], (r["seats"], r["why"]))
r = d(session_pct_used=95.0, source="ESTIMATE")
check("an ESTIMATE 5-hour reading brakes nothing", r["n_total"] > 0, r["seats"])
r = d({"token_mode": "SWEEP", "since": NOW - H, "total": 40}, source="UNMEASURED", week_pct_left=None,
      hours_to_week_reset=None, week_pct_used=None)
check("blind: a held total from an expired override is cut to the held mode's ceiling",
      r["n_total"] <= R["token"]["SWEEP"]["n"], (r["n_total"], r["why"]))
r = d(override=ov(mode="cross_hold_h"))
check("an override naming a scalar token key is not a mode (no crash, no relabel)",
      not r["mode"].startswith("cross_hold_h"), r["mode"])

r = d(override=ov(mode=["CRUISE"]))
check("an override whose mode is a list is not a mode (no crash)", r["mode"].endswith("+OWNER"), r["mode"])

r = d({"token_mode": "CRUISE", "since": NOW - 5 * H, "pending": {"to": "BURN", "since": NOW - 2.5 * H}, "total": 6},
      week_pct_left=10.0, week_pct_used=90.0, hours_to_week_reset=3.0)
check("BURN is never entered inside its own exit window (3 h to reset)", r["token_mode"] != "BURN", r["token_mode"])
r = d({"token_mode": "CRUISE", "since": NOW - 5 * H, "total": 6}, week_pct_used=99.0, week_pct_left=1.0,
      hours_to_week_reset=None)
check("MEASURED 99% used with no reset time is DARK, not a held CRUISE", r["token_mode"] == "DARK"
      and r["n_total"] <= R["token"]["DARK"]["n"], (r["token_mode"], r["n_total"]))

r = d({"token_mode": "CRUISE", "since": NOW - 5 * H, "queue_mode": "PAYDOWN"}, A1=20, D1=None)
check("an unmeasured D1 does not clear PAYDOWN", r["queue_mode"] == "PAYDOWN", r["queue_mode"])
r = d(override=ov(n=None, seats={"bench": 0}))
check("an override for seat 'bench' zeroes BENCH, never adds a 'bench' seat beside it",
      r["seats"].get("BENCH") == 0 and "bench" not in r["seats"], r["seats"])

# ---- review round P fixes
r = d({"token_mode": "CRUISE", "since": NOW - 5 * H, "queue_mode": "PAYDOWN"}, A1=None, D1=None)
check("PAYDOWN held when both queue counts are unmeasured", r["queue_mode"] == "PAYDOWN", r["queue_mode"])
r = d({"token_mode": "CRUISE", "since": NOW - 5 * H, "queue_mode": "CLEAR"}, A1=None, D1=None)
check("both queue counts unmeasured from CLEAR stays UNMEASURED", r["queue_mode"] == "UNMEASURED", r["queue_mode"])

ST = {"token_mode": "CRUISE", "since": NOW - 5 * H, "overage_h": 4.0, "overage_t": NOW - H, "total": 6}
r = d(ST, helpers_running={"BENCH": None, "FOUNDRY": None}, presence_unused=True)
check("unavailable helper counts do not credit overage debt", r["overage"]["owed_h"] == 4.0
      and r["overage"]["credited_h"] == 0 and "unavailable" in r["why"], (r["overage"], r["why"]))
r = d(ST, helpers_running={"BENCH": 0, "FOUNDRY": 0})
check("measured zero helpers still credits (control)", r["overage"]["credited_h"] > 0, r["overage"])
with tempfile.TemporaryDirectory() as td:
    missing = Path(td) / "nope"
    class _P(dict):
        pass
    hr = {s: (len(SA.running_helpers([p], NOW, R)) if os.path.isdir(p) and os.access(p, os.R_OK | os.X_OK) else None)
          for s, p in {"BENCH": missing}.items()}
    check("a missing transcript dir reads None, not 0", hr == {"BENCH": None}, hr)

r = d(override=ov(mode="BURN", n=None, seats=None))
check("a mode-only override splits the mode total by the FOUNDRY share, not all to BENCH",
      r["seats"]["FOUNDRY"] == int(R["token"]["BURN"]["n"] * R["split"]["FOUNDRY_share"]) and r["n_total"] == R["token"]["BURN"]["n"],
      (r["seats"], r["mode"]))

u, e = SA.override_until(None, None, None, NOW)
check("set without --hours and no known reset is an error, not 24 h", u is None and e and "unavailable" in e, (u, e))
u, e = SA.override_until(None, None, "2026-10-29T13:00-07:00", NOW)
check("set without --hours takes the meter's reset when nothing is persisted", u == "2026-10-29T13:00-07:00" and e is None, (u, e))
u, e = SA.override_until(None, "2026-10-01T00:00-07:00", None, NOW)
check("a persisted reset already past is not used", u is None and e, (u, e))
u, e = SA.override_until(2, None, None, NOW)
check("--hours still works with no reset", e is None and u, (u, e))

# ---- session cap (Conductor session mode)
CAP = 6.0
sit = lambda left=40.0, last=NOW - 0.5 * H: {"sitting": {"start": NOW - 1 * H, "start_left": left, "last_active": last,  # noqa: E731
                                                          "reset_at": "2026-10-28T13:00-07:00"}}
r = d(sit(), session_cap_pct=CAP, owner_window_t=NOW - 0.5 * H, week_pct_left=33.0, week_pct_used=67.0)
check("cap: a 7-point drop since sitting start -> BENCH 0 with the reason",
      r["seats"]["BENCH"] == 0 and "session cap reached: 7.0% of the week this sitting" in r["why"], (r["seats"], r["why"]))
r = d(sit(), session_cap_pct=CAP, owner_window_t=NOW - 0.5 * H, week_pct_left=36.0, week_pct_used=64.0)
check("cap: a 4-point drop leaves BENCH alone", r["seats"]["BENCH"] > 0 and "reached" not in r["why"], (r["seats"], r["why"]))
r = d(sit(), session_cap_pct=CAP, owner_window_t=NOW - 0.5 * H, week_pct_left=34.0, week_pct_used=66.0)
check("cap: exactly the cap (6.0) refuses", r["seats"]["BENCH"] == 0, r["seats"])
r = d({}, session_cap_pct=CAP, owner_window_t=NOW - 600, week_pct_left=40.0)
st = r["state"]["sitting"]
check("cap: first message after idle stamps a sitting at the current week_left", st["start_left"] == 40.0 and st["start"] == NOW - 600, st)
r = d(sit(), session_cap_pct=CAP, owner_window_t=NOW - 600, week_pct_left=20.0)
check("cap: a message 30 min into a live sitting keeps the old start (no reset of the allowance)",
      r["state"]["sitting"]["start_left"] == 40.0 and r["seats"]["BENCH"] == 0, r["state"]["sitting"])
old = {"sitting": {"start": NOW - 9 * H, "start_left": 60.0, "last_active": NOW - 5 * H, "reset_at": "2026-10-28T13:00-07:00"}}
r = d(old, session_cap_pct=CAP, owner_window_t=NOW - 300, week_pct_left=40.0)
check("cap: >= 2 h idle starts a fresh sitting, the old drop is forgotten", r["seats"]["BENCH"] > 0
      and r["state"]["sitting"]["start_left"] == 40.0, (r["seats"], r["state"]["sitting"]))
r = d(old, session_cap_pct=CAP, owner_window_t=None, week_pct_left=10.0)
check("cap: a dead sitting (idle > 2 h, no new message) caps nothing", r["seats"]["BENCH"] > 0, r["seats"])
# F9: the stamp survives a burn-account switch / weekly reset (re-based, drop carried)
def sit2(**kw):
    s0 = sit()["sitting"]
    s0.update({"account": "acctA", "carried": 0.0, "last_left": 34.0}, **kw)
    return {"sitting": s0}
r = d(sit2(), session_cap_pct=CAP, owner_window_t=NOW - 600, account="acctB", week_pct_left=80.0, week_pct_used=20.0)
sg = r["state"]["sitting"]
check("F9: account switch re-bases: 6 spent on A carried, B counted from its own reading, cap reached on the carry",
      sg["account"] == "acctB" and sg["start_left"] == 80.0 and sg["carried"] == 6.0 and r["seats"]["BENCH"] == 0, (sg, r["seats"]))
r = d(sit2(carried=2.0, last_left=39.0), session_cap_pct=CAP, owner_window_t=NOW - 600, account="acctB", week_pct_left=80.0, week_pct_used=20.0)
check("F9: after a switch, a 1-point spend on B plus 3 carried is under the cap, not a meaningless 40-point difference",
      r["state"]["sitting"]["carried"] == 3.0 and r["seats"]["BENCH"] > 0 and "reached" not in r["why"], (r["state"]["sitting"], r["why"]))
r = d(sit2(account="acctB", start_left=80.0, carried=3.0, last_left=80.0), session_cap_pct=CAP, owner_window_t=NOW - 600,
      account="acctB", week_pct_left=76.0, week_pct_used=24.0)
check("F9: carried 3 + 4 spent on B = 7 >= cap refuses", r["seats"]["BENCH"] == 0, (r["state"]["sitting"], r["why"]))
r = d(dict(sit2(), bench_n=2), session_cap_pct=CAP, owner_window_t=NOW - 600, account="acctB", source="UNMEASURED",
      week_pct_left=None, week_pct_used=None)
check("F9: switch with no measured reading: UNMEASURED hold, stamp not re-based, never unlimited",
      "session cap UNMEASURED" in r["why"] and r["seats"]["BENCH"] <= 2 and r["state"]["sitting"]["account"] == "acctA",
      (r["why"], r["state"]["sitting"]))
r = d(sit2(), session_cap_pct=CAP, owner_window_t=NOW - 600, account="acctA", week_resets_at="2026-11-04T13:00-07:00",
      week_pct_left=100.0, week_pct_used=0.0)
sg = r["state"]["sitting"]
check("F9: weekly reset mid-sitting carries the drop (6) instead of starting a new sitting", sg["carried"] == 6.0
      and sg["start"] == NOW - 1 * H and r["seats"]["BENCH"] == 0, (sg, r["seats"]))
r = d({"sitting": dict(sit()["sitting"])}, session_cap_pct=CAP, owner_window_t=NOW - 600, account="acctB", week_pct_left=36.0)
check("F9: an old unstamped sitting adopts the account without a spurious carry",
      r["state"]["sitting"]["carried"] == 0.0 or r["state"]["sitting"].get("carried") in (None, 0.0), r["state"]["sitting"])
# review U F9: reset_at jitter on ONE account (account_usage series.jsonl, 2026-10-27: lukas 16:00 x70 / 15:59 x5,
# steven 15:00 / 15:00:00 / 14:59, system 13:00 / 12:59) is the same reset: no re-base, no lost drop
JIT = ["2026-10-28T16:00-07:00", "2026-10-28T15:59-07:00", "2026-10-28T16:00-07:00", "2026-10-28T15:59-07:00",
       "2026-10-28T16:00:00-07:00", "2026-10-28T15:59-07:00"]
st_, drop = {}, None
for i, (left, ra) in enumerate(zip([50.0, 48.0, 46.0, 44.0, 42.0, 40.0], JIT)):
    sg, live, drop, _ = SA.sitting_step({"owner_window_t": NOW - 3000 + i * 300, "source": "MEASURED",
                                         "week_pct_left": left, "week_resets_at": ra, "account": "lukas"},
                                        st_, NOW - 3000 + i * 300)
    st_ = {"sitting": sg}
check("F9 jitter: 50 -> 40 with reset_at flipping 16:00/15:59 is a drop of 10 (was 2 before the tolerance)",
      drop == 10.0 and st_["sitting"]["carried"] == 0.0 and st_["sitting"]["start_left"] == 50.0, (drop, st_))
check("F9 jitter: same_reset sees the real variants as one reset, a week apart as two",
      SA.same_reset("2026-10-28T15:00-07:00", "2026-10-28T14:59-07:00")
      and SA.same_reset("2026-10-28T15:00:00-07:00", "2026-10-28T15:00-07:00")
      and not SA.same_reset("2026-10-28T13:00-07:00", "2026-11-04T13:00-07:00")
      and not SA.same_reset(None, "2026-10-28T13:00-07:00"), "same_reset")
sg, _, drop, _ = SA.sitting_step({"owner_window_t": NOW - 60, "source": "MEASURED", "week_pct_left": 100.0,
                                  "week_resets_at": "2026-11-04T16:00-07:00", "account": "lukas"}, st_, NOW - 60)
check("F9 jitter: a real weekly reset still re-bases and carries the 10", sg["carried"] == 10.0 and drop == 10.0,
      (sg, drop))
legacy = {"sitting": {"start": NOW - H, "start_left": 50.0, "last_active": NOW - 600, "account": "acctA",
                      "reset_at": "2026-10-28T16:00-07:00", "carried": 0.0}}
sg, _, drop, _ = SA.sitting_step({"owner_window_t": NOW - 60, "source": "MEASURED", "week_pct_left": 70.0,
                                  "week_resets_at": "2026-10-28T16:00-07:00", "account": "acctB"}, legacy, NOW - 60)
check("F9 LOW: a legacy stamp with no last_left re-bases as a fresh base (carried stays a number, not held)",
      sg["carried"] == 0.0 and drop == 0.0 and sg["start_left"] == 70.0, (sg, drop))
r = d(dict(sit(), bench_n=2), session_cap_pct=CAP, owner_window_t=NOW - 600, source="UNMEASURED", week_pct_left=None,
      week_pct_used=None)
check("cap: unmeasured reading holds BENCH at the last count and says UNMEASURED",
      r["seats"]["BENCH"] <= 2 and "session cap UNMEASURED" in r["why"] and r["state"]["bench_n"] == 2, (r["seats"], r["why"]))
r = d(sit(), session_cap_pct=CAP, owner_window_t=NOW - 600, source="STALE", week_pct_left=10.0)
check("cap: a STALE reading is unmeasured too, never 'unlimited'", "session cap UNMEASURED" in r["why"], r["why"])
r = d(sit(), session_cap_pct=None, owner_window_t=NOW - 600, week_pct_left=10.0)
check("cap: no cap configured -> no cap line", "session cap" not in r["why"], r["why"])
r = d(sit(), session_cap_pct=CAP, owner_window_t=NOW - 600, week_pct_left=20.0, override=ov(n=4, seats=None, mode=None))
check("cap: his word stands over the cap", r["seats"]["BENCH"] == 4, r["seats"])
r = d(sit(), session_cap_pct=CAP, owner_window_t=NOW - 600, week_pct_left=33.0, week_pct_used=67.0)
check("cap: FOUNDRY is not touched by BENCH's sitting cap", r["seats"]["FOUNDRY"] >= 0 and r["seats"]["BENCH"] == 0)
check("cap: the configured value is read from dispatcher_schedule.json", SA.session_cap_pct() == 6.0, SA.session_cap_pct())

# ---- code-review night 2026-10-27 (slot_allocator full-file review)
# S1: a one-minute reset_at jitter is the same reset for the token dial too, not a reset that drops ALMOST_OUT
r = d(ao, week_pct_left=30.0, week_resets_at="2026-10-28T12:59-07:00")
check("S1: reset_at jitter (13:00 -> 12:59) keeps ALMOST_OUT's hysteresis (P 0.88 not held 2 h)",
      r["token_mode"] == "ALMOST_OUT", (r["token_mode"], r["state"]))
# S2: a sitting that began unmeasured on account A, then measured on B: A's spend is unknown, held - never zero
sg, _, drop, _ = SA.sitting_step({"owner_window_t": NOW - 600, "source": "UNMEASURED", "week_pct_left": None,
                                  "week_resets_at": "2026-10-28T16:00-07:00", "account": "acctA"}, {}, NOW - 600)
sg, _, drop, _ = SA.sitting_step({"owner_window_t": NOW - 60, "source": "MEASURED", "week_pct_left": 80.0,
                                  "week_resets_at": "2026-10-28T16:00-07:00", "account": "acctB"}, {"sitting": sg}, NOW - 60)
check("S2: unmeasured start on A then a reading on B holds the drop unknown (None), not 0",
      drop is None and sg.get("carried") is None, (drop, sg))
sg2, _, drop2, _ = SA.sitting_step({"owner_window_t": NOW - 30, "source": "MEASURED", "week_pct_left": 70.0,
                                    "week_resets_at": "2026-10-28T16:00-07:00", "account": "acctB"}, {"sitting": sg}, NOW - 30)
check("S2: ... and stays held on the next reading", drop2 is None, (drop2, sg2))
sg3, _, drop3, _ = SA.sitting_step({"owner_window_t": NOW - 60, "source": "MEASURED", "week_pct_left": 80.0,
                                    "week_resets_at": "2026-10-28T16:00-07:00", "account": "acctA"},
                                   {"sitting": {"start": NOW - 600, "start_left": None, "last_active": NOW - 600,
                                                "account": "acctA", "reset_at": "2026-10-28T16:00-07:00",
                                                "carried": 0.0, "last_left": None}}, NOW - 60)
check("S2 control: unmeasured start then a reading on the SAME account takes it as the base (drop 0)",
      drop3 == 0.0 and sg3["start_left"] == 80.0, (drop3, sg3))
# S3: two writers (the scheduled tick and a manual `now --write`) must not share one temp file
_sd_old = os.environ.get("RM_STREAMS_DIR")
with tempfile.TemporaryDirectory() as _td:
    os.environ["RM_STREAMS_DIR"] = _td
    _real_replace, _nested = SA.os.replace, []

    def _racing_replace(src, dst):
        if not _nested:  # a second writer lands between this writer's temp write and its replace
            _nested.append(1)
            SA.write_atomic(Path(_td) / "allocation.json", json.dumps({"who": "second"}))
        return _real_replace(src, dst)
    SA.os.replace = _racing_replace
    err = None
    try:
        SA.write_atomic(Path(_td) / "allocation.json", json.dumps({"who": "first"}))
    except Exception as e:  # noqa: BLE001
        err = e
    finally:
        SA.os.replace = _real_replace
    got = json.loads((Path(_td) / "allocation.json").read_text(encoding="utf-8"))
    left_over = sorted(p.name for p in Path(_td).iterdir() if p.name != "allocation.json")
    check("S3: an interleaved second writer neither crashes the first nor publishes in its name",
          err is None and got == {"who": "first"} and not left_over, (err, got, left_over))
    # O1: `set` publishes his override by replace, never truncate-then-write (a collector reading mid-write saw
    # no override and published an allocation without his word)
    _replaced = []

    def _rec_replace(src, dst):
        _replaced.append(Path(dst).name)
        return _real_replace(src, dst)
    SA.os.replace = _rec_replace
    try:
        rc = SA.main(["set", "--n", "0", "--seat", "BENCH", "--owner-said", "bench off", "--hours", "2"])
    finally:
        SA.os.replace = _real_replace
    ov_now = json.loads((Path(_td) / "slot_override.json").read_text(encoding="utf-8"))
    left_over = sorted(p.name for p in Path(_td).iterdir() if p.name not in ("allocation.json", "slot_override.json"))
    check("O1: set writes slot_override.json by atomic replace, leaving no temp file",
          rc == 0 and "slot_override.json" in _replaced and ov_now["seats"] == {"BENCH": 0} and not left_over,
          (rc, _replaced, ov_now, left_over))
if _sd_old is None:
    os.environ.pop("RM_STREAMS_DIR", None)
else:
    os.environ["RM_STREAMS_DIR"] = _sd_old
# P1: a plan against a STALE/UNMEASURED reading is refused, never approved from an unusable number
for _src in ("STALE", "UNMEASURED"):
    ok, why = SA.check_plan(dict(stv(80.0, 150.0), source=_src), 10.0, R2, NOW)
    check(f"P1: check_plan refuses a {_src} reading of a lent account", not ok and "unmeasured" in why, why)
ok, why = SA.check_plan(stv(80.0, 150.0), 10.0, R2, NOW)
check("P1 control: the same ESTIMATE reading is allowed", ok, why)
_mn, _lr = SA.meter_now, SA.load_rules
SA.meter_now = lambda now: {"accounts": {"steven": {"week_pct_left": 80.0, "week_pct_used": 20.0,
                                                    "hours_to_week_reset": 150.0, "source": "STALE",
                                                    "week_resets_at": SA.iso_local(NOW + 150 * H)}}}
SA.load_rules = lambda: R2
try:
    rc = SA.main(["plan", "--account", "steven", "--draw", "10"])
finally:
    SA.meter_now, SA.load_rules = _mn, _lr
check("P1: the plan CLI passes the reading's source on (a STALE meter is refused, rc 2)", rc == 2, rc)

# S4: an override naming only FOUNDRY leaves BENCH's sitting cap in force
r = d(sit(), session_cap_pct=CAP, owner_window_t=NOW - 0.5 * H, week_pct_left=33.0, week_pct_used=67.0,
      override=ov(n=2, seats={"FOUNDRY": 2}, mode=None))
check("S4: a FOUNDRY-only override keeps BENCH's session cap (BENCH 0, FOUNDRY 2)",
      r["seats"]["BENCH"] == 0 and r["seats"]["FOUNDRY"] == 2 and "session cap reached" in r["why"], (r["seats"], r["why"]))
r = d(sit(), session_cap_pct=CAP, owner_window_t=NOW - 0.5 * H, week_pct_left=33.0, week_pct_used=67.0,
      override=ov(n=3, seats={"bench": 3}, mode=None))
check("S4 control: an override naming BENCH stands over the cap", r["seats"]["BENCH"] == 3, r["seats"])
# S5: a blind (STALE) reading carrying the next week's reset_at must not consume the reset unapplied
r = d(ao, source="STALE", week_pct_left=100.0, week_pct_used=0.0, hours_to_week_reset=167.0,
      week_resets_at="2026-11-04T13:00-07:00")
check("S5: a STALE reading holds the mode and keeps the old reset_at in state",
      r["token_mode"] == "ALMOST_OUT" and SA.epoch(r["state"]["reset_at"]) == SA.epoch("2026-10-28T13:00-07:00"),
      (r["token_mode"], r["state"].get("reset_at")))
r = d(r["state"], week_pct_left=100.0, week_pct_used=0.0, hours_to_week_reset=167.0,
      week_resets_at="2026-11-04T13:00-07:00")
check("S5: ... so the first MEASURED reading of the new week still ends ALMOST_OUT at once",
      r["token_mode"] == "CRUISE", r["token_mode"])
# S6: account_usage marks an old poll with stale=True and keeps source MEASURED: the plan and the spare list see STALE
SA.meter_now = lambda now: {"accounts": {"steven": {"week_pct_left": 80.0, "week_pct_used": 20.0,
                                                    "hours_to_week_reset": 150.0, "source": "MEASURED", "stale": True,
                                                    "week_resets_at": SA.iso_local(NOW + 150 * H)}}}
SA.load_rules = lambda: R2
try:
    rc = SA.main(["plan", "--account", "steven", "--draw", "10"])
    g = SA.gather(NOW, R2)
finally:
    SA.meter_now, SA.load_rules = _mn, _lr
check("S6: plan refuses a MEASURED reading flagged stale (rc 2)", rc == 2, rc)
check("S6: gather lists no spare from a stale reading", not [x for x in g["spare"] if x["account"] == "steven"],
      g["spare"])
# S7: an older decision never overwrites a newer one in allocation.json (scheduled tick vs manual `now --write`)
with tempfile.TemporaryDirectory() as _td:
    os.environ["RM_STREAMS_DIR"] = _td
    try:
        SA.write({"t": NOW + 10, "who": "newer"})
        wrote = SA.write({"t": NOW, "who": "older"})
        got = json.loads((Path(_td) / "allocation.json").read_text(encoding="utf-8"))
        check("S7: a decision computed before the published one is not written over it",
              got["who"] == "newer" and wrote is False, (got, wrote))
        wrote = SA.write({"t": NOW + 20, "who": "newest"})
        got = json.loads((Path(_td) / "allocation.json").read_text(encoding="utf-8"))
        check("S7 control: a newer decision replaces it", got["who"] == "newest" and wrote is not False, (got, wrote))
    finally:
        if _sd_old is None:
            os.environ.pop("RM_STREAMS_DIR", None)
        else:
            os.environ["RM_STREAMS_DIR"] = _sd_old

# S8: two of his messages between checks: 1 h 59 min then 2 h 01 min after the stamp's last_active. The newest alone
# looks like a 2 h idle gap (a fresh sitting, spend forgotten); the one before it shows he never left.
T0 = NOW - 3 * H
st8 = {"sitting": {"start": T0 - H, "start_left": 40.0, "last_active": T0, "account": "acctA",
                   "reset_at": "2026-10-28T16:00-07:00", "carried": 0.0, "last_left": 35.0}}
i8 = {"source": "MEASURED", "week_pct_left": 33.0, "week_resets_at": "2026-10-28T16:00-07:00", "account": "acctA",
      "owner_window_t": T0 + 2.0 * H + 60, "owner_window_ts": [T0 + 2.0 * H - 60, T0 + 2.0 * H + 60]}
sg, _, drop, _ = SA.sitting_step(i8, st8, T0 + 2.0 * H + 120)
check("S8: a message inside the idle gap keeps the sitting (drop 7, start unchanged)",
      drop == 7.0 and sg["start"] == T0 - H and sg["last_active"] == T0 + 2.0 * H + 60, (drop, sg))
sg, _, drop, _ = SA.sitting_step(dict(i8, owner_window_ts=[T0 + 2.0 * H + 60]), st8, T0 + 2.0 * H + 120)
check("S8 control: a real 2 h gap still starts a new sitting", sg["start"] == T0 + 2.0 * H + 60 and drop == 0.0, (drop, sg))

# S9: the token dial's hysteresis belongs to one burn account: a switch starts the new account's dial fresh
r = d(dict(ao, account="acctA"), account="acctB", week_pct_left=30.0)
check("S9: ALMOST_OUT on acctA does not hold acctB (P 0.88) at one helper", r["token_mode"] == "CRUISE"
      and r["state"].get("account") == "acctB", (r["token_mode"], r["state"].get("account")))
r = d(dict(ao, account="acctA"), account="acctA", week_pct_left=30.0)
check("S9 control: the same account keeps ALMOST_OUT's hold", r["token_mode"] == "ALMOST_OUT", r["token_mode"])
# S10: a writer computes AND publishes under the one lock, so two writers cannot both build on the same old state
import fcntl  # noqa: E402
with tempfile.TemporaryDirectory() as _td:
    os.environ["RM_STREAMS_DIR"] = _td
    _cmp, seen = SA.compute, []

    def _probe_compute(*a, **k):
        with open(Path(_td) / "allocation.json.lock", "a") as lk:
            try:
                fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(lk, fcntl.LOCK_UN)
                seen.append("unlocked")
            except BlockingIOError:
                seen.append("locked")
        return {"t": NOW + len(seen), "at": "x", "mode": "CRUISE", "n": 1, "seats": {"BENCH": 1}, "why": "w",
                "n_total": 1, "token_mode": "CRUISE", "queue_mode": "CLEAR", "presence": "-", "inputs": {}}
    SA.compute = _probe_compute
    try:
        err = None
        try:
            SA.publish(NOW)
            SA.main(["now", "--write", "--json"])
        except Exception as e:  # noqa: BLE001
            err = e
    finally:
        SA.compute = _cmp
        if _sd_old is None:
            os.environ.pop("RM_STREAMS_DIR", None)
        else:
            os.environ["RM_STREAMS_DIR"] = _sd_old
    check("S10: publish() and `now --write` compute while holding the allocation lock", err is None
          and seen == ["locked", "locked"], (err, seen))

print(f"\n{'GREEN' if not FAILS else 'RED'}: {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
