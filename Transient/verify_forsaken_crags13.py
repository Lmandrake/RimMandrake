"""Advance time toward night via step_game_ticks, checking progress."""
import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    t0 = time.time()
    r = rb.call("rimworld/step_game_ticks", {"ticks": 25000})
    print("step result:", json.dumps(r)[:400], "wall:", time.time() - t0)
