#!/usr/bin/env python3
"""FLOWWORKS_CLIMBERS_REWIRE_NAMES_THAT_LEFT: every one of OUR defNames (RM_, RSW_, RUT_) that
Patches/Canals/FlowWorks_LadderClimbers.xml names is a ThingDef defined somewhere under src/.

Why: a patch that matches nothing logs nothing (CLAUDE.md). When a creature moves tier (RSW_X -> RM_X) the old name
in the climber list silently stops matching, and that creature never gets its ladder traits. Third-party names
(GR_, VGE_, ...) are not checked here: their defs are not in this repo.

Second check (the xpath, not only the name): each patch xpath is RUN (lxml, XPath 1.0 like the game's System.Xml) on the
top-level defs under src/, and every name of ours it lists must be SELECTED by it. A name defined under another element
(a HAR race is <AlienRace.ThingDef_AlienRace>, not <ThingDef>) passes the name check yet the patch skips it silently.

Exit 0: every name of ours matches a def and its xpath selects it. Exit 1: names that match nothing (each with the twin
that does exist), or names their xpath does not select (each with the element it is defined under).
Exit 2: could not look (the patch or src/ is missing, no defName was read, or lxml is missing).
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PATCH = os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "Patches", "Canals", "FlowWorks_LadderClimbers.xml")
OURS = re.compile(r"^(RM|RSW|RUT)_")


def defined_names(src_root, tops=None):
    """Every defName under src_root. With tops (a list), also appends (element tag, defName) for each top-level def of a
    <Defs> file, the nodes a patch xpath "Defs/..." walks."""
    names = set()
    for root, dirs, files in os.walk(src_root):
        dirs[:] = [d for d in dirs if d not in ("obj", "bin", ".git", "art_source")]
        for f in files:
            if f.endswith(".xml"):
                with open(os.path.join(root, f), encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
                names.update(re.findall(r"<defName>\s*([^<\s]+)\s*</defName>", text))
                if tops is not None and "<Defs" in text:
                    tops.extend(top_defs(text))
    return names


def top_defs(text):
    from lxml import etree
    try:
        root = etree.fromstring(text.encode("utf-8"), etree.XMLParser(recover=True, remove_comments=True))
    except etree.XMLSyntaxError:
        return []
    if root is None or root.tag != "Defs":
        return []
    out = []
    for el in root:
        if isinstance(el.tag, str):
            dn = el.findtext("defName")
            if dn and dn.strip():
                out.append((el.tag, dn.strip()))
    return out


def unselected(patch_text, tops, ours_defined):
    """Names of ours (defined somewhere) that an xpath of the patch lists but does not select, run on a <Defs> document
    of the top-level defs: [(name, tags it is defined under, xpath head)]."""
    from lxml import etree
    doc = etree.Element("Defs")
    for tag, dn in tops:
        etree.SubElement(etree.SubElement(doc, tag), "defName").text = dn
    tags = {}
    for tag, dn in tops:
        tags.setdefault(dn, set()).add(tag)
    bad = []
    for xp in re.findall(r"<xpath>(.*?)</xpath>", patch_text, re.S):
        listed = [n for n in re.findall(r'defName="([^"]+)"', xp) if n in ours_defined]
        got = {e.findtext("defName") for e in etree.ElementTree(doc).xpath("/" + xp.strip())}
        for n in listed:
            if n not in got:
                bad.append((n, sorted(tags.get(n, ())), xp.strip()[:40]))
    return bad


def main():
    if not os.path.isfile(PATCH):
        print("COULD NOT LOOK: %s is missing" % PATCH)
        return 2
    with open(PATCH, encoding="utf-8") as fh:
        patch_text = fh.read()
    named = sorted(set(re.findall(r'defName="([^"]+)"', patch_text)))
    ours = [n for n in named if OURS.match(n)]
    try:
        import lxml.etree  # noqa: F401
    except ImportError:
        print("COULD NOT LOOK: lxml is missing (pip install lxml)")
        return 2
    tops = []
    have = defined_names(os.path.join(ROOT, "src"), tops)
    if not ours or len(have) < 100 or len(tops) < 100:
        print("COULD NOT LOOK: %d names of ours in the patch, %d defs read under src/, %d top-level defs"
              % (len(ours), len(have), len(tops)))
        return 2
    bad = []
    for n in ours:
        if n not in have:
            base = OURS.sub("", n)
            twins = [p + "_" + base for p in ("RM", "RSW", "RUT") if p + "_" + base in have]
            bad.append("%s matches no def (twin: %s)" % (n, ", ".join(twins) or "none"))
    skipped = unselected(patch_text, tops, set(n for n in ours if n in have))
    for n, tags, head in skipped:
        bad.append("%s is defined as <%s>; the xpath (%s...) does not select it" % (n, ", ".join(tags) or "?", head))
    if bad:
        print("FAIL: %d finding(s) on %d names of ours (%d top-level defs read)" % (len(bad), len(ours), len(tops)))
        for b in bad:
            print("  " + b)
        return 1
    print("PASS: %d of %d names of ours match a def and are selected by their xpath (%d top-level defs read)"
          % (len(ours), len(ours), len(tops)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
