import ctypes
from ctypes import wintypes
import sys, json, time

ctypes.windll.shcore.SetProcessDpiAwareness(2)
user32 = ctypes.windll.user32
hwnd = user32.FindWindowW(None, "RimWorld by Ludeon Studios")
origin = wintypes.POINT(0, 0)
user32.ClientToScreen(hwnd, ctypes.byref(origin))
user32.SetForegroundWindow(hwnd)
time.sleep(0.2)

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

def os_click_ui(ui_x, ui_y):
    x = int(origin.x + ui_x)
    y = int(origin.y + ui_y)
    user32.SetCursorPos(x, y)
    time.sleep(0.12)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.06)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    return x, y

def find_in_any_surface(layout, label):
    for surf in layout.get("surfaces", []):
        els = surf.get("elements", [])
        for i, e in enumerate(els):
            if e.get("label") == label:
                return els, i
    return None, None

st = call("rimworld/get_ui_state")
print("windows before:", [(w.get("type")) for w in st.get("windows", [])])
for w in st.get("windows", []):
    if w.get("type") == "LudeonTK.EditWindow_Log":
        call("rimworld/close_window", windowType="LudeonTK.EditWindow_Log")
        print("closed stray debug log window")

print(call("rimworld/open_window_by_type", windowType="aRandomKiwi.RimThemes.Dialog_ThemesList", replaceExisting=True).get("success"))
time.sleep(0.4)

layout = call("rimworld/get_ui_layout")
els, idx = find_in_any_surface(layout, "Cyberpunk")
if els is None:
    all_labels = [e.get("label") for surf in layout.get("surfaces", []) for e in surf.get("elements", []) if e.get("label")]
    print("Cyberpunk not found; labels seen:", all_labels)
    sys.exit(1)
target = els[idx + 2]
sr = target["screenRect"]
cx, cy = sr["x"] + sr["width"]/2, sr["y"] + sr["height"]/2
print("clicking Cyberpunk select icon at", os_click_ui(cx, cy))
time.sleep(0.5)

# close the dialog
layout2 = call("rimworld/get_ui_layout")
els2, idx2 = find_in_any_surface(layout2, "Close")
sr2 = els2[idx2]["screenRect"]
print("clicking Close at", os_click_ui(sr2["x"] + sr2["width"]/2, sr2["y"] + sr2["height"]/2))
time.sleep(0.5)

print("starting debug game...")
r = call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
print("start result:", r.get("success"), r.get("message"))
for i in range(60):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing":
        print("Playing after", i, "s")
        break
    time.sleep(1)

cols = call("rimworld/list_colonists", currentMapOnly=True)
c0 = cols["colonists"][0]
call("rimworld/select_pawn", pawnId=c0["pawnId"])
time.sleep(0.3)
r = call("rimworld/take_screenshot", fileName="rimtheme_cyberpunk_gizmo.png")
print("cyberpunk gizmo screenshot:", r.get("success"))
