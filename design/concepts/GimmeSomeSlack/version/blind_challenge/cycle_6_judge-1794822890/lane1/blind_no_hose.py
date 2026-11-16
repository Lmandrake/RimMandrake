#!/usr/bin/env python3
"""Blind lane 1, GimmeSomeSlack cycle 6: the no-hose bars (no_hose, no_hose_in_gss) from their words alone.

Bar (tree.json no_hose_in_gss): "The reader of the mod's defs and source finds no hose, reel or pipe drawing in Gimme Some
Slack: it draws power cords only, hoses live in FlowWorks." Oracle: "offline scan: no ThingDef, texture or class for hoses or
reels under src/RimMandrake/GimmeSomeSlack". False pass: "the scan matching only def names, missing a texture folder".
Record row no_hose: "GSS draws no hose or pipe: hoses and reels live in FlowWorks".

    python3 blind_no_hose.py [--mod-root <dir>] [--selfcheck]
Prints one JSON row per line. Exit 0 = no FAIL row. --selfcheck plants a hose into a temp copy one way at a time and
proves the matching row turns FAIL (the instrument can see)."""
import argparse, json, os, re, shutil, sys, tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")
BARS = ["no_hose", "no_hose_in_gss"]
HOSE = re.compile(r"(?i)hose|reel")
HOSE_WORD = re.compile(r"(?i)\b(flexible[- ]pipes?|hoses?|hose[- ]?reels?|reels?)\b")
PIPE = re.compile(r"(?i)pipe")
DEF_ID_TAGS = {"defName", "thingClass", "texPath", "compClass", "workerClass", "graphicClass", "drawerType", "placeWorkers", "li"}
TEXT_TAGS = {"label", "description", "reportString", "jobString", "labelShort", "text", "letterText", "letterLabel"}


def content_roots(mod):
    """Every folder the game may load from: the mod root, Common/, version folders (1.x), and LoadFolders.xml entries."""
    roots = [mod]
    for name in sorted(os.listdir(mod)):
        p = os.path.join(mod, name)
        if os.path.isdir(p) and (re.fullmatch(r"\d+\.\d+", name) or name == "Common"):
            roots.append(p)
    lf = os.path.join(mod, "LoadFolders.xml")
    if os.path.isfile(lf):
        try:
            for li in ET.parse(lf).getroot().iter("li"):
                if li.text and li.text.strip() not in ("/", ""):
                    p = os.path.join(mod, li.text.strip().strip("/"))
                    if os.path.isdir(p) and p not in roots:
                        roots.append(p)
        except ET.ParseError:
            pass
    return roots


def files_under(d, exts=None, skip=()):
    for dp, dn, fn in os.walk(d):
        dn[:] = [x for x in dn if os.path.join(dp, x) not in skip and x not in ("obj", "bin")]
        for f in fn:
            if exts is None or os.path.splitext(f)[1].lower() in exts:
                yield os.path.join(dp, f)


def cs_files(mod):
    """C# that compiles into the shipped assembly: Source/ (minus SelfTest, test code) plus every Compile Include the
    csproj pulls in from outside the folder (the shared slack geometry)."""
    src = os.path.join(mod, "Source")
    out = set()
    if os.path.isdir(src):
        out.update(files_under(src, {".cs"}, skip={os.path.join(src, "SelfTest")}))
        for proj in files_under(src, {".csproj"}):
            for m in re.finditer(r'<Compile Include="([^"]+)"', open(proj, encoding="utf-8", errors="replace").read()):
                p = os.path.normpath(os.path.join(os.path.dirname(proj), m.group(1).replace("\\", "/")))
                if os.path.isfile(p) and "SelfTest" not in p:
                    out.add(p)
    for r in content_roots(mod)[1:]:
        out.update(files_under(r, {".cs"}))
    return sorted(out)


def strip_cs_comments(s):
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
    return re.sub(r"//[^\n]*", " ", s)


def cs_literals(code):
    return [m.group(1) for m in re.finditer(r'"((?:[^"\\\n]|\\.)*)"', code)]


def sentence_ok(text, m):
    """A hose word is fine in player text when its sentence points at FlowWorks (the move) or names a port of another
    building (a cord avoids it). Anything else claims GSS has a hose."""
    a = max(text.rfind(".", 0, m.start()), text.rfind("\n", 0, m.start())) + 1
    b = min([x for x in (text.find(".", m.end()), text.find("\n", m.end())) if x >= 0] or [len(text)])
    sent = text[a:b]
    return bool(re.search(r"FlowWorks|\bports?\b", sent))


def scan(mod):
    rows = []
    roots = content_roots(mod)
    rel = lambda p: os.path.relpath(p, mod)

    # 1. textures, in every content root (the false pass: a texture folder missed)
    tex = []
    for r in roots:
        for d in ("Textures",):
            if os.path.isdir(os.path.join(r, d)):
                tex += [rel(p) for p in files_under(os.path.join(r, d))]
    bad = [p for p in tex if HOSE.search(p) or PIPE.search(p)]
    rows.append(dict(id="NH_TEXTURES", kind="fixed", verdict="FAIL" if bad else "PASS", cases=len(tex),
                     detail=("%d texture files in %d content roots; " % (len(tex), len(roots))) + ("hose/reel/pipe art: %s" % bad[:6] if bad else "no path names a hose, reel or pipe")))

    # 2. defs and patches, parsed as XML, every content root
    xmls, hits, pipe_text = [], [], []
    for r in roots:
        for d in ("Defs", "Patches"):
            if os.path.isdir(os.path.join(r, d)):
                xmls += list(files_under(os.path.join(r, d), {".xml"}))
    parse_err = []
    for p in xmls:
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError as e:
            parse_err.append(rel(p) + ": " + str(e)); continue
        for el in root.iter():
            vals = [v for k, v in el.attrib.items() if k in ("Name", "ParentName", "Class")]
            if el.tag in DEF_ID_TAGS and el.text and el.text.strip() and not (el.tag == "li" and " " in el.text.strip()):
                vals.append(el.text.strip())
            if HOSE.search(el.tag): vals.append("<" + el.tag + ">")
            for v in vals:
                if HOSE.search(v) or (el.tag != "li" and PIPE.search(v)):
                    hits.append("%s: %s" % (rel(p), v))
            if el.tag in TEXT_TAGS and el.text:
                for m in HOSE_WORD.finditer(el.text):
                    if not sentence_ok(el.text, m): hits.append("%s: <%s> %r" % (rel(p), el.tag, el.text.strip()[:90]))
                if PIPE.search(el.text): pipe_text.append("%s <%s>: %s" % (rel(p), el.tag, el.text.strip()[:90]))
    rows.append(dict(id="NH_DEFS_PATCHES", kind="fixed", verdict="FAIL" if hits or parse_err else "PASS", cases=len(xmls),
                     detail="%d def/patch files parsed as XML; " % len(xmls) + ("hose/reel/pipe ids or hose text: %s" % hits[:6] if hits else "no defName, class, texPath or ParentName names a hose, reel or pipe; no label/description claims a hose")
                     + ("; parse errors %s" % parse_err[:3] if parse_err else "")))
    rows.append(dict(id="NH_DEF_PIPE_WORDS_INFO", kind="info", verdict="INFO", cases=len(pipe_text),
                     detail="def text using the word pipe (material or ports, not a drawn pipe): %s" % pipe_text[:6]))

    # 3. C# types compiled into the assembly
    cs = cs_files(mod)
    types, pipe_types, literal_hits, literal_ok = [], [], [], []
    for p in cs:
        code = strip_cs_comments(open(p, encoding="utf-8", errors="replace").read())
        for m in re.finditer(r"\b(class|struct|enum|interface|record)\s+([A-Za-z_][A-Za-z0-9_]*)", code):
            if HOSE.search(m.group(2)): types.append("%s: %s %s" % (rel(p), m.group(1), m.group(2)))
            elif PIPE.search(m.group(2)): pipe_types.append("%s: %s" % (rel(p), m.group(2)))
        for lit in cs_literals(code):
            for m in HOSE_WORD.finditer(lit):
                (literal_ok if sentence_ok(lit, m) else literal_hits).append("%s: %r" % (os.path.basename(p), lit[:100]))
            if re.search(r"(?i)Textures?/[^\"]*(hose|reel)|(hose|reel)[^\"]*\.png", lit): literal_hits.append("%s: texture path %r" % (os.path.basename(p), lit[:100]))
    rows.append(dict(id="NH_CS_TYPES", kind="fixed", verdict="FAIL" if types else "PASS", cases=len(cs),
                     detail="%d C# files compiled into the assembly (Source minus SelfTest, plus the csproj's outside includes); " % len(cs)
                     + ("hose/reel types: %s" % types[:6] if types else "no class, struct, enum or interface names a hose or reel") + ("; pipe-named types (INFO): %s" % pipe_types[:4] if pipe_types else "")))
    rows.append(dict(id="NH_CS_PLAYER_TEXT", kind="fixed", verdict="FAIL" if literal_hits else "PASS", cases=len(literal_hits) + len(literal_ok),
                     detail=("string literals claiming a hose/reel/flexible pipe: %s" % literal_hits[:6]) if literal_hits else
                     "no string literal claims a hose, reel or flexible pipe; %d mention one only beside FlowWorks or a port: %s" % (len(literal_ok), literal_ok[:3])))

    # 4. About and Languages (player-facing text outside defs)
    txt_hits, txt_ok, n = [], [], 0
    for r in roots:
        for d in ("About", "Languages"):
            if os.path.isdir(os.path.join(r, d)):
                for p in files_under(os.path.join(r, d), {".xml", ".txt"}):
                    n += 1
                    t = open(p, encoding="utf-8", errors="replace").read()
                    for m in HOSE_WORD.finditer(t):
                        (txt_ok if sentence_ok(t, m) else txt_hits).append("%s: ...%s..." % (rel(p), t[max(0, m.start() - 40):m.end() + 30].replace("\n", " ")))
    rows.append(dict(id="NH_ABOUT_LANGUAGES", kind="fixed", verdict="FAIL" if txt_hits else "PASS", cases=n,
                     detail=("text claiming a hose: %s" % txt_hits[:4]) if txt_hits else "%d About/Languages files: no hose claim; mentions beside FlowWorks: %s" % (n, txt_ok[:2])))

    # 5. the changed file's settings header (GimmeSomeSlackMod.Header, the one line of the Mod Settings entry)
    hdr_file = os.path.join(mod, "Source", "GimmeSomeSlackMod.cs")
    hm = re.search(r'const string Header\s*=\s*"((?:[^"\\]|\\.)*)"', open(hdr_file, encoding="utf-8").read()) if os.path.isfile(hdr_file) else None
    hdr = hm.group(1) if hm else None
    hv = hdr is not None and not HOSE_WORD.search(hdr) and not PIPE.search(hdr)
    rows.append(dict(id="NH_SETTINGS_HEADER", kind="fixed", verdict="PASS" if hv else "FAIL", cases=1,
                     detail="Mod Settings header: %r" % hdr if hdr is not None else "header constant not found"))

    # 6. the overhead pipe spans GSS hosts for FlowWorks' pipe poles: words versus the pipe_pole_switch bar
    kind_refs = sum(open(p, encoding="utf-8", errors="replace").read().count("AerialLineKind.Pipe") for p in cs)
    rows.append(dict(id="NH_PIPE_SPAN_HOSTING_INFO", kind="info", verdict="INFO", cases=kind_refs,
                     detail="GSS's aerial engine draws overhead pipe spans between FlowWorks pipe poles (AerialLineKind.Pipe, %d references; "
                     "AerialMaterials.PipeMats draws the def's art or the look's wire as a stand-in). Owner by card 2026-10-22 "
                     "(PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES, after the 2026-10-10 hose ruling): pipe poles ride this engine under "
                     "their own FlowWorks switch (bar pipe_pole_switch). Read here as the owner's design, not a hose; the bar word "
                     "'pipe' in no_hose_in_gss means the old flexible pipe (the hose). Wording is a Polish note, not a failure." % kind_refs))
    for r in rows:
        r["bars"] = BARS
    return rows


def plant(mod, how):
    """Copy the mod (no heavy art_source) and plant one hose in it; returns the copy's path."""
    tmp = tempfile.mkdtemp(prefix="gss_nh_selfcheck_")
    dst = os.path.join(tmp, "GimmeSomeSlack")
    shutil.copytree(mod, dst, ignore=shutil.ignore_patterns("art_source", "review", "northstar*", "obj", "bin", "*.json", "*.png"))
    # the shared includes are resolved relative to the csproj: mirror them
    shared = os.path.join(os.path.dirname(mod), "_Shared")
    if os.path.isdir(shared):
        shutil.copytree(shared, os.path.join(tmp, "_Shared"), ignore=shutil.ignore_patterns("*.png", "obj", "bin"))
    def w(path, text):
        os.makedirs(os.path.dirname(path), exist_ok=True); open(path, "w").write(text)
    if how == "texture": w(os.path.join(dst, "Textures/RimMandrake/GimmeSomeSlack/Hose/HoseReel_north.png"), "x")
    if how == "texture_version": w(os.path.join(dst, "1.6/Textures/RimMandrake/GimmeSomeSlack/Coil_south.png".replace("Coil", "Reel")), "x")
    if how == "def": w(os.path.join(dst, "Defs/RM_X.xml"), "<Defs><ThingDef><defName>RM_HoseReel</defName></ThingDef></Defs>")
    if how == "def_common": w(os.path.join(dst, "Common/Defs/RM_Y.xml"), "<Defs><ThingDef><defName>RM_Thing</defName><thingClass>RimMandrake.Building_HoseReel</thingClass></ThingDef></Defs>")
    if how == "def_text": w(os.path.join(dst, "Defs/RM_Z.xml"), "<Defs><ThingDef><defName>RM_Cord</defName><description>A coiled flexible pipe for water.</description></ThingDef></Defs>")
    if how == "cs_type": w(os.path.join(dst, "Source/Aerial/Planted.cs"), "namespace X { public class HoseDrawer { } }")
    if how == "cs_shared": w(os.path.join(tmp, "_Shared/SlackGeometry/CordMath.cs"), open(os.path.join(tmp, "_Shared/SlackGeometry/CordMath.cs")).read() + "\nnamespace Y { class ReelLayer { } }\n")
    if how == "cs_text": w(os.path.join(dst, "Source/Aerial/Planted.cs"), 'namespace X { class P { string s = "Lay a hose to the pump"; } }')
    if how == "about":
        p = os.path.join(dst, "About/About.xml"); t = open(p).read(); w(p, t.replace("</description>", "\nAlso draws flexible pipes.</description>"))
    if how == "keyed": w(os.path.join(dst, "Languages/English/Keyed/GSS.xml"), "<LanguageData><K>Hose reel</K></LanguageData>")
    if how == "header":
        p = os.path.join(dst, "Source/GimmeSomeSlackMod.cs"); t = open(p).read()
        w(p, re.sub(r'(const string Header\s*=\s*")', r"\1Drawn flexible pipes and ", t, count=1))
    if how == "loadfolders":
        w(os.path.join(dst, "LoadFolders.xml"), "<loadFolders><v1.6><li>/</li><li>Extra</li></v1.6></loadFolders>")
        w(os.path.join(dst, "Extra/Defs/H.xml"), "<Defs><ThingDef><defName>RM_FireHose</defName></ThingDef></Defs>")
    return tmp, dst


PLANTS = {"texture": "NH_TEXTURES", "texture_version": "NH_TEXTURES", "def": "NH_DEFS_PATCHES", "def_common": "NH_DEFS_PATCHES",
          "def_text": "NH_DEFS_PATCHES", "cs_type": "NH_CS_TYPES", "cs_shared": "NH_CS_TYPES", "cs_text": "NH_CS_PLAYER_TEXT",
          "about": "NH_ABOUT_LANGUAGES", "keyed": "NH_ABOUT_LANGUAGES", "header": "NH_SETTINGS_HEADER", "loadfolders": "NH_DEFS_PATCHES"}


def selfcheck(mod):
    base = {r["id"]: r["verdict"] for r in scan(mod)}
    missed = []
    for how, row in PLANTS.items():
        tmp, dst = plant(mod, how)
        try:
            got = {r["id"]: r["verdict"] for r in scan(dst)}
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        new_fails = [k for k, v in got.items() if v == "FAIL" and base.get(k) != "FAIL"]
        if row not in new_fails: missed.append("%s (expected %s to turn FAIL; new FAILs %s)" % (how, row, new_fails))
    return dict(id="NH_SCANNER_SELFCHECK", bars=BARS, kind="fixed", verdict="FAIL" if missed else "PASS", cases=len(PLANTS),
                detail="%d planted hoses in a temp copy (texture, version-folder texture, def, Common def class, def text, C# type, "
                       "shared-include type, C# literal, About, Keyed, settings header, LoadFolders folder): " % len(PLANTS)
                       + ("missed %s" % missed if missed else "each turned its row FAIL"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--mod-root", default=MOD); ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()
    rows = scan(a.mod_root)
    if a.selfcheck: rows.append(selfcheck(a.mod_root))
    for r in rows: print(json.dumps(r))
    sys.exit(1 if any(r["verdict"] == "FAIL" for r in rows) else 0)
