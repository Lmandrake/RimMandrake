#!/usr/bin/env python3
"""Selftest for RIMMANDRAKE_HARDEN_ACCOUNT_USAGE_POLL_RACES_CODEX_FLAGGED: three Codex claims on account_usage.poll().

(a) an account_usage.json that exists but cannot be read or parsed is "could not look", never "no remotes": poll()
    names the failure and runs no warm (a warm then could refresh a login a remote holds live);
(b) a switch that lands here between poll's first live read and the vault probe is seen UNDER the switcher's lock:
    the now-live login is never probed through its vault dir;
(c) a switch between `claude auth status` and `/usage` (here or on a remote) is caught: the identity is read again
    after /usage and a change refuses the reading. Two switches inside one /usage call (A to B and back) are the
    documented race left open (see account_usage._same_login); this test does not claim them.
Fixture accounts and fake probes; no network, no claude, no credentials.

    python3 src/RimMandrake/Utils/selftest_account_usage_poll_races.py      exit 0 = pass
"""
import atexit
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(tempfile.mkdtemp(prefix="st_acct_usage_races_"))
atexit.register(shutil.rmtree, ROOT, True)
os.environ["RM_ACCOUNTS_DIR"] = str(ROOT / "acc")
os.environ["RM_ACCOUNT_USAGE_DIR"] = str(ROOT / "data")
os.environ["RM_ACCOUNT_USAGE_CONF"] = str(ROOT / "conf.json")
os.environ["RM_LIVE_CLAUDE_JSON"] = str(ROOT / "live.claude.json")
os.environ["RM_PULSE_STATE"] = str(ROOT / "pulse")
os.environ["RM_CLAUDE_ACCOUNT"] = str(ROOT / "no-such-claude-account")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import account_usage as au  # noqa: E402

FAILS = []
NOW = 1793043764.0  # 2026-10-26 12:42 PDT
TEXT = ("You are currently using your subscription to power your Claude Code usage\n\n"
        "Current week (all models): 59% used · resets Oct 28, 1pm (America/Los_Angeles)\n")
FIG = au.parse_usage(TEXT, NOW)


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)


acc = ROOT / "acc"
for n in ("one", "three", "four"):
    (acc / n).mkdir(parents=True, exist_ok=True)
(acc / "accounts.tsv").write_text("one a@x.test\nthree c@x.test\nfour d@x.test\n")
(acc / "machine.json").write_text(json.dumps({"machine": "here"}))
LIVE = Path(os.environ["RM_LIVE_CLAUDE_JSON"])
CONF = Path(os.environ["RM_ACCOUNT_USAGE_CONF"])


def live(email):
    LIVE.write_text(json.dumps({"oauthAccount": {"emailAddress": email}}))


def creds(name, secs, at):
    (acc / name / ".credentials.json").write_text(json.dumps({"claudeAiOauth": {"expiresAt": (at + secs) * 1000}}))


class Switcher:
    """Just enough of claude-account for warm(): records every warm it is asked for."""
    HEALTH = str(ROOT / "health.json")

    def __init__(self):
        self.warmed = []

    def MachineLock(self, wait=True):
        class _L:
            def __enter__(s):
                return s

            def __exit__(s, *a):
                pass
        return _L()

    def live_account(self):
        return "one", "a@x.test"

    def where(self, a):
        return "vault"

    def read_json(self, p, d=None):
        return d

    def write_json_atomic(self, p, d, mode=0o600):
        pass

    def warm_one(self, a, health):
        self.warmed.append(a)
        return {"result": "failed-auth"}

    def log_event(self, **kw):
        pass


SW = Switcher()
au.switcher_module = lambda: SW
au.clock = lambda: 0.0
au.remote_live = lambda t: ("there", "zz")  # a remote answers, on a login not in the registry
real_probe_remote = au.probe_remote
au.probe_remote = lambda t, e, n: (None, "not probed")
calls = []
real_probe_local = au.probe_local


def fake_local(config_dir, email, now):
    calls.append((config_dir, email))
    return dict(FIG), ""


def reset(at):
    live("a@x.test")
    creds("one", 7200, at)
    creds("three", 7200, at)
    creds("four", 60, at)  # needs a refresh: the only account a poll may warm
    (ROOT / "data" / "warm_state.json").unlink(missing_ok=True)
    SW.warmed.clear()
    calls.clear()
    au.probe_local = fake_local


# ---- (a) an unreadable config is "could not look", not "no remotes"
reset(NOW)
CONF.write_text("{this is not json")
recs = au.poll(NOW)
check("config(a): an unparseable account_usage.json runs no warm", SW.warmed == [], SW.warmed)
check("config(a): the why names the config failure", str(CONF) in recs["four"]["why"]
      and "unreadable" in recs["four"]["why"] and "remotes are unknown" in recs["four"]["why"], recs["four"]["why"])
reset(NOW + 4000)
CONF.write_text(json.dumps({"remotes": "r1"}))
recs = au.poll(NOW + 4000)
check("config(a): a remotes value that is not a list of hosts runs no warm", SW.warmed == [], SW.warmed)
reset(NOW + 8000)
CONF.write_text(json.dumps(["r1"]))
recs = au.poll(NOW + 8000)
check("config(a): a config that is not an object runs no warm", SW.warmed == [], SW.warmed)
reset(NOW + 10000)
CONF.write_text(json.dumps({"remotes": None}))
au.poll(NOW + 10000)
check("config(a): an explicit null remotes runs no warm", SW.warmed == [], SW.warmed)
# positive controls: a well-formed config, and no config file at all (a machine with no remotes), still warm
reset(NOW + 12000)
CONF.write_text(json.dumps({"remotes": ["r1"]}))
au.poll(NOW + 12000)
check("config(a) control: a readable config with an answering remote still warms", SW.warmed == ["four"], SW.warmed)
reset(NOW + 16000)
CONF.unlink()
au.poll(NOW + 16000)
check("config(a) control: no config file (no remotes declared) still warms", SW.warmed == ["four"], SW.warmed)

# ---- (b) a switch to a dormant login lands after poll's first live read, while it waits for the switcher's lock
reset(NOW + 20000)
CONF.write_text(json.dumps({"remotes": []}))


class SwitchOnLock(au.Lock):
    def __enter__(self):
        got = super().__enter__()
        live("c@x.test")  # 'three' is now live here; its vault dir is the live login's twin
        return got


real_lock, au.Lock = au.Lock, SwitchOnLock
recs = au.poll(NOW + 20000)
au.Lock = real_lock
check("switch(b): the login that became live under the lock is never vault-probed",
      (str(acc / "three"), "c@x.test") not in calls, calls)
check("switch(b): the why says it is live here now", "live" in recs["three"]["why"], recs["three"]["why"])
reset(NOW + 24000)
recs = au.poll(NOW + 24000)
check("switch(b) control: with no switch the valid vault login is probed",
      (str(acc / "three"), "c@x.test") in calls, calls)


class BlindOnLock(au.Lock):
    def __enter__(self):
        got = super().__enter__()
        LIVE.write_text("{torn")  # the live login file cannot be read under the lock
        return got


reset(NOW + 28000)
au.Lock = BlindOnLock
recs = au.poll(NOW + 28000)
au.Lock = real_lock
check("switch(b): an unreadable live login under the lock means no vault probe",
      (str(acc / "three"), "c@x.test") not in calls and "unreadable" in recs["three"]["why"], (calls, recs["three"]["why"]))


class SlowLock(au.Lock):
    def __enter__(self):
        got = super().__enter__()
        creds("three", 60, NOW + 32000)  # the lock wait and remote probes ate the margin: the token is near expiry
        return got


reset(NOW + 32000)
au.Lock = SlowLock
recs = au.poll(NOW + 32000)
au.Lock = real_lock
check("switch(b): a vault token that came inside the margin while waiting is not probed",
      (str(acc / "three"), "c@x.test") not in calls and "margin" in recs["three"]["why"], (calls, recs["three"]["why"]))

# a login live on a remote whose usage probe failed is never vault-probed here
reset(NOW + 36000)
CONF.write_text(json.dumps({"remotes": ["r1"]}))
au.remote_live = lambda t: ("there", "three")
recs = au.poll(NOW + 36000)
au.remote_live = lambda t: ("there", "zz")
check("remote: a login live on a remote (its probe failed) is never vault-probed here",
      (str(acc / "three"), "c@x.test") not in calls, calls)
CONF.write_text(json.dumps({"remotes": []}))

# a RimPulse reading republished at a poll keeps its own measurement time when it is later carried
pulse = ROOT / "pulse"
pulse.mkdir(exist_ok=True)
T0 = NOW + 40000
(pulse / "usage.json").write_text(json.dumps({"accounts": {"four": {"measured_at": T0 - 60,
                                  "week": {"pct": 40.0, "resets_at": T0 + 50 * 3600}}}}))
reset(T0)
recs = au.poll(T0)
check("pulse control: a fresh RimPulse reading is MEASURED at its own time",
      recs["four"]["source"] == "MEASURED" and recs["four"]["measured_at"] == au.iso(T0 - 60), recs["four"])
(pulse / "usage.json").unlink()
reset(T0 + 900)
recs = au.poll(T0 + 900)
check("pulse: carried later, the estimate keeps the reading's own time, not the poll that republished it",
      recs["four"]["source"] == "ESTIMATE" and recs["four"]["measured_at"] == au.iso(T0 - 60), recs["four"])

# ---- (c) a switch between `auth status` and `/usage` on the live probe
use = json.dumps({"is_error": False, "result": TEXT})
idents = []


def fake_run(argv, env, timeout=90):
    if argv[1:3] == ["auth", "status"]:
        return 0, json.dumps({"loggedIn": True, "email": idents.pop(0)})
    return 0, use


au._run = fake_run
idents[:] = ["a@x.test", "c@x.test"]
fig, why = real_probe_local(None, "a@x.test", NOW)
check("switch(c): a login change across /usage (one switch) refuses the reading", fig is None and "switch" in why, (fig, why))
idents[:] = ["a@x.test", "a@x.test"]
fig, why = real_probe_local(None, "a@x.test", NOW)
check("switch(c) control: the same login before and after reads", fig is not None, why)

# the remote probe carries the same bracket
SEP = au.SEP
outs = []
au._ssh = lambda target, script, timeout=120: (0, outs.pop(0))
outs[:] = [json.dumps({"loggedIn": True, "email": "a@x.test"}) + "\n" + SEP + "\n" + use + "\n" + SEP + "\n"
           + json.dumps({"loggedIn": True, "email": "c@x.test"})]
fig, why = real_probe_remote("r1", "a@x.test", NOW)
check("switch(c): a remote whose login changed across /usage is refused", fig is None and "switch" in why, (fig, why))
outs[:] = [json.dumps({"loggedIn": True, "email": "a@x.test"}) + "\n" + SEP + "\n" + use + "\n" + SEP + "\n"
           + json.dumps({"loggedIn": True, "email": "a@x.test"})]
fig, why = real_probe_remote("r1", "a@x.test", NOW)
check("switch(c) control: a remote on the same login before and after reads", fig is not None, why)

print(f"\n{len(FAILS)} failure(s)" if FAILS else "\nall passed")
sys.exit(1 if FAILS else 0)
