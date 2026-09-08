"""Advance time in a loop until night (or a cap), checking hour via screenshot text is
slow -- instead check via the debug-action-based state string. We just loop step_game_ticks."""
import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

TARGET_TOTAL = 42000  # ~16.8 game hours from tick 1 (6AM) -> should reach ~10-11PM

with RimBridge(host, port, token, timeout=60.0) as rb:
    total = 0
    while total < TARGET_TOTAL:
        remaining = TARGET_TOTAL - total
        batch = min(4000, remaining)
        r = rb.call("rimworld/step_game_ticks", {"ticks": batch})
        adv = r.get("advancedTicks", 0)
        total += adv
        print("advanced", adv, "total", total, "endTicksGame", r.get("endTicksGame"), "status", r.get("status"))
        if adv == 0:
            print("no progress, stopping")
            break
    print("FINAL total advanced:", total)
