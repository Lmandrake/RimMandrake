import ctypes
import sys
import time

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
