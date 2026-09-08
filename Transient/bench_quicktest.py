import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

# 1. Fire the quicktest; the response is expected to outlive the client timeout.
try:
    with RimBridge(host, port, token) as rb:
        r = rb.call("rimworld/start_debug_game_ready")
        print("START returned in time:", json.dumps(r)[:200])
except Exception as e:
    print("START call desynced as documented:", type(e).__name__, str(e)[:120])

# 2. Fresh connection; poll until a map exists (plan for >1 min on full stack).
deadline = time.time() + 240
ready = False
while time.time() < deadline and not ready:
    time.sleep(15)
    try:
        with RimBridge(host, port, token) as rb:
            r = rb.call("jawa/list_pawns", {})
            txt = json.dumps(r)
            if "No current map" in txt or '"status": "no_game"' in txt:
                print("poll: no map yet")
            else:
                ready = True
                print("MAP READY; pawns reply head:", txt[:300])
    except Exception as e:
        print("poll error:", type(e).__name__, str(e)[:100])

if not ready:
    print("TIMED OUT waiting for map")
    sys.exit(1)

# 3. List tool names relevant to selection/screenshots/UI.
with RimBridge(host, port, token) as rb:
    tools = rb.call("rimbridge/list_tools")
    names = []
    txt = json.dumps(tools)
    d = tools.get("tools") or tools.get("result") or tools
    if isinstance(d, list):
        names = [t.get("name", str(t)) if isinstance(t, dict) else str(t) for t in d]
    else:
        import re
        names = re.findall(r'"([a-z]+/[a-z_0-9]+)"', txt)
    hits = sorted({n for n in names if any(k in n for k in
        ("screenshot", "select", "ui", "window", "menu", "gizmo", "click", "pawn_list", "colonist"))})
    print("RELEVANT TOOLS:")
    for n in hits:
        print("  ", n)
