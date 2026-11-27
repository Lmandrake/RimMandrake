#!/usr/bin/env python3
"""
briefs.py - write one brief per facing and tier for one machine.

ONE CALL PER FACING
===================
Each picture is one image-model edit of ONE facing, at that facing's own
proportions, generated at about 1400 px on its long edge and area-averaged
down by fit_sprite.py. (A 2x2 sheet of four facings gave about 1.2x
oversampling against 4.8x for one facing per call, so the sheet route is gone.)

THE CHAIN
=========
    donor facing  --edit-->  Wrecked facing  --edit-->  Kludged facing

  * Wrecked: image 1 is the donor facing (restored/<file>); image 2 is the
    approved Wrecked smelter facing, the style anchor.
  * Kludged: image 1 is this machine's FITTED Wrecked facing (so every hole is
    the same hole); image 2 is the approved Kludged smelter facing.
  * Icon (the component): image 1 is the donor icon; image 2 is the approved
    Wrecked smelter south facing, for the worn metal.

For each brief it writes:
  <root>/<short>/briefs/<TIER>_<facing>.md   the brief a person reads
  <root>/<short>/briefs/<TIER>_<facing>.txt  the prompt, exactly as sent

The text says in positive words what the picture shows. The machine-specific
parts (kind, dead, alive) come from MANIFEST.json, which grab_source_art.py
writes from its TREATED and SMALL tables.

Run by grab_source_art.py; also standalone:
    python Source/briefs.py Autoloom --root /mnt/d/ClaudeWork/rimmandrake/art/wreckedmachines
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_ROOT = os.path.dirname(HERE)
ART_SOURCE = os.environ.get("WM_ART_ROOT") or os.path.join(MOD_ROOT, "art_source")
CODEX_IMAGE = "~/dev/MandrakeWorkflows/skills/generating-images/scripts/codex_image.py"
STYLE_ANCHOR = os.path.join(MOD_ROOT, "Textures", "WreckedMachines", "Factories",
                            "AutomatedSmelter", "{Tier}", "AutomatedSmelter_{facing}.png")

# gpt-image-2 needs both edges in multiples of 16 and 655,360..8,294,400 px in
# all (measured limits of the model, MACHINES.md). LONG_EDGE is about 1400 px:
# the size the approved smelter pictures were generated at.
LONG_EDGE = 1408
MIN_PX, MAX_PX = 655360, 8294400


_DEFAULT_ROOT = os.path.join(MOD_ROOT, "art_source")


def show(path):
    """A path as written into a brief: relative to the mod when inside it, so
    tracked briefs carry no machine-specific prefix."""
    ap = os.path.abspath(path)
    if ap.startswith(MOD_ROOT + os.sep):
        return os.path.relpath(ap, MOD_ROOT)
    return ap


def root_arg():
    return "" if os.path.abspath(ART_SOURCE) == _DEFAULT_ROOT else " --root %s" % ART_SOURCE


def gen_size(w, h):
    """Generation size at the donor's proportions, long edge LONG_EDGE, edges
    rounded to multiples of 16, area inside the model's limits."""
    if w >= h:
        gw, gh = LONG_EDGE, max(16, int(round(LONG_EDGE * h / float(w) / 16.0)) * 16)
    else:
        gw, gh = max(16, int(round(LONG_EDGE * w / float(h) / 16.0)) * 16), LONG_EDGE
    if not (MIN_PX <= gw * gh <= MAX_PX):
        raise ValueError("generation size %dx%d is outside the model's limits" % (gw, gh))
    return gw, gh


def facing_of(fn):
    stem = os.path.splitext(fn)[0]
    for f in ("north", "east", "south", "west"):
        if stem.endswith("_" + f):
            return f
    return None


def _anchor(tier, facing, short):
    if short == "AutomatedSmelter":
        return None                     # the smelter IS the anchor
    t = "Wrecked" if tier == "icon" else tier.capitalize()
    return STYLE_ANCHOR.format(Tier=t, facing=facing or "south")


def _view(facing):
    if facing:
        return ("Image 1 is the %s facing of the machine. Keep exactly this "
                "facing, orientation and position on the canvas." % facing)
    return ("Image 1 is the machine as the game draws it. Keep exactly this "
            "orientation and position on the canvas.")


def _kind_line(man, facing, wrecked=False):
    """The kind texts in TREATED and SMALL describe the machine as its SOUTH
    facing shows it (belts "at the top" and so on). For any other facing, say
    so, and let image 1 decide where each part sits."""
    L = "It is a %s%s, a building from a top-down colony game." % (
        "wrecked " if wrecked else "", man["kind"])
    if facing and facing != "south":
        L += (" That description is of its south face. Image 1 is its %s face, "
              "so every part stays exactly where image 1 has it." % facing)
    return L


def _common(man, gw, gh):
    return [
        "The camera is the game's building camera: orthographic, looking down "
        "at about 35 degrees, the same as image 1.",
        "The machine fills the same footprint as in image 1, at the same size "
        "and in the same place. Every edge of the machine sits on or inside "
        "the outline of image 1. Wherever image 1 is transparent, the output "
        "is transparent too: the notches and gaps in image 1's outline, such "
        "as the empty corners beside a belt that juts out, stay empty.",
        "The background is fully transparent: only the machine's own pixels "
        "are drawn, and its edges are drawn the same way as the edges of "
        "image 1.",
        "Output one image, %d x %d pixels, the same proportions as image 1."
        % (gw, gh),
    ]


def prompt_wrecked(man, facing, gw, gh, has_anchor):
    L = ["Edit image 1. " + _view(facing),
         _kind_line(man, facing)]
    if has_anchor:
        L.append("Image 2 is a finished wreck from the same game. Match its "
                 "rendering, palette, rust, grime and depth of damage. Keep "
                 "the shape and parts of image 1.")
    L += ["",
          "Draw this machine as a dead wreck, abandoned for decades:",
          "- every lamp, screen and heat window is dark and cold; the metal "
          "is grey-brown, rusted and grimed;",
          "- panels and plates are missing, so the dark inside shows through "
          "the gaps; corners are broken off; frames are bent; cables end in "
          "short cut stubs;",
          "- %s;" % (man.get("dead") or "its working parts are seized and dull"),
          "- the damage takes material away: the wreck is the original shape "
          "with pieces gone;",
          "- the conveyor ends stay in their places, dusty and still.",
          ""]
    L += _common(man, gw, gh)
    return "\n".join(L)


def prompt_kludged(man, facing, gw, gh, has_anchor):
    L = ["Edit image 1. " + _view(facing),
         _kind_line(man, facing, wrecked=True)]
    if has_anchor:
        L.append("Image 2 is a finished patched-and-running machine from the "
                 "same game. Match its rendering and the character of its "
                 "patches. Keep the shape and parts of image 1.")
    L += ["",
          "Draw this same wreck brought back into service by scavengers with "
          "salvage:",
          "- each hole of image 1 is closed with a bolted patch plate of a "
          "different metal, plainly a different colour and wear from the "
          "housing around it;",
          "- hand-spliced cable runs, clamped and taped, lie flat across the "
          "body from one part to another;",
          "- one plain bodge: a salvaged box or pump strapped onto the body, "
          "inside its outline;",
          "- it is plainly working: %s, and a few small added indicator lamps "
          "are lit;" % (man.get("alive") or "its working parts are active"),
          "- the conveyor belts and the intake are clear and running: their "
          "slats are clean and run the same way as in image 1, and the arrow "
          "mark beside each belt is bright and points exactly the way it "
          "points in image 1; the belts carry no other arrows or chevrons;",
          "- bent frames stay bent and rust stays wherever no patch covers it.",
          ""]
    L += _common(man, gw, gh)
    return "\n".join(L)


def prompt_icon(man, gw, gh, has_anchor):
    L = ["Edit image 1. Image 1 is an item icon from a top-down colony game.",
         "Draw it as a %s." % man["kind"]]
    if has_anchor:
        L.append("Image 2 is a wreck from the same game. Match its rendering, "
                 "palette and worn metal.")
    L += ["",
          "- the part is whole and usable, its metal old: darkened, scratched "
          "and worn smooth at the edges;",
          "- its contacts and circuitry are an older pattern than image 1, "
          "with one small lamp still faintly lit;",
          "- it sits centred at the size of image 1, in the same view.",
          "",
          "The background is fully transparent: only the item's own pixels are "
          "drawn, and its edges are drawn the same way as the edges of image 1.",
          "Output one image, %d x %d pixels." % (gw, gh)]
    return "\n".join(L)


def write_all(short):
    mdir = os.path.join(ART_SOURCE, short)
    man = json.load(open(os.path.join(mdir, "MANIFEST.json"), encoding="utf-8"))
    bdir = os.path.join(mdir, "briefs")
    os.makedirs(bdir, exist_ok=True)
    written = []
    for tier in man.get("tiers", ["wrecked", "kludged"]):
        for fn in man["expected_files"]:
            m = man["measurements"].get(fn, {})
            if "width" not in m:
                continue
            facing = facing_of(fn)
            gw, gh = gen_size(m["width"], m["height"])
            anchor = _anchor(tier, facing, short)
            has_anchor = bool(anchor)
            if tier == "wrecked":
                image1 = os.path.join(mdir, "restored", fn)
                prompt = prompt_wrecked(man, facing, gw, gh, has_anchor)
            elif tier == "kludged":
                image1 = os.path.join(mdir, "wrecked", fn)
                prompt = prompt_kludged(man, facing, gw, gh, has_anchor)
            elif tier == "icon":
                image1 = os.path.join(mdir, "restored", fn)
                prompt = prompt_icon(man, gw, gh, has_anchor)
            else:
                continue
            name = "%s_%s" % (tier.upper(), facing or "single")
            out_png = os.path.join(mdir, tier, fn)
            txt = os.path.join(bdir, name + ".txt")
            open(txt, "w", encoding="utf-8").write(prompt + "\n")
            imgs = " ".join("--image %s" % show(p) for p in [image1] + ([anchor] if anchor else []))
            cmd = ("python3 %s edit --out %s --timeout 520 --prompt \"$(cat %s)\" %s"
                   % (CODEX_IMAGE, show(out_png), show(txt), imgs))
            L = ["# %s - %s - %s" % (short, tier, facing or "single"), "",
                 "_Written by Source/briefs.py from MANIFEST.json. Re-run it; "
                 "do not hand-edit._", "",
                 "Run from src/RimMandrake/WreckedMachines/. "
                 "Donor file: `%s` (%dx%d). Generate at **%d x %d**; "
                 "fit_sprite.py brings it to the donor canvas."
                 % (fn, m["width"], m["height"], gw, gh), "",
                 "## Attach, in this order", ""]
            L.append("1. `%s`%s" % (show(image1), "  (the FITTED Wrecked facing: run "
                                    "fit_sprite --apply on it first)" if tier == "kludged" else ""))
            if anchor:
                L.append("2. `%s`  (style anchor, approved)" % show(anchor))
            L += ["", "## Prompt (exactly what is sent; also in `%s`)" % os.path.basename(txt),
                  "", "```", prompt, "```", "",
                  "## Commands", "", "```bash", cmd,
                  "python3 Source/fit_sprite.py %s --tier %s%s%s --inside --apply"
                  % (short, tier, (" --facing " + facing) if facing else "", root_arg()),
                  "python3 Source/check_sprite.py %s --tier %s%s"
                  % (short, tier, root_arg()),
                  "```", "",
                  "Then look at the fitted picture. One Codex call per run of the "
                  "first command; redo a facing at most twice."]
            p = os.path.join(bdir, name + ".md")
            open(p, "w", encoding="utf-8").write("\n".join(L) + "\n")
            written.append(p)
    return written


def main():
    global ART_SOURCE
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("machine", help="the machine's short name (its folder)")
    ap.add_argument("--root", help="work folder (default art_source/, or env WM_ART_ROOT)")
    args = ap.parse_args()
    if args.root:
        ART_SOURCE = os.path.abspath(args.root)
    for p in write_all(args.machine):
        print("wrote %s" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
