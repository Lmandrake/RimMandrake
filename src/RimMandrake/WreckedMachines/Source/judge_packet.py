#!/usr/bin/env python3
"""judge_packet.py: what the art judge is given for one machine, and the files as they will be installed. Dev tooling, not shipped.

    python3 Source/judge_packet.py <Short> [--root DIR]            write <root>/<Short>/_judge/
    python3 Source/judge_packet.py <Short> --record <verdicts.json> --out <repo path of the record> [--root DIR]

Run from src/RimMandrake/WreckedMachines/. The first form reads <root>/<Short>/MANIFEST.json and the fitted pictures in
<root>/<Short>/{wrecked,kludged}/ and writes, in <root>/<Short>/_judge/:

  install/<Tier>/<file>.png   the files as they go into Textures: every fitted facing, byte for byte, plus each facing that
                              the donor fills from another file (MANIFEST facing_fallbacks: west = the mirrored east, south =
                              a copy of north), because a level def names all four files of a Graphic_Multi
  full_<facing>.png           donor | Wrecked | Kludged at full resolution (the donor's 128 px per cell), on mid grey
  scale_<tier>_<facing>.png   the true-scale strip of src/RimMandrake/Utils/art/scale_panel.py: a vanilla human beside the
                              picture at max zoom, then normal play (32 px per cell) and zoomed out, on the desert ground
  sibling_south.png           the approved smelter: donor | Wrecked | Kludged, south (the sibling keeps)
  FACTS.json                  the def facts, each install file with its slot (the repo path it will have) and sha256, the
                              facings filled from another file, and the owner's notes on this kind of picture, verbatim

The second form turns a judge's verdicts into the record that T_ONBOARDING_COMPLETE reads (evidence/art/*.json): one entry
with every slot whose verdict is KEEP and the sha256 of its install file as it is now. A facing filled from another file
takes the verdict of the file it is filled from. It refuses (exit 1) when a verdict names a file that is not in the packet,
or when the judge's block does not say made_it false.

Exit 0 written; 1 refused; 2 COULD NOT LOOK (a manifest or a picture is missing: the line names it).
"""
import argparse
import hashlib
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(MOD, "..", "..", ".."))
FACINGS = ("north", "south", "east", "west")
TIERS = ("wrecked", "kludged")
MOBILE = ("VanometricPowerCell", "PsychicEmanator")          # the two carried machines: Textures/WreckedMachines/Mobile
OWNER_NOTES = [
    "2026-08-12, on the smelter's pictures: cross-facing damage correspondence is dropped. Holes need not be the same "
    "physical holes from facing to facing. Do not re-raise it as a defect. (MACHINES.md, 'What the smelter taught')",
    "His two corrections to the Kludged smelter (MACHINES.md): the conveyor belts stay clear, because they show where "
    "material flows; and the machine is sealed up and running, with no open breach full of fire.",
]


def could_not_look(msg):
    print("COULD NOT LOOK: " + msg)
    sys.exit(2)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def root_of(arg):
    return os.path.abspath(arg or os.environ.get("WM_ART_ROOT") or os.path.join(MOD, "art_source"))


def slot_dir(short, tier):
    group = "Mobile" if short in MOBILE else "Factories"
    return os.path.join("src", "RimMandrake", "WreckedMachines", "Textures", "WreckedMachines", group, short, tier.capitalize())


def vec(text, default):
    try:
        a, b = [float(x) for x in str(text).strip("() ").split(",")]
        return (a, b)
    except Exception:
        return default


def facing_of(name):
    stem = os.path.splitext(name)[0]
    for f in FACINGS:
        if stem.endswith("_" + f):
            return f
    return "single"


def build_install(root, short, man):
    """{tier: {file name: (path in install/, filled_from or None)}}; writes the install folder."""
    from PIL import Image, ImageOps
    out = {}
    for tier in TIERS:
        src_dir = os.path.join(root, short, tier)
        dst_dir = os.path.join(root, short, "_judge", "install", tier.capitalize())
        os.makedirs(dst_dir, exist_ok=True)
        files = {}
        for name in man["expected_files"]:
            src = os.path.join(src_dir, name)
            if not os.path.isfile(src):
                could_not_look("%s is not made yet" % src)
            dst = os.path.join(dst_dir, name)
            with open(src, "rb") as f, open(dst, "wb") as g:
                g.write(f.read())
            files[name] = (dst, None)
        for name, how in (man.get("facing_fallbacks") or {}).items():
            stem = name.rsplit("_", 1)[0]
            dst = os.path.join(dst_dir, name)
            if "mirror" in how and "east" in how:
                frm = "%s_east.png" % stem
                ImageOps.mirror(Image.open(files[frm][0]).convert("RGBA")).save(dst)
            elif "mirror" in how and "west" in how:
                frm = "%s_west.png" % stem
                ImageOps.mirror(Image.open(files[frm][0]).convert("RGBA")).save(dst)
            elif "north" in how:
                frm = "%s_north.png" % stem
                with open(files[frm][0], "rb") as f, open(dst, "wb") as g:
                    g.write(f.read())
            elif "south" in how:
                frm = "%s_south.png" % stem
                with open(files[frm][0], "rb") as f, open(dst, "wb") as g:
                    g.write(f.read())
            else:
                could_not_look("%s: the manifest's fill %r for %s is not one this tool knows" % (short, how, name))
            files[name] = (dst, frm)
        out[tier] = files
    return out


def panel(paths, bg=110):
    from PIL import Image
    ims = []
    for p in paths:
        im = Image.open(p).convert("RGBA")
        base = Image.new("RGBA", im.size, (bg, bg, bg, 255))
        base.alpha_composite(im)
        ims.append(base)
    sheet = Image.new("RGBA", (sum(i.width for i in ims), max(i.height for i in ims)), (bg, bg, bg, 255))
    x = 0
    for i in ims:
        sheet.paste(i, (x, 0))
        x += i.width
    return sheet.convert("RGB")


def scale_strip(png, draw, footprint, out):
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "art"))
    import scale_panel
    from pathlib import Path
    size = {"kind": "thing", "drawSize": draw, "footprint": footprint, "cells": max(draw)}
    tmp = out + ".compact.png"
    scale_panel.render_panel(open(png, "rb").read(), size, Path(tmp), Path(out))
    os.remove(tmp)


def make_packet(root, short):
    mpath = os.path.join(root, short, "MANIFEST.json")
    if not os.path.isfile(mpath):
        could_not_look("no %s" % mpath)
    man = json.load(open(mpath, encoding="utf-8"))
    jdir = os.path.join(root, short, "_judge")
    os.makedirs(jdir, exist_ok=True)
    inst = build_install(root, short, man)
    td = man["thingDef"]
    draw = vec(td.get("drawSize"), (1.0, 1.0))
    foot = vec(td.get("size"), (1.0, 1.0))
    pictures = []
    for name in man["expected_files"]:
        facing = facing_of(name)
        donor = os.path.join(root, short, "restored", name)
        if not os.path.isfile(donor):
            could_not_look("no donor file %s (run grab_source_art.py)" % donor)
        panel([donor, inst["wrecked"][name][0], inst["kludged"][name][0]]).save(os.path.join(jdir, "full_%s.png" % facing))
        pictures.append("full_%s.png" % facing)
        turned = facing in ("east", "west")
        d = (draw[1], draw[0]) if turned else draw
        fp = (foot[1], foot[0]) if turned else foot
        if facing in ("south", "east", "single"):
            for tier in TIERS:
                o = os.path.join(jdir, "scale_%s_%s.png" % (tier, facing))
                scale_strip(inst[tier][name][0], d, fp, o)
                pictures.append(os.path.basename(o))
    sm = os.path.join(MOD, "Textures", "WreckedMachines", "Factories", "AutomatedSmelter")
    sm_donor = os.path.join(MOD, "art_source", "AutomatedSmelter", "restored", "AutomatedSmelter_south.png")
    sib = [p for p in (sm_donor, os.path.join(sm, "Wrecked", "AutomatedSmelter_south.png"),
                       os.path.join(sm, "Kludged", "AutomatedSmelter_south.png")) if os.path.isfile(p)]
    if short != "AutomatedSmelter" and len(sib) >= 2:
        panel(sib).save(os.path.join(jdir, "sibling_south.png"))
        pictures.append("sibling_south.png")
    files = []
    for tier in TIERS:
        for name, (path, frm) in sorted(inst[tier].items()):
            files.append({"tier": tier, "file": name, "facing": facing_of(name), "packet_path": os.path.relpath(path, jdir),
                          "slot": os.path.join(slot_dir(short, tier), name).replace(os.sep, "/"), "sha": sha(path),
                          "filled_from": frm})
    facts = {"subject": short, "line": man.get("line"), "donor_def": man.get("defName"), "kind": man.get("kind"),
             "def_facts": {"drawSize": td.get("drawSize"), "footprint": td.get("size"), "graphicClass": td.get("graphicClass"),
                           "px_per_cell": 128, "what": "a building; Wrecked is the dead wreck found in a ruin, Kludged is the "
                           "same machine patched back into service by scavengers; the Refurbished level draws the donor's own picture"},
             "files": files, "pictures": pictures,
             "sibling_keeps": "the smelter's Wrecked and Kludged pictures (sibling_south.png), which the owner looked at and corrected",
             "donor_art": "the first column of each full_<facing>.png is the donor's own picture (Vanilla Furniture Expanded - Factory, "
                          "or the base game for the two carried machines); the donor draws a flat style with a dark rim, and these "
                          "pictures were asked to keep its outline, facing and parts",
             "owner_notes": OWNER_NOTES, "made": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    json.dump(facts, open(os.path.join(jdir, "FACTS.json"), "w", encoding="utf-8"), indent=1)
    print("PACKET %s: %d install files, %d pictures to look at, FACTS.json" % (jdir, len(files), len(pictures)))
    return 0


def make_record(root, short, verdicts_path, out):
    jdir = os.path.join(root, short, "_judge")
    try:
        facts = json.load(open(os.path.join(jdir, "FACTS.json"), encoding="utf-8"))
        v = json.load(open(verdicts_path, encoding="utf-8"))
    except (OSError, ValueError) as e:
        could_not_look(str(e))
    judge = v.get("judge") or {}
    if judge.get("made_it") is not False:
        print("REFUSED: the verdict file's judge block does not say made_it false")
        return 1
    by = {(f["tier"], f["file"]): f for f in facts["files"]}
    verdict = {}
    for row in v.get("verdicts") or []:
        k = (str(row.get("tier", "")).lower(), row.get("file"))
        if k not in by:
            print("REFUSED: the verdict names %s %s, which is not in the packet" % k)
            return 1
        verdict[k] = str(row.get("verdict", "")).upper()
    slots, redo = [], []
    for k, f in sorted(by.items()):
        src = (f["tier"], f["filled_from"]) if f["filled_from"] else k
        got = verdict.get(src)
        path = os.path.join(jdir, f["packet_path"])
        if got == "KEEP":
            if sha(path) != f["sha"]:
                print("REFUSED: %s changed after the packet was made (judge it again)" % path)
                return 1
            slots.append({"slot": f["slot"], "sha": f["sha"], "tier": f["tier"], "facing": f["facing"], "filled_from": f["filled_from"]})
        else:
            redo.append("%s %s: %s" % (f["tier"], f["file"], got or "no verdict"))
    rec = {"subject": short, "line": facts.get("line"), "verdict": "keep" if slots else "none kept", "slots": slots,
           "not_kept": redo, "judge": judge, "maker": v.get("maker") or {"agent": "rm-builder/opus with the Codex image door",
                                                                        "tool": "src/RimMandrake/WreckedMachines/Source/facing.py"},
           "constraints": v.get("constraints") or [], "reasons": v.get("reasons") or "", "notes": v.get("notes") or []}
    os.makedirs(os.path.dirname(os.path.join(REPO, out)), exist_ok=True)
    json.dump(rec, open(os.path.join(REPO, out), "w", encoding="utf-8"), indent=1)
    print("RECORD %s: %d slots kept, %d not kept%s" % (out, len(slots), len(redo), (": " + "; ".join(redo)) if redo else ""))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("short")
    ap.add_argument("--root")
    ap.add_argument("--record")
    ap.add_argument("--out")
    a = ap.parse_args()
    root = root_of(a.root)
    if a.record:
        if not a.out:
            ap.error("--record needs --out <repo path of the record>")
        return make_record(root, a.short, a.record, a.out)
    return make_packet(root, a.short)


if __name__ == "__main__":
    sys.exit(main())
