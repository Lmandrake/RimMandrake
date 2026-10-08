import sys, json, re, time
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rbc
host, port, token = rbc.resolve_endpoint()
LOG = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
def rep(rb):
    rb.call("rimworld/execute_debug_action", {"path": "Actions\\Report ledge refuge (current map)"}, check=False)
    time.sleep(1.5)
    for l in reversed(open(LOG, errors="ignore").read().splitlines()):
        if "[RMFloodedCanyonDebug] refuge:" in l: return int(re.search(r"carvingReaders=(\d+)", l).group(1))
pid="Human163813"
with rbc.RimBridge(host, port, token, timeout=180.0) as rb:
    print("before", rep(rb))
    rb.call("jawa/set_draft", {"pawnId": pid, "drafted": True}, check=False)
    print(str(rb.call("jawa/order_pawn", {"pawnId": pid, "x": 187, "z": 95, "waitTicks": 600}, check=False))[:150])
    for i in range(3):
        rb.call("rimworld/step_game_ticks", {"ticks": 600}, check=False)
        lp = [p for p in rb.call("jawa/list_pawns", {"limit": 300}, check=False)["pawns"] if p["id"]==pid][0]
        print("pos", lp["x"], lp["z"], "readers", rep(rb))
    r = rb.call("jawa/pawn_get", {"pawnId": pid, "includeNeeds": True}, check=False)
    s=json.dumps(r); i=s.find("ercy"); print("mercy mention:", s.count("ercy"), s[max(0,i-100):i+200] if i>=0 else "")
    ms = rb.call("jawa/list_pawns", {"includeHealth": True, "limit": 300}, check=False)
