import ctypes
from ctypes import wintypes
import sys, json, time

# Must set DPI awareness BEFORE any geometry queries, or Windows silently
# virtualizes coordinates at 96 DPI and every computed screen point is wrong.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PER_MONITOR_AWARE
except Exception as e:
    print("SetProcessDpiAwareness failed:", e)

user32 = ctypes.windll.user32

hwnd = user32.FindWindowW(None, "RimWorld by Ludeon Studios")
if not hwnd:
    sys.exit("RimWorld window not found")
print("hwnd:", hwnd)

rect = wintypes.RECT()
user32.GetWindowRect(hwnd, ctypes.byref(rect))
print("window rect:", rect.left, rect.top, rect.right, rect.bottom)

crect = wintypes.RECT()
user32.GetClientRect(hwnd, ctypes.byref(crect))
print("client size:", crect.right, crect.bottom)

origin = wintypes.POINT(0, 0)
user32.ClientToScreen(hwnd, ctypes.byref(origin))
print("client origin (screen coords):", origin.x, origin.y)

user32.SetForegroundWindow(hwnd)
time.sleep(0.3)

sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r

print(call("rimworld/open_window_by_type", windowType="aRandomKiwi.RimThemes.Dialog_ThemesList", replaceExisting=True))
time.sleep(0.4)

layout = call("rimworld/get_ui_layout")
els = layout["surfaces"][1]["elements"]
target = None
for i, e in enumerate(els):
    if e.get("label") == "Utinni Shell":
        target = els[i + 2]
        break
if not target:
    sys.exit("could not find Utinni Shell select icon in layout")
sr = target["screenRect"]
print("target UI-space screenRect:", sr)

# UI-space (game render pixels) -> logical screen pixels: divide by the
# render-to-client scale, then offset by the client origin.
scale_x = 2364.0 / crect.right
scale_y = 1205.0 / crect.bottom
print("computed scale:", scale_x, scale_y)

ui_cx = sr["x"] + sr["width"] / 2.0
ui_cy = sr["y"] + sr["height"] / 2.0
screen_x = int(origin.x + ui_cx / scale_x)
screen_y = int(origin.y + ui_cy / scale_y)
print("computed OS screen click point:", screen_x, screen_y)

# Move the real OS cursor there and click via SendInput (physical input,
# not a window message - this is what a real mouse does).
INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

user32.SetCursorPos(screen_x, screen_y)
time.sleep(0.15)
pt = wintypes.POINT()
user32.GetCursorPos(ctypes.byref(pt))
print("cursor now at:", pt.x, pt.y)

user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.08)
user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
print("click sent")

time.sleep(0.5)
r = call("rimworld/take_screenshot", fileName="rimthemes_os_click_after.png")
print("screenshot:", r.get("success"))
