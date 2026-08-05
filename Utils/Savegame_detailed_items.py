#!/usr/bin/env python3
"""
Savegame_detailed_items.py  —  RimWorld 1.6 (.rws) item & flavor-text reader
============================================================================

PURPOSE
-------
A companion to Savegame_mapview.py. Where that tool renders the *map*, this one
reads every ITEM currently in a savegame and pulls out the human-interesting
"flavor" attached to it — unique names, art tales, quality, material (stuff),
condition — plus the free narrative TEXT blocks (scenario intro, letters,
messages, backstory/quest descriptions) that give the save its story.

This is a research probe for the save-based world-authoring pipeline
(see ../save_authoring_pipeline.md and ../rimworld_file_lore.md).

WHAT COUNTS AS AN "ITEM"  (verified against 03_Gravtasm__starting_save.rws)
--------------------------------------------------------------------------
A save is well-formed XML. Any element that has BOTH a <def> and an <id> child
is a placed/stored Thing (weapon, apparel, chunk, plant, filth, building, pawn,
etc.). We parse with ElementTree (full file ~0.4s) rather than regex so each
flavor field is reliably associated with its OWN item.

FLAVOR FIELDS READ (all optional; only present when the item has them)
----------------------------------------------------------------------
  <title>       unique/legendary item name (e.g. "Ash Raven", "The Vulture")
  <quality>     Awful..Legendary
  <stuff>       material defName (Steel, Plasteel, Leather_*, modded stuffs)
  <health>      current hit points
  <stackCount>  stack size
  <taleRef>     art tale seed (procedural artwork "story" — seed only in save)
  <name>        proper name node (pawns, some named objects)

NARRATIVE TEXT (collected separately, with a short kind guess)
--------------------------------------------------------------
  <text>         letters / messages / archived comms
  <description>  scenario + quest + ideo/backstory narrative
  <title>        also listed in the named-items section

OUTPUT
------
  <stem>_items.json   full machine-readable inventory + flavor + narrative
  <stem>_items.md     readable report: summary, named/unique items table,
                      quality/material breakdowns, top item types, and the
                      collected narrative text blocks
  (console)           short summary

USAGE
-----
  python3 Savegame_detailed_items.py <path-to.rws> [--out DIR]
                                     [--min-quality Good] [--max-text 4000]
"""

import sys
import os
import json
import argparse
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

QUALITY_ORDER = ["Awful", "Poor", "Normal", "Good", "Excellent",
                 "Masterwork", "Legendary"]
QUALITY_RANK = {q: i for i, q in enumerate(QUALITY_ORDER)}

# ---- category heuristics by def-name prefix / keyword ----------------------
CATEGORY_RULES = [
    ("pawn", lambda d: d in ("Human",) or d.startswith("Mech_")),
    ("weapon", lambda d: d.startswith("Gun_") or d.startswith("MeleeWeapon_")
     or d.startswith("Weapon") or "Blaster" in d or "Saber" in d
     or "Bow_" in d or d.startswith("Gun")),
    ("apparel", lambda d: d.startswith("Apparel_") or "Apparel" in d
     or d.startswith("VAE_") or "Armor" in d or "Helmet" in d
     or "Suit" in d or "Jumpsuit" in d),
    ("plant", lambda d: d.startswith("Plant_")),
    ("chunk", lambda d: d.startswith("Chunk") or "Slag" in d),
    ("filth", lambda d: d.startswith("Filth_")),
    ("resource", lambda d: d in ("Steel", "WoodLog", "Silver", "Gold",
     "Plasteel", "ComponentIndustrial", "ComponentSpacer", "Uranium",
     "Chemfuel", "Medicine", "MedicineHerbal", "MedicineIndustrial")),
    ("building", lambda d: d in ("Wall",) or "Hull" in d or "Door" in d
     or "Console" in d or "Engine" in d or "Wall" in d),
    ("food", lambda d: "Meal" in d or d.startswith("Raw") or d.startswith("Meat_")
     or d.startswith("Egg") or "Kibble" in d or "Pemmican" in d),
    ("book", lambda d: "Book" in d or "Schematic" in d or "Textbook" in d),
    ("drug", lambda d: d in ("Beer", "Smokeleaf", "Flake", "Yayo",
     "GoJuice", "WakeUp", "Penoxycyline", "Luciferium")),
]


def categorize(defname: str) -> str:
    for name, rule in CATEGORY_RULES:
        try:
            if rule(defname):
                return name
        except Exception:
            pass
    return "other"


def text_of(el, tag):
    c = el.find(tag)
    if c is None:
        return None
    t = (c.text or "").strip()
    return t if t else None


def is_item(el):
    # has BOTH def and id direct children
    has_def = el.find("def") is not None
    has_id = el.find("id") is not None
    return has_def and has_id


def build_parent_map(root):
    return {child: parent for parent in root.iter() for child in parent}


def nearest_named_owner(el, parent_map):
    """Walk up to find an enclosing pawn's proper name (for held items)."""
    cur = parent_map.get(el)
    depth = 0
    while cur is not None and depth < 40:
        # a pawn element typically has def==Human and a <name><first>/<nick>
        nm = cur.find("name")
        if nm is not None:
            first = text_of(nm, "first")
            nick = text_of(nm, "nick")
            last = text_of(nm, "last")
            parts = [p for p in (first, ('"%s"' % nick) if nick else None, last)
                     if p]
            if parts:
                return " ".join(parts)
        cur = parent_map.get(cur)
        depth += 1
    return None


def guess_text_kind(el, parent_map):
    """Best-effort label for a <text>/<description> block."""
    p = parent_map.get(el)
    ptag = p.tag if p is not None else "?"
    # climb a little for a Class hint
    cur = p
    for _ in range(4):
        if cur is None:
            break
        cls = cur.get("Class") if hasattr(cur, "get") else None
        if cls:
            return cls
        cur = parent_map.get(cur)
    return ptag


def main():
    ap = argparse.ArgumentParser(description="RimWorld .rws item + flavor reader")
    ap.add_argument("save", help="path to .rws savegame")
    ap.add_argument("--out", default=None, help="output directory")
    ap.add_argument("--min-quality", default=None,
                    help="only list items at/above this quality in the "
                         "highlights table (e.g. Good)")
    ap.add_argument("--max-text", type=int, default=4000,
                    help="truncate each narrative text block to N chars in the "
                         "markdown report (JSON keeps full text)")
    args = ap.parse_args()

    if not os.path.isfile(args.save):
        sys.exit("No such file: %s" % args.save)

    stem = os.path.splitext(os.path.basename(args.save))[0]
    out_dir = args.out or os.path.dirname(os.path.abspath(args.save))
    os.makedirs(out_dir, exist_ok=True)

    print("Parsing %s ..." % args.save)
    tree = ET.parse(args.save)
    root = tree.getroot()
    parent_map = build_parent_map(root)

    items = []
    type_counts = Counter()
    cat_counts = Counter()
    quality_counts = Counter()
    stuff_counts = Counter()
    named_items = []

    for el in root.iter():
        if not is_item(el):
            continue
        defname = text_of(el, "def")
        idv = text_of(el, "id")
        if defname is None:
            continue
        cat = categorize(defname)
        rec = {"def": defname, "id": idv, "category": cat}

        title = text_of(el, "title")
        quality = text_of(el, "quality")
        stuff = text_of(el, "stuff")
        health = text_of(el, "health")
        stack = text_of(el, "stackCount")
        tale = el.find("taleRef")
        pos = text_of(el, "pos")

        if title:
            rec["title"] = title
        if quality:
            rec["quality"] = quality
            quality_counts[quality] += 1
        if stuff:
            rec["stuff"] = stuff
            stuff_counts[stuff] += 1
        if health:
            rec["health"] = health
        if stack:
            rec["stackCount"] = stack
        if pos:
            rec["pos"] = pos
        if tale is not None:
            seed = text_of(tale, "seed")
            rec["taleSeed"] = seed

        type_counts[defname] += 1
        cat_counts[cat] += 1

        # a "named / notable" item: has a title, or high quality, or a tale
        notable = bool(title) or (quality and QUALITY_RANK.get(quality, 0)
                                  >= QUALITY_RANK["Excellent"]) or tale is not None
        if notable:
            owner = nearest_named_owner(el, parent_map)
            if owner:
                rec["heldBy"] = owner
            named_items.append(rec)

        items.append(rec)

    # ---- narrative text ----
    narrative = []
    seen_text = set()
    for tag in ("text", "description"):
        for el in root.iter(tag):
            t = (el.text or "").strip()
            if not t or len(t) < 12:
                continue
            key = (tag, t[:120])
            if key in seen_text:
                continue
            seen_text.add(key)
            narrative.append({
                "kind": guess_text_kind(el, parent_map),
                "tag": tag,
                "text": t,
            })

    # ---- write JSON ----
    report = {
        "save": os.path.basename(args.save),
        "totals": {
            "items": len(items),
            "distinct_defs": len(type_counts),
            "categories": dict(cat_counts),
            "with_quality": sum(quality_counts.values()),
            "named_or_notable": len(named_items),
            "narrative_blocks": len(narrative),
        },
        "quality_breakdown": dict(quality_counts),
        "top_stuffs": stuff_counts.most_common(40),
        "top_types": type_counts.most_common(60),
        "named_items": named_items,
        "narrative": narrative,
        "all_items": items,
    }
    json_path = os.path.join(out_dir, "%s_items.json" % stem)
    with open(json_path, "w") as fh:
        json.dump(report, fh, indent=2)

    # ---- write Markdown ----
    minq = QUALITY_RANK.get(args.min_quality, -1) if args.min_quality else -1
    md = []
    md.append("# Item & flavor report — `%s`\n" % os.path.basename(args.save))
    md.append("Generated by `Utils/Savegame_detailed_items.py`.\n")
    md.append("## Summary\n")
    md.append("- **Items (Things with def+id):** %d across %d distinct defs"
              % (len(items), len(type_counts)))
    md.append("- **Categories:** " + ", ".join(
        "%s %d" % (k, v) for k, v in cat_counts.most_common()))
    md.append("- **Items with quality:** %d  ·  **named/notable:** %d  ·  "
              "**narrative blocks:** %d\n"
              % (sum(quality_counts.values()), len(named_items),
                 len(narrative)))

    # named/unique items
    md.append("## Named & notable items\n")
    md.append("Items carrying a unique `<title>`, Excellent+ quality, or "
              "procedural art (`taleRef`).\n")
    uniq = [r for r in named_items if r.get("title")]
    if uniq:
        md.append("### Uniquely-titled items\n")
        md.append("| Title | Def | Quality | Material | Held by |")
        md.append("|---|---|---|---|---|")
        for r in sorted(uniq, key=lambda r: r.get("title", "")):
            md.append("| %s | `%s` | %s | %s | %s |" % (
                r.get("title", ""), r["def"], r.get("quality", "—"),
                r.get("stuff", "—"), r.get("heldBy", "—")))
        md.append("")
    # high quality (non-titled)
    hq = [r for r in named_items if not r.get("title")
          and QUALITY_RANK.get(r.get("quality", ""), -1) >= max(minq,
          QUALITY_RANK["Excellent"])]
    if hq:
        md.append("### High-quality items (Excellent+)\n")
        md.append("| Def | Quality | Material | Held by |")
        md.append("|---|---|---|---|")
        for r in sorted(hq, key=lambda r: -QUALITY_RANK.get(
                r.get("quality", ""), 0)):
            md.append("| `%s` | %s | %s | %s |" % (
                r["def"], r.get("quality", "—"), r.get("stuff", "—"),
                r.get("heldBy", "—")))
        md.append("")

    # quality + material breakdown
    md.append("## Quality breakdown\n")
    for q in QUALITY_ORDER:
        if quality_counts.get(q):
            md.append("- %s: %d" % (q, quality_counts[q]))
    md.append("\n## Top materials (`stuff`)\n")
    for s, n in stuff_counts.most_common(25):
        md.append("- `%s`: %d" % (s, n))

    md.append("\n## Top item types\n")
    for d, n in type_counts.most_common(40):
        md.append("- `%s`: %d" % (d, n))

    # narrative
    md.append("\n## Narrative / flavor text\n")
    md.append("Scenario intro, letters, messages, and quest/backstory "
              "descriptions found in the save.\n")
    for i, blk in enumerate(narrative, 1):
        t = blk["text"]
        if len(t) > args.max_text:
            t = t[:args.max_text] + " …[truncated]"
        md.append("### %d. %s (`<%s>`)\n" % (i, blk["kind"], blk["tag"]))
        md.append("> " + t.replace("\n", "\n> ") + "\n")

    md_path = os.path.join(out_dir, "%s_items.md" % stem)
    with open(md_path, "w") as fh:
        fh.write("\n".join(md))

    # ---- console ----
    print("\nItems: %d (%d distinct defs)" % (len(items), len(type_counts)))
    print("Categories: " + ", ".join("%s=%d" % (k, v)
          for k, v in cat_counts.most_common()))
    print("Quality: " + ", ".join("%s=%d" % (k, v)
          for k, v in quality_counts.most_common()))
    print("Named/notable items: %d  ·  narrative blocks: %d"
          % (len(named_items), len(narrative)))
    if uniq:
        print("\nUniquely-titled items:")
        for r in uniq:
            print("  - %-28s (%s%s%s)" % (
                r.get("title", ""), r["def"],
                ", " + r["quality"] if r.get("quality") else "",
                ", held by " + r["heldBy"] if r.get("heldBy") else ""))
    print("\nReport MD:   %s" % md_path)
    print("Report JSON: %s" % json_path)


if __name__ == "__main__":
    main()
