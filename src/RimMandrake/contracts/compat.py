"""contracts.compat -- the COMPAT acceptance rules, STDLIB ONLY (the dispatcher tick imports these through
arbiter_pending/role_launch; the testq tick runs every 60 s). Each reproduces, exactly, the rule its reader applied
before contracts existed, so wiring changes no decision. The strict contracts are in contracts.models (pydantic);
contracts.replay runs both over real stores and lists every disagreement.
"""
import datetime
import re

DISPOSITIONS = ("PASS", "CONDITIONAL-PASS", "FAIL-module", "FAIL-check", "RESTART-environment", "BAR-defect",
                "UNRESOLVED")
TESTQ_RESULT_SCHEMA = "testq.result/1"


def truthy_problems(d, need):
    """arbiter_pending.read_jsonl's rule: a JSON object whose every `need` field is truthy."""
    if not isinstance(d, dict):
        return ["not a JSON object"]
    return ["%s missing or empty" % k for k in need if not d.get(k)]


def verdict_row_problems(d):
    """arbiter_pending.read_stores' verdict rule: item/sha/disposition truthy, disposition one of DISPOSITIONS."""
    p = truthy_problems(d, ("item", "sha", "disposition"))
    if not p and d["disposition"] not in DISPOSITIONS:
        p.append("disposition %r is not one of %s" % (d["disposition"], "/".join(DISPOSITIONS)))
    return p


def tiers_row_problems(d):
    """arbiter_pending's tiers_history rule: item/sha/decision truthy."""
    return truthy_problems(d, ("item", "sha", "decision"))


def testq_result_readable(res):
    """testq.py's rule before it uses a worker result: only the schema tag (testq.py collect / orphans)."""
    return isinstance(res, dict) and res.get("schema") == TESTQ_RESULT_SCHEMA


def sessions_ok(data):
    """dispatcher.sessions_ok: a list whose every entry is an object (review dispatcher-full #5)."""
    return isinstance(data, list) and all(isinstance(x, dict) for x in data)


def ledger_ts(ev):
    """THE comparison operand of dispatcher.seat_events_since: `ev.get("ts") or ""`. Shared, so the guard below
    validates exactly the value the consumer compares (review contracts #9): a falsey ts (null, 0, false, [], {})
    becomes "" in both places and sorts before every cutoff; a truthy non-string ts is refused."""
    return ev.get("ts") or ""


_ISO_OFFSET = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(Z|[+-]\d\d:\d\d)")


def iso_ts_ok(ts):
    """True when ts is an ISO-8601 instant with a Z/offset that is a real date and time (the contracts.models.IsoOffset
    rule, stdlib only). fullmatch: a trailing newline is not ISO."""
    if not isinstance(ts, str) or not _ISO_OFFSET.fullmatch(ts):
        return False
    try:
        datetime.datetime.fromisoformat(ts)
    except ValueError:
        return False
    return ts[11:13] != "24" and (ts[-1] == "Z" or ts[-2:] < "60")


def ledger_event_usable(ev):
    """dispatcher.seat_events_since: an object whose ts operand (ledger_ts) is "" (no ts: sorts before every cutoff)
    or an ISO-8601 instant. A non-string ts crashed the tick before contracts; a non-ISO string ('yesterday') sorted
    after every cutoff and counted as NEW (LEDGER_TS_HARDEN_NONISO_AFTER_CUTOFF): both are now passed over."""
    if not isinstance(ev, dict):
        return False
    ts = ledger_ts(ev)
    return ts == "" or iso_ts_ok(ts)
