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
  3b. RimPulse     - pulse/usage.py's last reading of the plan's usage endpoint (the same figures /usage
                     shows, read with the stored token, never refreshed), if under 20 minutes old.
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

  account_usage.py poll                 read every account once, append the series (the timer runs this)
  account_usage.py now [--json]         the newest reading per account (no polling)
  account_usage.py install [--deploy D] write + enable the systemd user timer rm-account-usage.timer
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
def registry() -> dict[str, str]:
    """name -> email from the switcher's registry (non-secret)."""
    reg = {}
    try:
        for line in (ACCOUNTS_DIR / "accounts.tsv").read_text().splitlines():
            parts = line.split()
            if len(parts) >= 2 and not line.lstrip().startswith("#"):
                reg[parts[0]] = parts[1].lower()
    except OSError:
        pass
    return reg


def config() -> dict:
    p = Path(os.environ.get("RM_ACCOUNT_USAGE_CONF") or ACCOUNTS_DIR / "account_usage.json")
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return {}


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


def probe_local(config_dir: str | None, want_email: str, now: float) -> tuple[dict | None, str]:
    env = _env(config_dir)
    rc, auth = _run([CLAUDE, "auth", "status"], env, 30)
    if rc != 0:
        return None, "auth status failed"
    rc, use = _run([CLAUDE, *USAGE_ARGS], env)
    if rc != 0:
        return None, f"/usage exited {rc}"
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
        return f"not warmed: {type(e).__name__}: {str(e)[:120]}"


SEP = "=====ACCOUNT_USAGE_SEP====="


def _ssh(target: str, script: str, timeout: int = 120) -> tuple[int, str]:
    try:
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", target, "bash -lc " +
                            shlex.quote(script)], capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout
    except (OSError, subprocess.TimeoutExpired) as e:
        return 124, type(e).__name__


def remote_live(target: str) -> tuple[str | None, str | None]:
    """(machine name, live account name) on a remote, from its switcher's status (non-secret)."""
    rc, out = _ssh(target, "claude-account status --json", 40)
    try:
        st = json.loads(out)
    except ValueError:
        return None, None
    return st.get("machine"), st.get("live")


def probe_remote(target: str, want_email: str, now: float) -> tuple[dict | None, str]:
    """The remote's live login, read with that machine's own environment (its sessions' config dir)."""
    script = (f'cd "$(mktemp -d)" && claude auth status; echo {SEP}; '
              f'claude {" ".join(USAGE_ARGS)}; cd / ')
    rc, out = _ssh(target, script)
    if SEP not in out:
        return None, f"remote probe failed ({rc})"
    auth, use = out.split(SEP, 1)
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


def _basis_time(r: dict | None) -> float:
    if not r:
        return 0.0
    return epoch(r.get("measured_at") if r.get("source") == "ESTIMATE" else r.get("ts")) or 0.0


def carry(name: str, prev: dict | None, now: float, why: str) -> dict:
    """ESTIMATE from the last MEASURED reading while its window has not reset; else UNMEASURED."""
    if prev and prev.get("source") in ("MEASURED", "ESTIMATE") and prev.get("week_pct_used") is not None:
        basis = prev.get("measured_at") if prev.get("source") == "ESTIMATE" else prev.get("ts")
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
    reg, cfg, here = registry(), config(), machine_name()
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
    remote_ok, live_remote = True, set()
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
            got[name] = dict(pr, ts=iso(now), why="; ".join(why[name]))
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
    out = {"schema": SCHEMA, "updated": lat.get("updated"), "accounts": {}}
    for name, r in (lat.get("accounts") or {}).items():
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
        out["accounts"][name] = d
    return out


# ------------------------------------------------------------------ timer
SERVICE = """[Unit]
Description=Claude account usage poll (claude /usage per account; account_usage.py)

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {script} poll
TimeoutStartSec=420s
"""
TIMER = """[Unit]
Description=Claude account usage poll, every 15 min

[Timer]
OnBootSec=3min
OnUnitActiveSec=15min
Persistent=true

[Install]
WantedBy=timers.target
"""


def install(deploy: str) -> str:
    script = Path(deploy) / "src/RimMandrake/Utils/account_usage.py"
    if not script.exists():
        raise SystemExit(f"install: {script} does not exist (pass --deploy <checkout>)")
    units = Path.home() / ".config/systemd/user"
    units.mkdir(parents=True, exist_ok=True)
    (units / f"{UNIT}.service").write_text(SERVICE.format(script=script))
    (units / f"{UNIT}.timer").write_text(TIMER)
    for argv in (["daemon-reload"], ["enable", "--now", f"{UNIT}.timer"]):
        subprocess.run(["systemctl", "--user", *argv], check=True)
    return f"{UNIT}.timer -> {script}"


def _fmt(d: dict) -> str:
    def f(k):
        p, h = d.get(f"{k}_pct_left"), d.get(f"hours_to_{k}_reset")
        return "?" if p is None else f"{p:g}% left" + ("" if h is None else f", resets in {h:.1f} h")
    return (f"{d['account']:<8} {d['source']:<10} week {f('week'):<28} session {f('session'):<28} "
            f"{'STALE ' if d['stale'] else ''}measured {d.get('measured_at') or 'never'} ({d.get('machine') or '-'})")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("poll")
    p = sub.add_parser("now")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("install")
    p.add_argument("--deploy", default=os.environ.get("RM_PULSE_DEPLOY", "/mnt/d/ClaudeWork/rimmandrake/pulse-deploy"))
    a = ap.parse_args(argv)
    if a.cmd == "poll":
        recs = poll()
        print(" ".join(f"{n}={r['source']}" for n, r in recs.items()))
        return 0 if recs else 1
    if a.cmd == "install":
        print(install(a.deploy))
        return 0
    st = read_now()
    if a.json:
        print(json.dumps(st, indent=1, sort_keys=True))
    else:
        if not st["accounts"]:
            print("no reading yet (account_usage.py poll)")
        for d in st["accounts"].values():
            print(_fmt(d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
