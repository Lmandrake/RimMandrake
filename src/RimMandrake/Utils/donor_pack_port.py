#!/usr/bin/env python3
"""donor_pack_port.py -- the script for DONOR_DEFS_PORT_TO_OURS_1 on mlie.starwarsanimalcollection.

Plan: design/RimMandrake/donor_pack_port_plan_2026-10-14.md. Tracker: design/RimMandrake/donor_pack_port_tracker.md.

    python3 src/RimMandrake/Utils/donor_pack_port.py diff [--json OUT]   W0: every twin against the donor
    python3 src/RimMandrake/Utils/donor_pack_port.py rosters             W1: donor-named roster rows, parsed as XML

`diff` compares each of the donor's 160 races with our same-named RSW_/RM_/RUT_ race ThingDef + PawnKindDef:
statBases, race body / bodySize / healthScale / lifeExpectancy, lifeStageAges, PawnKind lifeStage count and
whether every texPath the twin names resolves to a PNG under src/**/Textures (else it binds only through the
donor). A body is equal if the twin names the donor's body or RSW_<body>. Our texPath differing from the donor's
is expected (regenerated art) and is reported only when it does not resolve in our tree.

NOT PROVEN HERE: that anything loads. That is W4 (a donor-off load), owed live.
"""
import argparse
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
            row.update(issues=issues, tex_unresolved=tex_bad, stub=stub)
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


def roster_rows():
    """Every <wildAnimals> child under src/ whose MayRequire names the donor (XML elements, never <li> counts)."""
    out = []
    for f in sorted(glob.glob(os.path.join(SRC, "**", "*.xml"), recursive=True)):
        r = parse(f)
        if r is None:
            continue
        for wa in r.iter("wildAnimals"):
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
        for wa in root.iter("wildAnimals"):
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


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("repoint")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--only")
    p.add_argument("--donor", default=DONOR)
    p.set_defaults(fn=cmd_repoint)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("diff")
    p.add_argument("--json")
    p.add_argument("--donor", default=DONOR)
    p.set_defaults(fn=cmd_diff)
    p = sub.add_parser("rosters")
    p.set_defaults(fn=cmd_rosters)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
