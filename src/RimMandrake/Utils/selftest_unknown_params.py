#!/usr/bin/env python3
"""Selftest for rimbridge_client's unknown-parameter guard.

    python3 src/RimMandrake/Utils/selftest_unknown_params.py

WHY THIS EXISTS
===============
BRIDGE_DROPS_UNKNOWN_PARAMS_1, proven live 2026-08-26: the bridge DISCARDS an
argument key it does not know, silently, and runs the tool on its defaults —
returning `success: true` and a payload that looks right.

    jawa/new_allowed_area {label: "CHECK_correct"}           -> label "CHECK_correct"
    jawa/new_allowed_area {name:  "CHECK_wrong", banana: 42} -> label "Area 3"   success
    jawa/stop_job         {action: "StopAll"}                -> ran `endcurrent`

⛔ The server is RimBridgeServer's, not ours, so the drop cannot be fixed at the
source. The guard is client-side and fires before a byte is sent.

THE FAILURE MODE THIS TEST IS REALLY GUARDING
=============================================
🔑 A guard that cannot read a schema must say **UNCHECKED**, never pass. The
descriptor key holding a tool's schema is not knowable offline, so
`_declared_params` tries several candidates and returns **None** — not an empty
set — when none of them yields keys. An empty set would read as "this tool takes
no arguments" and would reject every correct call; None means "this client could
not look", and `check_params` says so out loud instead of returning a clean answer.

Runs entirely offline against hand-built descriptors. No game, no bridge, no socket.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rimbridge_client import RimBridge, UnknownParameterError    # noqa: E402

# Four descriptor SHAPES, because we do not know which one the live bridge emits
# and the guard has to survive being wrong about that.
DESCRIPTORS = [
    # JSON-Schema under inputSchema — the MCP-conventional shape
    {"name": "jawa/new_allowed_area",
     "inputSchema": {"type": "object", "properties": {"label": {"type": "string"}}}},
    # the snake_case spelling
    {"name": "jawa/stop_job",
     "input_schema": {"properties": {"pawnId": {}, "mode": {}}}},
    # no schema at all -> UNCHECKED, never "takes nothing"
    {"name": "jawa/map_info"},
    # a bare {name: spec} map rather than a JSON-Schema object
    {"name": "jawa/bare_map", "parameters": {"tile": {"type": "integer"}}},
]

# (tool, params, expected)  — the first three rows are the LIVE measurements.
CASES = [
    ("jawa/new_allowed_area", {"label": "ok"},                      "PASS"),
    ("jawa/new_allowed_area", {"name": "wrong", "banana": 42},      "RAISE"),
    ("jawa/stop_job",         {"pawnId": "x", "action": "StopAll"}, "RAISE"),
    ("jawa/stop_job",         {"pawnId": "x", "mode": "StopAll"},   "PASS"),
    ("jawa/map_info",         {},                                   "PASS"),
    ("jawa/map_info",         {"anything": 1},                      "UNCHECKED"),
    ("jawa/not_a_tool",       {"x": 1},                             "UNCHECKED"),
    ("jawa/bare_map",         {"tile": 18393},                      "PASS"),
    ("jawa/bare_map",         {"tileId": 18393},                    "RAISE"),
]


def main():
    rb = RimBridge.__new__(RimBridge)          # no socket, no handshake
    rb._param_index = None
    rb.list_tools = lambda: DESCRIPTORS

    failures = 0
    for tool, params, want in CASES:
        try:
            reason = rb.check_params(tool, params)
            got = "UNCHECKED" if reason else "PASS"
            detail = reason or ""
        except UnknownParameterError as exc:
            got, detail = "RAISE", str(exc)
        ok = got == want
        if not ok:
            failures += 1
        print("%s %-24s %-34s want=%-9s got=%-9s %s"
              % ("ok " if ok else "FAIL", tool, params, want, got, detail[:70]))

    print("\n%d case(s), %d failure(s)" % (len(CASES), failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
