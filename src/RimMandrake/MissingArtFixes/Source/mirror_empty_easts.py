#!/usr/bin/env python3
r"""mirror_empty_easts.py - repair empty directional textures by mirroring
the healthy sibling, into MissingArtFixes as a loose-texture override.

    python.exe src/RimMandrake/MissingArtFixes/Source/mirror_empty_easts.py

WHY THIS IS MECHANICAL REPAIR AND NOT ORIGINATION
=================================================
No pixel is invented. Each output is a horizontal flip of a sibling that
already ships in the mod - and it is specifically the image RimWorld would
have drawn ITSELF if the broken file had simply been absent, because
Graphic_Multi auto-mirrors east<->west when one side is missing. The bug is
that a 0-alpha file EXISTS, which suppresses that fallback. We are restoring
the engine's own default, not authoring art. (jawaeyes_glow precedent.)

Anything needing a genuinely new view - a _south that cannot be derived from
a _north, a door frame whose east is a different asset from its north - is
NOT here. Those go to CREATE as art requests.

DONOR SELECTION MATTERS
=======================
Where two active mods ship the same texture path, the LATER one wins at
runtime, so the donor must be the winner or the repair will not match what
the player sees. Measured from ModsConfig 2026-08-12:

    Research Reinvented              order 274
    Research Reinvented Retextured   order 456   <- donor for all 4 kits
    VAE - Accessories                order 360
    MissingArtFixes                  order 570   <- overrides all of them

VERIFIED EMPTY BEFORE REPAIR (alpha max 0, whole image), 2026-08-12:
    RR  SimpleResearchKit_east   256x256    870 B      RRtex ships its own
    RR  MultiAnalyzerKit_east    256x256    870 B      empty 512x512 one at
    RR  RemoteResearchKit_east   256x256    870 B      the same path, 1514 B,
    RR  HiTechResearchKit_east   256x256    870 B      and WINS - so the
    RRtex SimpleResearchKit_east 512x512   1514 B      override fixes both
    VAE ToolBelt_west            256x256    753 B
"""
import os, sys
from PIL import Image

WS = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "Textures")

# (donor mod, texture path relative to Textures/, donor dir, broken dir)
JOBS = [
    ("3279243445", r"Things\Items\SimpleResearchKit\SimpleResearchKit",        "west", "east"),
    ("3279243445", r"Things\Items\MultiAnalyzerResearchKit\MultiAnalyzerResearchKit", "west", "east"),
    ("3279243445", r"Things\Items\RemoteResearchKit\RemoteResearchKit",        "west", "east"),
    ("3279243445", r"Things\Items\HiTechResearchKit\HiTechResearchKit",        "west", "east"),
    ("2521176396", r"Things\Apparel\ToolBelt\ToolBelt",                        "east", "west"),
]

def coverage(im):
    h = im.getchannel("A").histogram()
    return 100.0 * sum(h[1:]) / (im.width * im.height)

fail = 0
for mod, rel, donor_dir, broken_dir in JOBS:
    donor = os.path.join(WS, mod, "Textures", rel + "_" + donor_dir + ".png")
    if not os.path.exists(donor):
        print(f"  MISSING DONOR  {donor}"); fail += 1; continue
    im = Image.open(donor).convert("RGBA")
    cov = coverage(im)
    if cov < 1.0:
        # refuse to mirror a donor that is itself blank - that would ship the
        # bug at a higher load order and make it permanent
        print(f"  REFUSED  donor is {cov:.2f}% covered, i.e. blank: {donor}")
        fail += 1; continue
    out = os.path.join(OUT, rel + "_" + broken_dir + ".png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    flipped = im.transpose(Image.FLIP_LEFT_RIGHT)
    flipped.save(out, "PNG", optimize=True)
    chk = Image.open(out).convert("RGBA")
    print(f"  {os.path.basename(out):<38} {chk.width}x{chk.height}  "
          f"{os.path.getsize(out):>6} B  coverage={coverage(chk):5.2f}%  "
          f"(from {donor_dir}, {cov:.2f}%)")
print("\n  FAILED" if fail else "\n  all outputs written and re-read clean")
sys.exit(1 if fail else 0)
