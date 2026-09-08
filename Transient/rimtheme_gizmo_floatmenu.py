import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

print("starting debug game...")
r = call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
print("start result success:", r.get("success"), r.get("message"))

for i in range(120):
    st = call("rimworld/get_ui_state")
    ps = st.get("programState")
    if ps == "Playing":
        print("Playing after", i, "s")
        break
    time.sleep(1)
else:
    print("never reached Playing, last state:", ps)

cols = call("rimworld/list_colonists", currentMapOnly=True)
print("list_colonists keys:", list(cols.keys()) if isinstance(cols, dict) else type(cols))
clist = cols.get("colonists") or cols.get("pawns") or cols.get("results") or []
print("colonist count:", len(clist))
if clist:
    print("first colonist raw:", json.dumps(clist[0])[:400])

call("rimworld/set_fog", action="unfogAll")
