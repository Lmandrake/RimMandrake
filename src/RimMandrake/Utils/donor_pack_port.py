#!/usr/bin/env python3
"""donor_pack_port.py -- the script for DONOR_DEFS_PORT_TO_OURS_1 on mlie.starwarsanimalcollection.

Plan: design/RimMandrake/donor_pack_port_plan_2026-10-14.md. Tracker: design/RimMandrake/donor_pack_port_tracker.md.

    python3 src/RimMandrake/Utils/donor_pack_port.py diff [--json OUT]   W0: every twin against the donor
    python3 src/RimMandrake/Utils/donor_pack_port.py rosters             donor-named roster rows, parsed as XML
    python3 src/RimMandrake/Utils/donor_pack_port.py repoint [--apply]   W1: those rows -> the RSW_ twin, our guard
    python3 src/RimMandrake/Utils/donor_pack_port.py check [--species A,B]  every RSW_ roster row resolves; ports complete
    python3 src/RimMandrake/Utils/donor_pack_port.py art --extract DIR [--apply] texPath...   donor art via art ledger

`diff` compares each of the donor's 160 races with our same-named RSW_/RM_/RUT_ race ThingDef + PawnKindDef:
statBases, race body / bodySize / healthScale / lifeExpectancy, lifeStageAges, PawnKind lifeStage count and
whether every texPath the twin names resolves to a PNG under src/**/Textures (else it binds only through the
donor). A body is equal if the twin names the donor's body or RSW_<body>. Our texPath differing from the donor's
is expected (regenerated art) and is reported only when it does not resolve in our tree.

NOT PROVEN HERE: that anything loads. That is W4 (a donor-off load), owed live.
"""
import argparse
import copy
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(REPO, "src")
DONOR = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3497316713"
DONOR_PKG = "mlie.starwarsanimalcollection"
DECLINED = {"Mynock"}  # owner 2026-09-18: donor Mynock stays unported; RSW_Mynock is a different, owner-authored species
PREFIXES = ("RSW_", "RM_", "RUT_")


def parse(path):
    try:
        return ET.parse(path).getroot()
    except ET.ParseError:
        return None


def donor_defs(donor=DONOR):
    races, kinds = {}, {}
    for f in glob.glob(os.path.join(donor, "1.6", "Defs", "**", "*.xml"), recursive=True):
        r = parse(f)
        if r is None:
            continue
        for d in r:
            if d.get("Abstract") == "True":
                continue
            if d.tag == "ThingDef" and d.find("race") is not None:
                races[d.findtext("defName")] = d
            elif d.tag == "PawnKindDef":
                kinds[d.findtext("race")] = d
    return races, kinds


def our_defs():
    races, kinds, named = {}, {}, {}
    files = {}
    for f in glob.glob(os.path.join(SRC, "**", "Defs", "**", "*.xml"), recursive=True):
        r = parse(f)
        if r is None:
            continue
        for d in r:
            if d.get("Name"):
                named[d.get("Name")] = d
            if d.get("Abstract") == "True":
                continue
            dn = d.findtext("defName")
            if d.tag == "ThingDef" and d.find("race") is not None and dn and dn.startswith(PREFIXES):
                races[dn] = d
                files[dn] = os.path.relpath(f, REPO)
            elif d.tag == "PawnKindDef" and dn:
                kinds.setdefault(d.findtext("race"), d)
    return races, kinds, named, files


def resolve(d, named, path):
    """Value at `path` following ParentName within our own abstracts (one chain)."""
    seen = 0
    while d is not None and seen < 8:
        v = d.find(path)
        if v is not None:
            return v
        d = named.get(d.get("ParentName"))
        seen += 1
    return None


def stats(d, named=None):
    out = {}
    chain = []
    while d is not None and len(chain) < 8:
        chain.append(d)
        d = (named or {}).get(d.get("ParentName"))
    for d in reversed(chain):
        sb = d.find("statBases")
        if sb is not None:
            for s in sb:
                out[s.tag] = (s.text or "").strip()
    return out


def lifestages(d):
    ls = d.find("race/lifeStageAges")
    if ls is None:
        return []
    return [(li.findtext("def"), li.findtext("minAge")) for li in ls]


def kind_tex(k):
    out = []
    if k is None:
        return out
    for el in k.iter():
        if el.tag == "texPath" and el.text:
            out.append(el.text.strip())
    return out


def texture_index():
    idx = set()
    for f in glob.glob(os.path.join(SRC, "**", "Textures", "**", "*.png"), recursive=True):
        rel = f.replace("\\", "/").split("/Textures/", 1)[1][:-4].lower()
        idx.add(rel)
        idx.add(os.path.dirname(rel))  # Graphic_Random folders
    return idx


def resolves(tp, idx):
    t = tp.lower()
    return t in idx or (t + "_south") in idx or (t + "_east") in idx


def num_eq(a, b):
    try:
        return abs(float(a) - float(b)) < 1e-6
    except (TypeError, ValueError):
        return a == b


def body_eq(donor_body, ours):
    return ours in (donor_body, "RSW_" + (donor_body or ""))


def donor_names(donor=DONOR):
    """Every defName (and abstract Name) the donor defines."""
    out = set()
    for f in glob.glob(os.path.join(donor, "1.6", "Defs", "**", "*.xml"), recursive=True):
        r = parse(f)
        for d in (r if r is not None else []):
            for n in (d.findtext("defName"), d.get("Name")):
                if n:
                    out.add(n)
    return out


def our_names():
    out = set()
    for f in glob.glob(os.path.join(SRC, "**", "Defs", "**", "*.xml"), recursive=True):
        r = parse(f)
        for d in (r if r is not None else []):
            for n in (d.findtext("defName"), d.get("Name")):
                if n:
                    out.add(n)
    return out


def our_typed():
    out = set()
    for f in glob.glob(os.path.join(SRC, "**", "Defs", "**", "*.xml"), recursive=True):
        r = parse(f)
        for d in (r if r is not None else []):
            if isinstance(d.tag, str) and d.findtext("defName"):
                out.add((d.tag, d.findtext("defName")))
    return out


def donor_refs(defs, dnames, onames):
    """Names in these defs (text, element tag, ParentName) that only the donor defines: each is a cross-reference
    that fails the moment the donor is off. Sounds were absorbed whole as RSW_<name>, so a bare donor sound
    counts too."""
    hits = set()
    for d in defs:
        if d is None:
            continue
        for el in d.iter():
            for n in ((el.text or "").strip(), el.tag, el.get("ParentName") or ""):
                if n in dnames and n not in onames:
                    hits.add(n)
    return sorted(hits)


def diff_one(name, dr, dk, our, ok, named, idx):
    issues = []
    ds, os_ = stats(dr), stats(our, named)
    for k in sorted(set(ds) | set(os_)):
        if not num_eq(ds.get(k), os_.get(k)):
            issues.append(f"stat {k}: donor {ds.get(k)} ours {os_.get(k)}")
    for p in ("race/baseBodySize", "race/baseHealthScale", "race/lifeExpectancy"):
        a, b = dr.find(p), resolve(our, named, p)
        a = a.text.strip() if a is not None and a.text else None
        b = b.text.strip() if b is not None and b.text else None
        if not num_eq(a, b):
            issues.append(f"{p.split('/')[-1]}: donor {a} ours {b}")
    db = dr.findtext("race/body")
    ob = resolve(our, named, "race/body")
    ob = ob.text.strip() if ob is not None and ob.text else None
    if not body_eq(db, ob):
        issues.append(f"body: donor {db} ours {ob}")
    dl, ol = lifestages(dr), lifestages(our)
    if [x[0] for x in dl] != [x[0] for x in ol] or not all(num_eq(a[1], b[1]) for a, b in zip(dl, ol)):
        issues.append(f"lifeStageAges: donor {dl} ours {ol}")
    if ok is None:
        issues.append("no PawnKindDef")
    else:
        dn = len(dk.findall("lifeStages/li")) if dk is not None else 0
        on = len(ok.findall("lifeStages/li"))
        if dn != on:
            issues.append(f"kind lifeStages: donor {dn} ours {on}")
    tex_bad = [t for t in kind_tex(ok) if not resolves(t, idx)]
    tex_bad += [t for t in kind_tex(our) if not resolves(t, idx)]
    stub = len(os_) < 3 or not ol
    return issues, tex_bad, stub


def cmd_diff(a):
    dr, dk = donor_defs(a.donor)
    our, ok, named, files = our_defs()
    idx = texture_index()
    dnames, onames = donor_names(a.donor), our_names()
    rows = []
    for name in sorted(dr):
        twin = next((p + name for p in PREFIXES if p + name in our), None)
        row = {"species": name, "twin": twin, "file": files.get(twin)}
        if name in DECLINED:
            row["verdict"] = "DECLINED"
        elif twin is None:
            row["verdict"] = "NO_TWIN"
        else:
            issues, tex_bad, stub = diff_one(name, dr[name], dk.get(name), our[twin], ok.get(twin), named, idx)
            row.update(issues=issues, tex_unresolved=tex_bad, stub=stub,
                       donor_refs=donor_refs([our[twin], ok.get(twin)], dnames, onames))
            row["verdict"] = "STUB" if stub else ("MATCH" if not issues and not tex_bad else "DIFF")
        rows.append(row)
    from collections import Counter
    c = Counter(r["verdict"] for r in rows)
    print(f"donor races {len(dr)} | " + " ".join(f"{k}={v}" for k, v in sorted(c.items())))
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(rows, fh, indent=1)
        print(f"wrote {a.json}")
    return 0


def roster_lists(root):
    """Every roster list in a file: <wildAnimals> elements, and the <value> of a patch op whose xpath ends in
    /wildAnimals (patch-injected rows)."""
    for wa in root.iter("wildAnimals"):
        yield wa
    for op in root.iter():
        xp = op.find("xpath")
        v = op.find("value")
        if xp is not None and v is not None and (xp.text or "").strip().endswith("/wildAnimals"):
            yield v


def roster_rows():
    """Every <wildAnimals> child under src/ whose MayRequire names the donor (XML elements, never <li> counts)."""
    out = []
    for f in sorted(glob.glob(os.path.join(SRC, "**", "*.xml"), recursive=True)):
        r = parse(f)
        if r is None:
            continue
        for wa in roster_lists(r):
            for ch in wa:
                if DONOR_PKG in (ch.get("MayRequire") or "").lower():
                    out.append((os.path.relpath(f, REPO), ch.tag, (ch.text or "").strip()))
    return out


def cmd_rosters(a):
    rows = roster_rows()
    for r in rows:
        print("\t".join(r))
    print(f"{len(rows)} donor rows in {len(set(r[0] for r in rows))} files")
    return 0


OUR_PKG = "mandrake.rsw.swbestiary"


def cmd_repoint(a):
    """W1: rewrite each donor-named <wildAnimals> row whose species has a proven RSW_ twin to the twin, guarded by
    our own package. If the twin already has a row in the same <wildAnimals>, the donor row is deleted instead
    (two children with one name would collide). Species with no twin, and DECLINED ones, are left alone."""
    dr, _ = donor_defs(a.donor)
    our, _, _, _ = our_defs()
    only = set(a.only.split(",")) if a.only else None
    rows = roster_rows()
    changed, kept = 0, []
    for rel in sorted(set(r[0] for r in rows)):
        path = os.path.join(REPO, rel)
        root = parse(path)
        text = open(path, encoding="utf-8").read()
        new = text
        for wa in roster_lists(root):
            names = {ch.tag for ch in wa}
            for ch in wa:
                if DONOR_PKG not in (ch.get("MayRequire") or "").lower():
                    continue
                sp, twin = ch.tag, "RSW_" + ch.tag
                if sp in DECLINED or twin not in our or (only and sp not in only):
                    kept.append((rel, sp))
                    continue
                pat = re.compile(r'([ \t]*)<%s MayRequire="[^"]*%s[^"]*">([^<]*)</%s>([^\n]*)\n' % (
                    re.escape(sp), re.escape(DONOR_PKG), re.escape(sp)), re.I)
                m = pat.search(new)
                if not m:
                    print(f"NO TEXT MATCH {rel} {sp}")
                    continue
                if twin in names:
                    rep = ""
                    print(f"{rel}: drop {sp} (twin {twin} already in this roster)")
                else:
                    rep = f'{m.group(1)}<{twin} MayRequire="{OUR_PKG}">{m.group(2)}</{twin}>{m.group(3)}\n'
                new = new[:m.start()] + rep + new[m.end():]
                changed += 1
        if new != text:
            ET.fromstring(new.encode("utf-8"))  # must still parse
            if a.apply:
                open(path, "w", encoding="utf-8").write(new)
    print(f"{'APPLIED' if a.apply else 'DRY'}: {changed} rows repointed/dropped; {len(kept)} left on the donor")
    for k in kept:
        print("  left:", *k)
    return 0


BESTIARY_TEX = os.path.join(SRC, "RimStarWars", "SWBestiary", "Textures")
FACING = re.compile(r"^(?:_(?:south|north|east|west)m?|m)?$")


def art_files(extract, tp):
    """Bundle PNGs (extracted with extract_bundle.py --keep-paths, lowercased) that a texPath binds:
    tp.png, tp_<facing>[m].png, or every PNG in folder tp (Graphic_Random)."""
    t = tp.lower().strip("/")
    d, base = os.path.split(t)
    out = []
    folder = os.path.join(extract, t)
    if os.path.isdir(folder):
        out += [os.path.join(folder, f) for f in sorted(os.listdir(folder)) if f.endswith(".png")]
    dd = os.path.join(extract, d)
    if os.path.isdir(dd):
        for f in sorted(os.listdir(dd)):
            if f.endswith(".png") and f.startswith(base) and FACING.match(f[len(base):-4]):
                out.append(os.path.join(dd, f))
    return out


def cmd_art(a):
    """Install extracted donor art for the given texPaths under SWBestiary/Textures/<texPath casing of the def>,
    through the art ledger (artwrite.TextureWriter, reason script:<this file>). Ruling: owner 2026-10-14,
    'ports may re-use extracted donor art until we regenerate'. Never overwrites a file already in our tree."""
    sys.path.insert(0, os.path.join(SRC, "RimMandrake", "Utils", "art"))
    from artwrite import TextureWriter
    tw = TextureWriter(__file__, provenance={"kind": "donor", "donor_pkg": DONOR_PKG}, dry_run=not a.apply)
    idx = texture_index()
    missing = []
    owned = []
    for tp in a.texpaths:
        if resolves(tp, idx):
            owned.append(tp)                                                 # already ours (e.g. owner art)
            continue
        files = art_files(a.extract, tp)
        if not files:
            missing.append(tp)
            continue
        for f, rel in art_targets(a.extract, tp, files):
            if rel[:-4].lower() in idx:
                continue                                                     # already ours: never touch
            dest = os.path.join(BESTIARY_TEX, rel)
            tw.copy(f, dest)
    print(f"{'APPLIED' if a.apply else 'DRY'}: {tw.counts} already-ours={len(owned)} missing={missing}")
    for r in tw.refusals:
        print("  REFUSED", r)
    return 1 if missing else 0


def cmd_check(a):
    """validate_patch.py does not check BiomeDef roster names (probed 2026-10-14: a bogus RSW_ row passes).
    This does: every RSW_ <wildAnimals> child under src/ (or in the given files) must name an RSW_ race ThingDef
    in src/ that has a PawnKindDef, and every PawnKind/race texPath of the ported species must resolve in our tree."""
    our, kinds, _, _ = our_defs()
    files = a.files or glob.glob(os.path.join(SRC, "**", "*.xml"), recursive=True)
    ok, bad = 0, []
    for f in files:
        r = parse(f)
        if r is None:
            continue
        for wa in roster_lists(r):
            for ch in wa:
                if not ch.tag.startswith("RSW_"):
                    continue
                if ch.tag in our and ch.tag in kinds:
                    ok += 1
                else:
                    bad.append((os.path.relpath(f, REPO), ch.tag))
    idx = texture_index()
    if a.vanilla_tex:
        VANILLA_TEX.update(x.strip().lower() for x in open(a.vanilla_tex) if x.strip())
    tex_bad = []
    for sp in (a.species.split(",") if a.species else []):
        d = "RSW_" + sp
        for t in kind_tex(our.get(d)) + kind_tex(kinds.get(d)):
            if not resolves(t, idx) and not vanilla_tex(t):
                tex_bad.append((d, t))
        if d not in our or d not in kinds:
            bad.append(("(species)", d))
    for f in glob.glob(os.path.join(SUPPORT_DIR, "*.xml")):          # support defs of every port batch
        r = parse(f)
        for d in (r if r is not None else []):
            for t in def_paths([d]):
                if not resolves(t, idx) and not vanilla_tex(t):
                    tex_bad.append((d.findtext("defName") or d.get("Name"), t))
    print(f"roster RSW_ rows resolved {ok}; unresolved {len(bad)}; unresolved texPaths {len(tex_bad)}")
    for b in bad + tex_bad:
        print("  BAD", *b)
    return 1 if bad or tex_bad else 0


RACES_DIR = os.path.join(SRC, "RimStarWars", "SWBestiary", "Defs", "ThingDefs_Races")
SUPPORT_DIR = os.path.join(SRC, "RimStarWars", "SWBestiary", "Defs", "DonorPackPort")
PATH_TAGS = ("texPath", "iconPath", "uiIconPath", "graphicPath", "wornGraphicPath", "texPathFaction")


def donor_index(donor):
    by_name, abstract, races = {}, {}, set()
    for f in sorted(glob.glob(os.path.join(donor, "1.6", "Defs", "**", "*.xml"), recursive=True)):
        r = parse(f)
        for d in (r if r is not None else []):
            if not isinstance(d.tag, str):
                continue
            if d.get("Abstract") == "True" and d.get("Name"):
                abstract[d.get("Name")] = d
                continue
            dn = d.findtext("defName")
            if dn:
                by_name.setdefault(dn, []).append(d)
                if d.tag == "ThingDef" and d.find("race") is not None:
                    races.add(dn)
                if d.tag == "PawnKindDef":
                    races.add(dn)
    return by_name, abstract, races


class Patches:
    """Our own PatchOperations that target a donor species, applied offline to the donor defs before the port, so
    the RSW_ def is the creature the game shows TODAY (owner art redirects, BeastNorm, tolerances, evictions,
    resizes...). Full XPath via lxml. Only top-level operations whose text names a batch species (defName="X" or
    swanimals/X/) are applied, so an op aimed elsewhere can never add to this document. FindMod is decided by mod
    NAME against the active list; an op's MayRequire by packageId. Unknown op classes raise (UNMEASURED, never
    silently skipped)."""

    def __init__(self, active):
        self.names = set(active["names"])
        self.pids = set(active["packageIds"])
        self.applied = []

    def _nodes(self, doc, xp):
        xp = (xp or "").strip()
        if not xp.startswith("/"):
            xp = "/" + xp
        return doc.xpath(xp)

    def _value(self, op):
        from lxml import etree
        v = op.find("value")
        return [copy.deepcopy(c) for c in v if isinstance(c.tag, str)] if v is not None else []

    def run(self, op, doc):
        from lxml import etree
        if op is None:
            return True
        req = op.get("MayRequire")
        if req and not all(p.strip().lower() in self.pids for p in req.split(",")):
            return True
        cls = (op.get("Class") or "").split(".")[-1]
        succ = (op.findtext("success") or "Normal").strip()
        if cls == "PatchOperationSequence":
            ok = all(self.run(li, doc) for li in op.findall("operations/li"))
        elif cls == "PatchOperationConditional":
            hit = bool(self._nodes(doc, op.findtext("xpath")))
            ok = self.run(op.find("match" if hit else "nomatch"), doc) if op.find("match" if hit else "nomatch") is not None else True
            ok = ok and (hit or op.find("nomatch") is not None)
        elif cls == "PatchOperationFindMod":
            hit = any((li.text or "").strip() in self.names for li in op.findall("mods/li"))
            br = op.find("match" if hit else "nomatch")
            ok = self.run(br, doc) if br is not None else hit
        else:
            nodes = self._nodes(doc, op.findtext("xpath"))
            ok = bool(nodes)
            for n in nodes:
                par = n.getparent()
                if cls == "PatchOperationAdd":
                    vals = self._value(op)
                    if (op.findtext("order") or "Append").strip() == "Prepend":
                        for i, v in enumerate(vals):
                            n.insert(i, v)
                    else:
                        n.extend(vals)
                elif cls == "PatchOperationInsert":
                    vals = self._value(op)
                    i = list(par).index(n)
                    if (op.findtext("order") or "Prepend").strip() == "Append":
                        i += 1
                    for k, v in enumerate(vals):
                        par.insert(i + k, v)
                elif cls == "PatchOperationReplace":
                    i = list(par).index(n)
                    par.remove(n)
                    for k, v in enumerate(self._value(op)):
                        par.insert(i + k, v)
                elif cls == "PatchOperationRemove":
                    par.remove(n)
                elif cls in ("PatchOperationAttributeSet", "PatchOperationAttributeAdd"):
                    if cls == "PatchOperationAttributeSet" or n.get(op.findtext("attribute")) is None:
                        n.set(op.findtext("attribute"), op.findtext("value") or "")
                elif cls == "PatchOperationAttributeRemove":
                    n.attrib.pop(op.findtext("attribute"), None)
                elif cls == "PatchOperationSetName":
                    n.tag = op.findtext("name")
                else:
                    raise ValueError(f"unsupported patch op {cls}")
            if nodes:
                self.applied.append((cls, (op.findtext("xpath") or "").strip()))
        if succ == "Always":
            return True
        if succ == "Never":
            return False
        if succ == "Invert":
            return not ok
        return ok

    def bake(self, defs, species):
        """defs: ElementTree elements (donor). Returns baked copies (same order) + files whose ops applied."""
        from lxml import etree
        tagged = []
        for i, d in enumerate(defs):
            d = copy.deepcopy(d)
            d.set("__pid", str(i))
            tagged.append(d)
        doc = etree.fromstring(b"<Defs>" + b"".join(ET.tostring(d) for d in tagged) + b"</Defs>")
        keys = [f'defName="{s}"' for s in species] + [f"defName='{s}'" for s in species] + \
               [f"swanimals/{s}/" for s in species]
        touched = {}
        for f in sorted(glob.glob(os.path.join(SRC, "**", "Patches", "**", "*.xml"), recursive=True)):
            raw = open(f, encoding="utf-8", errors="replace").read()
            if not any(k in raw for k in keys):
                continue
            root = etree.fromstring(raw.encode("utf-8"))
            for op in root:
                if not isinstance(op.tag, str) or op.tag != "Operation":
                    continue
                s = etree.tostring(op, encoding="unicode")
                if any(k in s for k in keys):
                    before = len(self.applied)
                    self.run(op, doc)
                    if len(self.applied) > before:
                        touched[os.path.relpath(f, REPO)] = touched.get(os.path.relpath(f, REPO), 0) + len(self.applied) - before
        out = [None] * len(defs)              # a def our patches REMOVED stays None (dropped from the port)
        for d in doc:
            if not isinstance(d.tag, str):
                continue
            pid = d.attrib.pop("__pid", None)
            if pid is None:
                raise ValueError("a patch ADDED a top-level def while baking; port this batch by hand")
            out[int(pid)] = ET.fromstring(etree.tostring(d))
        return out, touched


VANILLA_TEX = set()


def vanilla_tex(tp):
    """A texPath the base game or a DLC serves: its texture name (or name_<facing>) is in the name list made by
    extract_bundle.py --list over RimWorldWin64_Data/resources.assets and Data/*/AssetBundles (--vanilla-tex)."""
    b = os.path.basename(tp).lower()
    return any(x in VANILLA_TEX for x in (b, b + "_south", b + "_east", b + "_a"))   # _a: Graphic_Random member


def art_plan(texpaths, extract, idx):
    """Dry-run the art for these texPaths: (owned, installable files, refused messages, missing texPaths)."""
    sys.path.insert(0, os.path.join(SRC, "RimMandrake", "Utils", "art"))
    from artwrite import TextureWriter
    tw = TextureWriter(__file__, provenance={"kind": "donor", "donor_pkg": DONOR_PKG}, dry_run=True)
    owned, plan, missing = [], [], []
    for tp in sorted(texpaths):
        if resolves(tp, idx):
            owned.append(tp)
            continue
        files = art_files(extract, tp)
        if not files:
            if vanilla_tex(tp):
                owned.append(tp)
            else:
                missing.append(tp)
        for f, rel in art_targets(extract, tp, files):
            if tw.copy(f, os.path.join(BESTIARY_TEX, rel)):
                plan.append((f, rel))
    return owned, plan, tw.refusals, missing


def art_targets(extract, tp, files):
    d, base = os.path.split(tp.strip("/"))
    for f in files:
        name = os.path.basename(f)
        if os.path.relpath(os.path.dirname(f), extract).lower() == tp.lower().strip("/"):   # Graphic_Random member
            yield f, os.path.join(tp.strip("/"), name)
        else:
            yield f, os.path.join(d, base + name[len(base):])


def def_paths(defs):
    out = set()
    for d in defs:
        for el in d.iter():
            if el.tag in PATH_TAGS and el.text and el.text.strip():
                out.add(el.text.strip())
    return out


def cmd_port(a):
    """Port donor species as RSW_ defs, the MLIE_FAUNA_ABSORPTION_1 recipe made mechanical: the race ThingDef and its
    PawnKindDef(s) go to ThingDefs_Races/RSW_<Species>.xml; every donor-only def they reach (body, body parts and
    groups, meat/leather/eggs, abilities, hediffs, thoughts, namers, render trees...) is ported once, as RSW_<name>,
    into DonorPackPort/RSW_DonorPack_<batch>.xml, unless an RSW_ copy already exists, in which case the reference is
    just renamed. A reference to another donor SPECIES (canCrossBreedWith) is renamed forward to RSW_<name>; to a
    declined one (Mynock) it is dropped. Our own patches on the donor defName are baked in first (--active).
    With --extract, a species whose art the ledger refuses or the bundle lacks is ART_BLOCKED and left out whole,
    so no def ships with a texPath only the donor serves. Never overwrites an existing file."""
    by_name, abstract, races = donor_index(a.donor)
    onames, otyped = our_names(), our_typed()
    vanilla = set(open(a.vanilla).read().split()) if a.vanilla else set()
    if a.vanilla_tex:
        VANILLA_TEX.update(x.strip().lower() for x in open(a.vanilla_tex) if x.strip())
    idx = texture_index()
    active = json.load(open(a.active)) if a.active else None

    def build(species):
        rename, queue, seen, forward = {}, [], set(), set()
        sp_defs, support = {}, []
        for sp in species:
            ds = [d for d in by_name.get(sp, []) if d.tag in ("ThingDef", "PawnKindDef")]
            ds += [d for lst in by_name.values() for d in lst if d.tag == "PawnKindDef" and d.findtext("race") == sp
                   and d not in ds]
            sp_defs[sp] = ds
            support += [d for d in by_name.get(sp, []) if d not in ds   # e.g. the species' own BodyDef
                        and (d.tag, "RSW_" + sp) not in otyped]
            queue += by_name.get(sp, []) + ds
            seen.add(sp)
            rename[sp] = "RSW_" + sp
            for d in ds:
                rename[d.findtext("defName")] = "RSW_" + d.findtext("defName")

        def consider(n):
            if not n or n in vanilla or (n not in by_name and n not in abstract):
                return
            if n in onames:                       # we already define this exact name
                return
            rename[n] = "RSW_" + n
            if n in seen:
                return
            todo = [d for d in by_name.get(n, []) if (d.tag, "RSW_" + n) not in otyped]
            if not todo and n not in abstract:
                return
            if n in abstract and "RSW_" + n in onames:
                return
            if n in races and n not in species:   # another species: forward-rename, never drag it in
                forward.add(n)
                return
            seen.add(n)
            for d in todo:
                support.append(d)
                queue.append(d)
            if n in abstract and not todo:
                support.append(abstract[n])
                queue.append(abstract[n])

        while queue:
            d = queue.pop(0)
            for el in d.iter():
                if isinstance(el.tag, str):
                    consider((el.text or "").strip())
                    consider(el.tag)
                    consider(el.get("ParentName"))
        touched = {}
        if active:
            flat = [d for ds in sp_defs.values() for d in ds] + support
            baked, touched = Patches(active).bake(flat, list(sp_defs))
            bmap = dict(zip(map(id, flat), baked))
            gone = [d.findtext("defName") for d in flat if bmap[id(d)] is None]
            if gone:
                print("our patches REMOVE these donor defs; not ported:", gone)
            sp_defs = {sp: [bmap[id(d)] for d in ds if bmap[id(d)] is not None] for sp, ds in sp_defs.items()}
            support = [bmap[id(d)] for d in support if bmap[id(d)] is not None]
        return sp_defs, support, touched, forward, rename

    species = []
    for sp in [s for s in a.species.split(",") if s]:
        if ("ThingDef", "RSW_" + sp) in otyped:
            print(f"SKIP {sp}: RSW_{sp} already exists")
        elif sp in DECLINED:
            print(f"SKIP {sp}: declined")
        else:
            species.append(sp)
    blocked = {}
    while True:
        sp_defs, support, touched, forward, rename = build(species)
        if not a.extract:
            break
        newly = {}
        for sp, ds in sp_defs.items():
            owned, plan, refused, missing = art_plan(def_paths(ds), a.extract, idx)
            if refused or missing:
                newly[sp] = {"refused": refused, "missing": missing}
        if not newly:
            break
        blocked.update(newly)
        species = [s for s in species if s not in newly]
    for sp, why in blocked.items():
        print(f"ART_BLOCKED {sp}: missing={why['missing']}")
        for r in why["refused"]:
            print("    refused", r.split(": ", 1)[-1][:160])
    dropped = []

    def rewrite(d):
        d = copy.deepcopy(d)
        for parent in list(d.iter()):
            for el in list(parent):
                if not isinstance(el.tag, str):
                    continue
                t = (el.text or "").strip()
                if t in DECLINED and el.tag == "li":       # crossbreed partner we will never port
                    parent.remove(el)
                    dropped.append(t)
                    continue
                if t in rename:
                    el.text = rename[t]
                if el.tag in rename:
                    el.tag = rename[el.tag]
                if el.get("ParentName") in rename:
                    el.set("ParentName", rename[el.get("ParentName")])
        if d.get("ParentName") in rename:
            d.set("ParentName", rename[d.get("ParentName")])
        if d.get("Name") in rename:
            d.set("Name", rename[d.get("Name")])
        dn = d.find("defName")
        if dn is not None and dn.text.strip() in rename:
            dn.text = rename[dn.text.strip()]
        return d

    def write(path, defs, header):
        if os.path.exists(path):
            print(f"REFUSED {os.path.relpath(path, REPO)} exists")
            return
        root = ET.Element("Defs")
        root.append(ET.Comment(header))
        for d in defs:
            root.append(rewrite(d))
        ET.indent(root, space="  ")
        body = ET.tostring(root, encoding="unicode")
        ET.fromstring(body)
        if a.apply:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w", encoding="utf-8").write('<?xml version="1.0" encoding="utf-8"?>\n' + body + "\n")
        print(f"{'WROTE' if a.apply else 'WOULD WRITE'} {os.path.relpath(path, REPO)} ({len(defs)} defs)")

    src_note = ("Ported by src/RimMandrake/Utils/donor_pack_port.py port (DONOR_DEFS_PORT_TO_OURS_1, batch %s) from "
                "mlie.starwarsanimalcollection (MIT; workshop 3497316713, 1.6/Defs). Donor-only names renamed RSW_; "
                "values verbatim. A texPath under swanimals/ or swresource/ keeps the donor path; its PNGs are "
                "extracted donor art installed in SWBestiary/Textures through the art ledger (owner 2026-10-14: ports "
                "may re-use extracted donor art until we regenerate). Canon brief: "
                "design/RimStarWars/canon_references/%s.")
    if touched:
        src_note += (" Our own patches that targeted the donor defName were applied BEFORE the rename (so this is the "
                     "creature the game showed): " + ", ".join(f"{k} ({v} ops)" for k, v in sorted(touched.items())) +
                     ". Those patch ops still name the donor and go dead when it is retired.")
    for sp, ds in sp_defs.items():
        write(os.path.join(RACES_DIR, f"RSW_{sp}.xml"), ds,
              " " + src_note % (a.batch, (a.canon or {}).get(sp, "(see tracker)")) + " ")
    if support:
        write(os.path.join(SUPPORT_DIR, f"RSW_DonorPack_{a.batch}.xml"), support,
              " " + (src_note % (a.batch, "-")).replace(" Canon brief: design/RimStarWars/canon_references/-.", "") +
              " Support defs reached from the batch's species. ")
    print("ported:", ",".join(sp_defs))
    print("support:", ", ".join(f"{d.tag}:{d.findtext('defName') or d.get('Name')}" for d in support))
    print("forward species refs:", sorted(forward), "| dropped:", sorted(set(dropped)))
    paths = def_paths([x for ds in sp_defs.values() for x in ds] + support)
    if a.extract:
        owned, plan, refused, missing = art_plan(paths, a.extract, idx)
        print(f"art: {len(owned)} texPaths already ours, {len(plan)} PNGs to install, support refused/missing: "
              f"{len(refused)}/{missing}")
        for r in refused:
            print("    support refused", r[:200])
        if a.apply:
            sys.path.insert(0, os.path.join(SRC, "RimMandrake", "Utils", "art"))
            from artwrite import TextureWriter
            tw = TextureWriter(__file__, provenance={"kind": "donor", "donor_pkg": DONOR_PKG})
            for f, rel in plan:
                tw.copy(f, os.path.join(BESTIARY_TEX, rel))
            print("art installed:", tw.counts)
    else:
        print("texpaths:", " ".join(sorted(paths)))
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("repoint")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--only")
    p.add_argument("--donor", default=DONOR)
    p.set_defaults(fn=cmd_repoint)
    p = sub.add_parser("diff")
    p.add_argument("--json")
    p.add_argument("--donor", default=DONOR)
    p.set_defaults(fn=cmd_diff)
    p = sub.add_parser("art")
    p.add_argument("--extract", required=True, help="dir written by extract_bundle.py --extract --keep-paths")
    p.add_argument("--apply", action="store_true")
    p.add_argument("texpaths", nargs="+")
    p.set_defaults(fn=cmd_art)
    p = sub.add_parser("port")
    p.add_argument("--species", required=True)
    p.add_argument("--batch", required=True)
    p.add_argument("--apply", action="store_true")
    p.add_argument("--donor", default=DONOR)
    p.add_argument("--extract", help="extract_bundle.py --keep-paths dir; checks and installs art")
    p.add_argument("--vanilla-tex", help="file of vanilla/DLC texture names, one per line")
    p.add_argument("--active", help="json {packageIds:[], names:[]} of the active list (FindMod/MayRequire in bake)")
    p.add_argument("--vanilla", help="file of vanilla defNames (whitespace separated) never to rename")
    p.add_argument("--canon", type=lambda s: dict(x.split("=") for x in s.split(",")), help="Sp=slug,...")
    p.set_defaults(fn=cmd_port)
    p = sub.add_parser("check")
    p.add_argument("files", nargs="*")
    p.add_argument("--species", help="comma list of donor names whose RSW_ port must be complete")
    p.add_argument("--vanilla-tex", help="file of vanilla/DLC texture names, one per line")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("rosters")
    p.set_defaults(fn=cmd_rosters)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
