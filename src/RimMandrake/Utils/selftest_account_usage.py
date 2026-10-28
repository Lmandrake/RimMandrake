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
os.environ["RM_CLAUDE_ACCOUNT"] = str(ROOT / "no-such-claude-account")  # a test never reaches the real switcher
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
class FakeSwitcher:
    """claude-account loaded as a module: its MachineLock, live_account, where, warm_one, health file. live_account
    and warm_one assert they run under the lock; `switch_on_lock` lands a switch the instant the lock is taken (the
    race: a switch between poll's checks and the warm). warm_one renews 'four' only when `renew`."""

    class Refused(Exception):
        pass

    def __init__(self):
        self.HEALTH = str(ROOT / "health.json")
        self.live, self.renew, self.busy, self.switch_on_lock = ("one", "a@x.test"), False, False, None
        self.locked, self.warmed, self.events = False, [], []

    def MachineLock(self, wait=True):
        sw = self

        class _L:
            def __enter__(self):
                if sw.busy:
                    raise sw.Refused("another claude-account operation is running on this machine")
                if sw.switch_on_lock:
                    sw.live = sw.switch_on_lock
                sw.locked = True
                return self

            def __exit__(self, *a):
                sw.locked = False
        return _L()

    def live_account(self):
        assert self.locked, "live_account read outside the switcher lock"
        return self.live

    def where(self, a):
        assert self.locked, "where read outside the switcher lock"
        return "live" if a == self.live[0] else "vault" if (acc / a / ".credentials.json").exists() else None

    def read_json(self, p, d=None):
        try:
            return json.loads(Path(p).read_text())
        except (OSError, ValueError):
            return d

    def write_json_atomic(self, p, d, mode=0o600):
        assert self.locked
        Path(p).write_text(json.dumps(d))

    def warm_one(self, a, health):
        assert self.locked, "warm_one outside the switcher lock"
        self.warmed.append((a, self.live[0]))
        if self.renew:
            (acc / a / ".credentials.json").write_text(json.dumps({"claudeAiOauth": {"expiresAt": (NOW + 8 * 3600) * 1000}}))
        health.setdefault(a, {})["warm"] = {"result": "renewed" if self.renew else "failed-auth"}
        return health[a]["warm"]

    def log_event(self, **kw):
        self.events.append(kw)


SW = FakeSwitcher()
au.switcher_module = lambda: SW
au.clock = lambda: 0.0  # reservation time = the poll's own (fixture) time
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
check("warm: an expired dormant login is warmed once, under the switcher's lock", SW.warmed == [("four", "one")], SW.warmed)
check("warm: a failed warm is in the why", "warm" in recs["four"]["why"] and "failed" in recs["four"]["why"], recs["four"])
check("warm: the live login and a remote's live login are never warmed",
      not any(a in ("one", "two") for a, _ in SW.warmed), SW.warmed)

# ---- RimPulse reading: fresh = MEASURED, old = carry basis
pulse = ROOT / "pulse"
pulse.mkdir(exist_ok=True)
pulse_doc = {"accounts": {"four": {"measured_at": NOW - 300, "week": {"pct": 69.0, "resets_at": NOW + 50 * 3600},
                                   "five": {"pct": 1.0, "resets_at": NOW + 3600}}}}
(pulse / "usage.json").write_text(json.dumps(pulse_doc))
recs = au.poll(NOW + 60)
check("pulse: a fresh endpoint reading is MEASURED with its own time", recs["four"]["source"] == "MEASURED"
      and recs["four"]["measured_at"] == au.iso(NOW - 300) and recs["four"]["week_pct_used"] == 69.0, recs["four"])

check("warm: at most one warm per account per hour (none 1 min later)", SW.warmed == [("four", "one")], SW.warmed)

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

# ---- warm that renews: the dormant login is then read
au.probe_local = fake_local
au.probe_remote = lambda t, e, n: (dict(FIG), "")
(acc / "four" / ".credentials.json").write_text(json.dumps({"claudeAiOauth": {"expiresAt": (NOW + 60) * 1000}}))
(ROOT / "data" / "warm_state.json").unlink()
SW.renew = True
calls.clear()
SW.warmed.clear()
recs = au.poll(NOW + 120)
check("warm: a renewed login is probed and MEASURED", recs["four"]["source"] == "MEASURED"
      and ("local", str(acc / "four"), "d@x.test") in calls, (recs["four"], calls))


def rearm():
    (acc / "four" / ".credentials.json").write_text(json.dumps({"claudeAiOauth": {"expiresAt": (NOW + 60) * 1000}}))
    (ROOT / "data" / "warm_state.json").unlink(missing_ok=True)
    SW.warmed.clear()
    calls.clear()


# THE RACE (lesson 2026-10-28): a switch to 'four' lands after poll's checks, before the warm. Under the lock the
# switcher's own live_account says four is live: the warm must not run (it would refresh the LIVE login).
rearm()
SW.switch_on_lock = ("four", "d@x.test")
recs = au.poll(NOW + 180)
check("race: a switch landing before the warm is seen under the switcher's lock; nothing warmed",
      SW.warmed == [] and "dormant" not in recs["four"]["method"], (SW.warmed, recs["four"]))
check("race: the refusal is in the why", "not warmed" in recs["four"]["why"], recs["four"]["why"])
SW.switch_on_lock, SW.live = None, ("one", "a@x.test")
# the live login's email is the target's even though the registry name lookup failed: still refused
rearm()
SW.live = (None, "d@x.test")
au.poll(NOW + 200)
check("race: a live login with the target's email (unregistered name) is never warmed", SW.warmed == [], SW.warmed)
# no live login known under the lock: where each login is live is not proven, so no warm
rearm()
SW.live = (None, None)
au.poll(NOW + 210)
check("race: an unknown live login under the lock refuses the warm", SW.warmed == [], SW.warmed)
SW.live = ("one", "a@x.test")
# the switcher is busy (a switch in progress): no warm, and the poll still finishes
rearm()
SW.busy = True
recs = au.poll(NOW + 220)
check("lock: a busy switcher lock skips the warm and the poll completes", SW.warmed == [] and "four" in recs, SW.warmed)
SW.busy = False
# the switcher cannot be loaded: no warm, no crash
rearm()
au.switcher_module = lambda: (_ for _ in ()).throw(ImportError("gone"))
recs = au.poll(NOW + 230)
check("lock: an unloadable switcher means no warm", SW.warmed == [] and "not warmed" in recs["four"]["why"], recs["four"])
au.switcher_module = lambda: SW
# a remote that does not answer: we cannot know where each login is live, so no warm
rearm()
au.remote_live = lambda t: (None, None)
au.poll(NOW + 240)
check("warm: refused while a remote's live login is unknown", SW.warmed == [], SW.warmed)

# ---- the real switcher still offers what the locked warm uses (loaded, never called)
real = Path.home() / ".local" / "bin" / "claude-account"
if real.exists():
    mod = au.load_switcher(str(real))
    need = ("MachineLock", "live_account", "where", "warm_one", "read_json", "write_json_atomic", "HEALTH", "log_event")
    check("switcher API: the real claude-account has every name the locked warm uses",
          all(hasattr(mod, k) for k in need), [k for k in need if not hasattr(mod, k)])
else:
    print("SKIP switcher API: no claude-account on this machine")

# ---- no secret, host or account literal in the module
src = Path(au.__file__).read_text()
check("hygiene: the switcher is never run as a subprocess (its lock cannot be held across one)", "[CLAUDE_ACCOUNT" not in src)
check("hygiene: no email, host or token literal", "@gmail" not in src and "100.115" not in src
      and "accessToken" not in src and "refreshToken" not in src)

print(f"\n{len(FAILS)} failure(s)" if FAILS else "\nall passed")
sys.exit(1 if FAILS else 0)
