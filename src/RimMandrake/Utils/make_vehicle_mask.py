#!/usr/bin/env python3
"""make_vehicle_mask.py — derive an Alpha Vehicles tint mask from the art.

    python3 src/RimMandrake/Utils/make_vehicle_mask.py --art X_south.png --out X_southm.png
    python3 src/RimMandrake/Utils/make_vehicle_mask.py --art X_south.png --verify X_southm.png

WHY DERIVE RATHER THAN DRAW
===========================
Alpha Vehicles – Neolithic ships every facing with a paired `<facing>m.png`
mask that drives Vehicle Framework's colour/pattern system. Measured on
`AV_DogSled_south`:

    mask is a RED-CHANNEL map, 17 unique colours
      (255,0,0)  95.2%  -> takes the player's vehicle colour
      (0,0,0)     4.4%  -> untinted, keeps its own art colours
    the black region spans y 270..466 -- EXACTLY the draught-animal block
    (the sled body and its traces, y 11..255, are red)

So the rule the mod actually follows is: **the animals are untinted, the vehicle
is tinted.** Nothing about that needs artistic judgement, which means the mask is
a function of the art and should be computed from it.

That matters because a mask that disagrees with its art fails **silently** — the
new animal simply does not tint, with no error anywhere. Deriving removes the
whole failure mode instead of relying on remembering to edit two files in step.

⚠️ WHERE THIS TOOL DOES NOT WORK — measured 2026-08-13 by a retired seat
==============================================================
The animal is located by looking for **warm hide pixels**, so the rule breaks on
art whose *rigging* is the same temperature as its animals.

On the finished eopie sled it reported `waist y=262` when the animals actually
start at **y=331**: the leather traces read as hide, so the whole rigging was
marked untinted. Not a wrong answer from a broken tool — a colour heuristic being
asked a question colour cannot answer.

**If you composited the animals yourself, do not use this — emit the mask from
the geometry you already know.** That is what
`src/Jawa/DesertVehicleReskin/Source/build_eopie_sled_south.py` does, and
it is exact rather than inferred. This tool remains the right answer when you are
*editing* a shipped facing in place and do not have that knowledge.

The greyscale dog art it was written against has no such ambiguity, which is why
the limitation did not show up until the first reskin actually used it.

⚠️ SECOND LIMIT, and it applies to READING a shipped mask as well as writing one:
a shipped mask's black region is the animal's **interior fill**, not the animal.
The 4-6 px pure-black keyline around it is tagged RED, i.e. vehicle, so the black
region is an inward-eroded copy inset on every edge. Measured across DogSled,
Chariot and OxCart, nine facings. **Do not use a shipped mask as an erase stencil
without dilating it first** — as per the trap file.

HOW THE ANIMAL REGION IS FOUND
==============================
The draught animals are warm-toned (tan/hide) and the sled is neutral grey, so
`r - b >= WARM` finds animal pixels. Their dark KEYLINES are neutral and would
be missed, so warmth is used only to locate the region's top edge; every opaque
pixel at or below it is then treated as animal. That matches how the shipped
mask is drawn — a solid block, not a per-pixel colour key.

Verified against the shipped pair before use; see --verify.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "skills", "generating-images", "scripts"))
import pnglib                                                    # noqa: E402

WARM = 18          # r-b at or above this is hide rather than grey metal/wood
ALPHA = 32         # opacity floor, matching validate_sprite.py's solid test
RED = (255, 0, 0, 255)
BLACK = (0, 0, 0, 255)


# Which side of the vehicle the draught animals sit on, per facing. Measured
# from the shipped masks -- it is always the LEADING side, i.e. the direction of
# travel, so it differs per facing and cannot be assumed:
#     south  black y 270..466  (bottom)
#     north  black y  38..245  (TOP)
#     east   black x 261..488  (RIGHT)
SIDE = {"south": ("y", "ge"), "north": ("y", "le"), "east": ("x", "ge")}
DARK = 80          # keyline luminance; traces are light, outlines are near-black


def waist(w, h, d, axis, side):
    """Where the draught team begins, along the facing's travel axis.

    ⚠️ This was first written as "the narrowest interior slice" — the trace gap
    between vehicle and team. That is a real feature of the art and it is NOT
    reliable: on the eopie sled it picked y=41, the narrow twin rails at the top
    of the sled, instead of y≈253. A vehicle may be pinched anywhere.

    Anchored to the animals themselves instead. They are the warm-toned mass, so
    the first warm slice along the travel axis is the boundary, and no other
    narrow point can be mistaken for it. Measured against the shipped south
    pair, the animal block starts y=270 and the trace waist sits at y=253 — the
    warm edge is the one that matters, because the 17 rows between them are
    trace and must stay tinted.
    """
    warm = []
    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 4
            if d[i + 3] > ALPHA and d[i] - d[i + 2] >= WARM:
                warm.append(y if axis == "y" else x)
    if not warm:
        return None
    return min(warm) if side == "ge" else max(warm)


def is_animal(d, i):
    """Hide, or the dark keyline around it — but NOT a light-grey trace.

    Measured on the shipped south pair: 5,760 opaque pixels inside the animal
    band are RED, not black. Those are the traces weaving between the animals,
    which stay vehicle-tinted. So "inside the band" is necessary and not
    sufficient; the animal itself has to be identified.
    """
    r, g, b = d[i], d[i + 1], d[i + 2]
    if r - b >= WARM:
        return True                       # hide
    return (r + g + b) / 3 < DARK         # its keyline


def build(w, h, d, axis, side, cut):
    out = bytearray(w * h * 4)
    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 4
            v = y if axis == "y" else x
            beyond = (v >= cut) if side == "ge" else (v <= cut)
            animal = (d[i + 3] > ALPHA and beyond and is_animal(d, i))
            out[i:i + 4] = bytes(BLACK if animal else RED)
    return bytes(out)


def classify(px, i):
    r, g, b = px[i], px[i + 1], px[i + 2]
    return "black" if (r < 64 and g < 64 and b < 64) else (
        "red" if r > 128 else "other")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--art", required=True, help="the finished facing PNG")
    ap.add_argument("--facing", required=True, choices=sorted(SIDE),
                    help="which side the draught animals lead on")
    ap.add_argument("--out", help="write the derived mask here")
    ap.add_argument("--verify", metavar="MASK",
                    help="compare the derived mask against a shipped one "
                         "instead of writing; proves the rule on known-good art")
    args = ap.parse_args()

    w, h, d = pnglib.read_png(args.art)
    axis, side = SIDE[args.facing]
    cut = waist(w, h, d, axis, side)
    if cut is None:
        print("no warm/hide pixels found — is there a draught animal in this "
              "facing? refusing to guess a mask", file=sys.stderr)
        return 2
    derived = build(w, h, d, axis, side, cut)
    nblk = sum(1 for i in range(0, len(derived), 4) if derived[i] < 64)
    print("%s: %dx%d  facing=%s  waist %s=%d  untinted px=%d" % (
        os.path.basename(args.art), w, h, args.facing, axis, cut, nblk))

    if args.verify:
        vw, vh, v = pnglib.read_png(args.verify)
        if (vw, vh) != (w, h):
            print("canvas mismatch: mask %dx%d vs art %dx%d" % (vw, vh, w, h))
            return 1
        agree = dis = 0
        for i in range(0, len(v), 4):
            a, b = classify(derived, i), classify(v, i)
            if a == b:
                agree += 1
            else:
                dis += 1
        tot = agree + dis
        print("vs %s: %d/%d agree (%.2f%%), %d differ"
              % (os.path.basename(args.verify), agree, tot,
                 100.0 * agree / tot, dis))
        return 0

    if not args.out:
        print("nothing to do: pass --out or --verify", file=sys.stderr)
        return 2
    pnglib.write_rgba(args.out, w, h, derived)
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
