"""rimdrive.obs_events -- RETIRED (design 08 P5, 2026-10-21). Compatibility shim only.

It was a second per-call bridge recorder that duplicated rimbridge_client's evidence log
(<data root>\\scratch\\bridge_calls.jsonl). Its useful fields -- outcome, timeout, transport --
are now written on every `end` row by rimbridge_client.RimBridge.call, and `telemetry bridge`
reads that log. Every function below keeps its old signature and does nothing: no file is
written, nothing raises. Historic run files under <data root>\\obs\\runs stay readable by
modcheck/obs_summary.py. Do not add new callers.
"""
import os
import time

SCHEMA = 1
DEFAULT_CAPACITY = 20000
RETIRED = True


def default_dir():
    return os.environ.get("OBS_DIR", "")


def new_run_id(label="run"):
    """Still returns a unique run id (run_identity uses it); nothing is recorded under it."""
    return "%s-%s-%d" % (time.strftime("%Y%m%dT%H%M%S"), label, os.getpid())


def install(run_id, directory=None, **kw):
    return None


def uninstall(join_s=1.0):
    return None


def current():
    return None


def call_start(tool):
    return None


def call_end(handle, outcome, reply_success=None, timeout=False):
    return None


def end_exception(handle, e):
    return None


def classify_result(r):
    """-> (outcome, reply_success) for a returned reply."""
    if isinstance(r, dict) and r.get("success") is False:
        return "reply_fail", False
    return "ok", (r.get("success") if isinstance(r, dict) else None)


def classify_exception(e):
    if isinstance(e, TimeoutError) or "timed out" in str(e).lower():
        return "timeout", True
    if isinstance(e, (ConnectionError, OSError)):
        return "reconnected", False
    return "error", False
