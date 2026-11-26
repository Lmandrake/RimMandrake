import ctypes
import platform
import sys
import time

# Windows-only tool (ctypes.windll). Under WSL's python3 it re-runs itself through Windows python.exe
# (win_reexec.py); with no Windows Python it exits 2, never 0 with nothing done (selftest_system_tools_wsl.py).
if platform.system() != "Windows":
    sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
    import win_reexec
    sys.exit(win_reexec.reexec_or_exit(__file__, sys.argv[1:], path_args=()))

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
