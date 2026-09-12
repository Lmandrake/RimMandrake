#!/usr/bin/env python3
"""bridge_latency_bench.py — measure what DRIVING the bridge actually costs.

READ-ONLY: rimbridge/ping, rimworld/get_game_info, tools/list only. No mutations.

Separates the three taxes a bridge action can pay:
  A. process spawn        (python.exe started fresh from WSL per action)
  B. connection setup     (TCP connect + session/hello, + tools/list if guarded)
  C. the call itself      (persistent connection, per-call round trip)

The point: C is milliseconds; A+B are paid per PROCESS, and an LLM-in-the-loop
driver pays A+B (plus its own thinking time) for every handful of calls, where
a deterministic script pays them once per session.

Run FROM WINDOWS PYTHON (the bridge binds Windows loopback):
    cd /mnt/d/Luke/dev/Rimworld && python.exe src/RimMandrake/Utils/bridge_latency_bench.py

Per the rimbridge skill's rule, every number is printed WITH its conditions
(mod count is not read here — record it beside the output when you quote it;
ticksGame and map come from get_game_info on the same connection).
"""

import json
import statistics
import subprocess
import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rimbridge_client import RimBridge, resolve_endpoint, RimBridgeError  # noqa: E402


def stats(ms):
    return {
        "n": len(ms),
        "min_ms": round(min(ms), 2),
        "median_ms": round(statistics.median(ms), 2),
        "p90_ms": round(sorted(ms)[int(len(ms) * 0.9) - 1], 2) if len(ms) >= 10 else None,
        "max_ms": round(max(ms), 2),
    }


def timed(fn, n, settle=None):
    out = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        out.append((time.perf_counter() - t0) * 1000.0)
        if settle:
            time.sleep(settle)
    return out


def main():
    host, port, token = resolve_endpoint()
    if not token:
        print("no token — is the game up?", file=sys.stderr)
        return 2
    report = {"conditions": {}, "A_process_spawn": {}, "B_connection_setup": {},
              "C_per_call_persistent": {}}

    # --- A. bare interpreter spawn (the floor under every fresh-process action)
    def spawn_noop():
        subprocess.run([sys.executable, "-c", "pass"], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report["A_process_spawn"]["bare_interpreter"] = stats(timed(spawn_noop, 5))

    me = os.path.abspath(__file__)

    def spawn_connect_ping():
        subprocess.run([sys.executable, me, "--one-ping"], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report["A_process_spawn"]["fresh_process_connect_ping"] = stats(timed(spawn_connect_ping, 5))

    # --- B. connection setup, measured inside one process
    def connect_close():
        rb = RimBridge(host, port, token, timeout=15.0)
        rb.connect()
        rb.close()
    report["B_connection_setup"]["tcp_plus_hello"] = stats(timed(connect_close, 5))

    rb = RimBridge(host, port, token, timeout=15.0)
    rb.connect()
    t0 = time.perf_counter()
    tools = rb.list_tools()
    report["B_connection_setup"]["tools_list_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    report["B_connection_setup"]["tools_count"] = len(tools)

    # --- conditions, from the same connection
    try:
        info = rb.call("rimworld/get_game_info")
        report["conditions"] = {k: info.get(k) for k in
                                ("ticksGame", "mapCount", "colonistCount", "gameSpeed",
                                 "storyteller", "currentMap")} | {"raw_keys": sorted(info)[:20]}
    except RimBridgeError as ex:
        report["conditions"] = {"get_game_info": "FAILED: %s" % ex}

    # --- C. per-call cost on the persistent connection
    report["C_per_call_persistent"]["ping"] = stats(
        timed(lambda: rb.call("rimbridge/ping"), 100))
    report["C_per_call_persistent"]["get_game_info_main_thread"] = stats(
        timed(lambda: rb.call("rimworld/get_game_info"), 30))
    report["C_per_call_persistent"]["get_game_info_spaced_250ms"] = stats(
        timed(lambda: rb.call("rimworld/get_game_info"), 10, settle=0.25))
    rb.close()

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    if "--one-ping" in sys.argv:
        h, p, t = resolve_endpoint()
        with RimBridge(h, p, t, timeout=15.0) as rb:
            rb.call("rimbridge/ping")
        sys.exit(0)
    sys.exit(main())
