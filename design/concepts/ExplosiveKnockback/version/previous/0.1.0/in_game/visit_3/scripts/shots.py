#!/usr/bin/env python3
"""Zoomed capture of each walk-save station: python.exe .../shots.py x,z[;x,z...] [--half 7]
Per station: UI cleared, the 15x15 rect unfogged, rimworld/screenshot_cell_rect; prints 'x,z path' per shot."""
import os
import sys
import time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, *[".."] * 7, "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402

half = int(sys.argv[sys.argv.index("--half") + 1]) if "--half" in sys.argv else 7
host, port, token = resolve_endpoint()
with RimBridge(host=host, port=port, token=token) as b:
    for xz in sys.argv[1].split(";"):
        x, z = (int(v) for v in xz.split(","))
        rect = (x - half, z - half, 2 * half + 1, 2 * half + 1)
        b.call("jawa/clear_ui", {"all": True})
        b.call("jawa/window_list_close", {"action": "close", "typeName": "EditWindow_Log"})
        b.call("jawa/set_fog", {"action": "unfog", "rect": "%d,%d,%d,%d" % rect})
        b.call("rimworld/screenshot_cell_rect", {"x": rect[0], "z": rect[1], "width": rect[2], "height": rect[3], "paddingCells": 1})
        time.sleep(1.5)       # realtime-drawn things need a rendered frame (live-review traps): shoot again
        r = b.call("rimworld/screenshot_cell_rect", {"x": rect[0], "z": rect[1], "width": rect[2], "height": rect[3], "paddingCells": 1})
        print("%d,%d %s" % (x, z, r.get("path")), flush=True)
