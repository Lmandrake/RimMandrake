#!/usr/bin/env python3
"""Measured Claude plan usage per account and GPT (codex) capacity, against the owner's budget rule.

CLAUDE_PLAN_USAGE_MEASURE_A_SOURCE. The rule (design/RimMandrake/standing_rulings.md §Account and capacity
budget, owner 2026-10-25 by card): the owned accounts may be fully used each WEEK, with a rough daily share;
keep a reserve for evening sessions with him; the spare account only after both owned ones are spent, and
never past about half of it; watch GPT capacity too.

Sources, all MEASURED (never an estimate):
- Claude: the plan's own usage endpoint per account (`five_hour` / `seven_day` utilization + resets_at),
  called with that account's stored OAuth access token. The token is read, never printed, never refreshed
  (a refresh rotates the account's credentials under the switcher). An expired token means no new reading:
  the last good one is shown with its age, and with none the account reads "unknown".
- GPT: codex's own `rate_limits` record in its newest session rollout, measured as of that session.

Every account name, the endpoint and the codex folders come from ~/.claude-accounts/budget.json (or
$RM_BUDGET_CONF); this file names none of them.
"""
from __future__ import annotations

import glob
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ACCOUNTS_DIR = Path(os.environ.get("RM_ACCOUNTS_DIR", Path.home() / ".claude-accounts"))
LIVE_CREDS = Path(os.environ.get("RM_LIVE_CREDS", Path.home() / ".claude" / ".credentials.json"))
REFETCH = 600          # one call per account per 10 min at most
FRESH = 20 * 60        # a reading older than this is shown as "as of <time>", never as now
DEPLETED = 98.0        # an owned account at or past this percent of its week counts as spent


def config() -> dict:
    p = Path(os.environ.get("RM_BUDGET_CONF") or ACCOUNTS_DIR / "budget.json")
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return {}


def _live_account() -> str | None:
    try:
        return json.loads((ACCOUNTS_DIR / "live.json").read_text()).get("account")
    except (OSError, ValueError):
        return None


def read_token(name: str) -> tuple[str | None, float | None, str]:
    """(access token, expires-at epoch s, why-not). The live account's own file is the current one: the
    vault copy of the live account goes stale the moment Claude Code rotates it."""
    path = LIVE_CREDS if name == _live_account() else ACCOUNTS_DIR / name / ".credentials.json"
    try:
        oa = json.loads(path.read_text()).get("claudeAiOauth") or {}
    except (OSError, ValueError):
        return None, None, "no stored credentials"
    tok, exp = oa.get("accessToken"), oa.get("expiresAt")
    exp = float(exp) / 1000 if exp else None
    return (tok, exp, "") if tok else (None, exp, "no access token stored")


def fetch_usage(url: str, beta: str, token: str, timeout: float = 8) -> dict:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "anthropic-beta": beta,
                                               "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def _epoch(iso) -> float | None:
    if not iso:
        return None
    try:
        return datetime.fromisoformat(str(iso).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _window(body: dict, key: str) -> dict | None:
    w = body.get(key)
    if not isinstance(w, dict) or w.get("utilization") is None:
        return None
    return {"pct": round(float(w["utilization"]), 1), "resets_at": _epoch(w.get("resets_at"))}


def read_codex(dirs: list[str], now: float) -> dict | None:
    """The last `rate_limits` codex wrote, from its newest rollouts (a session that hit no model call has
    none, so look back a few files). Measured as of that record's own timestamp."""
    files = []
    for d in dirs:
        files += glob.glob(os.path.join(os.path.expanduser(d), "*", "*", "*", "rollout-*.jsonl"))
    for f in sorted(files, key=lambda p: os.path.getmtime(p) if os.path.exists(p) else 0, reverse=True)[:6]:
        try:
            with open(f, "rb") as fh:
                fh.seek(max(0, os.path.getsize(f) - (4 << 20)))
                tail = fh.read().decode("utf-8", "replace").splitlines()
        except OSError:
            continue
        for line in reversed(tail):
            if '"rate_limits"' not in line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            rl = (d.get("payload") or {}).get("rate_limits") or {}
            p = rl.get("primary") or {}
            if p.get("used_percent") is None:
                continue
            return {"name": "codex", "pct": round(float(p["used_percent"]), 1), "resets_at": p.get("resets_at"),
                    "window_min": p.get("window_minutes"), "plan": rl.get("plan_type"),
                    "measured_at": _epoch(d.get("timestamp")) or os.path.getmtime(f)}
    return None


def refresh(now: float | None = None, cfg: dict | None = None, fetch=fetch_usage, cache: Path | None = None) -> dict:
    """Re-read what is due (≤ one call per account per REFETCH) and return the panel. The cache keeps the
    last GOOD reading per account, so an expired token shows an aged measurement, never an invented one."""
    now = now or time.time()
    cfg = config() if cfg is None else cfg
    if cache is None:
        import pulse_core as pc
        cache = pc.STATE_DIR / "usage.json"
    try:
        st = json.loads(cache.read_text())
    except (OSError, ValueError):
        st = {}
    accts = st.setdefault("accounts", {})
    names = list(cfg.get("owned") or []) + list((cfg.get("spare") or {}).keys())
    for n in names:
        a = accts.setdefault(n, {})
        if now - (a.get("tried_at") or 0) < REFETCH:
            continue
        a["tried_at"] = now
        if not cfg.get("usage_url"):
            a["why"] = "no usage endpoint configured"
            continue
        tok, exp, why = read_token(n)
        if not tok:
            a["why"] = why
            continue
        if exp and exp < now:
            a["why"] = "token expired"   # never refreshed here: that would rotate the account's credentials
            continue
        try:
            body = fetch(cfg["usage_url"], cfg.get("usage_beta", ""), tok)
        except urllib.error.HTTPError as e:
            a["why"] = "token refused (expired)" if e.code in (401, 403) else f"usage endpoint HTTP {e.code}"
            continue
        except (OSError, ValueError) as e:
            a["why"] = f"usage endpoint unreachable ({type(e).__name__})"
            continue
        week = _window(body, "seven_day")
        if not week:
            a["why"] = "the endpoint returned no weekly figure"
            continue
        a.update({"why": "", "measured_at": now, "week": week, "five": _window(body, "five_hour")})
    for n in [k for k in accts if k not in names]:
        del accts[n]
    st["codex"] = read_codex(cfg.get("codex_sessions") or ["~/.codex/sessions"], now) or st.get("codex")
    cache.parent.mkdir(parents=True, exist_ok=True)
    tmp = cache.with_name(f"{cache.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(st, indent=1))
    tmp.replace(cache)
    return panel(st, cfg, now)


def panel(st: dict, cfg: dict, now: float) -> dict:
    """The snapshot's `charts.usage`: one row per account (state measured | stale | unknown) + codex."""
    rows = []
    spare = cfg.get("spare") or {}
    for n in list(cfg.get("owned") or []) + list(spare):
        a = (st.get("accounts") or {}).get(n) or {}
        w = a.get("week")
        state = "unknown" if not w else "measured" if now - (a.get("measured_at") or 0) <= FRESH else "stale"
        rows.append({"name": n, "role": "spare" if n in spare else "owned", "cap": spare.get(n),
                     "state": state, "pct": (w or {}).get("pct"), "resets_at": (w or {}).get("resets_at"),
                     "five_pct": (a.get("five") or {}).get("pct"), "measured_at": a.get("measured_at"),
                     "why": a.get("why") or ""})
    cx = st.get("codex")
    return {"at": now, "accounts": rows, "codex": cx, "evening_from": cfg.get("evening_from", 18),
            "evening_share": cfg.get("evening_share", 0.4)}


def _when(t: float | None, now: float) -> str:
    if not t:
        return "?"
    d = (t - now) / 86400
    return f"{time.strftime('%a %H:%M', time.localtime(t))} (in {d:.1f} d)" if d >= 1 else \
        f"{time.strftime('%a %H:%M', time.localtime(t))} (in {max(0, (t - now) / 3600):.0f} h)"


def _asof(r: dict, now: float) -> str:
    return "" if r["state"] == "measured" else \
        f" - as of {time.strftime('%a %H:%M', time.localtime(r['measured_at']))}, {r['why'] or 'not re-read'} since"


def lines(p: dict | None, now: float) -> list[dict]:
    """[{text, claim}] for the brief/digest. A share or a pace is arithmetic on a measured figure and says
    so; a missing figure is the word "unknown", never 0."""
    if not p:
        return [{"text": "Claude plan usage: unknown (the usage reader has not run)", "claim": {"type": "unknown"}}]
    out = []
    owned = [r for r in p["accounts"] if r["role"] == "owned"]
    ev = float(p.get("evening_share") or 0)
    for r in owned:
        if r["pct"] is None:
            out.append({"text": f"{r['name']}: unknown ({r['why'] or 'no reading'})", "claim": {"type": "unknown"}})
            continue
        left = max(0.0, 100 - r["pct"])
        days = max(0.5, ((r["resets_at"] or now) - now) / 86400)
        share = left / days
        out.append({"text": f"{r['name']}: {r['pct']:.0f}% of the week used, resets {_when(r['resets_at'], now)}; "
                            f"{left:.0f}% left ≈ {share:.0f}%/day, of it {share * ev:.0f}% kept for the evening"
                            + _asof(r, now),
                    "claim": {"type": "usage", "name": r["name"], "pct": r["pct"], "measured_at": r["measured_at"]}})
    known = [r for r in owned if r["pct"] is not None]
    spent = bool(owned) and len(known) == len(owned) and all(r["pct"] >= DEPLETED for r in known)
    for r in (x for x in p["accounts"] if x["role"] == "spare"):
        cap = 100 * float(r["cap"] or 0)
        if r["pct"] is None:
            out.append({"text": f"{r['name']} (spare): unknown ({r['why'] or 'no reading'})", "claim": {"type": "unknown"}})
            continue
        verdict = (f"past the ~{cap:.0f}% line we may use" if r["pct"] >= cap
                   else "not for us yet: the owned accounts are not spent" if not spent
                   else f"usable to ~{cap:.0f}% ({cap - r['pct']:.0f}% left of it)")
        out.append({"text": f"{r['name']} (spare): {r['pct']:.0f}% of the week used by everyone on it, resets "
                            f"{_when(r['resets_at'], now)}; {verdict}" + _asof(r, now),
                    "claim": {"type": "usage", "name": r["name"], "pct": r["pct"], "measured_at": r["measured_at"]}})
    cx = p.get("codex")
    if cx:
        out.append({"text": f"GPT (codex{' ' + cx['plan'] if cx.get('plan') else ''}): {cx['pct']:.0f}% of the week used, "
                            f"resets {_when(cx.get('resets_at'), now)} - as of its last session "
                            f"{time.strftime('%a %H:%M', time.localtime(cx['measured_at']))}",
                    "claim": {"type": "usage", "name": "codex", "pct": cx["pct"], "measured_at": cx["measured_at"]}})
    else:
        out.append({"text": "GPT (codex): unknown (no codex session with a rate-limit record)", "claim": {"type": "unknown"}})
    return out


def check_claim(c: dict, p: dict | None) -> str:
    """The judge's check of a usage line: the monitor's own panel must hold the same reading."""
    if not p:
        return "fail: no usage panel on the monitor"
    if c.get("name") == "codex":
        r = p.get("codex") or {}
    else:
        r = next((x for x in p.get("accounts") or [] if x["name"] == c.get("name")), None) or {}
    if r.get("pct") is None or r.get("pct") != c.get("pct") or r.get("measured_at") != c.get("measured_at"):
        return "fail: the monitor's usage panel holds a different reading"
    return "pass"


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    now = time.time()
    for ln in lines(refresh(now), now):
        print(ln["text"])
