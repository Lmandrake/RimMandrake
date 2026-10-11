#!/usr/bin/env python3
"""Generate the techprint gate patch from the research manifest (TECHPRINT_FACTION_GATING_1).

Writes src/RimUtinni/ResearchRetag/Patches/RUT_TechprintGating.xml: for every non-cut manifest
row it sets ResearchProjectDef.techprintCount and heldByFactionCategoryTags exactly as the
manifest's two columns say (assign_techprint_holders.py fills them). Field names and the
pair rule are the 1.6 engine's (Verse/ResearchProjectDef.cs: techprintCount int,
heldByFactionCategoryTags List<string>; ConfigErrors rejects count 0 with tags and count>0
without), so a 0 row also loses any heldByFactionCategoryTags node it had.

Configurable Techprints (com.makeitso.configurabletechprints) rewrites both fields at
DefGenerator.GenerateImpliedDefs_PreResolve for every project WITHOUT its
NativeTechprint_DefModExtension (CanHaveAutoTechprints, ConfigurableTechprintsMod.cs:125),
handing it every trading faction's tag. Its own marking patch runs at ITS load position,
before this mod, so it never sees our values. Without the extension the gate is erased at
startup (live dump 2026-10-11: VFEP_Warcaskets held by 11 tags). So every row here also
gets that extension, inside a PatchOperationFindMod so nothing references the type when
the mod is absent. Rows not in the manifest are left to Configurable Techprints.

The Hutt fence is already in the manifest's tags; UtinniPatches' FactionCategoryTags_Compat
adds HuttCartel only where it is missing, so the two do not double it.

    python3 design/Jawa/research_review/build_techprint_patches.py           # write
    python3 design/Jawa/research_review/build_techprint_patches.py --check   # shipped XML == manifest?
"""
import argparse
import csv
import os
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_retag_patches import MANIFEST, REPO, RETIRED_SOURCE_MODS, def_xpath  # noqa: E402

OUT = os.path.join(REPO, "src/RimUtinni/ResearchRetag/Patches/RUT_TechprintGating.xml")
CT_MOD_NAME = "Configurable Techprints"
CT_EXT = "ConfigurableTechprints.DataTypes.NativeTechprint_DefModExtension"


def wanted():
    """{defName: (count, [tags])} for every row the patch must write."""
    with open(MANIFEST, encoding="utf-8") as fh:
        fh.readline()
        rows = list(csv.DictReader(fh))
    out = {}
    for r in rows:
        if r["fate"] == "cut" or r["techprintCount"] == "" or r["source_mod"] in RETIRED_SOURCE_MODS:
            continue
        tags = [t for t in r["heldByFactionCategoryTags"].split(";") if t]
        n = int(r["techprintCount"])
        if (n > 0) != bool(tags):
            sys.exit("manifest row %s breaks the engine pair rule (count=%d tags=%s)" % (r["defName"], n, tags))
        out[r["defName"]] = (n, tags)
    return out


def field(base, node, val):
    return """      <li Class="PatchOperationConditional">
        <xpath>%(b)s/%(n)s</xpath>
        <match Class="PatchOperationReplace">
          <xpath>%(b)s/%(n)s</xpath>
          <value>%(v)s</value>
        </match>
        <nomatch Class="PatchOperationAdd">
          <xpath>%(b)s</xpath>
          <value>%(v)s</value>
        </nomatch>
      </li>""" % {"b": base, "n": node, "v": val}


def block(dn, n, tags):
    base = def_xpath(dn)
    ops = [field(base, "techprintCount", "<techprintCount>%d</techprintCount>" % n)]
    if tags:
        ops.append(field(base, "heldByFactionCategoryTags", "<heldByFactionCategoryTags>%s</heldByFactionCategoryTags>"
                         % "".join("<li>%s</li>" % escape(t) for t in tags)))
    else:
        ops.append("""      <li Class="PatchOperationConditional">
        <xpath>%(b)s/heldByFactionCategoryTags</xpath>
        <match Class="PatchOperationRemove">
          <xpath>%(b)s/heldByFactionCategoryTags</xpath>
        </match>
      </li>""" % {"b": base})
    ops.append("""      <li Class="PatchOperationFindMod">
        <mods><li>%(m)s</li></mods>
        <match Class="PatchOperationConditional">
          <xpath>%(b)s[not(modExtensions/li[@Class="%(e)s"])]</xpath>
          <match Class="PatchOperationAddModExtension">
            <xpath>%(b)s</xpath>
            <value><li Class="%(e)s" /></value>
          </match>
        </match>
      </li>""" % {"b": base, "m": CT_MOD_NAME, "e": CT_EXT})
    return """  <Operation Class="PatchOperationConditional">
    <xpath>%s</xpath>
    <match Class="PatchOperationSequence">
      <operations>
%s
      </operations>
    </match>
  </Operation>""" % (base, "\n".join(ops))


def shipped():
    """{defName: (count, [tags])} as the shipped XML writes them."""
    got = {}
    for op in ET.parse(OUT).getroot().findall("Operation"):
        dn = op.findtext("xpath").split('defName="')[1].split('"')[0]
        n, tags = None, []
        for li in op.find("match/operations"):
            v = li.find("match/value")
            if v is None:
                continue
            for el in v:
                if el.tag == "techprintCount":
                    n = int(el.text)
                elif el.tag == "heldByFactionCategoryTags":
                    tags = [x.text for x in el]
        got[dn] = (n, tags)
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="compare the shipped XML with the manifest; write nothing")
    a = ap.parse_args()
    want = wanted()
    if not a.check:
        with open(OUT, "w", encoding="utf-8") as fh:
            fh.write('<?xml version="1.0" encoding="utf-8"?>\n<Patch>\n')
            fh.write("  <!-- GENERATED by design/Jawa/research_review/build_techprint_patches.py from\n"
                     "       research_manifest_draft.csv (heldByFactionCategoryTags, techprintCount).\n"
                     "       Do not hand-edit; change the manifest and regenerate. -->\n")
            fh.write("\n".join(block(dn, *want[dn]) for dn in sorted(want)))
            fh.write("\n</Patch>\n")
    got = shipped()
    diff = sorted(d for d in set(want) | set(got) if want.get(d) != got.get(d))
    held = sum(1 for n, _ in want.values() if n)
    print("%s: %d defs (%d techprinted, %d at 0)" % (os.path.relpath(OUT, REPO), len(got), held, len(want) - held))
    for d in diff[:20]:
        print("DIFF %s manifest=%s shipped=%s" % (d, want.get(d), got.get(d)))
    print("CHECK %s (%d differences)" % ("PASS" if not diff else "FAIL", len(diff)))
    return 1 if diff else 0


if __name__ == "__main__":
    sys.exit(main())
