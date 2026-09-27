"""Prove rimworld/start_debug_game_ready reaches a real Playing map (DEBUG_GAME_READY_WORLDUI_CRASH_1).
Run under Windows python.exe from the repo root. Exit 0 = Playing with a world, 1 = not."""
import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0); S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

t0 = time.time()
r = call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
print("start_debug_game_ready:", json.dumps(r)[:400])
st = {}
for _ in range(90):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing": break
    time.sleep(1)
print("programState:", st.get("programState"), "after %.0fs" % (time.time() - t0))
gi = call("rimworld/get_game_info")
print("get_game_info:", json.dumps(gi)[:400])
ok = st.get("programState") == "Playing" and gi.get("hasCurrentGame") is not False
sys.exit(0 if ok else 1)
