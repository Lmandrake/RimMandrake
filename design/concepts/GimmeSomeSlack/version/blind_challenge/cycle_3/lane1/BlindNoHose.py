#!/usr/bin/env python3
"""Blind lane 1, cycle 3: the two offline bars no_hose (record row) and no_hose_in_gss (tree leaf), from their words only.

Bar words: "No hose, reel or pipe is drawn by this mod" (sheet); "no ThingDef, texture or class for hoses or reels under
src/RimMandrake/GimmeSomeSlack" (oracle); false pass "the scan matching only def names, missing a texture folder";
red "a hose reel def still ships in GSS"; record row: "GSS draws no hose or pipe: hoses and reels live in FlowWorks".

So the scan covers every place a drawn hose/reel/pipe could ship from: Defs (every def, not only defName: class,
texPath, comps), Patches (what they add), Textures (files AND folders), C# type names and texture-path literals under
Source/ (SelfTest excluded: it is not shipped drawing), and the shipped DLL's type names and string literals (handed in
by the C# harness, which reads its metadata). "Pipe" in prose (a mast "of scrap pipe", a "pipe slot" a cord avoids) is
not a drawn pipe: prose hits are INFO, never FAIL. Word match is camel/word-start aware, so "whose" and "freely" never hit.

    python3 BlindNoHose.py --root <mod dir> [--dll-types <file>] [--dll-strings <file>]
Prints one JSON row per line.
"""
import argparse, json, os, re, sys
import xml.etree.ElementTree as ET

WORD = re.compile(r"(?:(?<![A-Za-z])(?:hose|reel|pipe)|Hose|Reel|Pipe|HOSE|REEL|PIPE)")
HOSE_REEL = re.compile(r"(?:(?<![A-Za-z])(?:hose|reel)|Hose|Reel|HOSE|REEL)")
TEX_LIT = re.compile(r'"([A-Za-z0-9_]+(?:/[A-Za-z0-9_]+)+)"')   # a "A/B/C" literal: a texture or graphic path
TYPE_DECL = re.compile(r"\b(class|struct|enum|interface)\s+([A-Za-z_][A-Za-z0-9_]*)")
PROSE_TAGS = {"description", "label", "jobString", "reportString", "text", "letterText", "letterLabel", "comment"}

def row(id_, bars, kind, verdict, cases, detail):
    print(json.dumps({"id": id_, "bars": bars, "kind": kind, "verdict": verdict, "cases": cases, "detail": detail}))

def files(root, sub, exts):
    base = os.path.join(root, sub)
    for dp, dns, fns in os.walk(base):
        for f in fns:
            if not exts or os.path.splitext(f)[1].lower() in exts:
                yield os.path.join(dp, f)

def scan_xml(root, sub):
    """Every element and attribute value in every XML file; hits split into structural (FAIL) and prose (INFO)."""
    hard, soft, n = [], [], 0
    for p in files(root, sub, {".xml"}):
        n += 1
        rel = os.path.relpath(p, root)
        try:
            tree = ET.parse(p)
        except ET.ParseError as e:
            hard.append("%s: unparseable (%s)" % (rel, e)); continue
        for el in tree.iter():
            tag = el.tag if isinstance(el.tag, str) else ""
            vals = [("tag", tag)] + [("@" + k, v) for k, v in el.attrib.items()] + [("text", (el.text or "").strip())]
            for kind, v in vals:
                if not v or not WORD.search(v): continue
                where = "%s <%s> %s=%r" % (rel, tag, kind, v[:120])
                (soft if tag in PROSE_TAGS and kind == "text" and " " in v else hard).append(where)
        # comments are not parsed by ET: they are prose by definition, never shipped drawing
    return n, hard, soft

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--dll-types"); ap.add_argument("--dll-strings")
    a = ap.parse_args()
    bars = ["no_hose", "no_hose_in_gss"]

    n, hard, soft = scan_xml(a.root, "Defs")
    row("NH_DEFS_NO_HOSE_REEL_PIPE", bars, "fixed", "FAIL" if hard else "PASS", n,
        ("%d def files; structural hits: %s" % (n, hard[:12])) if hard else "%d def files, every element/attribute/value scanned; 0 structural hose|reel|pipe hits" % n)
    row("NH_DEFS_PROSE_INFO", bars, "info", "INFO", len(soft), "prose mentions (not drawing): %s" % soft[:8])
    n, hard, soft = scan_xml(a.root, "Patches")
    row("NH_PATCHES_NO_HOSE_REEL_PIPE", bars, "fixed", "FAIL" if hard else "PASS", n,
        ("%d patch files; structural hits: %s" % (n, hard[:12])) if hard else "%d patch files scanned; 0 structural hits" % n)

    tex = [os.path.relpath(p, a.root) for p in files(a.root, "Textures", None)]
    dirs = sorted({os.path.dirname(t) for t in tex})
    hits = [t for t in tex + dirs if WORD.search(t)]
    row("NH_TEXTURES_FILES_AND_FOLDERS", bars, "fixed", "FAIL" if hits or not tex else "PASS", len(tex) + len(dirs),
        ("hits: %s" % hits[:12]) if hits else ("no texture files found: the instrument is blind" if not tex else
        "%d texture files in %d folders, names and folders scanned; 0 hits" % (len(tex), len(dirs))))

    src = [p for p in files(a.root, "Source", {".cs"}) if os.sep + "SelfTest" + os.sep not in p]
    types, lits, pipe_types = [], [], []
    for p in src:
        t = open(p, encoding="utf-8-sig", errors="replace").read()
        rel = os.path.relpath(p, a.root)
        for m in TYPE_DECL.finditer(t):
            nm = m.group(2)
            if HOSE_REEL.search(nm): types.append("%s %s" % (rel, nm))
            elif WORD.search(nm): pipe_types.append("%s %s" % (rel, nm))
        for m in TEX_LIT.finditer(t):
            if WORD.search(m.group(1)): lits.append("%s %r" % (rel, m.group(1)))
    row("NH_SOURCE_NO_HOSE_REEL_TYPES", bars, "fixed", "FAIL" if types or not src else "PASS", len(src),
        ("hose/reel type names: %s" % types[:12]) if types else "%d shipped .cs files (SelfTest excluded); 0 hose/reel types" % len(src))
    row("NH_SOURCE_NO_PIPE_TEXTURE_LITERALS", bars, "fixed", "FAIL" if lits else "PASS", len(src),
        ("texture-path literals naming hose/reel/pipe: %s" % lits[:12]) if lits else "0 texture-path literals naming hose|reel|pipe")
    row("NH_SOURCE_PIPE_TYPES_INFO", bars, "info", "INFO", len(pipe_types),
        "type names with Pipe (lane 2 must decide whether any draws a pipe): %s" % pipe_types[:12])

    if a.dll_types:
        names = [l.strip() for l in open(a.dll_types) if l.strip()]
        bad = [x for x in names if HOSE_REEL.search(x)]
        pipe = [x for x in names if not HOSE_REEL.search(x) and WORD.search(x)]
        row("NH_DLL_NO_HOSE_REEL_TYPES", bars, "fixed", "FAIL" if bad or not names else "PASS", len(names),
            ("shipped DLL types: %s" % bad[:12]) if bad else ("no types read: blind" if not names else
            "%d types in the shipped DLL, 0 hose/reel names; Pipe-named: %s" % (len(names), pipe[:8])))
    else:
        row("NH_DLL_NO_HOSE_REEL_TYPES", bars, "fixed", "UNSETTLED", 0, "no --dll-types given")
    if a.dll_strings:
        strs = [l.rstrip("\n") for l in open(a.dll_strings)]
        bad = [s for s in strs if TEX_LIT.fullmatch('"%s"' % s) and WORD.search(s)]
        row("NH_DLL_NO_PIPE_TEXTURE_STRINGS", bars, "fixed", "FAIL" if bad or not strs else "PASS", len(strs),
            ("texture-path strings in the shipped DLL naming hose/reel/pipe: %s" % bad[:12]) if bad else
            ("no strings read: blind" if not strs else "%d user strings in the DLL; 0 texture paths naming hose|reel|pipe" % len(strs)))
    else:
        row("NH_DLL_NO_PIPE_TEXTURE_STRINGS", bars, "fixed", "UNSETTLED", 0, "no --dll-strings given")

if __name__ == "__main__":
    main()
