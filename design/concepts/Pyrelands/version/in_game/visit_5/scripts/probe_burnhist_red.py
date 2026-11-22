"""Acceptance test of RIMMANDRAKE_FIX_PYRE_BURN_HISTORY_PROBE_COUNTS_BEFORE_IT_PRUNES (live, any Pyrelands map with a burn
history, a scratch map only: it backdates the map's burn history). Reads ProbeBurnHistory(0), backdates every sample past
BurnHistoryKeepTicks (600000), reads ProbeBurnHistory(0) again. PASS (exit 0) when the second read answers (samples=0);
FAIL (exit 1) when it throws; UNMEASURED (exit 2) when the map has no history to prune or a call cannot be made."""
import json, os, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils", "modcheck"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
import clockgate  # noqa: E402
T = "RimMandrake.Pyrelands.MapComponent_BurnLine"
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as raw:
    def call(name, **kw):
        return clockgate._unwrap(raw.call(name, kw))
    a = call("jawa/static_call", type=T, method="ProbeBurnHistory", args="0") or {}
    print("BEFORE", json.dumps({k: a.get(k) for k in ("success", "result", "message")})[:400])
    if a.get("success") is False or "samples=0" in str(a.get("result")) or "samples=" not in str(a.get("result")):
        print("UNMEASURED: no burn history to prune on this map"); sys.exit(2)
    b = call("jawa/static_call", type=T, method="BackdateBurnHistory", args="700000") or {}
    print("BACKDATE", json.dumps({k: b.get(k) for k in ("success", "result", "message")})[:300])
    c = call("jawa/static_call", type=T, method="ProbeBurnHistory", args="0") or {}
    print("AFTER", json.dumps({k: c.get(k) for k in ("success", "result", "message")})[:400])
    if c.get("success") is False:
        print("FAIL: ProbeBurnHistory threw after its own prune emptied the history"); sys.exit(1)
    print("PASS"); sys.exit(0)
