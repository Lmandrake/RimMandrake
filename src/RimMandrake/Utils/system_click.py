import ctypes
import platform
import sys
import time

# Windows-only tool (ctypes.windll has no meaning on any other platform). Guarded
# here, not just documented, so `python3 system_click.py --help` under WSL's own
# python3 exits 0 instead of crashing at import with
# AttributeError: module 'ctypes' has no attribute 'windll' — see
# SYSTEM_TOOLS_SELFTEST_1. Actual Windows-side behavior below is unchanged.
if platform.system() != "Windows":
    print("system_click.py is Windows-only (ctypes.windll); nothing to do on this platform.",
          file=sys.stderr)
    sys.exit(0)

user32 = ctypes.windll.user32
ctypes.windll.shcore.SetProcessDpiAwareness(2)

x = int(sys.argv[1])
y = int(sys.argv[2])

user32.SetCursorPos(x, y)
time.sleep(0.1)
user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
time.sleep(0.05)
user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
print(f"Clicked at ({x}, {y})")
