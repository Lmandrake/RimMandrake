"""contracts.compat -- the COMPAT acceptance rules, STDLIB ONLY (the dispatcher tick imports these; the testq tick
runs every 60 s). Each reproduces, exactly, the rule its reader applied before contracts existed, so wiring changes no
decision. The strict contracts are in contracts.models (pydantic);
contracts.replay runs both over real stores and lists every disagreement.
"""
import datetime
import re

TESTQ_RESULT_SCHEMA = "testq.result/1"


def testq_result_readable(res):
    """testq.py's rule before it uses a worker result: only the schema tag (testq.py collect / orphans)."""
    return isinstance(res, dict) and res.get("schema") == TESTQ_RESULT_SCHEMA


def sessions_ok(data):
    """dispatcher.sessions_ok: a list whose every entry is an object (review dispatcher-full #5)."""
    return isinstance(data, list) and all(isinstance(x, dict) for x in data)


def ledger_ts(ev):
    """THE comparison operand of dispatcher.seat_events_since: `ev.get("ts") or ""`. Shared, so the guard below
    validates exactly the value the consumer compares (review contracts #9): a falsey ts (null, 0, false, [], {})
    becomes "" in both places and sorts before every cutoff; a truthy non-string ts is refused.
    A valid ISO instant is returned as UTC whole seconds "YYYY-MM-DDTHH:MM:SSZ" (review night): the guard accepts an
    offset or a fraction, and as raw text "12:00:00+02:00" sorted after "11:00:00Z" and "12:00:01.5Z" before
    "12:00:01Z". Anything else is returned unchanged for the guard to refuse."""
    ts = ev.get("ts") or ""
    if isinstance(ts, str) and iso_ts_ok(ts):
        dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return ts


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
