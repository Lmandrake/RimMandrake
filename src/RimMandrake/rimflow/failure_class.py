#!/usr/bin/env python3
"""failure_class.py -- the one answer to "does this outcome count against the work?" (a check, a trial, a run, a retry).

Item RIMMANDRAKE_SHARE_ONE_FAILURE_CLASSIFIER_EVERY_COUNTER_ROLLED_ITS_OWN; page
design/specs/2026-11-23-one-failure-classifier/boundary.md; tests selftest_failure_class.py. The rule: no trial, turn,
look, cycle or retry is spent by a run that was killed, timed out, refused or never started, or whose outcome is not the
work's own (standing_rulings.md §No trial is spent by a system failure, §Live tests have three kinds). Every counter that
stops, gives up, escalates or files something asks here; Utils/failure_counter_lint.py refuses a new one that does not.

    read(word, why="")            -> Reading, from one of the words below
    of_row(row, spec=None)        -> Reading, from a rows.jsonl row
    of_run(rec, runner=None)      -> Reading, from a detached run record
    of_launch(text)               -> Reading, from the text of a launch that did not start
    of_testq(rec, chain=None)     -> Reading, from a finished testq record (one chain of it, or the whole job)
    of_error(text)                -> Reading, from the error text of our own tool
    of_artpipe(manifest)          -> Reading, from an art render's manifest
    count(readings)               -> (n that count, {word: n} of the failures left out)

An outcome nobody can class does NOT count, and its Reading says so (classed False, the word in `why`). Pure: no file is
written, and none is read except through run_void.system_cause (a unit's live state)."""
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import live_kinds as LK  # noqa: E402

KILLED, TIMED_OUT, REFUSED, NEVER_STARTED = "KILLED", "TIMED OUT", "REFUSED", "NEVER STARTED"
STOPPED, ACCOUNT, ENDED, BAD_REQUEST = "STOPPED", "ACCOUNT LIMIT", "ENDED", "BAD REQUEST"
UNCLASSED = "UNCLASSED"
COUNTS = (LK.MOD_FAILURE, ENDED, BAD_REQUEST)
SYSTEM = (KILLED, TIMED_OUT, REFUSED, NEVER_STARTED, STOPPED, ACCOUNT)
NOT_COUNTED = (LK.SUCCESS, LK.RANDOM_MISS, LK.ENVIRONMENT, LK.APPARATUS, LK.UNRESOLVED, LK.NO_LOOK) + SYSTEM
WORDS = COUNTS + NOT_COUNTED
# a testq cause about the job itself: the same job sent again is refused again
BAD_REQUEST_CAUSES = ("PREFLIGHT", "BLOCKED_SELECTION", "SCHEMA")
OUR_INVALID_CAUSES = ("CANARY", "HARNESS", "DEPLOY", "SYNC", "GUARD_HELD")

Reading = collections.namedtuple("Reading", "counts word why classed")


def read(word, why=""):
    w = LK.norm(word) if isinstance(word, str) else ""
    if w in WORDS:
        return Reading(w in COUNTS, w, why, True)
    return Reading(False, UNCLASSED, "outcome %r is none of %s%s" % (
        word, ", ".join(WORDS), "; %s" % why if why else ""), False)


def of_row(row, spec=None):
    """A row's outcome word when it carries one, else its verdict and class as the exit reads an old row."""
    if not isinstance(row, dict):
        return read(None, "the row is a %s, not a record" % type(row).__name__)
    w, why = LK.outcome(row, spec)
    if w == LK.REFUSED:         # live_kinds' word for a row whose words cannot be read; not the run word REFUSED
        return read("row words refused", why)
    if w is not None:
        return read(w, why or "")
    v, c = LK.norm(row.get("verdict")), LK.norm(row.get("class"))
    if v == "PASS":
        return read(LK.SUCCESS)
    if v == "FAIL" and c in LK.WRONG:
        return read(LK.APPARATUS, "FAIL with class %s" % c)
    if v == "FAIL":
        return read(LK.MOD_FAILURE)
    if v in ("UNMEASURED", "NOT RUN", "SKIP"):
        return read(LK.NO_LOOK, v)
    return read(v or None, "the row's verdict")


def of_run(rec, runner=None):
    if not isinstance(rec, dict):
        return read(None, "no run record")
    import run_void as RV
    cause = RV.system_cause(rec, runner) if runner else RV.system_cause(rec)
    if cause:
        res = str(rec.get("result") or "")
        never = rec.get("status") == "launch_failed" or rec.get("state") == "launch_failed"
        return read(NEVER_STARTED if never else TIMED_OUT if res.startswith("timeout") else KILLED, cause)
    if rec.get("status") == "refused":
        return read(REFUSED, str(rec.get("result") or ""))
    if rec.get("status") == "finished" and rec.get("result"):
        return read(ENDED, str(rec.get("result")))
    return read(None, "run %s: status %r, result %r" % (rec.get("unit"), rec.get("status"), rec.get("result")))


def of_launch(text):
    """A launch that did not start never ran the work, whatever refused it."""
    return read(NEVER_STARTED, " ".join(str(text or "no text").split()))


def of_error(text):
    """The error text of our own tool. A crash or a timeout of the tool is not the record's fault; a refusal the tool
    gave on reading the record is."""
    t = " ".join(str(text or "").split())
    low = t.lower()
    if "timeoutexpired" in low or "timed out" in low:
        return read(TIMED_OUT, t)
    if low.startswith("crash:") or "traceback (most recent call last)" in low or "could not read" in low \
            or "index.lock" in low:
        return read(LK.APPARATUS, t)
    return read(BAD_REQUEST, t) if t else read(None, "no error text")


def of_testq(rec, chain=None):
    rec = rec if isinstance(rec, dict) else {}
    res = rec.get("result") if isinstance(rec.get("result"), dict) else {}
    out, cause = res.get("outcome"), res.get("cause")
    said = "%s%s" % (out, "/%s" % cause if cause else "")
    if rec.get("cancelled"):
        return read(STOPPED, "cancelled")
    if out == "DONE":
        rows = [r for r in res.get("rows") or [] if isinstance(r, dict) and (chain is None or r.get("chain") == chain)]
        v = {r.get("verdict") for r in rows}
        if "FAIL" in v:
            return read(LK.MOD_FAILURE, said)
        return read(LK.SUCCESS, said) if "PASS" in v else read(LK.NO_LOOK, "%s, no PASS or FAIL row%s" % (
            said, " of %s" % chain if chain else ""))
    if out in ("REFUSED", "INVALID") and cause in BAD_REQUEST_CAUSES:
        return read(BAD_REQUEST, said)
    if out == "REFUSED":
        return read(REFUSED, said)
    if out == "INTERRUPTED":
        return read(KILLED, said)
    if out == "INVALID":
        if cause in OUR_INVALID_CAUSES:
            return read(LK.APPARATUS, said)
        klass = _invalid_class(res)
        return read(LK.APPARATUS if klass in ("TEST", "DELIVERY") else LK.UNRESOLVED, "%s (%s)" % (said, klass))
    return read(None, "testq outcome %s" % said)


def _invalid_class(res):
    d = os.path.join(HERE, "..", "Utils", "testq")
    if d not in sys.path:
        sys.path.append(d)
    try:
        import invalid_class as IC
        return IC.classify(res)[0]
    except Exception as e:  # noqa: BLE001 - could not class it: UNRESOLVED, with the cause in the Reading
        return "UNKNOWN: %s: %s" % (type(e).__name__, e)


# artpiped's worker_status: a picture judged on its merits counts; a worker, a master or the account that failed does not
_ARTPIPE = {"ok": LK.SUCCESS, "worker_error": LK.APPARATUS, "master_failed": LK.APPARATUS, "rate_limited": ACCOUNT,
            "worker_reported_fail": ENDED, "failed_canon": ENDED, "placeholder_output": ENDED, "size_mismatch": ENDED,
            "bad_job_file": BAD_REQUEST}


def of_artpipe(man):
    """A finished artpipe manifest."""
    if not isinstance(man, dict):
        return read(None, "no manifest that can be read")
    if man.get("timed_out"):
        return read(TIMED_OUT, str(man.get("note") or ""))
    ws = man.get("worker_status")
    return read(_ARTPIPE.get(ws), "worker_status %r" % (ws,))


def count(readings):
    """-> (how many count, {word: n} of those left out, successes not listed)."""
    n, left = 0, collections.Counter()
    for r in readings:
        if r.counts:
            n += 1
        elif r.word != LK.SUCCESS:
            left[r.word] += 1
    return n, dict(left)


def named(left):
    """-> "2 KILLED, 1 REFUSED" for a report line, "" for none."""
    return ", ".join("%d %s" % (n, w) for w, n in sorted((left or {}).items()))
