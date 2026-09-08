#!/usr/bin/env python3
"""One-off: extract specific vanilla Core UI Texture2D assets from resources.assets
by name, for measuring exact pixel dimensions before a 9-slice repaint.
Run with Windows python.exe (UnityPy is installed there, not under WSL python3).
"""
import UnityPy
import sys

RESOURCES = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\resources.assets"
OUT = r"D:\Luke\dev\Rimworld\Transient\vanilla_ui_extract"

WANTED = {
    "ButtonBG", "ButtonBGMouseover", "ButtonBGClick",
    "ButtonSubtleAtlas",
    "TabAtlas",
    "DesButBG", "AbilityButBG",
    "CheckOn", "CheckOff", "CheckPartial",
    "RadioButOn", "RadioButOff",
    "SliderRail", "SliderHandle",
    "DropShadow",
}

import os
os.makedirs(OUT, exist_ok=True)

env = UnityPy.load(RESOURCES)
found = {}
for obj in env.objects:
    if obj.type.name != "Texture2D":
        continue
    try:
        data = obj.read()
    except Exception as e:
        continue
    name = data.m_Name
    if name in WANTED:
        path = os.path.join(OUT, f"{name}.png")
        try:
            data.image.save(path)
            found.setdefault(name, []).append((path, data.image.size))
        except Exception as e:
            print(f"FAILED to save {name}: {e}", file=sys.stderr)

for name in sorted(WANTED):
    if name in found:
        for path, size in found[name]:
            print(f"{name}: {size[0]}x{size[1]} -> {path}")
    else:
        print(f"{name}: NOT FOUND")
