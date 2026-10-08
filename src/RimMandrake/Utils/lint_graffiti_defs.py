#!/usr/bin/env python3
"""Offline lint of the Graffiti engine (mandrake.rm.graffiti) and of every mark that uses it: defs/patches vs C# via lint_mod_defs.py, plus

  gr-ext          every ModExtension_Graffiti in src/ (Graffiti, SacredGraffiti, GraffitiImperial): poolWeight >= 0, minArtistic 0..20,
                  form / category / visibility are real enum names (a bad enum value discards the whole def), ClanOnly has a reaction
  gr-class        each mark's effective thingClass (following ParentName) is Filth_Mark and its category is Filth
  gr-reaction     every reaction field names a ThoughtDef that exists and whose workerClass is ThoughtWorker_ViewedGraffitiMark (anything
                  else loads clean and never fires); every ThoughtDef using that worker is pointed at by some mark
  gr-sigil        sigilTierA marks name a frame texture that exists as a png
  gr-slider       the paint-interval slider range equals the kernel clamp and its default lies inside
  gr-kernel-pure  Kernel/*.cs names no Verse / RimWorld / UnityEngine / HarmonyLib
  sanity probe    the sweep must see the shipped marks (>= 20) and the sacred thoughts (>= 1)

    python3 src/RimMandrake/Utils/lint_graffiti_defs.py [--quiet] [--mod-dir D]
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
EXT = "RimMandrake.Graffiti.ModExtension_Graffiti"
WORKER = "RimMandrake.Graffiti.ThoughtWorker_ViewedGraffitiMark"
REACTIONS = ("viewerReactionThought", "onViewSubject", "onViewOwnFaction", "onViewSameIdeo", "onViewOtherIdeo", "onViewHostileMaker")


def enum_names(path, enum):
    txt = re.sub(r"//[^\n]*", "", open(path, encoding="utf-8-sig").read())
    body = re.search(r"enum %s\s*\{(.*?)\}" % enum, txt, re.S).group(1)
    return [x.strip() for x in body.split(",") if x.strip()]


def main(argv):
    rc = lint_mod_defs.run("Graffiti", argv)
    if rc == 2:
        return 2
    mod = os.path.join(REPO, "src", "RimMandrake", "Graffiti")
    if "--mod-dir" in argv:
        mod = argv[argv.index("--mod-dir") + 1]
    errs = []
    E = lambda c, m: errs.append("ERROR %s: %s" % (c, m))
    forms = enum_names(os.path.join(mod, "Source", "GraffitiForm.cs"), "GraffitiForm")
    cats = enum_names(os.path.join(mod, "Source", "GraffitiCategory.cs"), "GraffitiCategory")
    viss = enum_names(os.path.join(mod, "Source", "GraffitiCategory.cs"), "GraffitiVisibility")

    # gather defs from every mod, the planted/real Graffiti mod from `mod`
    real = os.path.join(REPO, "src", "RimMandrake", "Graffiti") + os.sep
    files = [p for p in glob.glob(os.path.join(REPO, "src", "*", "*", "Defs", "**", "*.xml"), recursive=True) if not p.startswith(real)]
    files += glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True)
    thing_by_name, named, thoughts, marks = {}, {}, {}, []
    for p in files:
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        rel = os.path.relpath(p, REPO) if p.startswith(REPO) else "Graffiti(copy)/" + os.path.relpath(p, mod)
        for d in root:
            if d.tag == "ThingDef":
                if d.get("Name"):
                    named[d.get("Name")] = d
                if d.findtext("defName"):
                    thing_by_name[d.findtext("defName").strip()] = d
                ext = next((li for li in d.findall("modExtensions/li") if li.get("Class") == EXT), None)
                if ext is not None and d.get("Abstract") != "True":
                    marks.append((rel, d, ext))
            elif d.tag == "ThoughtDef" and d.findtext("defName"):
                thoughts[d.findtext("defName").strip()] = (d.findtext("workerClass") or "").strip()

    def inherited(d, path):
        for _ in range(6):
            v = d.findtext(path)
            if v is not None:
                return v.strip()
            nxt = named.get(d.get("ParentName"))
            d = nxt if nxt is not None else thing_by_name.get(d.get("ParentName"))
            if d is None:
                return None
        return None

    pointed = set()
    for rel, d, ext in marks:
        name = (d.findtext("defName") or "?").strip()
        tag = "%s %s" % (rel, name)
        try:
            if float(ext.findtext("poolWeight") or 1) < 0:
                E("gr-ext", "%s: negative poolWeight" % tag)
            ma = int(ext.findtext("minArtistic") or 0)
            if not 0 <= ma <= 20:
                E("gr-ext", "%s: minArtistic %d outside 0..20" % (tag, ma))
        except ValueError as e:
            E("gr-ext", "%s: a number field is not a number (%s)" % (tag, e))
        for field, allowed in (("form", forms), ("category", cats), ("visibility", viss)):
            v = (ext.findtext(field) or "").strip()
            if v and v not in allowed:
                E("gr-ext", "%s: %s %r is not one of %s (a bad enum value discards the whole def)" % (tag, field, v, allowed))
        reacts = [(f, (ext.findtext(f) or "").strip()) for f in REACTIONS]
        if (ext.findtext("visibility") or "").strip() == "ClanOnly" and not any(v for _, v in reacts):
            E("gr-ext", "%s: ClanOnly with no reaction thought grants nothing" % tag)
        for f, v in reacts:
            if not v:
                continue
            pointed.add(v)
            if v not in thoughts:
                E("gr-reaction", "%s: %s names ThoughtDef %s which no mod defines" % (tag, f, v))
            elif thoughts[v] != WORKER:
                E("gr-reaction", "%s: %s -> %s has workerClass %r, so the reaction never fires" % (tag, f, v, thoughts[v]))
        if inherited(d, "thingClass") != "RimMandrake.Graffiti.Filth_Mark":
            E("gr-class", "%s: thingClass is %r, not Filth_Mark (no provenance, no going-over, no scrub protection)" % (tag, inherited(d, "thingClass")))
        if inherited(d, "category") != "Filth":
            E("gr-class", "%s: category is %r, not Filth" % (tag, inherited(d, "category")))
        if (ext.findtext("sigilTierA") or "").strip().lower() == "true":
            tex = (ext.findtext("sigilFrameTexPath") or "").strip()
            if not tex:
                E("gr-sigil", "%s: sigilTierA with no sigilFrameTexPath" % tag)
            elif not glob.glob(os.path.join(REPO, "src", "*", "*", "Textures", tex.replace("/", os.sep) + ".png")):
                E("gr-sigil", "%s: frame texture %s has no png in any mod's Textures" % (tag, tex))
    for tname, worker in sorted(thoughts.items()):
        if worker == WORKER and tname not in pointed:
            E("gr-reaction", "ThoughtDef %s uses the viewer worker but no mark points at it (unreachable)" % tname)
    n_worker = sum(1 for w in thoughts.values() if w == WORKER)
    if len(marks) < 20 or n_worker < 1:
        E("gr-ext", "sanity probe: the sweep saw %d marks and %d viewer thoughts (want >= 20 and >= 1)" % (len(marks), n_worker))

    # gr-slider
    modcs = open(os.path.join(mod, "Source", "RM_GraffitiMod.cs"), encoding="utf-8-sig").read()
    kern = open(os.path.join(mod, "Source", "Kernel", "RM_GraffitiKernel.cs"), encoding="utf-8-sig").read()
    sl = re.search(r"paintIntervalTicks = \(int\)list\.Slider\(paintIntervalTicks, ([\d.]+)f, ([\d.]+)f\)", modcs)
    kmin, kmax = re.search(r"MinPaintInterval = (\d+);", kern), re.search(r"MaxPaintInterval = (\d+);", kern)
    dflt = re.search(r"public static int paintIntervalTicks = (\d+);", modcs)
    if not (sl and kmin and kmax and dflt):
        E("gr-slider", "could not find the paint-interval slider, default or kernel clamp")
    else:
        if (float(sl.group(1)), float(sl.group(2))) != (float(kmin.group(1)), float(kmax.group(1))):
            E("gr-slider", "slider %s..%s differs from the kernel clamp %s..%s" % (sl.group(1), sl.group(2), kmin.group(1), kmax.group(1)))
        if not int(kmin.group(1)) <= int(dflt.group(1)) <= int(kmax.group(1)):
            E("gr-slider", "default paint interval %s lies outside the clamp" % dflt.group(1))
    for n, line in enumerate(kern.splitlines(), 1):
        if re.match(r"\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)\b", line):
            E("gr-kernel-pure", "RM_GraffitiKernel.cs:%d `%s`" % (n, line.strip()))
    print("graffiti data: %d marks, %d viewer thoughts, %d forms, %d categories" % (len(marks), n_worker, len(forms), len(cats)))
    for e in errs:
        print(e)
    return 1 if (errs or rc) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
