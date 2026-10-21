#!/usr/bin/env python3
"""Each Star Wars xenotype's size, from the defs: real body size, render scale and head scale.

Offline, from source. Reads every XenotypeDef under src/RimStarWars and src/RimUtinni, applies the
size swaps in src/RimStarWars/StarWarsPatches/Patches/BodySizeIsReal.xml (its PatchOperationConditional /
Replace / Add, with Big and Small present - the shipped list always has it), then sums the size stats of the
genes each xenotype ends up with:
  - our genes (src/RimStarWars/StarWarsRaces/Defs/GeneDefs/SW_Genes.xml) parsed from source;
  - Big and Small's frames from BS_FRAMES below, cross-checked against the live def dump when one is present
    (a donor def, not ours: READ from the 2026-10-21T01-39-11Z dump).
Mechanical size = 1 + SM_BodySizeOffset. Render uses SM_BodySizeOffset + SM_Cosmetic_BodySizeOffset (BSCache,
decompiled: totalCosmeticSize adds the mechanical offset), so turning a cosmetic gene mechanical does not move
the sprite. Head scale = fit_head_canvas.bs_render_size(render offset, head_mult), head_mult = 1 + the genes'
SM_HeadSize_Cosmetic offsets (stat base 1.0, min 0.05).

  python3 src/RimMandrake/Utils/art/species_size.py            # every xenotype with a size or head-size gene
"""
import glob
import json
import os
import sys

from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import fit_head_canvas as F  # noqa: E402

GENES = os.path.join(REPO, "src/RimStarWars/StarWarsRaces/Defs/GeneDefs/SW_Genes.xml")
PATCH = os.path.join(REPO, "src/RimStarWars/StarWarsPatches/Patches/BodySizeIsReal.xml")
XENO_GLOBS = ("src/RimStarWars/**/*.xml", "src/RimUtinni/**/*.xml")
SIZE_STATS = ("SM_BodySizeOffset", "SM_Cosmetic_BodySizeOffset", "SM_HeadSize_Cosmetic", "SM_RaidWealthOffset")

# Big and Small frames BodySizeIsReal.xml swaps in: statOffsets READ from the live def dump
# (GeneDef.json, capture 2026-10-21T01-39-11Z). check_frames_against_dump() re-reads them when a dump exists.
BS_FRAMES = {
    "HalfJotunFrame": {"SM_BodySizeOffset": 0.75, "SM_RaidWealthOffset": 1500},
    "BS_LargeFrame": {"SM_BodySizeOffset": 0.4, "SM_RaidWealthOffset": 750},
    "BS_SmallFrame": {"SM_BodySizeOffset": -0.35, "SM_RaidWealthOffset": -1000},
    "BS_RabbitFrame": {"SM_BodySizeOffset": -0.6, "SM_Cosmetic_BodySizeOffset": -0.15, "SM_RaidWealthOffset": -2000},
}


def our_gene_stats(path=GENES):
    """defName -> {stat: offset} for the size stats, plus 'cosmetic_size' flag source; from source XML."""
    out = {}
    for g in etree.parse(path).getroot().iter("GeneDef"):
        name = g.findtext("defName")
        if not name:
            continue
        so = g.find("statOffsets")
        out[name] = {c.tag: float(c.text) for c in (so if so is not None else []) if isinstance(c.tag, str)
                     and c.tag in SIZE_STATS}
    return out


def load_xenotypes():
    """A <Defs> tree holding every XenotypeDef we ship (deep copies), for the patch to run against."""
    root = etree.Element("Defs")
    for pat in XENO_GLOBS:
        for p in sorted(glob.glob(os.path.join(REPO, pat), recursive=True)):
            if "/Patches/" in p:
                continue
            try:
                t = etree.parse(p)
            except etree.XMLSyntaxError:
                continue
            for x in t.getroot().iter("XenotypeDef"):
                root.append(etree.fromstring(etree.tostring(x)))
    return root


def _xp(root, xp):
    """RimWorld runs a patch xpath against the document, so `Defs/...` starts at the root element."""
    xp = xp.strip()
    return root.xpath(xp if xp.startswith("/") else "/" + xp)


def _apply(op, root):
    cls = op.get("Class")
    if cls == "PatchOperationConditional":
        hit = _xp(root, op.findtext("xpath"))
        sub = op.find("match" if hit else "nomatch")
        if sub is not None:
            _apply(sub, root)
        return
    if cls == "PatchOperationSequence":
        for o in op.find("operations"):
            if isinstance(o.tag, str):
                _apply(o, root)
        return
    if cls == "PatchOperationFindMod":
        sub = op.find("match")              # Big and Small is always on the shipped list
        if sub is not None:
            _apply(sub, root)
        return
    nodes = _xp(root, op.findtext("xpath"))
    val = [c for c in op.find("value")] if op.find("value") is not None else []
    for n in nodes:
        if cls == "PatchOperationReplace":
            par = n.getparent()
            i = par.index(n)
            par.remove(n)
            for k, v in enumerate(val):
                par.insert(i + k, etree.fromstring(etree.tostring(v)))
        elif cls == "PatchOperationAdd":
            for v in val:
                n.append(etree.fromstring(etree.tostring(v)))
        elif cls == "PatchOperationRemove":
            n.getparent().remove(n)
        else:
            raise SystemExit("species_size: unhandled %s in %s" % (cls, PATCH))


def patched_xenotypes():
    root = load_xenotypes()
    etree.ElementTree(root)
    for op in etree.parse(PATCH).getroot():
        if isinstance(op.tag, str) and op.tag == "Operation":
            _apply(op, root)
    out = {}
    for x in root.iter("XenotypeDef"):
        name = x.findtext("defName")
        if name:
            out[name] = [(li.text or "").strip() for li in x.findall("genes/li")]
    return out


def size_of(genes, ours, frames=BS_FRAMES):
    tot = {s: 0.0 for s in SIZE_STATS}
    sources = []
    for g in genes:
        st = ours.get(g) if g in ours else frames.get(g)
        if not st:
            continue
        if any(st.get(s) for s in SIZE_STATS):
            sources.append(g)
        for s in SIZE_STATS:
            tot[s] += st.get(s, 0.0)
    mech = tot["SM_BodySizeOffset"]
    render_off = mech + tot["SM_Cosmetic_BodySizeOffset"]
    head_mult = max(1.0 + tot["SM_HeadSize_Cosmetic"], 0.05)
    body_r, head_r = F.bs_render_size(render_off, head_mult)
    return {"genes": sources, "mech_size": round(1 + mech, 4), "render_offset": round(render_off, 4),
            "head_mult": round(head_mult, 4), "body_render": round(body_r, 4), "head_render": round(head_r, 4),
            "raid_wealth_offset": tot["SM_RaidWealthOffset"]}


def check_frames_against_dump():
    """[(frame, stat, ours, dump)] disagreements; None when no dump is reachable (UNMEASURED)."""
    try:
        from game_paths import DEF_DUMP
        d = json.load(open(os.path.join(DEF_DUMP, "defs", "GeneDef.json"), encoding="utf-8"))
    except Exception:
        return None
    bad = []
    for x in d.get("defs", []):
        n = x.get("defName")
        if n not in BS_FRAMES:
            continue
        got = {m["stat"]: m["value"] for m in x.get("fields", {}).get("statOffsets", []) if m.get("stat") in SIZE_STATS}
        for s in set(got) | set(BS_FRAMES[n]):
            if abs(got.get(s, 0.0) - BS_FRAMES[n].get(s, 0.0)) > 1e-6:
                bad.append((n, s, BS_FRAMES[n].get(s), got.get(s)))
    return bad


def table():
    ours = our_gene_stats()
    rows = {}
    for x, genes in sorted(patched_xenotypes().items()):
        r = size_of(genes, ours)
        if r["genes"]:
            rows[x] = r
    return rows


if __name__ == "__main__":
    for x, r in table().items():
        print("%-32s mech %.2f  render-off %+.2f  head x%.3f (mult %.2f)  wealth %+5.0f  %s"
              % (x, r["mech_size"], r["render_offset"], r["head_render"], r["head_mult"],
                 r["raid_wealth_offset"], ",".join(r["genes"])))
