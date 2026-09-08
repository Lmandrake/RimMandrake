#!/usr/bin/env python3
r"""mirror_research_kit_easts.py - regenerate the four _east worn-graphic
textures this mod ships, by horizontally flipping Research Reinvented
Retextured's own _west.

    python.exe src/RimMandrake/ResearchKitEastFix/Source/mirror_research_kit_easts.py

Split out of MissingArtFixes/Source/mirror_empty_easts.py on 2026-08-13, when the
owner ruled one art-fix mod per donor mod. That script also produced ToolBelt_west
for a different donor; its ToolBelt half now lives in ToolBeltFix/Source/.

WHY THIS IS MECHANICAL REPAIR AND NOT ORIGINATION
=================================================
No pixel is invented. Each output is a horizontal flip of a texture that already
ships in Research Reinvented Retextured - and it is specifically the image
RimWorld would have drawn ITSELF had the broken file simply been absent, because
Graphic_Multi auto-mirrors east<->west when one side is missing. The bug is that
a 0-alpha file EXISTS, which suppresses that fallback.

TWO MODS SHIP THESE PATHS - PICK THE DONOR THAT WINS
====================================================
The defs (RR_FieldResearchKit*) belong to Research Reinvented, but its art is
overridden by Research Reinvented Retextured, which ships NO XML at all and
loads later. ContentFinder walks the running mod list in reverse, so the later
mod wins; the donor for a mirror must therefore be RRR, not RR, or the repaired
east would not match the west a player actually sees.

    ModsConfig.xml, 2026-08-13
      petetimessix.researchreinvented          line 275
      aw.researchreinvented.retextured         line 457   <- donor for all 4
      mandrake.rm.researchkiteastfix              (to be inserted after 558)

VERIFIED BROKEN BEFORE REPAIR, 2026-08-13 (alpha channel max over whole image)
=============================================================================
    RR    SimpleResearchKit_east          256x256    870 B   maxA 0
    RR    MultiAnalyzerResearchKit_east   256x256    870 B   maxA 0
    RR    RemoteResearchKit_east          256x256    870 B   maxA 0
    RR    HiTechResearchKit_east          256x256    870 B   maxA 0
    RRR   SimpleResearchKit_east          512x512   1514 B   maxA 0
    RRR   MultiAnalyzerResearchKit_east   ABSENT
    RRR   RemoteResearchKit_east          ABSENT
    RRR   HiTechResearchKit_east          ABSENT

So Simple is blank at BOTH layers, and the other three fall through RRR's gap
onto RR's blank 256x256 file. Every one of the four renders nothing either way.
"""
import os, sys
from PIL import Image

WS = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"
RRR = "3279243445"                     # Research Reinvented Retextured
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "Textures")

KITS = ["SimpleResearchKit", "MultiAnalyzerResearchKit",
        "RemoteResearchKit", "HiTechResearchKit"]


def coverage(im):
    h = im.getchannel("A").histogram()
    return 100.0 * sum(h[1:]) / (im.width * im.height)


fail = 0
for kit in KITS:
    rel = os.path.join("Things", "Items", kit, kit)
    donor = os.path.join(WS, RRR, "Textures", rel + "_west.png")
    if not os.path.exists(donor):
        print(f"  MISSING DONOR  {donor}"); fail += 1; continue
    im = Image.open(donor).convert("RGBA")
    cov = coverage(im)
    if cov < 1.0:
        # refuse to mirror a donor that is itself blank - that would ship the
        # bug at a higher load order and make it permanent
        print(f"  REFUSED  donor is {cov:.2f}% covered, i.e. blank: {donor}")
        fail += 1; continue
    out = os.path.join(OUT, rel + "_east.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.transpose(Image.FLIP_LEFT_RIGHT).save(out, "PNG", optimize=True)
    chk = Image.open(out).convert("RGBA")
    print(f"  {os.path.basename(out):<38} {chk.width}x{chk.height}  "
          f"{os.path.getsize(out):>6} B  coverage={coverage(chk):5.2f}%  "
          f"(from _west, {cov:.2f}%)")
print("\n  FAILED" if fail else "\n  all outputs written and re-read clean")
sys.exit(1 if fail else 0)
