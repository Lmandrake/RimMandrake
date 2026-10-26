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
check("next week, start of week (80% left): up to 30% more is allowed (50% used cap)", cp(80, 150, 30) and not cp(80, 150, 31))
check("mid-week at 55% left: only 5% more (45% already used)", cp(55, 60, 5) and not cp(55, 60, 10))
check("mid-week at 31% left (69% used): nothing", not cp(31, 60, 1))
check("near his reset (10 h): down to the 10% floor, never below", cp(31, 10, 21) and not cp(31, 10, 22))
check("near his reset at 8% left: nothing", not cp(8, 10, 1))
bad = []
for left in range(0, 101, 3):
    for h in (1, 10, 23, 24, 25, 60, 120, 167):
        for draw in range(1, 101, 2):
            if cp(left, h, draw) and (left - draw < 10 or (h > 24 and (100 - left) + draw > 50)):
                bad.append((left, h, draw))
check("no accepted plan takes steven under 10% or over 50% used outside the end window (sweep)", not bad, bad[:5])
r = SA.decide(inp(spare=[stv(80.0, 150.0)]), {}, R2, NOW)
check("a lent account is recommended only when the rule allows, naming the share", "steven may lend 30%" in r["why"]
      and "preferred" in r["why"] and "never automatic" in r["why"], r["why"])
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
env = dict(os.environ, RM_ACCOUNT_USAGE_DIR=str(au), RM_STREAMS_DIR=str(streams), RM_SLOT_PROJECTS=str(tmp / "projects"),
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

print(f"\n{'GREEN' if not FAILS else 'RED'}: {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
