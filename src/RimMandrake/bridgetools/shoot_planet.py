import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=120.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
name = sys.argv[1] if len(sys.argv) > 1 else "planet"
tile = int(sys.argv[2]) if len(sys.argv) > 2 else -1
call("jawa/world_view", show=True, centerTile=tile)
# The debug log AUTO-REOPENS on any error, and an open dialog blanks/obscures
# the shot. Close everything immediately before the capture, not earlier.
for wt in ("LudeonTK.EditWindow_Log", "LudeonTK.Dialog_DevPalette",
           "LudeonTK.Dialog_Debug", "LudeonTK.EditWindow_DebugInspector"):
    call("rimworld/close_window", windowType=wt)
call("jawa/clear_ui")
time.sleep(0.4)
sh = call("rimworld/take_screenshot", fileName=name, suppressMessage=True)
st = call("rimworld/get_ui_state")
print("windows open at capture:", st.get("windowCount"), st.get("topWindowType"))
print("saved:", sh.get("path") or sh.get("fileName"))
