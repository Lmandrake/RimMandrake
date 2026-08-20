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
alt  = float(sys.argv[3]) if len(sys.argv) > 3 else -1.0
v = call("jawa/world_view", show=True, centerTile=tile, altitude=alt, northUp=True)
print("view:", {k: v.get(k) for k in ("worldSelectedAfter", "centeredOn", "altitude")})
# The debug log AUTO-REOPENS on any warning ("Auto-open is ON"), and an open
# dialog obscures or blanks the shot. Closing once is not enough - something
# can log between the close and the capture. Retry until the frame is clean.
DIALOGS = ("LudeonTK.EditWindow_Log", "LudeonTK.Dialog_DevPalette",
           "LudeonTK.Dialog_Debug", "LudeonTK.EditWindow_DebugInspector",
           "LudeonTK.EditWindow_TweakValues")
sh = None
for attempt in range(4):
    for wt in DIALOGS:
        call("rimworld/close_window", windowType=wt)
    call("jawa/clear_ui")
    st = call("rimworld/get_ui_state")
    top = st.get("topWindowType") or ""
    if not any(d in top for d in DIALOGS) and st.get("windowCount", 9) <= 1:
        sh = call("rimworld/take_screenshot", fileName=name, suppressMessage=True)
        break
    time.sleep(0.6)
if sh is None:
    sh = call("rimworld/take_screenshot", fileName=name, suppressMessage=True)
    print("WARNING: could not get a clean frame after 4 tries; a dialog may obscure it")
st = call("rimworld/get_ui_state")
print("windows open at capture:", st.get("windowCount"), st.get("topWindowType"))
print("saved:", sh.get("path") or sh.get("fileName"))
