#!/usr/bin/env python3
"""PW7 graphics audit for the GimmeSomeSlack + FlowWorks review maps (design/RimMandrake/biome_review_save_standard.md section 8).

Re-runnable, offline, read-only (writes only FINDINGS.md, sheet.png, audit.json beside itself):
    python3 Transient/review_graphics_audit_gssfw_20261015/audit.py

What it measures: every texture path the game would load for the two mods, from the DEPLOYED Mods folder, in the live
load order (ModsConfig.xml activeMods, later mods win). Sources of paths: (1) every XML element in the deployed Defs of
both mods whose name says it is a texture path (inheritance from Core resolved); (2) the C#-built paths (rule tables
below, each with the Source/ file it comes from); (3) GSS's art_slots() board. Vanilla paths are NOT read from the
.assets bundles; they are matched by file name against the extracted bundle index and otherwise "vanilla, not checked".
"""
import copy, csv, hashlib, importlib.util, json, os, re, sys, xml.etree.ElementTree as ET
from collections import OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path("/home/mandrake/rm/bench")
SRC = REPO / "src/RimMandrake"
GAME = Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld")
MODS, DATA = GAME / "Mods", GAME / "Data"
MODSCONFIG = Path("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml")
BUNDLE_IDX = Path("/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures/index.csv")
OURS = {"GimmeSomeSlack": "mandrake.rm.gimmesomeslack", "FlowWorks": "mandrake.rm.flowworks"}
EXTS = (".png", ".jpg", ".jpeg", ".psd", ".tga")
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")

# ------------------------------------------------------------------ load order and mod roots
active = [e.text.strip().lower() for e in ET.parse(MODSCONFIG).find("activeMods")]
pkg_dir = {}
for d in sorted(MODS.iterdir()):
    a = d / "About" / "About.xml"
    if a.is_file():
        try:
            pid = (ET.parse(a).findtext("packageId") or "").strip().lower()
            pkg_dir.setdefault(pid, d)
        except ET.ParseError:
            pass
WORKSHOP = GAME.parent.parent / "workshop" / "content" / "294100"
if WORKSHOP.is_dir():
    for d in sorted(WORKSHOP.iterdir()):
        a = d / "About" / "About.xml"
        if a.is_file():
            try:
                pid = (ET.parse(a).findtext("packageId") or "").strip().lower()
                if pid in active:
                    pkg_dir.setdefault(pid, d)
            except ET.ParseError:
                pass
for pid, name in (("ludeon.rimworld", "Core"), ("ludeon.rimworld.royalty", "Royalty"), ("ludeon.rimworld.ideology", "Ideology"),
                  ("ludeon.rimworld.biotech", "Biotech"), ("ludeon.rimworld.anomaly", "Anomaly"), ("ludeon.rimworld.odyssey", "Odyssey")):
    pkg_dir[pid] = DATA / name
order = [(p, pkg_dir[p]) for p in active if p in pkg_dir]
not_found_active = [p for p in active if p not in pkg_dir]


def tex_dirs(root):
    lf = root / "LoadFolders.xml"
    out = []
    if lf.is_file():
        try:
            v = ET.parse(lf).getroot().find("v1.6")
            if v is not None:
                for li in v:
                    t = (li.text or "").strip()
                    out.append(root / ("" if t == "/" else t) / "Textures")
                return [d for d in out if d.is_dir()]
        except ET.ParseError:
            pass
    for c in ("Textures", "Common/Textures", "1.6/Textures"):
        if (root / c).is_dir():
            out.append(root / c)
    return out


TEXDIRS = [(p, r, tex_dirs(r)) for p, r in order]
_ls = {}


def ls(d):
    d = str(d)
    if d not in _ls:
        try:
            _ls[d] = {n.lower(): n for n in os.listdir(d)}
        except OSError:
            _ls[d] = {}
    return _ls[d]


def find_in_dir(texdir, rel, exts=EXTS):
    """CI lookup of rel(+ext) under texdir; returns Path or None."""
    parts = rel.split("/")
    cur = Path(texdir)
    for p in parts[:-1]:
        n = ls(cur).get(p.lower())
        if not n:
            return None
        cur = cur / n
    base = parts[-1].lower()
    for e in exts:
        n = ls(cur).get(base + e)
        if n:
            return cur / n
    return None


def folder_in_dir(texdir, rel):
    cur = Path(texdir)
    for p in rel.split("/"):
        n = ls(cur).get(p.lower())
        if not n:
            return None
        cur = cur / n
    return cur if cur.is_dir() else None


def find_file(rel):
    """(winner_pkg, Path, [all pkgs shipping it]) walking the load order in reverse (later mods win)."""
    hits = []
    for p, r, tds in reversed(TEXDIRS):
        for td in tds:
            f = find_in_dir(td, rel)
            if f:
                hits.append((p, f))
                break
    return (hits[0][0], hits[0][1], [h[0] for h in hits]) if hits else (None, None, [])


def find_folder(rel):
    out = []
    for p, r, tds in reversed(TEXDIRS):
        for td in tds:
            f = folder_in_dir(td, rel)
            if f:
                out.append((p, f))
    return out


# ------------------------------------------------------------------ vanilla knowledge
bundle_names = set()
if BUNDLE_IDX.is_file():
    for row in csv.DictReader(open(BUNDLE_IDX, encoding="utf-8", errors="replace")):
        bundle_names.add(row["m_Name"].lower())
OWN_MARK = re.compile(r"flowworks|gimmesomeslack|rimmandrake|/RM_|^RM_|Filth_?Tar", re.I)
repo_tex = {}   # mod -> {lower rel (no ext): Path}
for m in OURS:
    t = SRC / m / "Textures"
    d = {}
    for f in t.rglob("*"):
        if f.is_file():
            d[str(f.relative_to(t).with_suffix("")).replace(os.sep, "/").lower()] = f
    repo_tex[m] = d
repo_all = {k for d in repo_tex.values() for k in d}


def owned(path):
    return bool(OWN_MARK.search(path)) or path.lower() in repo_all or any(k.startswith(path.lower() + "/") or k.startswith(path.lower() + "_") for k in repo_all)


def vanilla_status(path):
    base = path.split("/")[-1].lower()
    cand = {base, base + "_south", base + "_atlas", base + "_east"}
    if cand & bundle_names or any(n.startswith(base + "_") for n in bundle_names if n[:3] == base[:3]):
        return "vanilla (name found in the extracted bundle index)"
    return "vanilla, not checked on disk"


# ------------------------------------------------------------------ defs (deployed) with inheritance
def load_defs(roots):
    """{(tag, defName): Element} plus {(tag, Name): Element} abstract bases; file of origin kept as attribute _file."""
    named, defs = {}, OrderedDict()
    for root in roots:
        for f in sorted(Path(root).rglob("*.xml")):
            try:
                tree = ET.parse(f)
            except ET.ParseError:
                continue
            for el in tree.getroot():
                if not isinstance(el.tag, str):
                    continue
                el.set("_file", str(f))
                nm = el.get("Name")
                if nm:
                    named[(el.tag, nm)] = el
                dn = el.findtext("defName")
                if dn:
                    defs[(el.tag, dn.strip())] = el
    return defs, named


def merge(parent, child):
    out = copy.deepcopy(parent)
    for c in child:
        if not isinstance(c.tag, str):
            continue
        if c.tag == "li":
            out.append(copy.deepcopy(c))
            continue
        ex = out.find(c.tag)
        if ex is None or c.get("Inherit") == "False":
            if ex is not None:
                out.remove(ex)
            out.append(copy.deepcopy(c))
        elif len(c) and len(ex) and all(x.tag == "li" for x in c):
            # list: child items appended to the parent's
            for x in c:
                ex.append(copy.deepcopy(x))
        elif len(c):
            new = merge(ex, c)
            out.remove(ex)
            out.append(new)
        else:
            ex.text = c.text
    for k, v in child.attrib.items():
        out.set(k, v)
    return out


def resolve(el, named, depth=0):
    pn = el.get("ParentName")
    if not pn or depth > 12:
        return el
    par = named.get((el.tag, pn))
    if par is None:
        el.set("_unresolved_parent", pn)
        return el
    return merge(resolve(par, named, depth + 1), el)


# ------------------------------------------------------------------ slot extraction
PATH_TAGS = re.compile(r"(path|tex|texture|icon)$", re.I)
PATH_VAL = re.compile(r"^[A-Za-z0-9_\-/ ]+$")
SKIP_TAGS = {"xpath", "texturescale", "soundpath"}


def parse_vec(el):
    if el is None or not el.text:
        return None
    m = re.match(r"\(\s*([\d.\-]+)\s*,\s*([\d.\-]+)", el.text.strip())
    return (float(m.group(1)), float(m.group(2))) if m else None


def extract_slots(defel, elp="", cls=None, gd_ctx=None):
    """Walk a resolved def; yield (xml path, texpath, graphicClass, ctx)."""
    out = []

    def walk(e, path, ctx):
        for c in e:
            if not isinstance(c.tag, str):
                continue
            p = path + "/" + c.tag
            text = (c.text or "").strip()
            ctx2 = ctx
            if len(c):
                gc = c.findtext("graphicClass")
                ctx2 = dict(ctx)
                if gc:
                    ctx2 = dict(ctx, cls=gc.strip(), drawSize=parse_vec(c.find("drawSize")), shader=c.findtext("shaderType"),
                                parent_tag=c.tag)
                walk(c, p, ctx2)
            elif text and PATH_TAGS.search(c.tag) and c.tag.lower() not in SKIP_TAGS and PATH_VAL.match(text) \
                    and ("/" in text or c.tag in ("texPath", "texturePath", "uiIconPath", "iconPath")) and not text.lower().endswith((".dll", ".xml")):
                out.append((p, text, ctx.get("cls") if (c.tag in ("texPath", "texturePath") and ctx.get("cls")) else None, ctx))
    walk(defel, defel.tag, {})
    return out


def check_slot(path, cls, tag, shader=None):
    """-> dict(kind, files[Path], pkgs, expect[str], missing[str], notes[str], status)"""
    r = dict(files=[], pkgs=[], expect=[], missing=[], notes=[], shipped_by=[])
    leaf = tag.split("/")[-1]
    c = (cls or "").strip()

    def one(rel, req=True):
        pk, f, allp = find_file(rel)
        r["expect"].append(rel)
        if f:
            r["files"].append(f)
            r["pkgs"].append(pk)
            r["shipped_by"].append(allp)
        elif req:
            r["missing"].append(rel)
        return f

    if c.startswith("Graphic_Multi") or c in ("Graphic_PawnBodySilhouette",):
        got = [one(path + "_" + d, False) for d in ("south", "east", "north", "west")]
        if not any(got):
            r["missing"].append(path + "_south")
        elif not got[0]:
            r["notes"].append("no _south (engine falls back to another facing)")
        elif not (got[1] and got[2]):
            r["notes"].append("partial facings: " + ",".join(d for d, g in zip(("S", "E", "N", "W"), got) if g))
        if (shader or "") == "CutoutComplex":
            for d in ("south", "east", "north"):
                one(path + "_" + d + "m", False)
    elif c in ("Graphic_Random", "Graphic_Collection", "Graphic_Flicker", "Graphic_StackCount", "Graphic_RandomRotated"):
        fol = find_folder(path)
        r["expect"].append(path + "/")
        if fol:
            files = [f for f in sorted(fol[0][1].iterdir()) if f.suffix.lower() in EXTS and not f.stem.lower().endswith(("_m", "south_m"))]
            if files:
                r["files"] += files
                r["pkgs"] += [fol[0][0]] * len(files)
            else:
                r["missing"].append(path + "/ (empty folder)")
        else:
            pk, f, _ = find_file(path)
            if f and c == "Graphic_StackCount":
                r["files"].append(f); r["pkgs"].append(pk)
            else:
                r["missing"].append(path + "/" + (" (a single file exists but the class needs a folder)" if f else ""))
    elif c.startswith("Graphic_Linked"):
        one(path + "_Atlas")
    elif c == "Graphic_Appearances":
        cnt = 0
        for p, rt, tds in reversed(TEXDIRS):
            for td in tds:
                par, _, base = path.rpartition("/")
                fol = folder_in_dir(td, par) if par else Path(td)
                if fol:
                    for n in sorted(os.listdir(fol)):
                        if n.lower().startswith(base.lower() + "_") and n.lower().endswith(EXTS):
                            r["files"].append(fol / n); r["pkgs"].append(p); cnt += 1
        r["expect"].append(path + "_<Appearance>")
        if not cnt:
            r["missing"].append(path + "_<Appearance>")
    elif c and c not in ("Graphic_Single", "Graphic_Terrain", "Graphic_Gas", "Graphic_Mote", "Graphic_MoteSplash", "Graphic_Shadow"):
        # custom class: accept any of the usual layouts
        pk, f, allp = find_file(path)
        r["expect"].append(path + " (custom class %s: loose check)" % c)
        got = [find_file(path + s) for s in ("_south", "_east", "_north", "_Atlas")]
        if f:
            r["files"].append(f); r["pkgs"].append(pk); r["shipped_by"].append(allp)
        for g in got:
            if g[1]:
                r["files"].append(g[1]); r["pkgs"].append(g[0])
        fol = find_folder(path)
        if fol:
            r["files"] += [x for x in sorted(fol[0][1].iterdir()) if x.suffix.lower() in EXTS]
            r["pkgs"] += [fol[0][0]] * (len(r["files"]) - len(r["pkgs"]))
        if not r["files"]:
            r["missing"].append(path)
        else:
            r["notes"].append("custom graphicClass %s: any layout accepted" % c)
    else:
        one(path)
    return r


# ------------------------------------------------------------------ load the two mods' defs
core_roots = [DATA / "Core" / "Defs"] + [DATA / n / "Defs" for n in ("Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey") if (DATA / n / "Defs").is_dir()]
mod_roots = {m: MODS / m / "Defs" for m in OURS}
print("loading defs ...", file=sys.stderr)
mod_defs = {}
all_named = {}
for m, rt in mod_roots.items():
    dd, nn = load_defs([rt])
    mod_defs[m] = dd
    all_named.update(nn)
_, core_named = load_defs(core_roots)
all_named = {**core_named, **all_named}
core_defnames = set()
for root in core_roots:
    for f in root.rglob("*.xml"):
        try:
            core_defnames.update(re.findall(r"<defName>\s*([^<\s]+)\s*</defName>", f.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            pass

# repo defs for the deployed-vs-repo defName comparison
repo_defnames = {}
for m in OURS:
    dd, _ = load_defs([SRC / m / "Defs"])
    repo_defnames[m] = set(k[1] for k in dd)

# other-mod duplicates of our defNames
dup_override = []
for p, r in order:
    if p in OURS.values() or p.startswith("ludeon."):
        continue
    if (r / "Defs").is_dir():
        txt_names = set()
        for f in (r / "Defs").rglob("*.xml"):
            try:
                txt_names.update(re.findall(r"<defName>\s*([^<\s]+)\s*</defName>", f.read_text(encoding="utf-8", errors="replace")))
            except OSError:
                pass
        mine = {k[1] for m in OURS for k in mod_defs[m]}
        for n in sorted(txt_names & mine):
            dup_override.append((p, n))

# ------------------------------------------------------------------ station subjects
sys.path.insert(0, str(SRC / "GimmeSomeSlack")); sys.path.insert(0, str(SRC / "FlowWorks")); sys.path.insert(0, str(SRC))
station_strings = {"GimmeSomeSlack": set(), "FlowWorks": set()}
station_note = []


exact_strings = set()


def strings_of(o, acc, depth=0):
    if depth > 12:
        return
    if isinstance(o, str):
        acc.add(o); exact_strings.add(o)
        acc.update(re.findall(r"[A-Za-z][A-Za-z0-9_]{3,}", o))
    elif isinstance(o, dict):
        for k, v in o.items():
            strings_of(k, acc, depth + 1); strings_of(v, acc, depth + 1)
    elif isinstance(o, (list, tuple, set)):
        for v in o:
            strings_of(v, acc, depth + 1)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


gss_mod = fw_mod = None
try:
    gss_mod = load_module("gss_human_review", SRC / "GimmeSomeSlack/human_review.py")
    strings_of(gss_mod.station_list(), station_strings["GimmeSomeSlack"])
    for nm in ("SETTINGS", "CARD", "STUFFED"):
        strings_of(getattr(gss_mod, nm, None), station_strings["GimmeSomeSlack"])
except Exception as ex:
    station_note.append("GSS station_list import failed (%r): fell back to scanning the builder source for quoted names" % ex)
try:
    fw_mod = load_module("fw_review_map", SRC / "FlowWorks/review_map.py")
    strings_of(fw_mod.station_list(), station_strings["FlowWorks"])
    strings_of(fw_mod.SETUPS, station_strings["FlowWorks"])
    strings_of(getattr(fw_mod, "RIVERS", None), station_strings["FlowWorks"])
    strings_of(getattr(fw_mod, "RIVER", None), station_strings["FlowWorks"])
    strings_of(fw_mod.VIS.stations(), station_strings["FlowWorks"])
except Exception as ex:
    station_note.append("FlowWorks review_map import failed (%r): fell back to scanning builder source" % ex)
for m, files in (("GimmeSomeSlack", [SRC / "GimmeSomeSlack/human_review.py"]),
                 ("FlowWorks", list((SRC / "FlowWorks").glob("review_map*.py")) + [SRC / "FlowWorks/review_map_stations_visuals.json"])):
    for f in files:
        station_strings[m].update(re.findall(r"[A-Za-z][A-Za-z0-9_]{3,}", f.read_text(encoding="utf-8", errors="replace")))
# FlowWorks rivers builder lives in review_map_rivers.py (in the glob above). Both maps cross-build the hose: share the sets
shared_strings = station_strings["GimmeSomeSlack"] | station_strings["FlowWorks"]

# ------------------------------------------------------------------ build slots
slots = []   # dicts
subjects = OrderedDict()   # (mod, defName) -> dict(type, on_station)


active_set = set(active)


def gated_off(el):
    req = [x.strip().lower() for x in (el.get("MayRequire") or "").split(",") if x.strip()]
    anyof = [x.strip().lower() for x in (el.get("MayRequireAnyOf") or "").split(",") if x.strip()]
    if req and not all(x in active_set for x in req):
        return ",".join(req)
    if anyof and not any(x in active_set for x in anyof):
        return ",".join(anyof)
    return None


def add_slot(mod, subject, stype, slot, path, cls, src, ctx=None, expect_kind="xml", fallback=None, tag=None, gated=None):
    ctx = ctx or {}
    res = check_slot(path, cls, tag or slot, ctx.get("shader"))
    s = dict(mod=mod, subject=subject, stype=stype, slot=slot, path=path, cls=cls or "", src=src, fallback=fallback,
             drawSize=ctx.get("drawSize"), size=ctx.get("size"), **res)
    # vanilla / owned classification
    if gated and res["missing"]:
        s["status"] = "GATED"
        s["gated"] = gated
    elif res["missing"] and not owned(path):
        s["status"] = "VANILLA"
        s["vanilla"] = vanilla_status(path)
    elif res["missing"]:
        s["status"] = "FALLBACK" if fallback else "MISSING"
    else:
        s["status"] = "OK"
    slots.append(s)
    return s


unresolved_parents = []
for m, dd in mod_defs.items():
    for (tag, dn), el in dd.items():
        rel = resolve(el, all_named)
        if rel.get("_unresolved_parent"):
            unresolved_parents.append((m, dn, rel.get("_unresolved_parent")))
        size = parse_vec(rel.find("size"))
        found = extract_slots(rel, "", None)
        on_station = dn in station_strings[m] or dn in shared_strings
        if found or tag in ("ThingDef", "TerrainDef", "ThingStyleDef", "StyleCategoryDef"):
            subjects[(m, dn)] = dict(type=tag, on_station=on_station, slots=len(found), file=Path(el.get("_file")).name)
        for p, text, cls, ctx in found:
            ctx = dict(ctx)
            ctx["size"] = size
            leaf = p.split("/")[-1]
            c = cls
            if tag == "TerrainDef" and leaf == "texturePath":
                c = c or "Graphic_Terrain"
            add_slot(m, dn, tag, p.replace(tag + "/", "", 1), text, c, "xml", ctx, tag=p, gated=gated_off(el))

# defs used by stations from vanilla (named in the builders): list only
vanilla_subjects = sorted(n for n in (core_defnames & exact_strings) if n and not any(n == k[1] for k in subjects))

# ---- C#-built paths (rule tables; each cites its Source file)
GSS, FW = "RimMandrake/GimmeSomeSlack/", "RimMandrake/FlowWorks/"


def code(mod, subject, slot, path, src, fallback=None, ctx=None):
    add_slot(mod, subject, "C#", slot, path, None, src, ctx or {}, fallback=fallback)


gs_src = "GimmeSomeSlack/Source/"
# art board (human_review.art_slots) : piece x look rows. The hose rows live in FlowWorks' texture folder.
if gss_mod is not None:
    for piece, row in gss_mod.art_slots():
        for look, (st, rel) in row.items():
            if rel in ("-",) or st == "n/a":
                continue
            is_hose = piece.startswith("hose") and not piece.startswith("hose reel coil")
            root = FW if is_hose else GSS
            code("FlowWorks" if is_hose else "GimmeSomeSlack", "art slot: " + piece, look, root + rel,
                 "human_review.py art_slots (CordMaterials/AerialMaterials/HoseStyles/ConduitStylePicker)",
                 fallback=(st if st.startswith("fallback") else "code fallback: " + st) if True else None)
else:
    station_note.append("art_slots() board not imported: C#-built GSS slots reduced to the extra table only")
for rel, why in (("Strand_Jawa", "CordMaterials static ctor, reportFailure:true"), ("StrandShadow", "CordMaterials / AerialMaterials shadow fallback"),
                 ("SparkGlow", "CordMaterials + AerialMaterials glow"), ("Aerial/SpanShadow", "AerialMaterials shadow"),
                 ("ConduitTransparent", "ConduitVisuals.cs:30"), ("PowerSwitch", "ConduitVisuals.cs:131 SwitchTexPathOurs"),
                 ("PowerSwitch_Off", "ConduitVisuals SwitchTexPathOurs + _Off"), ("Aerial/SpanWire", "AerialMaterials span (default look root)"),
                 ("Aerial/Insulator", "Aerial anchor art (see orphan check)"), ("Aerial/PoleTopDown", "Aerial anchor art (see orphan check)"),
                 ("Aerial/WallBracket", "unstyled bracket (see orphan check)")):
    code("GimmeSomeSlack", "C# path", "root art", GSS + rel, gs_src + why)
for col in ("Orange", "Green", "Brown", "Yellow", "Blue"):
    code("GimmeSomeSlack", "C# path", "ExtCord strand " + col, GSS + "Styles/ExtCord/Strand_" + col, gs_src + "CordMaterials.StrandPathsFor")
for k in ("BlackRubber", "CorrugatedSteel", "CoiledBlack"):
    code("GimmeSomeSlack", "C# path", "StarWars strand " + k, GSS + "Styles/StarWars/Strand_" + k, gs_src + "CordMaterials.StrandPathsFor")
for col in ("Green", "Brown", "Yellow", "Blue"):
    for sl in ("Plug", "Junction_T", "Junction_X", "StubWall", "StubRock", "EndFrayed_Dead"):
        code("GimmeSomeSlack", "C# path", "ExtCord %s piece %s" % (col, sl), GSS + "Styles/ExtCord/%s/%s" % (col, sl), gs_src + "CordMaterials.Build (ColourSlots, B14)", fallback="code: the style's own (orange) piece")
code("GimmeSomeSlack", "C# path", "Cybertek strand", GSS + "Styles/Cybertek/Strand", gs_src + "CordMaterials.StrandPathsFor")
# FlowWorks: hose pieces x looks, reel art x looks, pipe, tanks, scorch, designators
fw_src = "FlowWorks/Source/"
for look in LOOKS:
    folder = FW + "Hose/" + ("" if look == "Scrapper" else "Styles/" + look + "/")
    for piece in ("Strand_Flat", "Strand_Plump", "Binding", "Coupling_Bare", "Nozzle_Bare", "EndCap_Bare", "Mouth", "Reel_PumpHookup", "Reel_Deployed"):
        code("FlowWorks", "C# path", "hose %s %s" % (piece, look), folder + piece, fw_src + "Hose/HoseStyles.PathFor/ReelArt")
    code("FlowWorks", "C# path", "pipe atlas " + look, FW + "Pipe/" + look + "/UniversalPipe_Atlas", fw_src + "Machinery/PipeStyles.AtlasPath")
    code("FlowWorks", "C# path", "pipe menu icon " + look, FW + "Pipe/" + look + "/UniversalPipe_MenuIcon", fw_src + "Machinery/PipeStyles.IconPath")
    for t in ("RM_LiquidTank", "RM_LiquidTankTall", "RM_UniversalCargoTank", "RM_UniversalCargoTankXTall"):
        code("FlowWorks", "C# path", "%s %s" % (t, look), FW + "Tank/%s/%s" % (look, t), fw_src + "Machinery/PipeStyles.TankTexPath")
code("FlowWorks", "C# path", "hose shadow (shared)", FW + "Hose/Strand_Shadow", fw_src + "Hose/HoseStyles.SharedShadow")
for n in ("Nozzle", "EndCap", "Reel_PumpHookup"):
    code("FlowWorks", "C# path", "reel root " + n, FW + "Hose/" + n, fw_src + "Hose/CompHoseReel.cs:158-160", fallback="code: ContentFinder(..., false)")
for i in range(12):
    for k in ("Char", "Ash"):
        code("FlowWorks", "C# path", "scorch debris %s%d" % (k, i), "Terrain/FlowWorks/Debris/RM_ScorchDebris_%s%d" % (k, i), fw_src + "Superdeep/RM_FaceMaterial.DebrisMat")
for n in ("RM_Scorch_Ash", "RM_Scorch_DirtAsh", "RM_Scorch_Soot"):
    code("FlowWorks", "C# path", n, "Terrain/FlowWorks/" + n, fw_src + "Superdeep/RM_FaceMaterial.cs:179-181")
for n in ("RM_FillInCanal", "RM_DigCanal"):
    code("FlowWorks", "C# path", "designator icon " + n, "UI/Designators/FlowWorks/" + n, fw_src + "(designator)")

# ------------------------------------------------------------------ dedupe identical (subject,path) code/xml slots against XML ones
# (kept: a path reached by two routes is simply two slots; resolved-picture counts use distinct files)

# ------------------------------------------------------------------ deployed vs repo
def repo_file_for(path_rel):
    return None


deploy_defects = []
referenced = set()   # lower rel (no ext) of deployed files referenced
files_by_pic = OrderedDict()   # Path -> list of (subject, slot, mod-of-file)
for s in slots:
    for f in s["files"]:
        files_by_pic.setdefault(f, []).append((s["subject"], s["slot"], s))
        referenced.add(str(f))
    # repo-only
    if s["status"] in ("MISSING", "FALLBACK"):
        exp = [e for e in s["missing"]]
        in_repo = []
        for e in exp:
            e0 = e.split(" ")[0].rstrip("/")
            if e0.lower() in repo_all or any(k.startswith(e0.lower() + "/") for k in repo_all):
                in_repo.append(e0)
        if in_repo:
            s["status"] = "DEPLOY"
            s["notes"].append("exists in the repo Textures but not in the deployed copy")
# stale deployed copies (bytes differ from repo)
stale = []
for f in files_by_pic:
    for m in OURS:
        try:
            rel = f.relative_to(MODS / m / "Textures")
        except ValueError:
            continue
        rp = SRC / m / "Textures" / rel
        if rp.is_file():
            try:
                if hashlib.md5(f.read_bytes()).hexdigest() != hashlib.md5(rp.read_bytes()).hexdigest():
                    stale.append((m, str(rel)))
            except OSError:
                pass
        else:
            stale.append((m, str(rel) + "  (deployed only; not in repo)"))

# override: a path our mod ships but a LATER active mod also ships
overridden = []
for s in slots:
    for pk, allp in zip(s["pkgs"], s["shipped_by"] or [[]] * len(s["pkgs"])):
        mine = OURS.get(s["mod"])
        if mine in allp and pk != mine:
            overridden.append((s, pk))
            break

# orphans
orphans = {}
for m in OURS:
    td = MODS / m / "Textures"
    refd_dirs = set()
    allf = [f for f in td.rglob("*") if f.is_file()]
    for f in allf:
        if str(f) in referenced:
            continue
        stem = f.stem
        # mask / sibling of a referenced file counts as referenced (_m, _southm etc.)
        base = str(f.with_suffix(""))
        if any(base.lower().startswith(r.rsplit(".", 1)[0].lower()) and re.match(r"^(_?(south|east|north|west)?m|_(south|east|north|west))$", base[len(r.rsplit('.', 1)[0]):], re.I) for r in ()):
            continue
        orphans.setdefault(m, []).append(f)
# mask files: *_m / _southm etc. whose base is referenced
def masks_filter(lst):
    refbases = {os.path.splitext(r)[0].lower() for r in referenced}
    out = []
    for f in lst:
        b = os.path.splitext(str(f))[0].lower()
        if re.search(r"(_m|m)$", b) and any(b[:-1] in rb or b[:-2] in rb for rb in refbases if rb):
            if b[:-2] in refbases or b[:-1] in refbases:
                continue
        out.append(f)
    return out
for m in orphans:
    orphans[m] = masks_filter(orphans[m])

# ------------------------------------------------------------------ patches that mention our defs (UNMEASURED effects)
patch_hits = []
mine_names = {k[1] for m in OURS for k in mod_defs[m]}
for p, r in order:
    pd = r / "Patches"
    if not pd.is_dir():
        continue
    for f in pd.rglob("*.xml"):
        try:
            t = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if re.search(r"texPath|graphicData|texturePath|uiIconPath", t):
            hits = sorted({n for n in re.findall(r'defName="([^"]+)"', t) if n in mine_names})
            if hits and p not in OURS.values():
                patch_hits.append((p, f.name, hits[:6]))
own_patches = []
for m in OURS:
    pd = MODS / m / "Patches"
    if pd.is_dir():
        for f in pd.rglob("*.xml"):
            t = f.read_text(encoding="utf-8", errors="replace")
            if re.search(r"texPath|graphicData|texturePath|uiIconPath", t):
                own_patches.append((m, f.name))

def_diff = []
for m in OURS:
    rd, dd = SRC / m / "Defs", MODS / m / "Defs"
    rf = {str(f.relative_to(rd)): f for f in rd.rglob("*.xml")}
    df = {str(f.relative_to(dd)): f for f in dd.rglob("*.xml")}
    for k in sorted(set(rf) | set(df)):
        if k not in df:
            def_diff.append((m, k, "in repo, not deployed"))
        elif k not in rf:
            def_diff.append((m, k, "deployed only"))
        elif hashlib.md5(rf[k].read_bytes()).hexdigest() != hashlib.md5(df[k].read_bytes()).hexdigest():
            def_diff.append((m, k, "bytes differ"))

# ------------------------------------------------------------------ counts
n_slots = len(slots)
resolved_files = list(files_by_pic)
mod_pics = [f for f in resolved_files if str(f).startswith(str(MODS))]
n_ok = sum(1 for s in slots if s["status"] == "OK")
bad = [s for s in slots if s["status"] in ("MISSING", "FALLBACK", "DEPLOY")]
vanilla_slots = [s for s in slots if s["status"] == "VANILLA"]
n_subjects = len(subjects)

json.dump(dict(subjects=len(subjects), slots=n_slots, pictures=len(resolved_files), missing=len(bad),
               slot_table=[dict(mod=s["mod"], subject=s["subject"], slot=s["slot"], path=s["path"], status=s["status"], cls=s["cls"],
                                files=[str(f) for f in s["files"]], vanilla=s.get("vanilla", "")) for s in slots]), open(HERE / "audit.json", "w"), indent=0)

# ------------------------------------------------------------------ FINDINGS.md
L = []
n_fb = sum(1 for s in bad if s["status"] == "FALLBACK")
n_miss_missing = sum(1 for s in bad if s["status"] == "MISSING")
n_dep = sum(1 for s in bad if s["status"] == "DEPLOY")
L.append("PW7 graphics audit, GimmeSomeSlack + FlowWorks review maps, %s: %d subjects, %d slots, %d pictures resolved, %d missing "
         "(%d plain missing, %d known art-board fallbacks, %d deploy-only)" % ("2026-10-15", n_subjects, n_slots, len(resolved_files), len(bad),
                                                                                 n_miss_missing, n_fb, n_dep))
L.append("")
L.append("Measured against the DEPLOYED mods in `%s` in ModsConfig.xml order (%d activeMods, %d resolved to a folder; later wins). "
         "Re-run: `python3 /home/mandrake/rm/bench/Transient/review_graphics_audit_gssfw_20261015/audit.py`." % (MODS, len(active), len(order)))
L.append("Subjects = every ThingDef/TerrainDef/ThingStyleDef/StyleCategoryDef (any def with a texture path) in the DEPLOYED Defs of both mods "
         "(%d of them named by a station builder; the rest are shown by their style or not at all) plus the C#-built art rows." %
         sum(1 for v in subjects.values() if v["on_station"]))
L.append("")
L.append("## Defects")
L.append("")
i = 0
if not bad and not overridden:
    L.append("None.")
for s in bad:
    i += 1
    tag = {"MISSING": "MISSING", "FALLBACK": "FALLBACK (art board M, the code draws its fallback)", "DEPLOY": "DEPLOY (repo has it, game copy lacks it)"}[s["status"]]
    L.append("%d. [%s] `%s` slot `%s` (%s): expected `%s`; found nothing in any active mod%s" % (
        i, tag, s["subject"], s["slot"], s["mod"], ", ".join(s["missing"]),
        ("; " + "; ".join(s["notes"])) if s["notes"] else ""))
for s, pk in overridden:
    i += 1
    L.append("%d. [OVERRIDDEN] `%s` slot `%s`: `%s` is also shipped by `%s`, a later mod, which wins" % (i, s["subject"], s["slot"], s["path"], pk))
for m, rel in stale:
    i += 1
    L.append("%d. [DEPLOY-STALE] %s `%s`: deployed copy differs from the repo copy" % (i, m, rel))
for m, k, why in def_diff:
    i += 1
    L.append("%d. [DEPLOY-STALE-DEF] %s Defs/%s: %s (the audit read the deployed copy)" % (i, m, k, why))
for p, n in dup_override:
    i += 1
    L.append("%d. [DEF-OVERRIDE] active mod `%s` defines defName `%s`, which our mod also defines" % (i, p, n))
for slot_ in slots:
    if slot_["notes"] and slot_["status"] == "OK":
        pass
notes = [s for s in slots if s["notes"] and s["status"] == "OK"]
L.append("")
L.append("## Notes (resolved, with a caveat)")
L.append("")
if notes:
    for s in notes:
        L.append("- `%s` slot `%s` `%s`: %s" % (s["subject"], s["slot"], s["path"], "; ".join(s["notes"])))
else:
    L.append("None.")
L.append("")
L.append("## Orphans (deployed textures no def, style, or traced C# rule references): not defects")
L.append("")
for m, lst in orphans.items():
    L.append("%s: %d" % (m, len(lst)))
    for f in sorted(lst):
        L.append("  - `%s`" % f.relative_to(MODS / m / "Textures"))
L.append("")
L.append("Orphan caveat: C# builds more paths than the rule tables above list; each orphan name should be grepped in Source/ before it is called dead.")
L.append("")
L.append("## UNMEASURED")
L.append("")
L.append("- Vanilla/Core/DLC textures (%d slots across %d defs) live in .assets bundles: matched by file name against the extracted bundle index only, otherwise 'vanilla, not checked on disk'." % (len(vanilla_slots), len({s['subject'] for s in vanilla_slots})))
if not_found_active:
    L.append("- activeMods with no folder under Mods/ or Data/ (workshop or missing): %s. Their textures were not searched; they cannot override ours here." % ", ".join(not_found_active))
L.append("- Vanilla station subjects (their art is vanilla or patched at runtime by C#; textures not read here): %s" % (", ".join(vanilla_subjects[:60]) or "none"))
L.append("- C# paths built from runtime state (settings, per-net colour, tint) are covered only through the rule tables in audit.py; a path the code builds that is not in a table is not seen.")
L.append("- Other mods' XML patches on our defs: %s. Our own patches touching graphics: %s." % (
    ("; ".join("%s/%s -> %s" % h for h in patch_hits) or "none found by text search"), ("; ".join("%s/%s" % h for h in own_patches) or "none")))
L.append("- Station-to-def matching is by name appearing anywhere in the builder data (%s)." % ("; ".join(station_note) or "both builders imported"))
if unresolved_parents:
    L.append("- ParentName not found in Core/DLC/our Defs (a third-party mod's abstract, e.g. Dubs Bad Hygiene ResourceBasedMom): %s. Their own graphicData paths WERE checked; anything inherited from the parent was not." % ", ".join("%s<-%s" % (d, p) for _, d, p in unresolved_parents))
gated = [s for s in slots if s["status"] == "GATED"]
if gated:
    L.append("- GATED OFF in the live list (MayRequire donor not in activeMods, def never loads, nothing to draw): %d slots on %s; needs `%s`." % (len(gated), ", ".join(sorted({x['subject'] for x in gated})), gated[0]["gated"]))
L.append("- Styles: ThingStyleDef graphics are read from XML. GSS conduit styles are markers with no graphicData by design (ConduitStyles.xml header), so their art is the code rows above.")
L.append("")
L.append("Fine: %d of %d slots resolved to a picture the game will load (%d distinct files, %d of them mod art on the sheet); %d vanilla slots not checked on disk." %
         (n_ok, n_slots, len(resolved_files), len(mod_pics), len(vanilla_slots)))
(HERE / "FINDINGS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L[:3]))

# ------------------------------------------------------------------ sheet.png
try:
    from PIL import Image, ImageDraw, ImageFont
    sys.path.insert(0, str(SRC / "Utils/art"))
    import scale_panel as SP
    PPC = 64
    human, mesh, hoff = SP.human_sprite(PPC)
    # trim human to its drawn bbox
    bb = human.getbbox()
    human = human.crop(bb)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    tiles = []
    for f, uses in files_by_pic.items():
        if not str(f).startswith(str(MODS)):
            continue
        try:
            im = Image.open(f).convert("RGBA")
        except Exception:
            continue
        subj, slot, s = uses[0]
        ds = s.get("drawSize") or s.get("size")
        basis = "drawSize" if s.get("drawSize") else ("def size" if s.get("size") else "assumed 1 cell")
        kind = "ui" if re.search(r"icon|designator|UI/", s["path"] + s["slot"], re.I) else "world"
        if s.get("src") != "xml" and kind == "world":
            basis = "assumed 1 cell (code piece)"
        w_c, h_c = (ds if ds else (1.0, 1.0))
        if kind == "ui":
            w_c, h_c, basis = 1.0, 1.0, "UI icon at 1 cell (not in-world)"
        if im.width / max(im.height, 1) > 3 and not ds:     # strand strips: height 1/8 cell at width 1 cell, shown native-ish
            w_c, h_c, basis = 1.0, 1.0 * im.height / im.width, "assumed 1 cell wide (tiling strip)"
        w, h = max(1, round(w_c * PPC)), max(1, round(h_c * PPC))
        shrink = 1.0
        mx = 8 * PPC
        if max(w, h) > mx:
            shrink = mx / max(w, h)
            w, h = max(1, round(w * shrink)), max(1, round(h * shrink))
        art = im.resize((w, h), Image.LANCZOS if (w < im.width) else Image.NEAREST)
        lab = ["%s | %s" % (subj, slot), f.name + (" (%d%%)" % round(shrink * 100) if shrink < 1 else "") + " | " + basis]
        if len(uses) > 1:
            lab[0] += "  +%d more" % (len(uses) - 1)
        tiles.append((art, lab))
    W = 2700
    pad = 10
    rows, cur, curw, curh = [], [], 0, 0
    for art, lab in tiles:
        tw = max(art.width + human.width + 3 * pad, 330)
        th = max(art.height, human.height) + 40
        if curw + tw > W and cur:
            rows.append((cur, curh)); cur, curw, curh = [], 0, 0
        cur.append((art, lab, tw, th)); curw += tw; curh = max(curh, th)
    if cur:
        rows.append((cur, curh))
    H = sum(h for _, h in rows) + 60
    sheet = Image.new("RGBA", (W, H), (36, 32, 28, 255))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 8), "PW7 contact sheet: every resolved mod picture of GimmeSomeSlack + FlowWorks at 64 px per cell, vanilla colonist beside each (%d pictures)" % len(tiles), fill=(235, 220, 190, 255), font=font)
    y = 40
    for cur, rh in rows:
        x = pad
        for art, lab, tw, th in cur:
            base = y + rh - 40
            # one-cell reference box under the art
            d.rectangle([x, base - art.height, x + art.width, base], outline=(90, 80, 70, 255))
            sheet.alpha_composite(art, (x, base - art.height))
            hx = x + art.width + pad
            sheet.alpha_composite(human, (hx, base - human.height))
            d.text((x, base + 4), lab[0][:(tw - 12) // 7], fill=(235, 220, 190, 255), font=font)
            d.text((x, base + 18), lab[1][:(tw - 12) // 7], fill=(160, 150, 135, 255), font=font)
            x += tw
        y += rh
    out = sheet.convert("RGB")
    out.save(HERE / "sheet.png", optimize=True)
    if (HERE / "sheet.png").stat().st_size > 8 * 1024 * 1024:
        out.convert("P", palette=Image.ADAPTIVE, colors=256).save(HERE / "sheet.png", optimize=True)
    print("sheet.png", out.size, (HERE / "sheet.png").stat().st_size)
except Exception as ex:
    import traceback; traceback.print_exc()
    print("SHEET FAILED", ex)
