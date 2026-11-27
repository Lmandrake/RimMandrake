#!/usr/bin/env python3
"""
grab_source_art.py - copy a donor machine's own art into a work folder, measure
it, and write the per-facing briefs for its Wrecked and Kludged pictures.

WHAT IT DOES
============
Given a machine key (a donor defName from TREATED, or one of our defs from
SMALL), it:

  1. finds the donor art. A factory machine's art is in its Workshop mod, found
     by packageId (never by folder number). The texture path, graphic class,
     drawSize and size come from the donor's own ThingDef. The small three
     (power cell, emanator, component icon) draw vanilla art, read from the
     vanilla texture dump (env WM_VANILLA_DUMP);
  2. copies the donor files into `<root>/<short>/restored/`. These are the
     reference each picture is edited from and fitted against;
  3. records which facings the donor really has. A missing west is drawn by the
     game as a mirrored east, a missing south as the north, so those facings
     need no file of their own;
  4. records any other PNG in the donor's texture folder (for example the
     Autofarmer's extra base layer), because a picture of the machine without
     it may not be the whole machine in game;
  5. creates one folder for each tier (`wrecked/`, `kludged/`, or `icon/` for
     the component), each with a HOLES.txt that lists the files it needs;
  6. measures every donor image into MANIFEST.json (what fit_sprite.py and
     check_sprite.py read);
  7. renders CONTACT_SHEET.png of the donor facings;
  8. calls briefs.py, which writes one brief per facing and tier.

`<root>` is `art_source/` beside this folder, or `--root DIR`, or env
WM_ART_ROOT. Work outside the repo (for example a pilot in D:\\ClaudeWork)
uses --root.

USAGE
  python Source/grab_source_art.py VFEFactory_Autoloom
  python Source/grab_source_art.py VFEFactory_Autoloom --root /mnt/d/ClaudeWork/rimmandrake/art/wreckedmachines
  python Source/grab_source_art.py --list
  python Source/grab_source_art.py ALL
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pnglib import measure, contact_sheet, PngError          # noqa: E402
# ART_VERSION_WRANGLING_1: texture PNGs are written only through the art ledger (artwrite.py).
import atexit as _atexit, pathlib as _pathlib, sys as _sys  # noqa: E401
_sys.path.insert(0, next(str(_p / 'RimMandrake' / 'Utils' / 'art') for _p in _pathlib.Path(__file__).resolve().parents if _p.name == 'src'))
from artwrite import TextureWriter as _TextureWriter  # noqa: E402
_tw = _TextureWriter(__file__)
_atexit.register(_tw.report)

HERE = os.path.dirname(os.path.abspath(__file__))


def _check_sprite():
    """This folder's check_sprite.py, loaded by path (the general Utils/check_sprite.py is also on sys.path)."""
    global _CHECK
    if _CHECK is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("wm_check_sprite_grab", os.path.join(HERE, "check_sprite.py"))
        _CHECK = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_CHECK)
    return _CHECK


_CHECK = None
MOD_ROOT = os.path.dirname(HERE)
ART_SOURCE = os.environ.get("WM_ART_ROOT") or os.path.join(MOD_ROOT, "art_source")

_WORKSHOP = [r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100",
             "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"]
_VANILLA_DUMP = os.environ.get("WM_VANILLA_DUMP") or \
    "/mnt/d/ClaudeWork/rimmandrake/scratch/vanilla_tex/ludeon.rimworld.core"

FACINGS = ["north", "east", "south", "west"]
TIERS = ("wrecked", "kludged")      # the levels that have pictures of their own
                                    # (DESIGN.md: Refurbished may draw the donor's)

# The approved pictures every new picture is matched against (judge brief B3).
STYLE_ANCHOR = os.path.join(MOD_ROOT, "Textures", "WreckedMachines", "Factories",
                            "AutomatedSmelter", "{Tier}", "AutomatedSmelter_{facing}.png")

_VFE = "VanillaExpanded.VFEFactory"

# Every donor machine on the line (DESIGN.md "line keys"). `short` is the
# donor's texture basename, checked against its texPath when grabbed. `kind`,
# `dead` and `alive` describe in positive words what this machine looks like
# whole, as a wreck, and patched and running. They were written from the donor
# south facings (contact sheet of all 18, viewed 2026-11-27), so "top" and
# "bottom" are as the south facing shows them; briefs.py says so in every
# brief for another facing.
TREATED = {
    "VFEFactory_AutomatedSmelter": dict(
        line="smelter", short="AutomatedSmelter",
        kind="smelting furnace: a domed furnace on a square plinth with a heat "
             "ring round the dome, an intake belt at the top and three output "
             "belts along the bottom edge",
        dead="the heat ring is cold black metal and the dome is rust-streaked "
             "with a section of its cap gone",
        alive="the heat ring glows a dull working orange through its patched "
              "seams"),
    "VFEFactory_Autoloom": dict(
        line="autoloom", short="Autoloom",
        kind="textile loom: a red loom frame with three heddle boxes, a white "
             "cloth roller across the middle, thread spools in the top corner, "
             "an intake belt at the top and output belts at the bottom corners",
        dead="the roller is bare and torn, the spools empty, and the red paint "
             "faded and flaking to grey metal",
        alive="fresh pale cloth winds onto the roller and thread runs from the "
              "spools"),
    "VFEFactory_AutomatedAlloyForge": dict(
        line="alloyforge", short="AutomatedAlloyForge",
        kind="alloy forge: two round crucibles (one with a heat core, one under "
             "a fan cover), a control box between them, square heat windows "
             "and cone hoppers along the top, three output belts at the bottom",
        dead="the crucibles are cold and cracked, the heat windows dark and "
             "empty, a hopper torn away",
        alive="one crucible glows orange and the heat windows shine through "
              "patched frames"),
    "VFEFactory_AutomatedDrillPlatform": dict(
        line="drill", short="AutomatedDrillPlatform",
        kind="drill platform: an olive-green girder frame round a central "
             "drill head, bolted corner posts, on a dark square pad",
        dead="the drill head is seized and rust-scabbed, a girder bent and a "
             "corner post sheared off",
        alive="the drill head sits clean and greased in a frame braced with "
              "welded straps"),
    "VFEFactory_Autofarmer": dict(
        line="autofarmer", short="Autofarmer",
        kind="crop bed: a long open hopper of soil and crop along the back, a "
             "row of dispenser heads, and wide dark belts along the front edge",
        dead="the hopper holds dry dust and dead stalks, the dispenser heads "
             "missing or snapped",
        alive="the hopper holds dark soil and green shoots and the dispenser "
              "heads are mismatched replacements"),
    "VFEFactory_AutomatedBiofuelRefinery": dict(
        line="biofuelrefinery", short="AutomatedBiofuelRefinery",
        kind="biofuel refinery: two pale cylindrical tanks with copper pipes "
             "rising from them, a round vat of green liquid between them, three "
             "output belts at the bottom",
        dead="the vat is dry with a black crust, a tank split open and its "
             "copper pipe gone",
        alive="the vat holds fresh green liquid and the split tank is banded "
              "shut with straps"),
    "VFEFactory_AutomatedMasonrySaw": dict(
        line="masonrysaw", short="AutomatedMasonrySaw",
        kind="masonry saw: a grey gantry with a grid cage over the cutting bed, "
             "angled clamp arms in the top corners, an output belt at the bottom",
        dead="the cage is bent and half its bars gone, a clamp arm snapped off",
        alive="the cage is rebuilt with odd bars and the clamp arms hold a "
              "fresh stone block"),
    "VFEFactory_AutomatedMincer": dict(
        line="mincer", short="AutomatedMincer",
        kind="mincer: a grey housing with two dark-red rollers down its sides, "
             "a grinder plate in the middle, belts in and out",
        dead="the grinder plate is rusted solid and a roller cover is missing",
        alive="the grinder plate is bright from use and the rollers turn under "
              "patched covers"),
    "VFEFactory_ConveyorOven": dict(
        line="conveyoroven", short="ConveyorOven",
        kind="conveyor oven: a long grey oven body with rows of vent slats, a "
             "heated strip along its front, three belts along the bottom",
        dead="the heated strip is cold and black, vent slats missing in rows",
        alive="the heated strip glows orange and missing slats are replaced "
              "with a sheet of different metal"),
    "VFEFactory_AutomatedAssembler": dict(
        line="assembler", short="AutomatedAssembler",
        kind="assembler: a central rail flanked by two rows of jointed grey "
             "robot-arm segments, side ports, belts top and bottom",
        dead="arm segments hang loose or are missing and the rail is "
             "rust-pitted",
        alive="the arms are complete again with mismatched segments and spliced "
              "cable at their joints"),
    "VFEFactory_NeutroamineSynthesizer": dict(
        line="neutroamine", short="NeutroamineSynthesizer",
        kind="chemical synthesizer: two glass-domed centrifuges with cyan "
             "liquid, cyan tubing along the sides, a ribbed central column, two "
             "output belts",
        dead="the domes are cracked and dry, the tubing cut and gone",
        alive="the domes hold cyan liquid again, one dome a clouded replacement "
              "glass, tubing spliced with clamps"),
    "VFEFactory_AutomatedAmmunitionPress": dict(
        line="ammopress", short="AutomatedAmmunitionPress",
        kind="ammunition press: a teal press frame round a dark central ram, a "
             "tray of brass casings on one side and a tray of shot on the "
             "other, two output belts",
        dead="the trays are empty, the ram is seized and the teal paint is "
             "worn to rust",
        alive="the trays hold fresh brass and the ram is bright from use"),
    "VFEFactory_AutomatedDistillery": dict(
        line="distillery", short="AutomatedDistillery",
        kind="distillery: a pot-still dome with a riveted collar, a copper coil "
             "and a cylindrical tank in the top corner, belts in and out",
        dead="the dome is dented and green with corrosion and the coil is "
             "missing",
        alive="a new coil of a different metal is fitted and the dome is "
              "patched with riveted plates"),
    "VFEFactory_MedicineGranulator": dict(
        line="granulator", short="MedicineGranulator",
        kind="granulator: a central cyan glass drum with a rotor, white "
             "canisters on either side, white tubes standing at the corners, "
             "three output belts",
        dead="the drum glass is shattered and dark and the canisters are "
             "dented and grey",
        alive="the drum glows cyan behind a patched glass panel"),
    "VFEFactory_AutomatedMachiningBay": dict(
        line="machiningbay", short="AutomatedMachiningBay",
        kind="machining bay: a central dark rail flanked by two teal jointed "
             "robot arms, side ports, belts top and bottom",
        dead="one arm is collapsed and the other is missing its tool head",
        alive="both arms carry working tool heads, one arm rebuilt from grey "
              "salvage"),
    "VFEFactory_AutomatedCrematorium": dict(
        line="crematorium", short="ConveyorCrematorium",
        kind="crematorium: a squat rust-brown furnace box with a grey double "
             "door at the front, a control box in the top corner, an intake "
             "belt at the top",
        dead="the double door hangs open on one hinge and the box is cold and "
             "soot-black inside",
        alive="the door is shut and bolted with a plate of different metal and "
              "a warm glow shows at its seam"),
    "VFEFactory_AutomatedFishfarm": dict(
        line="fishfarm", short="AutomatedFishfarm",
        kind="fish farm: an open ring-shaped tank inside a square steel frame "
             "with corner bolts, an intake chute at the top",
        dead="the ring tank is dry and cracked, a frame bar is missing",
        alive="the cracks of the ring tank are sealed with patches, the "
              "missing frame bar is replaced with a mismatched beam, the "
              "open middle of the ring stays empty and transparent as in "
              "image 1, and every added box, cable and lamp sits on the frame, "
              "the lower ring or the chute and never over that open middle"),
    "VFEFactory_AutomatedCannery": dict(
        line="cannery", short="AutomatedCannery",
        kind="cannery: a rack of jars between two coiled spring columns, a "
             "round cutting disc at the front, a control panel, belts in and out",
        dead="the jar rack is empty and broken, a spring column collapsed",
        alive="the rack holds fresh jars and the collapsed spring column is "
              "replaced with a mismatched one"),
}

# Our own defs that draw vanilla art. Their pictures come from the vanilla
# texture dump, not a Workshop mod. Fields read from our Defs on 2026-11-27:
# Defs/ThingDefs_Buildings/Buildings_WreckedMachines_Mobile.xml and
# Defs/ThingDefs_Items/Items_WreckedMachines.xml.
# The base game draws these two at 64 px per cell (the emanator: 128 x 128 for a 2 x 2 drawSize; the power cell: 128 px
# across for 2 cells). The art judge brief's D2 asks drawSize x 128 px per cell and "never down-resolve", and the art
# judge refused the emanator's 128 px pictures for it on 2026-11-27. So the reference copy in restored/ is the base game's
# picture enlarged by this factor, and our own pictures are fitted from the image model's 1408 px drawing onto that canvas.
# Only the reference is enlarged; no picture of ours is ever made by enlarging a small one.
SMALL_CANVAS_SCALE = 2
SMALL = {
    "RM_WM_PowerCellBase": dict(
        line="powercell", short="VanometricPowerCell", tiers=TIERS,
        def_file="Defs/ThingDefs_Buildings/Buildings_WreckedMachines_Mobile.xml",
        label="vanometric power cell", texPath="Things/Building/Special/VanometricPowerCell",
        graphicClass="Graphic_Multi", drawSize="(2,3)", size="(1,2)",
        belts=False, canvas_scale=SMALL_CANVAS_SCALE,
        kind="power cell: a rounded olive-grey housing round a glass core "
             "cylinder held by four clamps, with a row of small indicator lamps "
             "along its base",
        dead="the glass core is dark, cracked and empty, two clamps are gone and "
             "the indicator lamps are dark",
        alive="the glass core glows a steady pale yellow-green behind one "
              "patched clamp, and the indicator lamps are lit"),
    "RM_WM_EmanatorBase": dict(
        line="emanator", short="PsychicEmanator", tiers=TIERS,
        def_file="Defs/ThingDefs_Buildings/Buildings_WreckedMachines_Mobile.xml",
        label="psychic emanator", texPath="Things/Building/Special/PsychicEmanator",
        graphicClass="Graphic_Single", drawSize="(2,2)", size=None,
        belts=False, canvas_scale=SMALL_CANVAS_SCALE,
        kind="psychic emanator: two fan-shaped emitter plates spread like "
             "wings from a central node, held up on a three-legged stand",
        dead="one emitter plate is bent and torn, the central node is dark and "
             "one leg is snapped short",
        alive="the emitter plates are braced with mismatched brackets and the "
              "central node glows faintly"),
    "RM_WM_AncientComponent": dict(
        line="component", short="AncientComponent", tiers=("icon",),
        donor_file="ComponentSpacer.png",
        def_file="Defs/ThingDefs_Items/Items_WreckedMachines.xml",
        label="ancient component", texPath="Things/Item/Resource/ComponentSpacer",
        graphicClass="Graphic_Single", drawSize=None, size=None,
        kind="machine component: a compact part pulled from an ancient machine "
             "that nobody alive can make",
        dead="", alive=""),
}

ALL = dict(TREATED)
ALL.update(SMALL)


def set_root(root):
    global ART_SOURCE
    if root:
        ART_SOURCE = os.path.abspath(root)
    return ART_SOURCE


def workshop_dir():
    for p in _WORKSHOP:
        if os.path.isdir(p):
            return p
    sys.exit("Could not find the Workshop content folder. Tried:\n  " + "\n  ".join(_WORKSHOP))


def find_mod_by_package_id(ws, package_id):
    """Locate a mod folder by packageId, case-insensitive.

    Parse, do not regex: an About.xml also holds a <packageId> for every entry
    in <modDependencies>, and VFE-Factory lists its dependencies first. Only
    the direct child of the root element is the mod's own identity.
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


def candidate_files(td):
    """Every file name the graphic class can load, before checking which exist."""
    base = os.path.basename(td["texPath"])
    if td["graphicClass"] == "Graphic_Multi":
        return ["%s_%s.png" % (base, f) for f in FACINGS]
    if td["graphicClass"] in ("Graphic_Single", None):
        return ["%s.png" % base]
    raise SystemExit("Unhandled graphicClass %r for %s - extend candidate_files()."
                     % (td["graphicClass"], td["texPath"]))


def facing_fallbacks(td, present):
    """Graphic_Multi draws a missing facing from another one. Return
    {missing_file: rule} for each missing facing the game fills itself, and the
    list of missing files it cannot fill."""
    if td["graphicClass"] != "Graphic_Multi":
        return {}, [f for f in candidate_files(td) if f not in present]
    base = os.path.basename(td["texPath"])
    have = {f for f in FACINGS if "%s_%s.png" % (base, f) in present}
    rules, unfilled = {}, []
    for f in FACINGS:
        fn = "%s_%s.png" % (base, f)
        if f in have:
            continue
        if f == "west" and "east" in have:
            rules[fn] = "mirror of east"
        elif f == "east" and "west" in have:
            rules[fn] = "mirror of west"
        elif f == "south" and "north" in have:
            rules[fn] = "same as north"
        elif f == "north" and "south" in have:
            rules[fn] = "same as south"
        else:
            unfilled.append(fn)
    return rules, unfilled


def resolve_texture_dir(mod_dir, tex_path):
    """RimWorld resolves texPath against any loaded Textures/ root."""
    rel = tex_path.replace("/", os.sep)
    for root, dirs, files in os.walk(mod_dir):
        if os.path.basename(root) == "Textures":
            cand = os.path.dirname(os.path.join(root, rel))
            if os.path.isdir(cand):
                return cand
    return None


def _donor(key, spec):
    """Return (td, owner, {file: source path}, other_layers)."""
    if key in TREATED:
        ws = workshop_dir()
        mod_dir = find_mod_by_package_id(ws, _VFE)
        if not mod_dir:
            sys.exit("Owner mod %s is not installed." % _VFE)
        td = read_thingdef(mod_dir, key)
        if not td:
            sys.exit("Could not find ThingDef %s inside %s." % (key, mod_dir))
        if os.path.basename(td["texPath"]) != spec["short"]:
            sys.exit("TREATED[%s].short is %r but the donor draws %r. Fix TREATED."
                     % (key, spec["short"], td["texPath"]))
        tex_dir = resolve_texture_dir(mod_dir, td["texPath"])
        if not tex_dir:
            sys.exit("Could not resolve texPath %r under %s." % (td["texPath"], mod_dir))
        srcs = {fn: os.path.join(tex_dir, fn) for fn in candidate_files(td)}
        mine = set(srcs)
        others = sorted(f for f in os.listdir(tex_dir)
                        if f.lower().endswith(".png") and f not in mine)
        return td, {"packageId": _VFE, "mod_dir": mod_dir}, srcs, others
    # SMALL: our def, vanilla art
    def_path = os.path.join(MOD_ROOT, spec["def_file"])
    txt = open(def_path, encoding="utf-8").read() if os.path.isfile(def_path) else ""
    if spec["texPath"] not in txt:
        sys.exit("%s no longer names texPath %s. Update SMALL[%s] from the def."
                 % (spec["def_file"], spec["texPath"], key))
    td = {k: spec.get(k) for k in ("label", "texPath", "graphicClass", "drawSize", "size")}
    td.update(def_file=spec["def_file"], research=[], costList={})
    if spec.get("donor_file"):
        srcs = {spec["donor_file"]: os.path.join(_VANILLA_DUMP, spec["donor_file"])}
    else:
        srcs = {fn: os.path.join(_VANILLA_DUMP, fn) for fn in candidate_files(td)}
    return td, {"packageId": "Ludeon.RimWorld", "mod_dir": _VANILLA_DUMP}, srcs, []


def enlarged(src, by):
    """The donor picture `by` times as large, as a PIL image: colour is resampled premultiplied by alpha, so the
    transparent pixels' colour does not bleed into the edge. It is the reference for the fit and the check, not art."""
    from PIL import Image
    im = Image.open(src).convert("RGBA")
    big = im.convert("RGBa").resize((im.width * by, im.height * by), Image.BICUBIC)
    return big.convert("RGBA")


def grab(key, quiet=False):
    spec = ALL.get(key)
    if not spec:
        sys.exit("%s is not in TREATED or SMALL. Add it to grab_source_art.py "
                 "first (and to MACHINES.md)." % key)
    tiers = tuple(spec.get("tiers", TIERS))
    td, owner, srcs, others = _donor(key, spec)

    out = os.path.join(ART_SOURCE, spec["short"])
    restored = os.path.join(out, "restored")
    os.makedirs(restored, exist_ok=True)
    for t in tiers:
        os.makedirs(os.path.join(out, t), exist_ok=True)

    present, measurements = [], {}
    for fn, src in srcs.items():
        if not os.path.isfile(src):
            continue
        dst = os.path.join(restored, fn)
        scale_by = int(spec.get("canvas_scale", 1))
        if scale_by > 1:
            _tw.save(enlarged(src, scale_by), dst)
        else:
            _tw.copy(src, dst)
        present.append(fn)
        try:
            m = measure(dst)
            m["file"] = fn
            # The donor's body (check_sprite.donor_body: small detached pieces left out): the box the check
            # and the fitter take as the reference. Equal to bbox when the donor has no such piece.
            _w, _h, _body, m["detached_px"] = _check_sprite().read_donor(dst)
            m["body_bbox"] = _check_sprite().body_bbox(_w, _h, _body) if m["detached_px"] else m["bbox"]
            m["body_bbox_wh"] = [m["body_bbox"][2] - m["body_bbox"][0] + 1,
                                 m["body_bbox"][3] - m["body_bbox"][1] + 1]
            measurements[fn] = m
        except PngError as e:
            measurements[fn] = {"file": fn, "error": str(e)}
    if spec.get("donor_file"):
        fallbacks, unfilled = {}, [f for f in srcs if f not in present]
    else:
        fallbacks, unfilled = facing_fallbacks(td, present)
    if unfilled:
        print("  ! the donor has no file for, and the game cannot fill: %s"
              % ", ".join(unfilled))
    wanted = [f for f in srcs if f in present]   # one picture per donor file

    ra = "" if ART_SOURCE == os.path.join(MOD_ROOT, "art_source") else " --root %s" % ART_SOURCE
    for t in tiers:
        with open(os.path.join(out, t, "HOLES.txt"), "w", encoding="utf-8") as fh:
            fh.write("Files required in this folder (%s tier of %s)\n" % (t, spec["short"]))
            fh.write("=" * 64 + "\n\n")
            for fn in wanted:
                have = os.path.isfile(os.path.join(out, t, fn))
                fh.write("  [%s] %s\n" % ("x" if have else " ", fn))
            for fn, rule in sorted(fallbacks.items()):
                fh.write("  [-] %s  (no file: the game draws it as the %s)\n" % (fn, rule))
            fh.write("\nEach must match its restored/ counterpart in canvas size and\n"
                     "closely in alpha bounding box. Fit and check with:\n\n"
                     "    python Source/fit_sprite.py %s --tier %s%s\n"
                     "    python Source/check_sprite.py %s --tier %s%s\n"
                     % (spec["short"], t, ra, spec["short"], t, ra))

    manifest = {
        "key": key,
        "defName": key,
        "line": spec["line"],
        "short": spec["short"],
        "tiers": list(tiers),
        "kind": spec["kind"],
        "dead": spec.get("dead", ""),
        "alive": spec.get("alive", ""),
        "belts": bool(spec.get("belts", True)),
        "canvas_scale": int(spec.get("canvas_scale", 1)),
        "owner": {"packageId": owner["packageId"],
                  "mod_dir": os.path.basename(owner["mod_dir"])},
        "thingDef": {k: (os.path.relpath(td[k], owner["mod_dir"]) if k == "def_file"
                         and td.get(k) and td[k].startswith(owner["mod_dir"]) else td.get(k))
                     for k in ("def_file", "label", "texPath", "graphicClass", "drawSize",
                      "size", "research", "costList")},
        "expected_files": wanted,
        "facing_fallbacks": fallbacks,
        "unfilled": unfilled,
        "other_layers": others,
        "restored_present": present,
        "measurements": measurements,
    }
    with open(os.path.join(out, "MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    sheet = None
    if present:
        sheet = contact_sheet([os.path.join(restored, f) for f in present],
                              os.path.join(out, "CONTACT_SHEET.png"),
                              cell=256, cols=min(4, len(present)))

    import briefs as _briefs
    _briefs.ART_SOURCE = ART_SOURCE
    written = _briefs.write_all(spec["short"])

    if not quiet:
        print("%s (%s)  line %s" % (key, td["label"], spec["line"]))
        print("  donor      : %s" % owner["mod_dir"])
        print("  texPath    : %s  [%s]" % (td["texPath"], td["graphicClass"]))
        print("  tile size  : %s   drawSize %s" % (td["size"], td["drawSize"]))
        print("  copied     : %d file(s) -> %s" % (len(present), restored))
        for fn in present:
            m = measurements[fn]
            if "error" in m:
                print("     %-38s ERROR %s" % (fn, m["error"])); continue
            print("     %-38s %dx%d  bbox %s  cover %.1f%%"
                  % (fn, m["width"], m["height"], m["bbox_wh"], m["coverage_pct"]))
        for fn, rule in sorted(fallbacks.items()):
            print("     %-38s no file: drawn as the %s" % (fn, rule))
        if others:
            print("  ! other art in the donor folder (extra layers?): %s" % ", ".join(others))
        print("  tiers      : %s  (see HOLES.txt)" % ", ".join(tiers))
        if sheet:
            print("  contact    : %s" % sheet)
        print("  briefs     : %d written under %s" % (len(written), out))
    return manifest


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("machine", nargs="?", help="a key from --list, or ALL")
    ap.add_argument("--list", action="store_true", help="list the machines and exit")
    ap.add_argument("--root", help="work folder (default art_source/, or env WM_ART_ROOT)")
    args = ap.parse_args()
    set_root(args.root)

    if args.list or not args.machine:
        print("Machines on the WreckedMachines line:\n")
        for k, v in ALL.items():
            print("  %-16s %-36s -> %s/%s/  [%s]"
                  % (v["line"], k, ART_SOURCE, v["short"], ",".join(v.get("tiers", TIERS))))
        return 0
    if args.machine in ("ALL", "ALL_TREATED"):
        for k in ALL:
            grab(k); print()
        return 0
    grab(args.machine)
    return 0


if __name__ == "__main__":
    sys.exit(main())
