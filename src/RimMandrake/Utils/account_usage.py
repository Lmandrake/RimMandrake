#!/usr/bin/env python3
"""How much is left on each Claude subscription account the system uses: a polled, labelled time series.

Owner, 2026-10-26: "The system should be able to confirm how much is left on each of the three accounts it
uses. This should be provided to rimpulse or any other rimflow need."

THE INSTRUMENT (MEASURED, first-party): Claude Code's own `/usage` command, run headless:
    claude -p /usage --output-format json --no-session-persistence
It makes no model call (num_turns 0, cost 0) and prints the same lines as the interactive `/usage`:
    Current session: 16% used · resets Oct 26, 4:10pm (America/Los_Angeles)
    Current week (all models): 59% used · resets Oct 28, 1pm (America/Los_Angeles)
Before each reading, `claude auth status` in the SAME environment proves which login answered; a reading
whose email is not the account's registry email is discarded, never filed under the wrong label.

Where each account is read, in order (the first that answers wins):
  1. live here     - the account this machine's own sessions use (default config dir, as they run it).
  2. live remote   - the account another machine's sessions use (ssh; remotes come from the config file).
  3. vault here    - a dormant login's own config dir, ONLY while its access token is valid for 15 more
                     minutes, so the probe never refreshes (a refresh rotates the credential under the
                     account switcher, `claude-account`). Held under the switcher's own machine lock.
                     A token that does need one is refreshed with the switcher's own warm_one (one short model
                     call), at most once an hour per account, only when every remote answered and none has it
                     live, and only under the switcher's machine lock after its live_account() is read again
                     there: no switch can land between that check and the refresh, so the live login is never
                     warmed (a refresh of the live credential is an "auto log out"). Then the token is read again.
  3b. RimPulse     - usage.json under $RM_PULSE_STATE, if under 20 minutes old: the reading RimPulse's daemon
                     wrote until it retired (2026-11-03). Nothing writes the file now, so this step finds none.
  4. ESTIMATE      - none answered: the last MEASURED reading carried forward while its window has not
                     reset. A lower bound (usage only rises inside a window); labelled, never "MEASURED".
  5. UNMEASURED    - nothing to carry (no reading yet, or the window reset since): every figure null.
A live account's vault copy is never run: it is a stale backup and running it could reuse a rotated token.

Account names (non-secret labels) and emails come from the switcher's registry
(~/.claude-accounts/accounts.tsv); remotes from ~/.claude-accounts/account_usage.json
({"remotes": ["user@host", ...]}, or $RM_ACCOUNT_USAGE_CONF). This file names no account, host or key.
Credentials are never printed, logged or stored: only the expiry time of a vault token is read.

FILE CONTRACT (schema 1), under $RM_ACCOUNT_USAGE_DIR (default /mnt/d/ClaudeWork/rimmandrake/account_usage):
  series.jsonl  append-only, one record per account per poll (RECORD_KEYS below)
  latest.json   {"schema", "updated", "accounts": {name: newest record}}, rewritten atomically each poll
Readers: `account_usage.py now --json` (latest + derived pct_left, hours_to_reset, age, stale) or
`account_usage.read_now()`. Times are ISO-8601 with offset; percentages are percent USED, as /usage shows.
Every per-model weekly limit (/usage's "Current week (Fable)" lines, `other_weeks`) is read too: read_now gives each
as LEFT in `model_weeks`, the status line prints each, and week_left_for(row, model) is an account's level for a
run of that model (the lower of all-models and the model's own; RIMMANDRAKE_READ_FABLE_WEEKLY_METER_USAGE_LINE_NEVER_SHOWED).

  account_usage.py poll                 read every account once, append the series (the timer runs this)
  account_usage.py now [--json]         the newest reading per account (no polling); text mode adds codex and jpl-genai lines (all as LEFT)
  its timer: src/RimMandrake/Utils/systemd/rm-account-usage.{service,timer} (ops_clocks.py install rm-account-usage --apply --enable)
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

SCHEMA = 1
ACCOUNTS_DIR = Path(os.environ.get("RM_ACCOUNTS_DIR", Path.home() / ".claude-accounts"))
DATA_DIR = Path(os.environ.get("RM_ACCOUNT_USAGE_DIR", "/mnt/d/ClaudeWork/rimmandrake/account_usage"))
LIVE_JSON = Path(os.environ.get("RM_LIVE_CLAUDE_JSON", Path.home() / ".claude.json"))
CLAUDE = os.environ.get("RM_CLAUDE_BIN") or str(Path.home() / ".local" / "bin" / "claude")
CLAUDE_ACCOUNT = os.environ.get("RM_CLAUDE_ACCOUNT") or str(Path.home() / ".local" / "bin" / "claude-account")
WARM_EVERY = 60 * 60        # at most one switcher warm per dormant account per hour (each costs one model call)
PULSE_USAGE = Path(os.environ.get("RM_PULSE_STATE", Path.home() / ".local/state/rm-dashboard")) / "usage.json"
PULSE_FRESH = 20 * 60       # RimPulse's own endpoint reading counts as a measurement of now for this long
VAULT_MARGIN = 15 * 60      # a vault token must stay valid this long, so the probe never triggers a refresh
STALE_AFTER = 45 * 60       # a reader treats an older record as stale (three missed polls)
LOCK_WAIT = 30
UNIT = "rm-account-usage"
RECORD_KEYS = ("schema", "ts", "account", "source", "method", "machine", "session_pct_used",
               "session_resets_at", "week_pct_used", "week_resets_at", "other_weeks", "measured_at", "why")
# Variables that would route a probe away from the subscription login (same list as the switcher).
BAD_ENV = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "CLAUDE_CODE_USE_BEDROCK",
           "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY", "CLAUDE_CODE_OAUTH_TOKEN", "CLAUDE_CONFIG_DIR",
           "CLAUDE_SECURESTORAGE_CONFIG_DIR")
USAGE_ARGS = ["-p", "/usage", "--output-format", "json", "--no-session-persistence", "--setting-sources", "project"]
MONTHS = {m: i for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}
LINE_RE = re.compile(r"^\s*Current (?:session|week \((?P<scope>[^)]+)\))\s*:\s*(?P<pct>\d+(?:\.\d+)?)%\s*used"
                     r"(?:\s*·\s*(?P<rest>.*))?$", re.M)
RESET_RE = re.compile(r"resets\s+(?:(?P<mon>[A-Z][a-z]{2})\s+(?P<day>\d{1,2}),?\s+)?(?P<h>\d{1,2})(?::(?P<mi>\d{2}))?"
                      r"\s*(?P<ap>am|pm)\s*(?:\((?P<tz>[^)]+)\))?", re.I)


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).astimezone().isoformat(timespec="seconds")


def epoch(s) -> float | None:
    try:
        return datetime.fromisoformat(str(s)).timestamp() if s else None
    except ValueError:
        return None


# ------------------------------------------------------------------ parsing /usage
def parse_reset(rest: str, now: float) -> str | None:
    """'resets Oct 28, 1pm (America/Los_Angeles)' -> ISO time. /usage omits the year (and the date when it is
    today): take the candidate nearest after now-1 day, which a 5-hour or 7-day window always satisfies."""
    m = RESET_RE.search(rest or "")
    if not m:
        return None
    try:
        tz = ZoneInfo(m["tz"]) if m["tz"] else datetime.now().astimezone().tzinfo
    except (KeyError, ValueError):
        tz = datetime.now().astimezone().tzinfo
    h = int(m["h"]) % 12 + (12 if m["ap"].lower() == "pm" else 0)
    base = datetime.fromtimestamp(now, tz)
    cands = []
    if m["mon"]:
        mon = MONTHS.get(m["mon"][:3].title())
        if not mon:
            return None
        for y in (base.year - 1, base.year, base.year + 1):
            try:
                cands.append(datetime(y, mon, int(m["day"]), h, int(m["mi"] or 0), tzinfo=tz))
            except ValueError:
                pass
    else:
        d0 = base.replace(hour=h, minute=int(m["mi"] or 0), second=0, microsecond=0)
        cands = [d0, d0 + timedelta(days=1)]
    ok = [c for c in cands if c.timestamp() >= now - 86400]
    return min(ok, key=lambda c: c.timestamp()).isoformat(timespec="minutes") if ok else None


def parse_usage(text: str, now: float) -> dict | None:
    """The /usage text -> figures, or None when it holds no weekly all-models line (the one figure that
    makes a reading)."""
    out = {"session_pct_used": None, "session_resets_at": None, "week_pct_used": None, "week_resets_at": None,
           "other_weeks": {}}
    for m in LINE_RE.finditer(text or ""):
        pct, reset = float(m["pct"]), parse_reset(m["rest"] or "", now)
        scope = m["scope"]
        if scope is None:
            out["session_pct_used"], out["session_resets_at"] = pct, reset
        elif scope.strip().lower() == "all models":
            out["week_pct_used"], out["week_resets_at"] = pct, reset
        else:
            out["other_weeks"][scope.strip()] = {"pct_used": pct, "resets_at": reset}
    return out if out["week_pct_used"] is not None else None


# ------------------------------------------------------------------ config
class RegistryUnreadable(RuntimeError):
    """The switcher's registry could not be read: no account is known, so nothing may be published."""


class RegistryEmpty(RuntimeError):
    """The registry was read and names no account: a different answer from unreadable, and nothing to poll."""


def registry(strict: bool = False) -> dict[str, str]:
    """name -> email from the switcher's registry (non-secret). strict: an unreadable file raises RegistryUnreadable
    (poll() must not publish an empty snapshot over good readings); otherwise readers get {} (an undecodable file
    included, which used to raise)."""
    reg = {}
    path = ACCOUNTS_DIR / "accounts.tsv"
    try:
        for line in path.read_text().splitlines():
            parts = line.split()
            if len(parts) >= 2 and not line.lstrip().startswith("#"):
                reg[parts[0]] = parts[1].lower()
    except (OSError, UnicodeDecodeError) as e:
        if strict:
            raise RegistryUnreadable(f"switcher registry {path} unreadable ({type(e).__name__}: {e})") from e
    return reg


def config() -> dict:
    """The poll's config. No file is a machine with no remotes ({}); a file that cannot be read, does not parse or
    whose `remotes` is not a list of hosts is "could not look": {"unreadable": why}, so poll() never takes it for "no
    remotes" and warms a login a remote may hold live (RIMMANDRAKE_HARDEN_ACCOUNT_USAGE_POLL_RACES_CODEX_FLAGGED)."""
    p = Path(os.environ.get("RM_ACCOUNT_USAGE_CONF") or ACCOUNTS_DIR / "account_usage.json")
    try:
        cfg = json.loads(p.read_text())
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as e:
        return {"unreadable": f"{p} unreadable ({type(e).__name__})"}
    if not isinstance(cfg, dict):
        return {"unreadable": f"{p} unreadable (not a JSON object)"}
    rem = cfg.get("remotes", [])
    if not (isinstance(rem, list) and all(isinstance(t, str) and t for t in rem)):
        return {"unreadable": f"{p} unreadable (remotes is not a list of hosts)"}
    return cfg


def machine_name() -> str:
    try:
        return json.loads((ACCOUNTS_DIR / "machine.json").read_text()).get("machine") or os.uname().nodename
    except (OSError, ValueError):
        return os.uname().nodename


def live_email() -> str | None:
    """The email this machine's own sessions are logged in as (default config dir); no secret is read."""
    try:
        return ((json.loads(LIVE_JSON.read_text()).get("oauthAccount") or {}).get("emailAddress") or "").lower() or None
    except (OSError, ValueError):
        return None


def vault_token_valid_until(name: str) -> float | None:
    """Expiry (epoch s) of the vault login's access token. Only that one field is kept."""
    try:
        exp = (json.loads((ACCOUNTS_DIR / name / ".credentials.json").read_text()).get("claudeAiOauth") or {}).get("expiresAt")
    except (OSError, ValueError):
        return None
    return float(exp) / 1000 if exp else None


# ------------------------------------------------------------------ probes
def _env(config_dir: str | None) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in BAD_ENV}
    if config_dir:
        env["CLAUDE_CONFIG_DIR"] = config_dir
    return env


def _run(argv, env, timeout=90) -> tuple[int, str]:
    cwd = tempfile.mkdtemp(prefix="acct-usage-")
    try:
        r = subprocess.run(argv, env=env, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout
    except (OSError, subprocess.TimeoutExpired) as e:
        return 124, type(e).__name__
    finally:
        shutil.rmtree(cwd, ignore_errors=True)


def _reading(auth_out: str, usage_out: str, want_email: str, now: float) -> tuple[dict | None, str]:
    """Check identity, then parse. Returns (figures, why-not)."""
    try:
        auth = json.loads(auth_out)
    except ValueError:
        return None, "auth status unreadable"
    if not auth.get("loggedIn"):
        return None, "not logged in"
    if (auth.get("email") or "").lower() != want_email:
        return None, "a different login answered"
    try:
        res = json.loads(usage_out)
    except ValueError:
        return None, "/usage output unreadable"
    text = res.get("result") or ""
    if res.get("is_error") or "subscription" not in text:
        return None, "/usage did not report a subscription"
    fig = parse_usage(text, now)
    return (fig, "") if fig else (None, "/usage held no weekly figure")


def _same_login(before: str, after: str) -> bool:
    """The login answering `auth status` after /usage is the one that answered before it: a switch in between would
    file one login's quota under the other's name (RIMMANDRAKE_HARDEN_ACCOUNT_USAGE_POLL_RACES_CODEX_FLAGGED). Two
    switches inside one /usage call (A to B and back) are the race left open: the live probe is not run under the
    switcher's lock because `claude-account use` waits only 5 s for it and would refuse the switch for the probe's
    length (each such switch also stops every Claude process, so two in one call are not an expected sequence)."""
    try:
        a, b = json.loads(before), json.loads(after)
    except ValueError:
        return False
    return isinstance(a, dict) and isinstance(b, dict) and (a.get("email") or "").lower() == (b.get("email") or "").lower()


def probe_local(config_dir: str | None, want_email: str, now: float) -> tuple[dict | None, str]:
    env = _env(config_dir)
    rc, auth = _run([CLAUDE, "auth", "status"], env, 30)
    if rc != 0:
        return None, "auth status failed"
    rc, use = _run([CLAUDE, *USAGE_ARGS], env)
    if rc != 0:
        return None, f"/usage exited {rc}"
    rc, after = _run([CLAUDE, "auth", "status"], env, 30)
    if rc != 0:
        return None, "auth status after /usage failed"
    if not _same_login(auth, after):
        return None, "the login changed during /usage (a switch landed); reading refused"
    return _reading(auth, use, want_email, now)


clock = time.time  # a seam: the warm reservation is stamped with the time it is made, not the poll's start


_SWITCHER = {}


def load_switcher(path: str):
    """The account switcher (claude-account, a Python script) loaded as a module, so the warm can run under ITS
    machine lock and ask IT which login is live. Loading runs only its definitions (its main is guarded)."""
    if path not in _SWITCHER:
        import importlib.machinery
        import importlib.util
        loader = importlib.machinery.SourceFileLoader("claude_account_switcher", path)
        mod = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
        loader.exec_module(mod)
        _SWITCHER[path] = mod
    return _SWITCHER[path]


def switcher_module():
    return load_switcher(CLAUDE_ACCOUNT)


def warm(name: str, email: str, now: float, remotes=()) -> str:
    """Refresh a DORMANT login, at most once per WARM_EVERY. The caller has proven no remote has it live; this
    machine is proven HERE, under the switcher's own machine lock (the one `claude-account use` takes): its
    live_account() is read again under that lock and the warm is refused if the target is live (by name or by
    email) or the live login is unknown, so a switch can never land between the check and the refresh. A warm of
    the live login is a refresh of the live credential: the "auto log out" the owner banned (2026-10-28).
    `remotes` are asked again right before the lock ([R] GPT 2026-10-28: a remote can switch to the target while
    the poll probes); a remote's switcher cannot be locked from here, so a switch there inside the seconds between
    that recheck and the warm is the one race left open."""
    path = DATA_DIR / "warm_state.json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / ".warm.lock", "a") as lk:  # two polls at once reserve the hour once ([R] GPT 2026-10-28)
        fcntl.flock(lk, fcntl.LOCK_EX)
        t = max(now, clock())
        try:
            st = json.loads(path.read_text())
        except (OSError, ValueError):
            st = {}
        last = float(st.get(name) or 0)
        if 0 <= t - last < WARM_EVERY:
            return f"warm tried {int((t - last) // 60)} min ago"
        st[name] = t
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(st))
        os.replace(tmp, path)
    for target in remotes:
        _mach, rn = remote_live(target)
        if not rn or rn == name:
            return f"not warmed: at the recheck {target} is {'on this login' if rn == name else 'not answering'}"
    try:
        ca = switcher_module()
        with ca.MachineLock(wait=LOCK_WAIT):
            live, live_mail = ca.live_account()
            if not live or live == name or (live_mail or "").lower() == email:
                return (f"not warmed: under the switcher's lock the live login here is "
                        f"{'this account' if live == name or (live_mail or '').lower() == email else 'unknown'}")
            if ca.where(name) != "vault":
                return "not warmed: no vault login under the switcher's lock"
            health = ca.read_json(ca.HEALTH, {}) or {}
            res = ca.warm_one(name, health)
            ca.write_json_atomic(ca.HEALTH, health)
        result = str((res or {}).get("result"))
        ca.log_event(op="warm", results={name: result}, by="account_usage")
        return "warm " + result
    except Exception as e:  # noqa: BLE001 - a switcher that cannot be loaded, is busy or fails: no warm, poll goes on
        return f"not warmed: {type(e).__name__}: {str(e)}"


SEP = "=====ACCOUNT_USAGE_SEP====="


def _ssh(target: str, script: str, timeout: int = 120) -> tuple[int, str]:
    try:
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", target, "bash -lc " +
                            shlex.quote(script)], capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout
    except (OSError, subprocess.TimeoutExpired) as e:
        return 124, type(e).__name__


def remote_live(target: str) -> tuple[str | None, str | None]:
    """(machine name, live account name) on a remote, from its switcher's status (non-secret; account_live, the one
    reader). (None, None) when the remote cannot be read or names no live account."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import account_live as AL
    a = AL.read(target=target)
    return AL.status_of(a).get("machine"), AL.name_of(a)


def probe_remote(target: str, want_email: str, now: float) -> tuple[dict | None, str]:
    """The remote's live login, read with that machine's own environment (its sessions' config dir)."""
    script = (f'cd "$(mktemp -d)" && claude auth status; echo {SEP}; '
              f'claude {" ".join(USAGE_ARGS)}; echo {SEP}; claude auth status; cd / ')
    rc, out = _ssh(target, script)
    if out.count(SEP) != 2:
        return None, f"remote probe failed ({rc})"
    auth, use, after = out.split(SEP)
    if not _same_login(auth.strip(), after.strip()):
        return None, "the login changed during /usage (a switch landed); reading refused"
    return _reading(auth.strip(), use.strip(), want_email, now)


class Lock:
    """The account switcher's machine lock, so a vault probe never overlaps a switch, warm or capture."""

    def __enter__(self):
        self.fh = open(ACCOUNTS_DIR / ".lock", "a")
        deadline = time.time() + LOCK_WAIT
        while True:
            try:
                fcntl.flock(self.fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except BlockingIOError:
                if time.time() > deadline:
                    self.fh.close()
                    raise TimeoutError("account switcher busy")
                time.sleep(0.5)

    def __exit__(self, *a):
        fcntl.flock(self.fh, fcntl.LOCK_UN)
        self.fh.close()


# ------------------------------------------------------------------ records
def record(name, now, source, method, machine, fig=None, measured_at=None, why="") -> dict:
    fig = fig or {}
    if source == "MEASURED" and fig.get("session_pct_used") is None and not why:
        # SESSION_METER_DIAGNOSE_SYSTEM_BLANK: /usage prints no `Current session` line, and the plan endpoint's
        # five_hour is null, for EVERY account when no 5-hour window is open. A blank session figure beside a
        # MEASURED week is the instrument's answer, not a fault of one account.
        why = "no session window reported (the plan shows none open); week figure is MEASURED"
    return {"schema": SCHEMA, "ts": iso(now), "account": name, "source": source, "method": method,
            "machine": machine, "session_pct_used": fig.get("session_pct_used"),
            "session_resets_at": fig.get("session_resets_at"), "week_pct_used": fig.get("week_pct_used"),
            "week_resets_at": fig.get("week_resets_at"), "other_weeks": fig.get("other_weeks") or {},
            "measured_at": measured_at, "why": why}


def pulse_reading(name: str) -> dict | None:
    """RimPulse's last good endpoint reading for this account, as a MEASURED record stamped at its own time."""
    try:
        a = (json.loads(PULSE_USAGE.read_text()).get("accounts") or {}).get(name) or {}
    except (OSError, ValueError):
        return None
    t, wk, five = a.get("measured_at"), a.get("week") or {}, a.get("five") or {}
    if not t or wk.get("pct") is None:
        return None
    rs = lambda w: iso(w["resets_at"]) if w.get("resets_at") else None  # noqa: E731
    fig = {"week_pct_used": float(wk["pct"]), "week_resets_at": rs(wk),
           "session_pct_used": None if five.get("pct") is None else float(five["pct"]), "session_resets_at": rs(five)}
    return record(name, float(t), "MEASURED", "plan usage endpoint, via RimPulse usage.json", None, fig, iso(float(t)))


def carry_model_weeks(prev: dict | None, now: float) -> dict:
    """The per-model weekly limits of the last reading, for a record whose source cannot see them (RimPulse's endpoint
    reading has the all-models week only): each limit whose window has not reset, stamped `carried_from` (the time it
    was read), so a reader can tell it is older than the record; a reset window is dropped (unknown now), never kept."""
    if not prev or prev.get("source") not in ("MEASURED", "ESTIMATE"):
        return {}
    basis = prev.get("measured_at") or prev.get("ts")
    return {k: dict(v, carried_from=v.get("carried_from") or basis)
            for k, v in (prev.get("other_weeks") or {}).items()
            if isinstance(v, dict) and (epoch(v.get("resets_at")) or 0) > now}


def _basis_time(r: dict | None) -> float:
    """When the record's figures were measured: measured_at (a RimPulse reading republished at a later poll keeps its
    own time there), else ts."""
    if not r:
        return 0.0
    return epoch(r.get("measured_at") or r.get("ts")) or 0.0


def carry(name: str, prev: dict | None, now: float, why: str) -> dict:
    """ESTIMATE from the last MEASURED reading while its window has not reset; else UNMEASURED."""
    if prev and prev.get("source") in ("MEASURED", "ESTIMATE") and prev.get("week_pct_used") is not None:
        basis = prev.get("measured_at") or prev.get("ts")
        wk = epoch(prev.get("week_resets_at"))
        if basis and wk and wk > now:
            fig = dict(prev)
            if (epoch(prev.get("session_resets_at")) or 0) <= now:
                fig["session_pct_used"] = fig["session_resets_at"] = None
            fig["other_weeks"] = {k: v for k, v in (prev.get("other_weeks") or {}).items()
                                  if (epoch(v.get("resets_at")) or 0) > now}
            return record(name, now, "ESTIMATE", f"carried forward from the MEASURED reading at {basis}; a lower "
                          "bound (usage only rises inside a window)", prev.get("machine"), fig, basis, why)
    return record(name, now, "UNMEASURED", "no reading and none to carry", None, None, None, why)


def poll(now: float | None = None) -> dict:
    now = now or time.time()
    reg = registry(strict=True)
    if not reg:  # read, and names no account: publishing {} would wipe every good reading (RIMMANDRAKE_GUARD_USAGE_POLL_WIPES_LATEST_ON_EMPTY_REGISTRY)
        raise RegistryEmpty(f"switcher registry {ACCOUNTS_DIR / 'accounts.tsv'} names no account")
    cfg, here = config(), machine_name()
    prev = (read_latest() or {}).get("accounts") or {}
    got, why = {}, {n: [] for n in reg}
    by_email = {e: n for n, e in reg.items()}
    # 1. live here
    n = by_email.get(live_email() or "")
    if n:
        fig, w = probe_local(None, reg[n], now)
        if fig:
            got[n] = record(n, now, "MEASURED", "claude /usage, live login", here, fig, iso(now))
        else:
            why[n].append(f"live on {here}: {w}")
    # 2. live on a remote
    remote_ok, live_remote = not cfg.get("unreadable"), set()
    if cfg.get("unreadable"):
        for k in why:
            if k not in got:
                why[k].append(f"config {cfg['unreadable']}: the remotes are unknown")
    for target in cfg.get("remotes") or []:
        mach, rn = remote_live(target)
        if not rn:
            remote_ok = False
            for k in why:
                if k not in got:
                    why[k].append("a remote did not answer its status")
            continue
        live_remote.add(rn)
        if rn in reg and rn not in got:
            fig, w = probe_remote(target, reg[rn], now)
            if fig:
                got[rn] = record(rn, now, "MEASURED", "claude /usage, live login", mach, fig, iso(now))
            else:
                why[rn].append(f"live on {mach}: {w}")
    # 3. dormant logins here, while their token needs no refresh (warmed by the switcher when it does)
    live_here = n
    for name in reg:
        if name in got or name == live_here:
            continue
        if name in live_remote:  # live on a remote whose probe failed: its vault copy here is never run either
            why[name].append(f"no vault probe on {here}: live on a remote")
            continue
        exp = vault_token_valid_until(name)
        if not exp:
            why[name].append(f"no vault login on {here}")
            continue
        if exp < now + VAULT_MARGIN:
            # remotes cannot be locked from here: a warm needs every remote to have answered and none to hold this
            # login live. Here, warm() re-reads the live login under the switcher's own lock.
            if not (remote_ok and name not in live_remote):
                why[name].append(f"vault token on {here} needs a refresh (not warmed: where each login is live "
                                 "is not proven)")
                continue
            res = warm(name, reg[name], now, cfg.get("remotes") or [])
            exp = vault_token_valid_until(name)
            if not exp or exp < now + VAULT_MARGIN:
                why[name].append(f"vault token on {here} needs a refresh ({res})")
                continue
        try:
            with Lock():
                # a switch may have landed since step 1: the login live here NOW is read under the switcher's lock,
                # and a vault dir that just became the live login is never probed (its twin is the live credential);
                # nor one whose token the remote probes and the lock wait have brought inside the margin
                now_live, exp = live_email(), vault_token_valid_until(name)
                if not now_live:
                    fig, w = None, "the live login here is unreadable under the switcher's lock; not vault-probed"
                elif now_live == reg[name]:
                    fig, w = None, "became the live login here during the poll; not vault-probed"
                elif not exp or exp < max(now, clock()) + VAULT_MARGIN:
                    fig, w = None, "vault token came inside the refresh margin during the poll; not vault-probed"
                else:
                    fig, w = probe_local(str(ACCOUNTS_DIR / name), reg[name], now)
        except (OSError, TimeoutError) as e:
            fig, w = None, str(e)
        if fig:
            got[name] = record(name, now, "MEASURED", "claude /usage, dormant login (valid token)", here, fig, iso(now))
        else:
            why[name].append(f"vault on {here}: {w}")
    # 3b. RimPulse's endpoint reading, when fresh; 4/5. carry the newest measurement, or give up
    for name in reg:
        if name in got:
            continue
        pr = pulse_reading(name)
        if pr and now - _basis_time(pr) <= PULSE_FRESH:
            got[name] = dict(pr, ts=iso(now), why="; ".join(why[name]),
                             other_weeks=carry_model_weeks(prev.get(name), now))
            continue
        basis = max((prev.get(name), pr), key=_basis_time)
        got[name] = carry(name, basis, now, "; ".join(why[name]))
    write(got, now)
    return got


def write(recs: dict, now: float) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / "series.jsonl", "a") as fh:
        for r in recs.values():
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    tmp = DATA_DIR / f"latest.json.{os.getpid()}.tmp"
    tmp.write_text(json.dumps({"schema": SCHEMA, "updated": iso(now), "accounts": recs}, indent=1, sort_keys=True))
    tmp.replace(DATA_DIR / "latest.json")


def read_latest() -> dict | None:
    try:
        return json.loads((DATA_DIR / "latest.json").read_text())
    except (OSError, ValueError):
        return None


def read_now(now: float | None = None) -> dict:
    """The stable reader: newest record per account plus allocator inputs. pct_left is 100 - pct_used (for an
    ESTIMATE it is an upper bound on what is left); hours_to_*_reset from now; age_min since the measurement
    the figures come from; stale when the poll itself is older than 45 min (the timer stopped)."""
    now = now or time.time()
    lat = read_latest() or {}
    return {"schema": SCHEMA, "updated": lat.get("updated"),
            "accounts": {name: derive_record(r, now) for name, r in (lat.get("accounts") or {}).items()}}


def derive_record(r: dict, now: float) -> dict:
    """One latest.json record plus the derived fields read_now documents. Pure."""
    d = dict(r)
    polled = now - (epoch(r.get("ts")) or 0)
    d["poll_age_min"] = round(polled / 60, 1)
    d["stale"] = polled > STALE_AFTER
    basis = epoch(r.get("measured_at"))
    d["age_min"] = None if basis is None else round((now - basis) / 60, 1)
    for k in ("session", "week"):
        used, rs = r.get(f"{k}_pct_used"), epoch(r.get(f"{k}_resets_at"))
        reset_passed = rs is not None and rs <= now
        d[f"{k}_pct_left"] = None if used is None or reset_passed else round(100 - used, 1)
        d[f"hours_to_{k}_reset"] = None if rs is None or reset_passed else round((rs - now) / 3600, 2)
    # every per-model weekly limit /usage shows beside the all-models one ("Current week (Fable)"), as LEFT: a scope
    # whose window has reset since the reading is None (unknown now), never 100 and never 0
    d["model_weeks"] = {}
    for scope, w in sorted((r.get("other_weeks") or {}).items()):
        used, rs = (w or {}).get("pct_used"), epoch((w or {}).get("resets_at"))
        gone = rs is not None and rs <= now
        d["model_weeks"][scope] = {"pct_left": None if used is None or gone else round(100 - used, 1),
                                   "hours_to_reset": None if rs is None or gone else round((rs - now) / 3600, 2),
                                   "resets_at": (w or {}).get("resets_at"), "carried_from": (w or {}).get("carried_from")}
    return d


def scope_for(model, scopes) -> str | None:
    """The per-model weekly limit a run of `model` also spends, or None. A scope is named by /usage ("Fable",
    "Opus", "Sonnet only"); its first word matched as a word inside the model alias or id ("fable",
    "claude-fable-5-2", "Fable 5.2") is the match. No model -> None (only the all-models limit applies)."""
    if not isinstance(model, str) or not model.strip():
        return None
    words = set(re.split(r"[^a-z0-9]+", model.lower()))
    for scope in scopes or ():
        head = (scope.split() or [""])[0].lower()
        if head and head != "all" and head in words:
            return scope
    return None


def week_left_for(d: dict, model=None) -> tuple[float | None, str, float | None]:
    """The level of one account for a run of `model`: the LOWEST of the all-models weekly limit and that model's
    own weekly limit, as (pct_left, limit_name, hours_to_that_limit's_reset). d is a derive_record() row.
    The all-models figure unknown -> (None, "all models", None): a per-model figure alone never makes a level.
    The model's own scope absent or unknown now (its window reset since the reading) -> the all-models figure."""
    left, h = d.get("week_pct_left"), d.get("hours_to_week_reset")
    if left is None:
        return None, "all models", None
    scope = scope_for(model, (d.get("model_weeks") or {}).keys())
    m = (d.get("model_weeks") or {}).get(scope) or {}
    if scope and m.get("pct_left") is not None and m["pct_left"] < left:
        return m["pct_left"], scope, m.get("hours_to_reset")
    return left, "all models", h


def _fmt(d: dict) -> str:
    def f(k):
        p, h = d.get(f"{k}_pct_left"), d.get(f"hours_to_{k}_reset")
        return "?" if p is None else f"{p:g}% left" + ("" if h is None else f", resets in {h:.1f} h")
    def mw(scope, w):
        p, h = w.get("pct_left"), w.get("hours_to_reset")
        return f" · {scope} week " + ("? (window reset since the reading)" if p is None else
                                f"{p:g}% left" + ("" if h is None else f", resets in {h:.1f} h")
                                + (f" (read {w['carried_from']})" if w.get("carried_from") else ""))
    models = "".join(mw(s, w) for s, w in (d.get("model_weeks") or {}).items())
    return (f"{d['account']:<8} {d['source']:<10} week {f('week'):<28}{models} session {f('session'):<28} "
            f"{'STALE ' if d['stale'] else ''}measured {d.get('measured_at') or 'never'} ({d.get('machine') or '-'})")


GENAI_SWITCH = "~/dev/GenAISwitch/bin/genai-switch"


def read_codex_points() -> dict:
    """Codex's weekly meter from the ops reader (ops_watch.c_codex, the one the ops digest's `## codex` block uses)."""
    import ops_watch
    return ops_watch.c_codex(time.time(), ops_watch.load_rules(), {})


def read_genai_status() -> tuple[str, str | None]:
    """(`absent`, None) when the tool is not on this machine; (`ok`, stdout) on exit 0; (`failed`, cause) otherwise."""
    tool = os.path.expanduser(GENAI_SWITCH)
    if not os.path.exists(tool):
        return "absent", None
    try:
        r = subprocess.run([tool, "status"], capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        return "failed", f"{type(e).__name__}: {e}"
    if r.returncode != 0:
        return "failed", f"exit {r.returncode}: {(r.stderr or r.stdout or '').strip()[-200:]}"  # cut-ok: terminal display
    return "ok", r.stdout


def _pacific(ts: float) -> str:
    return datetime.fromtimestamp(ts, ZoneInfo("America/Los_Angeles")).strftime("%a %b %d %H:%M %Z")


def _meter_line(name: str, left: float, reset_ts: float | None, now: float, mark: str, age_h: float | None) -> str:
    reset = "reset unknown" if reset_ts is None else f"resets {_pacific(reset_ts)} (in {(reset_ts - now) / 3600:.1f} h)"
    age = "" if age_h is None else f", {age_h:.1f} h old"
    return f"{name:<10}{left:g}% left, {reset} [{mark}{age}]"


def _codex_line(now: float, points: dict) -> tuple[str, bool]:
    used, hrs = points.get("codex.week_used_pct") or {}, points.get("codex.hours_to_reset") or {}
    v = used.get("v")
    if type(v) not in (int, float) or v < 0 or v != v:
        return f"{'codex':<10}UNMEASURED: {used.get('why') or 'no weekly reading'}", False
    h = hrs.get("v")
    reset = now + h * 3600 if type(h) in (int, float) else None
    at = epoch((used.get("x") or {}).get("reading_at"))
    mark = "measured" if used.get("m") == "MEASURED" else f"estimate: {used.get('why')}"
    return _meter_line("codex", round(100 - v, 1), reset, now, mark, None if at is None else (now - at) / 3600), True


def _genai_line(now: float, status: tuple[str, str | None]) -> tuple[str, bool]:
    kind, out = status
    if kind == "absent":
        return f"{'jpl-genai':<10}not on this machine", False
    if kind != "ok":
        return f"{'jpl-genai':<10}UNMEASURED: {out}", False
    m = re.search(r"(\d+(?:\.\d+)?)\s*%\s*(used|left|remaining)", out or "", re.I)
    if not m:
        return f"{'jpl-genai':<10}UNMEASURED: genai-switch status shows no percent meter", False
    pct = float(m.group(1))
    left = round(100 - pct, 1) if m.group(2).lower() == "used" else pct
    rs = re.search(r"\d{4}-\d\d-\d\dT[\d:]+(?:Z|[+-]\d\d:?\d\d)?", out)
    return _meter_line("jpl-genai", left, epoch(rs.group(0)) if rs else None, now, "measured", 0.0), True


def account_lines(now: float, st: dict, codex_reader=None, genai_reader=None) -> tuple[list[str], int]:
    """The one list: each Claude line as before, then codex, then JPL GenAI. Returns (lines, how many accounts
    gave a reading); `UNMEASURED: cause` and `not on this machine` are answers, never a percent."""
    codex_reader, genai_reader = codex_reader or read_codex_points, genai_reader or read_genai_status
    lines, n = [], 0
    for d in st["accounts"].values():
        lines.append(_fmt(d))
        n += d.get("week_pct_left") is not None
    try:
        cl, ok = _codex_line(now, codex_reader())
    except Exception as e:  # the reader failing is "could not look", named
        cl, ok = f"{'codex':<10}UNMEASURED: reader failed: {type(e).__name__}: {e}", False
    n += ok
    lines.append(cl)
    gl, ok = _genai_line(now, genai_reader())
    lines.append(gl)
    return lines, n + ok


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("poll")
    p = sub.add_parser("now")
    p.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "poll":
        try:
            recs = poll()
        except (RegistryUnreadable, RegistryEmpty) as e:
            # nothing published: latest.json keeps the last good snapshot, and stdout holds nothing that reads as one
            print(f"poll refused, nothing published: {e}", file=sys.stderr)
            return 3
        print(" ".join(f"{n}={r['source']}" for n, r in recs.items()))
        return 0 if recs else 1
    st = read_now()
    if a.json:
        print(json.dumps(st, indent=1, sort_keys=True))
    else:
        if not st["accounts"]:
            print("no reading yet (account_usage.py poll)")
        lines, n = account_lines(time.time(), st)
        print("\n".join(lines))
        if not n:
            print("no account could be read", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
