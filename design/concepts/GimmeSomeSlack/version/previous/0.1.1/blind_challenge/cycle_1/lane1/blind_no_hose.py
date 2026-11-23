#!/usr/bin/env python3
"""Blind lane 1, GimmeSomeSlack 0.1.1, cycle 1: the two offline bars no_hose and no_hose_in_gss, from their words alone.

Bar words: "GSS draws no hose or pipe: hoses and reels live in FlowWorks" (no_hose); "The reader of the mod's defs and
source finds no hose, reel or pipe drawing in Gimme Some Slack ... It must not read as a hose def or texture left
behind" (no_hose_in_gss; its false pass: "the scan matching only def names, missing a texture folder").

    python3 blind_no_hose.py [--mod-root <dir>]      prints one JSON row per line; exit 0 = no FAIL row

What ships: About, Defs, Patches, Textures, Languages, Sounds, Assemblies, LoadFolders.xml and Source minus Source/SelfTest
(the C# the build compiles). Words are matched as identifier words (camelCase / snake / path parts split), so "whose" and
"those" never match "hose". Written by the blind judge before reading any builder test.
"""
import argparse, json, os, re, shutil, sys, tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")
SHIP_DIRS = ["About", "Defs", "Patches", "Textures", "Languages", "Sounds", "Assemblies", "Source"]
HOSE = {"hose", "hoses", "reel", "reels", "hosereel", "hosereels"}
PIPE = {"pipe", "pipes"}
WORD = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+")


def words(s):
    out = []
    for tok in re.split(r"[^A-Za-z0-9]+", s or ""):
        out += [w.lower() for w in WORD.findall(tok)]
    return out


def has(s, vocab):
    return any(w in vocab for w in words(s))


def shipped_files(root):
    for d in SHIP_DIRS:
        base = os.path.join(root, d)
        for dp, dn, fn in os.walk(base):
            if os.path.relpath(dp, root).replace("\\", "/").startswith("Source/SelfTest"):
                dn[:] = []
                continue
            dn[:] = [x for x in dn if not (d == "Source" and x == "SelfTest" and dp == base)]
            for f in fn:
                yield os.path.relpath(os.path.join(dp, f), root).replace("\\", "/")
    if os.path.exists(os.path.join(root, "LoadFolders.xml")):
        yield "LoadFolders.xml"


DEF_FIELDS = ("defName", "texPath", "thingClass", "graphicClass", "compClass", "workerClass", "driverClass", "jobClass",
              "label", "category", "designationCategory", "drawerType", "iconPath", "uiIconPath")


def scan(root):
    files = list(shipped_files(root))
    xmls = [f for f in files if f.endswith(".xml") and (f.startswith("Defs/") or f.startswith("Patches/"))]
    texs = [f for f in files if f.startswith("Textures/")]
    cs = [f for f in files if f.endswith(".cs") and f.startswith("Source/")]
    dlls = [f for f in files if f.endswith(".dll") and f.startswith("Assemblies/")]
    rows = []
    # 1. defs and patches: every def element's name, class and texture fields, every Class attribute, every patch xpath/value text
    hose_defs, pipe_defs, parse_fail, ndefs = [], [], [], 0
    for f in xmls:
        try:
            tree = ET.parse(os.path.join(root, f))
        except ET.ParseError as e:
            parse_fail.append(f + ": " + str(e)); continue
        for el in tree.iter():
            vals = []
            if el.find("defName") is not None:
                ndefs += 1
                vals.append(("tag", el.tag))
            for k, v in el.attrib.items():
                if k in ("Class", "ParentName", "Name"): vals.append((k, v))
            if el.tag in DEF_FIELDS or el.tag in ("xpath", "li", "value"):
                if el.text and el.text.strip() and len(el.text.strip()) < 300: vals.append((el.tag, el.text.strip()))
            for k, v in vals:
                if has(v, HOSE): hose_defs.append("%s <%s> %s=%s" % (f, el.tag, k, v))
                elif has(v, PIPE) and el.tag not in ("li", "value", "xpath"): pipe_defs.append("%s <%s> %s=%s" % (f, el.tag, k, v))
    rows.append(dict(id="ns_defs_no_hose_reel", bars=["no_hose", "no_hose_in_gss"], kind="fixed",
                     verdict="FAIL" if hose_defs or parse_fail or not ndefs else "PASS", cases=len(xmls),
                     detail="%d def/patch files, %d defs parsed; hose/reel hits %d %s; parse failures %s" % (
                         len(xmls), ndefs, len(hose_defs), hose_defs[:8], parse_fail[:4])))
    rows.append(dict(id="ns_defs_no_pipe_def", bars=["no_hose", "no_hose_in_gss"], kind="fixed",
                     verdict="FAIL" if pipe_defs else "PASS", cases=ndefs,
                     detail="def name/class/texture fields naming a pipe: %d %s" % (len(pipe_defs), pipe_defs[:8])))
    # 2. textures: the folder the false pass names
    bad_tex = [t for t in texs if has(t, HOSE | PIPE)]
    rows.append(dict(id="ns_textures_no_hose_reel_pipe", bars=["no_hose", "no_hose_in_gss"], kind="fixed",
                     verdict="FAIL" if bad_tex or not texs else "PASS", cases=len(texs),
                     detail="%d texture files under Textures/; hose/reel/pipe path words: %d %s" % (len(texs), len(bad_tex), bad_tex[:8])))
    # 3. C#: declared types, texture-path string literals
    decl = re.compile(r"\b(?:class|struct|enum|interface|record)\s+([A-Za-z_][A-Za-z0-9_]*)")
    lit = re.compile(r'"((?:[^"\\]|\\.)*)"')
    hose_types, pipe_types, hose_lits, pipe_lits, hose_idents = [], [], [], [], {}
    pipe_files = {}
    for f in cs:
        src = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
        code = re.sub(r"//.*", "", src)
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
        for m in decl.finditer(code):
            n = m.group(1)
            if has(n, HOSE): hose_types.append(f + ":" + n)
            elif has(n, PIPE): pipe_types.append(f + ":" + n)
        for m in lit.finditer(code):
            s = m.group(1)
            if "/" in s and not " " in s:
                if has(s, HOSE): hose_lits.append(f + ":" + s)
                elif has(s, PIPE): pipe_lits.append(f + ":" + s)
        for m in re.finditer(r"[A-Za-z_][A-Za-z0-9_]*", lit.sub('""', code)):
            if has(m.group(0), HOSE): hose_idents[f + ":" + m.group(0)] = 1
            if has(m.group(0), PIPE): pipe_files[f] = pipe_files.get(f, 0) + 1
    rows.append(dict(id="ns_csharp_no_hose_reel_type", bars=["no_hose", "no_hose_in_gss"], kind="fixed",
                     verdict="FAIL" if hose_types or hose_lits or hose_idents or not cs else "PASS", cases=len(cs),
                     detail="%d shipped .cs files (SelfTest excluded); hose/reel types %s; texture literals %s; code identifiers %s" % (
                         len(cs), hose_types[:6], hose_lits[:6], list(hose_idents)[:8])))
    rows.append(dict(id="ns_csharp_no_pipe_texture_literal", bars=["no_hose", "no_hose_in_gss"], kind="fixed",
                     verdict="FAIL" if pipe_lits else "PASS", cases=len(cs),
                     detail="path-like string literals naming a pipe: %s" % pipe_lits[:8]))
    # 4. the shipped DLL: type and member names in its metadata
    hose_dll, ndll = [], 0
    for f in dlls:
        b = open(os.path.join(root, f), "rb").read()
        ndll += 1
        for m in re.finditer(rb"[A-Za-z_][A-Za-z0-9_./]{2,}", b):
            s = m.group(0).decode("ascii", "replace")
            if has(s, HOSE): hose_dll.append(f + ":" + s)
    hose_dll = sorted(set(hose_dll))
    rows.append(dict(id="ns_dll_no_hose_reel_name", bars=["no_hose", "no_hose_in_gss"], kind="fixed",
                     verdict="FAIL" if hose_dll or not ndll else "PASS", cases=ndll,
                     detail="%d shipped DLLs; hose/reel names in metadata: %s" % (ndll, hose_dll[:10])))
    # 5. pipe drawing in code. Lane 2 (cycle 1, after reading the callers) settled the rule: GSS's aerial engine draws a pipe span
    # only for an anchor whose def sets lineKind Pipe (AerialMaterials.SpanMats/PipeMats), with that def's spanTexPath art. So GSS
    # draws a pipe of its own exactly when one of ITS defs or patches sets a pipe line kind or names pipe art, or it ships pipe
    # art (rows above). Pipe words in code that serves another mod's pipe poles are listed, not failed.
    pipe_kind = []
    for f in xmls:
        try:
            tree = ET.parse(os.path.join(root, f))
        except ET.ParseError:
            continue
        for el in tree.iter():
            if isinstance(el.tag, str) and el.tag in ("lineKind", "spanTexPath") and el.text and (el.tag == "spanTexPath" or has(el.text, PIPE)):
                pipe_kind.append("%s <%s>%s" % (f, el.tag, el.text.strip()))
    decided = not pipe_kind and not pipe_defs and not bad_tex and not pipe_lits
    rows.append(dict(id="ns_pipe_words_in_code", bars=["no_hose", "no_hose_in_gss"], kind="fixed",
                     verdict="PASS" if decided else "FAIL", cases=len(cs) + len(xmls),
                     detail="GSS defs/patches setting a pipe line kind or pipe span art: %s. " % (pipe_kind[:6] or "none") +
                     "pipe-named types %s; files with pipe-word identifiers (code serving FlowWorks' pipe-pole defs, which carry "
                            "their own art) %s" % (pipe_types[:8], sorted(pipe_files.items(), key=lambda x: -x[1])[:10])))
    return rows


def self_check():
    """The scanner must see a planted hose: a def, a texture-only reel (the false pass), a class, a DLL name; and must not
    fire on prose words ("whose", "those")."""
    d = tempfile.mkdtemp(prefix="gss_nohose_plant_")
    try:
        def w(p, s, mode="w"):
            os.makedirs(os.path.dirname(os.path.join(d, p)), exist_ok=True)
            open(os.path.join(d, p), mode).write(s)
        clean = {"Defs/A.xml": "<Defs><ThingDef><defName>RM_Mast</defName><label>whose mast, those wires</label></ThingDef></Defs>",
                 "Textures/RimMandrake/Cord.png": "x", "Source/A.cs": "class Cord { /* whose hose comment */ string s = \"those\"; }",
                 "Source/SelfTest/T.cs": "class HoseReelTest {}", "Assemblies/A.dll": b"\x00Cord\x00Mast\x00"}
        for p, s in clean.items(): w(p, s, "wb" if isinstance(s, bytes) else "w")
        base = {r["id"]: r["verdict"] for r in scan(d)}
        results = {"clean_tree": all(v == "PASS" for v in base.values())}
        plants = {
            "def": ("Defs/B.xml", "<Defs><ThingDef><defName>RM_HoseReel</defName></ThingDef></Defs>", "ns_defs_no_hose_reel"),
            "texture_only": ("Textures/RimMandrake/Hoses/HoseCoil.png", "x", "ns_textures_no_hose_reel_pipe"),
            "pipe_texture": ("Textures/RimMandrake/Pipe_Straight.png", "x", "ns_textures_no_hose_reel_pipe"),
            "class": ("Source/H.cs", "public class CompHoseDrawer {}", "ns_csharp_no_hose_reel_type"),
            "dll": ("Assemblies/A.dll", b"\x00Cord\x00RM_HoseReel\x00", "ns_dll_no_hose_reel_name"),
            "texpath_literal": ("Source/P.cs", "class P { string t = \"RimMandrake/Pipes/PipeRun\"; }", "ns_csharp_no_pipe_texture_literal"),
            "pipe_kind_mast": ("Defs/C.xml", "<Defs><ThingDef><defName>RM_Mast2</defName><modExtensions><li><lineKind>Pipe</lineKind></li></modExtensions></ThingDef></Defs>", "ns_pipe_words_in_code"),
        }
        for name, (p, s, row) in plants.items():
            full = os.path.join(d, p); had = os.path.exists(full); old = open(full, "rb").read() if had else None
            w(p, s, "wb" if isinstance(s, bytes) else "w")
            got = {r["id"]: r["verdict"] for r in scan(d)}
            results[name] = got.get(row) == "FAIL"
            if had: open(full, "wb").write(old)
            else: os.remove(full)
        return dict(id="ns_scanner_sees_planted_hoses", bars=["no_hose", "no_hose_in_gss"], kind="fixed",
                    verdict="PASS" if all(results.values()) else "FAIL", cases=len(results),
                    detail="planted in a scratch tree, each must FAIL its row and the clean tree (prose 'whose'/'those', a SelfTest "
                           "class) must PASS: %s" % json.dumps(results))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mod-root", default=MOD)
    a = ap.parse_args()
    rows = [self_check()] + scan(a.mod_root)
    for r in rows: print(json.dumps(r))
    sys.exit(1 if any(r["verdict"] == "FAIL" for r in rows) else 0)


if __name__ == "__main__":
    main()
