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
    user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
    time.sleep(0.06)
    user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
    return x, y

layout = call("rimworld/get_ui_layout")
els = layout["surfaces"][1]["elements"]
close_btn = None
for e in els:
    if e.get("label") == "Close":
        close_btn = e
        break
print("close button:", close_btn)
sr = close_btn["screenRect"]
cx, cy = sr["x"] + sr["width"]/2, sr["y"] + sr["height"]/2
print("clicking close at ui-space", cx, cy, "-> os", os_click_ui(cx, cy))

time.sleep(0.6)
st = call("rimworld/get_ui_state")
print("windowCount after close:", st.get("windowCount"), "topWindowType:", st.get("topWindowType"))

call("rimworld/take_screenshot", fileName="rimthemes_main_menu_after.png")
print("screenshot done")
