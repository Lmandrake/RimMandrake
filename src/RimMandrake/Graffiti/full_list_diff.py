#!/usr/bin/env python3
"""full_list_diff.py -- what the owner's FULL list adds that Graffiti's minimal rung never saw
(GRAFFITI_NORTHSTAR_GREEN_FULL_1, acceptance: "Every full-list-only difference is listed in the sheet: pool
members, cleaning mods, camera mods"). The northstar_driver writes the result into the run's results JSON as
`full_list_differences` (plan hook `full_list_differences`); run alone it prints the same JSON:

    python3 src/RimMandrake/Graffiti/full_list_diff.py [--list <ModsConfig>] [--minimal <ModsConfig>]

full_only    every id on --list (default FULL.LATEST) absent from --minimal (default MINIMAL) and not the mod under
             test (mandrake.rm.graffiti: the minimal rung is MINIMAL + Graffiti) -- counted, listed.
pool_members full-only mods that can put marks in the spree's pool: their About.xml names mandrake.rm.graffiti
             (a dependency or load rule -- ModExtension_Graffiti cannot be used without it) AND an .xml under
             the mod carries `ModExtension_Graffiti`. Each with the mark defNames found.
cleaning     full-only mods whose About name/description says clean/filth/tidy (they can remove marks the
             bars count, or change who cleans): a NAME MATCH, labelled so, never a behaviour claim.
camera       full-only mods whose About name/description says camera/zoom (they change the screenshots'
             framing): a NAME MATCH, likewise.
not_installed full-only ids with no folder in either mod root: their category is UNMEASURED, named, never "none".
"""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
MODLISTS = os.path.join(ROOT, "infrastructure", "state", "modlists")
FULL_LATEST = os.path.join(MODLISTS, "ModsConfig.FULL.LATEST.xml")
MINIMAL = os.path.join(MODLISTS, "ModsConfig.MINIMAL.xml")
GRAFFITI_ID = "mandrake.rm.graffiti"

CLEAN_RE = re.compile(r"\bclean|\bfilth|\btidy", re.I)
CAMERA_RE = re.compile(r"\bcamera|\bzoom", re.I)
DEF_RE = re.compile(r"<ThingDef\b.*?</ThingDef>", re.S)
NAME_RE = re.compile(r"<defName>([^<]+)</defName>")


def _about(root):
    """(name, description, raw About.xml text) or None when unreadable."""
    p = os.path.join(root, "About", "About.xml")
    try:
        raw = open(p, encoding="utf-8-sig", errors="replace").read()
        r = ET.fromstring(raw)
    except (OSError, ET.ParseError):
        return None
    return ((r.findtext("name") or "").strip(), (r.findtext("description") or "").strip(), raw)


def _pool_defs(root):
    """Mark defNames: ThingDefs carrying ModExtension_Graffiti in any .xml under root."""
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ("Textures", "Sounds", "Source", "Assemblies", ".git")]
        for f in fn:
            if not f.endswith(".xml"):
                continue
            try:
                txt = open(os.path.join(dp, f), encoding="utf-8-sig", errors="replace").read()
            except OSError:
                continue
            if "ModExtension_Graffiti" not in txt:
                continue
            for blk in DEF_RE.findall(txt):
                if "ModExtension_Graffiti" in blk:
                    m = NAME_RE.search(blk)
                    if m:
                        out.append(m.group(1))
    return sorted(set(out))


def differences(list_path=None, minimal_path=None, roots=None):
    """-> dict (see module doc). `roots` {packageId: [dirs]} defaults to modmanifest.installed_roots()."""
    if UTILS not in sys.path:
        sys.path.insert(0, UTILS)
    import modmanifest
    list_path, minimal_path = list_path or FULL_LATEST, minimal_path or MINIMAL
    full = [i.lower() for i in modmanifest.read_modsconfig(list_path)]
    mini = {i.lower() for i in modmanifest.read_modsconfig(minimal_path)}
    if roots is None:
        roots = modmanifest.installed_roots()
    only = [i for i in full if i not in mini and i != GRAFFITI_ID]
    res = {"list": os.path.basename(list_path), "minimal": os.path.basename(minimal_path),
           "full_count": len(full), "minimal_count": len(mini), "full_only_count": len(only),
           "full_only": only, "pool_members": [], "cleaning": [], "camera": [], "not_installed": [],
           "method": "About.xml name/description match for cleaning/camera (a NAME MATCH, not behaviour); "
                     "pool = About names %s AND an .xml carries ModExtension_Graffiti" % GRAFFITI_ID}
    for pid in only:
        dirs = roots.get(pid) or []
        if not dirs:
            res["not_installed"].append(pid)
            continue
        a = _about(dirs[0])
        if a is None:
            res["not_installed"].append(pid)
            continue
        name, desc, raw = a
        row = {"packageId": pid, "name": name}
        if GRAFFITI_ID in raw.lower():
            defs = _pool_defs(dirs[0])
            if defs:
                res["pool_members"].append(dict(row, markDefs=defs))
        text = name + "\n" + desc
        if CLEAN_RE.search(text):
            res["cleaning"].append(dict(row, matched=CLEAN_RE.search(text).group(0)))
        if CAMERA_RE.search(text):
            res["camera"].append(dict(row, matched=CAMERA_RE.search(text).group(0)))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list")
    ap.add_argument("--minimal")
    a = ap.parse_args(argv)
    d = differences(a.list, a.minimal)
    json.dump(d, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
