#!/usr/bin/env python3
"""Selftest for usage.py (CLAUDE_PLAN_USAGE_MEASURE_A_SOURCE): measured plan usage per account, the budget
rule's lines, and that nothing unmeasured is ever shown as measured. Fixture accounts and a fake endpoint;
no network, no real credentials."""
import atexit
import json
import os
import shutil
import sys
import tempfile
import urllib.error
from pathlib import Path

ROOT = Path(tempfile.mkdtemp(prefix="st_usage_"))
atexit.register(shutil.rmtree, ROOT, True)
os.environ["RM_ACCOUNTS_DIR"] = str(ROOT / "acc")
os.environ["RM_LIVE_CREDS"] = str(ROOT / "live_creds.json")
os.environ["RM_PULSE_STATE"] = str(ROOT / "state")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import usage  # noqa: E402

FAILS = []
NOW = 1_792_900_000.0
DAY = 86400


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)


def creds(path: Path, tok: str, exp: float):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"claudeAiOauth": {"accessToken": tok, "expiresAt": int(exp * 1000)}}))


def iso(t):
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(t))


CFG = {"usage_url": "http://fixture.invalid/usage", "usage_beta": "b", "owned": ["own_a", "own_b"],
       "spare": {"spare_c": 0.5}, "evening_share": 0.4, "codex_sessions": [str(ROOT / "codex")]}
WEEK = {"tok_a": 12.0, "tok_b": 93.0, "tok_c": 30.0}
CALLS = []


def fake(url, beta, tok):
    CALLS.append(tok)
    if tok == "tok_refused":
        raise urllib.error.HTTPError(url, 401, "unauthorized", {}, None)
    return {"five_hour": {"utilization": 5.0, "resets_at": iso(NOW + 3600)},
            "seven_day": {"utilization": WEEK[tok], "resets_at": iso(NOW + 3 * DAY)}}


def main():
    acc = ROOT / "acc"
    acc.mkdir(parents=True)
    (acc / "live.json").write_text(json.dumps({"account": "own_a"}))
    creds(ROOT / "live_creds.json", "tok_a", NOW + 3600)            # the live account reads Claude Code's own file
    creds(acc / "own_a" / ".credentials.json", "stale_vault_tok", NOW - 3600)
    creds(acc / "own_b" / ".credentials.json", "tok_b", NOW + 3600)
    creds(acc / "spare_c" / ".credentials.json", "tok_c", NOW + 3600)
    cache = ROOT / "state" / "usage.json"

    p = usage.refresh(NOW, CFG, fake, cache)
    by = {r["name"]: r for r in p["accounts"]}
    check("the live account is read from the live credentials, not the vault copy", "stale_vault_tok" not in CALLS, CALLS)
    check("each account measured with its own reading", by["own_a"]["pct"] == 12.0 and by["own_b"]["pct"] == 93.0
          and all(r["state"] == "measured" for r in p["accounts"]), by)
    check("no token is ever written to the cache", not any(t in cache.read_text() for t in ("tok_a", "tok_b", "tok_c")))
    ls = usage.lines(p, NOW)
    txt = [ln["text"] for ln in ls]
    check("an owned line gives used, reset and the daily share", txt[0].startswith("own_a: 12% of the week used, resets")
          and "88% left ≈ 29%/day, of it 12% kept for the evening" in txt[0], txt[0])
    check("the spare is not for us while the owned accounts have room",
          "not for us yet" in txt[2] and txt[2].startswith("spare_c (spare): 30%"), txt[2])
    check("no codex record reads unknown, never 0", txt[3].startswith("GPT (codex): unknown"), txt[3])

    # the judge: the line's reading must be the panel's own
    c = ls[0]["claim"]
    check("judge passes a usage line the panel holds", usage.check_claim(c, p) == "pass")
    check("judge withholds a tampered percent", usage.check_claim({**c, "pct": 11.0}, p) != "pass")
    check("judge withholds with no panel", usage.check_claim(c, None) != "pass")

    # at most one call per account per REFETCH
    n = len(CALLS)
    usage.refresh(NOW + 60, CFG, fake, cache)
    check("no re-fetch inside ten minutes", len(CALLS) == n, CALLS)

    # an expired token: no call, the last good reading kept and shown with its age, never as now
    creds(acc / "own_b" / ".credentials.json", "tok_b", NOW + 600)
    creds(acc / "spare_c" / ".credentials.json", "tok_refused", NOW + 9 * 3600)
    later = NOW + 2 * 3600
    creds(ROOT / "live_creds.json", "tok_a", later + 3600)
    CALLS.clear()
    p2 = usage.refresh(later, CFG, fake, cache)
    by2 = {r["name"]: r for r in p2["accounts"]}
    check("an expired token is never sent", "tok_b" not in CALLS, CALLS)
    check("an expired token keeps the last good reading as stale", by2["own_b"]["state"] == "stale"
          and by2["own_b"]["pct"] == 93.0 and by2["own_b"]["why"] == "token expired", by2["own_b"])
    check("a refused token says so", by2["spare_c"]["why"] == "token refused (expired)", by2["spare_c"])
    t2 = [ln["text"] for ln in usage.lines(p2, later)]
    check("a stale reading names its time and why", "- as of" in t2[1] and "token expired since" in t2[1], t2[1])

    # never measured at all: the word unknown
    p3 = usage.panel({"accounts": {"own_a": {"why": "no stored credentials"}}}, CFG, NOW)
    t3 = [ln["text"] for ln in usage.lines(p3, NOW)]
    check("an account with no reading reads unknown with its reason", t3[0] == "own_a: unknown (no stored credentials)", t3)
    check("unknown lines carry no measured claim", usage.lines(p3, NOW)[0]["claim"] == {"type": "unknown"})

    # the spare rule: past its cap, and usable only once both owned are spent
    st = {"accounts": {"own_a": {"week": {"pct": 99.0, "resets_at": NOW + DAY}, "measured_at": NOW},
                       "own_b": {"week": {"pct": 100.0, "resets_at": NOW + DAY}, "measured_at": NOW},
                       "spare_c": {"week": {"pct": 20.0, "resets_at": NOW + DAY}, "measured_at": NOW}}}
    t4 = [ln["text"] for ln in usage.lines(usage.panel(st, CFG, NOW), NOW)]
    check("the spare opens once both owned are spent, to its cap", "usable to ~50% (30% left of it)" in t4[2], t4[2])
    st["accounts"]["spare_c"]["week"]["pct"] = 68.0
    t5 = [ln["text"] for ln in usage.lines(usage.panel(st, CFG, NOW), NOW)]
    check("a spare past its cap says so", "past the ~50% line" in t5[2], t5[2])

    # codex: the last rate_limits record of the newest rollout
    d = ROOT / "codex" / "2026" / "10" / "25"
    d.mkdir(parents=True)
    rec = lambda pct, ts: json.dumps({"timestamp": ts, "type": "event_msg", "payload": {"type": "token_count", "rate_limits": {
        "primary": {"used_percent": pct, "window_minutes": 10080, "resets_at": NOW + 5 * DAY}, "plan_type": "prolite"}}})
    (d / "rollout-x.jsonl").write_text(rec(1.0, "2026-10-26T05:00:00Z") + "\n" + rec(3.0, "2026-10-26T05:15:57.359Z")
                                       + "\n" + json.dumps({"type": "other"}) + "\n")
    cx = usage.read_codex([str(ROOT / "codex")], NOW)
    check("codex reads its last rate-limit record", cx and cx["pct"] == 3.0 and cx["plan"] == "prolite", cx)
    p6 = usage.refresh(NOW + 7 * 3600, CFG, fake, cache)
    t6 = [ln["text"] for ln in usage.lines(p6, NOW + 7 * 3600)]
    check("the codex line says it is as of its last session", t6[-1].startswith("GPT (codex prolite): 3% of the week used")
          and "as of its last session" in t6[-1], t6[-1])

    print(f"\n{'FAILED ' + str(len(FAILS)) if FAILS else 'ALL PASS'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
