#!/usr/bin/env python3
"""Blind lane 1, cycle 6, the no-hose half (bars no_hose, no_hose_in_gss), written from the bars alone.

The bar: "The reader of the mod's defs and source finds no hose, reel or pipe drawing in Gimme Some Slack: it draws power
cords only, hoses live in FlowWorks. It must not read as a hose def or texture left behind." False pass: "the scan
matching only def names, missing a texture folder". Red: "a hose reel def still ships in GSS".

So this scan reads the SHIPPED surface, every kind of it: About, Defs (every element and attribute, parsed as XML),
Patches, Languages, every texture file path, the C# source with comments stripped (identifiers and string literals
separately), and the srchash pairing of the shipped DLL with that source (the DLL's own metadata is read by
BlindLane1.cs). It never reads Source/SelfTest, validation*.py or selftest_*.py (dev tooling, and closed to a blind judge).

    python3 BlindLane1.py [--mod-root <dir>] [--guard]
One JSON row per line on stdout. --guard also proves the scanner can fail: it plants a hose in each surface of a
throwaway copy and expects a FAIL row for each.
"""
import argparse, hashlib, json, os, re, shutil, sys, tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")

# A hose or reel token: lower case only at a word start ("those", "whose", "wheel" never match), capitalised anywhere
# (camel case: RM_HoseReel, FireHosesMod).
HOSE = re.compile(r"(?<![A-Za-z])[hH]oses?(?![a-z])|Hose|(?<![A-Za-z])[rR]eels?(?![a-z])|Reel")
PIPE = re.compile(r"pipe", re.I)
# A sentence that names a hose only to say it lives elsewhere, or names another mod's hose PORT (a cord avoids it).
ELSEWHERE = re.compile(r"FlowWorks", re.I)
PORT = re.compile(r"(?<![A-Za-z])hoses?\s+ports?|pipe (or|and) hose ports?", re.I)


def row(id_, bars, kind, verdict, cases, detail):
    return {"id": id_, "bars": bars, "kind": kind, "verdict": verdict, "cases": cases, "detail": detail}


BARS = ["no_hose", "no_hose_in_gss"]


def files(root, sub, exts=None):
    base = os.path.join(root, sub)
    for d, dirs, fs in os.walk(base):
        dirs[:] = [x for x in dirs if x not in ("SelfTest", "obj", "bin")]
        for f in fs:
            if exts is None or os.path.splitext(f)[1].lower() in exts:
                yield os.path.join(d, f)


def xml_values(path):
    """Every tag, attribute and text of a parsed XML file (comments are not read by the game, so not here)."""
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        yield ("PARSE_ERROR", str(e))
        return
    for el in tree.iter():
        yield ("tag", el.tag)
        for k, v in el.attrib.items():
            yield ("attr " + k, v)
        if el.text and el.text.strip():
            yield (el.tag, el.text.strip())


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+|\n", text) if s.strip()]


def strip_cs(src):
    """C# source to (code with comments and strings blanked, [string literals]). Handles //, /* */, "..", @"..", $"..",
    and char literals well enough for identifier and literal scans."""
    code, lits, i, n = [], [], 0, len(src)
    while i < n:
        c = src[i]
        if src.startswith("//", i):
            j = src.find("\n", i); j = n if j < 0 else j
            code.append(" "); i = j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2); j = n if j < 0 else j + 2
            code.append(" "); i = j
        elif c == '"' or (c in "@$" and i + 1 < n and src[i + 1] in '"@$'):
            k = i
            verbatim = False
            while src[k] in "@$":
                verbatim |= src[k] == "@"; k += 1
            j = k + 1; buf = []
            while j < n:
                if verbatim and src[j] == '"' and j + 1 < n and src[j + 1] == '"':
                    buf.append('"'); j += 2; continue
                if not verbatim and src[j] == "\\":
                    buf.append(src[j:j + 2]); j += 2; continue
                if src[j] == '"':
                    break
                buf.append(src[j]); j += 1
            lits.append("".join(buf)); code.append(' "" '); i = j + 1
        elif c == "'":
            j = i + 1
            while j < n and src[j] != "'":
                j += 2 if src[j] == "\\" else 1
            code.append(" ' ' "); i = j + 1
        else:
            code.append(c); i += 1
    return "".join(code), lits


def scan(root):
    rows = []
    rel = lambda p: os.path.relpath(p, root)

    # 1. Defs: every value of every def, parsed as XML
    hits, n = [], 0
    for p in files(root, "Defs", {".xml"}):
        for where, v in xml_values(p):
            n += 1
            if where == "PARSE_ERROR":
                hits.append("%s: unparsable %s" % (rel(p), v)); continue
            if HOSE.search(v) and not (where == "description" and all(ELSEWHERE.search(s) or not HOSE.search(s) for s in sentences(v))):
                hits.append("%s <%s>: %s" % (rel(p), where, v[:120]))
    rows.append(row("S_DEFS_NO_HOSE_REEL_VALUE", BARS, "fixed", "FAIL" if hits else "PASS", n,
                    "every tag, attribute and text of every Defs/*.xml parsed: %d values, hose/reel tokens: %s" % (n, hits or "none")))

    # 2. Defs: no def is a pipe thing (defName, label, texPath, graphic or thing class naming a pipe)
    hits, ndefs = [], 0
    for p in files(root, "Defs", {".xml"}):
        try:
            top = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in top:
            ndefs += 1
            for f in ("defName", "label", "thingClass", "graphicData/texPath", "graphicData/graphicClass", "texPath", "graphicClass"):
                e = d.find(f)
                if e is not None and e.text and PIPE.search(e.text):
                    hits.append("%s %s <%s>%s" % (rel(p), d.findtext("defName"), f, e.text))
    rows.append(row("S_DEFS_NO_PIPE_THING", BARS, "fixed", "FAIL" if hits else "PASS", ndefs,
                    "%d defs: defName/label/texPath/graphicClass/thingClass naming a pipe: %s" % (ndefs, hits or "none")))

    # 3. Patches: no patch adds or touches hose/reel content, none adds a pipe graphic
    hits, n = [], 0
    for p in files(root, "Patches", {".xml"}):
        for where, v in xml_values(p):
            n += 1
            if HOSE.search(v) or (where in ("texPath", "graphicClass", "defName") and PIPE.search(v)):
                hits.append("%s <%s>: %s" % (rel(p), where, v[:120]))
    rows.append(row("S_PATCHES_NO_HOSE", BARS, "fixed", "FAIL" if hits else "PASS", n,
                    "every value of Patches/*.xml (%d): hose/reel, or a pipe texPath/graphicClass/defName: %s" % (n, hits or "none")))

    # 4. Textures: no file or folder names a hose, reel or pipe (the bar's false pass: a scan that misses the texture folder)
    hits, n = [], 0
    for p in files(root, "Textures"):
        n += 1
        r = rel(p)
        if HOSE.search(r) or re.search(r"hose|reel|pipe", r, re.I):
            hits.append(r)
    rows.append(row("S_TEXTURES_NO_HOSE_REEL_PIPE", BARS, "fixed", "FAIL" if hits else "PASS" if n else "UNSETTLED", n,
                    "%d texture files under Textures/: a path naming hose/reel/pipe: %s" % (n, hits or "none")))

    # 5. Languages / Keyed text: no hose or reel string (absent folder is a measured zero)
    hits, n = [], 0
    for p in files(root, "Languages", {".xml"}):
        for where, v in xml_values(p):
            n += 1
            if HOSE.search(v) and not PORT.search(v):
                hits.append("%s <%s>: %s" % (rel(p), where, v[:120]))
    rows.append(row("S_LANGUAGES_NO_HOSE", BARS, "fixed", "FAIL" if hits else "PASS", n,
                    "Languages/*.xml values (%d; 0 = no Languages folder): hose/reel: %s" % (n, hits or "none")))

    # 6. About.xml: a hose is named only to say it moved to FlowWorks
    hits, n = [], 0
    for p in files(root, "About", {".xml"}):
        for where, v in xml_values(p):
            for s in sentences(v):
                n += 1
                if HOSE.search(s) and not ELSEWHERE.search(s):
                    hits.append("%s <%s>: %s" % (rel(p), where, s[:160]))
    rows.append(row("S_ABOUT_HOSE_ONLY_ELSEWHERE", BARS, "fixed", "FAIL" if hits else "PASS", n,
                    "About/*.xml, %d sentences: a hose or reel named without saying it lives in FlowWorks: %s" % (n, hits or "none")))

    # 7. C# identifiers (comments and strings blanked): no Hose/Reel type, member or local
    hits, idents, lits_all = [], 0, []
    cs = list(files(root, "Source", {".cs"}))
    for p in cs:
        code, lits = strip_cs(open(p, encoding="utf-8-sig").read())
        lits_all += [(rel(p), s) for s in lits]
        for m in re.finditer(r"[A-Za-z_][A-Za-z0-9_]*", code):
            idents += 1
            if HOSE.search(m.group(0)):
                hits.append("%s: %s" % (rel(p), m.group(0)))
    rows.append(row("S_CS_NO_HOSE_REEL_IDENTIFIER", BARS, "fixed", "FAIL" if hits else "PASS" if cs else "UNSETTLED", idents,
                    "%d C# files (SelfTest excluded), %d identifier tokens outside comments and strings: Hose/Reel: %s"
                    % (len(cs), idents, sorted(set(hits)) or "none")))

    # 8. C# string literals: no user-visible text offers a hose or reel (another mod's hose PORT may be named: a cord avoids it)
    # An identifier-shaped literal (no space: a settings-file or type name for a migration or a reflection seam) is not
    # text a player reads; those are listed in their own INFO row so the judge still sees every one.
    ident_like = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")
    hits = [("%s: %r" % (f, s[:140])) for f, s in lits_all
            if HOSE.search(s) and not ident_like.match(s) and not PORT.search(s) and not ELSEWHERE.search(s)]
    rows.append(row("S_CS_LITERALS_NO_HOSE_OFFER", BARS, "fixed", "FAIL" if hits else "PASS", len(lits_all),
                    "%d string literals: player-readable text offering a hose/reel (not another mod's port, not FlowWorks'): %s"
                    % (len(lits_all), hits or "none")))
    names = sorted(set("%s: %s" % (f, s) for f, s in lits_all if HOSE.search(s) and ident_like.match(s)))
    rows.append(row("S_INFO_HOSE_NAMED_LITERALS", BARS, "info", "INFO", len(names),
                    "identifier-shaped literals naming a hose (not player text; judged in lane 2): %s" % (names or "none")))

    # 9. The one Mod Settings header (his B27 line) promises no pipe or hose drawing
    hdr = None
    modcs = os.path.join(root, "Source", "GimmeSomeSlackMod.cs")
    if os.path.exists(modcs):
        m = re.search(r'const\s+string\s+Header\s*=\s*"([^"]*)"', open(modcs, encoding="utf-8-sig").read())
        hdr = m.group(1) if m else None
    bad = hdr is not None and (HOSE.search(hdr) or PIPE.search(hdr))
    rows.append(row("S_SETTINGS_HEADER_NO_PIPE_HOSE", BARS, "fixed", "UNSETTLED" if hdr is None else "FAIL" if bad else "PASS", 1,
                    "GimmeSomeSlackMod.Header = %r" % hdr))

    # 10. Pipe-named literals: GSS's aerial engine also hangs FlowWorks' pipe-pole spans (an owner-approved seam:
    # bar pipe_pole_switch). Recorded as INFO for the judge, not decided here.
    pipes = sorted(set(s[:90] for f, s in lits_all if PIPE.search(s)))
    rows.append(row("S_INFO_PIPE_LITERALS", BARS, "info", "INFO", len(pipes),
                    "user-visible literals naming a pipe (the pipe-pole span UI GSS hosts for FlowWorks' def): %s" % pipes))

    # 11. The shipped DLL is the one the scanned source built (srchash pairs file hashes with the dll's own hash)
    sh = os.path.join(root, "Assemblies", "RimMandrakeGimmeSomeSlack.dll.srchash")
    dll = os.path.join(root, "Assemblies", "RimMandrakeGimmeSomeSlack.dll")
    if not (os.path.exists(sh) and os.path.exists(dll)):
        rows.append(row("S_DLL_BUILT_FROM_THIS_SOURCE", BARS, "fixed", "UNSETTLED", 0, "no dll or srchash"))
    else:
        lines = open(sh).read().splitlines()
        want_dll = next((l.split()[-1] for l in lines if l.startswith("# dll:")), None)
        got_dll = hashlib.sha256(open(dll, "rb").read()).hexdigest()
        bad, k = [], 0
        for l in lines:
            if l.startswith("#") or not l.strip():
                continue
            h, f = l.split(None, 1)
            p = os.path.normpath(os.path.join(root, "Source", f))
            k += 1
            if not os.path.exists(p):
                bad.append("missing " + f)
            elif hashlib.sha256(open(p, "rb").read()).hexdigest() != h:
                bad.append("changed " + f)
        listed = {os.path.normpath(os.path.join(root, "Source", l.split(None, 1)[1])) for l in lines if l.strip() and not l.startswith("#")}
        unlisted = [rel(p) for p in cs if os.path.normpath(p) not in listed and "SelfTest" not in p]
        if want_dll != got_dll:
            bad.append("dll hash %s != srchash %s" % (got_dll[:12], (want_dll or "?")[:12]))
        rows.append(row("S_DLL_BUILT_FROM_THIS_SOURCE", BARS, "fixed", "FAIL" if bad else "PASS", k,
                        "%d source hashes in srchash: mismatches %s; shipped .cs not listed (not compiled): %s" % (k, bad or "none", unlisted or "none")))
    return rows


def guard(root):
    """Plant a hose in each surface of a throwaway copy and expect a new FAIL row for each (the instrument can see)."""
    rows = []
    base = {r["id"]: r["verdict"] for r in scan(root)}
    plants = [
        ("Textures/RimMandrake/GimmeSomeSlack/Hose/RM_HoseReel_south.png", None, "S_TEXTURES_NO_HOSE_REEL_PIPE"),
        ("Defs/Aerial/ZZ_Plant.xml", '<Defs><ThingDef><defName>RM_HoseReel</defName><label>hose reel</label></ThingDef></Defs>', "S_DEFS_NO_HOSE_REEL_VALUE"),
        ("Defs/Aerial/ZZ_Plant2.xml", '<Defs><ThingDef><defName>RM_Thing</defName><graphicData><texPath>Things/FlexPipe</texPath></graphicData></ThingDef></Defs>', "S_DEFS_NO_PIPE_THING"),
        ("Source/ZZ_Plant.cs", 'namespace X { class HoseReelDrawer { string s = "Lay a hose"; } }', "S_CS_NO_HOSE_REEL_IDENTIFIER"),
        ("Source/ZZ_Plant2.cs", 'namespace X { class Y { string s = "Lay a hose here"; } }', "S_CS_LITERALS_NO_HOSE_OFFER"),
        ("Patches/ZZ_Plant.xml", '<Patch><Operation Class="PatchOperationAdd"><xpath>Defs/ThingDef[defName="RM_HoseReel"]</xpath><value><x/></value></Operation></Patch>', "S_PATCHES_NO_HOSE"),
    ]
    for rel_, content, expect in plants:
        tmp = tempfile.mkdtemp(prefix="gss_guard_")
        try:
            for sub in ("About", "Defs", "Patches", "Textures", "Source", "Assemblies", "Languages"):
                if os.path.isdir(os.path.join(root, sub)):
                    shutil.copytree(os.path.join(root, sub), os.path.join(tmp, sub), ignore=shutil.ignore_patterns("SelfTest", "obj", "bin"))
            p = os.path.join(tmp, rel_)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "wb" if content is None else "w").write(b"\x89PNG" if content is None else content)
            got = {r["id"]: r["verdict"] for r in scan(tmp)}
            caught = base.get(expect) != "FAIL" and got.get(expect) == "FAIL"
            rows.append(row("S_GUARD_" + expect[2:], BARS, "fixed", "PASS" if caught else "FAIL", 1,
                            "planted %s in a throwaway copy: %s went %s -> %s" % (rel_, expect, base.get(expect), got.get(expect))))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    # the header row must see a header that names a pipe
    tmp = tempfile.mkdtemp(prefix="gss_guard_")
    try:
        os.makedirs(os.path.join(tmp, "Source"))
        open(os.path.join(tmp, "Source", "GimmeSomeSlackMod.cs"), "w").write('class M { public const string Header = "Drawn flexible pipes and wires"; }')
        got = {r["id"]: r["verdict"] for r in scan(tmp)}
        rows.append(row("S_GUARD_SETTINGS_HEADER", BARS, "fixed", "PASS" if got["S_SETTINGS_HEADER_NO_PIPE_HOSE"] == "FAIL" else "FAIL", 1,
                        "the old header text planted: row went %s" % got["S_SETTINGS_HEADER_NO_PIPE_HOSE"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod-root", default=MOD)
    ap.add_argument("--guard", action="store_true")
    a = ap.parse_args()
    out = scan(a.mod_root) + (guard(a.mod_root) if a.guard else [])
    for r in out:
        print(json.dumps(r))
    sys.exit(1 if any(r["verdict"] == "FAIL" for r in out) else 0)
