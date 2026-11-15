#!/usr/bin/env python3
"""Blind lane 1, bars no_hose / no_hose_in_gss: an independent scan of what Gimme Some Slack SHIPS for hose, reel or
pipe drawing, written from the bars alone (cycle 2 judge; it never read the builder's no-hose test).

    python3 blind_no_hose.py [--mod <mod folder>] [--rows <out.jsonl>] [--seed N]

The bar (tree.json no_hose_in_gss): "offline scan: no ThingDef, texture or class for hoses or reels under
src/RimMandrake/GimmeSomeSlack"; false pass "the scan matching only def names, missing a texture folder"; red "a hose
reel def still ships in GSS". Its sheet line also says "No hose, reel or pipe is drawn by this mod".

What ships: About/, Defs/, Patches/, Textures/, Languages/, Assemblies/*.dll, and Source/ minus Source/SelfTest (the C#
the DLL is built from). Words are matched as identifier WORDS (camelCase / _ / - / . / / split), so "whose" and
"choose" never match "hose". C# comments are stripped before the class and literal checks (prose saying "hoses live in
FlowWorks" draws nothing).

Rows (one JSON per line): the live scan (hose/reel: PASS or FAIL; pipe drawing: INFO with every hit), then the controls:
each planted kind of hose content in a throwaway copy must be caught (a scanner that cannot see a texture folder is
the bar's false pass), the clean copy must stay clean, and seeded random plants must all be caught.
Exit 0 when no row FAILs."""
import argparse, json, os, random, re, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")
SHIP_DIRS = ("About", "Defs", "Patches", "Textures", "Languages", "Assemblies", "Source")
BAD = {"hose", "hoses", "reel", "reels", "hosereel", "hosereels"}
PIPE = {"pipe", "pipes"}
BARS = ["no_hose", "no_hose_in_gss"]


def words(s):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    return [w.lower() for w in re.split(r"[^A-Za-z0-9]+", s) if w]


def strip_cs_comments(src):
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if src.startswith("//", i):
            j = src.find("\n", i); i = n if j < 0 else j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2); i = n if j < 0 else j + 2
        elif c == '"' or src.startswith('@"', i) or src.startswith('$"', i):
            j = i + (2 if c in "@$" else 1); verbatim = c == "@"
            while j < n:
                if not verbatim and src[j] == "\\": j += 2; continue
                if src[j] == '"':
                    if verbatim and j + 1 < n and src[j + 1] == '"': j += 2; continue
                    break
                j += 1
            out.append(src[i:j + 1]); i = j + 1
        else:
            out.append(c); i += 1
    return "".join(out)


def shipped_files(mod):
    for d in SHIP_DIRS:
        root = os.path.join(mod, d)
        for dp, dns, fns in os.walk(root):
            if d == "Source":
                dns[:] = [x for x in dns if x not in ("SelfTest", "obj", "bin")]
            for fn in fns:
                yield os.path.join(dp, fn)


def compiled_sources(mod):
    """Every .cs the shipped DLL is built from: the csproj's Compile items (some live in src/RimMandrake/_Shared)."""
    src = os.path.join(mod, "Source")
    projs = [f for f in os.listdir(src) if f.endswith(".csproj")] if os.path.isdir(src) else []
    out = []
    for pj in projs:
        txt = open(os.path.join(src, pj), encoding="utf-8", errors="replace").read()
        if re.search(r"<EnableDefaultCompileItems>\s*false", txt, re.I):
            for m in re.finditer(r'<Compile Include="([^"]+)"', txt):
                out.append(os.path.normpath(os.path.join(src, m.group(1).replace("\\", "/"))))
        else:
            for dp, dns, fns in os.walk(src):
                dns[:] = [x for x in dns if x not in ("SelfTest", "obj", "bin")]
                out += [os.path.join(dp, f) for f in fns if f.endswith(".cs")]
    return [p for p in out if os.path.isfile(p)]


def scan(mod):
    """-> (bad hits, pipe hits): each hit (kind, relpath, what)."""
    bad, pipe = [], []
    dll_files, members, dll_hose, enum_hose, hose_use = [], set(), set(), [], []
    scan.members, scan.dll_hose, scan.enum_hose, scan.hose_use = members, dll_hose, enum_hose, hose_use
    def hit(kind, rel, what, ws):
        if BAD & set(ws): bad.append((kind, rel, what))
        if PIPE & set(ws): pipe.append((kind, rel, what))
    for p in shipped_files(mod):
        rel = os.path.relpath(p, mod)
        ext = os.path.splitext(p)[1].lower()
        top = rel.split(os.sep)[0]
        if top in ("Textures",):
            hit("texture_path", rel, rel, words(rel.replace("Textures" + os.sep, "", 1)))
            continue
        if ext == ".xml":
            txt = open(p, encoding="utf-8", errors="replace").read()
            txt = re.sub(r"<!--.*?-->", "", txt, flags=re.S)
            # defs (and defs a patch adds): the elements that name or draw a thing
            for tag in ("defName", "label", "texPath", "thingClass", "graphicClass", "compClass", "class", "workerClass",
                        "jobClass", "driverClass", "li"):
                for m in re.finditer(r"<%s>([^<]*)</%s>" % (tag, tag), txt):
                    hit("xml_" + tag, rel, m.group(1).strip(), words(m.group(1)))
            for m in re.finditer(r"\b(Class|Name|ParentName)=\"([^\"]*)\"", txt):
                hit("xml_attr_" + m.group(1), rel, m.group(2), words(m.group(2)))
            # a def element whose TYPE is a hose def (e.g. <FlowWorks.HoseReelDef>)
            for m in re.finditer(r"<([A-Za-z_.]+Def)\b", txt):
                hit("xml_deftype", rel, m.group(1), words(m.group(1)))
            continue
        if ext == ".cs":
            continue   # C# is scanned from the csproj's Compile list below (it reaches _Shared files outside the mod folder)
        if ext == ".dll":
            dll_files.append(p)
            continue
    for p in compiled_sources(mod):
        rel = os.path.relpath(p, mod)
        if True:
            src = strip_cs_comments(open(p, encoding="utf-8", errors="replace").read())
            for m in re.finditer(r"\b[A-Za-z_][A-Za-z0-9_]*\b", src):
                if BAD & set(words(m.group(0))): members.add(m.group(0))
            for m in re.finditer(r"\b(class|struct|enum|interface|record)\s+([A-Za-z_][A-Za-z0-9_]*)", src):
                hit("cs_type", rel, m.group(2), words(m.group(2)))
            for m in re.finditer(r"\"((?:[^\"\\]|\\.)*)\"", src):
                s = m.group(1)
                if "/" in s or s.startswith("RM_") or s.startswith("RimMandrake"):   # a texture path or a def name
                    hit("cs_literal", rel, s, words(s))
            for m in re.finditer(r"\b(?:enum\s+\w+\s*\{([^}]*)\})", src):
                for member in re.split(r"[,\s=]+", m.group(1)):
                    if member:
                        ws = words(member)
                        if PIPE & set(ws): pipe.append(("cs_enum_member", rel, member))
                        if BAD & set(ws): enum_hose.append((rel, member))   # a lay KIND, not a def/texture/class: reported, decided below
            # does GSS's OWN code (not the shared geometry it compiles in) ever select the hose lay?
            if not rel.startswith(".."):
                for m in re.finditer(r"\bCordKind\.Hose\b|\bLayParams\.Hose\s*\(", src):
                    hose_use.append((rel, m.group(0)))
    for p in dll_files:
        rel = os.path.relpath(p, mod)
        if True:
            blob = open(p, "rb").read()
            idents = set(re.findall(rb"[A-Za-z_][A-Za-z0-9_]{2,}", blob))
            idents |= {x.decode("utf-16-le", "ignore").encode() for x in re.findall(rb"(?:[A-Za-z_/]\x00){3,}", blob)}
            for x in sorted(idents):
                s = x.decode("ascii", "ignore")
                ws = words(s)
                if PIPE & set(ws): pipe.append(("dll_string", rel, s))
                if BAD & set(ws):
                    dll_hose.add(s)
                    # a hose name in the DLL that no compiled source spells (member, literal or comment-free) means the DLL
                    # was not built from the source it ships with, so the source scan cannot vouch for it
                    if s not in members and not any(s in open(q, encoding="utf-8", errors="replace").read() for q in compiled_sources(mod)):
                        bad.append(("dll_unaccounted", rel, s))
    return bad, pipe


def row(i, kind, verdict, cases, detail):
    return {"id": i, "bars": BARS, "kind": kind, "verdict": verdict, "cases": cases, "detail": detail}


PLANTS = {
    "def": ("Defs/Blind_Hose.xml", '<?xml version="1.0"?><Defs><ThingDef><defName>RM_HoseReel</defName><label>hose reel</label></ThingDef></Defs>'),
    "texture_folder_only": ("Textures/RimMandrake/GimmeSomeSlack/Hose/Coil.png", None),
    "texture_file": ("Textures/RimMandrake/GimmeSomeSlack/ReelSpool.png", None),
    "cs_class": ("Source/BlindHoseDrawer.cs", "namespace X { public class SectionLayer_RM_Hoses { } }"),
    "cs_texpath": ("Source/BlindTex.cs", 'namespace X { class T { string p = "RimMandrake/GimmeSomeSlack/HoseCoil"; } }'),
    "patch_adds_def": ("Patches/Blind_Patch.xml", '<?xml version="1.0"?><Patch><Operation Class="PatchOperationAdd"><xpath>Defs</xpath>'
                       '<value><ThingDef><defName>RM_GardenHose</defName></ThingDef></value></Operation></Patch>'),
    "thing_class": ("Defs/Blind_Class.xml", '<?xml version="1.0"?><Defs><ThingDef><defName>RM_Thing</defName>'
                    '<thingClass>RimMandrake.GimmeSomeSlack.Building_Reel</thingClass></ThingDef></Defs>'),
}
DECOYS = {  # words that contain the letters but are not hoses: a substring scanner false-flags these
    "Source/BlindDecoy.cs": 'namespace X { class Whose { string s = "RimMandrake/choose/Wheel"; } }',
}


def plant(copy, rel, body):
    p = os.path.join(copy, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(body.encode() if body is not None else b"\x89PNG\r\n\x1a\n")
    if rel.endswith(".cs") and rel.startswith("Source/"):   # a class ships only if the csproj compiles it
        src = os.path.join(copy, "Source")
        projs = [f for f in os.listdir(src) if f.endswith(".csproj")]
        if not projs:
            open(os.path.join(src, "Blind.csproj"), "w").write("<Project></Project>")
        else:
            pj = os.path.join(src, projs[0]); t = open(pj).read()
            inc = rel[len("Source/"):].replace("/", "\\")
            t = t.replace("</Project>", '<ItemGroup><Compile Include="%s" /></ItemGroup></Project>' % inc, 1)
            open(pj, "w").write(t)


def fresh_copy(mod, tmp, name):
    """A copy laid out like the repo (<tmp>/<name>/RimMandrake/{GimmeSomeSlack,_Shared}) so ../../_Shared resolves."""
    dst = os.path.join(tmp, name, "RimMandrake", "GimmeSomeSlack")
    for d in SHIP_DIRS:
        s = os.path.join(mod, d)
        if os.path.isdir(s):
            shutil.copytree(s, os.path.join(dst, d), ignore=shutil.ignore_patterns("SelfTest", "obj", "bin"))
    shared = os.path.join(os.path.dirname(os.path.abspath(mod)), "_Shared")
    if os.path.isdir(shared):
        shutil.copytree(shared, os.path.join(tmp, name, "RimMandrake", "_Shared"))
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod", default=MOD); ap.add_argument("--rows", default=None); ap.add_argument("--seed", type=int, default=20261115)
    a = ap.parse_args()
    rows = []
    bad, pipe = scan(a.mod)
    rows.append(row("L1_NOHOSE_LIVE_SCAN", "fixed", "FAIL" if bad else "PASS", len(list(shipped_files(a.mod))),
                    "hose/reel hits in shipped content: %d %s" % (len(bad), json.dumps(bad[:12]))))
    rows.append(row("L1_NOHOSE_HOSE_NAMED_MEMBERS", "info", "INFO", len(scan.members),
                    "hose/reel-named identifiers (not types, not texture paths) in compiled sources: %s; in the DLL: %s"
                    % (sorted(scan.members), sorted(scan.dll_hose))))
    rows.append(row("L1_NOHOSE_GSS_NEVER_SELECTS_HOSE_LAY", "fixed", "FAIL" if scan.hose_use else "PASS", len(scan.enum_hose),
                    "shared geometry compiled into the DLL defines hose lay kinds %s; GSS's own compiled sources select one at %s"
                    % (json.dumps(scan.enum_hose), json.dumps(scan.hose_use))))
    kinds = sorted({k for k, _, _ in pipe})
    files = sorted({r for _, r, _ in pipe})
    rows.append(row("L1_NOHOSE_PIPE_WORDS", "info", "INFO", len(pipe),
                    "the sheet says 'no hose, reel or pipe is drawn'; 'pipe' identifiers in shipped content: %d hits in %d files, kinds %s; "
                    "files %s; sample %s" % (len(pipe), len(files), kinds, files[:20], json.dumps(sorted({w for _, _, w in pipe})[:40]))))
    tmp = tempfile.mkdtemp(prefix="gss_blind_nohose_")
    try:
        base = fresh_copy(a.mod, tmp, "clean")
        b0, _ = scan(base)
        rows.append(row("L1_NOHOSE_COPY_CLEAN", "fixed", "PASS" if len(b0) == len(bad) else "FAIL", 1,
                        "the throwaway copy scans like the mod: %d vs %d" % (len(b0), len(bad))))
        for k, (rel, body) in sorted(PLANTS.items()):
            c = fresh_copy(a.mod, tmp, "plant_" + k)
            plant(c, rel, body)
            bk, _ = scan(c)
            new = [h for h in bk if h[1] == rel.replace("/", os.sep)]
            rows.append(row("L1_NOHOSE_CATCH_" + k.upper(), "fixed", "PASS" if new else "FAIL", 1,
                            "planted %s at %s: caught %s" % (k, rel, json.dumps(new[:3]))))
        # a DLL holding a hose name its source does not spell (built from other source than ships)
        c = fresh_copy(a.mod, tmp, "stale_dll")
        dlls = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(c, "Assemblies")) for f in fs if f.endswith(".dll")]
        if dlls:
            with open(dlls[0], "ab") as f: f.write(b"\x00SectionLayer_RM_HoseReels\x00")
            bk, _ = scan(c)
            new = [h for h in bk if h[0] == "dll_unaccounted"]
            rows.append(row("L1_NOHOSE_CATCH_STALE_DLL", "fixed", "PASS" if new else "FAIL", 1,
                            "a hose type name in the DLL that no compiled source spells: caught %s" % json.dumps(new[:2])))
        c = fresh_copy(a.mod, tmp, "decoy")
        for rel, body in DECOYS.items(): plant(c, rel, body)
        bd, _ = scan(c)
        extra = [h for h in bd if h[1].startswith("Source" + os.sep + "BlindDecoy")]
        rows.append(row("L1_NOHOSE_DECOY_NOT_FLAGGED", "fixed", "FAIL" if extra else "PASS", 1,
                        "whose/choose/Wheel must not read as hose/reel: flagged %s" % json.dumps(extra)))
        rng = random.Random(a.seed)
        misses, n = [], 40
        roots = ["Defs/Rand", "Textures/RimMandrake/GimmeSomeSlack/Rand", "Source/Rand", "Patches/Rand"]
        for i in range(n):
            word = rng.choice(["Hose", "hose", "HOSE", "Reel", "reel", "Hoses", "Reels"])
            r = rng.choice(roots)
            style = rng.choice(["camel", "snake", "dot"])
            ident = {"camel": "RM_Blue%sCart" % word.capitalize(), "snake": "rm_%s_cart" % word.lower(), "dot": "Blue.%s.Cart" % word}[style]
            if r.startswith("Defs") or r.startswith("Patches"):
                rel, body = r + "%d.xml" % i, "<Defs><ThingDef><defName>%s</defName></ThingDef></Defs>" % ident
            elif r.startswith("Textures"):
                rel, body = r + "/%s/a%d.png" % (ident, i), None
            else:
                rel, body = r + "%d.cs" % i, "namespace X { class %s { } }" % re.sub(r"\W", "_", ident)
            c = os.path.join(tmp, "rand%d" % i)
            os.makedirs(os.path.join(c, "Source"), exist_ok=True)
            plant(c, rel, body)
            bk, _ = scan(c)
            if not bk: misses.append((rel, ident))
        # shrink: the shortest missed identifier
        shr = min(misses, key=lambda m: len(m[1])) if misses else None
        rows.append(row("L1_NOHOSE_RANDOM_PLANTS", "random", "FAIL" if misses else "PASS", n,
                        "seed %d: %d of %d random plants caught; shrunk miss %s" % (a.seed, n - len(misses), n, json.dumps(shr))))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    out = "\n".join(json.dumps(r) for r in rows) + "\n"
    if a.rows:
        open(a.rows, "a").write(out)
    sys.stdout.write(out)
    sys.exit(1 if any(r["verdict"] == "FAIL" for r in rows) else 0)


if __name__ == "__main__":
    main()
