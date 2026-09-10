import ctypes
from ctypes import wintypes
import platform
import sys

# Windows-only tool (ctypes.windll has no meaning on any other platform). Guarded
# here, not just documented, so `python3 system_screenshot.py --help` under WSL's
# own python3 exits 0 instead of crashing at import with
# AttributeError: module 'ctypes' has no attribute 'windll' — see
# SYSTEM_TOOLS_SELFTEST_1. Actual Windows-side behavior below is unchanged.
if platform.system() != "Windows":
    print("system_screenshot.py is Windows-only (ctypes.windll); nothing to do on this platform.",
          file=sys.stderr)
    sys.exit(0)

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
ctypes.windll.shcore.SetProcessDpiAwareness(2)

width = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
height = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
left = user32.GetSystemMetrics(76)   # SM_XVIRTUALSCREEN
top = user32.GetSystemMetrics(77)    # SM_YVIRTUALSCREEN

hdesktop = user32.GetDesktopWindow()
desktop_dc = user32.GetWindowDC(hdesktop)
img_dc = gdi32.CreateCompatibleDC(desktop_dc)
bmp = gdi32.CreateCompatibleBitmap(desktop_dc, width, height)
gdi32.SelectObject(img_dc, bmp)
gdi32.BitBlt(img_dc, 0, 0, width, height, desktop_dc, left, top, 0x00CC0020)  # SRCCOPY

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD), ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG), ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD), ("biClrImportant", wintypes.DWORD),
    ]

bmi = BITMAPINFOHEADER()
bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
bmi.biWidth = width
bmi.biHeight = -height
bmi.biPlanes = 1
bmi.biBitCount = 24
bmi.biCompression = 0

buf_size = width * height * 3
buf = ctypes.create_string_buffer(buf_size)
gdi32.GetDIBits(img_dc, bmp, 0, height, buf, ctypes.byref(bmi), 0)

out_path = sys.argv[1] if len(sys.argv) > 1 else r"D:\Luke\dev\Rimworld\Transient\system_screenshot.bmp"
with open(out_path, "wb") as f:
    file_header = b"BM" + (54 + buf_size).to_bytes(4, "little") + b"\x00\x00\x00\x00" + (54).to_bytes(4, "little")
    f.write(file_header)
    f.write(bytes(bmi))
    f.write(buf.raw)

gdi32.DeleteObject(bmp)
gdi32.DeleteDC(img_dc)
user32.ReleaseDC(hdesktop, desktop_dc)
print(f"Saved {width}x{height} to {out_path}")
