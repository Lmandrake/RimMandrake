#!/usr/bin/env python3
"""
Selftest: the retired donors' world-tile mutators and landmarks stay ported.

Owner, 2026-10-19: "Reproduce the mutators into our own code, then proceed with deprecation of the donors."
Mapping: design/RimMandrake/retired_mutators_port_map.json (doc: design/RimMandrake/retired_mutators_port_2026-10-19.md).

Proves, offline:
  1. every mapped port (`new`) exists in src/ as a def of the right element type (TileMutatorDef / LandmarkDef), and
     every RimMandrake.EnvironmentalHazards.* class a port names is declared in the EnvironmentalHazards source;
  2. NO def or patch of ours references a retired donor mutator/landmark: no element text, element tag
     (mutatorChances children) or attribute value under src/**/Defs or src/**/Patches equals a retired name.
     Retired names = the map's keys plus every TileMutatorDef/LandmarkDef the 2026-08-29 DefDump capture
     attributes to a retired package (when the capture is readable). XML comments are provenance and are skipped
     (ElementTree drops them);
  3. the save-rename hash simulation in save_donor_rewrite.py reproduces every live TileMutatorDef shortHash of the
     donor-free capture and gives each port a distinct hash (skipped, and said so, when the capture is unreadable);
  4. the instrument can see: a planted def naming AB_TarLakes is caught by the same scan.

    python3 src/RimMandrake/Utils/selftest_retired_mutator_ports.py
"""
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
MAP = os.path.join(ROOT, "design", "RimMandrake", "retired_mutators_port_map.json")
EH_SRC = os.path.join(ROOT, "src", "RimMandrake", "EnvironmentalHazards", "Source")
CAPTURES = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/captures/"

fails, notes = [], []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def xml_files(kind):
    return [p for p in glob.glob(os.path.join(ROOT, "src", "**", kind, "**", "*.xml"), recursive=True)]


def our_defs():
    out = {}
    for p in xml_files("Defs"):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in root:
            n = d.findtext("defName")
            if n:
                out.setdefault((d.tag, n), p)
    return out


def retired_names(mapping):
    names = set(mapping["TileMutatorDef"]) | set(mapping["LandmarkDef"])
    try:
        retired = {r["packageId"].lower() for r in json.load(open(os.path.join(ROOT, "infrastructure", "state", "facts", "retired_mods.json")))["retired"]}
        for t in ("TileMutatorDef", "LandmarkDef"):
            for r in json.load(open(os.path.join(CAPTURES, "2026-08-29T13-30-02Z", "defs", t + ".json")))["defs"]:
                if (r.get("packageId") or "").lower() in retired:
                    names.add(r["defName"])
    except (OSError, ValueError, KeyError) as e:
        notes.append("capture/retired list unreadable (%s): scanning the map's %d names only" % (e.__class__.__name__, len(names)))
    return names


def scan(paths, bad):
    hits = []
    for p in paths:
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for el in root.iter():
            vals = [el.tag, (el.text or "").strip()] + list(el.attrib.values())
            for v in vals:
                if v in bad:
                    hits.append((os.path.relpath(p, ROOT), v))
    return hits


def main():
    mapping = json.load(open(MAP))
    ours = our_defs()

    # 1. ports exist
    for t in ("TileMutatorDef", "LandmarkDef"):
        for old, r in sorted(mapping[t].items()):
            if r["new"]:
                check((t, r["new"]) in ours, "%s %s -> %s exists in src (%s)" % (t, old, r["new"], r["status"]))
            else:
                notes.append("%s %s: not reproduced (%s)" % (t, old, r["how"]))
    eh = "".join(open(p, encoding="utf-8").read() for p in glob.glob(os.path.join(EH_SRC, "*.cs")))
    named = set()
    for p in xml_files("Defs"):
        if "RetiredMutatorPorts" in p or p.endswith("RSW_DonorPack_WildPlantMutators.xml"):
            named |= set(re.findall(r"RimMandrake\.EnvironmentalHazards\.(\w+)", open(p, encoding="utf-8").read()))
    for c in sorted(named):
        check(re.search(r"\bclass %s\b" % c, eh) is not None, "class RimMandrake.EnvironmentalHazards.%s is declared" % c)

    # 2. nothing of ours references a retired name
    bad = retired_names(mapping)
    hits = scan(xml_files("Defs") + xml_files("Patches"), bad)
    for f, v in hits[:20]:
        print("   hit: %s names %s" % (f, v))
    check(not hits, "no def or patch in src names one of %d retired mutator/landmark defNames (%d hits)" % (len(bad), len(hits)))

    # 3. hash simulation
    try:
        import save_donor_rewrite as sdr
        hm = sdr.mutator_hash_map(mapping)
        new_hashes = [nh for (_, n, nh) in hm.values() if n]
        check(len(set(new_hashes)) == len(new_hashes), "ported mutators get %d distinct predicted shortHashes" % len(new_hashes))
    except SystemExit as e:
        check(False, "hash simulation refused: %s" % e)
    except (OSError, ValueError) as e:
        notes.append("hash simulation SKIPPED, capture unreadable: %s" % e)

    # 4. the instrument can see
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as fh:
        fh.write('<Defs><LandmarkDef><defName>X</defName><mutatorChances><AB_TarLakes Required="True"/></mutatorChances>'
                 '</LandmarkDef><TileMutatorDef><defName>Y</defName><plantKinds><li>Z</li></plantKinds></TileMutatorDef></Defs>')
    planted = scan([fh.name], bad)
    os.unlink(fh.name)
    check([v for _, v in planted] == ["AB_TarLakes"], "PLANTED: a def naming AB_TarLakes is caught, nothing else is")

    for n in notes:
        print("NOTE " + n)
    print("%s: %d failure(s)" % ("FAIL" if fails else "PASS", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
