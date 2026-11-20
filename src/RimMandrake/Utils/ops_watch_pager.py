#!/usr/bin/env python3
"""ops_watch_pager.py — the pager's readings for the ops digest (ops_watch family `pager`). Read only.

pager.py (item RIMMANDRAKE_DESIGN_PUSHOVER_ALERTS_CRITICAL_ONLY_TWO_SENDERS) writes <pager dir>/state.json and
log.jsonl. These points put a page that could not leave, and refused callers, into digest.md, which Operations reads:
    pager.could_not_send   faults whose page has not left yet (a failing streak); 0 = none
    pager.refused_24h      refused send attempts in 24 h (a helper or seat that tried to page him)
    pager.sent_7d          pages that reached Pushover in 7 days
No state file and no log is a measured 0 (nothing was ever attempted); a torn file is UNMEASURED, never 0.
Selftest: selftest_pager.py (t_could_not_send_is_visible).
"""
import datetime as dt
import json
import os


def _M(v, unit, **x):
    p = {"v": v, "m": "MEASURED", "unit": unit}
    if x:
        p["x"] = x
    return p


def _U(why, unit):
    return {"v": None, "m": "UNMEASURED", "why": why, "unit": unit}


def _t(s):
    try:
        return dt.datetime.strptime(str(s), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except (TypeError, ValueError):
        return None


def points(pager_dir, now):
    """-> {key: point}. `now` is an aware datetime."""
    out = {}
    sp = os.path.join(pager_dir, "state.json")
    try:
        with open(sp, encoding="utf-8") as f:
            s = json.load(f)
        if not isinstance(s, dict) or not isinstance(s.get("failing"), dict):
            raise ValueError("not a pager state")
        fl = s["failing"]
        out["pager.could_not_send"] = _M(len(fl), "faults whose page has not left",
                                         keys=sorted(fl)[:5], since=min((v.get("since") or "" for v in fl.values()),
                                                                        default=None))
    except FileNotFoundError:
        out["pager.could_not_send"] = _M(0, "faults whose page has not left", cause="no page ever attempted")
    except (OSError, ValueError) as e:
        out["pager.could_not_send"] = _U("%s unreadable: %s" % (sp, e), "faults whose page has not left")
    lp = os.path.join(pager_dir, "log.jsonl")
    refused = sent = torn = 0
    try:
        with open(lp, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except ValueError:
                    torn += 1
                    continue
                t = _t(r.get("at"))
                if t is None:
                    torn += 1
                    continue
                age = (now - t).total_seconds()
                if r.get("outcome") == "REFUSED" and age <= 86400:
                    refused += 1
                if r.get("outcome") == "SENT" and age <= 7 * 86400:
                    sent += 1
        out["pager.refused_24h"] = _M(refused, "refused send attempts, 24 h", torn_lines=torn)
        out["pager.sent_7d"] = _M(sent, "pages accepted by Pushover, 7 d", torn_lines=torn)
    except FileNotFoundError:
        out["pager.refused_24h"] = _M(0, "refused send attempts, 24 h", cause="no log yet")
        out["pager.sent_7d"] = _M(0, "pages accepted by Pushover, 7 d", cause="no log yet")
    except OSError as e:
        out["pager.refused_24h"] = _U("%s unreadable: %s" % (lp, e), "refused send attempts, 24 h")
        out["pager.sent_7d"] = _U("%s unreadable: %s" % (lp, e), "pages accepted by Pushover, 7 d")
    return out
