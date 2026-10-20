#!/usr/bin/env python3
"""salvation_paint_clean.py — derive a PAINT-loadable copy of The Salvation.rid.

The owner's approved ideo (`src/Jawa/ideoligion/The Salvation.rid`) names defs and C#
classes from mods that are not on the PAINT list (VME memes, More Precepts, Prison Labor,
Romance on the Rim, Ritual Attachable Outcomes, ...). Loaded on PAINT, Ideo.ExposeData drops
the null-def precepts but the rituals whose *pattern/behavior/outcome* is off-list survive
half-built and throw PostLoadInit NREs at every load (world remake run 2026-10-20).

This writes a SEPARATE file and never touches the original (cosmetic/design changes need
the owner; the variant is a dev-world convenience, not a ruling). Smallest change only:

  * a meme that is off PAINT                          -> removed from <memes>
  * a precept whose subtree names an off-PAINT def or class -> the whole precept removed
    (a ritual cannot run without its pattern/behavior/outcome; a role without its role def)
  * an off-PAINT <attachableOutcomeEffect>            -> that element removed (optional field)
  * an off-PAINT ability on a role's chosenPawn       -> that ability <li> removed
  * a style entry naming an off-PAINT style            -> that key/value pair removed
  * <meta><modIds>                                    -> filtered to PAINT (+ the DLCs)

"Off PAINT" = the def resolves in the dump only to packageIds absent from the PAINT list
(or resolves nowhere), or a Class attribute's namespace belongs to an off-PAINT assembly.

Usage: python3 src/RimMandrake/Utils/remake/salvation_paint_clean.py [--check]
  --check   build in memory, print the removal list, write nothing; exit 1 if the
            committed variant differs from what would be written.
"""
import argparse
import io
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils"))
import validate_save_artifact as vsa  # noqa: E402

SRC = REPO / "src/Jawa/ideoligion/The Salvation.rid"
OUT = REPO / "src/Jawa/ideoligion/The Salvation (PAINT-clean).rid"
LIST = REPO / "src/Jawa/ideoligion/The Salvation (PAINT-clean).removed.md"
PAINT = REPO / "infrastructure/state/modlists/ModsConfig.PAINT.RULED_2026-10-20.xml"
DLC = {"ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology",
       "ludeon.rimworld.biotech", "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey"}
# C# namespace -> packageId, for Class="" attributes (the dump indexes defs, not types).
CLASS_NS = {
    "AlphaMemes": "sarg.alphamemes",
    "Lightsaber": "lee.theforce.lightsaber",
    "VFETribals": "oskarpotocki.vfe.tribals",
    "VanillaGravshipExpanded": "vanillaexpanded.gravship",
    "MorePrecepts": "llunak.moreprecepts",
    "PrisonLabor": "avius.prisonlabor",
    "RomanceOnTheRim": "telardo.romanceontherim",
    "TPRitualAttachableOutcomes": "thesepeople.ritualattachableoutcomes",
    "VanillaMemesExpanded": "vanillaexpanded.vmemese",
}


def paint_set():
    root = ET.parse(PAINT).getroot()
    return {li.text.strip().lower() for li in root.find("activeMods")} | DLC


def build():
    index, _meta = vsa.build_index()
    if index is None:
        sys.exit("UNMEASURED: no def dump index")
    paint = paint_set()
    refs, _e, _m = vsa.collect(SRC)
    refnames = {v for _x, v in refs}

    def why_off(name):
        ent = index.get(name)
        if not ent:
            return "resolves in no dump (dangling everywhere)"
        pk = sorted({p.lower() for _t, p in ent})
        return None if set(pk) & paint else "from " + ", ".join(pk) + " (not on PAINT)"

    def class_off(cls):
        if not cls or "." not in cls:
            return None
        ns = cls.split(".")[0]
        pk = CLASS_NS.get(ns)
        if pk is None:
            sys.exit(f"UNMEASURED: unknown Class namespace {ns!r} — add it to CLASS_NS")
        return None if pk in paint else f"class {cls} from {pk} (not on PAINT)"

    def subtree_reasons(el):
        out = []
        for d in el.iter():
            c = class_off(d.get("Class"))
            if c:
                out.append(c)
            t = (d.text or "").strip()
            if len(d) == 0 and t in refnames:
                w = why_off(t)
                if w:
                    out.append(f"{d.tag} {t}: {w}")
        return out

    def remove(parent, el):
        kids = list(parent)
        i = kids.index(el)
        if i > 0:
            kids[i - 1].tail = el.tail
        elif len(kids) == 1:
            parent.text = el.tail
        parent.remove(el)

    with open(SRC, "rb") as fh:
        raw = fh.read()
    tree = ET.parse(io.BytesIO(raw))
    root = tree.getroot()
    ideo = root.find("ideo")
    removed = []

    meta_ids = root.find("meta/modIds")
    dropped_ids = [li for li in list(meta_ids) if (li.text or "").strip().lower() not in paint]
    for li in dropped_ids:
        remove(meta_ids, li)
    removed.append(("meta/modIds", f"{len(dropped_ids)} modIds not on PAINT",
                    "load-dialog stamp only; " + ", ".join(sorted(li.text.strip() for li in dropped_ids))))

    memes = ideo.find("memes")
    for li in list(memes):
        w = why_off(li.text.strip())
        if w:
            remove(memes, li)
            removed.append(("meme", li.text.strip(), w))

    precepts = ideo.find("precepts")
    for p in list(precepts):
        label = f"{(p.findtext('name') or '?')} [{p.findtext('def')}, ID {p.findtext('ID')}]"
        # sub-element strips first, so they do not condemn the whole precept
        for att in p.findall("attachableOutcomeEffect"):
            w = why_off((att.text or "").strip())
            if w:
                remove(p, att)
                removed.append(("ritual attachable outcome", f"{att.text.strip()} on {label}", w))
        for abil_list in p.findall("chosenPawn/abilities"):
            for ab in list(abil_list):
                w = why_off(ab.findtext("def") or "")
                if w:
                    remove(abil_list, ab)
                    removed.append(("role ability", f"{ab.findtext('def')} on {label}", w))
        rs = subtree_reasons(p)
        if rs:
            remove(precepts, p)
            kind = "ritual" if p.get("Class") == "Precept_Ritual" else (
                "role" if (p.get("Class") or "").startswith("Precept_Role") else (
                    "building" if p.get("Class") == "Precept_Building" else "precept"))
            removed.append((kind, label, "; ".join(dict.fromkeys(rs))))

    sft = ideo.find("style/styleForThingDef")
    if sft is not None:
        keys, vals = sft.find("keys"), sft.find("values")
        for k, v in list(zip(list(keys), list(vals))):
            rs = subtree_reasons(v)
            if rs:
                remove(keys, k)
                remove(vals, v)
                removed.append(("style", f"styleForThingDef {k.text}", "; ".join(rs)))

    # Removed precepts must not be referenced by ID anywhere that remains.
    gone = {f"Precept_{r[1].rsplit('ID ', 1)[1].rstrip(']')}" for r in removed
            if r[0] in ("ritual", "role", "building", "precept")}
    left = {(e.text or "").strip() for e in root.iter()}
    dangling_ids = sorted(gone & left)
    if dangling_ids:
        sys.exit(f"REFUSED: removed precepts still referenced: {dangling_ids}")

    buf = io.BytesIO()
    tree.write(buf, encoding="utf-8", xml_declaration=False)
    body = buf.getvalue()
    head = b'\xef\xbb\xbf<?xml version="1.0" encoding="utf-8"?>\n'
    return head + body + (b"\n" if raw.endswith(b"\n") else b""), removed


def render_list(removed):
    lines = [
        "# The Salvation (PAINT-clean) — what was removed and why",
        "",
        "Generated by `src/RimMandrake/Utils/remake/salvation_paint_clean.py` from",
        "`src/Jawa/ideoligion/The Salvation.rid` (untouched, the owner's approved artifact) against",
        "`infrastructure/state/modlists/ModsConfig.PAINT.RULED_2026-10-20.xml`. A dev-world variant only:",
        "every row is reversible by loading the original on a list that carries the mod. Porting any",
        "of these to Core or our own defs is a design change and is the owner's call.",
        "",
        "| kind | element | reason |",
        "|---|---|---|",
    ]
    for kind, what, why in removed:
        lines.append(f"| {kind} | {what} | {why} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    data, removed = build()
    listing = render_list(removed)
    n = sum(1 for r in removed if r[0] != "meta/modIds")
    if a.check:
        sys.stdout.write(listing)
        same = OUT.exists() and OUT.read_bytes() == data and LIST.exists() and LIST.read_text() == listing
        print("CURRENT" if same else "STALE (re-run without --check)")
        return 0 if same else 1
    OUT.write_bytes(data)
    LIST.write_text(listing)
    print(f"wrote {OUT.relative_to(REPO)} ({len(data)} bytes), {n} elements removed; list {LIST.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
