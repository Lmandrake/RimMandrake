#!/usr/bin/env python3
r"""mirror_toolbelt_west.py - regenerate the ToolBelt_west worn-graphic texture
this mod ships, by horizontally flipping the donor's own ToolBelt_east.

    python.exe src/RimMandrake/ToolBeltFix/Source/mirror_toolbelt_west.py

Split out of MissingArtFixes/Source/mirror_empty_easts.py on 2026-08-13, when the
owner ruled one art-fix mod per donor mod. That script also produced four
research-kit textures for a different donor; that half now lives in
ResearchKitEastFix/Source/.

WHY THIS IS MECHANICAL REPAIR AND NOT ORIGINATION
=================================================
No pixel is invented. The output is a horizontal flip of a texture that already
ships in Vanilla Apparel Expanded - Accessories - and it is specifically the
image RimWorld would have drawn ITSELF had the broken file simply been absent,
because Graphic_Multi auto-mirrors east<->west when one side is missing. The bug
is that a 0-alpha file EXISTS, which suppresses that fallback.

VERIFIED BROKEN BEFORE REPAIR, 2026-08-13
=========================================
    ToolBelt_east.png    256x256   16,945 B   alpha max 255   (healthy donor)
    ToolBelt_west.png    256x256      753 B   alpha max 0     (the defect)
    ToolBelt_north.png   256x256    7,161 B   alpha max 255
    ToolBelt_south.png   256x256    7,449 B   alpha max 255

LOAD ORDER IS LOAD-BEARING HERE
===============================
VAE - Accessories ships all of its art as loose PNGs; it contains no
AssetBundles at all. Between two loose files at the same path ContentFinder
returns the LAST mod in the running order, so this mod must load after the
donor or the donor's blank file wins and the repair is invisible.

    ModsConfig.xml, 2026-08-13
      vanillaexpanded.vaeaccessories     line 361
      mandrake.toolbeltfix               (to be inserted after 558)
"""
import os, sys
from PIL import Image

WS = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"
VAEA = "2521176396"                    # Vanilla Apparel Expanded - Accessories
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "Textures")

REL = os.path.join("Things", "Apparel", "ToolBelt", "ToolBelt")


def coverage(im):
    h = im.getchannel("A").histogram()
    return 100.0 * sum(h[1:]) / (im.width * im.height)


donor = os.path.join(WS, VAEA, "Textures", REL + "_east.png")
if not os.path.exists(donor):
    print(f"  MISSING DONOR  {donor}"); sys.exit(1)

im = Image.open(donor).convert("RGBA")
cov = coverage(im)
if cov < 1.0:
    # refuse to mirror a donor that is itself blank - that would ship the bug at
    # a higher load order and make it permanent
    print(f"  REFUSED  donor is {cov:.2f}% covered, i.e. blank: {donor}")
    sys.exit(1)

out = os.path.join(OUT, REL + "_west.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
im.transpose(Image.FLIP_LEFT_RIGHT).save(out, "PNG", optimize=True)
chk = Image.open(out).convert("RGBA")
print(f"  {os.path.basename(out):<20} {chk.width}x{chk.height}  "
      f"{os.path.getsize(out):>6} B  coverage={coverage(chk):5.2f}%  "
      f"(from _east, {cov:.2f}%)")
print("\n  output written and re-read clean")
