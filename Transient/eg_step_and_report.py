import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

def step(n, timeout_s=25):
    try:
        with RimBridge(host, port, token, timeout=timeout_s) as rb:
            r = rb.call("rimworld/step_game_ticks", {"ticks": n, "timeoutMs": (timeout_s - 3) * 1000})
            print("step result:", r.get("success"), r.get("message"))
    except Exception as e:
        print("step exc (connection dropped, fresh conn next):", e)

def report():
    with RimBridge(host, port, token) as rb:
        g = rb.call("rimworld/get_game_info", {})
        path2 = "Actions" + chr(92) + "Report state (current map)"
        r2 = rb.call("rimworld/execute_debug_action", {"path": path2})
        logs = (r2.get("effects") or {}).get("logs")
        print("ticksGame:", g.get("ticksGame"), "|", logs[0]["message"] if logs else None)

for i in range(4):
    step(1200)
    time.sleep(1)
    report()
