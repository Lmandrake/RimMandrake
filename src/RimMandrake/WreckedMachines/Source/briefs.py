#!/usr/bin/env python3
"""
briefs.py — generate the sequential commission briefs for one machine.

WHY THREE BRIEFS AND NOT ONE
============================
An image model returns one image per turn, so "give me three versions" cannot
be a single request. More importantly the three states are not independent:
each is produced *by modifying the previous one*, which is what keeps the damage
consistent between them. A hole torn in the wrecked state must still be there,
patched, in the repaired state. That only happens if the model is looking at the
previous step while it works.

So the pipeline is a chain, not a fan-out:

    SOURCE_SHEET  ->  wrecked sheet  ->  kludged sheet  ->  repaired sheet

Each brief attaches the output of the step before it.

WHY A SHEET AND NOT FOUR IMAGES
===============================
All four facings travel together in one 2x2 image, so the model is drawing one
machine seen four ways rather than four machines that happen to share a name.
`sheet.py` builds it and cuts the result back apart.

Run automatically by `grab_source_art.py`; also standalone:
    python Source/briefs.py AutomatedSmelter
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_ROOT = os.path.dirname(HERE)
ART_SOURCE = os.path.join(MOD_ROOT, "art_source")


def _common(man, lay, short):
    """The specification block every brief repeats.

    Repeated deliberately: each brief is pasted into a fresh conversation, so
    anything not in the brief is not in the model's context.
    """
    td = man["thingDef"]
    sw, sh = lay["sheet_wh"] if lay else (None, None)
    L = []
    A = L.append
    A("## The image you are working on")
    A("")
    if lay:
        A("One image, **%d x %d**, containing the same machine drawn from four "
          "directions in a 2x2 grid:" % (sw, sh))
        A("")
        A("```")
        A("    +-----------------+-----------------+")
        A("    |     NORTH       |      EAST       |")
        A("    +-----------------+-----------------+")
        A("    |     SOUTH       |      WEST       |")
        A("    +-----------------+-----------------+")
        A("```")
        A("")
        A("**Modify all four. They must agree with each other.** This is one "
          "physical machine seen from four sides — a hole torn in its left flank "
          "appears on the north view *and* on the south view, from the other "
          "side. Damage that exists in only one panel is the single most obvious "
          "way this fails.")
    A("")
    A("The machine is an industrial **%s** from a top-down colony game. It is "
      "seen from directly above at a slight angle." % (td["label"] or short))
    A("")
    A("## Rules that are not negotiable")
    A("")
    A("**1. Return exactly the same image dimensions: %s.** Not larger, not "
      "cropped, not re-framed. Same 2x2 layout, same cell positions."
      % ("%d x %d" % (sw, sh) if lay else "as supplied"))
    A("")
    A("**2. Each machine must stay the same size within its cell.** Do not "
      "shrink the machine to make room for anything. Do not zoom in. If you "
      "overlay the result on the original, every machine should still cover the "
      "same area of its cell.")
    A("")
    A("**3. ⛔ Nothing may extend beyond the machine's outline.** No hoses, "
      "cables, pipes, vents, antennae, smoke plumes or debris reaching outside "
      "the shape you were given.")
    A("")
    A("   This is how the game works, not a style preference. The machine owns a "
      "fixed block of floor tiles — this one occupies **%s** — and anything "
      "drawn outside that block overlaps whatever the player built next to it. "
      "It is also self-defeating: the art gets scaled back to the original "
      "footprint, so every pixel of cable sticking out shrinks the *machine "
      "itself* to make room. Measured on a first attempt at this machine, "
      "projecting cables cost the body 14%% of its size." % td["size"])
    A("")
    A("   Everything you add must be bolted **onto the body, inside its existing "
      "outline**. Damage must be **subtractive** — chunks torn out, panels "
      "missing, corners blown away.")
    A("")
    A("**4. Transparent background.** If you cannot produce transparency, use "
      "flat pure black `#000000` and nothing else — no gradient, no vignette, no "
      "shadow. Say which you did.")
    A("")
    A("**5. Keep the art style.** Same rendering style, same palette family, "
      "same level of detail as the image supplied. This must look like it "
      "shipped in the same game.")
    return L


def _tail(step, tier, short):
    L = []
    A = L.append
    A("")
    A("## What to return")
    A("")
    A("**One image.** Same dimensions, same 2x2 layout, all four facings "
      "modified consistently.")
    A("")
    A("## After you deliver it")
    A("")
    A("_(For the human, not the model.)_ Save the returned image, then:")
    A("")
    A("```bash")
    A("python Source/sheet.py split %s --tier %s --sheet <the-returned-file> --then-fit" % (short, tier))
    A("python Source/check_sprite.py %s --tier %s" % (short, tier))
    A("```")
    A("")
    A("`split` cuts the sheet into four facings, `fit_sprite` conforms each one "
      "to its own reference canvas and pose, and `check_sprite` refuses anything "
      "that would waste a game load. The cut does not need to be pixel-perfect — "
      "the fitter registers each facing against the original afterwards.")
    return L


def write_all(short):
    mdir = os.path.join(ART_SOURCE, short)
    man = json.load(open(os.path.join(mdir, "MANIFEST.json"), encoding="utf-8"))
    lay_path = os.path.join(mdir, "sheets", "SHEET_LAYOUT.json")
    lay = json.load(open(lay_path, encoding="utf-8")) if os.path.isfile(lay_path) else None
    td = man["thingDef"]
    written = []

    # ---------------------------------------------------------------- step 1
    L = ["# Brief 1 of 3 — WRECKED", "",
         "_Generated from the live ThingDef. Do not hand-edit; re-run "
         "`Source/briefs.py`._", "",
         "**Attach:** `sheets/SOURCE_SHEET.png` — the intact machine.", ""]
    L += _common(man, lay, short)
    L += ["", "## What to draw", "",
          "Take this machine and make it a **long-dead wreck**. It has sat "
          "abandoned for a very long time. Nobody has maintained it, and "
          "scavengers have been at it.",
          "",
          "- Heavy corrosion and rust across every surface.",
          "- **Chunks missing.** Panels torn away, plating peeled back, corners "
          "broken off, holes punched through. Take material *out* of the "
          "outline — this is where the damage should read from a distance.",
          "- Deformation: bent frames, sagging structure, buckled housings.",
          "- Evidence of scavenging: fixtures stripped, access panels removed, "
          "cabling cut back to stubs.",
          "",
          "### ⚡ The one absolute for this step",
          "",
          "**NO lights. NO power signatures. NOTHING glowing, anywhere.**",
          "",
          "The original has lit indicator strips and glowing status lamps. Every "
          "one of them must be **dark, dead, cracked or missing**. No orange "
          "glow, no green telltales, no illuminated panels, no residual heat, no "
          "sparks, no embers. This machine has had no power for years and must "
          "read as completely inert at a glance.",
          "",
          "It should look like a monument, not a machine."]
    L += _tail(1, "wrecked", short)
    p = os.path.join(mdir, "BRIEF_1_WRECKED.md")
    open(p, "w", encoding="utf-8").write("\n".join(L) + "\n")
    written.append(p)

    # ---------------------------------------------------------------- step 2
    L = ["# Brief 2 of 3 — KLUDGED", "",
         "_Generated from the live ThingDef. Do not hand-edit; re-run "
         "`Source/briefs.py`._", "",
         "**Attach: the image you produced in Brief 1 (the wrecked sheet).** "
         "Not the original intact machine — this step modifies the *wreck*.", ""]
    L += _common(man, lay, short)
    L += ["", "## What to draw", "",
          "Scavengers have dragged this wreck back into service. Not repaired "
          "it — **forced it to work**, crudely, with whatever was to hand.",
          "",
          "**Keep the wreck underneath.** Every hole, tear and corroded surface "
          "from Brief 1 is still there. You are adding *on top of* it, not "
          "cleaning it up. If a panel was missing, it is still missing — there "
          "is now something jury-rigged bridging the gap.",
          "",
          "Add, generously and crudely:",
          "",
          "- Salvaged pipes and conduit strapped across the body.",
          "- Cable looms and hoses lashed on with clamps, wire and tape.",
          "- Mismatched boxes, tanks, pumps and improvised housings bolted on.",
          "- Bracing and props holding bent structure in place.",
          "- Weld scars, patch plates over the smaller holes.",
          "",
          "### 🔥 The signature of this step",
          "",
          "**Openly escaping flame.** This machine is running when it should "
          "not be. Show fire venting from gaps it was never meant to vent "
          "from — flame licking out of a split seam, a torn panel, a broken "
          "joint. Some heat glow and a little smoke are right too.",
          "",
          "This is the first step where the machine has power again, so a few "
          "improvised indicator lights are appropriate — but they should look "
          "*added*, not original.",
          "",
          "⚠️ Flame and smoke count as part of the machine for rule 3: **they "
          "must not extend past the outline.** Keep plumes short and inside the "
          "shape.",
          "",
          "It should look alarming — like it works, and like standing next to it "
          "is a bad idea."]
    L += _tail(2, "kludged", short)
    p = os.path.join(mdir, "BRIEF_2_KLUDGED.md")
    open(p, "w", encoding="utf-8").write("\n".join(L) + "\n")
    written.append(p)

    # ---------------------------------------------------------------- step 3
    L = ["# Brief 3 of 3 — REPAIRED", "",
         "_Generated from the live ThingDef. Do not hand-edit; re-run "
         "`Source/briefs.py`._", "",
         "**Attach: the image you produced in Brief 2 (the kludged sheet).** "
         "This step finishes the repair that Brief 2 started.", ""]
    L += _common(man, lay, short)
    L += ["", "## What to draw", "",
          "The crew has finished the job. This machine works properly now — but "
          "it was rebuilt by scavengers out of what they had, and it will never "
          "look factory-fresh again.",
          "",
          "Starting from the kludged version:",
          "",
          "- **Fill in every remaining hole with metal of a visibly different "
          "colour.** Patch plates and replacement panels in mismatched alloys — "
          "brighter, duller, differently weathered than the original housing. "
          "The repairs should be obvious as repairs.",
          "- **Tidy the cabling.** The lashed-on hoses and cables from Brief 2 "
          "are now routed **semi-neatly, plugging from one part of the device to "
          "another** — proper runs between real connection points, clipped down, "
          "deliberate. Still clearly aftermarket, no longer chaos.",
          "- **Keep some escaping smoke vents.** A few improvised exhausts still "
          "venting steam or smoke. This machine breathes through holes its "
          "designers did not put there.",
          "- Remove the open flame. Nothing should be burning any more.",
          "- Bring the indicator lights back to steady, working illumination.",
          "- Clean up the worst corrosion where the crew has worked, but leave "
          "the machine visibly old and hard-used.",
          "",
          "The read at a glance: **functional, cared for, and unmistakably "
          "rebuilt from a wreck.**",
          "",
          "⚠️ Rule 3 still applies to the tidied cabling: routed **across the "
          "body**, never looping outside the outline."]
    L += _tail(3, "repaired", short)
    p = os.path.join(mdir, "BRIEF_3_REPAIRED.md")
    open(p, "w", encoding="utf-8").write("\n".join(L) + "\n")
    written.append(p)

    return written


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python Source/briefs.py <MachineShortName>")
    for p in write_all(sys.argv[1]):
        print("wrote %s" % os.path.relpath(p, MOD_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
