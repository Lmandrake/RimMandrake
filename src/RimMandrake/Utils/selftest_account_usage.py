#!/usr/bin/env python3
"""Selftest for account_usage.py: /usage parsing (year-less and date-less resets), the identity check that
refuses a reading from the wrong login, the source order (live > remote > vault-with-valid-token >
RimPulse > ESTIMATE > UNMEASURED), that a vault login whose token needs a refresh is never run, and the
file contract readers consume. Fixture accounts and fake probes; no network, no claude, no credentials."""
import atexit
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(tempfile.mkdtemp(prefix="st_acct_usage_"))
atexit.register(shutil.rmtree, ROOT, True)
os.environ["RM_ACCOUNTS_DIR"] = str(ROOT / "acc")
os.environ["RM_ACCOUNT_USAGE_DIR"] = str(ROOT / "data")
os.environ["RM_ACCOUNT_USAGE_CONF"] = str(ROOT / "conf.json")
os.environ["RM_LIVE_CLAUDE_JSON"] = str(ROOT / "live.claude.json")
os.environ["RM_PULSE_STATE"] = str(ROOT / "pulse")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import account_usage as au  # noqa: E402

FAILS = []
# 2026-10-26 12:42 PDT (19:42Z)
NOW = 1793043764.0


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)


TEXT = ("You are currently using your subscription to power your Claude Code usage\n\n"
        "Current session: 16% used · resets Oct 26, 4:10pm (America/Los_Angeles)\n"
        "Current week (all models): 59% used · resets Oct 28, 1pm (America/Los_Angeles)\n"
        "Current week (Fable): 0% used · resets Oct 28, 1pm (America/Los_Angeles)\n\n"
        "What's contributing to your limits usage?\n")

# ---- parsing
f = au.parse_usage(TEXT, NOW)
check("parse: session pct", f and f["session_pct_used"] == 16.0, f)
check("parse: session reset with zone", f and f["session_resets_at"] == "2026-10-26T16:10-07:00", f)
check("parse: week pct + reset", f and f["week_pct_used"] == 59.0 and f["week_resets_at"] == "2026-10-28T13:00-07:00", f)
check("parse: other model week kept apart", f and f["other_weeks"] == {"Fable": {"pct_used": 0.0,
      "resets_at": "2026-10-28T13:00-07:00"}}, f)
check("parse: year rolls over at new year", au.parse_reset("resets Jan 2, 1am (UTC)", 1798675200.0)  # 2026-12-31Z
      == "2027-01-02T01:00+00:00")
check("parse: a time-only reset is today or tomorrow",
      au.parse_reset("resets 3:30pm (America/Los_Angeles)", NOW) == "2026-10-26T15:30-07:00")
check("parse: no weekly line is no reading", au.parse_usage("Current session: 5% used\n", NOW) is None)
check("parse: unused session (no reset) still reads", (au.parse_usage(
    "Current session: 0% used\nCurrent week (all models): 93% used · resets Oct 28, 4pm (America/Los_Angeles)", NOW)
    or {}).get("session_resets_at") is None)

# ---- identity check
ok_auth = json.dumps({"loggedIn": True, "email": "A@x.test"})
use = json.dumps({"is_error": False, "result": TEXT})
check("identity: right login reads", au._reading(ok_auth, use, "a@x.test", NOW)[0] is not None)
check("identity: wrong login refused", au._reading(ok_auth, use, "b@x.test", NOW) == (None, "a different login answered"))
check("identity: API-key run refused", au._reading(ok_auth, json.dumps({"result": "Current week (all models): 1% used"}),
                                                     "a@x.test", NOW)[0] is None)

# ---- poll source order
acc = ROOT / "acc"
for n in ("one", "two", "three", "four"):
    (acc / n).mkdir(parents=True, exist_ok=True)
(acc / "accounts.tsv").write_text("# reg\none a@x.test\ntwo b@x.test\nthree c@x.test\nfour d@x.test\n")
(acc / "machine.json").write_text(json.dumps({"machine": "here"}))
Path(os.environ["RM_LIVE_CLAUDE_JSON"]).write_text(json.dumps({"oauthAccount": {"emailAddress": "a@x.test"}}))
Path(os.environ["RM_ACCOUNT_USAGE_CONF"]).write_text(json.dumps({"remotes": ["r1"]}))
# one: live here; two: live on r1; three: vault, valid token; four: vault, token needing a refresh
(acc / "one" / ".credentials.json").write_text(json.dumps({"claudeAiOauth": {"expiresAt": (NOW + 7200) * 1000}}))
(acc / "three" / ".credentials.json").write_text(json.dumps({"claudeAiOauth": {"expiresAt": (NOW + 7200) * 1000}}))
(acc / "four" / ".credentials.json").write_text(json.dumps({"claudeAiOauth": {"expiresAt": (NOW + 60) * 1000}}))
calls = []
FIG = au.parse_usage(TEXT, NOW)


def fake_local(config_dir, email, now):
    calls.append(("local", config_dir, email))
    return dict(FIG), ""


au.probe_local = fake_local
au.remote_live = lambda t: ("there", "two")
au.probe_remote = lambda t, e, n: (calls.append(("remote", t, e)) or (dict(FIG), ""))
recs = au.poll(NOW)
check("poll: live here measured with the default config", recs["one"]["source"] == "MEASURED"
      and ("local", None, "a@x.test") in calls, calls)
check("poll: live account's vault copy never run", ("local", str(acc / "one"), "a@x.test") not in calls, calls)
check("poll: remote live measured, labelled with its machine", recs["two"]["source"] == "MEASURED"
      and recs["two"]["machine"] == "there")
check("poll: valid vault token measured", recs["three"]["source"] == "MEASURED"
      and ("local", str(acc / "three"), "c@x.test") in calls)
check("poll: vault token needing a refresh is never run", not any(c[1] == str(acc / "four") for c in calls), calls)
check("poll: nothing to carry reads UNMEASURED with null figures", recs["four"]["source"] == "UNMEASURED"
      and recs["four"]["week_pct_used"] is None and "refresh" in recs["four"]["why"], recs["four"])
check("poll: every record has the contract keys", all(set(au.RECORD_KEYS) == set(r) for r in recs.values()))

# ---- RimPulse reading: fresh = MEASURED, old = carry basis
pulse = ROOT / "pulse"
pulse.mkdir(exist_ok=True)
pulse_doc = {"accounts": {"four": {"measured_at": NOW - 300, "week": {"pct": 69.0, "resets_at": NOW + 50 * 3600},
                                   "five": {"pct": 1.0, "resets_at": NOW + 3600}}}}
(pulse / "usage.json").write_text(json.dumps(pulse_doc))
recs = au.poll(NOW + 60)
check("pulse: a fresh endpoint reading is MEASURED with its own time", recs["four"]["source"] == "MEASURED"
      and recs["four"]["measured_at"] == au.iso(NOW - 300) and recs["four"]["week_pct_used"] == 69.0, recs["four"])

# ---- carry: everything fails 4 h later (past the 16:10 session reset)
au.probe_local = lambda *a: (None, "boom")
au.probe_remote = lambda *a: (None, "boom")
recs = au.poll(NOW + 4 * 3600)
r = recs["three"]
check("carry: ESTIMATE, never MEASURED", r["source"] == "ESTIMATE" and "lower bound" in r["method"], r)
check("carry: week figure carried, basis kept", r["week_pct_used"] == 59.0 and r["measured_at"] == au.iso(NOW + 60), r)
check("carry: a reset session window is dropped", r["session_pct_used"] is None, r)
r2 = au.poll(NOW + 5 * 3600)["three"]
check("carry: an estimate of an estimate keeps the original basis", r2["measured_at"] == au.iso(NOW + 60), r2)
r3 = au.poll(NOW + 3 * 86400)["three"]
check("carry: after the week resets it is UNMEASURED, not the old percent", r3["source"] == "UNMEASURED", r3)

# ---- file contract + reader
lines = (ROOT / "data" / "series.jsonl").read_text().splitlines()
check("series: one line per account per poll", len(lines) == 4 * 5, len(lines))
check("series: every line parses with schema 1", all(json.loads(x)["schema"] == 1 for x in lines))
au.write({"one": au.record("one", NOW, "MEASURED", "m", "here", FIG, au.iso(NOW))}, NOW)
st = au.read_now(NOW + 3600)
d = st["accounts"]["one"]
check("reader: pct_left and hours to reset", d["week_pct_left"] == 41.0 and abs(d["hours_to_week_reset"] - 47.3) < 0.1, d)
check("reader: age 60 min, and a 60-min-old poll is stale", d["age_min"] == 60.0 and d["stale"] is True, d)
st = au.read_now(NOW + 4 * 3600)
d = st["accounts"]["one"]
check("reader: a passed session reset reads unknown, not the old percent",
      d["session_pct_left"] is None and d["hours_to_session_reset"] is None, d)
check("reader: --json CLI round-trips", au.main(["now", "--json"]) == 0)

# ---- no secret, host or account literal in the module
src = Path(au.__file__).read_text()
check("hygiene: no email, host or token literal", "@gmail" not in src and "100.115" not in src
      and "accessToken" not in src and "refreshToken" not in src)

print(f"\n{len(FAILS)} failure(s)" if FAILS else "\nall passed")
sys.exit(1 if FAILS else 0)
