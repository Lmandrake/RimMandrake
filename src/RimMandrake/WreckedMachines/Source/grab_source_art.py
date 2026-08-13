#!/usr/bin/env python3
"""
grab_source_art.py — pull a donor machine's pristine art out of its mod and lay
out the empty "holes" the damaged tiers have to fill.

WHAT IT DOES
============
Given a machine defName, it:

  1. finds the owning mod in the Workshop tree by **packageId**, never by folder
     number (folder IDs change when a mod is re-uploaded; packageIds do not);
  2. reads the real `ThingDef` for `texPath`, `graphicClass`, `drawSize` and
     `size`, so the file list comes from the game's own data rather than a
     guess about naming;
  3. copies the pristine textures into `art_source/<Machine>/restored/` — the
     target state, and the reference every damaged tier is drawn against;
  4. creates `wrecked/` and `kludged/` containing a `HOLES.txt` naming the exact
     files that must appear there, so the gap is visible in a file browser;
  5. measures every source image (dimensions, alpha bounding box, coverage,
     greyscale-or-colour, tonal split) into `MANIFEST.json`, which is what
     `check_sprite.py` later validates returned art against;
  6. renders `CONTACT_SHEET.png` of all four facings on a checkerboard;
  7. writes `BRIEF.md` — a per-machine commission brief with the measured specs
     already filled in, ready to hand to an image model.

WHY MEASURE FIRST
=================
The single thing that will ruin this art is **misalignment**. RimWorld draws a
building from the texture's centre at `drawSize`, so a damaged version whose
silhouette sits 40px higher than the original will float off its own footprint
and no amount of redrawing the rust will fix it. Capturing the source bounding
box up front turns "does this line up?" from an in-game eyeball test costing a
~25-minute reload into a one-second offline check.

USAGE
  python Source/grab_source_art.py VFEFactory_AutomatedSmelter
  python Source/grab_source_art.py --list            # what can I grab?
  python Source/grab_source_art.py ALL_TREATED       # re-grab every registered machine

Runs from WSL or native Windows; the Workshop path is auto-detected.
"""

import argparse
import json
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pnglib import measure, contact_sheet, PngError          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_ROOT = os.path.dirname(HERE)
ART_SOURCE = os.path.join(MOD_ROOT, "art_source")

_WORKSHOP = [r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100",
             "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"]

# Machines this mod treats. Adding one here is the only edit needed to bring a
# new machine into the pipeline; MACHINES.md documents the policy for that.
TREATED = {
    "VFEFactory_AutomatedSmelter": {
        "owner_package_id": "VanillaExpanded.VFEFactory",
        "short": "AutomatedSmelter",
        "why": "Phase 2 of the ship_deck_plan repair ladder — the first machine "
               "the player restores, so it is the pilot for the whole pipeline.",
    },
}

FACINGS = ["north", "east", "south", "west"]


def workshop_dir():
    for p in _WORKSHOP:
        if os.path.isdir(p):
            return p
    sys.exit("Could not find the Workshop content folder. Tried:\n  " + "\n  ".join(_WORKSHOP))


def find_mod_by_package_id(ws, package_id):
    """Locate a mod folder by packageId. Case-insensitive; IDs are not stable-cased.

    ⚠️ Parse, do not regex. An About.xml contains a `<packageId>` for the mod
    AND one for every entry in `<modDependencies>`, and they are not in a
    reliable order — VFE-Factory lists Harmony's and VFE-Core's *before* its
    own. A naive "first packageId in the file" match therefore identifies the
    wrong mod, which is how this function failed on its first run. Only the
    direct child of the root element is the mod's own identity.
    """
    want = package_id.lower()
    for entry in sorted(os.listdir(ws)):
        about = os.path.join(ws, entry, "About", "About.xml")
        if not os.path.isfile(about):
            continue
        try:
            root = ET.parse(about).getroot()
        except (ET.ParseError, OSError):
            continue
        node = root.find("packageId")          # direct child only, never nested
        if node is not None and (node.text or "").strip().lower() == want:
            return os.path.join(ws, entry)
    return None


def read_thingdef(mod_dir, def_name):
    """Pull the ThingDef block for def_name and extract the fields we need."""
    for root, dirs, files in os.walk(mod_dir):
        if "Source" in dirs:
            dirs.remove("Source")
        for f in files:
            if not f.endswith(".xml"):
                continue
            path = os.path.join(root, f)
            try:
                txt = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if def_name not in txt:
                continue
            m = re.search(r"<ThingDef[^>]*>(?:(?!</ThingDef>).)*?<defName>%s</defName>.*?</ThingDef>"
                          % re.escape(def_name), txt, re.S)
            if not m:
                continue
            block = m.group(0)
            grab = lambda tag: (lambda mm: mm.group(1).strip() if mm else None)(
                re.search(r"<%s>(.*?)</%s>" % (tag, tag), block, re.S))
            return {
                "def_file": path,
                "label": grab("label"),
                "texPath": grab("texPath"),
                "graphicClass": grab("graphicClass"),
                "drawSize": grab("drawSize"),
                "size": grab("size"),
                "research": re.findall(r"<li>([^<]+)</li>",
                                       grab("researchPrerequisites") or ""),
                "costList": dict(re.findall(r"<(\w+)>(\d+)</\1>", grab("costList") or "")),
            }
    return None


def expected_files(td):
    """Which texture files this graphicClass implies. Only what we can prove."""
    base = os.path.basename(td["texPath"])
    if td["graphicClass"] == "Graphic_Multi":
        return ["%s_%s.png" % (base, f) for f in FACINGS]
    if td["graphicClass"] in ("Graphic_Single", None):
        return ["%s.png" % base]
    raise SystemExit("Unhandled graphicClass %r for %s — extend expected_files()."
                     % (td["graphicClass"], td["texPath"]))


def resolve_texture_dir(mod_dir, tex_path):
    """RimWorld resolves texPath against any loaded Textures/ root."""
    rel = tex_path.replace("/", os.sep)
    for root, dirs, files in os.walk(mod_dir):
        if os.path.basename(root) == "Textures":
            cand = os.path.dirname(os.path.join(root, rel))
            if os.path.isdir(cand):
                return cand
    return None


def grab(def_name, quiet=False):
    spec = TREATED.get(def_name)
    if not spec:
        sys.exit("%s is not in TREATED. Add it to grab_source_art.py first "
                 "(and to MACHINES.md)." % def_name)

    ws = workshop_dir()
    mod_dir = find_mod_by_package_id(ws, spec["owner_package_id"])
    if not mod_dir:
        sys.exit("Owner mod %s is not installed." % spec["owner_package_id"])

    td = read_thingdef(mod_dir, def_name)
    if not td:
        sys.exit("Could not find ThingDef %s inside %s." % (def_name, mod_dir))

    tex_dir = resolve_texture_dir(mod_dir, td["texPath"])
    if not tex_dir:
        sys.exit("Could not resolve texPath %r under %s." % (td["texPath"], mod_dir))

    wanted = expected_files(td)
    out = os.path.join(ART_SOURCE, spec["short"])
    restored = os.path.join(out, "restored")
    for sub in ("restored", "wrecked", "kludged", "repaired"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)

    copied, measurements, missing = [], {}, []
    for fn in wanted:
        src = os.path.join(tex_dir, fn)
        if not os.path.isfile(src):
            missing.append(fn); continue
        dst = os.path.join(restored, fn)
        shutil.copy2(src, dst)
        copied.append(fn)
        try:
            m = measure(dst)
            m["file"] = fn
            measurements[fn] = m
        except PngError as e:
            measurements[fn] = {"file": fn, "error": str(e)}

    if missing:
        print("  ! expected but not found in the mod: %s" % ", ".join(missing))

    for tier in ("wrecked", "kludged", "repaired"):
        with open(os.path.join(out, tier, "HOLES.txt"), "w", encoding="utf-8") as fh:
            fh.write("Files required in this folder (%s tier of %s)\n" % (tier, spec["short"]))
            fh.write("=" * 64 + "\n\n")
            for fn in wanted:
                have = os.path.isfile(os.path.join(out, tier, fn))
                fh.write("  [%s] %s\n" % ("x" if have else " ", fn))
            fh.write("\nEach must match its restored/ counterpart exactly in canvas size,\n"
                     "and closely in alpha bounding box, or it will not sit on its footprint\n"
                     "in game. Validate with:\n\n"
                     "    python Source/check_sprite.py %s --tier %s\n" % (spec["short"], tier))

    manifest = {
        "defName": def_name,
        "short": spec["short"],
        "why_treated": spec["why"],
        "owner": {"packageId": spec["owner_package_id"], "mod_dir": mod_dir},
        "thingDef": {k: td[k] for k in
                     ("def_file", "label", "texPath", "graphicClass", "drawSize",
                      "size", "research", "costList")},
        "expected_files": wanted,
        "restored_present": copied,
        "restored_missing": missing,
        "measurements": measurements,
    }
    with open(os.path.join(out, "MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    sheet = None
    if copied:
        sheet = contact_sheet([os.path.join(restored, f) for f in copied],
                              os.path.join(out, "CONTACT_SHEET.png"),
                              cell=256, cols=min(4, len(copied)))

    # sequential briefs need the sheet layout; build the sheet first if absent
    try:
        import sheet as _sheet
        if not os.path.isfile(os.path.join(out, "sheets", "SHEET_LAYOUT.json")):
            _sheet.make(spec["short"])
    except SystemExit:
        pass
    import briefs as _briefs
    _briefs.write_all(spec["short"])

    if not quiet:
        print("%s (%s)" % (def_name, td["label"]))
        print("  owner      : %s" % os.path.basename(mod_dir))
        print("  texPath    : %s  [%s]" % (td["texPath"], td["graphicClass"]))
        print("  tile size  : %s   drawSize %s" % (td["size"], td["drawSize"]))
        print("  research   : %s" % (", ".join(td["research"]) or "-"))
        print("  copied     : %d file(s) -> art_source/%s/restored/" % (len(copied), spec["short"]))
        for fn in copied:
            m = measurements[fn]
            if "error" in m:
                print("     %-34s ERROR %s" % (fn, m["error"])); continue
            print("     %-34s %dx%d  bbox %s  cover %.1f%%  %s"
                  % (fn, m["width"], m["height"], m["bbox_wh"], m["coverage_pct"],
                     "greyscale" if m["is_greyscale"] else "colour"))
        print("  holes      : art_source/%s/{wrecked,kludged}/  (see HOLES.txt)" % spec["short"])
        if sheet:
            print("  sheet      : %s" % os.path.relpath(sheet, MOD_ROOT))
        print("  briefs     : art_source/%s/BRIEF_{1_WRECKED,2_KLUDGED,3_REPAIRED}.md" % spec["short"])
        print("  sheet      : art_source/%s/sheets/SOURCE_SHEET.png" % spec["short"])
    return manifest


def write_brief(out_dir, man):
    """Machine-specific commission brief, with the measured numbers filled in."""
    td, ms = man["thingDef"], man["measurements"]
    first = next((v for v in ms.values() if "error" not in v), None)
    lines = []
    A = lines.append
    A("# Art brief — %s" % (td["label"] or man["short"]))
    A("")
    A("_Generated by `Source/grab_source_art.py` from the live ThingDef. "
      "Do not hand-edit; re-run the grabber._")
    A("")
    A("## The machine")
    A("")
    A("| | |")
    A("|---|---|")
    A("| defName | `%s` |" % man["defName"])
    A("| Owner mod | `%s` |" % man["owner"]["packageId"])
    A("| Occupies | %s tiles, drawn at %s |" % (td["size"], td["drawSize"]))
    A("| Build cost | %s |" % (", ".join("%s %s" % (k, v) for k, v in td["costList"].items()) or "-"))
    A("| Vanilla research | %s |" % (", ".join(td["research"]) or "-"))
    A("| Why we treat it | %s |" % man["why_treated"])
    A("")
    A("## What to produce")
    A("")
    A("Two damaged variants of **every** file in `restored/`, one set per tier:")
    A("")
    A("- **`wrecked/`** — badly deformed, scavenged, attacked, missing chunks, "
      "corroded. Dead. Reads as a hazard and a monument, not a machine.")
    A("- **`kludged/`** — partly restored. Exposed wiring, patches, mismatched "
      "plating, strange technology grafted onto the original elegant design. "
      "Visibly working, visibly wrong.")
    A("")
    A("The unmodified originals in `restored/` are the third tier and need no work.")
    A("")
    A("## Hard specifications (measured from the source art)")
    A("")
    if first:
        A("- **Canvas: exactly %d × %d px**, PNG with a real alpha channel. Not "
          "%d×%d, not cropped, not padded." % (first["width"], first["height"],
                                               first["width"], first["height"]))
        A("- **Keep the silhouette on its footprint.** The source art occupies a "
          "bounding box of about **%s px** inside that canvas. A damaged version "
          "may lose chunks at the edges, but its remaining mass must sit in the "
          "same place — the game draws from the texture centre, so a shifted "
          "silhouette floats off the machine's tiles."
          % first["bbox_wh"])
        A("- **Source art is %s.** Match it." %
          ("greyscale" if first["is_greyscale"] else "full colour"))
        A("- Transparent background. No drop shadow, no ground, no frame, no caption.")
    A("- **One file per facing, and they must agree.** This machine is "
      "`%s`, so the same physical damage has to be drawn consistently from "
      "every side. A hole punched in the north face has to exist on the south "
      "face too." % td["graphicClass"])
    A("")
    A("### ⛔ Nothing may extend beyond the machine's own outline")
    A("")
    A("**No hoses, cables, pipes, vents, antennae, smoke plumes or debris "
      "reaching outside the silhouette of the original machine.** Everything "
      "must sit within the shape you were given.")
    A("")
    A("This is not a style preference, it is how the game works. A RimWorld "
      "building owns a fixed block of tiles — this one occupies **%s** — and "
      "anything drawn outside that block overlaps whatever the player built "
      "next door. Worse, it is self-defeating: the art gets scaled to fit the "
      "original's footprint, so every pixel of cable sticking out shrinks the "
      "*machine itself* to make room."
      % td["size"])
    A("")
    A("Measured on the first attempt at this machine: appendages pushed the "
      "wrecked version's core body to **7% shorter** than the original once "
      "fitted. The machine reads smaller and weaker purely because of the "
      "cables around it.")
    A("")
    A("Damage should therefore be **subtractive**: chunks torn out of the "
      "outline, panels missing, corners blown away. Add nothing that projects. "
      "Grafted-on kludges are welcome, but they must be bolted *onto the body*, "
      "inside its existing outline.")
    A("")
    A("## Files required")
    A("")
    A("| File | Canvas | Source bbox | Coverage |")
    A("|---|---|---|---|")
    for fn in man["expected_files"]:
        m = ms.get(fn)
        if not m or "error" in m:
            A("| `%s` | — | — | (missing from source) |" % fn); continue
        A("| `%s` | %d×%d | %s | %.1f%% |"
          % (fn, m["width"], m["height"], m["bbox_wh"], m["coverage_pct"]))
    A("")
    A("Deliver them into `art_source/%s/wrecked/` and `.../kludged/` "
      "under **exactly these filenames**, then run:" % man["short"])
    A("")
    A("```bash")
    A("python Source/check_sprite.py %s --tier wrecked" % man["short"])
    A("python Source/check_sprite.py %s --tier kludged" % man["short"])
    A("```")
    A("")
    A("See `CONTACT_SHEET.png` in this folder for the source art on a "
      "checkerboard, and `../../DESIGN.md` for what the three tiers mean.")
    with open(os.path.join(out_dir, "BRIEF.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("machine", nargs="?", help="defName, or ALL_TREATED")
    ap.add_argument("--list", action="store_true", help="list treated machines and exit")
    args = ap.parse_args()

    if args.list or not args.machine:
        print("Machines currently treated by WreckedMachines:\n")
        for k, v in TREATED.items():
            print("  %-34s -> art_source/%s/" % (k, v["short"]))
            print("      %s\n" % v["why"])
        print("Add new ones to TREATED in this file, and to MACHINES.md.")
        return 0

    if args.machine == "ALL_TREATED":
        for k in TREATED:
            grab(k); print()
        return 0
    grab(args.machine)
    return 0


if __name__ == "__main__":
    sys.exit(main())
